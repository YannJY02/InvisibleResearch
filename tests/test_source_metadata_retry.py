"""Missing-source audits distinguish HTTP observations from identity evidence."""
import importlib.util
from pathlib import Path
import sys

import pytest
import requests

DIRECTORY = Path(__file__).parents[1] / 'research' / 'openalex-journal-baseline' / 'analysis'
sys.path.insert(0, str(DIRECTORY))
SPEC = importlib.util.spec_from_file_location('source_retry', DIRECTORY / 'retry_source_metadata.py')
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class Response:
    def __init__(self, status=200, value=None):
        self.status_code = status
        self.content = b'<html>Not found</html>' if status == 404 else PIPELINE.base.dumps(value)
        self.headers = {'Date': 'Thu, 01 Oct 2026 00:00:00 GMT', 'Server': 'test'}
        self.history = []


class Session:
    def __init__(self, responses):
        self.headers = {}
        self.responses = iter(responses)
    def get(self, *args, **kwargs):
        assert kwargs['headers']['Cache-Control'] == 'no-cache'
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def client(responses):
    session = Session(responses)
    value = PIPELINE.AuditClient('test-not-real-secret', session_factory=lambda: session)
    value.acquire = lambda kind: None
    return value


def test_time_separated_404_then_200_is_recovered_without_mutating_first_receipt(tmp_path):
    first = PIPELINE.run_phase(client([Response(404)]), ['S1'], 'pass1', tmp_path, 1, {})
    second = PIPELINE.run_phase(client([Response(value={'id':'https://openalex.org/S1','topics':[]})]),
                                ['S1'], 'pass2', tmp_path, 1, {})
    assert first['S1']['status'] == 'not_found'
    assert second['S1']['status'] == 'ok'
    saved = PIPELINE.base.loads((tmp_path/'checkpoints/pass1/S1.json').read_bytes())
    assert saved['status_code'] == 404
    assert saved['attempts'][0]['response_sha256'] == PIPELINE.sha(b'<html>Not found</html>')
    assert 'test-not-real-secret' not in str(saved)


def test_transport_timeout_does_not_become_404(tmp_path, monkeypatch):
    monkeypatch.setattr(PIPELINE.time, 'sleep', lambda seconds: None)
    value = client([requests.Timeout()] * 4).fetch('/sources/S1', 'S1', 'pass1', tmp_path)
    assert value['status'] == 'error'
    assert value['status_code'] is None
    assert len(value['attempts']) == 4
    assert all(x['outcome'] == 'transport_error' for x in value['attempts'])


def test_timeout_then_actual_404_records_both_observations(tmp_path, monkeypatch):
    monkeypatch.setattr(PIPELINE.time, 'sleep', lambda seconds: None)
    value = client([requests.Timeout(), Response(404)]).fetch('/sources/S1','S1','pass1',tmp_path)
    assert value['status'] == 'not_found'
    assert [r['status_code'] for r in value['attempts']] == [None, 404]


def test_conflicting_issn_candidates_are_not_arbitrarily_merged():
    identity = {'issn_l':'1059-941X', 'issn':['1059-941X','1532-849X']}
    receipts = {'1059-941X':{'status':'ok','resolved_id':'S1'},
                '1532-849X':{'status':'ok','resolved_id':'S2'}}
    status, candidates = PIPELINE.reconciliation(identity,receipts)
    assert status == 'multiple_candidates'
    assert candidates == ['S1','S2']
    receipts['1532-849X'] = {'status':'error'}
    assert PIPELINE.reconciliation(identity,receipts)[0] == 'lookup_incomplete'


def test_issn_checksum_and_one_candidate_are_only_candidates():
    assert PIPELINE.valid_issn('1059-941x') == '1059-941X'
    assert PIPELINE.valid_issn('1059-9411') is None
    status, candidates = PIPELINE.reconciliation({'issn_l':'1059-941X','issn':[]},
                                                {'1059-941X':{'status':'ok','resolved_id':'S99'}})
    assert status == 'one_candidate_not_confirmed_merge'
    assert candidates == ['S99']


def test_checkpoint_rounds_cannot_be_interchanged(tmp_path):
    rows = PIPELINE.run_phase(client([Response(404)]), ['S1'], 'pass1', tmp_path, 1,{})
    path = tmp_path/'checkpoints/pass1/S1.json'
    with pytest.raises(ValueError, match='phase/key mismatch'):
        PIPELINE.reusable(path,tmp_path,'S1','pass2')
    assert PIPELINE.reusable(path,tmp_path,'S1','pass1') == rows['S1']


