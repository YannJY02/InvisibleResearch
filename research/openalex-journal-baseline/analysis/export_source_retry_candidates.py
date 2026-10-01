"""Export verified retry Source objects as a separate current-ID metadata CSV.

Only an already completed retry run is accepted. All successful phase receipts
are verified before their objects are considered. When several observations
resolve to one Source, choose the latest observation with a deterministic
receipt-path tie break, retaining every observation in selection provenance.
No API requests, old-to-new identity assertions or original-export writes occur.
"""

import argparse
from collections import Counter
import ctypes
import datetime as dt
import errno
import hashlib
import os
from pathlib import Path
import shutil
import sys
import uuid

import collect_source_metadata as base

PHASES = ("pass1", "pass2", "issn", "merge")
_LIBC = ctypes.CDLL(None, use_errno=True) if sys.platform == "darwin" else None
_CLONEFILE = getattr(_LIBC, "clonefile", None)
if _CLONEFILE is not None:
    _CLONEFILE.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int)
    _CLONEFILE.restype = ctypes.c_int
CSV_ENCODING = {
    "absent_attribute": "\\M", "json_null": "\\N",
    "escaped_string_prefix": "\\S followed by a JSON string",
    "other_strings": "original text", "other_values": "compact JSON",
    "objects": "dot paths; empty objects stay {}",
    "path_keys": "backslashes and dots escaped with a backslash",
    "arrays": "complete compact JSON in one cell; never expanded",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def clone_file(source, target):
    """Try macOS clonefile: independent inodes with shared copy-on-write extents."""
    if _CLONEFILE is None:
        return False
    if _CLONEFILE(os.fsencode(source), os.fsencode(target), 0) == 0:
        return True
    code = ctypes.get_errno()
    if code in {errno.ENOTSUP, errno.EOPNOTSUPP, errno.EXDEV, errno.ENOSYS, errno.EINVAL}:
        return False
    raise OSError(code, os.strerror(code), str(target))


def atomic_source_copy(source, target, raw, reserve_bytes=0):
    """Clone, or copy only when the remaining export fits; verify before rename."""
    if target.is_symlink() or target.parent.resolve() != target.parent:
        raise ValueError("Derived Source JSON destination may not be a symlink")
    temporary = target.with_name(target.name + ".clone-" + uuid.uuid4().hex)
    try:
        cloned = clone_file(source, temporary)
        if cloned:
            method = "apfs_clonefile_copy_on_write"
        else:
            # Preserve room for all remaining ordinary copies, a conservative
            # CSV estimate, and provenance. Do not fill the disk with duplicates.
            free = shutil.disk_usage(target.parent).free
            if free < len(raw) + reserve_bytes:
                raise OSError(errno.ENOSPC, "Ordinary JSON copy would consume space reserved for "
                              "the remaining candidate export; APFS clonefile is unavailable")
            with temporary.open("xb") as stream:
                stream.write(raw)
            method = "ordinary_byte_copy"
        if temporary.stat().st_size != len(raw) or base.sha256_file(temporary) != sha(raw):
            raise ValueError("Derived Source JSON copy does not preserve verified response bytes")
        copied_stat, source_stat = temporary.stat(), source.stat()
        if (copied_stat.st_dev, copied_stat.st_ino) == (source_stat.st_dev, source_stat.st_ino):
            raise ValueError("Derived Source JSON must not be a hard link")
        os.replace(temporary, target)
        return method
    finally:
        temporary.unlink(missing_ok=True)


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Receipt completed_at must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


def source_object(run, receipt):
    path = (run / receipt["json_file"]).resolve()
    if not path.is_relative_to(run):
        raise ValueError("Receipt source path escapes the retry run")
    raw = path.read_bytes()
    if len(raw) != receipt["json_bytes"] or sha(raw) != receipt["json_sha256"]:
        raise ValueError("Candidate Source JSON does not match its receipt checksum")
    value = base.loads(raw)
    if not isinstance(value, dict) or base.source_id(value.get("id", "")) != base.source_id(receipt["resolved_id"]):
        raise ValueError("Candidate Source JSON ID does not match its receipt")
    return raw, value


def observations(run):
    by_id, phase_counts = {}, Counter()
    success_counts = Counter()
    for phase in PHASES:
        directory = run / "checkpoints" / phase
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            if not path.resolve().is_relative_to(run):
                raise ValueError("Receipt path escapes the retry run")
            raw = path.read_bytes()
            row = base.loads(raw)
            if row["phase"] != phase or row["key"] != path.stem:
                raise ValueError("Receipt phase/key does not match its checkpoint path")
            phase_counts[phase] += 1
            if row["status"] not in base.SUCCESS:
                continue
            if row["status_code"] != 200:
                raise ValueError("A successful receipt must have HTTP status 200")
            _, value = source_object(run, row)
            resolved = base.source_id(value["id"])
            timestamp(row["completed_at"])
            observation = {"receipt_file": str(path.relative_to(run)),
                           "receipt_sha256": sha(raw), "receipt": row}
            by_id.setdefault(resolved, []).append(observation)
            success_counts[phase] += 1
    return by_id, dict(phase_counts), dict(success_counts)


def export_candidates(run):
    run = run.resolve()
    if "artifacts" not in run.parts or run.name == "artifacts":
        raise ValueError("The retry run must be a named artifacts directory")
    summary_path = run / "summary.json"
    summary_raw = summary_path.read_bytes()
    summary = base.loads(summary_raw)
    if summary.get("status") != "complete" or not summary.get("verification", {}).get("passed"):
        raise ValueError("The outer retry summary must be complete and verified before export")
    output = run / "candidate-csv"
    if output.resolve() != output:
        raise ValueError("Derived candidate CSV output may not be a symlink")
    output.mkdir(exist_ok=True)
    sources = output / "sources"
    if sources.resolve() != sources:
        raise ValueError("Derived Source JSON directory may not be a symlink")
    sources.mkdir(exist_ok=True)
    existing_manifest = output / "manifest.json"
    if existing_manifest.exists():
        previous = base.loads(existing_manifest.read_bytes())
        if previous.get("retry_summary_sha256") != sha(summary_raw):
            raise ValueError("Existing derived output belongs to a different retry summary")
    manifest = {"version": 1, "status": "running", "started_at": base.now(),
                "retry_run": str(run), "retry_summary_sha256": sha(summary_raw),
                "retry_completed_at": summary.get("completed_at"),
                "selection_rule": "latest timezone-aware completed_at, then receipt path; "
                                  "exact response bytes are retained",
                "identity_interpretation": "Current Source metadata only; inclusion does not "
                                           "confirm an old-to-new identity or merge",
                "original_export_mutated": False, "api_requests": 0,
                "csv_encoding": CSV_ENCODING}
    base.save_json(output / "manifest.json", manifest)
    by_id, phase_counts, success_counts = observations(run)
    ids = sorted(by_id, key=lambda key: int(key[1:]))
    records, field_types, selections = {}, {}, []
    selected_types = Counter()
    selected_json_bytes = sum(max(items, key=lambda item: (
        timestamp(item["receipt"]["completed_at"]), item["receipt_file"]))["receipt"]["json_bytes"]
        for items in by_id.values())
    remaining_json_bytes = selected_json_bytes
    ordinary_copy_reserve = 2 * selected_json_bytes + 32 * 1024 * 1024
    copy_methods = Counter()
    for resolved in ids:
        candidates = sorted(by_id[resolved], key=lambda item: (
            timestamp(item["receipt"]["completed_at"]), item["receipt_file"]))
        chosen = candidates[-1]
        receipt = chosen["receipt"]
        raw, value = source_object(run, receipt)
        source_type = value.get("type", "__MISSING__")
        selected_types[source_type if isinstance(source_type, str) else
                       "__" + base.value_type(source_type).upper() + "__"] += 1
        target = sources / (resolved + ".json")
        if target.is_symlink():
            raise ValueError("Derived Source JSON output may not be a symlink")
        method = atomic_source_copy((run / receipt["json_file"]).resolve(), target, raw,
                                    reserve_bytes=ordinary_copy_reserve + remaining_json_bytes - len(raw))
        copy_methods[method] += 1
        remaining_json_bytes -= len(raw)
        for field, child in base.flatten(value).items():
            field_types.setdefault(field, set()).add(base.value_type(child))
        records[resolved] = {"requested_id": resolved,
                             "resolved_id": base.canonical(resolved), "status": "ok",
                             "fetched_at": receipt["completed_at"],
                             "bytes": len(raw), "sha256": receipt["json_sha256"]}
        selections.append({"source_id": resolved,
                           "selected_receipt_file": chosen["receipt_file"],
                           "selected_receipt_sha256": chosen["receipt_sha256"],
                           "selected_json_sha256": receipt["json_sha256"],
                           "selected_completed_at": receipt["completed_at"],
                           "observations": candidates})
    payload = ("\n".join(ids) + ("\n" if ids else "")).encode()
    base.atomic_bytes(output / "source-ids.txt", payload)
    provenance = {"version": 1, "retry_summary_sha256": sha(summary_raw),
                  "selection_rule": manifest["selection_rule"],
                  "identity_interpretation": manifest["identity_interpretation"],
                  "selections": selections}
    provenance_raw = base.dumps(provenance) + b"\n"
    base.atomic_bytes(output / "selection-provenance.json", provenance_raw)
    fields = {key: sorted(types) for key, types in sorted(field_types.items())}
    conversion = base.convert_csv(output, ids, records, fields)
    if sha(summary_path.read_bytes()) != sha(summary_raw):
        raise ValueError("The outer retry summary changed during export")
    manifest.update(conversion)
    manifest.update(status="complete", completed_at=base.now(),
                    requested_sources=len(ids), source_json_files=len(ids),
                    cohort_sha256=sha(payload),
                    cohort_sha256_encoding="UTF-8 numeric-sorted short Source IDs, one per line, final LF",
                    checkpoint_counts_by_phase=phase_counts,
                    successful_observation_counts_by_phase=success_counts,
                    successful_observations=sum(success_counts.values()),
                    observations_deduplicated=sum(success_counts.values()) - len(ids),
                    selected_source_records=[records[key] for key in ids],
                    selection_provenance={"filename": "selection-provenance.json",
                                          "sha256": sha(provenance_raw),
                                          "all_successful_receipt_objects_verified": True},
                    selected_source_type_counts=dict(selected_types))
    manifest.update(derived_json_copy_methods=dict(copy_methods),
                    copy_verification="Every temporary copy has verified byte length and SHA-256 "
                                      "before atomic rename; no hard links are used")
    base.save_json(output / "manifest.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    result = export_candidates(args.run)
    print(base.dumps({"status": result["status"], "csv": result["csv"],
                      "successful_observations": result["successful_observations"],
                      "observations_deduplicated": result["observations_deduplicated"],
                      "verification": result["verification"]}).decode())


if __name__ == "__main__":
    main()
