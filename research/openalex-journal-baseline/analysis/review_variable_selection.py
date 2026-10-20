"""Verify a full 80-field recommendation against the unchanged delivered Route B."""
import csv
import gzip
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OWNER = Path(__file__).resolve().parents[1]
OUTPUT = OWNER / "artifacts/variable-selection-review-2026-10-20"
SOURCE = OWNER / "artifacts/two-route-delivery-2026-10-01/route-b-api/openalex-route-b-api-2026-10-01-journals.csv.gz"
PROFILE = OWNER / "artifacts/variable-selection-2026-10-16/profile.json"
DECISIONS = Path(__file__).with_name("variable_selection_decisions.tsv")


def main():
    profile = json.loads(PROFILE.read_text())
    with DECISIONS.open(newline="") as stream:
        decisions = list(csv.DictReader(stream, delimiter="\t"))
    if [row["field"] for row in decisions] != profile["header"]:
        raise ValueError("Recommendations do not cover the exact input header in order")
    if any(row["decision"] not in {"yes", "no", "maybe"} for row in decisions):
        raise ValueError("Each field needs a valid recommendation")
    if any(not row["reason_zh"] or not row["reason_en"]
           for row in decisions if row["decision"] == "maybe"):
        raise ValueError("Unresolved recommendations need a short explanation")
    outcome_fields = {"scopus_membership_in_reference", "scopus_active_journal_in_reference"}
    if {row["field"] for row in decisions if row["role"] == "outcome"} != outcome_fields:
        raise ValueError("Both retained Scopus outcomes need an explicit outcome role")
    if any(row["role"] not in {"outcome", "predictor_candidate", "support_only"}
           for row in decisions):
        raise ValueError("Each field needs an explicit study role")
    if any(row["decision"] != "yes" for row in decisions if row["role"] == "outcome"):
        raise ValueError("The requested outcome fields must remain retained")
    if any(row["role"] == "predictor_candidate"
           for row in decisions if row["field"].startswith("scopus_")):
        raise ValueError("Outcome-derived Scopus fields cannot become predictor inputs")
    if any(row["decision"] != "no" for row in decisions
           if row["field"].startswith("scopus_") and row["field"] not in outcome_fields):
        raise ValueError("Other Scopus fields remain matching evidence only")
    fingerprint = hashlib.sha256()
    with SOURCE.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            fingerprint.update(block)
    if fingerprint.hexdigest() != profile["source"]["compressed_sha256"]:
        raise ValueError("Input differs from the previously profiled Route B")

    pairs = [("issn", "ids.issn"), ("issn_l", "ids.issn_l"), ("id", "ids.openalex")]
    unequal = Counter({f"{a} vs {b}": 0 for a, b in pairs})
    targets = {key: Counter() for key in
               ("scopus_membership_in_reference", "scopus_active_journal_in_reference")}
    types, repository_flags = Counter(), Counter()
    row_count = 0
    csv.field_size_limit(100_000_000)
    with gzip.open(SOURCE, "rt", newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != profile["header"]:
            raise ValueError("Actual CSV header differs from the stored profile")
        for row in reader:
            row_count += 1
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Malformed CSV row")
            for a, b in pairs:
                unequal[f"{a} vs {b}"] += row[a] != row[b]
            for key, counts in targets.items():
                counts[row[key] if row[key] else "unresolved_blank"] += 1
            types[row["type"]] += 1
            repository_flags[row["is_preprint_repository"]] += 1
    if row_count != profile["denominator_rows"]:
        raise ValueError("Input row count differs from the profile")
    evidence = {
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE.relative_to(OWNER)),
        "source_sha256": fingerprint.hexdigest(),
        "rows": row_count, "columns": len(decisions),
        "profile_generated_at_utc": profile["profile_generated_at_utc"],
        "profile_reused_after_full_input_hash_verification": True,
        "decision_counts": dict(Counter(row["decision"] for row in decisions)),
        "retained_role_counts": dict(Counter(row["role"] for row in decisions
                                             if row["decision"] == "yes")),
        "category_counts": dict(Counter(row["category"] for row in decisions)),
        "duplicate_representation_unequal_rows": dict(unequal),
        "target_counts": {key: dict(counts) for key, counts in targets.items()},
        "source_type_counts": dict(types),
        "preprint_repository_flag_counts": dict(repository_flags),
        "decisions": decisions,
        "verification": {"exact_header_order": True, "all_80_classified_once": True,
                         "no_scopus_predictors": True, "model_fitted": False},
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: evidence[key] for key in
                      ("rows", "columns", "decision_counts", "category_counts",
                       "duplicate_representation_unequal_rows", "target_counts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