def test_recovered_json_is_hash_checked_on_resume(tmp_path):
    rows = PIPELINE.run_phase(client([Response(value={'id':'https://openalex.org/S99'})]),
                              ['S1'],'pass1',tmp_path,1,{})
    assert rows['S1']['status'] == 'redirected'
    (tmp_path/rows['S1']['json_file']).write_bytes(b'corrupted')
    with pytest.raises(ValueError,match='JSON changed'):
        PIPELINE.reusable(tmp_path/'checkpoints/pass1/S1.json',tmp_path,'S1','pass1')


def test_global_rate_cannot_automatically_ramp_above_verified_safe_limit():
    value = PIPELINE.AuditClient('test-not-real-secret', rate=35)
    assert value.rate == 20
    assert value.maximum_rate == 20

def test_output_csv_full_readback_preserves_rows_and_nulls(tmp_path):
    rows = [{'id':'S1','value':None},{'id':'S2','value':'[]'}]
    result = PIPELINE.write_csv(tmp_path/'test.csv',['id','value'],rows)
    assert result['rows'] == 2
    assert result['sha256'] == PIPELINE.sha((tmp_path/'test.csv').read_bytes())


def test_output_cannot_be_original_or_inside_it(tmp_path):
    original = tmp_path/'artifacts'/'approved'
    for output in (original, original/'retry', original/'retry'/'nested'):
        with pytest.raises(ValueError,match='isolated'):
            PIPELINE.validate_output(original,output)
    PIPELINE.validate_output(original,tmp_path/'artifacts'/'retry')

def test_cached_error_is_reissued_and_previous_attempts_preserved(tmp_path,monkeypatch):
    monkeypatch.setattr(PIPELINE.time,'sleep',lambda seconds: None)
    first = PIPELINE.run_phase(client([requests.Timeout()]*4),['S1'],'pass1',tmp_path,1,{})
    assert first['S1']['status'] == 'error'
    second = PIPELINE.run_phase(client([Response(404)]),['S1'],'pass1',tmp_path,1,{})
    assert second['S1']['status'] == 'not_found'
    assert len(second['S1']['previous_attempts']) == 4

def test_resume_rejects_changed_baseline_or_requested_ids(tmp_path):
    original = tmp_path/'artifacts'/'approved'
    (original/'checkpoints').mkdir(parents=True)
    PIPELINE.base.save_json(original/'manifest.json',{'status':'complete','requested_sources':1,
                            'status_counts':{'not_found':1},'cohort_sha256':PIPELINE.sha(b'S1\n')})
    (original/'source-ids.txt').write_text('S1\n')
    PIPELINE.base.save_json(original/'checkpoints/batch-000000.json',
                           {'records':[{'requested_id':'S1','status':'not_found','fetched_at':'t0'}]})
    output = tmp_path/'artifacts'/'retry'
    output.mkdir()
    baseline = tmp_path/'baseline.csv'
    baseline.write_text('id,display_name,issn_l,type,works_count,updated_date,created_date,issn\n1,Journal,1059-941X,journal,10,t1,t2,[]\n')
    PIPELINE.read_cohort(original,output,baseline)
    baseline.write_text(baseline.read_text().replace('Journal','Changed'))
    with pytest.raises(ValueError,match='provenance mismatch'):
        PIPELINE.read_cohort(original,output,baseline)

def test_retry_after_http_date_is_honored(tmp_path,monkeypatch):
    from email.utils import format_datetime
    from datetime import datetime,timezone,timedelta
    delays = []
    monkeypatch.setattr(PIPELINE.time,'sleep',delays.append)
    response = Response(status=503)
    response.headers['Retry-After'] = format_datetime(datetime.now(timezone.utc)+timedelta(seconds=30))
    value = client([response,Response(404)]).fetch('/sources/S1','S1','pass1',tmp_path)
    assert value['status'] == 'not_found'
    assert 28 < delays[0] <= 30


