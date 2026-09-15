"""Inventory BigQuery datasets, then compare bounded journal-table fingerprints.

Metadata equality is not content equality. Fingerprints include every selected
row and duplicate occurrence, with deterministic scalar-field serialization.
Queries run separately in each dataset's region; only digests return locally.
No permanent cloud table is created. Existing runs are never overwritten.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.parse
import urllib.request
import uuid


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def fingerprint_sql(project, dataset, metadata, tables):
    """Hash sorted row digests in 256 buckets, preserving multiplicities."""
    selects = []
    for table in tables:
        fields = metadata[table]["schema"]["fields"]
        supported = {"INTEGER", "FLOAT", "BOOLEAN", "STRING", "DATETIME"}
        if any(f["type"] not in supported or f.get("mode") == "REPEATED"
               for f in fields):
            raise ValueError(f"Unsupported serialization schema: {table}")
        columns = ", ".join(f"t.`{f['name']}` AS `{f['name']}`"
                            for f in sorted(fields, key=lambda f: f["name"]))
        selects.append(
            f"SELECT '{table}' AS table_name, "
            f"TO_HEX(SHA256(TO_JSON_STRING(STRUCT({columns})))) AS digest "
            f"FROM `{project}.{dataset}.{table}` AS t")
    names = ", ".join(f"'{table}'" for table in tables)
    return """WITH row_digests AS (
""" + "\nUNION ALL\n".join(selects) + """
), buckets AS (
  SELECT table_name, SUBSTR(digest, 1, 2) AS bucket, COUNT(*) AS n,
    TO_HEX(SHA256(STRING_AGG(digest, '' ORDER BY digest))) AS digest
  FROM row_digests GROUP BY table_name, bucket
), totals AS (
  SELECT table_name, SUM(n) AS row_count,
    TO_HEX(SHA256(STRING_AGG(
      CONCAT(bucket, ':', CAST(n AS STRING), ':', digest), '\\n'
      ORDER BY bucket))) AS fingerprint
  FROM buckets GROUP BY table_name
)
SELECT table_name, COALESCE(row_count, 0) AS row_count,
  COALESCE(fingerprint, TO_HEX(SHA256(''))) AS fingerprint
