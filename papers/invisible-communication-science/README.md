# Invisible Communication Science

Status: **Publication Compendium containing Exploratory Analysis**.

This directory collects the source-authoritative analysis and the active
Etmaal slide source without changing their scientific status. Placement here
does not make the analysis a Paper Analysis Candidate and does not designate it
as Paper Analysis.

## Source authority

`analysis/analyze.Rmd` is the latest researcher-supplied analysis. Its retained
SHA-256 is
`42395d4f28ddaf3d1f062d74d215e68fc93b691d47f2e6632943f976c65797b5`.
The file remains byte-for-byte unchanged from
`Writing Report/Slides/material/analyze.Rmd`.

The source still has known reproducibility gaps: its declared relative CSV and
shapefile paths are not executable in this compendium, the R environment is
not locked, and its WDI request is live. These gaps are recorded rather than
silently repaired during migration.

## External input

The 2.58 GB Dimensions-derived CSV remains outside Git at
`$DATA_ROOT/processed/dimensions_april2025_consolidated.csv`. Its four-field
Artifact Version record is
[`data/artifact-versions/dimensions-april2025-consolidated.json`](../../data/artifact-versions/dimensions-april2025-consolidated.json).

Verify the external bytes through the shared content-identity capability:

```bash
DATA_ROOT=/path/to/InvisibleResearch/data PYTHONPATH=src \
  python papers/invisible-communication-science/analysis/verify_inputs.py
```

This verification is not a successful analysis run and does not satisfy the
Paper Analysis Candidate gate.

## Contents

- `analysis/`: unchanged Source Authority plus input verification orchestration.
- `manuscript/`: active Etmaal presentation source and required theme assets.
- `artifacts/`: ignored local presentation figures with recorded legacy hashes.
- `environment/`: retained environment evidence and known gaps.
- `governance/`: current candidate/designation boundary; no event is created here.
