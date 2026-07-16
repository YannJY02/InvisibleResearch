# Follow-on Journal Metadata Source Assessment

Assessed 2026-07-16 for the exploratory PKP journal metadata pipeline. This
note decides which sources merit investigation after OpenAlex; it does not
authorize or implement an integration.

## Decision

Do not build a five-source enrichment chain. Finish the OpenAlex coverage
report first, preserve every PKP row, and evaluate follow-ons only against the
specific gaps or analyses that remain.

| Source | Decision after OpenAlex | Why |
|---|---|---|
| Crossref | Run the first bounded follow-on pilot | It is public, directly queryable by ISSN, and can add DOI activity and deposit-quality evidence with little access risk. It is not an identifier authority and will miss journals without Crossref deposits. |
| ISSN Portal | Use as the identity-resolution benchmark; automate only if access is funded | It is the authoritative source in this set for ISSN-L, media versions, title history, and identifier status. Useful automation is subscription-gated. |
| Scopus | Defer unless valid API entitlement and a Scopus-metric question both exist | Its strongest increment is curated inclusion, subject areas, and CiteScore/SJR/SNIP, not open journal identity. Licensing and entitlement are material constraints. |
| Web of Science | Defer unless a paid Journals API license and a JCR-metric question both exist | JIF/JCI, ranks, and JCR categories are genuinely distinct, but the source is selective and the journal API is a paid add-on. |
| Dimensions | Do not add to this journal-enrichment pipeline | Its Source Titles fields mostly overlap identifiers, title, SJR/SNIP, and start year; the API is subscription-gated and expressly not a bulk local-copy service. Reconsider only for a cross-domain publications/grants/patents question. |

The practical order is therefore:

1. OpenAlex coverage report.
2. Crossref pilot on deduplicated valid ISSNs, reporting incremental matches
   and fields rather than silently filling columns.
3. Manual ISSN Portal audit of a stratified sample of OpenAlex-unmatched and
   ambiguous journals. Seek API terms only if this materially resolves identity.
4. Scopus or Web of Science only for a pre-specified bibliometric variable and
   only after credentials, retention, attribution, and publication terms are
   recorded.

Missingness in a selective index is analytically meaningful for this project.
Do not convert absence from Scopus, Web of Science, Dimensions, or Crossref
into a generic metadata failure.

## Common join and reporting contract

- Start from the PKP row identity `(oai_url, repository_name, set_spec)` and
  left-join all enrichment. No source may drop or deduplicate PKP rows.
- Split, normalize, checksum-validate, and deduplicate ISSNs before remote
  requests. Retain the original PKP ISSN cell and all candidate matches.
- Prefer exact ISSN/eISSN matches. Use ISSN-L only as a media-family link, not
  as proof that two PKP rows are the same journal context.
- Keep source-native IDs (`OpenAlex Source ID`, Scopus source ID, Dimensions
  source-title ID, JCR journal ID) as provenance, never as PKP row keys.
- Record `source`, retrieval date, query identifier, response identifier,
  match route, ambiguity, and license/access basis for every accepted value.
- Namespace metrics by source and year. `SJR`, `SNIP`, `CiteScore`, `JIF`, and
  `JCI` are not interchangeable measures.
- Report coverage separately for journals with no ISSN, invalid ISSN, valid
  but unmatched ISSN, ambiguous match, and matched journal.

## Source comparison

### Scopus

**Access.** The Scopus APIs require an Elsevier API key. Non-commercial
research access can be free, but returned views and fields depend on the API
key and institutional entitlement; IP authentication, institutional tokens,
and OAuth are supported. This project must verify the actual UvA entitlement,
not infer it from browser access. [Scopus API overview][scopus-overview]

**Identifiers and joinability.** The Serial Title API can retrieve a source by
ISSN and returns ISSN, eISSN, a Scopus source link/ID, title, publisher, and
serial type. It also supports title search, but title-only matches should remain
review candidates. [Serial Title API][scopus-serial-api]

**Journal-level value.** Entitled views expose Scopus subject areas, open-access
metadata, CiteScore, SJR, SNIP, and historical publication/citation indicators.
These are the source's meaningful increment over general OpenAlex enrichment.
[Serial Title views][scopus-serial-views]

