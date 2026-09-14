"""Read a complete OpenAlex sources table through the official tabledata API.

This creates no SQL job. Outputs are exploratory candidates until the snapshot
and source-table scope are accepted. Run from the repository root.
"""

import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    for value in (args.project, args.dataset):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
            parser.error("Invalid project or dataset identifier")
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    token = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token", "--quiet"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    base = ("https://bigquery.googleapis.com/bigquery/v2/projects/"
            f"{args.project}/datasets/{args.dataset}/tables/sources")

    def get(url):
        request = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)

    def save(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

    before = get(base)
    save("metadata-before.json", before)
    if before.get("type") != "TABLE":
        raise ValueError("This reader requires a physical table")
    schema = before["schema"]["fields"]
    names = [field["name"] for field in schema]
    if not {"id", "type", "issn", "issn_l"}.issubset(names):
        raise ValueError("Required source identity fields are absent")
    if any(field.get("mode") == "REPEATED" or field["type"] == "RECORD" for field in schema):
        raise ValueError("Nested schema requires an explicit decoding extension")
    expected = int(before["numRows"])
    seen_ids, seen_tokens = set(), set()
    type_counts = collections.Counter()
    fields = {name: collections.Counter() for name in names}
    count = journals = 0
    pages = []
    page_token = None
    raw_path = out / "sources.jsonl.gz.partial"
    journal_path = out / "journals.csv.gz.partial"
    with gzip.open(raw_path, "wt", encoding="utf-8") as raw, gzip.open(
        journal_path, "wt", encoding="utf-8", newline=""
    ) as journal_file:
        writer = csv.DictWriter(journal_file, fieldnames=names)
        writer.writeheader()
        while True:
            params = {"maxResults": 10000}
            if page_token:
                params["pageToken"] = page_token
            page = get(base + "/data?" + urllib.parse.urlencode(params))
            if int(page["totalRows"]) != expected:
                raise ValueError("Table row count changed during pagination")
            rows = page.get("rows", [])
            for row in rows:
                if len(row["f"]) != len(schema):
                    raise ValueError("Row does not match captured schema")
                decoded = {}
                for field, cell in zip(schema, row["f"]):
                    value = cell.get("v")
                    if value is not None:
                        if field["type"] in ("INTEGER", "INT64"):
                            value = int(value)
                        elif field["type"] in ("FLOAT", "FLOAT64"):
                            value = float(value)
                        elif field["type"] in ("BOOLEAN", "BOOL"):
                            if value not in ("true", "false", "True", "False"):
                                raise ValueError("Unexpected boolean representation")
                            value = value.lower() == "true"
                    decoded[field["name"]] = value
                    category = ("null" if value is None else "empty_string" if value == ""
                                else "empty_list_string" if value == "[]" else "present")
                    fields[field["name"]][category] += 1
                if decoded["id"] is None or decoded["id"] in seen_ids:
                    raise ValueError("Missing or duplicate OpenAlex source ID")
                seen_ids.add(decoded["id"])
                type_counts[str(decoded["type"])] += 1
                raw.write(json.dumps(decoded, ensure_ascii=False, allow_nan=False) + "\n")
                if decoded["type"] == "journal":
                    writer.writerow(decoded)
                    journals += 1
                count += 1
            pages.append({"page": len(pages) + 1, "rows": len(rows), "cumulative_rows": count})
            save("pagination.json", pages)
            print(f"Read {count}/{expected} sources; {journals} journals", flush=True)
            page_token = page.get("pageToken")
            if not page_token:
                break
            if not rows or page_token in seen_tokens:
                raise ValueError("Pagination stopped advancing")
            seen_tokens.add(page_token)
    after = get(base)
    save("metadata-after.json", after)
    for key in ("numRows", "numBytes", "lastModifiedTime", "schema"):
        if before[key] != after[key]:
            raise ValueError(f"Table changed during extraction: {key}")
    if count != expected:
        raise ValueError(f"Incomplete extraction: {count} of {expected}")
    raw_path.rename(out / "sources.jsonl.gz")
    journal_path.rename(out / "journals.csv.gz")
    hashes = {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
              for name in ("sources.jsonl.gz", "journals.csv.gz")}
    save("manifest.json", {
        "started_at": started, "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": before["id"], "method": "BigQuery REST tabledata.list; no SQL job",
        "status": "exploratory candidate; snapshot approval and related-table scope pending",
        "schema_fields": len(schema), "source_rows": count, "unique_source_ids": len(seen_ids),
        "journal_filter": "type == journal", "journal_rows": journals,
        "type_counts": dict(type_counts), "field_states_all_sources": fields,
        "metadata_stable_before_after": True, "pages": len(pages), "sha256": hashes,
        "csv_null_encoding": "empty cell; JSONL preserves null versus empty string",
    })


if __name__ == "__main__":
    main()
