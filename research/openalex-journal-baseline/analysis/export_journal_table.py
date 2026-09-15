"""Execute the journal consolidation in BigQuery, audit, and download one CSV.

Uses existing gcloud credentials and only SELECT jobs, with dry runs and a
per-job cap. SQL, job references, source metadata and validation stay together.
Rerunning a directory reuses saved jobs; an ambiguous submission is never replayed.
The manifest is the completion marker; partial files are not deliverables.
"""
import argparse
import csv
import datetime as dt
import hashlib
import gzip
import json
from pathlib import Path
import subprocess
import time
import urllib.parse
import urllib.request
import uuid

SOURCE = 'multiobs.publicdb_openalex_2026_01_rm'
PROJECT = 'gen-lang-client-0676290976'
CAP = 536870912
CHILDREN = {
    'apc_prices': 'apc_prices_json', 'concepts': 'concepts_json',
    'counts_by_year': 'counts_by_year_json',
    'host_institution_lineage': 'host_institution_lineage_json',
    'host_institution_lineage_names': 'host_institution_lineage_names_json',
    'host_organization_lineage': 'host_organization_lineage_json',
    'host_organization_lineage_names': 'host_organization_lineage_names_json',
    'publisher_lineage': 'publisher_lineage_json',
    'publisher_lineage_names': 'publisher_lineage_names_json',
    'societies': 'societies_json',
}


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def decode(result):
    fields = result['schema']['fields']
    return [dict(zip([f['name'] for f in fields], [c['v'] for c in row['f']]))
            for row in result.get('rows', [])]


class BigQuery:
    def __init__(self, root, gcloud):
        self.root = root
        self.token = subprocess.run([gcloud, 'auth', 'print-access-token', '--quiet'],
                                    capture_output=True, text=True, check=True).stdout.strip()

    def get(self, path, body=None):
        req = urllib.request.Request(
            'https://bigquery.googleapis.com/bigquery/v2/projects/' + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json',
                     'Accept-Encoding': 'gzip'})
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read()
            if response.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            return json.loads(raw)

    def run(self, name, sql, cap=CAP):
        folder = self.root / name
        folder.mkdir(exist_ok=True)
        config = {'query': sql, 'useLegacySql': False, 'useQueryCache': False,
                  'maximumBytesBilled': str(cap)}
        saved = folder / 'request.json'
        if saved.exists():
            body = json.loads(saved.read_text())
            if body['configuration']['query'] != config:
                raise ValueError(f'SQL/config changed for existing {name}; choose a new output directory')
            ref = body['jobReference']
            job = self.get(f"{PROJECT}/jobs/{ref['jobId']}?location=US")
        else:
            (folder / 'query.sql').write_text(sql)
            dry = self.get(PROJECT + '/jobs', {
                'jobReference': {'projectId': PROJECT, 'location': 'US'},
                'configuration': {'dryRun': True, 'query': config}})
            save(folder / 'dry-run.json', dry)
            estimate = int(dry['statistics']['query']['totalBytesProcessed'])
            if estimate > cap:
                raise ValueError(f'{name} exceeds cap: {estimate}')
            print(f'{name}: dry run {estimate:,} bytes', flush=True)
            ref = {'projectId': PROJECT, 'location': 'US',
                   'jobId': 'codex_journal_' + name + '_' + uuid.uuid4().hex}
            body = {'jobReference': ref, 'configuration': {'query': config}}
            save(saved, body)  # Save before POST; resume reads this exact job only.
            job = self.get(PROJECT + '/jobs', body)
        deadline = time.monotonic() + 600
        while job['status']['state'] != 'DONE':
            if time.monotonic() > deadline:
                raise TimeoutError(ref['jobId'])
            time.sleep(2)
            job = self.get(f"{PROJECT}/jobs/{ref['jobId']}?location=US")
        save(folder / 'job.json', job)
        if job['status'].get('errorResult'):
            raise RuntimeError(job['status']['errorResult'])
        return job

    def page(self, job, token=None, size=1000, start_index=None):
        params = {'location': 'US', 'maxResults': size}
        if token:
            params['pageToken'] = token
        elif start_index is not None:
            params['startIndex'] = start_index
        result = self.get(f"{PROJECT}/queries/{job['jobReference']['jobId']}?" + urllib.parse.urlencode(params))
        if not result.get('jobComplete'):
            raise RuntimeError('Result not complete')
        return result

    def small_result(self, job, name):
        result = self.page(job)
        if result.get('pageToken'):
            raise ValueError('Unexpected pagination for aggregate result')
        save(self.root / name, result)
        return decode(result)


