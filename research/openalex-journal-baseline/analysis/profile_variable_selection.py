"""Descriptive streaming profile; never changes the source CSV or modelling data."""
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

csv.field_size_limit(sys.maxsize)
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'src/invisible_research').is_dir())
INPUT = ROOT / 'research/openalex-journal-baseline/artifacts/two-route-delivery-2026-10-01/route-b-api/openalex-route-b-api-2026-10-01-journals.csv.gz'
OUTPUT = ROOT / 'research/openalex-journal-baseline/artifacts/variable-selection-2026-10-16/profile.json'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
BUCKETS = ('missing_marker', 'null_marker', 'empty_string', 'empty_array', 'empty_object', 'nonempty')
LEVELS = ('topic', 'subfield', 'field', 'domain')

def decode(raw):
    if raw == r'\M': return 'missing', None
    if raw == r'\N': return 'null', None
    if raw.startswith(r'\S'):
        val = json.loads(raw[2:])
        assert isinstance(val, str)
        return 'string', val
    if raw and (raw[0] in '[{"-0123456789' or raw in {'null','true','false','NaN','Infinity'}):
        try: val = json.loads(raw)
        except (ValueError, TypeError): return 'string', raw
        if val is None: return 'null', val
        if isinstance(val, bool): return 'boolean', val
        if isinstance(val, int): return 'integer', val
        if isinstance(val, float): return 'number', val
        if isinstance(val, list): return 'array', val
        if isinstance(val, dict): return 'object', val
        return 'string', val
    return 'string', raw

def bucket(raw):
    return {r'\M':'missing_marker', r'\N':'null_marker', '':'empty_string', '[]':'empty_array', '{}':'empty_object'}.get(raw, 'nonempty')

def sample(row, raw):
    return {'source_id': row['source_id'], 'route_row_id': row['route_row_id'], 'display_name': row['display_name'], 'raw_preview': raw[:220], 'truncated': len(raw)>220, 'raw_length':len(raw)}

def new_levels():
    return {level: {'names':defaultdict(set), 'parents':defaultdict(set), 'counts':Counter(), 'missing_id_entries':0, 'missing_name_entries':0} for level in LEVELS}

def topic_add(stats, entries):
    sets = {level:set() for level in LEVELS}
    for entry in entries:
        assert isinstance(entry,dict)
        vals={'topic':entry, **{level:entry.get(level) for level in LEVELS[1:]}}
        for i,level in enumerate(LEVELS):
            val = vals[level]
            if not isinstance(val,dict) or not val.get('id'):
                stats[level]['missing_id_entries'] += 1
                continue
            ident=val['id']; sets[level].add(ident)
            if val.get('display_name'): stats[level]['names'][ident].add(val['display_name'])
            else: stats[level]['missing_name_entries']+=1
            if i<3:
                parent=vals[LEVELS[i+1]]
                if isinstance(parent,dict) and parent.get('id'): stats[level]['parents'][ident].add(parent['id'])
    for level in LEVELS: stats[level]['counts'][len(sets[level])] += 1

def summarise_levels(stats, rows):
    out={}
    for level,s in stats.items():
        counts=s['counts']; names=s['names']; parents=s['parents']
        nonzero={n:c for n,c in counts.items() if n}
        conflicts={i:sorted(v) for i,v in names.items() if len(v)>1}
        multi={i:sorted(v) for i,v in parents.items() if len(v)>1}
        out[level]={'unique_id_count':len(names), 'journals_with_nonempty_level':sum(nonzero.values()),
                    'per_journal_unique_id_min_including_empty':min(counts), 'per_journal_unique_id_max':max(counts),
                    'per_nonempty_journal_unique_id_min':min(nonzero) if nonzero else None,
                    'per_nonempty_journal_unique_id_max':max(nonzero) if nonzero else None,
                    'per_journal_unique_id_count_distribution':dict(sorted(counts.items())),
                    'id_name_conflict_count':len(conflicts), 'id_name_conflicts':conflicts,
                    'multiple_immediate_parent_id_count':len(multi), 'multiple_immediate_parents':multi,
                    'missing_id_entry_count':s['missing_id_entries'], 'missing_name_entry_count':s['missing_name_entries']}
        assert sum(counts.values()) == rows
    return out

sha=hashlib.sha256()
with INPUT.open('rb') as f:
    while b:=f.read(1024*1024): sha.update(b)

