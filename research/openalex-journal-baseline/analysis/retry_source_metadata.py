"""Audit two separated retries of missing Sources, then reconcile historical ISSNs.

Never mutate the original export. HTTP absence is an observation, and an ISSN
candidate is not a confirmed merge. Every request has a durable phase receipt.
"""
import argparse
import collections
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import datetime as dt
from email.utils import parsedate_to_datetime
import math
import hashlib
import json
from pathlib import Path
import re
import time

import requests
import collect_source_metadata as base

HEADERS = {'date', 'content-type', 'content-length', 'cache-control', 'age', 'etag',
           'last-modified', 'via', 'server', 'retry-after', 'x-cache', 'cf-cache-status',
           'x-request-id', 'x-amzn-requestid', 'x-amz-cf-id', 'x-ratelimit-remaining-usd'}
SUCCESS = {'ok', 'redirected'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def selected_headers(headers):
    return {key.lower(): value for key, value in headers.items() if key.lower() in HEADERS}


class AuditClient(base.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate = min(self.rate, 20)
        self.maximum_rate = min(self.maximum_rate, 20)

    def fetch(self, endpoint, key, phase, output):
        receipt = {'key': key, 'phase': phase, 'endpoint': endpoint,
                   'started_at': base.now(), 'attempts': []}
        for attempt in range(self.attempts):
            self.acquire('singleton')
            entry = {'attempt': attempt + 1, 'started_at': base.now()}
            try:
                response = self.session().get(base.API + endpoint, timeout=(10, self.timeout),
                                              headers={'Cache-Control': 'no-cache'})
            except requests.RequestException:
                entry.update(status_code=None, outcome='transport_error', completed_at=base.now())
                delay = 2 ** attempt
            else:
                body = response.content
                entry.update(status_code=response.status_code, completed_at=base.now(),
                             response_bytes=len(body), response_sha256=sha(body),
                             headers=selected_headers(response.headers),
                             redirect_history=[{'status_code': r.status_code,
                                                'location': r.headers.get('Location'),
                                                'headers': selected_headers(r.headers)}
                                               for r in getattr(response, 'history', [])])
                if response.status_code == 404:
                    entry['outcome'] = 'not_found'
                    receipt['attempts'].append(entry)
                    receipt.update(status='not_found', status_code=404, completed_at=base.now())
                    return receipt
                if response.status_code == 200:
                    try:
                        value = base.loads(body)
                        if not isinstance(value, dict):
                            raise ValueError('not an object')
                        resolved = base.source_id(value['id'])
                    except (ValueError, TypeError, KeyError, AttributeError):
                        entry['outcome'] = 'invalid_source_response'
                        delay = 2 ** attempt
                    else:
                        directory = (str(Path('recovered') / phase) if phase.startswith('pass') else
                                     ('issn-candidates' if phase == 'issn' else 'merge-candidates'))
                        name = key.replace(':', '_') + '.json'
                        target = output / directory / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        base.atomic_bytes(target, body)
                        entry['outcome'] = 'ok'
                        receipt['attempts'].append(entry)
                        receipt.update(status='redirected' if phase.startswith('pass') and resolved != key else 'ok',
                                       status_code=200, resolved_id=resolved, completed_at=base.now(),
                                       json_file=str(target.relative_to(output)), json_bytes=len(body),
                                       json_sha256=sha(body))
                        return receipt
                elif response.status_code == 429 or response.status_code >= 500:
                    entry['outcome'] = 'http_' + str(response.status_code)
                    delay = 2 ** attempt
                    try:
                        delay = max(delay, float(response.headers.get('Retry-After', '0')))
                    except ValueError:
                        try:
                            delay = max(delay, (parsedate_to_datetime(response.headers['Retry-After'])
                                                - dt.datetime.now(dt.timezone.utc)).total_seconds())
                        except (TypeError, ValueError, OverflowError, KeyError):
                            pass
                    if not math.isfinite(delay) or delay < 0:
                        delay = 2 ** attempt
                    if response.status_code == 429:
                        self.throttle(response, delay)
                else:
                    entry['outcome'] = 'http_' + str(response.status_code)
                    receipt['attempts'].append(entry)
                    receipt.update(status='error', status_code=response.status_code, completed_at=base.now())
                    return receipt
            receipt['attempts'].append(entry)
            if attempt + 1 < self.attempts:
                time.sleep(delay)
        receipt.update(status='error', status_code=receipt['attempts'][-1]['status_code'],
                       completed_at=base.now())
        return receipt


def valid_issn(value):
    value = str(value).strip().upper()
    if not re.fullmatch(r'\d{4}-\d{3}[\dX]', value):
        return None
    digits = value.replace('-', '')
    if (sum(int(v) * (8 - i) for i, v in enumerate(digits[:7])) +
            (10 if digits[-1] == 'X' else int(digits[-1]))) % 11:
        return None
    return value


def identity_issns(identity):
    raw = [identity.get('issn_l')] + (identity.get('issn') or [])
    return sorted({normalized for item in raw if item and (normalized := valid_issn(item))})


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def validate_output(original, output):
    original, output = original.resolve(), output.resolve()
    if output == original or original in output.parents or output in original.parents:
        raise ValueError('Retry output must be isolated from the original approved run')
    if 'artifacts' not in output.parts or output.name == 'artifacts':
        raise ValueError('Named artifacts output required')


def read_cohort(original, output, baseline):
    path = output / 'cohort.json'
    input_digest = file_sha256(baseline)
    manifest_digest = file_sha256(original / 'manifest.json')
    original_manifest = base.loads((original / 'manifest.json').read_bytes())
    all_requested = []
    original_statuses = collections.Counter()
    records = {}
    for receipt_path in sorted((original / 'checkpoints').glob('batch-*.json')):
        for record in base.loads(receipt_path.read_bytes())['records']:
            all_requested.append(base.source_id(record['requested_id']))
            original_statuses[record['status']] += 1
            if record['status'] == 'not_found':
                if record['requested_id'] in records:
                    raise ValueError('Duplicate original ID')
                records[record['requested_id']] = record
    accepted_ids, accepted_digest = base.read_ids(original / 'source-ids.txt')
    if (len(all_requested) != original_manifest['requested_sources'] or
            len(set(all_requested)) != len(all_requested) or
            all_requested != accepted_ids or
            accepted_digest != original_manifest['cohort_sha256'] or
            dict(original_statuses) != original_manifest['status_counts'] or
            len(records) != original_manifest['status_counts'].get('not_found', 0)):
        raise ValueError('Original accepted checkpoint cohort/count mismatch')
    ids_digest = sha(('\n'.join(records) + '\n').encode())
    if path.exists():
        cached = base.loads(path.read_bytes())
        if (cached.get('original_receipts') != records or
                cached.get('ids_sha256') != ids_digest or
                set(cached.get('identities', {})) != set(records) or
                cached.get('baseline_file') != str(baseline.resolve()) or
                cached.get('original_run') != str(original.resolve()) or
                cached.get('baseline_sha256', input_digest) != input_digest or
                cached.get('original_manifest_sha256', manifest_digest) != manifest_digest):
            raise ValueError('Resume cohort/input provenance mismatch')
        cached.update(baseline_sha256=input_digest, original_manifest_sha256=manifest_digest)
        base.save_json(path, cached)
        return cached
    identities = {}
    csv.field_size_limit(100_000_000)
    with baseline.open(newline='', encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            key = base.source_id(row['id'])
            if key in records:
                identities[key] = {k: row[k] for k in ('id', 'display_name', 'issn_l', 'type',
                                                      'works_count', 'updated_date', 'created_date')}
                identities[key]['issn_l'] = None if row['issn_l'] == '\\N' else row['issn_l']
                identities[key]['issn'] = None if row['issn'] == '\\N' else base.loads(row['issn'])
    if len(identities) != len(records):
        raise ValueError('Missing baseline identities')
    cohort = {'version': 1, 'created_at': base.now(), 'original_run': str(original.resolve()),
              'baseline_file': str(baseline.resolve()), 'count': len(records),
              'ids_sha256': ids_digest, 'baseline_sha256': input_digest,
              'original_manifest_sha256': manifest_digest,
              'original_receipts': records, 'identities': identities}
    base.save_json(output / 'cohort.json', cohort)
    return cohort


def reusable(path, output, key, phase):
    if not path.exists():
        return None
    row = base.loads(path.read_bytes())
    if row['key'] != key or row['phase'] != phase:
        raise ValueError('Checkpoint phase/key mismatch')
    if row['status'] == 'error':
        return None
    if row['status'] in SUCCESS:
        content = (output / row['json_file']).read_bytes()
        if sha(content) != row['json_sha256']:
            raise ValueError('Recovered JSON changed')
    return row


def observed_window(rows):
    started, completed = [], []
    for row in rows:
        started.append(row['started_at'])
        completed.append(row['completed_at'])
        for attempt in row.get('previous_attempts', []) + row['attempts']:
            started.append(attempt['started_at'])
            completed.append(attempt['completed_at'])
    return {'observed_started_at': min(started) if started else None,
            'observed_completed_at': max(completed) if completed else None}


def run_phase(client, keys, phase, output, workers, manifest):
    directory = output / 'checkpoints' / phase
    directory.mkdir(parents=True, exist_ok=True)
    rows = {}
    pending = []
    for key in keys:
        row = reusable(directory / (key + '.json'), output, key, phase)
        if row:
            rows[key] = row
        else:
            pending.append(key)
    def work(key):
        endpoint = '/sources/' + (('issn:' + key) if phase == 'issn' else key)
        row = client.fetch(endpoint, key, phase, output)
        existing = directory / (key + '.json')
        if existing.exists():
            previous = base.loads(existing.read_bytes())
            row['previous_attempts'] = previous.get('previous_attempts', []) + previous['attempts']
        base.save_json(existing, row)
        return key, row
    began = base.now()
    manifest['phase'] = phase
    manifest['phase_total'] = len(keys)
    def progress():
        manifest.update(updated_at=base.now(), phase_completed=len(rows),
                        phase_counts=dict(collections.Counter(r['status'] for r in rows.values())),
                        request_counts=dict(client.requests), throttle_count=client.throttle_count,
                        current_requests_per_second=client.rate, rate_events=client.rate_events)
        base.save_json(output / 'progress.json', manifest)
    progress()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(work, key) for key in pending]
        for future in as_completed(futures):
            key, row = future.result()
            rows[key] = row
            if len(rows) % 250 == 0 or len(rows) == len(keys):
                progress()
                print(json.dumps({'phase': phase, 'complete': len(rows), 'total': len(keys),
                                  'counts': manifest['phase_counts']}), flush=True)
    ordered = [rows[key] for key in keys]
    window = observed_window(ordered)
    phase_info = {'started_at': window['observed_started_at'],
                  'completed_at': window['observed_completed_at'],
                  'invocation_started_at': began, 'invocation_completed_at': base.now(),
                  'total': len(keys), **window,
                  'counts': dict(collections.Counter(r['status'] for r in ordered))}
    base.save_json(output / (phase + '-summary.json'), phase_info)
    return rows


def reconciliation(identity, receipts):
    requested = identity_issns(identity)
    candidates = sorted({receipts[issn]['resolved_id'] for issn in requested
                         if receipts[issn]['status'] in SUCCESS})
    failures = [issn for issn in requested if receipts[issn]['status'] == 'error']
    if not requested:
        status = 'no_valid_historical_issn'
    elif failures:
        status = 'lookup_incomplete'
    elif len(candidates) > 1:
        status = 'multiple_candidates'
    elif candidates:
        status = 'one_candidate_not_confirmed_merge'
    else:
        status = 'historical_issns_not_found'
    return status, candidates


def write_csv(path, columns, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    with path.open(newline='', encoding='utf-8') as stream:
        reread = list(csv.DictReader(stream))
    expected = [{column: '' if row.get(column) is None else str(row.get(column, ''))
                 for column in columns} for row in rows]
    if reread != expected:
        raise ValueError('CSV readback content/order mismatch')
    return {'filename': path.name, 'rows': len(rows), 'columns': len(columns),
            'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes())}


def finalize(output, cohort, first, second, issns):
    retry_rows, maps = [], []
    accepted_path = output / 'version-audit' / 'accepted-success-resolved-ids.txt'
    accepted_profile = output / 'version-audit' / 'accepted-csv-success-profile.json'
    accepted = None
    accepted_digest = None
    if accepted_path.exists() and accepted_profile.exists():
        accepted_digest = file_sha256(accepted_path)
        profile = base.loads(accepted_profile.read_bytes())
        if accepted_digest != profile['resolved_ids_file_sha256']:
            raise ValueError('Accepted successful ID index hash mismatch')
        accepted = set(base.read_ids(accepted_path)[0])
    summary = collections.Counter()
    for key in cohort['original_receipts']:
        one = first[key]
        two = second.get(key)
        final = one if one['status'] in SUCCESS else two
        identity = cohort['identities'][key]
        status = 'recovered' if final['status'] in SUCCESS else ('persistent_404' if
                  one['status'] == 'not_found' and final['status'] == 'not_found' else 'error_or_unconfirmed_404')
        rec_status, candidates = reconciliation(identity, issns) if status == 'persistent_404' else ('not_required', [])
        summary[status] += 1
        if status == 'persistent_404':
            summary[rec_status] += 1
        retry_rows.append({'original_id': key, 'old_display_name': identity['display_name'],
                           'old_issn_l': identity['issn_l'], 'old_issns_json': json.dumps(identity['issn']),
                           'original_fetched_at': cohort['original_receipts'][key]['fetched_at'],
                           'pass1_http_status': one['status_code'], 'pass1_completed_at': one['completed_at'],
                           'pass2_http_status': two['status_code'] if two else '',
                           'pass2_completed_at': two['completed_at'] if two else '',
                           'retry_outcome': status, 'resolved_id': final.get('resolved_id', ''),
                           'issn_outcome': rec_status, 'candidate_ids_json': json.dumps(candidates)})
        for issn in identity_issns(identity) if status == 'persistent_404' else []:
            record = issns[issn]
            if record['status'] in SUCCESS:
                value = base.loads((output / record['json_file']).read_bytes())
                maps.append({'original_id': key, 'lookup_issn': issn, 'candidate_id': record['resolved_id'],
                             'candidate_display_name': value.get('display_name'), 'candidate_type': value.get('type'),
                             'candidate_issn_l': value.get('issn_l'), 'candidate_issns_json': json.dumps(value.get('issn')),
                             'candidate_created_date': value.get('created_date'), 'candidate_updated_date': value.get('updated_date'),
                             'candidate_works_count': value.get('works_count'),
                             'candidate_contains_lookup_issn': issn in identity_issns(value),
                             'candidate_already_in_accepted_success':
                                 record['resolved_id'] in accepted if accepted is not None else None,
                             'identity_outcome': rec_status,
                             'confirmed_merge': False})
    lookup_rows = [{'issn': key, 'status': value['status'], 'http_status': value['status_code'],
                    'candidate_id': value.get('resolved_id', ''), 'fetched_at': value['completed_at'],
                    'json_file': value.get('json_file', ''), 'json_sha256': value.get('json_sha256', '')}
                   for key, value in issns.items()]
    files = [write_csv(output / 'source-retry-status.csv', list(retry_rows[0]), retry_rows)]
    files.append(write_csv(output / 'issn-lookups.csv', ['issn','status','http_status','candidate_id','fetched_at','json_file','json_sha256'], lookup_rows))
    files.append(write_csv(output / 'old-source-candidates.csv', ['original_id','lookup_issn','candidate_id','candidate_display_name','candidate_type','candidate_issn_l','candidate_issns_json','candidate_created_date','candidate_updated_date','candidate_works_count','candidate_contains_lookup_issn','candidate_already_in_accepted_success','identity_outcome','confirmed_merge'], maps))
    verified = 0
    attempt_counts = collections.Counter()
    for directory in (output / 'checkpoints').iterdir():
        phase_receipts = []
        for path in directory.glob('*.json'):
            receipt = base.loads(path.read_bytes())
            phase_receipts.append(receipt)
            reusable(path, output, receipt['key'], directory.name)
            verified += 1
            attempt_counts.update(str(attempt['status_code']) if attempt['status_code'] is not None
                                  else attempt['outcome'] for attempt in
                                  receipt.get('previous_attempts', []) + receipt['attempts'])
        phase_path = output / (directory.name + '-summary.json')
        if phase_path.exists():
            phase_info = base.loads(phase_path.read_bytes())
            phase_info.setdefault('invocation_started_at', phase_info['started_at'])
            phase_info.setdefault('invocation_completed_at', phase_info['completed_at'])
            window = observed_window(phase_receipts)
            phase_info.update(window, started_at=window['observed_started_at'],
                              completed_at=window['observed_completed_at'],
                              final_verified_at=base.now())
            base.save_json(phase_path, phase_info)
    return {'status': 'complete', 'completed_at': base.now(), 'counts': dict(summary),
            'original_not_found_count': len(retry_rows), 'issn_lookup_count': len(issns),
            'issn_lookup_counts': dict(collections.Counter(r['status'] for r in issns.values())),
            'candidate_mapping_rows': len(maps), 'csv_files': files,
            'candidate_issn_membership_mismatch_rows': sum(not row['candidate_contains_lookup_issn'] for row in maps),
            'accepted_success_id_index_sha256': accepted_digest,
            'candidate_unique_ids': len({row['candidate_id'] for row in maps}),
            'candidate_unique_ids_already_in_accepted_success': len({row['candidate_id'] for row in maps if row['candidate_already_in_accepted_success']}),
            'original_ids_with_candidate_already_in_accepted_success': len({row['original_id'] for row in maps if row['candidate_already_in_accepted_success']}),
            'http_attempt_counts_all_phases': dict(attempt_counts),
            'verification': {'passed': True, 'finalizer_code_sha256': file_sha256(Path(__file__)),
                             'all_checkpoint_receipts_read_back': verified,
                             'all_success_json_hashes_verified': True,
                             'original_id_order_and_uniqueness': len({r['original_id'] for r in retry_rows}) == len(retry_rows)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=48)
    parser.add_argument('--requests-per-second', type=float, default=20)
    parser.add_argument('--pass-gap-seconds', type=float, default=60)
    parser.add_argument('--env-file', type=Path, default=Path('.env'))
    args = parser.parse_args()
    output = args.output.resolve()
    validate_output(args.original, output)
    output.mkdir(parents=True, exist_ok=True)
    client = AuditClient(base.api_key(args.env_file), rate=args.requests_per_second, timeout=45)
    budget = client.free_budget(0)
    base.save_json(output / 'budget-before.json', budget)
    cohort = read_cohort(args.original, output, args.baseline)
    manifest = {'status': 'running', 'started_at': base.now(), 'cohort_count': cohort['count'],
                'two_passes': True, 'minimum_pass_gap_seconds': args.pass_gap_seconds,
                'original_export_immutable': True, 'free_budget': budget}
    ids = list(cohort['original_receipts'])
    first = run_phase(client, ids, 'pass1', output, args.workers, manifest)
    remaining = [key for key in ids if first[key]['status'] not in SUCCESS]
    second_dir = output / 'checkpoints' / 'pass2'
    if not second_dir.exists():
        # Full rounds are separated even for a resumed completed first round.
        gap_end = time.monotonic() + args.pass_gap_seconds
        while time.monotonic() < gap_end:
            time.sleep(min(1, gap_end - time.monotonic()))
    second = run_phase(client, remaining, 'pass2', output, args.workers, manifest)
    persistent = [key for key in remaining if first[key]['status'] == 'not_found' and second[key]['status'] == 'not_found']
    unique_issns = sorted({issn for key in persistent for issn in identity_issns(cohort['identities'][key])})
    issns = run_phase(client, unique_issns, 'issn', output, args.workers, manifest)
    merge_path = output / 'official-merge-map.csv'
    merge_rows = []
    if merge_path.exists():
        with merge_path.open(newline='', encoding='utf-8') as stream:
            merge_rows = list(csv.DictReader(stream))
        target_ids = sorted({base.source_id(row['new_id']) for row in merge_rows})
        targets = run_phase(client, target_ids, 'merge', output, args.workers, manifest)
        target_rows = [{'target_id': key, 'status': value['status'],
                        'http_status': value['status_code'], 'candidate_id': value.get('resolved_id', ''),
                        'fetched_at': value['completed_at'], 'json_file': value.get('json_file', ''),
                        'json_sha256': value.get('json_sha256', '')} for key, value in targets.items()]
        write_csv(output / 'official-merge-targets.csv', ['target_id','status','http_status','candidate_id','fetched_at','json_file','json_sha256'], target_rows)
    result = finalize(output, cohort, first, second, issns)
    result['official_merge_mapping_rows'] = len(merge_rows)
    result['budget_after'] = client.free_budget(0)
    base.save_json(output / 'budget-after.json', result['budget_after'])
    result['request_counts'] = dict(client.requests)
    result['throttle_count'] = client.throttle_count
    result['rate_events'] = client.rate_events
    base.save_json(output / 'summary.json', result)
    manifest.update(result)
    base.save_json(output / 'progress.json', manifest)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
