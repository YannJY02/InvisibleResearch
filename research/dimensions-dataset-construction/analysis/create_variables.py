#!/usr/bin/env python3
from __future__ import annotations

import os
# Setup and paths

from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DATA_ROOT = Path(os.environ['DATA_ROOT']).expanduser().resolve()
REQUIRED_INPUTS = (
    'processed/dimension_merged.parquet',
    'processed/scimagojr_communication_journal_1999_2024.csv',
    'processed/scimagoir_2025_Overall Rank_Communication.csv',
)
missing_inputs = [path for path in REQUIRED_INPUTS if not (DATA_ROOT / path).is_file()]
if missing_inputs:
    raise FileNotFoundError(f'Missing required Dimensions inputs under {DATA_ROOT}: {missing_inputs}')

PARQUET_INPUT = DATA_ROOT / 'processed/dimension_merged.parquet'
SJR_CSV = DATA_ROOT / 'processed/scimagojr_communication_journal_1999_2024.csv'
OUTPUT_PARQUET = DATA_ROOT / 'processed/dimension_data_for_analysis.parquet'

pd.set_option('display.max_colwidth', 160)
pd.set_option('display.width', 160)

print('Data root:', DATA_ROOT)
print('Input exists:', PARQUET_INPUT.exists())
print('SJR CSV exists:', SJR_CSV.exists())
print('Output path:', OUTPUT_PARQUET)


# %%

# Read schema (column names) and show a small preview
pf = pq.ParquetFile(PARQUET_INPUT)
print('Number of columns:', len(pf.schema.names))
print('Columns:')
print(pf.schema.names)

# Lightweight row count and a tiny data preview
num_rows = pf.metadata.num_rows
print('Total rows (metadata):', num_rows)

# Sample a few rows without loading entire file (avoid unsupported filters arg)
base_head = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=pf.schema.names[:12]).head(5)
print('\nHead (subset of columns):')
print(base_head)


# %%

# Build invisibility (robust to non-numeric times_cited)
base = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=['id','times_cited','date'])
inv = base[['id','times_cited','date']].copy()
# Convert to numeric, coercing invalid tokens (e.g., stray dict fragments) to NaN
_tc = pd.to_numeric(inv['times_cited'], errors='coerce')
# Initialize as NA; then fill where numeric is available
inv['invisibility'] = pd.Series(pd.NA, index=inv.index, dtype='Int8')
mask_num = _tc.notna()
inv.loc[mask_num, 'invisibility'] = (_tc.loc[mask_num] == 0).astype('int8')
inv['invisibility'] = inv['invisibility'].astype('Int8')
# Order output columns as specified
inv = inv[['id','invisibility','times_cited','date']]
print(inv.head())
print(inv['invisibility'].value_counts(dropna=False).rename('invisibility_counts'))


# %%

# Keep geographic fields
geo_cols = ['id','research_org_country_names','research_org_names','research_org_types']
existing_geo = [c for c in geo_cols if c in pf.schema.names]
geo = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=existing_geo)
print(geo.head())


# %%

# Keep topical fields
top_cols = ['id','concepts','concepts_scores']
existing_top = [c for c in top_cols if c in pf.schema.names]
top = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=existing_top)
print(top.head())


# %%

# Build disciplinary via SJR ISSN match (robust to multi-valued fields)
import re

# Base identifiers
disc_cols = ['id','issn','isbn']
existing_disc = [c for c in disc_cols if c in pf.schema.names]
disc = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=existing_disc)

# --- Utilities ---
TOK = re.compile(r'[0-9A-Za-z]+')

def issn_tokens(val: object) -> set[str]:
    """Extract standardized ISSN-like tokens (length==8, digits/X) from any string-ish value.
    Handles multi-valued cases separated by commas/semicolons/spaces/brackets/quotes/hyphens.
    """
    if pd.isna(val):
        return set()
    # split into alnum chunks, then strip to [0-9X], uppercase
    raw = TOK.findall(str(val))
    cleaned = [re.sub(r'[^0-9X]', '', t.upper()) for t in raw]
    # keep only 8-char tokens (ISSN normalized without hyphen)
    return {t for t in cleaned if len(t) == 8}

# --- Build SJR ISSN set (SJR side may also contain comma-separated values) ---
sjr = pd.read_csv(SJR_CSV, dtype=str, usecols=['Issn'])
sjr_issn_set: set[str] = set()
for s in sjr['Issn'].astype(str):
    sjr_issn_set.update(issn_tokens(s))

