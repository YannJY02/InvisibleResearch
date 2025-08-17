#!/usr/bin/env python3
"""
LLM_name_detect.py

Pipeline on top of `creator_sample.parquet` to:
1) Pre-clean the raw `creator` field (strip HTML, normalize whitespace, Unicode NFKC)
2) Decide whether a row is "simple" (rule-based parsing is enough) or "complex" (send to an LLM)
3) Use GPT-4o to extract a clean list of authors and affiliations for complex rows
4) Write the result to `creator_sample_clean.parquet`, adding `authors_clean` and `affiliations` columns

Dependencies:
    pip install pyarrow pandas beautifulsoup4 lxml unidecode nameparser openai tenacity python-dotenv

Configuration:
    Create a .env file in the project root or set environment variables:
    OPENAI_API_KEY=your_api_key_here                    # Required: Your OpenAI API key
    OPENAI_BASE_URL=https://your-proxy.com/v1          # Optional: Custom proxy URL
    OPENAI_MODEL=gpt-4o                                 # Optional: Model to use (default: gpt-4o)
    BATCH_SIZE=20                                       # Optional: Batch size (default: 20)

Run:
    python LLM_name_detect.py
"""
from __future__ import annotations

from pathlib import Path
import os
import re
import json
import unicodedata
from typing import List, Tuple, Optional

import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from bs4 import BeautifulSoup
from unidecode import unidecode
from nameparser import HumanName

import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# -----------------------------------------------------------------------------
# OpenAI API configuration
# -----------------------------------------------------------------------------
def _validate_api_key(api_key: str) -> bool:
    """Validate API key format (basic security check)."""
    if not api_key:
        return False
    if len(api_key) < 10:  # Reasonable minimum length
        return False
    if api_key.startswith('sk-') and len(api_key) < 20:  # OpenAI format check
        return False
    return True

def _get_openai_client() -> openai.OpenAI:
    """Initialize and return the OpenAI client with secure configuration."""
    # Read configuration from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # Default to official API
    
    # Validate API key
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Please set it in your environment or create a .env file with:\n"
            "OPENAI_API_KEY=your_api_key_here\n"
            "OPENAI_BASE_URL=your_proxy_url_here  # Optional, defaults to OpenAI official API"
        )
    
    if not _validate_api_key(api_key):
        raise ValueError(
            "Invalid API key format. Please check your OPENAI_API_KEY environment variable."
        )
    
    # Additional security: mask API key in logs
    masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:] if len(api_key) > 12 else "*" * len(api_key)
    print(f"🔐 Initializing OpenAI client with API key: {masked_key}")
    print(f"🌐 Using base URL: {base_url}")
    
    return openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SRC_PARQUET = Path(__file__).parent.parent.parent / "data/processed/creator_sample.parquet"
DST_PARQUET = Path(__file__).parent.parent.parent / "data/final/creator_sample_clean_v2.parquet"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # Default to official model name, can be overridden
BATCH = int(os.getenv("BATCH_SIZE", "20"))   # Configurable batch size

# Instantiate the OpenAI client (will be initialized when needed)
client: Optional[openai.OpenAI] = None

def get_client() -> openai.OpenAI:
    """Get or initialize the OpenAI client."""
    global client
    if client is None:
        client = _get_openai_client()
    return client

# -----------------------------------------------------------------------------
# Regex patterns and helpers
# -----------------------------------------------------------------------------
# Anything that clearly looks like affiliation / contact / URL
AFFIL_PAT = re.compile(
    r"\b(universit|faculty|department|institute|hospital|school|center|college|email|@|www\.|http|orcid|tel|phone|doi:)",
    re.I,
)

# Delimiters used for authors (commas are intentionally *not* a primary delimiter
# because they often appear inside a single name in the form "Last, First")
AUTHOR_DELIMS = re.compile(
    r"\s*(?:;|&|\band\b|\+|/|\\|\||<br>|<br/>|<br />)\s*"  # explicit separators
    r"|\s{2,}"                                                  # 2+ spaces after cleanup
    r"|\s*[,؛،،]\s+(?=[A-ZА-ЯЁĀ-Ŷ])",                         # comma-space-Capital in many scripts
    flags=re.IGNORECASE,
)

