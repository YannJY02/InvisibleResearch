"""Join full Source objects and audited language aggregates without collapsing journals.

Route A preserves the original BigQuery row IDs and every original column.
ISSN fallback objects are candidate observations, never asserted historical merges.
Route B preserves the independently enumerated current journal IDs. Both retain
complete arrays and null/missing distinctions, with a portable full-object sidecar.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path

import collect_source_metadata as base
from retry_source_metadata import valid_issn

OWNER = Path(__file__).resolve().parents[1]
ART = OWNER / "artifacts"
BASELINE_SHA = "7c555e0a926510d0efb4c97847c75a45709ff4b3eba6aa37fa84e164d76aca48"
META = ["route", "route_row_id", "source_id", "resolved_id", "source_identity_status",
        "source_fetched_at", "source_content_sha256", "resolved_identity_row_count",
        "scopus_match_issn_json", "scopus_identifier_policy", "language_basis",
        "language_source_id", "language_works_count", "language_known_works_count",
        "language_unknown_works_count", "language_unknown_share", "language_counts_json",
        "language_proportions_json", "language_known_proportions_json", "language_status"]


def read_json(path):
    return base.loads(path.read_bytes())


def read_csv(path):
    opener = gzip.open if path.name.endswith(".gz") else Path.open
    with opener(path, "rt", newline="", encoding="utf-8") as stream:
        yield from csv.DictReader(stream)


def identifiers(obj):
    values = list(obj.get("issn") or [])
    values.append(obj.get("issn_l"))
    return {x for value in values if (x := valid_issn(value))}


def language_value(counts, known, unknown, total):
    if sum(counts.values()) != total or known + unknown != total:
        raise ValueError("Language counts do not reconcile")
    # The unknown category is a reserved key, never a language code.
    if counts.get("__unknown__", 0) != unknown:
        raise ValueError("Unknown category differs from unknown denominator")
    return {"language_works_count": total, "language_known_works_count": known,
            "language_unknown_works_count": unknown,
            "language_unknown_share": unknown / total if total else None,
            "language_counts_json": counts,
            "language_proportions_json": {k: n / total for k, n in counts.items()} if total else {},
            "language_known_proportions_json": {k: n / known for k, n in counts.items()
                                                if k != "__unknown__"} if known else {},
            "language_status": "complete" if total else "no_works"}


def bq_languages(root):
    summary = read_json(root / "summary.json")
    if summary.get("status") != "complete":
        raise ValueError("BigQuery language run is incomplete")
    if summary.get("null_work_ids_in_journal_cohort") != 0 or not summary.get("source_metadata_stable"):
        raise ValueError("BigQuery identity/version audit failed")
    for entry in summary["files"]:
        if base.sha256_file(root / entry["file"]) != entry["sha256"]:
            raise ValueError("BigQuery language input hash differs")
    counts = defaultdict(Counter)
    for row in read_csv(root / "journal-language-counts.csv"):
        key = "__unknown__" if row["language_status"] != "known" else row["language_code"].casefold()
        counts["S" + row["source_id"]][key] += int(row["language_count"])
    values = {}
    for row in read_csv(root / "journal-language-totals.csv"):
        key = "S" + row["source_id"]
        if key in values:
            raise ValueError("Duplicate BigQuery language source")
        values[key] = language_value(dict(sorted(counts[key].items())), int(row["n_known"]),
                                     int(row["n_unknown"]), int(row["n_works"]))
    return values


def api_languages(root):
    audit = read_json(root / "reconciliation.json")
    if audit.get("status") != "complete" or audit["per_source_denominator_mismatches"] != []:
        raise ValueError("API language sum differs from independently fetched denominator")
    if not audit.get("independent_source_totals_checked") or not audit.get("id_only_source_denominators_checked"):
        raise ValueError("API language attribution lacks exhaustive ID-only denominators")
    if audit.get("orphan_source_ids"):
        if (not audit.get("orphan_source_audit_complete")
                or base.sha256_file(root / audit["orphan_source_audit_file"]) != audit["orphan_source_audit_sha256"]
                or base.sha256_file(root / audit["outside_universe_counts_file"]) != audit["outside_universe_counts_sha256"]):
            raise ValueError("Outside-cohort API groups lack verified retained diagnostics")
    independent = read_json(root / audit["id_only_denominator_summary_file"])
    if (independent.get("status") != "complete" or not independent.get("all_batch_keys_and_totals_verified")
            or independent.get("source_type_filter") is not None or independent.get("corpus") != "all"
            or base.sha256_file(root / independent["file"]) != independent["sha256"]):
        raise ValueError("Independent API denominator traversal is incomplete or altered")
    if base.sha256_file(root / audit["file"]) != audit["sha256"]:
        raise ValueError("API reconciled language input hash differs")
    if read_json(root / "languages-summary.json").get("status") != "complete":
        raise ValueError("API language traversal is incomplete")
    values = {}
    for row in read_csv(root / "journal-language-counts.csv.gz"):
        key = base.source_id(row["source_id"])
        if key in values:
            raise ValueError("Duplicate API language source")
        raw = json.loads(row["language_counts_json"])
        counts = Counter()
        for code, n in raw.items():
            counts["__unknown__" if code in ("unknown", "null", "__unknown__") else code.casefold()] += n
        values[key] = language_value(dict(sorted(counts.items())), int(row["known_language_works"]),
                                     int(row["unknown_language_works"]), int(row["works_count"]))
    return values


def original_records(root):
    records = {}
    for path in sorted((root / "checkpoints").glob("batch-*.json")):
        for row in read_json(path)["records"]:
            if row["requested_id"] in records:
                raise ValueError("Duplicate original receipt ID")
            records[row["requested_id"]] = row
    return records


def route_a_inputs():
    original = ART / "source-api-2026-09-30"
    retry = ART / "source-retry-2026-10-01"
    candidate = retry / "candidate-csv"
    for directory in (original, candidate):
        if read_json(directory / "manifest.json").get("verification", {}).get("passed") is not True:
            raise ValueError("Source input has not passed its full verification")
    baseline = ART / "journal-export-2026-01/openalex-journals-2026-01.csv"
    if base.sha256_file(baseline) != BASELINE_SHA:
        raise ValueError("Original baseline hash differs")
    records = original_records(original)
    candidates = {}
    for row in read_csv(retry / "old-source-candidates.csv"):
        if row["candidate_contains_lookup_issn"] != "True":
            raise ValueError("ISSN candidate lacks lookup identifier")
        candidates.setdefault(row["original_id"], set()).add(row["candidate_id"])
    selection = {r["source_id"]: r for r in read_json(candidate / "selection-provenance.json")["selections"]}
    resolved_counts = Counter()
    for key, rec in records.items():
        if rec["status"] in base.SUCCESS:
            resolved_counts[base.source_id(rec["resolved_id"])] += 1
        elif len(candidates.get(key, set())) == 1:
            resolved_counts[next(iter(candidates[key]))] += 1

    def rows():
        for old in read_csv(baseline):
            key = "S" + old["id"]
            rec = records[key]
            historical = {"issn": json.loads(old["issn"]) if old["issn"] not in ("", "\\N") else [],
                          "issn_l": old["issn_l"] if old["issn_l"] != "\\N" else None}
            h_issns = identifiers(historical)
            choices = sorted(candidates.get(key, set()))
            if rec["status"] in base.SUCCESS:
                obj = base.source_from_record(original, rec)
                resolved = base.source_id(obj["id"])
                status = "same_id" if resolved == key else "api_redirect"
                fetched = rec["fetched_at"]
                approved = h_issns | identifiers(obj) if resolved == key else h_issns & identifiers(obj)
                policy = "historical_current_union_same_id" if resolved == key else "historical_current_intersection_redirect"
            elif len(choices) == 1:
                resolved = choices[0]
                chosen = selection[resolved]
                raw = (candidate / "sources" / (resolved + ".json")).read_bytes()
                if hashlib.sha256(raw).hexdigest() != chosen["selected_json_sha256"]:
                    raise ValueError("Candidate object hash differs")
                obj = base.loads(raw)
                if base.source_id(obj["id"]) != resolved:
                    raise ValueError("Candidate ID differs")
                approved = h_issns & identifiers(obj)
                if not approved:
                    raise ValueError("Fallback has no supporting shared ISSN")
                status = "issn_candidate_unconfirmed"
                fetched = chosen["selected_completed_at"]
                policy = "historical_current_intersection_unconfirmed_candidate"
            else:
                obj, resolved, fetched = {}, None, rec["fetched_at"]
                status = "not_found" if not choices else "multiple_candidates_unresolved"
                approved, policy = h_issns, "historical_only_api_unavailable"
            meta = {"route": "A", "route_row_id": key, "source_id": key, "resolved_id": resolved,
                    "source_identity_status": status, "source_fetched_at": fetched,
                    "resolved_identity_row_count": resolved_counts[resolved] if resolved else None,
                    "scopus_match_issn_json": sorted(approved), "scopus_identifier_policy": policy,
                    "language_basis": "bigquery_original_primary_source_id", "language_source_id": key}
            # Original cells are deliberately preserved, including their documented SQL NULL encoding.
            yield meta, obj, {"historical_" + k: v for k, v in old.items()}
    with baseline.open(newline="", encoding="utf-8") as stream:
        historical_fields = ["historical_" + k for k in csv.DictReader(stream).fieldnames]
    fields = sorted(set(read_json(original / "manifest.json")["field_types"]) |
                    set(read_json(candidate / "manifest.json")["field_types"]))
    return rows, fields, historical_fields, len(records)


def route_b_inputs(root):
    summary = read_json(root / "sources-summary.json")
    if summary.get("status") != "complete" or not summary.get("all_attributes_retained"):
        raise ValueError("Current Source enumeration is incomplete")
    path = root / "sources.jsonl.gz"
    if summary["file"] != path.name or base.sha256_file(path) != summary["sha256"]:
        raise ValueError("Current Source enumeration input hash differs")
    fields, rows, seen = set(), 0, set()
    with gzip.open(path, "rb") as stream:
        for line in stream:
            rec = base.loads(line)
            obj = rec["source"]
            key = base.source_id(obj["id"])
            if obj.get("type") != "journal" or key in seen:
                raise ValueError("Current enumeration contains duplicate/nonjournal identity")
            seen.add(key)
            fields.update(base.flatten(obj))
            rows += 1
    if rows != summary["rows"] or rows != summary["meta_count_start"] or rows != summary["meta_count_end"]:
        raise ValueError("Current Source enumeration differs from live censuses")

    def objects():
        with gzip.open(path, "rb") as stream:
            for line in stream:
                rec = base.loads(line)
                obj = rec["source"]
                key = base.source_id(obj["id"])
                yield {"route": "B", "route_row_id": key, "source_id": key, "resolved_id": key,
                       "source_identity_status": "current_api_journal", "source_fetched_at": rec["fetched_at"],
                       "resolved_identity_row_count": 1, "scopus_match_issn_json": sorted(identifiers(obj)),
                       "scopus_identifier_policy": "current_api_identifiers",
                       "language_basis": "current_api_all_corpus_primary_source_id", "language_source_id": key}, obj, {}
    return objects, sorted(fields), [], rows


def build(route, input_root, output):
    output.mkdir(parents=True, exist_ok=True)
    if (output / "summary.json").exists():
        raise FileExistsError("Completed route output already exists")
    if route == "A":
        objects, fields, historical, expected = route_a_inputs()
        langs = bq_languages(input_root)
    else:
        objects, fields, historical, expected = route_b_inputs(input_root)
        langs = api_languages(input_root)
    header = META + fields + historical
    if len(set(header)) != len(header):
        raise ValueError("Column name collision")
    path = output / "journals.pre-scopus.csv.gz"
    raw_path = output / "sources-with-provenance.jsonl.gz"
    schema, statuses, hashes = {}, Counter(), {}
    totals, unknown, no_works, api_missing = 0, 0, 0, 0
    example = {}
    with gzip.open(path, "wt", newline="", encoding="utf-8", compresslevel=1) as stream, gzip.open(raw_path, "wb", compresslevel=1) as raw:
        writer = csv.DictWriter(stream, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        for i, (meta, obj, old) in enumerate(objects(), 1):
            key = meta["route_row_id"]
            if key in hashes:
                raise ValueError("Duplicate cohort row")
            flat = base.flatten(obj)
            if not set(flat).issubset(fields):
                raise ValueError("Unobserved Source field would be dropped")
            for f, val in flat.items():
                schema.setdefault(f, set()).add(base.value_type(val))
            hashes[key] = base.content_hash(obj).hex()
            meta["source_content_sha256"] = hashes[key]
            language = langs.get(key)
            if language is None:
                raise ValueError("Cohort row missing language denominator")
            row = {f: base.encode_cell(flat.get(f, base.MISSING)) for f in fields}
            row.update({k: base.encode_cell(v) for k, v in (meta | language).items()})
            row.update(old)
            writer.writerow(row)
            raw.write(base.dumps({"provenance": meta, "source": obj if obj else None,
                                  "historical_cells": old if old else None}) + b"\n")
            statuses[meta["source_identity_status"]] += 1
            totals += language["language_works_count"]
            unknown += language["language_unknown_works_count"]
            no_works += language["language_works_count"] == 0
            api_missing += not bool(obj)
            if key == "S107737141":
                example = {"source": obj, "language": language, "provenance": meta, "historical_cells": old}
            if i % 20000 == 0:
                print(f"route {route}: wrote {i:,} journal rows", flush=True)
    if i != expected:
        raise ValueError("Final row count differs from input cohort")
    verified, known_rows, identity_duplicates = 0, 0, 0
    for row in read_csv(path):
        key = base.decode_cell(row["route_row_id"])
        reconstructed = {f: base.decode_cell(row[f]) for f in fields if row[f] != "\\M"}
        obj = base.unflatten(reconstructed)
        if base.content_hash(obj).hex() != hashes.pop(key):
            raise ValueError("Complete Source object does not roundtrip through CSV")
        data = {k: base.decode_cell(row[k]) for k in META}
        counts, shares = data["language_counts_json"], data["language_proportions_json"]
        n = data["language_works_count"]
        if sum(counts.values()) != n or (n and abs(sum(shares.values()) - 1) > 1e-10):
            raise ValueError("Exported language denominator/share readback failed")
        if (data["language_unknown_share"] is None) != (n == 0):
            raise ValueError("No-work share must be null")
        known_rows += n > 0
        identity_duplicates += (data["resolved_identity_row_count"] or 0) > 1
        verified += 1
    if hashes or verified != expected:
        raise ValueError("Incomplete CSV readback")
    raw_rows = 0
    with gzip.open(raw_path, "rb") as stream:
        for line in stream:
            rec = base.loads(line)
            if base.content_hash(rec["source"] or {}).hex() != rec["provenance"]["source_content_sha256"]:
                raise ValueError("Raw portable Source record changed")
            raw_rows += 1
    if raw_rows != expected:
        raise ValueError("Portable JSONL missing rows")
    summary = {"route": route, "status": "complete", "completed_at": base.now(),
               "rows": expected, "columns_before_scopus": len(header), "source_fields": fields,
               "source_field_types": {k: sorted(v) for k, v in sorted(schema.items())},
               "source_identity_status_counts": dict(statuses), "api_missing_rows": api_missing,
               "rows_sharing_resolved_identity": identity_duplicates,
               "language_works_total": totals, "unknown_language_works": unknown,
               "journals_with_works": known_rows, "journals_without_works": no_works,
               "language_input": str(input_root.resolve()),
               "language_scope": "All available years and Work types; XPAC included; primary Source only",
               "ratio_denominator": "all unique Works attributed to row's own primary Source, including unknown language",
               "unknown_language_key": "__unknown__", "no_work_ratios": "null; empty distributions",
               "csv_encoding": {"missing": "\\M", "null": "\\N", "escaped_string": "\\S plus JSON string", "arrays_and_maps": "complete compact JSON"},
               "verification": {"passed": True, "all_rows_read_back": verified, "complete_source_roundtrip": True,
                                "portable_jsonl_rows": raw_rows, "language_counts_and_proportions_reconciled": True},
               "files": [{"name": p.name, "bytes": p.stat().st_size, "sha256": base.sha256_file(p)} for p in (path, raw_path)]}
    base.save_json(output / "summary.json", summary)
    base.save_json(output / "example-journal-of-communication.json", example)
    print(base.dumps({k: summary[k] for k in ("route", "rows", "source_identity_status_counts", "language_works_total", "unknown_language_works")}).decode())


if __name__ == "__main__":
    csv.field_size_limit(2**31 - 1)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route", choices=("A", "B"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if "artifacts" not in args.output.parts or args.output.name == "artifacts":
        parser.error("Use a named artifacts directory")
    build(args.route, args.input, args.output)
