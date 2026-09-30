from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


SCRIPT = (Path(__file__).parents[1] / "research/openalex-journal-baseline/analysis"
          / "package_source_metadata.py")
SPEC = importlib.util.spec_from_file_location("source_metadata_package", SCRIPT)
PACKAGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGER)


class SourceMetadataPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)
        (self.run / "sources").mkdir()
        (self.run / "sources/S1.json").write_text(
            '{"id":"https://openalex.org/S1","topics":[{"name":"传播学"}]}\n',
            encoding="utf-8")
        # Redirects keep the requested filename but the returned identity.
        (self.run / "sources/S2.json").write_text(
            '{"id":"https://openalex.org/S20","topics":[]}\n', encoding="utf-8")
        (self.run / "source-ids.txt").write_text(
            "https://openalex.org/S1\nhttps://openalex.org/S2\nhttps://openalex.org/S3\n")
        (self.run / "input-provenance.json").write_text('{"source":"fixture"}\n')
        (self.run / "schema.json").write_text('{"topics":"array"}\n')
        (self.run / "private-config.json").write_text('{"private":"excluded"}\n')
        self.csv = self.run / "sources.csv"
        self.csv.write_bytes(b'id,status,nested\nS1,ok,"[]"\nS2,redirected,"[]"\nS3,not_found,\n')
        self.manifest = {
            "status": "complete", "requested_sources": 3, "source_json_files": 2,
            "cohort_sha256": hashlib.sha256(b"S1\nS2\nS3\n").hexdigest(),
            "status_counts": {"ok": 1, "redirected": 1, "not_found": 1},
            "csv": {"filename": self.csv.name, "rows": 3, "columns": 3,
                    "bytes": self.csv.stat().st_size,
                    "sha256": hashlib.sha256(self.csv.read_bytes()).hexdigest()},
            "verification": {key: True for key in PACKAGER.VERIFICATION},
        }
        acquisition_raw = b'{"status":"acquired","requested_sources":3}\n'
        (self.run / "acquisition-manifest.json").write_bytes(acquisition_raw)
        self.manifest["acquisition_manifest"] = {
            "filename": "acquisition-manifest.json",
            "sha256": hashlib.sha256(acquisition_raw).hexdigest(),
        }
        (self.run / "cohort.json").write_text(json.dumps({
            "version": 1, "cohort_sha256": self.manifest["cohort_sha256"],
            "source_count": 3, "batch_size": 2,
        }))
        (self.run / "checkpoints").mkdir()
        for index, ids in enumerate((["S1", "S2"], ["S3"])):
            records = []
            for source_id in ids:
                status = {"S1": "ok", "S2": "redirected", "S3": "not_found"}[source_id]
                record = {"requested_id": source_id, "status": status}
                if status != "not_found":
                    raw = (self.run / "sources" / (source_id + ".json")).read_bytes()
                    record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                records.append(record)
            (self.run / "checkpoints" / f"batch-{index:06d}.json").write_text(
                json.dumps({"requested_ids": ids, "records": records, "field_types": {}}))
        self.save_manifest()
        self.output = self.run / "delivery"
        self.prefix = "openalex-sources-2026-09-30"

    def save_manifest(self) -> None:
        (self.run / "manifest.json").write_text(json.dumps(self.manifest) + "\n")

    def package(self) -> dict:
        return PACKAGER.package(self.run, self.csv, self.output, self.prefix)

    def test_verified_package_preserves_members_and_csv_with_not_found_rows(self) -> None:
        result = self.package()
        self.assertEqual(result["source_json_files"], 2)
        self.assertEqual(result["requested_sources"], 3)
        self.assertEqual(result["original_csv_name"], "sources.csv")
        gz = self.output / result["files"]["csv_gzip"]["filename"]
        with gzip.open(gz, "rb") as reader:
            self.assertEqual(reader.read(), self.csv.read_bytes())
        self.assertTrue(result["files"]["csv_gzip"]["verification"]["decompressed_readback_passed"])
        zip_path = self.output / result["files"]["source_json_zip"]["filename"]
        with zipfile.ZipFile(zip_path) as archive:
            self.assertEqual(set(archive.namelist()), {
                "source-ids.txt", "manifest.json", "input-provenance.json", "schema.json",
                "cohort.json", "checkpoints/batch-000000.json", "checkpoints/batch-000001.json",
                "acquisition-manifest.json",
                "sources/S1.json", "sources/S2.json",
            })
            for member in result["members"]:
                payload = archive.read(member["path"])
                self.assertEqual(len(payload), member["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), member["sha256"])
        verification = result["files"]["source_json_zip"]["verification"]
        self.assertTrue(verification["crc_readback_passed"])
        self.assertEqual(verification["members"], 10)
        self.assertEqual(verification["uncompressed_bytes"],
                         sum(member["bytes"] for member in result["members"]))
        self.assertFalse(list(self.output.glob("*.partial-*")))

    def test_rejects_unfinished_unverified_or_unresolved_runs(self) -> None:
        for change in ("acquired", "verification", "unresolved"):
            with self.subTest(change=change):
                original = json.loads(json.dumps(self.manifest))
                if change == "acquired":
                    self.manifest["status"] = "acquired"
                elif change == "verification":
                    self.manifest["verification"]["all_rows_read_back"] = False
                else:
                    self.manifest["status_counts"] = {"ok": 1, "redirected": 1, "error": 1}
                self.save_manifest()
                with self.assertRaises(ValueError):
                    self.package()
                self.assertFalse(self.output.exists())
                self.manifest = original

    def test_missing_json_or_changed_csv_never_creates_success_marker(self) -> None:
        (self.run / "sources/S2.json").unlink()
        with self.assertRaises(ValueError):
            self.package()
        (self.run / "sources/S2.json").write_text('{"id":"https://openalex.org/S20"}\n')
        self.csv.write_bytes(self.csv.read_bytes().replace(b"ok", b"no", 1))
        with self.assertRaisesRegex(ValueError, "CSV changed"):
            self.package()
        self.assertFalse((self.output / "delivery-manifest.json").exists())
        self.assertFalse(list(self.output.glob("*.partial-*")))

    def test_reuse_and_restart_after_publish_are_reproducible(self) -> None:
        first = self.package()
        zip_path = self.output / first["files"]["source_json_zip"]["filename"]
        original_mtime = zip_path.stat().st_mtime_ns
        self.assertEqual(self.package(), first)
        self.assertEqual(zip_path.stat().st_mtime_ns, original_mtime)
        (self.output / "delivery-manifest.json").unlink()
        restarted = self.package()
        self.assertEqual(first["files"], restarted["files"])
        self.assertEqual(zip_path.stat().st_mtime_ns, original_mtime)

    def test_existing_different_file_is_not_overwritten(self) -> None:
        self.output.mkdir()
        zip_path = self.output / (self.prefix + "-json.zip")
        zip_path.write_bytes(b"existing different delivery")
        with self.assertRaises(FileExistsError):
            self.package()
        self.assertEqual(zip_path.read_bytes(), b"existing different delivery")
        self.assertFalse((self.output / "delivery-manifest.json").exists())

    def test_reuse_rejects_corrupted_delivery_bytes(self) -> None:
        result = self.package()
        path = self.output / result["files"]["csv_gzip"]["filename"]
        path.write_bytes(path.read_bytes() + b"corrupted")
        with self.assertRaises(FileExistsError):
            self.package()
        self.assertTrue(path.read_bytes().endswith(b"corrupted"))

    def test_zip_readback_checks_member_crc(self) -> None:
        path = self.run / "bad-crc.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("source.json", b'{"x":1}')
            info = archive.getinfo("source.json")
            member = {"path": info.filename, "bytes": info.file_size,
                      "crc32": f"{info.CRC:08x}"}
        payload = bytearray(path.read_bytes())
        start = info.header_offset + 30 + len(info.filename.encode()) + len(info.extra)
        payload[start] ^= 1
        path.write_bytes(payload)
        with self.assertRaises(zipfile.BadZipFile):
            PACKAGER.verify_zip(path, [member])

    def test_changed_json_is_rejected_against_acquisition_receipt(self) -> None:
        path = self.run / "sources/S1.json"
        path.write_bytes(path.read_bytes().replace(b"S1", b"S9"))
        with self.assertRaisesRegex(ValueError, "differs from its verified receipt"):
            self.package()
        self.assertFalse((self.output / "delivery-manifest.json").exists())

    def test_checkpoint_cohort_order_must_match_finalized_ids(self) -> None:
        path = self.run / "checkpoints/batch-000000.json"
        receipt = json.loads(path.read_text())
        receipt["requested_ids"].reverse()
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "Checkpoint rows differ"):
            self.package()
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
