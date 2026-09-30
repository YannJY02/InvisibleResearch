"""Full Source acquisition/CSV contracts using local mock responses only."""

import csv
import importlib.util
from pathlib import Path

import pytest


SCRIPT = (Path(__file__).parents[1] / "research" / "openalex-journal-baseline"
          / "analysis" / "collect_source_metadata.py")
SPEC = importlib.util.spec_from_file_location("source_metadata_pipeline", SCRIPT)
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class Response:
    def __init__(self, value=None, status=200, headers=None):
        self.status_code = status
        self.content = b"<html>not found</html>" if status == 404 else PIPELINE.dumps(value)
        self.headers = headers or {}


class Session:
    def __init__(self, route):
        self.headers = {}
        self.route = route
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        return self.route(url, params)


def client_for(route):
    session = Session(route)
    client = PIPELINE.Client("secret-for-test", rate=95, session_factory=lambda: session)
    return client, session


def output_for(tmp_path, ids, batch_size=100):
    digest = PIPELINE.hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()
    return PIPELINE.prepare_output(tmp_path / "artifacts" / "source-test", ids, digest, batch_size)


def source(number, **attributes):
    return {"id": f"https://openalex.org/S{number}", **attributes}


def test_batch_matches_shuffled_ids_and_singleton_fallback_preserves_redirects(tmp_path):
    ids = ["S1", "S2", "S3", "S4"]
    output = output_for(tmp_path, ids)

    def route(url, params):
        if url.endswith("/sources"):
            assert params == {"filter": "ids.openalex:S1|S2|S3|S4", "per_page": 100}
            return Response({"results": [source(4), source(99), source(1)]})
        if url.endswith("/sources/S2"):
            return Response(source(99, display_name="Merged journal"))
        if url.endswith("/sources/S3"):
            return Response(status=404)
        raise AssertionError("Unexpected mock request")

    client, session = client_for(route)
    receipt = PIPELINE.collect_batch(client, output, 0, ids)
    assert [row["status"] for row in receipt["records"]] == ["ok", "redirected", "not_found", "ok"]
    assert receipt["records"][1]["resolved_id"] == "https://openalex.org/S99"
    assert PIPELINE.loads((output / "sources" / "S2.json").read_bytes())["id"].endswith("S99")
    assert not (output / "sources" / "S99.json").exists()
    assert len(session.calls) == 3  # HTML 404 is not JSON-decoded or retried.
    assert PIPELINE.receipt_complete(output, receipt)
    assert "secret-for-test" not in (output / "checkpoints" / "batch-000000.json").read_text()