def audit_sql(metadata):
    """Direct source aggregates, separate from consolidation SQL."""
    queries = []
    for table, meta in metadata.items():
        source = f'`{SOURCE}.{table}` AS t'
        if table == 'sources':
            source += " WHERE t.type = 'journal'"
        elif table.startswith('sources_'):
            source += f" WHERE t.source_id IN (SELECT id FROM `{SOURCE}.sources` WHERE type='journal')"
        else:
            source += f" WHERE t.id IN (SELECT SAFE_CAST(REGEXP_EXTRACT(host_organization, r'^https://openalex.org/P([0-9]+)$') AS INT64) FROM `{SOURCE}.sources` WHERE type='journal')"
        stats = ["COUNT(*) AS n", "COUNT(DISTINCT t.id) AS unique_ids" if table in {'sources', 'publishers'}
                 else 'COUNT(DISTINCT source_id) AS unique_ids']
        for f in meta['schema']['fields']:
            col = f['name']
            stats += [f'COUNTIF(t.`{col}` IS NULL) AS `{col}_null`']
            if f['type'] == 'STRING':
                stats += [f"COUNTIF(t.`{col}` = '') AS `{col}_empty`"]
        if table == 'sources':
            stats += ["TO_HEX(SHA256(STRING_AGG(CAST(id AS STRING), '\\n' ORDER BY id))) AS id_sha256"]
        queries.append(f"SELECT '{table}' AS table_name, TO_JSON_STRING(x) AS stats FROM (SELECT "
                       + ', '.join(stats) + ' FROM ' + source + ') x')
    return '\nUNION ALL\n'.join(queries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--gcloud', default='gcloud')
    args = parser.parse_args()
    root = args.output
    root.mkdir(parents=True, exist_ok=True)
    if (root / 'manifest.json').exists():
        raise FileExistsError('Completed run exists; choose a new output directory')
    bq = BigQuery(root, args.gcloud)
    table_ids = ['sources', *['sources_' + s for s in CHILDREN], 'publishers']
    meta_path = 'multiobs/datasets/publicdb_openalex_2026_01_rm/tables/'
    before_path = root / 'metadata-before.json'
    if before_path.exists():
        before = json.loads(before_path.read_text())
    else:
        before = {t: bq.get(meta_path + t) for t in table_ids}
        save(before_path, before)
    if any(t.get('streamingBuffer') for t in before.values()):
        raise ValueError('Streaming input requires an explicit snapshot')
    audit_job = bq.run('source_audit', audit_sql(before))
    audit = {r['table_name']: json.loads(r['stats'])
             for r in bq.small_result(audit_job, 'source-audit.json')}
    # Source-field denominators differ: journals, matched child rows, or distinct
    # matched publishers. Preserve those denominators instead of flattening them.
    source_missing = []
    for table, meta in before.items():
        for field in meta['schema']['fields']:
            name = field['name']
            source_missing.append({'table': table, 'column': name,
                                   'row_denominator': audit[table]['n'],
                                   'null_count': audit[table][name + '_null'],
                                   'empty_string_count': audit[table].get(name + '_empty', 0)})
    with (root / 'source-field-missingness.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=source_missing[0].keys())
        writer.writeheader()
        writer.writerows(source_missing)
    core = audit['sources']
    if core['n'] != core['unique_ids'] or core['id_null']:
        raise ValueError('Source IDs are not unique and non-null')
    # Also reject duplicate publisher IDs before a many-to-one join.
    publisher_job = bq.run('publisher_keys', f'SELECT COUNT(*) n, COUNT(DISTINCT id) unique_ids FROM `{SOURCE}.publishers`')
    keys = bq.small_result(publisher_job, 'publisher-keys.json')[0]
    if keys['n'] != keys['unique_ids']:
        raise ValueError('Publisher IDs are duplicated/null')
    sql = Path(__file__).with_suffix('.sql').read_text()
    export_job = bq.run('export', sql)
    page = bq.page(export_job, size=0)
    fields = page['schema']['fields']
    if any(f.get('mode') == 'REPEATED' or f['type'] == 'RECORD' for f in fields):
        raise ValueError('CSV requires scalar output fields')
    names = [f['name'] for f in fields]
    if any(f.get('type') != 'STRING' for f in fields if f['name'].endswith('_json')):
        raise ValueError('Related rows must be serialized JSON strings')
    save(root / 'schema.json', page['schema'])
    nulls = dict.fromkeys(names, 0)
    empty = dict.fromkeys(names, 0)
    related_counts = dict.fromkeys(CHILDREN, 0)
    related_coverage = dict.fromkeys(CHILDREN, 0)
    ids, pages, publisher_rows = [], [], 0
    csv_path = root / 'openalex-journals-2026-01.csv'
    partial = csv_path.with_suffix('.csv.partial')
    def observe(row):
        nonlocal publisher_rows
        if row['id'] is None or (ids and int(row['id']) <= int(ids[-1])):
            raise ValueError('Missing, duplicate, or unordered output ID')
        ids.append(row['id'])
        for name, value in row.items():
            nulls[name] += value is None
            empty[name] += value == ''
            if value == '\\N':
                raise ValueError('Literal value collides with CSV null marker')
        for child, name in CHILDREN.items():
            records = json.loads(row[name])
            if not isinstance(records, list) or any(str(r['source_id']) != row['id'] for r in records):
                raise ValueError(f'Related row has wrong journal ID: {child}')
            related_counts[child] += len(records)
            related_coverage[child] += bool(records)
        if row['publisher_record_json'] is not None:
            publisher = json.loads(row['publisher_record_json'])
            if row['host_organization'] != 'https://openalex.org/P' + str(publisher['id']):
                raise ValueError('Publisher association mismatch')
            publisher_rows += 1

    checkpoint_path = root / 'download-checkpoint.json'
    if partial.exists():
        checkpoint = json.loads(checkpoint_path.read_text())
        if (checkpoint['bytes'] != partial.stat().st_size
                or checkpoint['job'] != export_job['jobReference']):
            raise ValueError('Partial CSV differs from completed-page checkpoint; inspect before recovery')
        with partial.open(newline='', encoding='utf-8') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != names:
                raise ValueError('Partial CSV schema differs')
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError('Malformed partial CSV')
                observe({k: None if v == '\\N' else v for k, v in row.items()})
        if len(ids) != checkpoint['rows']:
            raise ValueError('Partial CSV row count differs from checkpoint')
        pages = checkpoint['pages']
        print(f'Resuming saved result after {len(ids):,} validated CSV rows', flush=True)
    page = bq.page(export_job, start_index=len(ids), size=1000)
    with partial.open('a' if ids else 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=names, lineterminator='\n')
        if not ids:
            writer.writeheader()
        while True:
            if int(page['totalRows']) != core['n']:
                raise ValueError('Consolidation changed journal count')
            rows = decode(page)
            for row in rows:
                observe(row)
                writer.writerow({k: '\\N' if v is None else v for k, v in row.items()})
            token = page.get('pageToken')
            pages.append({'page': len(pages) + 1, 'rows': len(rows), 'cumulative': len(ids)})
            handle.flush()
            save(checkpoint_path, {'job': export_job['jobReference'], 'rows': len(ids),
                                   'bytes': partial.stat().st_size, 'pages': pages})
            print(f'CSV: {len(ids):,}/{core["n"]:,} rows', flush=True)
            if not token:
                break
            if not rows:
                raise ValueError('Empty page with continuation')
            page = bq.page(export_job, token, size=1000)
    id_hash = hashlib.sha256('\n'.join(ids).encode()).hexdigest()
    if len(ids) != core['n'] or id_hash.lower() != core['id_sha256'].lower():
        raise ValueError('Output ID set differs from source')
    for child in CHILDREN:
        if related_counts[child] != audit['sources_' + child]['n']:
            raise ValueError(f'Lost/multiplied child rows: {child}')
        if related_coverage[child] != audit['sources_' + child]['unique_ids']:
            raise ValueError(f'Changed child journal coverage: {child}')
    # Check final-column null/empty/list coverage inside BigQuery as requested.
    dest = export_job['configuration']['query']['destinationTable']
    dest_id = '.'.join(dest[k] for k in ['projectId', 'datasetId', 'tableId'])
    stats = []
    for f in fields:
        c = f['name']
        e = f"COUNTIF(`{c}` = '')" if f['type'] == 'STRING' else 'CAST(0 AS INT64)'
        a = f"COUNTIF(`{c}` = '[]')" if c in CHILDREN.values() else 'CAST(0 AS INT64)'
        stats.append(f"STRUCT('{c}' AS column_name, COUNT(*) AS n, COUNTIF(`{c}` IS NULL) AS null_count, {e} AS empty_string_count, {a} AS empty_list_count)")
    missing_sql = 'SELECT cell.* FROM (SELECT [' + ', '.join(stats) + f'] AS cells FROM `{dest_id}`), UNNEST(cells) AS cell'
    # JSON repeats field names for each child row, so audit its larger temporary
    # result with a separate 2 GiB cap, still checked before submission.
    missing_job = bq.run('missingness', missing_sql, cap=2147483648)
    missing = bq.small_result(missing_job, 'missingness-bigquery.json')
    for r in missing:
        c = r['column_name']
        if int(r['n']) != len(ids) or int(r['null_count']) != nulls[c] or int(r['empty_string_count']) != empty[c]:
            raise ValueError(f'Cloud/local missingness differs: {c}')
        for child, col in CHILDREN.items():
            if col == c and int(r['empty_list_count']) != len(ids) - related_coverage[child]:
                raise ValueError(f'Cloud/local empty-list counts differ: {c}')
    with (root / 'column-missingness.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=missing[0].keys())
        writer.writeheader(); writer.writerows(missing)
    after = {t: bq.get(meta_path + t) for t in table_ids}
    save(root / 'metadata-after.json', after)
    for t in table_ids:
        for key in ['schema', 'numRows', 'numBytes', 'lastModifiedTime', 'streamingBuffer']:
            if before[t].get(key) != after[t].get(key):
                raise ValueError(f'Input changed during run: {t}.{key}')
    # Reopen the physical CSV; quoted newlines are legal, so count parsed records.
    with partial.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        readback_ids = []
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError('Malformed CSV row')
            readback_ids.append(row['id'])
        if reader.fieldnames != names or readback_ids != ids:
            raise ValueError('CSV readback changed schema/rows')
    partial.rename(csv_path)
    digest = hashlib.file_digest(csv_path.open('rb'), 'sha256').hexdigest()
    save(root / 'manifest.json', {
        'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'source': SOURCE, 'execution_project': PROJECT, 'location': 'US',
        'rows': len(ids), 'columns': len(names), 'id_sha256': id_hash,
        'csv': csv_path.name, 'bytes': csv_path.stat().st_size, 'sha256': digest,
        'null_marker': '\\N', 'empty_string': '', 'unmatched_child_list': '[]',
        'related_rows': related_counts, 'related_journal_coverage': related_coverage,
        'publisher_rows': publisher_rows, 'pages': pages,
        'source_metadata_stable': True, 'csv_readback_passed': True,
        'jobs': [j['jobReference'] for j in [audit_job, publisher_job, export_job, missing_job]],
        'bytes_billed': sum(int(j['statistics']['query']['totalBytesBilled'])
                            for j in [audit_job, publisher_job, export_job, missing_job]),
        'boundary': 'Observed stable source metadata; no transactionally atomic cross-job snapshot. Empty tables/missing mappings do not prove absence of real relationships.'})
    print(f'Validated {len(ids):,} rows, {len(names)} columns; SHA256 {digest}', flush=True)


if __name__ == '__main__':
    main()
