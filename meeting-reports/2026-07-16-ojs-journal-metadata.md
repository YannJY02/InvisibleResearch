# OJS Journal Metadata Enrichment — Group Meeting Brief

- **Date:** 2026-07-16
- **Status:** Exploratory Analysis; for group discussion

## Purpose

Agree on the first analysis question to take forward after the PKP–OpenAlex
coverage run, and identify any access or matching decisions needed before more
sources or models are added.

## Evidence available

- [Khanna et al. (2022) Literature Evidence Note](../papers/invisible-communication-science/literature/khanna-2022-recalibrating-scholarly-publishing.md)
  records the study's framing, data, methods, findings, limitations, and
  literature-review leads. The reusable note format is documented in the
  [Literature Evidence Note specification](../docs/literature-evidence-note-spec.md).
- [OJS Journal Metadata Enrichment](../research/ojs-journal-metadata/README.md)
  records the pinned PKP input, row identity, OpenAlex matching rules, retained
  fields, and reproduction command. The generated `coverage-report.json` and
  review CSV remain in the owner's ignored `artifacts/` directory; the
  collaborator-visible result is recorded in [Build and validate the
  exploratory PKP–OpenAlex pipeline](https://github.com/YannJY02/InvisibleResearch/issues/69).
- [Follow-on Journal Metadata Source Assessment](../research/ojs-journal-metadata/follow-on-source-assessment.md)
  compares Crossref, the ISSN Portal, Scopus, Web of Science, and Dimensions.

## What we know

- Khanna et al. show that selective indexes omit a large, multilingual and
  Global South-centred OJS publishing stratum. Their 2020 study cohort contained
  25,671 active journals and reported 63.8% OpenAlex coverage for its
  ISSN-dependent comparison.
- The current pinned PKP Beacon V6.0 file contains 86,282 OJS rows. The pipeline
  preserved every row: 64,773 have a valid ISSN and 21,509 have no ISSN.
- Exact ISSN matching produced 49,877 uniquely matched rows, 14,706 unmatched
  rows with valid ISSNs, 190 ambiguous rows, and 21,509 rows not attempted
  because no ISSN was available. Strict coverage is 57.807%; no title-only
  candidates are included in that figure.
- OpenAlex's `is_ojs` field cannot validate PKP provenance: 8,778 unique matches
  report `is_ojs=false`. PKP and OpenAlex country values also disagree for 2,615
  of 30,028 rows where both are present.
- The exact-ISSN run is reproducible and inexpensive: 936 batched calls, two
  retries, no failed batches, and USD 0.0936 reported cost.

## What remains uncertain

- The 57.807% result is not directly comparable with Khanna et al.'s 63.8%.
  The datasets, cohort rules, dates, denominators, and matching procedures
  differ, so the difference is not evidence that OpenAlex coverage declined.
- Current noncoverage mixes distinct cases: no ISSN, a valid ISSN absent from
  OpenAlex, an ambiguous Source match, and possible title or identifier history.
- We have not defined an active-journal cohort or tested whether coverage gaps
  vary by country, activity, journal age, DOAJ presence, language, or discipline.
  The current data do not support a causal claim about why a journal is absent.
- Entitlement and reuse terms for Scopus, Web of Science, Dimensions, and
  automated ISSN Portal access have not been confirmed.

## Smallest next analysis choices

1. **Coverage-gap profile — recommended first.** Using only the current joined
   data, compare the four match-status groups by PKP country, activity and age
   fields, and DOAJ evidence. Keep the full cohort and any agreed active subset
   as separate denominators.
2. **Identity-resolution audit.** Manually review a small stratified sample of
   valid-ISSN unmatched, multi-ISSN ambiguous, and missing-ISSN rows. Use the
   ISSN Portal and title/homepage evidence to estimate how much of the gap is
   identifier history rather than OpenAlex noncoverage.
3. **Bounded Crossref pilot.** Run only if the group wants to study DOI deposit
   activity or metadata completeness. Test it first on deduplicated unmatched
   valid ISSNs and report incremental evidence rather than silently filling
   OpenAlex gaps.

A predictors model, commercial-source integration, or full literature-review
synthesis should wait until the group chooses the outcome and cohort.

## Decisions and access questions for the group

1. Is the immediate question about **OpenAlex coverage inequality**, **identifier
   quality**, or **DOI/deposit infrastructure**?
2. Should the primary denominator be all 86,282 OJS rows, an activity-qualified
   subset, or both? If an active subset is needed, which observable rule should
   define it?
3. Should "invisibility" remain a family of source-specific outcomes rather
   than one binary label? At minimum, should no-ISSN and valid-ISSN-unmatched
   cases stay separate?
4. May the next pass use bounded title/homepage review, and who will confirm
   ambiguous journal identities?
5. Does the project have usable UvA access and retention/publication rights for
   the ISSN Portal, Scopus, or Web of Science? No licensed source is needed for
   the recommended first profile.
6. After the analysis question is fixed, should a separate review be opened to
   prepare a Candidate Version? This meeting brief itself creates no Candidate
   Version, Designation Event, or Paper Analysis designation.
