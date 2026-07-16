#!/usr/bin/env python3
"""Enrich PKP OJS rows with OpenAlex Sources and profile strict coverage."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import tempfile
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


EXPECTED_MD5 = "9f43fa051c7ed1cc45d8592593542011"
EXPECTED_ALL_ROWS = 87_170
EXPECTED_OJS_ROWS = 86_282
EXPECTED_VALID_ISSN_ROWS = 64_773
EXPECTED_VALID_STATUS_COUNTS = {
    "unique": 49_877,
    "ambiguous": 190,
    "unmatched": 14_706,
}
MISSING_COUNTRY_GROUP = "Missing PKP-inferred country"
PROFILE_FIELDS = (
    "dimension",
    "group",
    "cohort_rows",
    "unique_matches",
    "ambiguous_matches",
    "unmatched_rows",
    "strict_coverage_pct",
    "wilson_95_lower_pct",
    "wilson_95_upper_pct",
)
REQUIRED_COLUMNS = {
    "oai_url",
    "application",
    "repository_name",
    "set_spec",
    "context_name",
    "stats_id",
    "issn",
    "last_beacon",
    "last_oai_response",
    "unresponsive_endpoint",
    "unresponsive_context",
}
SELECT_FIELDS = (
    "id",
    "display_name",
    "alternate_titles",
    "issn_l",
    "issn",
    "type",
    "ids",
    "host_organization",
    "host_organization_name",
    "host_organization_lineage",
    "country_code",
    "homepage_url",
    "is_oa",
    "is_in_doaj",
    "is_ojs",
    "is_core",
    "is_high_oa_rate",
    "is_high_oa_rate_since_year",
    "is_in_doaj_since_year",
    "is_in_scielo",
    "oa_flip_year",
    "works_count",
    "oa_works_count",
    "cited_by_count",
    "summary_stats",
    "first_publication_year",
    "last_publication_year",
    "counts_by_year",
    "apc_prices",
    "apc_usd",
    "topics",
    "topic_share",
    "societies",
    "created_date",
    "updated_date",
    "works_api_url",
)
FLAT_FIELDS = (
    "id",
    "display_name",
    "issn_l",
    "issn",
    "type",
    "host_organization",
    "host_organization_name",
    "host_organization_lineage",
    "country_code",
    "homepage_url",
    "is_oa",
    "is_in_doaj",
    "is_ojs",
    "is_core",
    "is_high_oa_rate",
    "is_high_oa_rate_since_year",
    "is_in_doaj_since_year",
    "is_in_scielo",
    "oa_flip_year",
    "works_count",
    "oa_works_count",
    "cited_by_count",
    "summary_stats",
    "first_publication_year",
    "last_publication_year",
    "apc_usd",
    "created_date",
    "updated_date",
    "works_api_url",
)
PROVENANCE_FIELDS = (
    "identifier_status",
    "input_issns",
    "matched_issns",
    "match_route",
    "match_status",
    "match_reason",
    "candidate_count",
    "candidate_ids",
    "candidate_types",
    "candidate_evidence_json",
    "selected_source_id",
    "openalex_retrieved_at",
)
RETRYABLE_STATUS = {403, 429, 500, 502, 503, 504}


class ApiRequestError(RuntimeError):
    pass


def normalize_issn(value: Any) -> str | None:
    """Reuse the repository's alphanumeric ISSN shape, then enforce checksum."""
    token = "".join(ch for ch in str(value or "").strip().upper() if ch.isalnum())
    if (
        len(token) != 8
        or not token[:7].isdigit()
        or not (token[7].isdigit() or token[7] == "X")
    ):
        return None
    checksum = (
        11
        - sum(int(digit) * weight for digit, weight in zip(token[:7], range(8, 1, -1)))
        % 11
    ) % 11
    expected = "X" if checksum == 10 else str(checksum)
    return f"{token[:4]}-{token[4:]}" if token[7] == expected else None


