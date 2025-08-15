#!/usr/bin/env python3
"""
LLM_name_detect.py

Pipeline on top of `creator_sample.parquet` to:
1) Pre-clean the raw `creator` field (strip HTML, normalize whitespace, Unicode NFKC)
2) Decide whether a row is "simple" (rule-based parsing is enough) or "complex" (send to an LLM)
3) Use GPT-4o (function calling style) to extract a clean list of authors and affiliations for complex rows
4) Write the result to `creator_sample_clean.parquet`, adding `authors_clean` and `affiliations` columns

Dependencies:
    pip install pyarrow pandas beautifulsoup4 lxml unidecode nameparser openai tenacity

Run:
    OPENAI_API_KEY=<your_key> python LLM_name_detect.py
"""
from __future__ import annotations

from pathlib import Path
import os
import re
import json
import asyncio
import unicodedata
from typing import List, Tuple

import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from bs4 import BeautifulSoup
from unidecode import unidecode
from nameparser import HumanName

from openai import AsyncOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# -----------------------------------------------------------------------------
# OpenAI API‑key helper
# -----------------------------------------------------------------------------
def _get_openai_api_key() -> str:
    """Return the OpenAI API key from env or raise an explicit error."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set. Please `export OPENAI_API_KEY=<key>` first."
        )
    return key

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SRC_PARQUET = Path(__file__).parent.parent.parent / "data/processed/creator_sample.parquet"
DST_PARQUET = Path(__file__).parent.parent.parent / "data/final/creator_sample_clean.parquet"
MODEL = "gpt-4o"
BATCH = 20               # number of complex rows per LLM call

# Instantiate the async OpenAI client (requires helper above)
client = AsyncOpenAI(api_key=_get_openai_api_key())

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
async def call_llm(text: str) -> dict:
    """Send one creator string to GPT‑4o (OpenAI 1.x API) and return a dict."""
    messages = [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user",   "content": text},
    ]

    response = await client.chat.completions.create(
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
async def main() -> None:
    if not SRC_PARQUET.exists():
        raise SystemExit(f"Parquet not found: {SRC_PARQUET}")

    df = pq.read_table(SRC_PARQUET).to_pandas()

    n = len(df)
    authors_orig_out: List[List[str]] = [None] * n
    affil_out:   List[List[str]] = [None] * n

    complex_batch: List[str] = []
    complex_idx:   List[int] = []
    pending_tasks: List[asyncio.Task] = []

    semaphore = asyncio.Semaphore(8)  # limit concurrent LLM requests

    async def flush_batch() -> None:
        """Send queued complex rows concurrently, keep order mapping."""
        nonlocal complex_batch, complex_idx
        if not complex_batch:
            return

        async def runner(txt: str, i: int):
            async with semaphore:
                res = await call_llm(txt)
                return i, res

        tasks = [asyncio.create_task(runner(t, i)) for t, i in zip(complex_batch, complex_idx)]
        pending_tasks.extend(tasks)
        complex_batch, complex_idx = [], []

    # Pass 1: decide simple vs complex and collect complex batches
    for idx, raw in enumerate(df["creator"].astype(str).fillna("")):
        clean_txt = rough_clean(raw)
        if not clean_txt:
            authors_orig_out[idx] = []
            affil_out[idx] = []
            continue

        if is_simple(clean_txt):
            # Do not modify name text, just trim outer spaces
            name_str = clean_txt.strip()
            authors_orig_out[idx] = [name_str] if name_str else []
            affil_out[idx] = []
        else:
            complex_batch.append(clean_txt)
            complex_idx.append(idx)
            if len(complex_batch) >= BATCH:
                await flush_batch()

    await flush_batch()  # flush remaining complex rows

    # Pass 2: gather results from LLM and place them into the right rows
    for fut in pending_tasks:
        i, res = await fut
        authors_orig_out[i] = res.get("authors_original", [])
        affil_out[i]        = res.get("affiliations", [])

    # Safety: any leftover None -> empty list
    authors_orig_out = [a if a is not None else [] for a in authors_orig_out]
    affil_out   = [b if b is not None else [] for b in affil_out]

    # Only standardize separators between people; keep each name string untouched (except trimming)
    authors_clean = ["; ".join(n.strip() for n in names if n) for names in authors_orig_out]

    df["authors_original"] = authors_orig_out      # list[str] untouched
    df["authors_clean"]    = authors_clean         # single string "name1; name2" ...
    df["affiliations"]     = affil_out

    # Write back to Parquet
    pq.write_table(pa.Table.from_pandas(df), DST_PARQUET)
    print(f"✅ Clean parquet written to {DST_PARQUET} ({len(df)} rows)")


if __name__ == "__main__":
    asyncio.run(main())