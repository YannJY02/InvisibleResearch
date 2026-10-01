"""Aggregate all available Works, including XPAC, without downloading Works."""
import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

from export_journal_table import BigQuery, SOURCE, PROJECT, decode, save

CAP = 64 * 1024 ** 3
SQL = f"""WITH journals AS (
 SELECT id FROM `{SOURCE}.sources` WHERE type='journal'
), unique_works AS (
 SELECT id, MIN(primary_source_id) source_id, MIN(language) language_code,
 COUNT(*) raw_rows,
 (MIN(primary_source_id) != MAX(primary_source_id)
   OR (COUNTIF(primary_source_id IS NULL)>0 AND COUNTIF(primary_source_id IS NOT NULL)>0)) source_conflict,
 (MIN(language) != MAX(language)
   OR (COUNTIF(language IS NULL)>0 AND COUNTIF(language IS NOT NULL)>0)) language_conflict,
 (COUNTIF(is_xpac)>0 AND COUNTIF(is_xpac=FALSE)>0
   OR COUNTIF(is_xpac IS NULL)>0 AND COUNTIF(is_xpac IS NOT NULL)>0) xpac_conflict,
 COUNTIF(is_xpac)>0 is_xpac, COUNTIF(is_xpac IS NULL)=COUNT(*) xpac_unknown
 FROM `{SOURCE}.works` GROUP BY id
), aggregates AS (
 SELECT j.id IS NOT NULL is_journal, w.source_id, w.language_code,
 GROUPING(w.source_id) global_group, GROUPING(w.language_code) source_group,
 COUNT(*) n_works,
 COUNTIF(w.language_code IS NOT NULL AND TRIM(w.language_code)!='') n_known,
 COUNTIF(w.language_code IS NULL OR TRIM(w.language_code)='') n_unknown,
 COUNTIF(w.is_xpac) n_xpac,
 COUNTIF(NOT w.is_xpac AND NOT w.xpac_unknown) n_non_xpac,
 COUNTIF(w.xpac_unknown) n_xpac_unknown,
 SUM(raw_rows) raw_rows, COUNTIF(raw_rows>1) duplicated_work_ids,
 COUNTIF(w.id IS NULL) null_work_id_groups,
 COUNTIF(source_conflict) source_conflicts,
 COUNTIF(language_conflict) language_conflicts,
 COUNTIF(xpac_conflict) xpac_conflicts
 FROM unique_works w LEFT JOIN journals j ON j.id=w.source_id
 GROUP BY GROUPING SETS ((is_journal,w.source_id,w.language_code), (is_journal,w.source_id), ())
)
SELECT IF(global_group=1,'audit',IF(source_group=1,'source','language')) record_kind,
 source_id, language_code,
 IF(source_group=1,NULL,IF(language_code IS NULL,'null',IF(language_code='','empty',IF(TRIM(language_code)='','whitespace','known')))) language_status,
 n_works,n_known,n_unknown,n_xpac,n_non_xpac,n_xpac_unknown,raw_rows,
 duplicated_work_ids,null_work_id_groups,source_conflicts,language_conflicts,xpac_conflicts,
 IF(global_group=1,TO_JSON_STRING(STRUCT(
 (SELECT COUNT(*) FROM journals) AS cohort_rows,
 (SELECT COUNT(DISTINCT id) FROM journals) AS cohort_unique_ids,
 (SELECT COUNTIF(id IS NULL) FROM journals) AS cohort_null_ids,
 (SELECT TO_HEX(SHA256(STRING_AGG(CAST(id AS STRING),'\\n' ORDER BY id))) FROM journals) AS cohort_id_sha256
 )),NULL) audit_json
FROM aggregates WHERE global_group=1 OR is_journal
ORDER BY global_group DESC,source_id,source_group DESC,language_code
"""


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--gcloud', default='/Users/yann.jy/.local/google-cloud-sdk/bin/gcloud')
    parser.add_argument('--baseline', type=Path, default=Path('research/openalex-journal-baseline/artifacts/journal-export-2026-01/openalex-journals-2026-01.csv'))
    args = parser.parse_args()
    root = args.output
    if 'artifacts' not in root.parts or root.name == 'artifacts':
        parser.error('Use a named artifacts subdirectory')
    root.mkdir(parents=True, exist_ok=True)
    if (root/'summary.json').exists():
        raise FileExistsError('Completed output exists')
    csv.field_size_limit(2**31-1)
    with args.baseline.open(newline='', encoding='utf-8') as stream:
        ids = [int(row['id']) for row in csv.DictReader(stream)]
    if len(ids)!=209799 or len(set(ids))!=len(ids):
        raise ValueError('Expected original 209799 unique journal IDs')
    id_hash = hashlib.sha256('\n'.join(map(str,sorted(ids))).encode()).hexdigest()
    bq = BigQuery(root,args.gcloud)
    metadata_path='multiobs/datasets/publicdb_openalex_2026_01_rm/tables/'
    before={t:bq.get(metadata_path+t) for t in ('works','sources')}
    save(root/'metadata-before.json',before)
    config={'query':SQL,'useLegacySql':False,'useQueryCache':False,'maximumBytesBilled':str(CAP)}
    dry=bq.get(PROJECT+'/jobs',{'jobReference':{'projectId':PROJECT,'location':'US'},'configuration':{'dryRun':True,'query':config}})
    estimate=int(dry['statistics']['query']['totalBytesProcessed'])
    save(root/'cost-plan.json',{'bytes_processed_estimate':estimate,'GiB':estimate/1024**3,'on_demand_usd_estimate_before_allowances':estimate/1024**4*6.25,'maximum_bytes_billed':CAP,'scope':'all years, all Works types, no XPAC filter, global unique Work ID validation'})
    print(f'BEFORE SUBMISSION: {estimate:,} bytes ({estimate/1024**3:.3f} GiB), estimated USD {estimate/1024**4*6.25:.5f} before allowances; cap 64 GiB',flush=True)
    if estimate>CAP:
        raise ValueError('Dry run exceeds cap')
    job=bq.run('language_aggregate',SQL,cap=CAP)
    page=bq.page(job,size=1000)
    schema=page['schema'];names=[f['name'] for f in schema['fields']]
    save(root/'schema.json',schema)
    raw_path=root/'aggregate-query-results.csv'
    sources={};languages=[];audit=None;pages=[];row_count=0
    with raw_path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=names,lineterminator='\n');writer.writeheader()
        while True:
            rows=decode(page)
            for row in rows:
                if any(value=='\\N' for value in row.values()):
                    raise ValueError('Literal field value collides with CSV null marker')
                writer.writerow({k:'\\N' if v is None else v for k,v in row.items()})
                row_count+=1
                if row['record_kind']=='audit':
                    if audit is not None: raise ValueError('Duplicate audit')
                    audit=row
                    cohort=json.loads(row['audit_json'])
                    save(root/'global-work-audit.json',row)
                    if cohort['cohort_rows']!=len(ids) or cohort['cohort_unique_ids']!=len(ids) or cohort['cohort_null_ids'] or cohort['cohort_id_sha256'].lower()!=id_hash:
                        raise ValueError('BigQuery journal cohort differs from original baseline')
                    if any(int(row[k]) for k in ('source_conflicts','language_conflicts','xpac_conflicts')):
                        raise ValueError('Conflicting/missing Work identities: inspect global-work-audit.json; no completed dataset')
                elif row['record_kind']=='source':
                    key=int(row['source_id'])
                    if int(row['null_work_id_groups']):
                        raise ValueError('Journal-associated Works contain null IDs; no completed dataset')
                    if key in sources: raise ValueError('Duplicate source aggregate')
                    sources[key]={k:int(row[k]) for k in ('n_works','n_known','n_unknown','n_xpac','n_non_xpac','n_xpac_unknown')}
                elif row['record_kind']=='language':
                    languages.append({'source_id':int(row['source_id']),'language_code':row['language_code'],'language_status':row['language_status'],'language_count':int(row['n_works'])})
                else: raise ValueError('Unexpected record kind')
            pages.append({'page':len(pages)+1,'rows':len(rows),'cumulative':row_count})
            token=page.get('pageToken')
            if not token: break
            if not rows: raise ValueError('Empty page with continuation')
            page=bq.page(job,token,size=1000)
    if audit is None or row_count!=int(page['totalRows']): raise ValueError('Incomplete aggregate download')
    if int(audit['raw_rows'])!=int(before['works']['numRows']):
        raise ValueError('Global raw-row count differs from Works metadata')
    language_sums={};known_sums={}
    for row in languages:
        key=row['source_id'];den=sources[key]
        row.update(den)
        row['share_all']=row['language_count']/den['n_works'] if den['n_works'] else None
        row['share_known']=row['language_count']/den['n_known'] if row['language_status']=='known' and den['n_known'] else None
        language_sums[key]=language_sums.get(key,0)+row['language_count']
        if row['language_status']=='known':known_sums[key]=known_sums.get(key,0)+row['language_count']
    for key,row in sources.items():
        if row['n_known']+row['n_unknown']!=row['n_works'] or language_sums.get(key,0)!=row['n_works'] or known_sums.get(key,0)!=row['n_known'] or row['n_xpac']+row['n_non_xpac']+row['n_xpac_unknown']!=row['n_works']:
            raise ValueError('Language/XPAC reconciliation failed')
    if not set(sources).issubset(ids):raise ValueError('Unexpected source IDs')
    totals=[{'source_id':key,**sources.get(key,dict.fromkeys(('n_works','n_known','n_unknown','n_xpac','n_non_xpac','n_xpac_unknown'),0))} for key in ids]
    for row in totals:
        row['share_language_unknown']=row['n_unknown']/row['n_works'] if row['n_works'] else None
    files=[]
    for name,rows,columns in [('journal-language-totals.csv',totals,list(totals[0])),('journal-language-counts.csv',languages,list(languages[0]))]:
        path=root/name
        with path.open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns,lineterminator='\n');writer.writeheader()
            writer.writerows({k:'\\N' if v is None else v for k,v in row.items()} for row in rows)
        with path.open(newline='',encoding='utf-8') as stream:
            observed=list(csv.DictReader(stream))
        expected=[{k:'\\N' if v is None else str(v) for k,v in row.items()} for row in rows]
        if observed!=expected:raise ValueError('Full CSV readback differs')
        files.append({'file':name,'rows':len(rows),'columns':columns,'bytes':path.stat().st_size,'sha256':digest(path),'full_readback_passed':True})
    after={t:bq.get(metadata_path+t) for t in before}
    save(root/'metadata-after.json',after)
    for table in before:
        if any(before[table].get(k)!=after[table].get(k) for k in ('schema','numRows','numBytes','lastModifiedTime','streamingBuffer')):
            raise ValueError('Source metadata changed')
    stats=job['statistics']['query']
    summary={'status':'complete','source':SOURCE,'cohort_rows':len(ids),'cohort_id_sha256':id_hash,'baseline_sha256':digest(args.baseline),'work_attribution':'primary_source_id','window':'all available years','work_types':'all available types','xpac':'included without filtering','null_marker':'\\N','no_work_ratio':None,'known_language_rule':'non-null and TRIM(language) nonempty; raw language strings preserved','journal_unique_works':sum(x['n_works'] for x in totals),'journals_with_no_works':sum(x['n_works']==0 for x in totals),'global_work_audit':audit,'global_valid_unique_work_ids':int(audit['n_works'])-int(audit['null_work_id_groups']),'null_work_ids_in_journal_cohort':0,'files':files,'raw_aggregate_sha256':digest(raw_path),'raw_aggregate_rows':row_count,'pages':pages,'job':job['jobReference'],'bytes_processed':stats.get('totalBytesProcessed'),'bytes_billed':stats.get('totalBytesBilled'),'source_metadata_stable':True,'limitations':'Counts are all available Works in this fixed dataset, not verified total real-world publication output; metadata stability is not transactional snapshot proof. Global audit n_works includes the null-ID group, explicitly excluded from global_valid_unique_work_ids; journal aggregates contain no null-ID group.'}
    save(root/'integrity.json',{'query_sql_sha256':digest(root/'language_aggregate'/'query.sql'),
                              'job_request_sha256':digest(root/'language_aggregate'/'request.json'),
                              'result_schema_sha256':digest(root/'schema.json'),
                              'raw_aggregate_sha256':digest(raw_path),
                              'derived_files':files})
    summary['completed_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    save(root/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('pages','global_work_audit')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