n=0; widths=Counter(); route_ids=set(); duplicate_route_ids=[]
levels={key:new_levels() for key in ('topics','topic_share','union')}
list_lengths={key:Counter() for key in ('topics','topic_share')}
sample_candidates={}; preferred_rows=[]; same_title_rows=[]
scalar_value_counts = {key:Counter() for key in ('route','source_identity_status','language_basis','scopus_identifier_policy','language_status','type','is_core','is_preprint_repository','is_ojs')}
scalar_distinct_bounded = {}
listed_in_counts = Counter()
with gzip.open(INPUT,'rt',encoding='utf-8',newline='') as f:
    reader=csv.reader(f); header=next(reader)
    assert len(header)==len(set(header))
    fields={key:{'raw_buckets':Counter({b:0 for b in BUCKETS}), 'parsed_type_counts':Counter(), 'examples':[]} for key in header}
    scalar_distinct_bounded = {key:set() for key in header}
    for cells in reader:
        widths[len(cells)]+=1
        assert len(cells)==len(header)
        row=dict(zip(header,cells)); n+=1
        for key in scalar_value_counts: scalar_value_counts[key][row[key]] += 1
        rid=row['route_row_id']
        if rid in route_ids: duplicate_route_ids.append(rid)
        route_ids.add(rid)
        if any(row.get(k,'').rstrip('/').split('/')[-1]=='S107737141' for k in ('source_id','route_row_id','id','ids.openalex')):
            preferred_rows.append(row)
        if row['display_name']=='Journal of Communication':
            same_title_rows.append({k:row[k] for k in ('route_row_id','source_id','id','display_name','works_count')})
        parsed={}
        for key,raw in zip(header,cells):
            fs=fields[key]; b=bucket(raw); fs['raw_buckets'][b]+=1
            typ,val=decode(raw); fs['parsed_type_counts'][typ]+=1
            if typ not in ('array','object') and len(scalar_distinct_bounded[key])<3: scalar_distinct_bounded[key].add(raw)
            if key=='listed_in' and isinstance(val,list): listed_in_counts.update(set(val))
            if key in ('topics','topic_share'): parsed[key]=val
            if b=='nonempty' and len(fs['examples'])<2 and all(e['raw_preview'] != raw[:220] for e in fs['examples']): fs['examples'].append(sample(row,raw))
        for key in ('topics','topic_share'):
            val=parsed[key]
            assert isinstance(val,list)
            list_lengths[key][len(val)]+=1
            topic_add(levels[key],val)
        topic_add(levels['union'],parsed['topics']+parsed['topic_share'])
        if n % 50000 ==0: print(f'profiled {n} rows',flush=True)

# Prefer the specifically identified example journal when it actually exists.
for row in preferred_rows[:1]:
    for key in header:
        raw=row[key]
        if bucket(raw)=='nonempty':
            prior=[e for e in fields[key]['examples'] if e['raw_preview']!=raw[:220]]
            fields[key]['examples']=[sample(row,raw)]+prior[:1]

for key,fs in fields.items():
    assert sum(fs['raw_buckets'].values())==n, key
    assert sum(fs['parsed_type_counts'].values())==n, key
    fs['raw_buckets']=dict(fs['raw_buckets']); fs['parsed_type_counts']=dict(fs['parsed_type_counts'])

result={
    'profile_generated_at_utc':datetime.now(timezone.utc).isoformat(),
    'source':{'path':str(INPUT), 'relative_path':str(INPUT.relative_to(ROOT)), 'bytes':INPUT.stat().st_size, 'compressed_sha256':sha.hexdigest(), 'route':'B', 'source_acquisition_date':'2026-10-01', 'scope':'Entire final post-Scopus Route B CSV, streamed without cohort filtering; denominator is CSV rows, not papers/Works.'},
    'denominator_rows':n, 'column_count':len(header), 'header':header,
    'encoding':{'missing_marker':r'\M means absent/not supplied field', 'null_marker':r'\N means explicit null', 'empty_string':'raw empty cell', 'empty_array':'raw []', 'empty_object':'raw {}', 'nonempty':'all remaining raw cells, including zero and false', 'escaped_string':r'\S followed by a JSON string', 'parsed_types':'Decoded using collect_source_metadata.py CSV encoding; missing is separate from null. These are observed types, not inferred meanings.'},
    'field_profiles':fields,
    'selected_scalar_raw_value_counts':{key:dict(c) for key,c in scalar_value_counts.items()},
    'listed_in_value_journal_counts':dict(sorted(listed_in_counts.items())),
    'constant_scalar_fields':{key:next(iter(vals)) for key,vals in scalar_distinct_bounded.items() if len(vals)==1 and not any(t in fields[key]['parsed_type_counts'] for t in ('array','object'))},
    'topic_lists':{key:{'raw_empty_array_rows':fields[key]['raw_buckets']['empty_array'], 'raw_missing_marker_rows':fields[key]['raw_buckets']['missing_marker'], 'raw_null_marker_rows':fields[key]['raw_buckets']['null_marker'], 'list_entry_count_distribution':dict(sorted(list_lengths[key].items())), 'levels':summarise_levels(levels[key],n)} for key in ('topics','topic_share')},
    'topic_union_levels':summarise_levels(levels['union'],n),
    'preferred_example':{'requested_canonical_source_id':'S107737141', 'matched_rows':len(preferred_rows), 'rows':preferred_rows, 'other_exact_title_matches':same_title_rows},
    'verification':{'header_unique':len(header)==len(set(header)), 'row_width_counts':dict(widths), 'all_row_widths_match_header':set(widths)=={len(header)}, 'unique_route_row_id_count':len(route_ids), 'duplicate_route_row_ids':duplicate_route_ids, 'all_field_bucket_totals_equal_denominator':True, 'all_field_type_totals_equal_denominator':True, 'topic_distribution_totals_equal_denominator':True}
}
assert not duplicate_route_ids
OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUTPUT),'rows':n,'sha256':sha.hexdigest(),'preferred_example_matches':len(preferred_rows),'topic_levels':{key:{level:s['unique_id_count'] for level,s in result['topic_lists'][key]['levels'].items()} for key in ('topics','topic_share')}},ensure_ascii=False),flush=True)