def test_finalization_keeps_original_rows_and_flags_existing_candidate(tmp_path):
    original = {'S1':{'fetched_at':'old1'},'S2':{'fetched_at':'old2'}}
    identity = {'display_name':'Historical journal','issn_l':'1059-941X','issn':[]}
    cohort = {'original_receipts':original,'identities':{'S1':identity,'S2':identity}}
    first = PIPELINE.run_phase(client([Response(404),Response(value={'id':'https://openalex.org/S2'})]),
                               ['S1','S2'],'pass1',tmp_path,1,{})
    second = PIPELINE.run_phase(client([Response(404)]),['S1'],'pass2',tmp_path,1,{})
    issns = PIPELINE.run_phase(client([Response(value={'id':'https://openalex.org/S99',
                                'display_name':'Current journal','issn_l':'1059-941X','issn':[]})]),
                                ['1059-941X'],'issn',tmp_path,1,{})
    directory = tmp_path/'version-audit'
    directory.mkdir()
    (directory/'accepted-success-resolved-ids.txt').write_text('S99\n')
    PIPELINE.base.save_json(directory/'accepted-csv-success-profile.json',
                            {'resolved_ids_file_sha256':PIPELINE.sha(b'S99\n')})
    summary = PIPELINE.finalize(tmp_path,cohort,first,second,issns)
    assert summary['counts']['persistent_404'] == 1
    assert summary['counts']['recovered'] == 1
    assert summary['candidate_unique_ids_already_in_accepted_success'] == 1
    assert summary['original_ids_with_candidate_already_in_accepted_success'] == 1
    assert summary['http_attempt_counts_all_phases'] == {'404':2,'200':2}
    assert summary['verification']['passed'] is True
    text = (tmp_path/'old-source-candidates.csv').read_text()
    assert 'confirmed_merge' in text
    assert text.rstrip().endswith('False')


def test_resume_success_in_first_round_cannot_overwrite_second_round_evidence(tmp_path,monkeypatch):
    monkeypatch.setattr(PIPELINE.time,'sleep',lambda seconds: None)
    PIPELINE.run_phase(client([requests.Timeout()]*4),['S1'],'pass1',tmp_path,1,{})
    second = PIPELINE.run_phase(client([Response(value={'id':'https://openalex.org/S1','name':'second'})]),
                                ['S1'],'pass2',tmp_path,1,{})
    second_bytes = (tmp_path/second['S1']['json_file']).read_bytes()
    first = PIPELINE.run_phase(client([Response(value={'id':'https://openalex.org/S1','name':'first resumed'})]),
                               ['S1'],'pass1',tmp_path,1,{})
    assert first['S1']['json_file'] == 'recovered/pass1/S1.json'
    assert second['S1']['json_file'] == 'recovered/pass2/S1.json'
    assert (tmp_path/second['S1']['json_file']).read_bytes() == second_bytes
    assert PIPELINE.reusable(tmp_path/'checkpoints/pass2/S1.json',tmp_path,'S1','pass2') == second['S1']


def test_missing_original_checkpoint_cannot_shrink_accepted_cohort(tmp_path):
    original = tmp_path/'artifacts'/'approved'
    (original/'checkpoints').mkdir(parents=True)
    PIPELINE.base.save_json(original/'manifest.json',{'status':'complete','requested_sources':2,
                            'status_counts':{'not_found':2},'cohort_sha256':PIPELINE.sha(b'S1\nS2\n')})
    (original/'source-ids.txt').write_text('S1\nS2\n')
    PIPELINE.base.save_json(original/'checkpoints/batch-000000.json',
                           {'records':[{'requested_id':'S1','status':'not_found','fetched_at':'t0'}]})
    output = tmp_path/'artifacts'/'retry'
    output.mkdir()
    baseline = tmp_path/'baseline.csv'
    baseline.write_text('id,display_name,issn_l,type,works_count,updated_date,created_date,issn\n1,Journal,1059-941X,journal,10,t1,t2,[]\n')
    with pytest.raises(ValueError,match='accepted checkpoint cohort/count mismatch'):
        PIPELINE.read_cohort(original,output,baseline)


def test_phase_request_window_includes_prior_resumed_attempts():
    rows = [{'started_at':'2026-10-01T03:34:00+00:00',
             'completed_at':'2026-10-01T03:34:01+00:00',
             'previous_attempts':[{'started_at':'2026-10-01T03:31:00+00:00',
                                   'completed_at':'2026-10-01T03:31:02+00:00'}],
             'attempts':[{'started_at':'2026-10-01T03:34:00+00:00',
                          'completed_at':'2026-10-01T03:34:01+00:00'}]}]
    assert PIPELINE.observed_window(rows) == {
        'observed_started_at':'2026-10-01T03:31:00+00:00',
        'observed_completed_at':'2026-10-01T03:34:01+00:00'}
