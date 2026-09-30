"""Collect complete OpenAlex Sources and produce a reversible journal-level CSV.

Each requested Source ID keeps its own JSON and CSV row, including redirected,
missing and failed requests. Resume uses batch receipts from the same cohort.
Generated files must stay in a named artifacts directory. No database is used.
"""

import argparse
import collections
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import datetime as dt
from decimal import Decimal, ROUND_FLOOR
from email.utils import parsedate_to_datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import threading
import time

import requests

try:
    import orjson
except ImportError:
    orjson = None


API = "https://api.openalex.org"
VERSION = 1
META_COLUMNS = ("source_id", "resolved_id", "fetch_status", "fetched_at")
SUCCESS = {"ok", "redirected"}
TERMINAL = SUCCESS | {"not_found"}
MISSING = object()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dumps(value):
    # JSON's primitive types and empty containers remain distinguishable in CSV.
    if orjson is not None:
        return orjson.dumps(value)
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def loads(value):
    return orjson.loads(value) if orjson is not None else json.loads(value)


def content_hash(value):
    serialized = (orjson.dumps(value, option=orjson.OPT_SORT_KEYS) if orjson is not None else
                  json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))
    return hashlib.sha256(serialized).digest()


def atomic_bytes(path, value):
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(value)
    os.replace(temporary, path)


def save_json(path, value):
    atomic_bytes(path, dumps(value) + b"\n")


def source_id(value):
    match = re.fullmatch(r"(?:https://openalex\.org/)?S?([1-9][0-9]*)", value.strip())
    if not match:
        raise ValueError("Invalid OpenAlex Source ID in input or response")
    return "S" + match.group(1)


def canonical(value):
    return "https://openalex.org/" + source_id(value)


def read_ids(path):
    ids = [source_id(line) for line in path.read_text(encoding="utf-8").splitlines()
           if line.strip()]
    if not ids:
        raise ValueError("The Source ID cohort is empty")
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate Source IDs in the cohort; no rows were dropped")
    digest = hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()
    return ids, digest


def escape_key(key):
    return key.replace("\\", "\\\\").replace(".", "\\.")


def split_path(path):
    keys, current, escaped = [], [], False
    for character in path:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == ".":
            keys.append("".join(current))
            current = []
        else:
            current.append(character)
    if escaped:
        raise ValueError("Invalid escaped CSV field path")
    keys.append("".join(current))
    return keys


def flatten(value, prefix=""):
    result = {}
    for key, child in value.items():
        name = prefix + escape_key(key)
        if name in META_COLUMNS:
            raise ValueError("Source attribute collides with a CSV provenance column")
        if isinstance(child, dict) and child:
            result.update(flatten(child, name + "."))
        else:
            result[name] = child
    return result


def unflatten(flat):
    result = {}
    for path, value in flat.items():
        keys = split_path(path)
        target = result
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = value
    return result


def encode_cell(value):
    if value is MISSING:
        return "\\M"
    if value is None:
        return "\\N"
    if not isinstance(value, str):
        return dumps(value).decode("utf-8")
    # Leave ordinary titles/URLs legible. Escape strings that could be confused
    # with a reserved marker or a JSON value, including the string "0".
    ambiguous = False
    if json_candidate(value):
        try:
            json.loads(value)
            ambiguous = True
        except (ValueError, TypeError):
            pass
    if value.startswith("\\") or ambiguous:
        return "\\S" + dumps(value).decode("utf-8")
    return value


def decode_cell(value):
    if value == "\\M":
        return MISSING
    if value == "\\N":
        return None
    if value.startswith("\\S"):
        restored = loads(value[2:])
        if not isinstance(restored, str):
            raise ValueError("Invalid CSV string escape")
        return restored
    if json_candidate(value):
        try:
            return loads(value)
        except (ValueError, TypeError):
            pass
    return value


def json_candidate(value):
    return bool(value) and (value[0] in '[{\"-0123456789' or
                            value in {"null", "true", "false", "NaN", "Infinity"})


def value_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    raise ValueError("Unsupported JSON value type")


def api_key(env_file):
    key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if key:
        return key
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*(?:export\s+)?OPENALEX_API_KEY\s*=\s*(.*)$", line)
            if match:
                value = match.group(1).strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    return value[1:-1]
                return value.split(" #", 1)[0].strip()
    raise ValueError("OPENALEX_API_KEY is required for collection")


class FetchError(Exception):
    def __init__(self, code, fatal=False):
        super().__init__(code)
        self.code = code
        self.fatal = fatal