def test_csv_roundtrip_preserves_arrays_types_and_absent_attributes(tmp_path):
    ids = ["S1", "S2", "S3"]
    output = output_for(tmp_path, ids)
    values = [source(2, summary_stats={"h_index": 0}, topics=[],
                     issn_l="0", display_name="", mixed="[]"),
              source(1, summary_stats={"h_index": 8, "extra": None}, topics=[
                  {"id": "T1", "count": 0, "nested": {"empty": [], "null": None}},
                  {"id": "T2", "count": 1}], issn_l=None, mixed="\\N", enabled=False,
                     empty_object={}, **{"key.with.dot": {"x\\y": "null"}})]

    def route(url, params):
        return Response({"results": values}) if url.endswith("/sources") else Response(status=404)

    client, _ = client_for(route)
    PIPELINE.collect_batch(client, output, 0, ids)
    records, fields = PIPELINE.read_receipts(output, ids, 100)
    result = PIPELINE.convert_csv(output, ids, records, fields)
    assert result["csv"]["rows"] == len(ids)
    assert result["verification"]["passed"] is True
    assert result["verification"]["all_source_fields_roundtrip_equal"] is True
    assert result["field_states"]["summary_stats.h_index"] == {"present": 2, "absent": 1}
    with (output / "sources.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 3
    assert rows[0]["issn_l"] == "\\N"
    assert rows[1]["issn_l"] == '\\S"0"'
    assert rows[1]["display_name"] == ""
    assert rows[1]["enabled"] == "\\M"
    assert rows[1]["topics"] == "[]"
    assert rows[2]["fetch_status"] == "not_found"
    assert rows[2]["topics"] == "\\M"
    for value in (None, 0, False, [], {}, "", "\\N", "\\M", "\\Sfoo", "false", "[]", '"text"'):
        decoded = PIPELINE.decode_cell(PIPELINE.encode_cell(value))
        assert decoded == value
        assert type(decoded) is type(value)


def test_csv_roundtrip_stdlib_without_orjson(tmp_path, monkeypatch):
    monkeypatch.setattr(PIPELINE, "orjson", None)
    ids = ["S1"]
    output = output_for(tmp_path, ids)
    client, _ = client_for(lambda url, params: Response({"results": [
        source(1, display_name="中文期刊", summary_stats={"score": 0.25}, topics=[])]}))
    PIPELINE.collect_batch(client, output, 0, ids)
    records, fields = PIPELINE.read_receipts(output, ids, 100)
    result = PIPELINE.convert_csv(output, ids, records, fields)
    assert result["verification"]["passed"]
    assert "中文期刊" in (output / "sources.csv").read_text()


def test_resume_contract_and_damaged_size_refetch_only_affected_source(tmp_path):
    ids = ["S1", "S2"]
    output = output_for(tmp_path, ids)
    client, _ = client_for(lambda url, params: Response({"results": [source(1), source(2)]}))
    receipt = PIPELINE.collect_batch(client, output, 0, ids)
    (output / "sources" / "S1.json").write_text("{}")
    assert not PIPELINE.receipt_complete(output, receipt)

    def route(url, params):
        assert params["filter"] == "ids.openalex:S1"
        return Response({"results": [source(1)]})

    resumed, session = client_for(route)
    refreshed = PIPELINE.collect_batch(resumed, output, 0, ids)
    assert PIPELINE.receipt_complete(output, refreshed)
    assert len(session.calls) == 1
    assert refreshed["records"][1] == receipt["records"][1]
    with pytest.raises(ValueError, match="different cohort"):
        PIPELINE.prepare_output(output, ["S3"], "changed-digest", 100)


def test_same_size_corruption_is_rejected_before_csv_is_published(tmp_path):
    ids = ["S1"]
    output = output_for(tmp_path, ids)
    client, _ = client_for(lambda url, params: Response({"results": [source(1)]}))
    PIPELINE.collect_batch(client, output, 0, ids)
    path = output / "sources" / "S1.json"
    path.write_bytes(path.read_bytes().replace(b"S1", b"S9"))
    records, fields = PIPELINE.read_receipts(output, ids, 100)
    with pytest.raises(ValueError, match="S1 does not match its receipt checksum"):
        PIPELINE.convert_csv(output, ids, records, fields)
    assert not (output / "sources.csv").exists()


def test_damaged_prior_json_followed_by_confirmed_404_removes_only_that_source(tmp_path):
    ids = ["S1"]
    output = output_for(tmp_path, ids)
    input_path = tmp_path / "ids.txt"
    input_path.write_text("S1\n")
    initial, _ = client_for(lambda url, params: Response({"results": [source(1)]}))
    receipt = PIPELINE.collect_batch(initial, output, 0, ids)
    path = output / "sources" / "S1.json"
    path.write_text("{}")
    unrelated = output / "unchanged.json"
    unrelated.write_text('{"retain":true}')
    assert not PIPELINE.receipt_complete(output, receipt)

    def route(url, params):
        return Response({"results": []}) if url.endswith("/sources") else Response(status=404)

    resumed, _ = client_for(route)
    refreshed = PIPELINE.collect_batch(resumed, output, 0, ids)
    assert refreshed["records"][0]["status"] == "not_found"
    assert PIPELINE.receipt_complete(output, refreshed)
    assert not path.exists()
    assert unrelated.read_text() == '{"retain":true}'
    assert PIPELINE.main(["--ids", str(input_path), "--output", str(output), "--convert-only"]) == 0
    final = PIPELINE.loads((output / "manifest.json").read_bytes())
    assert final["status"] == "complete"
    assert final["status_counts"] == {"not_found": 1}
    assert final["source_json_files"] == 0
    assert len(list((output / "sources").glob("*.json"))) == 0
    with (output / "sources.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["source_id"] == "https://openalex.org/S1"
    assert rows[0]["fetch_status"] == "not_found"


def test_input_normalization_and_duplicates_do_not_silently_drop_rows(tmp_path):
    path = tmp_path / "ids.txt"
    path.write_text("123\nS456\nhttps://openalex.org/S789\n")
    ids, _ = PIPELINE.read_ids(path)
    assert ids == ["S123", "S456", "S789"]
    path.write_text("S1\nhttps://openalex.org/S1\n")
    with pytest.raises(ValueError, match="Duplicate"):
        PIPELINE.read_ids(path)
    for invalid in ("https://example.org/S1", "S0", "S1?api_key=x", "S1|S2", "S1/extra"):
        with pytest.raises(ValueError, match="Invalid"):
            PIPELINE.source_id(invalid)


def test_failed_requests_stay_distinct_from_not_found_in_complete_csv(tmp_path):
    ids = ["S1", "S2"]
    output = output_for(tmp_path, ids)
    client, _ = client_for(lambda url, params: Response(status=401))
    receipt = PIPELINE.collect_batch(client, output, 0, ids)
    assert [row["status"] for row in receipt["records"]] == ["error:http_401"] * 2
    assert not PIPELINE.receipt_complete(output, receipt)
    records, fields = PIPELINE.read_receipts(output, ids, 100)
    result = PIPELINE.convert_csv(output, ids, records, fields)
    assert result["csv"]["rows"] == 2
    with (output / "sources.csv").open(newline="") as stream:
        assert all(row["fetch_status"] == "error:http_401" for row in csv.DictReader(stream))


def test_budget_uses_free_balance_and_never_persists_api_key():
    value = {"api_key": "secret-for-test", "rate_limit": {
        "daily_budget_usd": 1, "daily_used_usd": 0.1, "daily_remaining_usd": 0.9,
        "prepaid_balance_usd": 200, "endpoint_costs_usd": {"singleton": 0, "list": 0.0001}}}
    client, _ = client_for(lambda url, params: Response(value))
    safe = client.free_budget(2000)
    assert safe["maximum_list_requests_this_run"] == 8100
    assert safe["reserved_list_attempts_this_run"] == 8000
    assert "secret-for-test" not in str(safe)
    with pytest.raises(PIPELINE.FetchError, match="insufficient_free_budget"):
        client.free_budget(2100)


def test_429_pauses_all_workers_and_rate_changes_once_per_burst(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(PIPELINE.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(PIPELINE.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds))
    client, _ = client_for(lambda url, params: Response({}))
    response = Response(status=429, headers={"Retry-After": "2", "X-RateLimit-Remaining-USD": "0.8"})
    client.throttle(response, 2)
    assert client.rate == 25
    client.throttle(response, 2)
    assert client.rate == 25
    client.acquire("list")
    assert clock[0] >= 1002
    assert client.requests["list"] == 1
    assert client.rate_events[-1]["daily_remaining_usd"] == "0.8"
    assert client.throttle_count == 2


def test_convert_only_preserves_acquisition_manifest_and_timing(tmp_path):
    ids = ["S1"]
    output = output_for(tmp_path, ids)
    input_path = tmp_path / "ids.txt"
    input_path.write_text("S1\n")
    client, _ = client_for(lambda url, params: Response({"results": [source(1)]}))
    PIPELINE.collect_batch(client, output, 0, ids)
    previous = {"status": "acquired", "started_at": "2026-09-30T01:00:00+00:00",
                "timing_seconds": {"collection_this_run": 321.0},
                "free_budget": {"free_only": True}, "request_counts_this_run": {"list": 1}}
    PIPELINE.save_json(output / "manifest.json", previous)
    assert PIPELINE.main(["--ids", str(input_path), "--output", str(output), "--convert-only"]) == 0
    final = PIPELINE.loads((output / "manifest.json").read_bytes())
    assert final["status"] == "complete"
    assert final["started_at"] == previous["started_at"]
    assert final["timing_seconds"]["collection_this_run"] == 321.0
    assert final["free_budget"] == previous["free_budget"]
    assert PIPELINE.loads((output / "acquisition-manifest.json").read_bytes()) == previous