# --- Match against SJR set ---
# Prefer explicit column checks for clarity
has_issn = 'issn' in disc.columns
has_isbn = 'isbn' in disc.columns

issn_hit = pd.Series(False, index=disc.index)
if has_issn:
    issn_hit = disc['issn'].map(issn_tokens).apply(lambda s: any(t in sjr_issn_set for t in s))

isbn_hit = pd.Series(False, index=disc.index)
if has_isbn:
    # ISBN tokens typically not length 8; this filter ensures only ISSN-like tokens can match
    isbn_hit = disc['isbn'].map(issn_tokens).apply(lambda s: any(t in sjr_issn_set for t in s))

disc['disciplinary'] = (issn_hit | isbn_hit).astype('Int8')
print(disc.head())
print(disc['disciplinary'].value_counts(dropna=False).rename('disciplinary_counts'))


# %%

# Build prestige from SCImagoIR 2025 (Communication) by fuzzy-matching (rapidfuzz-accelerated)
import re
import numpy as np

# Ensure rapidfuzz is available in the current kernel
try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
except ModuleNotFoundError:
    import sys, subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'rapidfuzz'])
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz

# Tunable fuzzy threshold (validated by sampling)
PRESTIGE_FUZZY_THRESHOLD = 0.92
SCORE_CUTOFF = int(PRESTIGE_FUZZY_THRESHOLD * 100)

rank_csv = DATA_ROOT / 'processed/scimagoir_2025_Overall Rank_Communication.csv'
# Robust CSV reading with explicit columns and trailing placeholder to avoid misalignment
rank_df_raw = pd.read_csv(
    rank_csv,
    dtype=str,
    sep=';',
    engine='python',
    header=0,
    names=['Global Rank', 'Institution', 'Country', 'Sector', '_extra']
)
rank_df_raw = rank_df_raw.drop(columns=['_extra'], errors='ignore')

# Use fixed columns from SCImagoIR export
name_col = 'Institution'
rank_col = 'Global Rank'

# Normalize institution names and numeric rank

def norm_text(x: object) -> str:
    s = str(x) if pd.notna(x) else ''
    s = s.lower().strip()
    s = re.sub(r"[\-–—'’`\"]", ' ', s)
    s = re.sub(r"[^a-z0-9&\s]", ' ', s)
    s = re.sub(r"\s+", ' ', s).strip()
    return s

rank_df = rank_df_raw[[name_col, rank_col]].copy()
rank_df[name_col] = rank_df[name_col].map(norm_text)
# Drop empty institution names explicitly (treat empty string as missing)
rank_df = rank_df[rank_df[name_col].astype(str).str.strip() != '']
rank_df[rank_col] = pd.to_numeric(rank_df[rank_col], errors='coerce')

# Build lookup: normalized name → (best rank, original Institution)
rank_best = (
    rank_df.join(rank_df_raw[[name_col]], rsuffix='_orig')
            .dropna(subset=[rank_col])
            .sort_values(rank_col)
            .drop_duplicates(subset=[name_col], keep='first')
)
rank_map = rank_best.set_index(name_col)[rank_col].to_dict()
orig_by_norm = rank_best.set_index(name_col)[f'{name_col}_orig'].to_dict()
choices = list(rank_map.keys())

# Read research_org_names from the geographic frame (may contain multi-values)
geo_names = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=['id','research_org_names'])


def split_names(val: object) -> list[str]:
    if pd.isna(val):
        return []
    # Split by commas/semicolons/slashes/pipes and collapse bracket/quote noise
    s = str(val)
    # Replace brackets/quotes with space
    s = re.sub(r"[\[\]\(\)\{\}\'\"]", ' ', s)
    # Then split on common delimiters or 2+ spaces
    tokens = re.split(r"[;,/\|]|\s{2,}", s)
    # Drop empties and very short tokens
    return [t.strip() for t in tokens if t and t.strip()]

# Build unique normalized tokens once
unique_tokens: set[str] = set()
for val in geo_names['research_org_names']:
    if pd.isna(val) or str(val).strip() == '':
        continue
    for t in split_names(val):
        qn = norm_text(t)
        if qn:
            unique_tokens.add(qn)

