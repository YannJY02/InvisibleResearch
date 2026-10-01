"""Bounded feasibility checks; no BigQuery cohort and no full-corpus download."""

import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import time

import requests

from collect_source_metadata import api_key


API = "https://api.openalex.org"
BUCKET = "https://openalex.s3.amazonaws.com/"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if "artifacts" not in args.output.parts or args.output.name == "artifacts":
        parser.error("Use a named directory beneath artifacts")
    args.output.mkdir(parents=True, exist_ok=False)
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + api_key(Path(".env"))
    observations = []

    def get(label, url, params=None, authenticated=True):
        start = time.monotonic()
        # Snapshot requests are anonymous; never send the API credential to S3.
        client = session if authenticated else requests
        response = client.get(url, params=params, timeout=60)
        response.raise_for_status()
        (args.output / label).write_bytes(response.content)
        observations.append({"file": label, "status": response.status_code,
                             "bytes": len(response.content),
                             "sha256": hashlib.sha256(response.content).hexdigest(),
                             "elapsed_seconds": time.monotonic() - start,
                             "url": url, "params": params,
                             "etag": response.headers.get("ETag")})
        return response

    summary = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "scope": "three Source cursor pages, snapshot partition, language aggregation and Source-group samples"}
    cursor = "*"
    ids, field_sets, pages = set(), set(), []
    for index in range(3):
        data = get(f"api-page-{index + 1}.json", API + "/sources",
                   {"filter": "type:journal", "per_page": 100, "cursor": cursor}).json()
        rows = data["results"]
        assert len(rows) == 100 and all(row["type"] == "journal" for row in rows)
        new_ids = {row["id"] for row in rows}
        assert len(new_ids) == 100 and not ids.intersection(new_ids)
        ids.update(new_ids)
        field_sets.update(tuple(sorted(row)) for row in rows)
        next_cursor = data["meta"]["next_cursor"]
        assert next_cursor and next_cursor != cursor
        pages.append({"count": data["meta"]["count"], "rows": len(rows),
                      "cost_usd": data["meta"].get("cost_usd")})
        cursor = next_cursor
    summary["api"] = {"pages": pages, "unique_ids": len(ids),
                      "field_counts": sorted({len(keys) for keys in field_sets}),
                      "complete_enumeration": False}

    manifests = {}
    for entity in ("sources", "works"):
        manifest = get(f"{entity}-manifest.json", BUCKET +
                       f"data/jsonl/{entity}/manifest.json", authenticated=False).json()
        assert sum(f["meta"]["record_count"] for f in manifest["files"]) == manifest["record_count"]
        assert sum(f["meta"]["content_length"] for f in manifest["files"]) == manifest["content_length"]
        manifests[entity] = manifest
        summary[entity + "_snapshot"] = {key: manifest[key] for key in
                                         ("date", "record_count", "content_length")}
        summary[entity + "_snapshot"]["files"] = len(manifest["files"])
    get("release-notes.txt", BUCKET + "RELEASE_NOTES.txt", authenticated=False)
    small_files = [f for f in manifests["sources"]["files"]
                   if f["meta"]["content_length"] <= 1_000_000]
    sample = max(small_files, key=lambda f: f["url"])
    raw = get("snapshot-sample.gz", sample["url"].replace("s3://openalex/", BUCKET),
              authenticated=False).content
    records = [json.loads(line) for line in gzip.decompress(raw).splitlines()]
    assert len(raw) == sample["meta"]["content_length"]
    assert len(records) == sample["meta"]["record_count"]
    source = next(row for row in records if row["type"] == "journal")
    current = get("sample-source-current.json", API + "/sources/" +
                  source["id"].rsplit("/", 1)[1]).json()
    summary["snapshot_sample"] = {"file": sample, "rows": len(records),
                                  "journal_id": source["id"],
                                  "snapshot_fields": sorted(source),
                                  "api_only_fields": sorted(set(current) - set(source)),
                                  "snapshot_only_fields": sorted(set(source) - set(current))}
    # A known journal tests the research-required language endpoint, not cohort selection.
    params = {"filter": "primary_location.source.id:S107737141,publication_year:2020-2024",
              "group_by": "language:include_unknown", "per_page": 100, "cursor": "*"}
    data = get("language-groups.json", API + "/works", params).json()
    groups = list(data["group_by"])
    language_cost = data["meta"].get("cost_usd", 0)
    group_cursors = {"*"}
    group_pages = 1
    while data["meta"].get("next_cursor"):
        params["cursor"] = data["meta"]["next_cursor"]
        assert params["cursor"] not in group_cursors
        group_cursors.add(params["cursor"])
        group_pages += 1
        assert group_pages <= 10  # This is a bounded example, not a cohort pipeline.
        data = get(f"language-groups-{group_pages}.json", API + "/works", params).json()
        groups.extend(data["group_by"])
        language_cost += data["meta"].get("cost_usd", 0)
    assert sum(row["count"] for row in groups) == data["meta"]["count"]
    assert not data["meta"].get("next_cursor")
    summary["language_example"] = {"filter": params["filter"], "corpus": "API default",
                                   "works": data["meta"]["count"], "groups": groups,
                                   "cost_usd": language_cost, "pages": group_pages,
                                   "window_status": "feasibility example, not an accepted analysis window"}
    # Invert the aggregation for a full cohort: enumerate languages, then Sources
    # within each language, instead of one request for each individual journal.
    by_source = get("english-source-groups.json", API + "/works",
                    {"filter": "primary_location.source.type:journal,language:en,publication_year:2020-2024",
                     "group_by": "primary_location.source.id", "per_page": 100,
                     "cursor": "*"}).json()
    first_group = by_source["group_by"][0]
    source_id = first_group["key"].rsplit("/", 1)[1]
    check = get("english-first-source-check.json", API + "/works",
                {"filter": f"primary_location.source.id:{source_id},language:en,publication_year:2020-2024",
                 "per_page": 1, "select": "id"}).json()
    assert check["meta"]["count"] == first_group["count"]
    summary["language_by_source"] = {"total_english_works": by_source["meta"]["count"],
                                     "first_page_sources": len(by_source["group_by"]),
                                     "first_group": first_group, "independent_count_matches": True,
                                     "has_next_cursor": bool(by_source["meta"].get("next_cursor")),
                                     "complete_enumeration": False}
    unknown = get("unknown-language-source-groups.json", API + "/works",
                  {"filter": "primary_location.source.type:journal,language:null,publication_year:2020-2024",
                   "group_by": "primary_location.source.id", "per_page": 100,
                   "cursor": "*"}).json()
    unknown_check = None
    if unknown["group_by"]:
        unknown_group = unknown["group_by"][0]
        unknown_id = unknown_group["key"].rsplit("/", 1)[1]
        unknown_check = get("unknown-first-source-check.json", API + "/works",
                            {"filter": f"primary_location.source.id:{unknown_id},language:null,publication_year:2020-2024",
                             "per_page": 1, "select": "id"}).json()["meta"]["count"]
        assert unknown_check == unknown_group["count"]
    summary["unknown_language_by_source"] = {"works": unknown["meta"]["count"],
                                             "first_page_sources": len(unknown["group_by"]),
                                             "first_group": unknown["group_by"][:1],
                                             "independent_count": unknown_check,
                                             "complete_enumeration": False}
    after = get("sources-manifest-after.json", BUCKET +
                "data/jsonl/sources/manifest.json", authenticated=False).json()
    assert after == manifests["sources"]
    summary["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    summary["requests"] = observations
    summary["status"] = "bounded_checks_passed"
    (args.output / "probe-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "requests"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
