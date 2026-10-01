"""Collect an independent live journal universe and all-Works language aggregates.

All raw API responses are compressed and checkpointed. The free-budget guard
never purchases credits. Language uses primary_location.source, all years and
all work types (corpus=all). Case variants exposed by group_by are folded because
OpenAlex's language filter folds them; original group keys remain in the index.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

from collect_source_metadata import Client, api_key, atomic_bytes, dumps, loads, now, save_json


class Collector:
    def __init__(self, output, client):
        self.output, self.client = output, client

    def pages(self, name, endpoint, params, rows_key):
        directory = self.output / 'raw' / name
        directory.mkdir(parents=True, exist_ok=True)
        cursor, index, seen_cursors = '*', 1, {'*'}
        while True:
            file = directory / f'page-{index:06d}.json.gz'
            request = dict(params, cursor=cursor, per_page=200)
            if file.exists():
                envelope = loads(gzip.decompress(file.read_bytes()))
                if envelope['params'] != request or envelope['endpoint'] != endpoint:
                    raise ValueError('Checkpoint request differs from its contract')
                response = envelope['response']
            else:
                response = self.client.get(endpoint, request, kind='list')
                envelope = {'retrieved_at': now(), 'endpoint': endpoint,
                            'params': request, 'response': response}
                atomic_bytes(file, gzip.compress(dumps(envelope), mtime=0))
            yield response[rows_key], response['meta'], envelope['retrieved_at']
            next_cursor = response['meta'].get('next_cursor')
            # OpenAlex currently returns a cursor even after a short final
            # group page; a non-ASCII language key can then cycle to page1.
            # A short page exhausts this requested page size. Totals are
            # independently reconciled after collection.
            short_final_page = len(response[rows_key]) < request['per_page']
            effective_next = None if short_final_page else next_cursor
            save_json(directory / 'checkpoint.json', {
                'pages': index, 'last_retrieved_at': envelope['retrieved_at'],
                'next_cursor': effective_next, 'api_next_cursor': next_cursor,
                'termination': 'short_page' if short_final_page else 'api_cursor',
                'complete': effective_next is None})
            if effective_next is None:
                break
            if next_cursor in seen_cursors:
                raise ValueError('Cursor did not advance')
            seen_cursors.add(next_cursor)
            cursor, index = next_cursor, index + 1

    def source_partition(self, partition, expression):
        path = self.output / f'source-partition-{partition}.jsonl.gz'
        counts, ids, fields, pages = [], set(), Counter(), 0
        temporary = path.with_suffix('.gz.tmp')
        with gzip.open(temporary, 'wb') as stream:
            for rows, meta, fetched in self.pages('source-partition-' + partition, '/sources',
                    {'filter': 'type:journal,works_count:' + expression}, 'results'):
                counts.append(meta['count']); pages += 1
                for row in rows:
                    if row['type'] != 'journal' or row['id'] in ids:
                        raise ValueError('Non-journal or duplicate Source within partition')
                    ids.add(row['id']); fields[len(row)] += 1
                    stream.write(dumps({'fetched_at': fetched, 'source': row}) + b'\n')
                if pages % 25 == 0:
                    print(json.dumps({'stage': 'sources', 'partition': partition,
                                      'pages': pages, 'unique_sources': len(ids)}), flush=True)
        temporary.replace(path)
        result = {'partition': partition, 'filter': expression, 'pages': pages,
                  'rows': len(ids), 'meta_count_start': counts[0], 'meta_count_end': counts[-1],
                  'meta_count_values': sorted(set(counts)), 'file': path.name,
                  'sha256': file_hash(path), 'top_level_field_counts': {str(key): value for key, value in fields.items()}}
        if len(ids) != counts[-1]:
            raise ValueError('Partition enumeration differs from final live count')
        save_json(path.with_suffix('.summary.json'), result)
        return result

    def sources(self):
        started = now()
        census = self.client.get('/sources', {'filter': 'type:journal', 'per_page': 1,
                                             'select': 'id'}, kind='list')
        save_json(self.output / 'sources-census-before.json', {'retrieved_at': now(), 'response': census})
        expressions = ['0', '1', '2-4', '5-9', '10-24', '25-49', '50-99',
                       '100-199', '200-299', '300-499', '500-999', '1000-1999', '>1999']
        parts = []
        with ThreadPoolExecutor(max_workers=5) as pool:
            jobs = [pool.submit(self.source_partition, f'{i:02d}', expression)
                    for i, expression in enumerate(expressions)]
            for job in as_completed(jobs):
                parts.append(job.result())
        ids, fields = set(), Counter()
        target = self.output / 'sources.jsonl.gz'
        temporary = target.with_suffix('.gz.tmp')
        with gzip.open(temporary, 'wb') as stream:
            for part in sorted(parts, key=lambda value: value['partition']):
                with gzip.open(self.output / part['file'], 'rb') as source:
                    for line in source:
                        row = loads(line)['source']
                        if row['id'] in ids:
                            raise ValueError('Source moved across partitions; inspect live drift')
                        ids.add(row['id']); fields[len(row)] += 1; stream.write(line)
        temporary.replace(target)
        after = self.client.get('/sources', {'filter': 'type:journal', 'per_page': 1,
                                            'select': 'id'}, kind='list')
        save_json(self.output / 'sources-census-after.json', {'retrieved_at': now(), 'response': after})
        summary = {'status': 'complete', 'started_at': started, 'completed_at': now(),
                   'rows': len(ids), 'pages': sum(p['pages'] for p in parts),
                   'meta_count_start': census['meta']['count'], 'meta_count_end': after['meta']['count'],
                   'enumeration_equals_initial_count': len(ids) == census['meta']['count'],
                   'enumeration_equals_final_count': len(ids) == after['meta']['count'],
                   'partitions': sorted(parts, key=lambda value: value['partition']),
                   'partition_exhaustiveness': 'disjoint nonnegative works_count ranges; partition sums reconciled to unfiltered live journal census',
                   'top_level_field_counts': {str(key): value for key, value in fields.items()}, 'atomic_snapshot': False,
                   'all_attributes_retained': True, 'file': target.name, 'sha256': file_hash(target)}
        if not summary['enumeration_equals_initial_count'] or not summary['enumeration_equals_final_count']:
            raise ValueError('Full partition union differs from unfiltered journal census')
        save_json(self.output / 'sources-summary.json', summary)
        return summary

    def language_index(self):
        groups, counts = [], []
        for rows, meta, fetched in self.pages('language-index', '/works',
              {'filter': 'primary_location.source.type:journal',
               'group_by': 'language:include_unknown', 'corpus': 'all'}, 'group_by'):
            groups.extend(rows); counts.append(meta['count'])
        keys = [row['key'] for row in groups]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate global language group')
        folded = defaultdict(lambda: {'count': 0, 'raw_groups': []})
        for row in groups:
            token = row['key'].rsplit('/', 1)[-1] if row['key'] else 'unknown'
            code = 'null' if token == 'unknown' else token.casefold()
            folded[code]['count'] += row['count']; folded[code]['raw_groups'].append(row)
        summary = {'meta_count_start': counts[0], 'meta_count_end': counts[-1],
                   'meta_count_values': sorted(set(counts)), 'grouped_works': sum(r['count'] for r in groups),
                   'raw_language_groups': len(groups), 'folded_languages': dict(folded),
                   'filter_casefolding': 'API language filters casefold; raw variants retained',
                   'corpus': 'all', 'year_filter': None, 'work_type_filter': None}
        if summary['grouped_works'] != counts[-1]:
            raise ValueError('Global language groups do not reconcile with Works count')
        save_json(self.output / 'language-index.json', summary)
        return summary

    def language(self, code, expected):
        path = self.output / 'language-tables' / f'{code}.csv.gz'
        path.parent.mkdir(exist_ok=True)
        rows_by_source, counts, pages = {}, [], 0
        for rows, meta, fetched in self.pages('language-' + code, '/works',
                {'filter': 'primary_location.source.type:journal,language:' + code,
                 'group_by': 'primary_location.source.id', 'corpus': 'all'}, 'group_by'):
            pages += 1; counts.append(meta['count'])
            for row in rows:
                if row['key'] in rows_by_source:
                    raise ValueError('Duplicate Source in one language aggregation')
                rows_by_source[row['key']] = row['count']
            if pages % 100 == 0:
                print(json.dumps({'stage': 'language', 'code': code, 'pages': pages,
                                  'sources': len(rows_by_source)}), flush=True)
        total = sum(rows_by_source.values())
        temporary = path.with_suffix('.gz.tmp')
        with gzip.open(temporary, 'wt', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(['source_id', 'language', 'works_count'])
            for source, count in sorted(rows_by_source.items()):
                writer.writerow([source, code, count])
        temporary.replace(path)
        summary = {'language': code, 'sources': len(rows_by_source), 'works': total,
                   'index_expected_works': expected, 'meta_count_start': counts[0],
                   'meta_count_end': counts[-1], 'meta_count_values': sorted(set(counts)),
                   'matches_index': total == expected,
                   'matches_final_meta_count': total == counts[-1], 'pages': pages,
                   'file': str(path.relative_to(self.output)), 'sha256': file_hash(path)}
        save_json(path.with_suffix('.summary.json'), summary)
        print(json.dumps({'stage': 'language-complete', **summary}), flush=True)
        return summary

    def languages(self):
        index = self.language_index()
        languages = index['folded_languages']
        # At most one page per 200 matching journals, plus an empty terminal page;
        # small-language source groups cannot exceed their number of Works.
        source_n = 207602
        estimates = {code: math.ceil(min(source_n, value['count']) / 200) + 1
                     for code, value in languages.items()}
        save_json(self.output / 'language-cost-estimate.json', {
            'estimate_kind': 'conservative upper bound, one Source group per Work maximum',
            'requests_upper_bound': sum(estimates.values()), 'by_language': estimates,
            'expected_cost_usd_upper_bound': sum(estimates.values()) * 0.0001,
            'budget_guard': 'shared Client stops at 90 percent of remaining free budget'})
        summaries = []
        with ThreadPoolExecutor(max_workers=5) as pool:
            jobs = [pool.submit(self.language, code, value['count'])
                    for code, value in sorted(languages.items(), key=lambda kv: -kv[1]['count'])]
            for job in as_completed(jobs):
                summaries.append(job.result())
        save_json(self.output / 'languages-summary.json', {
            'status': 'complete', 'completed_at': now(), 'languages': sorted(summaries, key=lambda r: r['language']),
            'total_works': sum(row['works'] for row in summaries),
            'index_works': index['grouped_works'],
            'all_language_totals_match_index': all(row['matches_index'] for row in summaries),
            'all_language_totals_match_final_meta': all(row['matches_final_meta_count'] for row in summaries)})
        return summaries

    def source_work_totals(self):
        totals, counts = {}, []
        for rows, meta, fetched in self.pages('source-work-totals', '/works',
                {'filter': 'primary_location.source.type:journal',
                 'group_by': 'primary_location.source.id', 'corpus': 'all'}, 'group_by'):
            counts.append(meta['count'])
            for row in rows:
                if row['key'] in totals:
                    raise ValueError('Duplicate Source in independent denominator groups')
                totals[row['key']] = row['count']
        target = self.output / 'independent-source-work-totals.json.gz'
        atomic_bytes(target, gzip.compress(dumps(totals), mtime=0))
        summary = {'completed_at': now(), 'source_groups': len(totals),
                   'works': sum(totals.values()), 'meta_count_values': sorted(set(counts)),
                   'meta_count_start': counts[0], 'meta_count_end': counts[-1],
                   'matches_final_meta_count': sum(totals.values()) == counts[-1],
                   'file': target.name, 'sha256': file_hash(target)}
        save_json(self.output / 'independent-source-work-totals-summary.json', summary)
        return summary

    def id_only_denominators(self):
        source_summary = loads((self.output / 'sources-summary.json').read_bytes())
        ids = []
        with gzip.open(self.output / 'sources.jsonl.gz', 'rb') as stream:
            for line in stream:
                ids.append(loads(line)['source']['id'])
        ids = sorted(ids)
        if len(ids) != len(set(ids)) or len(ids) != source_summary['rows']:
            raise ValueError('ID-only denominator cohort differs from Source enumeration')
        batches = [ids[i:i + 100] for i in range(0, len(ids), 100)]
        save_json(self.output / 'id-only-denominator-cost-estimate.json', {
            'current_source_ids': len(ids), 'batch_size': 100, 'batches': len(batches),
            'expected_cost_usd': len(batches) * 0.0001,
            'scope': 'corpus=all, primary Source IDs only, no Source-type/year/work-type filter',
            'retry_reserve': 'hard limit 150 percent of expected requests, within 90 percent of remaining daily free budget'})
        directory = self.output / 'id-only-denominator-batches'
        directory.mkdir(exist_ok=True)
        def batch(index, cohort):
            file = directory / f'batch-{index:06d}.json.gz'
            params = {'filter': 'primary_location.source.id:' + '|'.join(key.rsplit('/', 1)[-1] for key in cohort),
                      'group_by': 'primary_location.source.id', 'corpus': 'all',
                      'per_page': 200, 'cursor': '*'}
            if file.exists():
                envelope = loads(gzip.decompress(file.read_bytes()))
                if envelope['source_ids'] != cohort or envelope['params'] != params:
                    raise ValueError('ID-only denominator batch contract mismatch')
                response = envelope['response']
            else:
                response = self.client.get('/works', params, kind='list')
                envelope = {'retrieved_at': now(), 'source_ids': cohort, 'params': params,
                            'response': response}
                atomic_bytes(file, gzip.compress(dumps(envelope), mtime=0))
            groups = response['group_by']; keys = [row['key'] for row in groups]
            if (len(keys) != len(set(keys)) or not set(keys).issubset(cohort)
                    or len(groups) > 100 or sum(row['count'] for row in groups) != response['meta']['count']):
                raise ValueError('ID-only denominator batch failed key/total reconciliation')
            totals = {key: 0 for key in cohort}
            totals.update({row['key']: row['count'] for row in groups})
            return totals, envelope['retrieved_at']
        totals, times, completed = {}, [], 0
        with ThreadPoolExecutor(max_workers=10) as pool:
            jobs = [pool.submit(batch, index, cohort) for index, cohort in enumerate(batches)]
            for job in as_completed(jobs):
                values, retrieved = job.result(); totals.update(values); times.append(retrieved); completed += 1
                if completed % 100 == 0:
                    print(json.dumps({'stage': 'id-only-denominators', 'completed_batches': completed,
                                      'batches': len(batches)}), flush=True)
        target = self.output / 'id-only-source-work-totals.json.gz'
        atomic_bytes(target, gzip.compress(dumps(totals), mtime=0))
        summary = {'status': 'complete', 'started_at': min(times), 'completed_at': max(times),
                   'sources': len(totals), 'batches': len(batches), 'total_works': sum(totals.values()),
                   'zero_work_sources': sum(value == 0 for value in totals.values()),
                   'source_cohort_sha256': source_summary['sha256'], 'all_batch_keys_and_totals_verified': True,
                   'source_type_filter': None, 'corpus': 'all', 'file': target.name, 'sha256': file_hash(target)}
        save_json(self.output / 'id-only-source-work-totals-summary.json', summary)
        return summary

    def raw_manifest(self):
        records, times, charged_response_cost = [], [], 0
        for directory in sorted((self.output / 'raw').iterdir()):
            checkpoint_path = directory / 'checkpoint.json'
            if not checkpoint_path.exists():
                continue
            checkpoint = loads(checkpoint_path.read_bytes())
            for file in sorted(directory.glob('page-*.json.gz')):
                raw = file.read_bytes(); envelope = loads(gzip.decompress(raw))
                response = envelope['response']; meta = response['meta']
                index = int(file.name.split('-')[1].split('.')[0])
                used = directory.name not in {'sources', 'source-work-totals'} and index <= checkpoint['pages']
                if used:
                    times.append(envelope['retrieved_at'])
                charged_response_cost += meta.get('cost_usd', 0)
                records.append({'file': str(file.relative_to(self.output)), 'bytes': len(raw),
                                'sha256': hashlib.sha256(raw).hexdigest(),
                                'retrieved_at': envelope['retrieved_at'],
                                'endpoint': envelope['endpoint'], 'params': envelope['params'],
                                'meta_count': meta['count'], 'cost_usd': meta.get('cost_usd'),
                                'used_in_final_collection': used})
        for file in sorted((self.output / 'id-only-denominator-batches').glob('batch-*.json.gz')):
            raw = file.read_bytes(); envelope = loads(gzip.decompress(raw))
            meta = envelope['response']['meta']; times.append(envelope['retrieved_at'])
            charged_response_cost += meta.get('cost_usd', 0)
            records.append({'file': str(file.relative_to(self.output)), 'bytes': len(raw),
                            'sha256': hashlib.sha256(raw).hexdigest(),
                            'retrieved_at': envelope['retrieved_at'], 'endpoint': '/works',
                            'params': envelope['params'], 'meta_count': meta['count'],
                            'cost_usd': meta.get('cost_usd'), 'used_in_final_collection': True})
        result = {'completed_at': now(), 'responses': len(records), 'files': records,
                  'acquisition_started_at': min(times), 'acquisition_completed_at': max(times),
                  'saved_response_cost_usd': round(charged_response_cost, 8),
                  'cost_limit': 'Response charges exclude unsaved retries and external probes; budget receipts give account totals',
                  'unused_trace': 'Initial sequential Source attempt, language-cursor overrun, and partial type-filtered global denominator retained for provenance'}
        save_json(self.output / 'raw-responses-manifest.json', result)
        return {key: value for key, value in result.items() if key != 'files'}

    def repair_source_languages(self, source, expected):
        groups, counts = [], []
        for rows, meta, fetched in self.pages('source-language-repair-' + source.rsplit('/', 1)[-1], '/works',
                {'filter': 'primary_location.source.id:' + source.rsplit('/', 1)[-1],
                 'group_by': 'language:include_unknown', 'corpus': 'all'}, 'group_by'):
            groups.extend(rows); counts.append(meta['count'])
        result = Counter()
        for row in groups:
            token = row['key'].rsplit('/', 1)[-1] if row['key'] else 'unknown'
            result['null' if token == 'unknown' else token.casefold()] += row['count']
        if sum(result.values()) != expected or sum(result.values()) != counts[-1]:
            raise ValueError('Source-specific all-Works language repair differs from ID denominator')
        return dict(result)

    def reconcile(self):
        source_summary = loads((self.output / 'sources-summary.json').read_bytes())
        language_summary = loads((self.output / 'languages-summary.json').read_bytes())
        if (source_summary['status'] != 'complete'
                or not source_summary['enumeration_equals_initial_count']
                or not source_summary['enumeration_equals_final_count']
                or file_hash(self.output / source_summary['file']) != source_summary['sha256']):
            raise ValueError('Source enumeration summary or content hash failed')
        ids = set()
        with gzip.open(self.output / 'sources.jsonl.gz', 'rb') as stream:
            for line in stream:
                ids.add(loads(line)['source']['id'])
        if len(ids) != source_summary['rows']:
            raise ValueError('Source table row count differs from verified census')
        counts = defaultdict(dict)
        for row in language_summary['languages']:
            if file_hash(self.output / row['file']) != row['sha256']:
                raise ValueError('Language aggregate content hash failed')
            with gzip.open(self.output / row['file'], 'rt', encoding='utf-8', newline='') as stream:
                for record in csv.DictReader(stream):
                    counts[record['source_id']][record['language']] = int(record['works_count'])
        orphans = sorted(set(counts) - ids)
        typed_raw_total = sum(sum(value.values()) for value in counts.values())
        raw_cohort_total = sum(sum(counts.get(key, {}).values()) for key in ids)
        # The earlier type-filtered global cursor attempt is retained only as
        # unused trace. Exhaustive ID-only counts below are the independent
        # proof of all Works for each member of the current journal universe.
        id_file = self.output / 'id-only-source-work-totals.json.gz'
        id_summary = loads((self.output / 'id-only-source-work-totals-summary.json').read_bytes())
        if (id_summary['status'] != 'complete' or not id_summary['all_batch_keys_and_totals_verified']
                or id_summary['source_cohort_sha256'] != source_summary['sha256']
                or file_hash(id_file) != id_summary['sha256']):
            raise ValueError('ID-only denominator audit or content hash failed')
        independent = loads(gzip.decompress(id_file.read_bytes()))
        if set(independent) != ids or sum(independent.values()) != id_summary['total_works']:
            raise ValueError('ID-only denominator keys or total differ from current Source universe')
        repaired = []
        for key in sorted(ids):
            if sum(counts.get(key, {}).values()) != independent[key]:
                old = counts.get(key, {})
                counts[key] = self.repair_source_languages(key, independent[key])
                repaired.append({'source_id': key, 'typed_filter_language_counts': old,
                                 'all_works_language_counts': counts[key]})
        save_json(self.output / 'source-language-repairs.json', {'repairs': repaired})
        mismatches = [{'source_id': key, 'language_sum': sum(counts.get(key, {}).values()),
                       'independent_denominator': independent[key]}
                      for key in sorted(ids) if sum(counts.get(key, {}).values()) != independent[key]]
        audit_valid = not orphans
        audit_file = self.output / 'orphan-source-current-audit.json'
        if orphans and audit_file.exists():
            audit = loads(audit_file.read_bytes())
            audit_valid = (set(row['requested_id'] for row in audit['records']) == set(orphans)
                           and all(row['source'] is None for row in audit['records']))
        columns = ['source_id','works_count','known_language_works','unknown_language_works',
                   'language_counts_json','language_proportions_json','language_status']
        def export(path, cohort, outside=False):
            with gzip.open(path, 'wt', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream); writer.writerow(columns)
                for source in sorted(cohort):
                    values = counts.get(source, {}); total = sum(values.values()); unknown = values.get('null', 0)
                    proportions = {code: n / total for code, n in sorted(values.items())} if total else None
                    writer.writerow([source, total, total - unknown, unknown,
                                     json.dumps(values, sort_keys=True), json.dumps(proportions, sort_keys=True),
                                     'outside_current_source_universe_404' if outside else ('complete' if total else 'no_works')])
        target = self.output / 'journal-language-counts.csv.gz'; export(target, ids)
        outside = self.output / 'outside-universe-source-language-counts.csv.gz'; export(outside, orphans, True)
        summary = {'status': ('complete' if not mismatches and audit_valid
                              and language_summary['all_language_totals_match_index']
                              and language_summary['all_language_totals_match_final_meta'] else 'needs_reconciliation'),
                   'completed_at': now(), 'source_rows': len(ids), 'language_rows': len(ids),
                   'sources_with_works': sum(independent[key] > 0 for key in ids),
                   'sources_without_works': sum(independent[key] == 0 for key in ids),
                   'orphan_source_ids': orphans, 'orphan_sources': len(orphans),
                   'orphan_works': sum(sum(counts[key].values()) for key in orphans),
                   'orphan_source_audit_complete': audit_valid,
                   'orphan_source_audit_file': audit_file.name if orphans else None,
                   'orphan_source_audit_sha256': file_hash(audit_file) if orphans else None,
                   'outside_universe_counts_file': outside.name, 'outside_universe_counts_sha256': file_hash(outside),
                   'outside_universe_reason': 'All outside-universe IDs returned404 in current Source singleton API; retained separately from the current journal Source census',
                   'in_universe_works': sum(independent.values()), 'raw_language_group_in_universe_works': raw_cohort_total,
                   'all_works': typed_raw_total, 'index_works': language_summary['index_works'],
                   'source_language_repair_count': len(repaired),
                   'independent_source_totals_checked': True,
                   'independent_denominator_method': 'Every current Source ID, corpus=all, without a Source type filter',
                   'typed_filter_global_denominator_used': False,
                   'id_only_source_denominators_checked': True,
                   'id_only_denominator_summary_file': 'id-only-source-work-totals-summary.json',
                   'id_only_denominator_mismatches': mismatches, 'per_source_denominator_mismatches': mismatches,
                   'file': target.name, 'sha256': file_hash(target),
                   'denominator': 'Works from all corpora attributed by primary_location.source.id to each current journal; every Source ID validated, unknown languages included',
                   'zero_works_proportions': None, 'atomic_snapshot': False}
        save_json(self.output / 'reconciliation.json', summary)
        if summary['status'] != 'complete':
            raise ValueError('Current route requires verified all-Works ID-only denominators before completion')
        summary['raw_response_manifest'] = self.raw_manifest()
        save_json(self.output / 'reconciliation.json', summary)
        return summary


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--env-file', default=Path('.env'), type=Path)
    parser.add_argument('--stage', choices=['all','sources','languages','totals','id-totals','reconcile'], default='all')
    args = parser.parse_args()
    if 'artifacts' not in args.output.parts or args.output.name == 'artifacts':
        parser.error('Use a named artifacts subdirectory')
    args.output.mkdir(parents=True, exist_ok=True)
    contract = {'route': 'current_api', 'source_filter': 'type:journal', 'corpus': 'all',
                'language_source_relation': 'primary_location.source.id',
                'publication_year_filter': None, 'work_type_filter': None, 'per_page': 200}
    file = args.output / 'contract.json'
    if file.exists() and loads(file.read_bytes()) != contract:
        raise ValueError('Existing output has a different collection contract')
    save_json(file, contract)
    id_request_cap = None
    if args.stage == 'id-totals':
        source_rows = loads((args.output / 'sources-summary.json').read_bytes())['rows']
        id_request_cap = math.ceil(math.ceil(source_rows / 100) * 1.5)
    client = Client(api_key(args.env_file), rate=10, attempts=3, timeout=90,
                    max_list_requests=id_request_cap)
    budget = client.free_budget(0)
    save_json(args.output / 'budget-before.json', budget)
    save_json(args.output / 'source-cost-estimate.json', {
        'count_prior_live_probe': 207602, 'expected_source_pages': 1039,
        'expected_source_cost_usd': 0.1039, 'freebudget': budget,
        'retry_and_other_request_reserve': 'shared 90 percent daily free budget ceiling'})
    collector = Collector(args.output, client)
    try:
        if args.stage == 'all':
            with ThreadPoolExecutor(max_workers=2) as pool:
                sources, languages = pool.submit(collector.sources), pool.submit(collector.languages)
                sources.result(); languages.result()
            collector.id_only_denominators()
            print(json.dumps(collector.reconcile()), flush=True)
        elif args.stage == 'sources':
            print(json.dumps(collector.sources()), flush=True)
        elif args.stage == 'languages':
            collector.languages()
        elif args.stage == 'totals':
            print(json.dumps(collector.source_work_totals()), flush=True)
        elif args.stage == 'id-totals':
            print(json.dumps(collector.id_only_denominators()), flush=True)
        else:
            print(json.dumps(collector.reconcile()), flush=True)
    finally:
        save_json(args.output / 'run-receipt.json', {'saved_at': now(), 'attempts': dict(client.requests),
                                                  'abort_reason': client.abort_reason})
        # Sanitize the rate-limit response using the shared existing helper.
        if not client.aborted.is_set():
            save_json(args.output / 'budget-after.json', client.free_budget(0))


if __name__ == '__main__':
    main()