class Client:
    def __init__(self, key, rate=80, attempts=4, timeout=60,
                 max_list_requests=None, session_factory=requests.Session):
        self.key = key
        self.rate = rate
        self.maximum_rate = rate
        self.attempts = attempts
        self.timeout = timeout
        self.factory = session_factory
        self.local = threading.local()
        self.lock = threading.Lock()
        self.next_request = 0.0
        self.pause_until = 0.0
        self.last_throttle = 0.0
        self.last_rate_adjustment = 0.0
        self.throttle_count = 0
        self.rate_events = []
        self.requests = collections.Counter()
        self.max_list_requests = max_list_requests
        self.aborted = threading.Event()
        self.abort_reason = None

    def session(self):
        if not hasattr(self.local, "session"):
            self.local.session = self.factory()
            self.local.session.headers.update({"Authorization": "Bearer " + self.key,
                                               "User-Agent": "InvisibleResearch/source-csv"})
        return self.local.session

    def acquire(self, kind):
        while True:
            with self.lock:
                if self.aborted.is_set():
                    raise FetchError(self.abort_reason or "collection_stopped")
                clock = time.monotonic()
                if (self.last_throttle and clock - self.last_throttle >= 120
                        and clock - self.last_rate_adjustment >= 120):
                    self.rate = min(self.maximum_rate, self.rate * 1.1)
                    self.last_rate_adjustment = clock
                wait = max(self.next_request, self.pause_until) - clock
                if wait <= 0:
                    if (kind == "list" and self.max_list_requests is not None
                            and self.requests[kind] >= self.max_list_requests):
                        self.abort_reason = "free_request_budget_exhausted"
                        self.aborted.set()
                        raise FetchError(self.abort_reason, fatal=True)
                    self.next_request = clock + 1 / self.rate
                    self.requests[kind] += 1
                    return
            # Recheck shared pause after waking; unissued requests have no old
            # reservations that could burst through a newly received 429.
            time.sleep(wait)

    def throttle(self, response, delay):
        with self.lock:
            clock = time.monotonic()
            previous = self.rate
            if not self.last_throttle or clock - self.last_rate_adjustment >= 5:
                self.rate = min(self.maximum_rate, max(2, min(25, self.rate * 0.5)))
                self.last_rate_adjustment = clock
            self.last_throttle = clock
            self.pause_until = max(self.pause_until, clock + max(1, delay))
            self.throttle_count += 1
            remaining = None
            try:
                amount = Decimal(response.headers.get("X-RateLimit-Remaining-USD", ""))
                if amount.is_finite():
                    remaining = str(amount)
            except ArithmeticError:
                pass
            self.rate_events.append({"at": now(), "rate_before": previous,
                                     "rate_after": self.rate,
                                     "pause_seconds": max(1, delay),
                                     "daily_remaining_usd": remaining})
            self.rate_events = self.rate_events[-20:]

    def stop(self, code):
        with self.lock:
            self.abort_reason = code
            self.aborted.set()

    def get(self, endpoint, params=None, kind="singleton"):
        last_code = "request_failed"
        for attempt in range(self.attempts):
            self.acquire(kind)
            try:
                response = self.session().get(API + endpoint, params=params,
                                              timeout=(10, self.timeout))
            except requests.RequestException:
                # Exception text can contain URLs or headers. Only a fixed code
                # is persisted or printed, never repr(exception).
                last_code = "transport_error"
                delay = 2 ** attempt
            else:
                if response.status_code == 404 and kind == "singleton":
                    return None
                if 200 <= response.status_code < 300:
                    try:
                        result = loads(response.content)
                    except (ValueError, TypeError):
                        last_code = "invalid_json_response"
                        delay = 2 ** attempt
                    else:
                        if not isinstance(result, dict):
                            raise FetchError("invalid_response_object")
                        return result
                elif response.status_code == 429 or response.status_code >= 500:
                    last_code = "http_" + str(response.status_code)
                    delay = 2 ** attempt
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = max(delay, float(retry_after))
                        except ValueError:
                            try:
                                delay = max(delay, (parsedate_to_datetime(retry_after)
                                                    - dt.datetime.now(dt.timezone.utc)).total_seconds())
                            except (TypeError, ValueError, OverflowError):
                                pass
                    if not math.isfinite(delay) or delay < 0:
                        delay = 2 ** attempt
                    if response.status_code == 429:
                        self.throttle(response, delay)
                else:
                    code = "http_" + str(response.status_code)
                    self.stop(code)
                    raise FetchError(code, fatal=True)
            if attempt + 1 < self.attempts:
                time.sleep(delay)
        raise FetchError(last_code)

    def free_budget(self, batches):
        response = self.get("/rate-limit", kind="rate_limit")
        rate = response.get("rate_limit", {})
        required = ("daily_budget_usd", "daily_used_usd", "daily_remaining_usd",
                    "prepaid_balance_usd", "endpoint_costs_usd")
        if not all(key in rate for key in required):
            raise FetchError("unrecognized_free_budget_response", fatal=True)
        costs = rate["endpoint_costs_usd"]
        singleton = Decimal(str(costs.get("singleton", "-1")))
        list_cost = Decimal(str(costs.get("list", "-1")))
        remaining = Decimal(str(rate["daily_remaining_usd"]))
        if singleton != 0 or list_cost <= 0 or remaining <= 0:
            raise FetchError("free_only_collection_not_available", fatal=True)
        safe_limit = int((remaining * Decimal("0.9") / list_cost).to_integral_value(
            rounding=ROUND_FLOOR))
        self.max_list_requests = min(self.max_list_requests or safe_limit, safe_limit)
        if batches * self.attempts > self.max_list_requests:
            raise FetchError("insufficient_free_budget_for_retry_reserve", fatal=True)
        # Only known budget fields are stored; /rate-limit also returns api_key.
        return {"checked_at": now(), "daily_budget_usd": rate["daily_budget_usd"],
                "daily_used_usd": rate["daily_used_usd"],
                "daily_remaining_usd": rate["daily_remaining_usd"],
                "prepaid_balance_usd": rate["prepaid_balance_usd"],
                "singleton_cost_usd": str(singleton), "list_cost_usd": str(list_cost),
                "maximum_list_requests_this_run": self.max_list_requests,
                "reserved_list_attempts_this_run": batches * self.attempts,
                "free_only": True, "resets_at": rate.get("resets_at")}


