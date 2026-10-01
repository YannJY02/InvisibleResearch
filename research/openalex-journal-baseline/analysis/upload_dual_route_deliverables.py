"""Upload new named artifacts to the already authorized SURFdrive Data share.

No existing remote file is overwritten. An uncertain PUT is followed only by
readback. Conditional ranges read every remote byte and verify the whole SHA256.
Private share tokens are read locally and are never included in receipts.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import http.client
import json
from pathlib import Path
import time
import urllib.parse

import collect_source_metadata as base

CHUNK = 4 * 1024 * 1024
OWNER = Path(__file__).resolve().parents[1]


def upload(file, remote_name, evidence_dir):
    private = OWNER / "artifacts/surfdrive-delivery/destination.private.json"
    destination = urllib.parse.urlsplit(json.loads(private.read_text())["url"])
    if destination.scheme != "https" or destination.hostname != "surfdrive.surf.nl":
        raise ValueError("Destination is not the existing SURFdrive share")
    if Path(remote_name).name != remote_name or not remote_name.startswith("openalex-"):
        raise ValueError("Remote filename must be a new named OpenAlex artifact")
    token = destination.path.rstrip("/").split("/")[-1]
    auth = "Basic " + base64.b64encode((token + ":").encode()).decode()
    path = "/public.php/webdav/" + urllib.parse.quote(remote_name, safe="")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    receipt = evidence_dir / (remote_name + ".upload.json")
    size, digest = file.stat().st_size, base.sha256_file(file)
    evidence = {"filename": remote_name, "local_bytes": size, "local_sha256": digest,
                "started_at": base.now(), "verified": False}
    if receipt.exists():
        previous = json.loads(receipt.read_text())
        if any(previous.get(k) != evidence[k] for k in ("filename", "local_bytes", "local_sha256")):
            raise ValueError("Existing upload receipt belongs to a different local artifact")
        evidence = previous
        evidence["verified"] = False
        evidence["last_resume_at"] = base.now()

    def save():
        base.save_json(receipt, evidence)

    def head(etag=None):
        conn = http.client.HTTPSConnection(destination.hostname, timeout=45)
        headers = {"Authorization": auth, "Accept-Encoding": "identity"}
        if etag:
            headers["If-Match"] = etag
        conn.request("HEAD", path, headers=headers)
        response = conn.getresponse()
        value = {"status": response.status, "bytes": response.getheader("Content-Length"),
                 "etag": response.getheader("ETag")}
        response.read()
        conn.close()
        return value

    initial = head()
    evidence["initial_head"] = initial
    if initial["status"] == 404:
        # A prior uncertain PUT must not be replayed, even if propagation is delayed.
        if evidence.get("put_started_at"):
            raise ValueError("Prior PUT outcome uncertain; remote currently absent; do not resend")
        evidence["put_started_at"] = base.now()
        save()
        try:
            conn = http.client.HTTPSConnection(destination.hostname, timeout=90)
            conn.putrequest("PUT", path)
            for key, value in {"Authorization": auth, "Content-Length": str(size),
                               "Content-Type": "application/octet-stream", "If-None-Match": "*"}.items():
                conn.putheader(key, value)
            conn.endheaders()
            sent, last = 0, time.monotonic()
            with file.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    conn.send(chunk)
                    sent += len(chunk)
                    if time.monotonic() - last > 20:
                        print(f"{remote_name}: uploaded {sent:,}/{size:,} bytes", flush=True)
                        last = time.monotonic()
            response = conn.getresponse()
            evidence["put_status"] = response.status
            response.read()
            conn.close()
        except (OSError, http.client.HTTPException) as error:
            evidence["put_uncertain"] = type(error).__name__
        save()
    elif initial["status"] != 200:
        raise RuntimeError("SURFdrive HEAD status " + str(initial["status"]))
    start = head()
    evidence["readback_start"] = start
    save()
    if start["status"] != 200 or int(start["bytes"]) != size or not start["etag"]:
        raise ValueError("Remote metadata differs; existing remote file will not be overwritten")
    etag = start["etag"]
    cache = evidence_dir / (remote_name + ".readback-chunks") / hashlib.sha256(etag.encode()).hexdigest()[:16]
    cache.mkdir(parents=True, exist_ok=True)
    ranges = []

    def get_range(index):
        lower, upper = index * CHUNK, min(size, (index + 1) * CHUNK) - 1
        target = cache / f"{index:05d}.bin"
        # Check cached bytes against the local byte range before reusing them.
        if target.exists():
            cached = target.read_bytes()
            with file.open("rb") as stream:
                stream.seek(lower)
                expected = stream.read(upper - lower + 1)
            if cached == expected:
                return {"index": index, "bytes": len(cached), "sha256": hashlib.sha256(cached).hexdigest(), "cached": True}
        for attempt in range(4):
            conn = http.client.HTTPSConnection(destination.hostname, timeout=45)
            try:
                conn.request("GET", path, headers={"Authorization": auth, "Accept-Encoding": "identity",
                                                   "If-Match": etag, "Range": f"bytes={lower}-{upper}"})
                response = conn.getresponse()
                if response.status != 206 or response.getheader("ETag") != etag or response.getheader("Content-Range") != f"bytes {lower}-{upper}/{size}":
                    raise ValueError("Conditional remote range response differs")
                data = response.read()
                if len(data) != upper - lower + 1:
                    raise ValueError("Remote range length differs")
                base.atomic_bytes(target, data)
                return {"index": index, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "status": 206, "etag": etag}
            except (OSError, http.client.HTTPException):
                if attempt == 3:
                    raise
                time.sleep(attempt + 1)
            finally:
                conn.close()

    count = (size + CHUNK - 1) // CHUNK
    with ThreadPoolExecutor(max_workers=12) as pool:
        for future in as_completed([pool.submit(get_range, i) for i in range(count)]):
            ranges.append(future.result())
            if len(ranges) % 20 == 0:
                print(f"{remote_name}: read back {len(ranges)}/{count} ranges", flush=True)
    remote_digest, remote_bytes = hashlib.sha256(), 0
    for i in range(count):
        data = (cache / f"{i:05d}.bin").read_bytes()
        remote_digest.update(data)
        remote_bytes += len(data)
    final = head(etag)
    evidence.update({"final_head": final, "remote_bytes": remote_bytes,
                     "remote_sha256": remote_digest.hexdigest(), "ranges": sorted(ranges, key=lambda r: r["index"])})
    if final != start or remote_digest.hexdigest() != digest or remote_bytes != size:
        save()
        raise ValueError("Full remote bytes or stable ETag verification failed")
    evidence.update({"verified": True, "verified_at": base.now()})
    save()
    print(f"REMOTE VERIFIED {remote_name}: {size:,} bytes {digest}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    if "artifacts" not in args.evidence.parts or args.evidence.name == "artifacts":
        parser.error("Use a named artifacts evidence directory")
    upload(args.file, args.name, args.evidence)