**Constraints.** The documented default Serial Title quota is 20,000 requests
per week, six requests per second, and at most 200 results per response. The
research must deduplicate ISSNs and profile a small batch before estimating a
full run. Elsevier's academic-research policy limits reuse, retention, public
sharing, and permitted fields; metrics also carry attribution/display rules.
[API quotas][scopus-quotas] [Scopus use policy][scopus-policy]

**Gate.** Add no Scopus code until the OpenAlex report identifies a question
that CiteScore/SJR/SNIP, Scopus subject classification, or Scopus inclusion can
answer; the repository records a valid API key/entitlement path; and the
intended retained artifact is permitted. Do not use Scopus merely as an
expensive title fallback.

### Dimensions

**Access.** The Dimensions Analytics API is available through institutional
subscription, with free access possible for eligible scientometric projects.
It uses an API key to obtain a short-lived query token. The documented limit is
30 requests per IP address per minute. [Dimensions API access][dimensions-api]

**Identifiers and joinability.** The `Source Titles` entity exposes a
Dimensions ID, combined/print/electronic ISSNs, title, type, journal-list
memberships, and linkout. Exact ISSN filtering is available. The generic
`source title` ID is provenance only; PKP has no native Dimensions ID.
[Dimensions Source Titles][dimensions-source-titles]

**Journal-level value.** Current fields include SJR, SNIP, journal lists, and
start year. Publisher, last year, and total publications are deprecated on the
Source Titles entity. The broader Dimensions graph becomes distinctive only
when the analysis needs linked publications, grants, datasets, patents, policy
documents, or clinical trials, which is beyond journal identity enrichment.

**Constraints.** Queries return at most 1,000 records per page and 50,000 per
search, with at most 400 items in an `in` filter. More importantly, the API is
not intended to create local copies, bulk datasets, dashboards, or undefined
future-use extracts. [Dimensions reasonable use][dimensions-use]

The repository already contains a large Dimensions-derived artifact, but its
origin, extraction query, version, and license remain unresolved. It is not
evidence of current API entitlement or permission to enrich this new cohort.
[Local authority inventory](../../docs/artifact-authority-inventory.md)

**Gate.** No follow-on implementation for the current destination. Reopen the
decision only for a named cross-domain analysis and a documented access/license
basis; use an approved bulk delivery rather than the Analytics API if a local
corpus is required.

### Web of Science

**Access.** The Web of Science Journals API requires an API key and a paid
license sold as an add-on to Journal Citation Reports or InCites. Its plan is
limited to five requests per second. The Starter API has a public free trial,
but that is basic document/journal lookup with 50 requests per day and does not
substitute for Journals API access to JCR metrics. [Journals API][wos-journals]
[Starter API][wos-starter]

**Identifiers and joinability.** The Journals API searches by ISSN/eISSN,
title, JCR abbreviation, or publisher. A journal record includes a native JCR
ID, current and previous ISSNs, eISSN, titles, publisher, frequency, first issue
year, language, open-access information, categories, and yearly report links.
[Journals API schema][wos-schema]

**Journal-level value.** The yearly reports provide JIF, JCI, category ranks,
quartiles and percentiles, influence/source metrics, citation distributions,
open-access profile counts, and cited/citing journal relationships. These are
distinct bibliometric variables, not match-repair metadata.

**Constraints.** Results are limited to 50 per page; metric filters require a
JCR year; coverage is intentionally restricted to journals in the selected Web
of Science/JCR collections. Product terms govern retained and published data.

**Gate.** Add no Web of Science code unless a collaborator confirms a paid
Journals API license and pre-specifies the JCR metric and year needed. Treat
non-coverage as index selection, not evidence that a PKP journal is invalid.

### Crossref

**Access.** The Crossref REST API is public with no registration. Use the polite
pool with a contact email and identifying user agent; current documented limits
are 10 requests per second and three concurrent requests for that pool. Cache
responses and back off on `429`. [Crossref access][crossref-access]

**Identifiers and joinability.** `/journals/{issn}` and
`/journals/{issn}/works` provide exact ISSN routes. Journal results can contain
title, publisher, associated ISSNs, DOI counts, annual DOI breakdowns, and
metadata-deposit coverage. Crossref only describes content registered with
Crossref; absence is not evidence that a journal does not exist.
[Crossref REST API][crossref-rest]

**Journal-level value.** The useful increment is operational rather than
authoritative: whether a journal has Crossref-registered content, recent and
backfile DOI counts, and how completely the depositing member supplies
references, abstracts, licenses, funders, ORCIDs, RORs, and resource links.
These fields can help characterize discoverability infrastructure.

