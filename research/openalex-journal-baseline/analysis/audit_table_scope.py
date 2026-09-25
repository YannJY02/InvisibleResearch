"""Inventory every table and distinguish schema routes from verified joins.

The rules CSV is a human-authored interpretation. Metadata and the bounded
example are fetched from BigQuery. No full works/author scan is performed.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.parse

from export_journal_table import BigQuery, SOURCE, save

BASE = 'multiobs/datasets/publicdb_openalex_2026_01_rm'
HERE = Path(__file__).resolve().parent


def collect(root, client):
    if (root / 'metadata.json').exists():
        raise ValueError('Use a new directory to collect a new observation')
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    items, token = [], None
    while True:
        params = {'maxResults': 1000}
        if token:
            params['pageToken'] = token
        page = client.get(BASE + '/tables?' + urllib.parse.urlencode(params))
        items.extend(page.get('tables', []))
        token = page.get('nextPageToken')
        if not token:
            break
    names = sorted(x['tableReference']['tableId'] for x in items)
    if len(names) != len(set(names)):
        raise ValueError('Duplicate table IDs in inventory')
    save(root / 'tables.json', items)
    with ThreadPoolExecutor(max_workers=4) as pool:
        metadata = dict(zip(names, pool.map(
            lambda name: client.get(BASE + '/tables/' + name), names)))
    save(root / 'metadata.json', metadata)
    save(root / 'collection.json', {
        'started_at': started,
        'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'dataset': SOURCE, 'table_count': len(names),
        'methods': ['tables.list', 'tables.get'], 'sql_jobs': 0,
        'boundary': 'Sequential metadata observation, not a transactional snapshot.'})


def probe(root, client):
    """Read four 100-row blocks via tabledata.list; join only small tables.

    These are convenience examples, not random or representative sampling.
    The initial first-block-only attempt is retained separately as evidence.
    """
    columns = ['id', 'primary_source_id', 'primary_topic_id']
    # tabledata.list returns selected fields in schema order, checked here.
    metadata = json.loads((root / 'metadata.json').read_text())
    order = [f['name'] for f in metadata['works']['schema']['fields'] if f['name'] in columns]
    if order != columns:
        raise ValueError('Preview field order changed')
    records = []
    count = int(metadata['works']['numRows'])
    offsets = [count * n // 4 for n in range(4)]
    for offset in offsets:
        sample_path = root / ('works-preview.json' if offset == 0 else f'works-preview-{offset}.json')
        if not sample_path.exists():
            params = {'maxResults': 100, 'startIndex': offset, 'selectedFields': ','.join(columns)}
            page = client.get(BASE + '/tables/works/data?' + urllib.parse.urlencode(params))
            save(sample_path, page)
        page = json.loads(sample_path.read_text())
        for row in page.get('rows', []):
            values = [cell['v'] for cell in row['f']]
            if len(values) != len(columns):
                raise ValueError('Unexpected preview width')
            records.append(dict(zip(columns, values)))
    if not records:
        raise ValueError('Empty works preview')
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('Repeated work IDs in preview blocks; inspect before interpreting the example')
    structs = []
    for row in records:
        literals = []
        for key in columns:
            value = row[key]
            if value is not None and not re.fullmatch(r'[0-9]+', str(value)):
                raise ValueError('Non-integer ID in preview')
            literals.append(f'CAST({value if value is not None else "NULL"} AS INT64) AS {key}')
        structs.append('STRUCT(' + ', '.join(literals) + ')')
    sql = f"""-- This example uses at most 400 previewed works; it does not scan works.
WITH preview AS (SELECT * FROM UNNEST([{', '.join(structs)}]))
SELECT w.id AS work_id, s.id AS source_id, s.display_name AS journal,
       w.primary_topic_id, t.display_name AS topic,
       t.domain AS domain_id, d.display_name AS domain,
       t.field AS field_id, f.display_name AS field,
       t.subfield AS subfield_id, sf.display_name AS subfield,
       f.domain_id = t.domain AS field_domain_agrees,
       sf.field_id = t.field AND sf.domain_id = t.domain AS subfield_agrees