def parse_input_issns(raw: str) -> tuple[str, list[str]]:
    if not raw.strip():
        return "missing", []
    parts = [part.strip() for part in raw.splitlines() if part.strip()]
    normalized = [normalize_issn(part) for part in parts]
    if not parts or any(token is None for token in normalized):
        return "invalid", []
    return "valid", list(dict.fromkeys(token for token in normalized if token))


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_input(path: Path) -> tuple[list[dict[str, str]], list[str], int]:
    actual_md5 = md5(path)
    if actual_md5 != EXPECTED_MD5:
        raise ValueError(f"Pinned beacon.csv MD5 mismatch: {actual_md5}")

    rows: list[dict[str, str]] = []
    identities: set[tuple[str, str, str]] = set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = sorted(REQUIRED_COLUMNS - set(fieldnames))
        if missing:
            raise ValueError(f"Pinned input is missing columns: {missing}")
        all_rows = 0
        for source_row in reader:
            all_rows += 1
            if source_row["application"].strip().casefold() != "ojs":
                continue
            for field in ("oai_url", "set_spec", "context_name"):
                if not source_row[field].strip():
                    raise ValueError(
                        f"OJS row {all_rows} has blank required field {field}"
                    )
            identity = tuple(
                source_row[field]
                for field in ("oai_url", "repository_name", "set_spec")
            )
            if identity in identities:
                raise ValueError(f"Duplicate OJS row identity at source row {all_rows}")
            identities.add(identity)
            identifier_status, tokens = parse_input_issns(source_row["issn"])
            row = {
                key: value for key, value in source_row.items() if key != "admin_email"
            }
            row["_identifier_status"] = identifier_status
            row["_input_issns"] = tokens  # type: ignore[assignment]
            rows.append(row)

    if all_rows != EXPECTED_ALL_ROWS or len(rows) != EXPECTED_OJS_ROWS:
        raise ValueError(
            f"Pinned input baseline mismatch: all={all_rows}, ojs={len(rows)}"
        )
    return rows, [name for name in fieldnames if name != "admin_email"], all_rows


def chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def request_json(
    params: dict[str, str], api_key: str
) -> tuple[dict[str, Any], dict[str, str], int]:
    safe_params = dict(params)
    safe_params["api_key"] = api_key
    request = Request(
        f"https://api.openalex.org/sources?{urlencode(safe_params)}",
        headers={"Accept": "application/json", "User-Agent": "InvisibleResearch/1.0"},
    )
    for attempt in range(5):
        try:
            with urlopen(request, timeout=30) as response:
                headers = {
                    name: response.headers.get(name, "")
                    for name in (
                        "X-RateLimit-Limit",
                        "X-RateLimit-Remaining",
                        "X-RateLimit-Credits-Used",
                        "X-RateLimit-Reset",
                    )
                }
                return json.load(response), headers, attempt
        except HTTPError as error:
            if error.code not in RETRYABLE_STATUS or attempt == 4:
                detail = error.read(200).decode("utf-8", errors="replace")
                raise ApiRequestError(f"OpenAlex HTTP {error.code}: {detail}") from None
        except (URLError, TimeoutError) as error:
            if attempt == 4:
                raise ApiRequestError(
                    f"OpenAlex network failure: {error.reason if isinstance(error, URLError) else error}"
                ) from None
        time.sleep(2**attempt)
    raise AssertionError("unreachable")


def cache_path(cache_dir: Path, tokens: list[str]) -> Path:
    digest = hashlib.sha256(("v1\0" + "\n".join(tokens)).encode()).hexdigest()
    return cache_dir / f"issn-{digest}.json.gz"