# Map tokens → meta (rank, original matched institution, score, type, token)
token_to_meta: dict[str, dict] = {}
for tok in unique_tokens:
    if tok in rank_map:
        token_to_meta[tok] = {
            'rank': float(rank_map[tok]),
            'choice': orig_by_norm.get(tok, tok),
            'score': 100.0,
            'match_type': 'exact',
            'token': tok,
        }
        continue
    match = rf_process.extractOne(tok, choices, scorer=rf_fuzz.ratio, score_cutoff=SCORE_CUTOFF)
    if match is None:
        token_to_meta[tok] = {
            'rank': None, 'choice': None, 'score': None, 'match_type': 'none', 'token': tok
        }
    else:
        choice_norm, score, _ = match
        token_to_meta[tok] = {
            'rank': float(rank_map[choice_norm]),
            'choice': orig_by_norm.get(choice_norm, choice_norm),
            'score': float(score),
            'match_type': 'fuzzy',
            'token': tok,
        }

# For each row, compute best candidate by (rank asc, score desc)
rows = []
for rid, names in geo_names[['id','research_org_names']].itertuples(index=False):
    candidates = []
    for n in split_names(names):
        qn = norm_text(n)
        if not qn:
            continue
        m = token_to_meta.get(qn)
        if m is not None and (m['rank'] is not None):
            candidates.append(m)
    if candidates:
        best = sorted(candidates, key=lambda m: (m['rank'], - (m['score'] or 0.0)))[0]
        rows.append((rid, best['rank'], best['choice'], best['token'], best['match_type'], best['score']))
    else:
        rows.append((rid, None, None, None, None, None))

prest_df = pd.DataFrame(rows, columns=['id','best_rank','matched_institution','matched_token','match_type','match_score'])

# Map to bins (Unknown for unmatched/missing)

def to_prestige(r: float | None) -> str:
    if r is None or (isinstance(r, float) and np.isnan(r)):
        return 'Unknown'
    r = float(r)
    if r <= 100:
        return 'Elite'
    if r <= 500:
        return 'High'
    if r <= 1000:
        return 'Medium'
    return 'Low'

prest_df['prestige'] = prest_df['best_rank'].map(to_prestige)
prest = prest_df[['id','best_rank','matched_institution','matched_token','match_type','match_score','prestige']]
print(prest.head())


# %%

# Keep OA field
oa_cols = ['id','open_access']
existing_oa = [c for c in oa_cols if c in pf.schema.names]
oa = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=existing_oa)
print(oa['open_access'].value_counts(dropna=False).head())
print(oa.head())


# %%

# Build first_author_experience (robust to multi-valued id fields)
import json, ast, re

# Base columns
fae_cols = ['id','year','date','researchers','authors']
existing_fae = [c for c in fae_cols if c in pf.schema.names]
fa_raw = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=existing_fae)

# Derive paper_year: prefer `year`, fallback to year parsed from `date`
if 'year' in fa_raw.columns:
    paper_year = pd.to_numeric(fa_raw['year'], errors='coerce')
else:
    paper_year = pd.Series(pd.NA, index=fa_raw.index, dtype='Float64')

if 'date' in fa_raw.columns:
    def year_from_date(v: object):
        if pd.isna(v):
            return pd.NA
        s = str(v)
        m = re.search(r'(\d{4})', s)
        return float(m.group(1)) if m else pd.NA
    paper_year = paper_year.fillna(pd.to_numeric(fa_raw['date'].map(year_from_date), errors='coerce'))

fa_raw['paper_year'] = paper_year

# Helpers
ID_PATTERN = re.compile(r'^[a-z]{2,}\.[0-9]+', re.IGNORECASE)

def to_struct(val: object):
    if isinstance(val, (list, dict)):
        return val
    if pd.isna(val):
        return None
    s = str(val)
    if s.strip().lower() in {'', 'none', 'nan', 'null'}:
        return None
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return None

def extract_id_from_dict(d: dict) -> str | None:
    # primary
    for k in ('id','researcher_id','author_id'):
        if k in d and d[k] not in (None, '', 'None'):
            sid = str(d[k])
            if ID_PATTERN.match(sid):
                return sid
    # nested ids container
    if 'ids' in d:
        ids_obj = d['ids']
        ids_parsed = to_struct(ids_obj)
        if isinstance(ids_parsed, list):
            for itm in ids_parsed:
                if isinstance(itm, dict):
                    v = itm.get('id') or itm.get('value') or itm.get('dimensions_id')
                    if v is not None and ID_PATTERN.match(str(v)):
                        return str(v)
                elif isinstance(itm, str) and ID_PATTERN.match(itm):
                    return itm
        elif isinstance(ids_parsed, dict):
            for v in ids_parsed.values():
                if v is not None and ID_PATTERN.match(str(v)):
                    return str(v)
    return None