FROM UNNEST([""" + names + """]) AS table_name
LEFT JOIN totals USING (table_name)
ORDER BY table_name
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["inventory", "fingerprint", "resume"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--datasets", required=True, nargs="+")
    parser.add_argument("--execution-project")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gcloud", default="gcloud")
    parser.add_argument("--maximum-bytes-billed", type=int, default=536870912)
    args = parser.parse_args()
    for value in [args.project, *args.datasets, args.execution_project or "unused"]:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
            parser.error("Invalid resource identifier")
    args.output.mkdir(parents=True, exist_ok=True)
    token = subprocess.run([args.gcloud, "auth", "print-access-token", "--quiet"],
                           check=True, capture_output=True, text=True).stdout.strip()
    base = "https://bigquery.googleapis.com/bigquery/v2/projects/"

    def request(path, body=None):
        req = urllib.request.Request(
            base + path, data=None if body is None else json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + token,
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=45) as response:
            return json.load(response)

    for dataset in args.datasets:
        root = f"{args.project}/datasets/{dataset}"
        metadata_path = args.output / f"{dataset}-metadata.json"
        if args.phase == "inventory":
            if metadata_path.exists():
                raise FileExistsError(metadata_path)
            save(args.output / f"{dataset}.json", request(root))
            tables, page = [], None
            while True:
                params = {"maxResults": 1000}
                if page:
                    params["pageToken"] = page
                listing = request(root + "/tables?" + urllib.parse.urlencode(params))
                tables.extend(t["tableReference"]["tableId"]
                              for t in listing.get("tables", []))
                page = listing.get("nextPageToken")
                if not page:
                    break
            with ThreadPoolExecutor(max_workers=6) as pool:
                values = list(pool.map(lambda t: request(root + "/tables/" + t), tables))
            save(metadata_path, dict(zip(tables, values)))
            print(f"{dataset}: inventoried {len(tables)} tables", flush=True)
            continue

        if not args.execution_project:
            parser.error("fingerprint requires --execution-project")
        run = args.output / f"{dataset}-fingerprint"
        if args.phase != "resume":
            run.mkdir(exist_ok=False)
        before = json.loads(metadata_path.read_text())
        tables = sorted(t for t in before if t == "publishers" or t.startswith("sources"))
        if not tables:
            raise ValueError("No journal tables found")
        if any(before[t].get("streamingBuffer") for t in tables):
            raise ValueError("Streaming table needs a separately defined comparison boundary")
        location = request(root)["location"]
        query = fingerprint_sql(args.project, dataset, before, tables)
        config = {"query": query, "useLegacySql": False, "useQueryCache": False,
                  "maximumBytesBilled": str(args.maximum_bytes_billed)}
        if args.phase == "resume":
            saved = json.loads((run / "request.json").read_text())
            reference = saved["jobReference"]
            if (reference["projectId"] != args.execution_project
                    or reference["location"] != location
                    or saved["configuration"]["query"] != config):
                raise ValueError("Resume inputs differ from saved request")
            job_id = reference["jobId"]
            job = request(f"{args.execution_project}/jobs/{job_id}?location={location}")
        else:
            (run / "query.sql").write_text(query)
            # Persist the ID before submission; resume only reads this same job.
            job_id = "codex_dataset_comparison_" + uuid.uuid4().hex
            reference = {"projectId": args.execution_project, "location": location,
                         "jobId": job_id}
            save(run / "request.json", {"jobReference": reference, "configuration": {"query": config}})
            dry = request(args.execution_project + "/jobs", {
                "jobReference": {"projectId": args.execution_project, "location": location},
                "configuration": {"dryRun": True, "query": config}})
            save(run / "dry-run.json", dry)
            if dry.get("status", {}).get("errorResult"):
                raise RuntimeError(dry["status"]["errorResult"])
            estimate = int(dry["statistics"]["query"]["totalBytesProcessed"])
            if estimate > args.maximum_bytes_billed:
                raise ValueError(f"Dry run exceeds cap: {estimate}")
            print(f"{dataset}: dry-run {estimate:,} bytes; {job_id}", flush=True)
            job = request(args.execution_project + "/jobs", {
                "jobReference": reference, "configuration": {"query": config}})
            save(run / "submitted-job.json", job)
        path = f"{args.execution_project}/jobs/{job_id}?location={location}"
        deadline = time.monotonic() + 600
        while job.get("status", {}).get("state") != "DONE":
            if time.monotonic() > deadline:
                raise TimeoutError(f"Job still running; inspect saved job ID {job_id}")
            time.sleep(2)
            job = request(path)
        save(run / "completed-job.json", job)
        if job["status"].get("errorResult"):
            raise RuntimeError(job["status"]["errorResult"])
        result = request(f"{args.execution_project}/queries/{job_id}?location={location}&maxResults=1000")
        save(run / "result.json", result)
        if not result.get("jobComplete") or result.get("pageToken"):
            raise ValueError("Incomplete fingerprint result")
        names = [f["name"] for f in result["schema"]["fields"]]
        rows = [dict(zip(names, [c["v"] for c in r["f"]])) for r in result.get("rows", [])]
        if {r["table_name"] for r in rows} != set(tables):
            raise ValueError("Missing or extra result table")
        with ThreadPoolExecutor(max_workers=6) as pool:
            after = dict(zip(tables, pool.map(lambda t: request(root + "/tables/" + t), tables)))
        save(run / "metadata-after.json", after)
        for row in rows:
            table = row["table_name"]
            for key in ["schema", "numRows", "numBytes", "lastModifiedTime", "streamingBuffer"]:
                if before[table].get(key) != after[table].get(key):
                    raise ValueError(f"Metadata changed: {table}.{key}")
            if int(row["row_count"]) != int(before[table]["numRows"]):
                raise ValueError(f"Row count mismatch: {table}")
        save(run / "summary.json", {
            "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "job_reference": reference, "tables": rows,
            "bytes_processed": job["statistics"]["query"]["totalBytesProcessed"],
            "bytes_billed": job["statistics"]["query"]["totalBytesBilled"],
            "metadata_stable": True,
            "boundary": "Full selected-row multiset fingerprints; not a collision-free equality proof or a cross-region atomic snapshot."})
        print(f"{dataset}: {len(rows)} full-table fingerprints verified", flush=True)


if __name__ == "__main__":
    main()