def read_json(path: Path) -> dict[str, Any]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        if path.suffix == ".gz":
            with gzip.open(temporary, "wt", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False)
        else:
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def fetch_batch(
    tokens: list[str], api_key: str, cache_dir: Path
) -> tuple[dict[str, Any], bool]:
    path = cache_path(cache_dir, tokens)
    if path.is_file():
        cached = read_json(path)
        if cached.get("tokens") != tokens:
            raise ValueError(f"Cache token mismatch: {path}")
        return cached, True

    results: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    cursor = "*"
    while cursor:
        payload, headers, retries = request_json(
            {
                "filter": f"issn:{'|'.join(tokens)}",
                "per_page": "100",
                "cursor": cursor,
                "select": ",".join(SELECT_FIELDS),
            },
            api_key,
        )
        page_results = payload.get("results", [])
        if not isinstance(page_results, list):
            raise ApiRequestError("OpenAlex returned a non-list results value")
        results.extend(page_results)
        meta = payload.get("meta") or {}
        pages.append({"meta": meta, "rate_limit_headers": headers, "retries": retries})
        next_cursor = meta.get("next_cursor")
        if (
            not page_results
            or len(page_results) < 100
            or not next_cursor
            or next_cursor == cursor
        ):
            break
        cursor = next_cursor

    cached = {
        "tokens": tokens,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "pages": pages,
        "results": results,
    }
    write_json_atomic(path, cached)
    return cached, False


def source_tokens(source: dict[str, Any]) -> list[str]:
    values = list(source.get("issn") or [])
    if source.get("issn_l"):
        values.append(source["issn_l"])
    return list(
        dict.fromkeys(token for value in values if (token := normalize_issn(value)))
    )