def extract_first_id(val: object) -> str | None:
    obj = to_struct(val)
    if obj is None:
        return None
    if isinstance(obj, list) and obj:
        first = obj[0]
        if isinstance(first, dict):
            got = extract_id_from_dict(first)
            if got:
                return got
            return None
        if isinstance(first, str) and ID_PATTERN.match(first):
            return first
        return None
    if isinstance(obj, dict):
        return extract_id_from_dict(obj)
    return None

# First-author key priority: researchers[0].id -> authors[0].id (no name fallback)
fa_key = pd.Series([None]*len(fa_raw), index=fa_raw.index, dtype='object')
if 'researchers' in fa_raw.columns:
    fa_key = fa_raw['researchers'].map(extract_first_id)
if 'authors' in fa_raw.columns:
    fallback_ids = fa_raw['authors'].map(extract_first_id)
    fa_key = fa_key.fillna(fallback_ids)
fa_raw['first_author_key'] = fa_key

# Earliest first-author year map (within this dataset)
valid_rows = fa_raw.dropna(subset=['first_author_key','paper_year']).copy()
valid_rows['paper_year'] = pd.to_numeric(valid_rows['paper_year'], errors='coerce')
first_year_map = valid_rows.groupby('first_author_key')['paper_year'].min()

# Experience = paper_year - earliest first-author year
delta = pd.to_numeric(fa_raw['paper_year'], errors='coerce') - fa_raw['first_author_key'].map(first_year_map)
delta = pd.to_numeric(delta, errors='coerce')
fa_exp = delta.round().astype('Int16')

# Output frames
fae = pd.DataFrame({'id': fa_raw['id'], 'first_author_experience': fa_exp})
fae_debug = pd.DataFrame({
    'id': fa_raw['id'],
    'first_author_key': fa_raw['first_author_key'],
    'first_author_first_year': fa_raw['first_author_key'].map(first_year_map)
})

print(fae.head())
print(fae['first_author_experience'].value_counts(dropna=False).head())
print('first_author_key non-null:', int(fae_debug['first_author_key'].notna().sum()))
print(fae_debug.head())
print('\n[Sanity check] fae valid experience count:', int(pd.to_numeric(fae['first_author_experience'], errors='coerce').notna().sum()))


# %%

# Keep control variables
ctrl_cols = ['id','document_type','type','authors_count','reference_ids','referenced_pubs']
existing_ctrl = [c for c in ctrl_cols if c in pf.schema.names]
ctrl = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=existing_ctrl)
print(ctrl.head())


# %%

# Merge by id and order columns
from functools import reduce

# Pre-merge validation
pre_merge_fae_count = int(pd.to_numeric(fae['first_author_experience'], errors='coerce').notna().sum())
print('[Pre-merge] fae valid count:', pre_merge_fae_count)

# Ensure required frames exist
frames = [inv, geo, top, disc, prest, oa, fae, ctrl]
final = reduce(lambda l, r: l.merge(r, on='id', how='left'), frames)

# Post-merge validation
post_merge_fae = pd.to_numeric(final['first_author_experience'], errors='coerce')
post_merge_fae_count = int(post_merge_fae.notna().sum())
print('[Post-merge] final first_author_experience valid:', post_merge_fae_count)
assert post_merge_fae_count == pre_merge_fae_count, 'first_author_experience changed during merge'
assert (post_merge_fae.dropna() >= 0).all(), 'first_author_experience must be non-negative'

# Column ordering by conceptual blocks
ordered_cols = (
    ['id'] +
    ['invisibility','times_cited','date','first_author_experience'] +
    ['research_org_country_names','research_org_names','research_org_types'] +
    ['concepts','concepts_scores'] +
    ['issn','isbn','disciplinary'] +
    # Prestige block with matching details
    ['best_rank','matched_institution','matched_token','match_type','match_score','prestige'] +
    ['open_access'] +
    ['document_type','type','authors_count','reference_ids','referenced_pubs']
)
final_cols = [c for c in ordered_cols if c in final.columns]
final = final[final_cols]

print('Final shape:', final.shape)
print('Columns (ordered):', final.columns.tolist())

