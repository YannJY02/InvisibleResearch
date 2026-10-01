#!/usr/bin/env python3
"""Enrich either journal cohort with the pinned August 2026 Scopus reference.

All input columns and row order survive. Exact valid ISSNs provide candidate
links, not adjudicated historical identity or proof of never being indexed.
The two labels describe the reference workbook only; they are not model labels.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from match_scopus import (
    BASE, REFERENCE_NAME, REFERENCE_SHA256, REFERENCE_URL,
    build_candidates, dumps, load_reference, normalize_issn, sha256, write_json,
)


EXTRA_FIELDS = [
    "scopus_valid_issns_json", "scopus_invalid_issns_json",
    "scopus_identifier_fields_json", "scopus_match_status",
    "scopus_candidate_count", "scopus_candidate_ids_json",
    "scopus_matched_issns_json", "scopus_candidates_json",
    "scopus_source_types_json", "scopus_has_status_conflict",
    "scopus_has_discontinued_evidence", "scopus_accepted_pending_json",
    "scopus_membership_in_reference", "scopus_active_journal_in_reference",
    "scopus_reference_version",
]


def identifiers(row: dict, fields: tuple[str, ...]) -> tuple[list[str], list[dict], dict]:
    valid, invalid, origins = set(), [], defaultdict(set)
    for field in fields:
        raw = row.get(field)
        if raw is None or raw in ("", "\\N", "null"):
            continue
        if isinstance(raw, str) and raw.lstrip().startswith("["):
            raw = json.loads(raw)
        values = raw if isinstance(raw, list) else [raw]
        for value in values:
            normalized, reason = normalize_issn(value)
            if normalized:
                valid.add(normalized)
                origins[normalized].add(field)
            elif reason != "missing":
                invalid.append({"field": field, "raw": value, "reason": reason})
    return sorted(valid), invalid, {key: sorted(values) for key, values in sorted(origins.items())}


class ReferenceMatcher:
    def __init__(self, records: list[dict], accepted: list[dict]):
        self.index, self.grouped = defaultdict(set), defaultdict(list)
        self.pending = defaultdict(list)
        for record in records:
            key = ("id:" + record["source_id"] if record["source_id"]
                   else f"row:{record['sheet']}:{record['excel_row']}")
            self.grouped[key].append(record)
            for issn in record["valid_issns"]:
                self.index[issn].add(key)
        for record in accepted:
            for issn in record["valid_issns"]:
                self.pending[issn].append(record)

    @classmethod
    def from_workbook(cls, path: Path) -> tuple[ReferenceMatcher, dict]:
        if sha256(path) != REFERENCE_SHA256:
            raise ValueError("Scopus workbook hash differs from pinned August 2026 reference")
        records, accepted, inventory = load_reference(path)
        return cls(records, accepted), inventory

    def match_row(self, row: dict, fields: tuple[str, ...] = ("issn", "issn_l")) -> dict:
        valid, invalid, origins = identifiers(row, fields)
        candidates = build_candidates(valid, self.index, self.grouped)
        pending = {f"{r['sheet']}:{r['excel_row']}": r
                   for issn in valid for r in self.pending.get(issn, [])}
        unknown_identity = any(not candidate["source_id"] for candidate in candidates)
        status = ("no_valid_issn" if not valid else "not_listed_in_reference" if not candidates
                  else "matched_multiple" if len(candidates) > 1
                  else "matched_identity_unknown" if unknown_identity
                  else "matched_" + candidates[0]["candidate_status"])
        membership, active_journal = "", ""
        if valid and not candidates:
            # A reproducible reference-absence observation, not a non-indexing label.
            membership, active_journal = "0", "0"
        elif len(candidates) == 1 and not unknown_identity:
            membership = "1"
            candidate = candidates[0]
            types, state = candidate["source_types"], candidate["candidate_status"]
            if not candidate["status_conflict"]:
                if types and "Journal" not in types:
                    active_journal = "0"
                elif types == ["Journal"] and state in {"active", "inactive"}:
                    active_journal = "1" if state == "active" else "0"
        return {
            "scopus_valid_issns_json": dumps(valid),
            "scopus_invalid_issns_json": dumps(invalid),
            "scopus_identifier_fields_json": dumps(origins),
            "scopus_match_status": status,
            "scopus_candidate_count": str(len(candidates)),
            "scopus_candidate_ids_json": dumps(sorted({c["source_id"] for c in candidates if c["source_id"]})),
            "scopus_matched_issns_json": dumps(sorted({i for c in candidates for i in c["matched_issns"]})),
            "scopus_candidates_json": dumps(candidates),
            "scopus_source_types_json": dumps(sorted({t for c in candidates for t in c["source_types"]})),
            "scopus_has_status_conflict": str(any(c["status_conflict"] for c in candidates)).lower(),
            "scopus_has_discontinued_evidence": str(any(c["has_discontinued_evidence"] for c in candidates)).lower(),
            "scopus_accepted_pending_json": dumps(list(pending.values())),
            "scopus_membership_in_reference": membership,
            "scopus_active_journal_in_reference": active_journal,
            "scopus_reference_version": "2026-08",
        }


def open_csv(path: Path, mode: str):
    return (gzip.open(path, mode + "t", encoding="utf-8", newline="") if path.suffix == ".gz"
            else path.open(mode, encoding="utf-8", newline=""))


def match_file(input_path: Path, output_path: Path, matcher: ReferenceMatcher,
               route_name: str, id_field: str = "id",
               issn_fields: tuple[str, ...] = ("issn", "issn_l")) -> dict:
    """Stream a route CSV; identify rows by cohort ID, not a possibly shared API ID."""
    csv.field_size_limit(20 * 1024 * 1024)
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output must differ")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_name("partial-" + output_path.name)
    seen, statuses, memberships, active_labels, usage = set(), Counter(), Counter(), Counter(), Counter()
    ids_hash, rows = hashlib.sha256(), 0
    with open_csv(input_path, "r") as source, open_csv(partial, "w") as destination:
        reader = csv.DictReader(source)
        original_fields = reader.fieldnames or []
        if set(original_fields) & set(EXTRA_FIELDS):
            raise ValueError("Input already contains Scopus enrichment fields")
        if id_field not in original_fields or any(field not in original_fields for field in issn_fields):
            raise ValueError("Configured ID or ISSN columns are absent")
        writer = csv.DictWriter(destination, fieldnames=original_fields + EXTRA_FIELDS)
        writer.writeheader()
        for row in reader:
            identifier = row[id_field]
            if not identifier or identifier in seen:
                raise ValueError("Cohort row IDs must be unique and nonempty")
            seen.add(identifier)
            ids_hash.update((identifier + "\n").encode())
            enrichment = matcher.match_row(row, issn_fields)
            writer.writerow({**row, **enrichment})
            rows += 1
            statuses[enrichment["scopus_match_status"]] += 1
            memberships[enrichment["scopus_membership_in_reference"] or "unknown"] += 1
            active_labels[enrichment["scopus_active_journal_in_reference"] or "unknown"] += 1
            usage.update(json.loads(enrichment["scopus_candidate_ids_json"]))
    verified_rows = 0
    with open_csv(input_path, "r") as source, open_csv(partial, "r") as destination:
        original_reader, result_reader = csv.DictReader(source), csv.DictReader(destination)
        for result in result_reader:
            original = next(original_reader, None)
            if original is None or any(original[field] != result[field] for field in original_fields):
                raise ValueError("Original cells or row order changed during Scopus matching")
            if result["scopus_candidate_count"] != str(len(json.loads(result["scopus_candidates_json"]))):
                raise ValueError("Candidate count disagrees with serialized candidate records")
            verified_rows += 1
        if next(original_reader, None) is not None or verified_rows != rows:
            raise ValueError("Original rows were lost")
    partial.replace(output_path)
    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "route": route_name,
        "input_path": str(input_path.resolve()), "input_sha256": sha256(input_path),
        "output_path": str(output_path.resolve()), "output_sha256": sha256(output_path),
        "reference_url": REFERENCE_URL, "reference_sha256": REFERENCE_SHA256,
        "reference_version": "2026-08", "rows": rows, "cohort_id_field": id_field,
        "issn_fields": list(issn_fields), "ordered_cohort_ids_sha256": ids_hash.hexdigest(),
        "match_status_counts": dict(statuses), "membership_counts": dict(memberships),
        "active_journal_counts": dict(active_labels),
        "scopus_source_ids_used_by_multiple_cohort_rows": sum(count > 1 for count in usage.values()),
        "validation": {"all_original_cells_and_order_preserved": True, "readback_rows": verified_rows,
                       "unique_cohort_ids": len(seen), "candidate_json_counts_verified": True},
        "label_definitions": {
            "scopus_membership_in_reference": "1: exactly one candidate with known Scopus Source ID; "
                "0: valid ISSN(s) but no candidate in the pinned included-source worksheets; "
                "blank: no valid ISSN, multiple identities or unknown candidate identity. "
                "0 does not mean never indexed. Accepted-pending titles are not included candidates.",
            "scopus_active_journal_in_reference": "1: one known candidate with exactly Journal type "
                "and explicit Active status; 0: reference absence, or one explicit non-Journal or "
                "Inactive Journal; blank: ambiguous identity, no valid ISSN, unknown type/status, "
                "multiple type classifications or status conflict. This is not a predictive outcome.",
        },
        "method": "Exact checksum-valid ISSN overlap; group workbook rows by Scopus Source ID, "
            "retain unidentified worksheet rows; preserve all candidate evidence and original cohort "
            "provenance. ISSN-L is an additional literal identifier, not an ISSN Registry mapping. "
            "No title fuzzy matching. Scopus Article Language in Source is never used as a predictor.",
    }
    write_json(output_path.parent / (output_path.name + ".summary.json"), summary)
    return summary


class BoundaryTests(unittest.TestCase):
    @staticmethod
    def record(source_id="1", status="Active", source_type="Journal", sheet="Scopus Sources Aug. 2026", marker=""):
        return {"source_id": source_id, "sheet": sheet, "excel_row": 2, "valid_issns": ["0378-5955"],
                "active_or_inactive": status, "source_type": source_type, "discontinued_marker": marker}

    def test_unknown_invalid_and_absent(self):
        matcher = ReferenceMatcher([], [])
        self.assertEqual(matcher.match_row({"issn": ["0378-5956"]})["scopus_membership_in_reference"], "")
        self.assertEqual(matcher.match_row({"issn": ["0378-5955"]})["scopus_membership_in_reference"], "0")

    def test_duplicate_sheets_are_one_identity(self):
        matcher = ReferenceMatcher([self.record(), self.record(sheet="Serial Conf. Proc. with Profile", status="", source_type="")], [])
        result = matcher.match_row({"issn": '["0378-5955"]', "issn_l": "0378-5955"})
        self.assertEqual(result["scopus_candidate_count"], "1")
        self.assertEqual(result["scopus_active_journal_in_reference"], "1")

    def test_ambiguous_identity_and_status_conflict(self):
        matcher = ReferenceMatcher([self.record(), self.record(source_id="2")], [])
        self.assertEqual(matcher.match_row({"issn": ["0378-5955"]})["scopus_membership_in_reference"], "")
        matcher = ReferenceMatcher([self.record(), self.record(status="", source_type="", sheet="Discontinued Titles Aug. 2026")], [])
        result = matcher.match_row({"issn": ["0378-5955"]})
        self.assertEqual(result["scopus_membership_in_reference"], "1")
        self.assertEqual(result["scopus_active_journal_in_reference"], "")

    def test_pending_and_unknown_id_are_not_positive(self):
        matcher = ReferenceMatcher([], [self.record(source_id="", sheet="Accepted Titles Aug. 2026")])
        result = matcher.match_row({"issn": ["0378-5955"]})
        self.assertEqual(result["scopus_membership_in_reference"], "0")
        self.assertTrue(json.loads(result["scopus_accepted_pending_json"]))
        matcher = ReferenceMatcher([self.record(source_id="")], [])
        self.assertEqual(matcher.match_row({"issn": ["0378-5955"]})["scopus_membership_in_reference"], "")

    def test_known_inactive_and_unknown_status_differ(self):
        inactive = ReferenceMatcher([self.record(status="Inactive")], [])
        unknown = ReferenceMatcher([self.record(status="")], [])
        self.assertEqual(inactive.match_row({"issn": ["0378-5955"]})["scopus_active_journal_in_reference"], "0")
        self.assertEqual(unknown.match_row({"issn": ["0378-5955"]})["scopus_active_journal_in_reference"], "")

    def test_shared_returned_identity_preserves_original_rows(self):
        output_dir = BASE / "artifacts/two-route-scopus-2026-10-01"
        output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output_dir) as directory:
            input_path, output_path = Path(directory) / "input.csv.gz", Path(directory) / "output.csv.gz"
            with open_csv(input_path, "w") as stream:
                writer = csv.DictWriter(stream, fieldnames=["route_row_id", "resolved_id", "issn", "issn_l"])
                writer.writeheader()
                writer.writerows([{"route_row_id": f"old{number}", "resolved_id": "S123", "issn": '["0378-5955"]',
                                  "issn_l": "\\N"} for number in range(2)])
            summary = match_file(input_path, output_path, ReferenceMatcher([self.record()], []),
                                 "boundary", "route_row_id")
            self.assertEqual(summary["rows"], 2)
            self.assertEqual(summary["scopus_source_ids_used_by_multiple_cohort_rows"], 1)
            self.assertTrue(summary["validation"]["all_original_cells_and_order_preserved"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, default=BASE / "artifacts/two-route-scopus-2026-10-01")
    parser.add_argument("--reference", type=Path, default=BASE / "artifacts/scopus-2026-08" / REFERENCE_NAME)
    parser.add_argument("--route", default="cohort")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--issn-fields", default="issn,issn_l")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests)
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
            raise SystemExit(1)
        return
    matcher, inventory = ReferenceMatcher.from_workbook(args.reference)
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "reference-inventory.json", inventory)
    write_json(args.output / "reference-index-summary.json", {
        "reference_path": str(args.reference.resolve()), "sha256": REFERENCE_SHA256,
        "candidate_identities": len(matcher.grouped), "valid_issns": len(matcher.index),
        "issns_with_multiple_identities": sum(len(keys) > 1 for keys in matcher.index.values()),
    })
    if args.input:
        summary = match_file(args.input, args.output / f"{args.route}-journals-scopus.csv.gz",
                             matcher, args.route, args.id_field, tuple(args.issn_fields.split(",")))
        print(dumps({key: summary[key] for key in ("rows", "match_status_counts", "membership_counts", "active_journal_counts")}))
    else:
        print(dumps({"reference_index_ready": True, "candidate_identities": len(matcher.grouped),
                     "valid_issns": len(matcher.index)}))


if __name__ == "__main__":
    main()