def classify_row(
    row: dict[str, Any],
    token_sources: dict[str, dict[str, dict[str, Any]]],
    failed_tokens: set[str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    status = row["_identifier_status"]
    tokens = row["_input_issns"]
    if status != "valid":
        return {
            "identifier_status": status,
            "input_issns": "",
            "matched_issns": "",
            "match_route": "none",
            "match_status": "not_attempted",
            "match_reason": f"{status}_issn",
            "candidate_count": 0,
            "candidate_ids": "",
            "candidate_types": "",
            "candidate_evidence_json": "[]",
            "selected_source_id": "",
        }, None

    candidates: dict[str, dict[str, Any]] = {}
    evidence: dict[str, list[str]] = defaultdict(list)
    for token in tokens:
        for source_id, source in token_sources.get(token, {}).items():
            candidates[source_id] = source
            evidence[source_id].append(token)
    candidate_ids = sorted(candidates)
    candidate_evidence = [
        {
            "source_id": source_id,
            "source_type": candidates[source_id].get("type"),
            "matched_tokens": sorted(evidence[source_id]),
        }
        for source_id in candidate_ids
    ]
    failed = any(token in failed_tokens for token in tokens)
    selected: dict[str, Any] | None = None
    if failed:
        match_status, reason = "api_error", "incomplete_issn_retrieval"
    elif len(candidate_ids) > 1:
        match_status, reason = "ambiguous", "multiple_source_ids"
    elif (
        len(candidate_ids) == 1
        and candidates[candidate_ids[0]].get("type") == "journal"
    ):
        match_status, reason = "unique", "one_journal_source"
        selected = candidates[candidate_ids[0]]
    elif len(candidate_ids) == 1:
        match_status, reason = "unmatched", "non_journal_candidate"
    else:
        match_status, reason = "unmatched", "no_source_for_issn"

    return {
        "identifier_status": status,
        "input_issns": "|".join(tokens),
        "matched_issns": "|".join(
            sorted({token for values in evidence.values() for token in values})
        ),
        "match_route": "issn",
        "match_status": match_status,
        "match_reason": reason,
        "candidate_count": len(candidate_ids),
        "candidate_ids": "|".join(candidate_ids),
        "candidate_types": "|".join(
            str(candidates[source_id].get("type") or "") for source_id in candidate_ids
        ),
        "candidate_evidence_json": json.dumps(
            candidate_evidence, ensure_ascii=False, separators=(",", ":")
        ),
        "selected_source_id": selected.get("id", "") if selected else "",
    }, selected


def as_cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def run(
    input_path: Path, output_dir: Path, batch_size: int, workers: int
) -> dict[str, Any]:
    if not 1 <= batch_size <= 100:
        raise ValueError("batch size must be between 1 and 100")
    if not 1 <= workers <= 16:
        raise ValueError("workers must be between 1 and 16")
    api_key = os.environ.get("OPENALEX_API_KEY")
    if not api_key:
        raise RuntimeError("OPENALEX_API_KEY is required")

    rows, source_fields, all_rows = load_input(input_path)
    valid_tokens = sorted({token for row in rows for token in row["_input_issns"]})
    valid_token_set = set(valid_tokens)
    cache_dir = output_dir / "openalex-cache"
    output_dir.mkdir(parents=True, exist_ok=True)

    token_sources: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    failed_tokens: set[str] = set()
    failures: list[dict[str, Any]] = []
    api_stats: Counter[str] = Counter()
    cost_usd = 0.0
    last_rate_headers: dict[str, str] = {}
    batches = list(chunks(valid_tokens, batch_size))
    # ponytail: 8 workers made the measured full run practical while remaining far
    # below OpenAlex's rate limit; tune --workers only if network conditions change.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(fetch_batch, batch, api_key, cache_dir): batch
            for batch in batches
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            batch = futures[future]
            try:
                cached, from_cache = future.result()
            except ApiRequestError as error:
                failed_tokens.update(batch)
                failures.append({"tokens": batch, "error": str(error)})
                continue
            api_stats["cached_batches" if from_cache else "live_batches"] += 1
            for page in cached["pages"]:
                api_stats["request_count"] += 1
                if not from_cache:
                    api_stats["live_request_count"] += 1
                api_stats["retries"] += int(page.get("retries", 0))
                cost_usd += float((page.get("meta") or {}).get("cost_usd") or 0)
                last_rate_headers = page.get("rate_limit_headers") or last_rate_headers
            for source in cached["results"]:
                source_id = source.get("id")
                if not source_id:
                    continue
                for token in source_tokens(source):
                    if token in valid_token_set:
                        token_sources[token][source_id] = source
            if completed % 25 == 0 or completed == len(batches):
                print(f"OpenAlex ISSN batches: {completed}/{len(batches)}")

    retrieved_at = datetime.now(timezone.utc).isoformat()
    enriched_path = output_dir / "pkp-openalex-enriched.csv"
    review_path = output_dir / "pkp-openalex-review.csv"
    output_fields = (
        source_fields
        + list(PROVENANCE_FIELDS)
        + [f"openalex_{field}" for field in FLAT_FIELDS]
    )
    status_counts: Counter[str] = Counter()
    identifier_counts: Counter[str] = Counter()
    unique_sources: dict[str, dict[str, Any]] = {}
    is_ojs_false = 0
    country_comparable = 0
    country_disagreements = 0

    with enriched_path.open(
        "w", encoding="utf-8", newline=""
    ) as enriched_handle, review_path.open(
        "w", encoding="utf-8", newline=""
    ) as review_handle:
        enriched_writer = csv.DictWriter(enriched_handle, fieldnames=output_fields)
        review_writer = csv.DictWriter(review_handle, fieldnames=output_fields)
        enriched_writer.writeheader()
        review_writer.writeheader()
        for row in rows:
            provenance, selected = classify_row(row, token_sources, failed_tokens)
            output = {field: row.get(field, "") for field in source_fields}
            output.update(provenance)
            output["openalex_retrieved_at"] = retrieved_at
            output.update(
                {
                    f"openalex_{field}": (
                        as_cell(selected.get(field)) if selected else ""
                    )
                    for field in FLAT_FIELDS
                }
            )
            enriched_writer.writerow(output)
            if provenance["match_status"] != "unique":
                review_writer.writerow(output)
            status_counts[provenance["match_status"]] += 1
            identifier_counts[provenance["identifier_status"]] += 1
            if selected:
                unique_sources[selected["id"]] = selected
                is_ojs_false += selected.get("is_ojs") is False
                pkp_country = (
                    str(row.get("country_consolidated") or "").strip().casefold()
                )
                oa_country = str(selected.get("country_code") or "").strip().casefold()
                if pkp_country and oa_country:
                    country_comparable += 1
                    country_disagreements += pkp_country != oa_country

    null_rates = {
        field: (
            round(
                sum(
                    source.get(field) in (None, "", [])
                    for source in unique_sources.values()
                )
                / len(unique_sources),
                6,
            )
            if unique_sources
            else None
        )
        for field in FLAT_FIELDS
    }
    report = {
        "artifact_scope": "Exploratory Analysis",
        "input": {
            "path": str(input_path),
            "md5": EXPECTED_MD5,
            "all_rows": all_rows,
            "ojs_rows": len(rows),
            "identifier_status_counts": dict(identifier_counts),
            "distinct_valid_issns": len(valid_tokens),
        },
        "matching": {
            "route": "exact_issn_only",
            "status_counts": dict(status_counts),
            "row_preserved": sum(status_counts.values()) == len(rows),
            "strict_issn_coverage": round(status_counts["unique"] / len(rows), 6),
            "provisional_title_coverage": 0,
            "unique_openalex_sources": len(unique_sources),
            "openalex_field_null_rates_among_unique_sources": null_rates,
            "unique_matches_with_is_ojs_false": is_ojs_false,
            "country_comparable_rows": country_comparable,
            "country_disagreement_rows": country_disagreements,
        },
        "api": {
            "request_count": api_stats["request_count"],
            "live_request_count": api_stats["live_request_count"],
            "live_batches": api_stats["live_batches"],
            "cached_batches": api_stats["cached_batches"],
            "retries": api_stats["retries"],
            "cost_usd": round(cost_usd, 6),
            "failed_batches": len(failures),
            "failed_token_count": len(failed_tokens),
            "failures": failures,
            "last_rate_limit_headers": last_rate_headers,
        },
        "outputs": {
            "enriched_csv": str(enriched_path),
            "review_csv": str(review_path),
            "raw_cache": str(cache_dir),
        },
        "generated_at": retrieved_at,
    }
    write_json_atomic(output_dir / "coverage-report.json", report)
    print(json.dumps(report, ensure_ascii=False))
    return report


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2))
        / denominator
    )
    return (center - margin) * 100, (center + margin) * 100


