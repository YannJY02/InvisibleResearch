"""
download_openalex_by_year.py
============================

This script demonstrates how to use the OpenAlex API with cursor‑based paging to
download all works for a given range of publication years within a specific
subfield.  The example below targets the **Communication** subfield
(OpenAlex identifier `subfields/3315`) and iterates from the year 2000 up to
2025.  For each year, it retrieves every record by requesting successive
pages using the `cursor` parameter and writes the results to a JSON
```.jsonl``` (JSON Lines) file.  A JSON Lines file contains one JSON object per
line, which makes it easy to stream large datasets without loading them all
into memory at once.

Key features of this script include:

- **Cursor paging:** The OpenAlex API limits simple page indexing to the first
  10,000 results.  Cursor paging allows you to fetch all results regardless of
  count.  After requesting the first page with ``cursor=*``, each subsequent
  response provides a ``next_cursor`` token which you should feed into the next
  request.  When ``next_cursor`` is ``None``, you have reached the end of the
  result set.
- **Contact information:** OpenAlex requests that heavy users provide a
  contact email address via the ``mailto`` query parameter.  This example
  supplies a placeholder email; you should replace ``YOUR_EMAIL@example.com`` with
  your actual address.
- **Count validation:** The script records the ``meta['count']`` value
  reported by the API and verifies that the number of retrieved records
  matches this count.  If there is a discrepancy, it prints a warning.

Usage
-----

Run the script from a terminal with Python 3 installed.  You can adjust
``START_YEAR``, ``END_YEAR`` or the ``SUBFIELD_ID`` constants to suit your
needs.  By default, it will create a folder named ``openalex_communication``
in the current working directory and populate it with ``communication_works_<year>.jsonl``
files.

Example::

    python download_openalex_by_year.py

Note: depending on your internet connection and the number of records per
year, downloading all data from 2000–2025 can take a significant amount of
time.  Consider limiting the year range or running the script in smaller
batches if you encounter rate limits (the API allows up to 100,000 requests
per day).
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Iterator, Dict, Any

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Replace this with your actual email address.  OpenAlex uses it to contact
# you if needed.  Supplying the ``mailto`` parameter is considered good
# etiquette when making large numbers of API requests.
CONTACT_EMAIL = "jinyi.yang@student.uva.nl"

# The OpenAlex subfield identifier for Communication.  See
# https://openalex.org/subfields/3315 for details.
SUBFIELD_ID = "subfields/3315"

# Range of years to download (inclusive)
START_YEAR = 2000
END_YEAR = 2025

# Number of records per page (max 200).  A higher value reduces the number
# of requests but increases response size.
PER_PAGE = 200

# Directory where output files will be saved
OUTPUT_DIR = "openalex_communication"


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def fetch_page(year: int, cursor: str = "*") -> Dict[str, Any]:
    """Fetch a single page of results for a given year and cursor.

    Args:
        year: Publication year to filter by.
        cursor: Cursor token returned by the previous page.  Use "*" for the
            first page.

    Returns:
        Parsed JSON response from the API.
    """
    base_url = "https://api.openalex.org/works"
    filters = f"primary_topic.subfield.id:{SUBFIELD_ID},publication_year:{year}"
    params = {
        "filter": filters,
        "per-page": PER_PAGE,
        "cursor": cursor,
        "mailto": CONTACT_EMAIL,
    }
    response = requests.get(base_url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def iterate_year(year: int) -> Iterator[Dict[str, Any]]:
    """Iterate over all works for a given year.

    This generator yields each work dictionary one at a time by
    transparently handling cursor paging.

    Args:
        year: Publication year to iterate over.

    Yields:
        Individual work JSON objects as returned by the OpenAlex API.
    """
    cursor = "*"
    total_retrieved = 0
    meta_count = None
    while True:
        data = fetch_page(year, cursor=cursor)
        if meta_count is None:
            meta_count = data["meta"]["count"]
            print(f"Year {year}: expected {meta_count} works")
        results = data.get("results", [])
        for work in results:
            total_retrieved += 1
            yield work
        # obtain next cursor
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        # polite pacing between requests
        time.sleep(0.5)
    # Validate count
    if meta_count is not None and total_retrieved != meta_count:
        print(
            f"WARNING: Retrieved {total_retrieved} works for {year}, "
            f"but meta.count reported {meta_count}."
        )
    else:
        print(f"Validated {total_retrieved} works for {year} (counts match)")


def save_year_data(year: int, directory: str) -> None:
    """Download all works for a given year and save them to a JSON Lines file.

    Args:
        year: The publication year to download.
        directory: Folder where the output file will be stored.  This folder
            must exist prior to calling this function.
    """
    filename = f"communication_works_{year}.jsonl"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        for work in iterate_year(year):
            json_line = json.dumps(work, ensure_ascii=False)
            f.write(json_line + "\n")
    print(f"Saved data for {year} to {filepath}")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(
        f"Downloading works for subfield {SUBFIELD_ID} "
        f"from {START_YEAR} through {END_YEAR}..."
    )
    start_time = datetime.now()
    for year in range(START_YEAR, END_YEAR + 1):
        try:
            save_year_data(year, OUTPUT_DIR)
        except Exception as exc:
            print(f"Error downloading data for {year}: {exc}")
    elapsed = datetime.now() - start_time
    print(f"Completed downloads in {elapsed}")


if __name__ == "__main__":
    main()