def prepare_output(output, ids, digest, batch_size):
    output = output.resolve()
    if "artifacts" not in output.parts or output.name == "artifacts":
        raise ValueError("Choose a named directory beneath artifacts for all generated outputs")
    output.mkdir(parents=True, exist_ok=True)
    contract = {"version": VERSION, "cohort_sha256": digest,
                "source_count": len(ids), "batch_size": batch_size}
    path = output / "cohort.json"
    if path.exists():
        if loads(path.read_bytes()) != contract:
            raise ValueError("Existing output belongs to a different cohort or batch contract")
    else:
        if (output / "checkpoints").exists() or (output / "sources").exists():
            raise ValueError("Existing source outputs lack a cohort contract; choose a new directory")
        save_json(path, contract)
    (output / "sources").mkdir(exist_ok=True)
    (output / "checkpoints").mkdir(exist_ok=True)
    return output


def load_receipt(output, index, ids):
    path = output / "checkpoints" / f"batch-{index:06d}.json"
    if not path.exists():
        return None
    receipt = loads(path.read_bytes())
    if receipt.get("requested_ids") != ids:
        raise ValueError("Receipt does not match this cohort batch")
    if [row["requested_id"] for row in receipt["records"]] != ids:
        raise ValueError("Receipt rows do not preserve requested Source IDs")
    return receipt


def receipt_complete(output, receipt):
    if receipt is None:
        return False
    for row in receipt["records"]:
        if row["status"] not in TERMINAL:
            return False
        if row["status"] in SUCCESS:
            path = output / "sources" / (row["requested_id"] + ".json")
            if not path.is_file() or path.stat().st_size != row["bytes"]:
                return False
    return True