WS_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Remove HTML tags but keep a single space as a separator."""
    return BeautifulSoup(text, "lxml").get_text(" ", strip=True)


def rough_clean(text: str) -> str:
    """HTML → plain text, Unicode NFKC, compress whitespace."""
    txt = strip_html(text)
    txt = unicodedata.normalize("NFKC", txt)
    txt = WS_RE.sub(" ", txt)
    return txt.strip()


def _canonical(name: str) -> str:
    """Canonicalise a single personal name: keep first+last, unidecode, lowercase, single spaces."""
    hn = HumanName(name)
    simplified = f"{hn.first} {hn.last}".strip()
    simplified = unidecode(simplified).lower()
    simplified = WS_RE.sub(" ", simplified)
    return simplified


# -----------------------------------------------------------------------------
# Name formatting helper
# -----------------------------------------------------------------------------
def format_person(name: str) -> str:
    """Format a single name as 'Last, First Middle'. Ensure comma+space inside a name and do NOT touch separators between different people.
    Falls back gracefully if parsing fails or parts are missing."""
    if not name:
        return ""
    # normalize internal spaces
    name = WS_RE.sub(" ", name).strip()

    # If already contains a comma, just normalize spaces around the first comma
    if "," in name:
        parts = [p.strip() for p in name.split(",", 1)]
        if len(parts) == 2:
            left, right = parts
            right = WS_RE.sub(" ", right).strip()
            return f"{left}, {right}" if right else left
        return parts[0]

    # Use nameparser to split
    hn = HumanName(name)
    last  = WS_RE.sub(" ", hn.last.strip()) if hn.last else ""
    first = WS_RE.sub(" ", hn.first.strip()) if hn.first else ""
    middle = WS_RE.sub(" ", hn.middle.strip()) if hn.middle else ""

    # Title-case tokens (keep accents)
    def tc(s: str) -> str:
        return " ".join(w.capitalize() for w in s.split())

    last_tc   = tc(last)   if last   else ""
    fm_tc     = tc(" ".join([p for p in [first, middle] if p])) if (first or middle) else ""

    if last_tc and fm_tc:
        return f"{last_tc}, {fm_tc}"
    return last_tc or fm_tc or name


def is_simple(txt: str) -> bool:
    """Conservatively decide if a row can be parsed with simple rules (avoid false negatives)."""
    if AFFIL_PAT.search(txt):
        return False
    if re.search(r"[;&/\\]| and ", txt, re.I):
        return False
    comma_groups = re.findall(r",[ ]*[A-ZÁÀÄÂÅÆĆČÇÉÈÊËÍÌÎÏÑÓÒÔÖØŚŠÚÙÛÜÝŽ]", txt)
    return len(comma_groups) <= 1

# -----------------------------------------------------------------------------
# LLM schema & call helper
# -----------------------------------------------------------------------------
schema = {
    "name": "parse_authors",
    "description": "Extract original author strings and affiliations without altering or translating names.",
    "parameters": {
        "type": "object",
        "properties": {
            "authors_original": {"type": "array", "items": {"type": "string"}},
            "affiliations": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["authors_original"],
    },
}

SYSTEM_MSG = (
    "You are a data-cleaning assistant. Input is a raw 'creator' field from academic metadata. "
    "Return JSON with two keys: 'authors_original' (list of personal names EXACTLY as they appear, aside from trimming leading/trailing spaces) "
    "and 'affiliations' (anything that is not a personal name: organisation, email, phone, ORCID, DOI, address, etc.). "
    "Do NOT translate, romanize, change case, reorder tokens inside a single name, or add/remove accents. Only split the string into individual names. "
    "If you are unsure whether a token is an affiliation, put it in 'affiliations'. If no affiliation, return an empty list."
)


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def call_llm(text: str) -> dict:
    """Send one creator string to GPT-4o and return a dict."""
    messages = [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user",   "content": text},
    ]

    response = get_client().chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        tools=[{"type": "function", "function": schema}],
        tool_choice={"type": "function", "function": {"name": "parse_authors"}},
        max_tokens=1000,
    )

    tool_calls = response.choices[0].message.tool_calls or []
    if not tool_calls:
        return {"authors_original": [], "affiliations": []}

    args_json = tool_calls[0].function.arguments
    data = json.loads(args_json)
    # Backward safety: if the model returned the old key 'authors', map it
    if "authors_original" not in data and "authors" in data:
        data["authors_original"] = data.pop("authors")
    return data


# -----------------------------------------------------------------------------
# Main pipeline
# -----------------------------------------------------------------------------
def main() -> None:
    if not SRC_PARQUET.exists():
        raise SystemExit(f"Parquet not found: {SRC_PARQUET}")

    df = pq.read_table(SRC_PARQUET).to_pandas()

    n = len(df)
    authors_clean: List[str] = [""] * n
    affil_out: List[List[str]] = [None] * n

    complex_batch: List[Tuple[str, int]] = []

    def process_batch(batch: List[Tuple[str, int]]) -> None:
        """Process a batch of complex rows synchronously."""
        for clean_txt, idx in batch:
            try:
                res = call_llm(clean_txt)
                # Extract authors and format as clean string
                authors = res.get("authors_original", [])
                authors_clean[idx] = "; ".join(author.strip() for author in authors if author.strip())
                affil_out[idx] = res.get("affiliations", [])
            except Exception as e:
                print(f"Warning: Failed to process row {idx}: {e}")
                authors_clean[idx] = ""
                affil_out[idx] = []

    # Process all rows
    for idx, raw in enumerate(df["creator"].astype(str).fillna("")):
        clean_txt = rough_clean(raw)
        if not clean_txt:
            authors_clean[idx] = ""
            affil_out[idx] = []
            continue

        if is_simple(clean_txt):
            # Simple case: use the cleaned text as-is
            authors_clean[idx] = clean_txt.strip()
            affil_out[idx] = []
        else:
            # Complex case: add to batch for LLM processing
            complex_batch.append((clean_txt, idx))
            
            # Process batch when it reaches the limit
            if len(complex_batch) >= BATCH:
                process_batch(complex_batch)
                complex_batch = []

    # Process any remaining complex rows
    if complex_batch:
        process_batch(complex_batch)

    # Safety: ensure no None values remain
    affil_out = [a if a is not None else [] for a in affil_out]

    # Add columns to dataframe
    df["authors_clean"] = authors_clean
    df["affiliations"] = affil_out

    # Write back to Parquet
    pq.write_table(pa.Table.from_pandas(df), DST_PARQUET)
    print(f"✅ Clean parquet written to {DST_PARQUET} ({len(df)} rows)")


if __name__ == "__main__":
    main()