# Write Parquet (single file)
final.to_parquet(OUTPUT_PARQUET, engine='pyarrow', compression='snappy', index=False)
print('Wrote:', OUTPUT_PARQUET)


# %%

# Load final and run checks
final_df = pd.read_parquet(OUTPUT_PARQUET, engine='pyarrow')
print('Final shape (reloaded):', final_df.shape)

import numpy as np

# Expanded missingness for variable-related columns ONLY (treat empty string '' as NA)
var_cols = [
    # Invisibility block
    'invisibility','times_cited','date','first_author_experience',
    # Geographic/Institutional (include names/types as requested)
    'research_org_country_names','research_org_names','research_org_types',
    # Topical
    'concepts','concepts_scores',
    # Disciplinary
    'issn','isbn','disciplinary',
    # Prestige
    'prestige',
    # OA
    'open_access',
    # Controls
    'document_type','type','authors_count','reference_ids','referenced_pubs'
]
var_cols = [c for c in var_cols if c in final_df.columns]

def is_blank(s: pd.Series) -> pd.Series:
    return s.isna() | s.astype(str).str.strip().eq('')

var_na_counts = {c: int(is_blank(final_df[c]).sum()) for c in var_cols}
var_na_ratio = {c: round(var_na_counts[c] / len(final_df), 4) for c in var_cols}
var_missing = (
    pd.DataFrame({'na_count': pd.Series(var_na_counts), 'na_ratio': pd.Series(var_na_ratio)})
      .sort_values('na_ratio', ascending=False)
)
print('\nVariable columns missingness (NA + empty strings), sorted by na_ratio (final output columns only):')
print(var_missing)

# Key constraints
print('\nID uniqueness check:')
print('Total ids:', final_df['id'].size, 'Distinct ids:', final_df['id'].nunique())

# Domain checks
if 'invisibility' in final_df.columns:
    print('\nInvisibility value counts:')
    print(final_df['invisibility'].value_counts(dropna=False))

if 'times_cited' in final_df.columns:
    # Coerce to numeric for robust comparison and quantiles
    tc = pd.to_numeric(final_df['times_cited'], errors='coerce')
    print('\nTimes cited quantiles:')
    print(tc.describe(percentiles=[0.5,0.9,0.99]))
    neg_tc = (tc.dropna() < 0).sum()
    print('Negative times_cited count:', int(neg_tc))

if 'authors_count' in final_df.columns:
    ac = pd.to_numeric(final_df['authors_count'], errors='coerce')
    print('\nAuthors count quantiles:')
    print(ac.describe(percentiles=[0.5,0.9,0.99]))
    neg_ac = (ac.dropna() < 0).sum()
    print('Negative authors_count count:', int(neg_ac))

if ('issn' in final_df.columns) or ('isbn' in final_df.columns):
    def valid_issn_like(x: object) -> bool:
        return bool(issn_tokens(x))
    both_missing = 0
    if ('issn' in final_df.columns) and ('isbn' in final_df.columns):
        both_missing = (is_blank(final_df['issn']) & is_blank(final_df['isbn'])).sum()
    print('\nRows missing both issn and isbn (NA + empty strings):', int(both_missing))
    if 'issn' in final_df.columns:
        print('Share of rows with a token that looks like ISSN:', round(final_df['issn'].map(valid_issn_like).mean(), 4))

# Risk indicators (base-level DOI duplicates if DOI exists upstream)
if 'doi' in pf.schema.names:
    doi_base = pd.read_parquet(PARQUET_INPUT, engine='pyarrow', columns=['id', 'doi'])
    doi_base['doi_norm'] = (
        doi_base['doi'].astype(str)
        .str.lower()
        .str.replace(r'^https?://(dx\.)?doi\.org/', '', regex=True)
        .str.replace(r'\s+', '', regex=True)
    )
    dup = doi_base[
        doi_base['doi_norm'].ne('') & doi_base['doi_norm'].notna()
    ].duplicated('doi_norm', keep=False).sum()
    print('\nDuplicate DOI (normalized) at base level:', int(dup))

# First author experience checks
if 'first_author_experience' in final_df.columns:
    fae_num = pd.to_numeric(final_df['first_author_experience'], errors='coerce')
    print('\nFirst author experience quantiles:')
    print(fae_num.describe(percentiles=[0.5, 0.9, 0.99]))
    print('Negative first_author_experience count:', int((fae_num.dropna() < 0).sum()))