def generate_country_profile(output_dir: Path) -> dict[str, Any]:
    enriched_path = output_dir / "pkp-openalex-enriched.csv"
    report_path = output_dir / "coverage-report.json"
    profile_path = output_dir / "strict-openalex-coverage-profile.csv"
    summary_path = output_dir / "strict-openalex-coverage-profile-summary.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    status_counts: Counter[str] = Counter()

    with enriched_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        required = {
            "country_consolidated",
            "identifier_status",
            "match_route",
            "match_status",
        }
        if missing := sorted(required - fields):
            raise ValueError(f"Joined artifact is missing profile fields: {missing}")
        if "admin_email" in fields:
            raise ValueError("Joined artifact contains restricted admin_email")
        for row in reader:
            if row["identifier_status"] != "valid":
                continue
            if row["match_route"] != "issn":
                raise ValueError("Valid-ISSN cohort contains a non-ISSN match route")
            status = row["match_status"]
            if status not in EXPECTED_VALID_STATUS_COUNTS:
                raise ValueError(f"Unexpected Valid-ISSN match status: {status}")
            country = row["country_consolidated"].strip() or MISSING_COUNTRY_GROUP
            groups[country][status] += 1
            status_counts[status] += 1

    if sum(status_counts.values()) != EXPECTED_VALID_ISSN_ROWS:
        raise ValueError(f"Valid-ISSN cohort mismatch: {sum(status_counts.values())}")
    if dict(status_counts) != EXPECTED_VALID_STATUS_COUNTS:
        raise ValueError(f"Valid-ISSN status mismatch: {dict(status_counts)}")
    if report["input"]["identifier_status_counts"]["valid"] != sum(
        status_counts.values()
    ) or any(
        report["matching"]["status_counts"][status] != count
        for status, count in EXPECTED_VALID_STATUS_COUNTS.items()
    ):
        raise ValueError("Country profile does not reconcile with coverage-report.json")

    profile_rows: list[dict[str, Any]] = []
    for country in sorted(
        groups, key=lambda value: (value == MISSING_COUNTRY_GROUP, value)
    ):
        counts = groups[country]
        denominator = sum(counts.values())
        lower, upper = wilson_interval(counts["unique"], denominator)
        profile_rows.append(
            {
                "dimension": "pkp_inferred_country",
                "group": country,
                "cohort_rows": denominator,
                "unique_matches": counts["unique"],
                "ambiguous_matches": counts["ambiguous"],
                "unmatched_rows": counts["unmatched"],
                "strict_coverage_pct": round(counts["unique"] / denominator * 100, 6),
                "wilson_95_lower_pct": round(lower, 6),
                "wilson_95_upper_pct": round(upper, 6),
            }
        )
    with profile_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PROFILE_FIELDS)
        writer.writeheader()
        writer.writerows(profile_rows)

    total_lower, total_upper = wilson_interval(
        status_counts["unique"], EXPECTED_VALID_ISSN_ROWS
    )
    summary = {
        "artifact_scope": "Exploratory Analysis",
        "analysis_question": (
            "How does Strict OpenAlex Coverage vary descriptively by "
            "PKP-inferred country in the Valid-ISSN OJS Cohort?"
        ),
        "definitions": {
            "cohort": {
                "name": "Valid-ISSN OJS Cohort",
                "rule": "identifier_status == valid",
            },
            "outcome": "unique exact-ISSN match",
            "ambiguous": "multiple exact-ISSN OpenAlex Source candidates",
            "unmatched": "no unique journal Source from the exact-ISSN route",
            "pkp_inferred_country": {
                "source_field": "country_consolidated",
                "missing_group": MISSING_COUNTRY_GROUP,
                "caveat": (
                    "PKP-inferred country is descriptive metadata, not authoritative "
                    "publisher location."
                ),
            },
            "uncertainty": "95% Wilson score interval for unique / cohort rows",
        },
        "reconciliation": {
            "cohort_rows": EXPECTED_VALID_ISSN_ROWS,
            "status_counts": EXPECTED_VALID_STATUS_COUNTS,
            "strict_coverage_pct": round(
                status_counts["unique"] / EXPECTED_VALID_ISSN_ROWS * 100, 6
            ),
            "wilson_95_lower_pct": round(total_lower, 6),
            "wilson_95_upper_pct": round(total_upper, 6),
            "country_group_count": len(profile_rows),
            "grouped_cohort_rows": sum(row["cohort_rows"] for row in profile_rows),
            "matches_coverage_report": True,
        },
        "generation": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_enriched_csv": enriched_path.name,
            "source_coverage_report": report_path.name,
            "source_generated_at": report["generated_at"],
            "openalex_api_requests": 0,
        },
        "privacy": {
            "restricted_source_fields_excluded": ["admin_email"],
            "contains_restricted_contact_data": False,
        },
        "outputs": {
            "profile_csv": profile_path.name,
            "summary_json": summary_path.name,
        },
    }
    write_json_atomic(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def check_outputs(output_dir: Path) -> None:
    assert normalize_issn("0378-5955") == "0378-5955"
    assert normalize_issn("03785956") is None
    source = {"id": "https://openalex.org/S1", "type": "journal"}
    row = {"_identifier_status": "valid", "_input_issns": ["0378-5955"]}
    provenance, selected = classify_row(
        row, {"0378-5955": {source["id"]: source}}, set()
    )
    assert provenance["match_status"] == "unique" and selected == source

    report = json.loads(
        (output_dir / "coverage-report.json").read_text(encoding="utf-8")
    )
    assert report["artifact_scope"] == "Exploratory Analysis"
    assert report["input"]["ojs_rows"] == EXPECTED_OJS_ROWS
    assert report["matching"]["row_preserved"] is True
    assert report["matching"]["provisional_title_coverage"] == 0
    country_counts: Counter[str] = Counter()
    valid_status_counts: Counter[str] = Counter()
    valid_routes: set[str] = set()
    with (output_dir / "pkp-openalex-enriched.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        assert "admin_email" not in (reader.fieldnames or [])
        row_count = 0
        for enriched_row in reader:
            row_count += 1
            if enriched_row["identifier_status"] != "valid":
                continue
            country = enriched_row["country_consolidated"].strip()
            country_counts[country or MISSING_COUNTRY_GROUP] += 1
            valid_status_counts[enriched_row["match_status"]] += 1
            valid_routes.add(enriched_row["match_route"])
        assert row_count == EXPECTED_OJS_ROWS
    assert sum(valid_status_counts.values()) == EXPECTED_VALID_ISSN_ROWS
    assert dict(valid_status_counts) == EXPECTED_VALID_STATUS_COUNTS
    assert valid_routes == {"issn"}

    summary = json.loads(
        (output_dir / "strict-openalex-coverage-profile-summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["artifact_scope"] == "Exploratory Analysis"
    assert summary["definitions"]["outcome"] == "unique exact-ISSN match"
    country_definition = summary["definitions"]["pkp_inferred_country"]
    assert country_definition["source_field"] == "country_consolidated"
    assert "not authoritative publisher location" in country_definition["caveat"]
    assert summary["generation"]["openalex_api_requests"] == 0
    datetime.fromisoformat(summary["generation"]["generated_at"])
    assert summary["privacy"]["restricted_source_fields_excluded"] == ["admin_email"]
    assert summary["privacy"]["contains_restricted_contact_data"] is False
    assert summary["outputs"] == {
        "profile_csv": "strict-openalex-coverage-profile.csv",
        "summary_json": "strict-openalex-coverage-profile-summary.json",
    }

    reconciliation = summary["reconciliation"]
    assert reconciliation["cohort_rows"] == EXPECTED_VALID_ISSN_ROWS
    assert reconciliation["status_counts"] == EXPECTED_VALID_STATUS_COUNTS
    assert reconciliation["matches_coverage_report"] is True
    assert reconciliation["grouped_cohort_rows"] == EXPECTED_VALID_ISSN_ROWS
    assert (
        report["input"]["identifier_status_counts"]["valid"]
        == reconciliation["cohort_rows"]
    )
    for status, count in EXPECTED_VALID_STATUS_COUNTS.items():
        assert report["matching"]["status_counts"][status] == count

    profile_totals: Counter[str] = Counter()
    profile_country_counts: dict[str, int] = {}
    with (output_dir / "strict-openalex-coverage-profile.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or []) == PROFILE_FIELDS
        assert "admin_email" not in (reader.fieldnames or [])
        for profile_row in reader:
            assert profile_row["dimension"] == "pkp_inferred_country"
            group = profile_row["group"]
            assert group and group not in profile_country_counts
            denominator = int(profile_row["cohort_rows"])
            unique = int(profile_row["unique_matches"])
            ambiguous = int(profile_row["ambiguous_matches"])
            unmatched = int(profile_row["unmatched_rows"])
            assert denominator == unique + ambiguous + unmatched
            estimate = unique / denominator * 100
            reported = float(profile_row["strict_coverage_pct"])
            lower = float(profile_row["wilson_95_lower_pct"])
            upper = float(profile_row["wilson_95_upper_pct"])
            assert math.isclose(reported, estimate, abs_tol=0.000001)
            assert 0 <= lower <= reported <= upper <= 100
            profile_country_counts[group] = denominator
            profile_totals.update(
                cohort_rows=denominator,
                unique=unique,
                ambiguous=ambiguous,
                unmatched=unmatched,
            )
    assert profile_country_counts == dict(country_counts)
    assert profile_totals == Counter(
        cohort_rows=EXPECTED_VALID_ISSN_ROWS, **EXPECTED_VALID_STATUS_COUNTS
    )
    print("PKP–OpenAlex pipeline check passed")


def parse_args() -> argparse.Namespace:
    data_root = os.environ.get("DATA_ROOT")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(data_root) / "raw/pkp-beacon-v6/beacon.csv" if data_root else None,
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).parents[1] / "artifacts"
    )
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--workers", type=int, default=8)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--profile", action="store_true")
    action.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.check:
        check_outputs(args.output_dir)
        return
    if args.profile:
        generate_country_profile(args.output_dir)
        return
    if args.input is None:
        raise SystemExit("Set DATA_ROOT or pass --input")
    run(args.input, args.output_dir, args.batch_size, args.workers)


if __name__ == "__main__":
    main()
