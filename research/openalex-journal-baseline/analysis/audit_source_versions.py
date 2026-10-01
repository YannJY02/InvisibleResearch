"""Read-only census of the fixed BigQuery journal cohort and live Source API.

The BigQuery census is dry-run checked separately. This helper reads the local
January-labelled export and uses only three small live API list requests.
It does not mutate the accepted export or infer that absent IDs were deleted.
"""

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

from collect_source_metadata import (Client, MISSING, api_key, atomic_bytes,
                                     decode_cell, dumps, now, source_id)


class HashingReader(io.RawIOBase):
    """Hash the accepted file's exact bytes while the CSV parser consumes them."""

    def __init__(self, stream):
        self.stream = stream
        self.digest = hashlib.sha256()
        self.byte_count = 0

    def readable(self):
        return True

    def readinto(self, buffer):
        count = self.stream.readinto(buffer)
        if count:
            self.digest.update(memoryview(buffer)[:count])
            self.byte_count += count
        return count


def accepted_csv_profile(path, output):
    expected = json.loads((path.parent / "manifest.json").read_bytes())
    statuses, returned_types = Counter(), Counter()
    requested, resolved = set(), set()
    resolved_by_type = {}
    minimum_fetched = maximum_fetched = None
    started_at = now()
    csv.field_size_limit(sys.maxsize)
    with path.open("rb", buffering=0) as raw:
        hashing = HashingReader(raw)
        with io.TextIOWrapper(io.BufferedReader(hashing, buffer_size=8 * 1024 * 1024),
                              encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            columns = reader.fieldnames
            for row in reader:
                requested_id = source_id(row["source_id"])
                if requested_id in requested:
                    raise ValueError("Duplicate requested ID in accepted CSV")
                requested.add(requested_id)
                statuses[row["fetch_status"]] += 1
                if row["fetch_status"] not in {"ok", "redirected"}:
                    continue
                resolved_id = source_id(row["resolved_id"])
                if source_id(decode_cell(row["id"])) != resolved_id:
                    raise ValueError("Source id and resolved_id disagree")
                resolved.add(resolved_id)
                source_type = decode_cell(row["type"])
                if source_type is MISSING:
                    source_type = "__MISSING__"
                elif source_type is None:
                    source_type = "__NULL__"
                elif not isinstance(source_type, str):
                    raise ValueError("Returned Source type is not a string")
                returned_types[source_type] += 1
                resolved_by_type.setdefault(source_type, set()).add(resolved_id)
                fetched = row["fetched_at"]
                minimum_fetched = min(minimum_fetched, fetched) if minimum_fetched else fetched
                maximum_fetched = max(maximum_fetched, fetched) if maximum_fetched else fetched
    actual_hash = hashing.digest.hexdigest()
    if actual_hash != expected["csv"]["sha256"]:
        raise ValueError("Accepted CSV hash does not match its original manifest")
    if len(requested) != expected["requested_sources"]:
        raise ValueError("Accepted CSV rows do not match its cohort manifest")
    successful_rows = sum(returned_types.values())
    ids_payload = ("\n".join(sorted(resolved, key=lambda value: int(value[1:]))) + "\n").encode()
    atomic_bytes(output / "accepted-success-resolved-ids.txt", ids_payload)
    summary = {"audit_started_at": started_at, "audit_completed_at": now(),
               "accepted_csv": str(path.resolve()), "csv_sha256": actual_hash,
               "csv_bytes": hashing.byte_count, "hash_verified_against_original_manifest": True,
               "single_stream_read": True, "columns": len(columns),
               "requested_rows": len(requested), "status_counts": dict(statuses),
               "successful_rows": successful_rows, "successful_returned_type_rows": dict(returned_types),
               "successful_unique_resolved_ids": len(resolved),
               "successful_unique_resolved_ids_by_returned_type": {
                   key: len(value) for key, value in resolved_by_type.items()},
               "successful_rows_still_journal": returned_types["journal"],
               "successful_rows_changed_type": successful_rows - returned_types["journal"],
               "successful_duplicate_resolved_id_rows": successful_rows - len(resolved),
               "successful_fetch_time_range": {"minimum": minimum_fetched, "maximum": maximum_fetched},
               "original_run_started_at": expected.get("started_at"),
               "original_run_completed_at": expected.get("completed_at"),
               "resolved_ids_file": "accepted-success-resolved-ids.txt",
               "resolved_ids_file_sha256": hashlib.sha256(ids_payload).hexdigest(),
               "resolved_ids_file_encoding": "numeric-sorted short S IDs, UTF-8, LF, final LF",
               "limits": "Successful Sept 30 responses for the fixed older cohort, not an Oct 1 "
                         "universe enumeration. Different retrieval dates prohibit interpreting "
                         "the current journal census minus these unique journal IDs as exact additions."}
    atomic_bytes(output / "accepted-csv-success-profile.json", dumps(summary))
    return summary


def original_null(value):
    # The accepted BigQuery CSV uses the literal two-backslash sentinel \\N.
    return value in {"", "\\N", "\\\\N", "null"}


def valid_issn(value):
    text = str(value or "").strip().upper()
    if not re.fullmatch(r"\d{4}-\d{3}[\dX]", text):
        return False
    digits = text.replace("-", "")
    total = sum(int(digits[i]) * (8 - i) for i in range(7))
    check = (11 - total % 11) % 11
    return digits[7] == ("X" if check == 10 else str(check))


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def historical_issn_peers(export, original_run, output):
    """Compare ISSN co-occurrence inside the same historical journal cohort.

    Identifier sharing is an observation, never a confirmed journal identity.
    Read the historical CSV once while hashing its original bytes.
    """
    started_at = now()
    missing, original_success_to_resolved = set(), {}
    for path in sorted((original_run / "checkpoints").glob("batch-*.json")):
        for receipt in json.loads(path.read_bytes())["records"]:
            key = source_id(receipt["requested_id"])
            if receipt["status"] == "not_found":
                missing.add(key)
            elif receipt["status"] in {"ok", "redirected"}:
                original_success_to_resolved[key] = source_id(receipt["resolved_id"])
    accepted_profile = json.loads((output / "accepted-csv-success-profile.json").read_bytes())
    accepted_raw = (output / "accepted-success-resolved-ids.txt").read_bytes()
    if hashlib.sha256(accepted_raw).hexdigest() != accepted_profile["resolved_ids_file_sha256"]:
        raise ValueError("Accepted successful ID index hash mismatch")
    accepted = set(accepted_raw.decode().splitlines())
    if set(original_success_to_resolved.values()) != accepted:
        raise ValueError("Original successful receipts and accepted resolved IDs differ")
    original_profile = json.loads((output / "original-cohort-profile.json").read_bytes())
    owners, missing_issns, cohort_ids = {}, {}, set()
    csv.field_size_limit(sys.maxsize)
    with export.open("rb", buffering=0) as raw:
        hashing = HashingReader(raw)
        with io.TextIOWrapper(io.BufferedReader(hashing, buffer_size=8 * 1024 * 1024),
                              encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                key = source_id(row["id"])
                if key in cohort_ids:
                    raise ValueError("Historical journal cohort has a duplicate Source ID")
                cohort_ids.add(key)
                values = [] if original_null(row["issn"]) else json.loads(row["issn"])
                if not isinstance(values, list):
                    raise ValueError("Historical issn field is not a JSON list")
                if not original_null(row["issn_l"]):
                    values.append(row["issn_l"])
                identifiers = {str(value).strip().upper() for value in values if valid_issn(value)}
                for identifier in identifiers:
                    owners.setdefault(identifier, set()).add(key)
                if key in missing:
                    missing_issns[key] = identifiers
    baseline_hash = hashing.digest.hexdigest()
    if baseline_hash != original_profile["original_export_sha256"]:
        raise ValueError("Historical CSV hash differs from the verified original profile")
    successful = set(original_success_to_resolved)
    if (missing & successful or cohort_ids != (missing | successful)
            or len(missing_issns) != len(missing)):
        raise ValueError("Historical cohort is not partitioned by its original acquisition receipts")
    counts = Counter({key: 0 for key in (
        "no_valid_historical_issn", "shares_historical_issn_with_successful_old_id",
        "shares_historical_issn_only_with_other_not_found_old_ids",
        "historical_issns_unique_within_old_cohort")})
    both_peer_groups = 0
    peer_success_ids = set()
    columns = ["original_id", "historical_issns_json", "peer_outcome",
               "successful_peer_old_ids_json", "successful_peer_resolved_ids_json",
               "not_found_peer_old_ids_json"]
    rows = []
    numeric = lambda value: int(value[1:])
    for key in sorted(missing, key=numeric):
        identifiers = missing_issns[key]
        if not identifiers:
            counts["no_valid_historical_issn"] += 1
            continue
        peers = set().union(*(owners[identifier] for identifier in identifiers)) - {key}
        success_peers, missing_peers = peers & successful, peers & missing
        peer_success_ids.update(success_peers)
        if success_peers:
            outcome = "shares_historical_issn_with_successful_old_id"
            both_peer_groups += bool(missing_peers)
        elif missing_peers:
            outcome = "shares_historical_issn_only_with_other_not_found_old_ids"
        else:
            outcome = "historical_issns_unique_within_old_cohort"
        counts[outcome] += 1
        rows.append(dict(zip(columns, [key, json.dumps(sorted(identifiers)), outcome,
                    json.dumps(sorted(success_peers, key=numeric)),
                    json.dumps(sorted({original_success_to_resolved[value] for value in success_peers}, key=numeric)),
                    json.dumps(sorted(missing_peers, key=numeric))])))
    path = output / "original-404-historical-issn-peers.csv"
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with temporary.open(encoding="utf-8", newline="") as stream:
        if list(csv.DictReader(stream)) != rows:
            raise ValueError("Historical ISSN peer CSV full readback differs from its rows")
    temporary.replace(path)
    summary = {"audit_started_at": started_at, "audit_completed_at": now(),
               "original_export_sha256": baseline_hash, "single_original_csv_stream_read": True,
               "original_export_bytes": hashing.byte_count, "cohort_source_ids": len(cohort_ids),
               "original_not_found_ids": len(missing), "original_successful_ids": len(successful),
               "accepted_successful_resolved_ids": len(accepted),
               "accepted_id_index_sha256": hashlib.sha256(accepted_raw).hexdigest(),
               "unique_valid_historical_issns_in_cohort": len(owners),
               "not_found_ids_with_any_valid_historical_issn": len(rows),
               "counts": dict(counts),
               "successful_peer_and_not_found_peer": both_peer_groups,
               "unique_successful_old_peer_ids": len(peer_success_ids),
               "csv": {"filename": path.name, "rows": len(rows), "columns": len(columns),
                       "bytes": path.stat().st_size, "sha256": file_hash(path),
                       "all_rows_read_back_equal": True},
               "interpretation": "Co-occurring historical identifiers in the same old cohort. "
                                 "Sharing an ISSN does not prove same journal, merger, replacement "
                                 "or that a live ISSN lookup resolves to this historical peer.",
               "success_basis": "Original Sep 30 successful requested IDs, cross-checked through "
                                "their resolved IDs against the full verified accepted CSV index."}
    atomic_bytes(output / "historical-issn-peer-summary.json", dumps(summary))
    return summary


def historical_candidate_examples(export, ids, output):
    requested = {source_id(key) for key in ids}
    columns = ["id", "display_name", "type", "issn_l", "issn", "works_count",
               "created_date", "updated_date"]
    found = {}
    csv.field_size_limit(sys.maxsize)
    with export.open("rb", buffering=0) as raw:
        hashing = HashingReader(raw)
        with io.TextIOWrapper(io.BufferedReader(hashing, buffer_size=8 * 1024 * 1024),
                              encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                key = source_id(row["id"])
                if key in requested:
                    found[key] = {column: row[column] for column in columns}
    if set(found) != requested:
        raise ValueError("Some requested example IDs are absent from the historical journal cohort")
    expected = json.loads((output / "original-cohort-profile.json").read_bytes())
    if hashing.digest.hexdigest() != expected["original_export_sha256"]:
        raise ValueError("Historical example CSV hash differs from the verified original profile")
    result = {"audit_completed_at": now(), "baseline_sha256": hashing.digest.hexdigest(),
              "core_columns": columns, "historical_csv_core_fields": found,
              "interpretation": "These are historical CSV values only; current candidate links "
                                "do not prove historical ISSN equality or confirmed merger."}
    atomic_bytes(output / "historical-candidate-examples.json", dumps(result))
    return result


def profile(export, original_run):
    missing_ids = set()
    status_counts = Counter()
    for path in sorted((original_run / "checkpoints").glob("batch-*.json")):
        for record in json.loads(path.read_bytes())["records"]:
            status_counts[record["status"]] += 1
            if record["status"] == "not_found":
                missing_ids.add(record["requested_id"])
    counters = {"all_journals": Counter(), "original_not_found": Counter()}
    ids = set()
    missing_seen = set()
    ranges = {"created_date": [], "updated_date": [], "updated": []}
    csv.field_size_limit(sys.maxsize)
    with export.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            source_id = "S" + row["id"]
            if source_id in ids:
                raise ValueError("Duplicate original Source ID")
            ids.add(source_id)
            groups = [counters["all_journals"]]
            if source_id in missing_ids:
                groups.append(counters["original_not_found"])
                missing_seen.add(source_id)
            raw_issn = row["issn"].strip()
            issns = [] if original_null(raw_issn) else json.loads(raw_issn)
            if not isinstance(issns, list):
                raise ValueError("Original issn field is not a JSON list")
            issn_l = row["issn_l"].strip()
            issn_l = "" if original_null(issn_l) else issn_l
            works = None if original_null(row["works_count"]) else int(row["works_count"])
            for counts in groups:
                counts["rows"] += 1
                counts["nonempty_issn_l"] += bool(issn_l)
                counts["valid_issn_l"] += valid_issn(issn_l)
                counts["nonempty_issn_array"] += bool(issns)
                counts["any_valid_issn_array"] += any(valid_issn(v) for v in issns)
                counts["any_valid_identifier"] += (valid_issn(issn_l) or
                                                   any(valid_issn(v) for v in issns))
                counts["positive_works_count"] += works is not None and works > 0
                counts["zero_works_count"] += works == 0
                counts["null_works_count"] += works is None
            for key in ranges:
                if not original_null(row[key]):
                    ranges[key].append(row[key])
    if missing_seen != missing_ids:
        raise ValueError("The export does not contain all original 404 IDs")
    return {"checked_at": now(), "original_export": str(export),
            "original_export_bytes": export.stat().st_size,
            "original_export_sha256": file_hash(export),
            "original_acquisition_status_counts": dict(status_counts),
            "groups": {key: dict(value) for key, value in counters.items()},
            "date_ranges": {key: {"minimum": min(values), "maximum": max(values)}
                            for key, values in ranges.items()},
            "issn_validation": "ISO ISSN shape plus modulus-11 check digit; "
                               "any_valid_identifier includes ISSN-L or ISSN array",
            "interpretation": "Fixed January-labelled cohort; its ID failures "
                              "are not a census of the live API universe."}


def live_census(output, env_file):
    client = Client(api_key(env_file), rate=2, attempts=4, max_list_requests=12)
    budget = client.free_budget(3)
    atomic_bytes(output / "budget-before.json", dumps(budget))
    queries = [
        ("all-sources", {"per_page": 1,
                         "select": "id,type,issn_l,created_date,updated_date"}),
        ("journal-sources", {"per_page": 1, "filter": "type:journal",
                             "select": "id,type,issn_l,created_date,updated_date"}),
        ("source-types", {"group_by": "type", "per_page": 100}),
    ]
    receipts = []
    for label, params in queries:
        response = client.get("/sources", params=params, kind="list")
        payload = dumps(response)
        atomic_bytes(output / (label + ".json"), payload)
        # The authenticated key is supplied in a header, never in the query URL.
        receipts.append({"query": label, "retrieved_at": now(),
                         "url": "https://api.openalex.org/sources?" + urlencode(params),
                         "response_json_sha256": hashlib.sha256(payload).hexdigest(),
                         "hash_encoding": "parsed response serialized as compact UTF-8 JSON",
                         "meta": response.get("meta"),
                         "group_by": response.get("group_by")})
    atomic_bytes(output / "api-census.json", dumps({"receipts": receipts,
                 "requests": dict(client.requests), "free_budget": budget,
                 "interpretation": "Live retrieval, not a January snapshot or "
                 "net additions/deletions calculation."}))
    return receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--original-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--local-only", action="store_true")
    parser.add_argument("--accepted-csv-only", action="store_true",
                        help="Only stream and audit original-run/sources.csv; no API or BigQuery calls")
    parser.add_argument("--issn-peers-only", action="store_true",
                        help="Only audit historical ISSN sharing against the accepted successful ID index")
    parser.add_argument("--historical-example-id", action="append", default=[],
                        help="Repeat to capture selected historical core identity rows without API calls")
    args = parser.parse_args()
    args.output = args.output.resolve()
    if "artifacts" not in args.output.parts or args.output.name == "artifacts":
        raise ValueError("A named artifacts output directory is required")
    if args.output.is_relative_to(args.original_run.resolve()):
        raise ValueError("Version audit output must not be inside the accepted original run")
    args.output.mkdir(parents=True, exist_ok=True)
    if sum([args.accepted_csv_only, args.issn_peers_only, bool(args.historical_example_id)]) > 1:
        parser.error("Choose only one local diagnostic mode")
    if args.historical_example_id:
        print(json.dumps(historical_candidate_examples(args.export, args.historical_example_id, args.output)))
        return
    if args.issn_peers_only:
        print(json.dumps(historical_issn_peers(args.export, args.original_run, args.output)))
        return
    if args.accepted_csv_only:
        print(json.dumps(accepted_csv_profile(args.original_run / "sources.csv", args.output)))
        return
    local = profile(args.export, args.original_run)
    atomic_bytes(args.output / "original-cohort-profile.json", dumps(local))
    print(json.dumps({"local_groups": local["groups"],
                      "date_ranges": local["date_ranges"]}, ensure_ascii=False))
    if not args.local_only:
        print(json.dumps(live_census(args.output, args.env_file), ensure_ascii=False))


if __name__ == "__main__":
    main()