def collect_batch(client, output, index, ids):
    started = time.monotonic()
    previous = load_receipt(output, index, ids)
    records = {}
    for row in (previous or {}).get("records", []):
        path = output / "sources" / (row["requested_id"] + ".json")
        if (row["status"] == "not_found" or
                (row["status"] in SUCCESS and path.is_file() and path.stat().st_size == row["bytes"])):
            records[row["requested_id"]] = row
    needed = [item for item in ids if item not in records]
    schema = {name: set(types) for name, types in (previous or {}).get("field_types", {}).items()}

    def save_source(requested, value):
        if not isinstance(value, dict) or "id" not in value:
            raise FetchError("invalid_source_object")
        resolved = source_id(value["id"])
        raw = dumps(value) + b"\n"
        atomic_bytes(output / "sources" / (requested + ".json"), raw)
        for name, child in flatten(value).items():
            schema.setdefault(name, set()).add(value_type(child))
        records[requested] = {"requested_id": requested, "resolved_id": canonical(resolved),
                              "status": "ok" if requested == resolved else "redirected",
                              "fetched_at": now(), "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()}

    try:
        if needed:
            result = client.get("/sources", {"filter": "ids.openalex:" + "|".join(needed),
                                              "per_page": 100}, kind="list")
            values = result.get("results")
            if not isinstance(values, list):
                raise FetchError("invalid_source_list")
            indexed = {}
            for value in values:
                if not isinstance(value, dict) or "id" not in value:
                    raise FetchError("invalid_source_object")
                returned_id = source_id(value["id"])
                if returned_id in indexed:
                    raise FetchError("duplicate_source_response_id")
                indexed[returned_id] = value
            # Matching only on IDs is deliberate: list results can be shuffled,
            # omit deleted IDs, or include a merged ID instead of the old one.
            for requested in needed:
                if requested in indexed:
                    save_source(requested, indexed[requested])
            for requested in needed:
                if requested in records:
                    continue
                try:
                    value = client.get("/sources/" + requested)
                    if value is None:
                        # A damaged/stale file can remain from a prior successful
                        # attempt. Confirmed singleton 404 supersedes that file;
                        # keep the directory consistent with the receipt status.
                        (output / "sources" / (requested + ".json")).unlink(missing_ok=True)
                        records[requested] = {"requested_id": requested, "resolved_id": None,
                                              "status": "not_found", "fetched_at": now()}
                    else:
                        save_source(requested, value)
                except FetchError as error:
                    records[requested] = {"requested_id": requested, "resolved_id": None,
                                          "status": "error:" + error.code, "fetched_at": now()}
    except FetchError as error:
        for requested in needed:
            if requested not in records:
                records[requested] = {"requested_id": requested, "resolved_id": None,
                                      "status": "error:" + error.code, "fetched_at": now()}
    receipt = {"version": VERSION, "requested_ids": ids,
               "records": [records[item] for item in ids],
               "field_types": {key: sorted(types) for key, types in sorted(schema.items())},
               "completed_at": now(), "elapsed_seconds": round(time.monotonic() - started, 3)}
    save_json(output / "checkpoints" / f"batch-{index:06d}.json", receipt)
    return receipt


def read_receipts(output, ids, batch_size):
    records, schema = {}, {}
    for index, offset in enumerate(range(0, len(ids), batch_size)):
        receipt = load_receipt(output, index, ids[offset:offset + batch_size])
        if receipt is None:
            continue
        for row in receipt["records"]:
            records[row["requested_id"]] = row
        for name, types in receipt["field_types"].items():
            schema.setdefault(name, set()).update(types)
    return records, {key: sorted(types) for key, types in sorted(schema.items())}


def source_from_record(output, record):
    raw = (output / "sources" / (record["requested_id"] + ".json")).read_bytes()
    if len(raw) != record["bytes"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError(f"Source JSON {record['requested_id']} does not match its receipt checksum; "
                         "remove this JSON file and resume collection to refetch it")
    value = loads(raw)
    if canonical(value.get("id", "")) != record["resolved_id"]:
        raise ValueError("Source JSON ID does not match its receipt")
    return value


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def convert_csv(output, ids, records, field_types):
    started = time.monotonic()
    fields = list(field_types)
    header = list(META_COLUMNS) + fields
    temporary = output / "sources.csv.tmp"
    states = {name: collections.Counter() for name in fields}
    expected_hashes = {}
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(header)
        for requested in ids:
            record = records.get(requested, {"status": "pending", "resolved_id": None,
                                            "fetched_at": None})
            source = (source_from_record(output, record) if record["status"] in SUCCESS else {})
            flat = flatten(source)
            expected_hashes[requested] = content_hash(source)
            if not set(flat).issubset(field_types):
                raise ValueError("Source fields are absent from the receipt schema union")
            values = []
            for field in fields:
                value = flat.get(field, MISSING)
                state = ("absent" if value is MISSING else "null" if value is None
                         else "empty_string" if value == "" else
                         "empty_array" if isinstance(value, list) and not value else
                         "empty_object" if isinstance(value, dict) and not value else "present")
                states[field][state] += 1
                values.append(encode_cell(value))
            writer.writerow([canonical(requested), encode_cell(record["resolved_id"]),
                             record["status"], encode_cell(record["fetched_at"])] + values)
    write_seconds = time.monotonic() - started
    # Verification reads the actual written CSV in order and compares every
    # present Source value to its archived JSON; it is not a sample check.
    verified = 0
    arrays = 0
    source_bytes = 0
    csv.field_size_limit(sys.maxsize)
    with temporary.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != header:
            raise ValueError("Written CSV header does not match the complete schema")
        for requested, row in zip(ids, reader):
            if row.get("source_id") != canonical(requested) or None in row:
                raise ValueError("CSV row ID/order or width changed during conversion")
            record = records.get(requested, {"status": "pending", "resolved_id": None,
                                            "fetched_at": None})
            if (row["fetch_status"] != record["status"]
                    or decode_cell(row["resolved_id"]) != record["resolved_id"]
                    or decode_cell(row["fetched_at"]) != record["fetched_at"]):
                raise ValueError("CSV provenance does not match the acquisition receipt")
            restored = {}
            for field in fields:
                value = decode_cell(row[field])
                if value is not MISSING:
                    restored[field] = value
                    arrays += isinstance(value, list)
            if content_hash(unflatten(restored)) != expected_hashes.pop(requested):
                raise ValueError("CSV readback does not preserve the complete Source JSON")
            if record["status"] in SUCCESS:
                source_bytes += record["bytes"]
            verified += 1
        if verified != len(ids) or next(reader, None) is not None:
            raise ValueError("CSV row count differs from the original Source cohort")
    verification_seconds = time.monotonic() - started - write_seconds
    os.replace(temporary, output / "sources.csv")
    return {"csv": {"filename": "sources.csv", "rows": verified, "columns": len(header),
                    "bytes": (output / "sources.csv").stat().st_size,
                    "sha256": sha256_file(output / "sources.csv")},
            "source_json_bytes": source_bytes,
            "field_types": field_types,
            "field_states": {name: dict(counts) for name, counts in states.items()},
            "verification": {"completed": True, "passed": True, "all_rows_read_back": True,
                             "requested_id_order_and_uniqueness": True,
                             "all_source_fields_roundtrip_equal": True,
                             "json_array_cells_validated": arrays},
            "timing_seconds": {"csv_write": round(write_seconds, 3),
                               "csv_full_readback": round(verification_seconds, 3)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--requests-per-second", type=float, default=80)
    parser.add_argument("--max-attempts", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--max-list-requests", type=int)
    parser.add_argument("--max-batches", type=int, help="Limit new batches for a resumable pilot")
    parser.add_argument("--convert-only", action="store_true")
    parser.add_argument("--no-convert", action="store_true")
    args = parser.parse_args(argv)
    if not (1 <= args.batch_size <= 100 and 1 <= args.workers <= 64
            and 0 < args.requests_per_second <= 95 and 1 <= args.max_attempts <= 10
            and args.timeout > 0):
        parser.error("Invalid batch, concurrency, retry, timeout or rate setting (rate must be <=95/s)")
    if args.max_list_requests is not None and args.max_list_requests < 1:
        parser.error("--max-list-requests must be positive")
    if args.max_batches is not None and args.max_batches < 1:
        parser.error("--max-batches must be positive")
    if args.convert_only and args.no_convert:
        parser.error("--convert-only cannot be combined with --no-convert")
    started = time.monotonic()
    ids, digest = read_ids(args.ids)
    output = prepare_output(args.output, ids, digest, args.batch_size)
    previous = (loads((output / "manifest.json").read_bytes())
                if (output / "manifest.json").exists() else {})
    if (args.convert_only and previous.get("status") in {"acquired", "partial"}
            and not (output / "acquisition-manifest.json").exists()):
        save_json(output / "acquisition-manifest.json", previous)
    manifest = {**previous, "version": VERSION, "started_at": previous.get("started_at", now()),
                "last_run_started_at": now(), "status": "partial",
                "cohort_sha256": digest, "requested_sources": len(ids),
                "cohort_sha256_encoding": "UTF-8 short Source IDs (S<number>), input order, one per line, final newline",
                "api": {"base": API, "entity": "sources", "full_source_objects": True,
                        "select": None, "batch_filter": "ids.openalex", "batch_size": args.batch_size},
                "csv_encoding": {"absent_attribute": "\\M", "json_null": "\\N",
                                 "escaped_string_prefix": "\\S followed by a JSON string",
                                 "other_strings": "original text", "other_values": "compact JSON",
                                 "objects": "dot paths; empty objects stay {}",
                                 "path_keys": "backslashes and dots escaped with a backslash",
                                 "arrays": "complete compact JSON in one cell; never expanded"},
                "timing_seconds": previous.get("timing_seconds", {}).copy()}
    manifest.pop("verification", None)
    manifest.pop("csv", None)
    save_json(output / "manifest.json", manifest)
    if not args.convert_only:
        jobs = []
        for index, offset in enumerate(range(0, len(ids), args.batch_size)):
            batch = ids[offset:offset + args.batch_size]
            if not receipt_complete(output, load_receipt(output, index, batch)):
                jobs.append((index, batch))
        if args.max_batches is not None:
            jobs = jobs[:args.max_batches]
        if jobs:
            client = Client(api_key(args.env_file), rate=args.requests_per_second,
                            attempts=args.max_attempts, timeout=args.timeout,
                            max_list_requests=args.max_list_requests)
            manifest["free_budget"] = client.free_budget(len(jobs))
            save_json(output / "budget-before.json", manifest["free_budget"])
            save_json(output / "manifest.json", manifest)
            fetch_started = time.monotonic()
            completed = 0
            status = collections.Counter()
            print(f"Collecting {len(jobs):,} batches, up to {args.workers} workers; free-only budget confirmed",
                  flush=True)
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(collect_batch, client, output, index, batch): index
                           for index, batch in jobs}
                for future in as_completed(futures):
                    receipt = future.result()
                    completed += 1
                    status.update(row["status"] for row in receipt["records"])
                    if completed == 1 or completed % 20 == 0 or completed == len(jobs):
                        progress = {"completed_batches_this_run": completed,
                                    "scheduled_batches_this_run": len(jobs),
                                    "status_counts_this_run": dict(status),
                                    "request_counts_this_run": dict(client.requests),
                                    "effective_requests_per_second": client.rate,
                                    "throttle_responses_this_run": client.throttle_count,
                                    "elapsed_seconds": round(time.monotonic() - fetch_started, 3),
                                    "updated_at": now()}
                        save_json(output / "progress.json", progress)
                        print(f"Batches {completed:,}/{len(jobs):,}; statuses {dict(status)}; "
                              f"elapsed {progress['elapsed_seconds']:.1f}s", flush=True)
            manifest["request_counts_this_run"] = dict(client.requests)
            manifest["rate_control"] = {"maximum_requests_per_second": client.maximum_rate,
                                       "final_requests_per_second": client.rate,
                                       "http_429_responses": client.throttle_count,
                                       "recent_throttle_events": client.rate_events}
            manifest["timing_seconds"]["collection_this_run"] = round(time.monotonic() - fetch_started, 3)
            if client.abort_reason:
                manifest["collection_stop_reason"] = client.abort_reason
    records, fields = read_receipts(output, ids, args.batch_size)
    counts = collections.Counter(records.get(item, {"status": "pending"})["status"] for item in ids)
    manifest["status_counts"] = dict(counts)
    manifest["source_json_files"] = sum(counts[status] for status in SUCCESS)
    complete = all(status in TERMINAL for status in counts)
    if not args.convert_only:
        acquisition = {**manifest, "status": "acquired" if complete else "partial",
                       "completed_at": now()}
        save_json(output / "acquisition-manifest.json", acquisition)
    if (output / "acquisition-manifest.json").exists():
        manifest["acquisition_manifest"] = {"filename": "acquisition-manifest.json",
                                            "sha256": sha256_file(output / "acquisition-manifest.json")}
    if not args.no_convert:
        print(f"Writing CSV for all {len(ids):,} requested Sources; {len(fields)} Source columns", flush=True)
        converted = convert_csv(output, ids, records, fields)
        manifest["timing_seconds"].update(converted.pop("timing_seconds"))
        manifest.update(converted)
    manifest["status"] = ("complete" if complete and not args.no_convert else
                          "acquired" if complete else "partial")
    manifest["completed_at"] = now()
    manifest["timing_seconds"]["total_this_run"] = round(time.monotonic() - started, 3)
    save_json(output / "manifest.json", manifest)
    print(f"Status {manifest['status']}; requested {len(ids):,}; counts {dict(counts)}; "
          f"elapsed {manifest['timing_seconds']['total_this_run']:.1f}s", flush=True)
    return 0 if complete else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FetchError, ValueError) as error:
        print(f"Stopped: {error}", file=sys.stderr)
        sys.exit(2)
