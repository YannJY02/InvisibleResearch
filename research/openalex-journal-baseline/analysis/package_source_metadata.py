"""Package a verified Source run without changing its raw files.

Use --csv explicitly (a filename relative to --run, or an absolute path).
Only delivery-manifest.json marks a complete package; .partial files do not.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import time
import uuid
import zipfile

CHUNK = 1024 * 1024
TERMINAL = {"ok", "redirected", "not_found"}
VERIFICATION = (
    "completed",
    "passed",
    "all_rows_read_back",
    "requested_id_order_and_uniqueness",
    "all_source_fields_roundtrip_equal",
)


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def load_inputs(run: Path, csv_path: Path) -> tuple[dict, list[Path], dict]:
    manifest_raw = (run / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw)
    verification = manifest.get("verification", {})
    if (manifest.get("status") != "complete"
            or not all(verification.get(key) is True for key in VERIFICATION)):
        raise ValueError("Run must be complete with CSV roundtrip verification passed")
    statuses = manifest["status_counts"]
    if any(count and status not in TERMINAL for status, count in statuses.items()):
        raise ValueError("Run has unresolved source statuses")
    requested = manifest["requested_sources"]
    if sum(statuses.values()) != requested or manifest["csv"]["rows"] != requested:
        raise ValueError("Manifest does not cover all requested sources")

    ids = []
    ids_raw = (run / "source-ids.txt").read_bytes()
    for line in ids_raw.decode("utf-8").splitlines():
        match = re.fullmatch(r"https://openalex\.org/(S[0-9]+)", line)
        if not match:
            raise ValueError("source-ids.txt must contain canonical Source URLs")
        ids.append(match[1])
    if len(ids) != requested or len(set(ids)) != requested:
        raise ValueError("Input IDs are missing or duplicated")
    cohort_hash = hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()
    if cohort_hash != manifest["cohort_sha256"]:
        raise ValueError("Input ID order differs from the verified cohort")

    cohort_raw = (run / "cohort.json").read_bytes()
    cohort = json.loads(cohort_raw)
    if cohort["cohort_sha256"] != cohort_hash or cohort["source_count"] != requested:
        raise ValueError("Cohort contract differs from the final manifest")
    batch_size = cohort["batch_size"]
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("Invalid cohort batch size")
    checkpoints = [run / "checkpoints" / f"batch-{index:06d}.json"
                   for index in range((requested + batch_size - 1) // batch_size)]
    if set((run / "checkpoints").glob("batch-*.json")) != set(checkpoints):
        raise ValueError("Checkpoint inventory does not cover this cohort")
    expected = {}
    receipt_counts = Counter()
    for index, path in enumerate(checkpoints):
        raw = path.read_bytes()
        receipt = json.loads(raw)
        batch = ids[index * batch_size:(index + 1) * batch_size]
        if (receipt["requested_ids"] != batch
                or [record["requested_id"] for record in receipt["records"]] != batch):
            raise ValueError("Checkpoint rows differ from the requested cohort")
        expected[path.relative_to(run).as_posix()] = {
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        for record in receipt["records"]:
            status = record["status"]
            if status not in TERMINAL:
                raise ValueError("Checkpoint has an unresolved source status")
            receipt_counts[status] += 1
            if status != "not_found":
                expected["sources/" + record["requested_id"] + ".json"] = {
                    "bytes": record["bytes"], "sha256": record["sha256"]}
    if receipt_counts != Counter({key: count for key, count in statuses.items() if count}):
        raise ValueError("Checkpoint statuses differ from the final manifest")

    sources = sorted((run / "sources").glob("*.json"), key=lambda path: path.name)
    expected_raw = statuses.get("ok", 0) + statuses.get("redirected", 0)
    if len(sources) != expected_raw or manifest["source_json_files"] != expected_raw:
        raise ValueError("Source JSON file count differs from completed statuses")
    if {path.relative_to(run).as_posix() for path in sources} != {
            name for name in expected if name.startswith("sources/")}:
        raise ValueError("Source JSON inventory differs from successful receipt IDs")
    members = [run / name for name in (
        "source-ids.txt", "manifest.json", "input-provenance.json", "cohort.json",
    )]
    if (run / "schema.json").exists():
        members.append(run / "schema.json")
    acquisition = manifest.get("acquisition_manifest")
    if acquisition:
        if acquisition["filename"] != "acquisition-manifest.json":
            raise ValueError("Unexpected acquisition manifest filename")
        members.append(run / "acquisition-manifest.json")
    members.extend(checkpoints)
    members.extend(sources)
    if any(not path.is_file() or path.is_symlink() for path in members):
        raise ValueError("Archive inputs must be regular files, not symlinks")
    if not csv_path.is_file() or csv_path.is_symlink() or csv_path.suffix.lower() != ".csv":
        raise ValueError("--csv must identify a regular CSV file")
    if csv_path.stat().st_size != manifest["csv"]["bytes"]:
        raise ValueError("Selected CSV size differs from its verified manifest")
    for path in members:
        name = path.relative_to(run).as_posix()
        if name not in expected:
            raw = {"manifest.json": manifest_raw, "source-ids.txt": ids_raw,
                   "cohort.json": cohort_raw}.get(name)
            if raw is None:
                raw = path.read_bytes()
            expected[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if (acquisition and expected.get("acquisition-manifest.json", {}).get("sha256")
            != acquisition["sha256"]):
        raise ValueError("Acquisition manifest differs from the final manifest")
    return manifest, members, expected


def compress_csv(source: Path, target: Path, expected: dict) -> dict:
    before = source.stat()
    digest = hashlib.sha256()
    size = 0
    with source.open("rb") as reader, target.open("xb") as raw:
        with gzip.GzipFile(filename=source.name, mode="wb", compresslevel=1,
                           fileobj=raw, mtime=0) as writer:
            while chunk := reader.read(CHUNK):
                digest.update(chunk)
                size += len(chunk)
                writer.write(chunk)
    after = source.stat()
    if (size != before.st_size or before.st_mtime_ns != after.st_mtime_ns
            or digest.hexdigest() != expected["sha256"]):
        raise ValueError("CSV changed or differs from its verified SHA256")
    restored = hashlib.sha256()
    restored_bytes = 0
    with gzip.open(target, "rb") as reader:
        while chunk := reader.read(CHUNK):
            restored.update(chunk)
            restored_bytes += len(chunk)
    if restored_bytes != size or restored.hexdigest() != digest.hexdigest():
        raise ValueError("Gzip CSV readback differs from the verified original")
    return {"bytes": target.stat().st_size, "sha256": sha256(target),
            "original_csv_name": source.name, "uncompressed_bytes": size,
            "uncompressed_sha256": digest.hexdigest(),
            "verification": {"decompressed_readback_passed": True}}


def archive_sources(run: Path, paths: list[Path], target: Path, expected: dict) -> list[dict]:
    """Read each source once while hashing and writing its ZIP member."""
    members = []
    last_progress = time.monotonic()
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as archive:
        for index, path in enumerate(paths, 1):
            before = path.stat()
            name = path.relative_to(run).as_posix()
            digest = hashlib.sha256()
            size = 0
            # open(name) uses a fixed 1980 timestamp and this archive's level.
            with path.open("rb") as reader, archive.open(
                    name, "w", force_zip64=before.st_size >= zipfile.ZIP64_LIMIT) as writer:
                while chunk := reader.read(CHUNK):
                    digest.update(chunk)
                    size += len(chunk)
                    writer.write(chunk)
            after = path.stat()
            if size != before.st_size or before.st_mtime_ns != after.st_mtime_ns:
                raise ValueError("Archive input changed: " + name)
            if size != expected[name]["bytes"] or digest.hexdigest() != expected[name]["sha256"]:
                raise ValueError("Archive input differs from its verified receipt: " + name)
            members.append({"path": name, "bytes": size, "sha256": digest.hexdigest(),
                            "crc32": f"{archive.getinfo(name).CRC:08x}",
                            "source_mtime_ns": before.st_mtime_ns})
            if time.monotonic() - last_progress >= 15:
                print(f"Archived {index:,}/{len(paths):,} members", flush=True)
                last_progress = time.monotonic()
    return members


def verify_zip(path: Path, members: list[dict]) -> dict:
    expected = {member["path"]: member for member in members}
    total = 0
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(expected) or set(names) != set(expected):
            raise ValueError("ZIP member set differs from the source inventory")
        for info in archive.infolist():
            member = expected[info.filename]
            size = 0
            with archive.open(info) as reader:
                while chunk := reader.read(CHUNK):
                    size += len(chunk)  # ZipExtFile also checks the full CRC.
            if (size != member["bytes"] or info.file_size != size
                    or f"{info.CRC:08x}" != member["crc32"]):
                raise ValueError("ZIP member readback differs: " + info.filename)
            total += size
    return {"crc_readback_passed": True, "members": len(members),
            "uncompressed_bytes": total}


def publish(partial: Path, final: Path, digest: str) -> None:
    """Publish atomically; an existing different file is never overwritten."""
    if final.is_symlink():
        raise FileExistsError("Delivery output is a symlink: " + final.name)
    if final.exists():
        if sha256(final) != digest:
            raise FileExistsError("Different existing delivery file: " + final.name)
    else:
        os.link(partial, final)
    partial.unlink()


def reuse_delivery(run: Path, output: Path, csv_path: Path, paths: list[Path],
                   prefix: str, manifest: dict, expected: dict) -> dict | None:
    marker = output / "delivery-manifest.json"
    if not marker.exists():
        return None
    previous = json.loads(marker.read_text(encoding="utf-8"))
    if (previous.get("status") != "complete" or previous.get("prefix") != prefix
            or previous.get("source_manifest_sha256") != sha256(run / "manifest.json")
            or previous.get("original_csv_name") != csv_path.name
            or sha256(csv_path) != manifest["csv"]["sha256"]):
        raise FileExistsError("Existing package belongs to different or unverified inputs")
    inventory = {member["path"]: member for member in previous["members"]}
    if len(inventory) != len(paths):
        raise FileExistsError("Existing package has a different member inventory")
    for path in paths:
        name = path.relative_to(run).as_posix()
        member = inventory.get(name)
        stat = path.stat()
        if (not member or member["bytes"] != stat.st_size
                or member["source_mtime_ns"] != stat.st_mtime_ns
                or member["sha256"] != expected[name]["sha256"]):
            raise FileExistsError("Archive inputs changed after the previous package")
    for info in previous["files"].values():
        path = output / info["filename"]
        if not path.is_file() or path.stat().st_size != info["bytes"] or sha256(path) != info["sha256"]:
            raise FileExistsError("Existing delivery bytes differ from their manifest")
    return previous


def package(run: Path, csv_path: Path, output: Path, prefix: str) -> dict:
    started = time.monotonic()
    manifest, paths, expected = load_inputs(run, csv_path)
    previous = reuse_delivery(run, output, csv_path, paths, prefix, manifest, expected)
    if previous:
        print("Existing complete package verified", flush=True)
        return previous
    output.mkdir(parents=True, exist_ok=True)
    nonce = uuid.uuid4().hex
    gzip_name, zip_name = prefix + ".csv.gz", prefix + "-json.zip"
    gzip_partial = output / (gzip_name + ".partial-" + nonce)
    zip_partial = output / (zip_name + ".partial-" + nonce)
    marker_partial = output / ("delivery-manifest.json.partial-" + nonce)
    source_manifest_hash = sha256(run / "manifest.json")
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            gz_future = pool.submit(compress_csv, csv_path, gzip_partial, manifest["csv"])
            zip_future = pool.submit(archive_sources, run, paths, zip_partial, expected)
            gzip_info = gz_future.result()
            members = zip_future.result()
        zip_verification = verify_zip(zip_partial, members)
        if sha256(run / "manifest.json") != source_manifest_hash:
            raise ValueError("Source manifest changed during packaging")
        zip_info = {"filename": zip_name, "bytes": zip_partial.stat().st_size,
                    "sha256": sha256(zip_partial), "verification": zip_verification}
        gzip_info["filename"] = gzip_name
        result = {"status": "complete", "prefix": prefix,
                  "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                  "elapsed_seconds": round(time.monotonic() - started, 3),
                  "source_manifest_sha256": source_manifest_hash,
                  "original_csv_name": csv_path.name,
                  "requested_sources": manifest["requested_sources"],
                  "status_counts": manifest["status_counts"],
                  "source_json_files": manifest["source_json_files"],
                  "compression_level": 1,
                  "files": {"csv_gzip": gzip_info, "source_json_zip": zip_info},
                  "members": members}
        publish(zip_partial, output / zip_name, zip_info["sha256"])
        publish(gzip_partial, output / gzip_name, gzip_info["sha256"])
        marker_partial.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        publish(marker_partial, output / "delivery-manifest.json", sha256(marker_partial))
        print(f"Package verified: {manifest['source_json_files']:,} JSON files; "
              f"{result['elapsed_seconds']:.1f} seconds", flush=True)
        return result
    finally:
        for partial in (gzip_partial, zip_partial, marker_partial):
            partial.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path,
                        help="Absolute CSV path, or filename relative to --run")
    parser.add_argument("--output", type=Path, help="Default: RUN/delivery")
    parser.add_argument("--prefix", help="Delivery filename stem; default: selected CSV stem")
    args = parser.parse_args()
    run = args.run.resolve()
    csv_path = args.csv if args.csv.is_absolute() else run / args.csv
    prefix = args.prefix or csv_path.stem
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", prefix):
        parser.error("--prefix must be a plain filename stem")
    try:
        package(run, csv_path, args.output or run / "delivery", prefix)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Packaging failed: {error}\n")


if __name__ == "__main__":
    main()