FROM preview w
JOIN `{SOURCE}.sources` s ON s.id = w.primary_source_id AND s.type = 'journal'
LEFT JOIN `{SOURCE}.topics` t ON t.id = w.primary_topic_id
LEFT JOIN `{SOURCE}.domains` d ON d.id = t.domain
LEFT JOIN `{SOURCE}.fields` f ON f.id = t.field
LEFT JOIN `{SOURCE}.subfields` sf ON sf.id = t.subfield
ORDER BY work_id"""
    job = client.run('scope_offsets', sql)
    result = client.small_result(job, 'scope-offsets-result.json')
    if len({r['work_id'] for r in result}) != len(result):
        raise ValueError('Example join multiplied works; inspect dictionary/source keys')
    matched = [r for r in result if r['topic'] is not None]
    if any(r['field_domain_agrees'] != 'true' or r['subfield_agrees'] != 'true'
           or r['domain'] is None for r in matched):
        raise ValueError('Example classification hierarchy did not match')
    save(root / 'scope-offsets-summary.json', {
        'preview_offsets': offsets, 'preview_rows': len(records), 'journal_join_rows': len(result),
        'matched_topic_rows': len(matched),
        'preview_and_join_work_ids_unique': True,
        'matched_hierarchies_agree': True,
        'example': next((r for r in result if r['domain'] is not None), None),
        'job': job['jobReference'],
        'bytes_processed': job['statistics']['query']['totalBytesProcessed'],
        'bytes_billed': job['statistics']['query'].get('totalBytesBilled'),
        'boundary': 'API preview order, not a random sample. Only existence of these paths is tested; no population coverage or key uniqueness claim.'})


def summarize(root, previous):
    metadata = json.loads((root / 'metadata.json').read_text())
    rules_path = HERE / 'table_scope_rules.csv'
    with rules_path.open(newline='') as handle:
        rules = list(csv.DictReader(handle))
    names = [r['table'] for r in rules]
    if len(set(names)) != len(names) or set(names) != set(metadata):
        raise ValueError(f'Rule coverage mismatch: missing={set(metadata)-set(names)}, extra={set(names)-set(metadata)}')
    fields = {name: {f['name'] for f in table['schema']['fields']}
              for name, table in metadata.items()}
    used = set(re.findall(r'`' + re.escape(SOURCE) + r'\.([^`]+)`',
                          (HERE / 'export_journal_table.sql').read_text()))
    rows = []
    for rule in rules:
        for table, column in re.findall(r'\b([a-z][a-z_]+)\.([a-z][a-z_]+)\b', rule['join_fields']):
            if table not in fields or column not in fields[table]:
                raise ValueError(f'Unknown field in rule: {table}.{column}')
        name = rule['table']
        rows.append({**rule, 'current_sql': 'yes' if name in used else 'no',
                     'metadata_rows': int(metadata[name]['numRows']),
                     'metadata_bytes': int(metadata[name]['numBytes']),
                     'columns': ', '.join(f['name'] for f in metadata[name]['schema']['fields'])})
    with (root / 'table-inventory.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    old = json.loads(previous.read_text()) if previous else {}
    summary = {
        'observation': json.loads((root / 'collection.json').read_text()),
        'table_count': len(rows), 'current_sql_tables': sorted(used),
        'empty_tables': sorted(n for n, t in metadata.items() if int(t['numRows']) == 0),
        'families': dict(sorted(Counter(n.split('_')[0] for n in names).items())),
        'priorities': dict(Counter(r['priority'] for r in rows)),
        'total_logical_bytes': sum(r['metadata_bytes'] for r in rows),
        'declared_constraint_tables': [n for n, t in metadata.items() if t.get('tableConstraints')],
        'previous_metadata': str(previous) if previous else None,
        'added_tables': sorted(metadata.keys() - old.keys()) if previous else None,
        'removed_tables': sorted(old.keys() - metadata.keys()) if previous else None,
        'changed_schema_counts_or_mtime': [n for n in metadata.keys() & old.keys()
            if any(metadata[n].get(k) != old[n].get(k)
                   for k in ['schema', 'numRows', 'numBytes', 'lastModifiedTime'])] if previous else None,
        'metadata_sha256': hashlib.sha256((root / 'metadata.json').read_bytes()).hexdigest(),
        'rules_sha256': hashlib.sha256(rules_path.read_bytes()).hexdigest(),
        'boundary': 'Rules are human-authored proposals. Existing fields are not proof of unique keys, correct types/semantics or complete foreign-key matches.'}
    save(root / 'summary.json', summary)
    lines = ['# 全部表的逐项清单', '',
             '数据行数来自本轮元数据，不是期刊子集行数；建议是人工解释，不是数据库返回的研究结论。', '']
    for family in summary['families']:
        lines += ['## ' + family, '', '| 表 | 元数据行数 | 现有 SQL | 用途与建议 |', '|---|---:|---|---|']
        for row in rows:
            if row['table'].split('_')[0] != family:
                continue
            lines.append(f"| `{row['table']}` | {row['metadata_rows']:,} | {row['current_sql']} | {row['purpose']}；{row['treatment']} |")
        lines.append('')
        for row in rows:
            if row['table'].split('_')[0] == family:
                lines += [f"### {row['table']}", '', f"- 连接路径：{row['route']}",
                          f"- 连接字段：{('`' + row['join_fields'] + '`') if row['join_fields'] else '母表，无需外部连接；行键为 sources.id'}", f"- 优先级：{row['priority']}",
                          f"- 限制：{row['caveat']}", '']
    (root / 'table-inventory.md').write_text('\n'.join(lines))
    print(json.dumps({k: summary[k] for k in ['table_count', 'families', 'priorities', 'empty_tables']}, ensure_ascii=False))


def render(root):
    """Render the dated narrative and generated full inventory using Pandoc."""
    owner = HERE.parent
    repo = owner.parent.parent
    narrative = (owner / 'table-scope.md').read_text()
    observed = json.loads((root / 'collection.json').read_text())['observed_at'][:10]
    if f'日期：{observed}' not in narrative:
        raise ValueError('Update and review the narrative for this observation date before rendering')

    def link(match):
        label, target = match.groups()
        if '://' in target or target.startswith('#'):
            return match.group(0)
        path = (owner / target).resolve().relative_to(repo)
        return f'[{label}](https://github.com/YannJY02/InvisibleResearch/blob/main/{path.as_posix()})'

    narrative = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, narrative)
    full = narrative + '\n\n---\n\n' + (root / 'table-inventory.md').read_text()
    (root / 'table-scope-render.md').write_text(full)
    style = root / 'style.html'
    style.write_text('''<style>
html { background:#f3f5f7; color:#17283b; font-family:system-ui,sans-serif; }
body { max-width:1100px; margin:24px auto; padding:32px 42px; background:white; }
h1,h2,h3 { color:#123b50; scroll-margin-top:20px; }
h2 { border-bottom:2px solid #d3e4e7; padding-bottom:10px; margin-top:38px; }
p,li { line-height:1.75; } a { color:#096a80; }
table { border-collapse:collapse; width:100%; margin:20px 0; font-size:14px; }
th,td { border:1px solid #d9e2e8; padding:10px; text-align:left; vertical-align:top; }
th { background:#edf4f5; } tr:nth-child(even) { background:#fafcfd; }
pre { background:#eef3f6; padding:18px; overflow-x:auto; }
code { font-size:.88em; overflow-wrap:anywhere; } pre code { overflow-wrap:normal; }
nav { background:#f4f8fa; padding:16px 24px; }
@media(max-width:700px) { body { margin:0; padding:20px; } table { font-size:12px; } }
</style>''')
    subprocess.run(['pandoc', '--from=gfm', '--to=html5', '--standalone',
                    '--toc', '--toc-depth=2', '--metadata',
                    'title=期刊合表范围与全部表的连接清单',
                    '--include-in-header', str(style), '--output', str(root / 'table-scope.html')],
                   input=full, text=True, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--gcloud', default='/Users/yann.jy/.local/google-cloud-sdk/bin/gcloud')
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--probe', action='store_true')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--previous', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.collect or args.probe:
        client = BigQuery(args.output, args.gcloud)
        if args.collect:
            collect(args.output, client)
        if args.probe:
            probe(args.output, client)
    summarize(args.output, args.previous)
    if args.render:
        render(args.output)


if __name__ == '__main__':
    main()
