"""Plan first, then run a small stratified historical-ISSN lookup comparison."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from pathlib import Path
import random
import sys

import collect_source_metadata as base
import retry_source_metadata as audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--prior-retry', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if 'artifacts' not in args.output.parts or args.output.name == 'artifacts':
        parser.error('Use a named artifacts directory')
    if args.output.exists() and not args.execute:
        parser.error('Choose a new plan directory')
    args.output.mkdir(parents=True, exist_ok=True)
    plan_path = args.output / 'plan.json'
    if not args.execute:
        prior = base.loads((args.prior_retry / 'cohort.json').read_bytes())
        digest = audit.file_sha256(args.baseline)
        if digest != prior['baseline_sha256']:
            raise ValueError('Baseline differs from the verified retry cohort')
        missing = set(prior['identities'])
        samples = {name: [] for name in ('id_ok_valid_issn', 'id_404_valid_issn', 'no_valid_issn')}
        sizes = Counter()
        rng = random.Random(20261001)
        csv.field_size_limit(sys.maxsize)
        with args.baseline.open(newline='', encoding='utf-8') as stream:
            for row in csv.DictReader(stream):
                key = base.source_id(row['id'])
                identity = {'issn_l': None if row['issn_l'] == '\\N' else row['issn_l'],
                            'issn': None if row['issn'] == '\\N' else json.loads(row['issn'])}
                numbers = audit.identity_issns(identity)
                group = ('no_valid_issn' if not numbers else
                         'id_404_valid_issn' if key in missing else 'id_ok_valid_issn')
                sizes[group] += 1
                sample = {'old_id': key, 'title': row['display_name'], 'issns': numbers,
                          'original_id_status': 'not_found' if key in missing else 'ok', 'stratum': group}
                if len(samples[group]) < 100:
                    samples[group].append(sample)
                else:
                    index = rng.randrange(sizes[group])
                    if index < 100:
                        samples[group][index] = sample
        selected = [row for group in samples.values() for row in group]
        numbers = sorted({number for row in selected for number in row['issns']})
        cached = [number for number in numbers if audit.reusable(
            args.prior_retry / 'checkpoints' / 'issn' / (number + '.json'),
            args.prior_retry, number, 'issn')]
        plan = {'created_at': base.now(), 'seed': 20261001, 'population_counts': dict(sizes),
                'baseline_sha256': digest, 'baseline': str(args.baseline.resolve()),
                'prior_retry': str(args.prior_retry.resolve()), 'sample': selected,
                'unique_sample_issns': len(numbers), 'verified_cached_issns': len(cached),
                'new_singleton_lookups': len(numbers) - len(cached),
                'maximum_lookup_attempts': 3 * (len(numbers) - len(cached)),
                'estimated_singleton_api_usd': 0,
                'scope': '100 rows per stratum; disproportional sample, not a full-cohort match estimate'}
        base.save_json(plan_path, plan)
        print(json.dumps({k: v for k, v in plan.items() if k != 'sample'}))
        return
    if not plan_path.exists():
        parser.error('Create the offline plan before executing')
    plan = base.loads(plan_path.read_bytes())
    if (str(args.baseline.resolve()) != plan['baseline'] or
            str(args.prior_retry.resolve()) != plan['prior_retry'] or
            audit.file_sha256(args.baseline) != plan['baseline_sha256']):
        raise ValueError('Execution input differs from the costed plan')
    client = audit.AuditClient(base.api_key(Path('.env')), rate=10, attempts=3, timeout=30)
    base.save_json(args.output / 'budget-before.json', client.free_budget(0))
    numbers = sorted({number for row in plan['sample'] for number in row['issns']})
    directory = args.output / 'checkpoints' / 'issn'
    directory.mkdir(parents=True, exist_ok=True)

    def lookup(number):
        fresh = audit.reusable(directory / (number + '.json'), args.output, number, 'issn')
        if fresh:
            return number, fresh, args.output, 'this_probe'
        cached = audit.reusable(args.prior_retry / 'checkpoints' / 'issn' / (number + '.json'),
                                args.prior_retry, number, 'issn')
        if cached:
            return number, cached, args.prior_retry, 'prior_verified_retry'
        receipt = client.fetch('/sources/issn:' + number, number, 'issn', args.output)
        base.save_json(directory / (number + '.json'), receipt)
        return number, receipt, args.output, 'this_probe'

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lookup, numbers))
    evidence = {}
    for number, receipt, root, origin in results:
        entry = {'status': receipt['status'], 'origin': origin,
                 'receipt': str(root / 'checkpoints' / 'issn' / (number + '.json')),
                 'resolved_id': receipt.get('resolved_id')}
        if receipt['status'] in audit.SUCCESS:
            obj = base.loads((root / receipt['json_file']).read_bytes())
            entry.update(source_type=obj['type'], issn_in_returned_set=number in audit.identity_issns(obj))
            if not entry['issn_in_returned_set']:
                raise ValueError('ISSN lookup returned an object without the queried identifier')
        evidence[number] = entry
    rows, counts = [], {}
    for selected in plan['sample']:
        hits = [evidence[number] for number in selected['issns']]
        ids = sorted({hit['resolved_id'] for hit in hits if hit['status'] in audit.SUCCESS})
        if not selected['issns']:
            outcome = 'no_valid_issn'
        elif any(hit['status'] == 'error' for hit in hits):
            outcome = 'request_error'
        elif not ids:
            outcome = 'unmatched'
        elif len(ids) > 1:
            outcome = 'ambiguous'
        elif ids[0] == selected['old_id']:
            outcome = 'same_id'
        else:
            outcome = 'different_id_candidate'
        rows.append({**selected, 'outcome': outcome, 'candidate_ids': ids})
        counts.setdefault(selected['stratum'], Counter())[outcome] += 1
    summary = {'completed_at': base.now(), 'status': 'bounded_probe_completed',
               'population_counts': plan['population_counts'],
               'stratum_outcomes': {k: dict(v) for k, v in counts.items()},
               'lookup_status_counts': dict(Counter(v['status'] for v in evidence.values())),
               'lookup_origin_counts': dict(Counter(v['origin'] for v in evidence.values())),
               'actual_request_counts': dict(client.requests),
               'budget_after': client.free_budget(0),
               'sample_rows': rows, 'lookups': evidence,
               'interpretation': 'ISSN candidates do not certify historical mergers; no rows were overwritten'}
    base.save_json(args.output / 'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('sample_rows', 'lookups')}))


if __name__ == '__main__':
    main()