**Constraints.** ISSN medium typing and title/publisher values are depositor
metadata, not ISSN authority data. A journal without Crossref DOIs will not be
rescued. Work-level retrieval can become large, so the first pilot should use
the journal summary endpoint and request works only for a pre-specified need.

**Gate.** This is the only immediate implementation candidate, but still only
after OpenAlex. A pilot should report incremental coverage on OpenAlex-unmatched
valid ISSNs, unique fields on matched journals, request volume, and ambiguity.
Promote it to the pipeline only if the pilot answers a named analysis question.

### ISSN Portal

**Access.** Free records expose essential identity information. Full records,
exports, and automated access are paid: the portal advertises full access from
EUR 1,028/year and Search API/OAI-PMH access by quotation. The current product
page describes the Search API as SRU, while an older FAQ describes automated
REST access; obtain the actual specification and reuse terms from ISSN sales
before coding. [ISSN Portal plans][issn-plans]
[ISSN automated access][issn-automated]

**Identifiers and joinability.** The registry's central value is authoritative
ISSN and ISSN-L identity. Free information includes ISSN/ISSN-L, key title,
country, language, and medium. Full records add title variants, former and
successor relationships, publisher history, publication dates, subjects,
status, and related resources. ISSN-L groups media versions of the same serial.
[ISSN full records][issn-full] [ISSN-L definition][issn-l]

**Journal-level value.** This is the best source here for deciding whether two
print/electronic ISSNs belong to one continuing resource family, whether an
identifier is current/cancelled/incorrect, and whether title changes explain a
failed or ambiguous match. It is not a citation-impact source.

**Constraints.** Download formats and quotas depend on subscription package;
the published minimum package allows 1,000 record downloads per year, far below
the PKP cohort. A manual portal lookup can validate a sample but is not a
reproducible bulk pipeline. [ISSN downloads][issn-downloads]

**Gate.** Before any purchase or integration, manually audit a stratified
sample of OpenAlex-unmatched journals: valid single ISSN, multiple ISSNs,
ambiguous OpenAlex match, and suspected title change. Seek API access only if
ISSN authority data materially reduces unresolved identity and the license
permits the planned derived coverage report.

## Evidence required before a follow-on implementation ticket

A source graduates from assessment to an implementation decision only when the
OpenAlex report and a source-specific pilot establish all of the following:

1. the unresolved OpenAlex gap or new analytic variable;
2. valid access and data-reuse terms for this project;
3. exact input identifiers and expected match route;
4. incremental coverage and fields on a reproducible sample;
5. rate/quota and cost estimate after ISSN deduplication;
6. treatment of ambiguous, missing, and selective-index cases; and
7. the smallest retained artifact allowed by the source license.

Until then, Scopus, Dimensions, Web of Science, and ISSN Portal remain evaluated
options rather than integrations. Crossref remains a bounded pilot candidate.

[scopus-overview]: https://dev.elsevier.com/sc_apis.html
[scopus-serial-api]: https://dev.elsevier.com/documentation/SerialTitleAPI.wadl
[scopus-serial-views]: https://dev.elsevier.com/sc_serial_title_views.html
[scopus-quotas]: https://dev.elsevier.com/api_key_settings.html
[scopus-policy]: https://dev.elsevier.com/policy.html
[dimensions-api]: https://docs.dimensions.ai/dsl/api.html
[dimensions-source-titles]: https://docs.dimensions.ai/dsl/datasource-source_titles.html
[dimensions-use]: https://docs.dimensions.ai/dsl/usagepolicy.html
[wos-journals]: https://developer.clarivate.com/apis/wos-journal
[wos-starter]: https://developer.clarivate.com/apis/wos-starter
[wos-schema]: https://developer.clarivate.com/apis/wos-journal/swagger
[crossref-access]: https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/
[crossref-rest]: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
[issn-plans]: https://portal.issn.org/products/essential
[issn-automated]: https://www.issn.org/services/subscribe-to-the-register/subscription-options/
[issn-full]: https://publishers.issn.org/faq4
[issn-l]: https://www.issn.org/understanding-the-issn/assignment-rules/the-issn-l-for-publications-on-multiple-media/
[issn-downloads]: https://publishers.issn.org/faq7
