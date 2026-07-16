# Khanna et al. (2022) — Recalibrating scholarly publishing

- **Citation:** Khanna, S., Ball, J., Alperin, J. P., & Willinsky, J. (2022). Recalibrating the scope of scholarly publishing: A modest step in a vast decolonization process. *Quantitative Science Studies, 3*(4), 912–930. https://doi.org/10.1162/qss_a_00228
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/57TC9FXV)
- **DOI or URL:** https://doi.org/10.1162/qss_a_00228
- **Reviewed:** 2026-07-16
- **Reading basis:** Full text, pp. 912–930

## Why this source matters

Khanna et al. reveal a large stratum of scholarly publishing that is poorly
represented by conventional journal counts and selective indexes. Their study
connects the scale of journals using Open Journal Systems (JUOJS) to geographic,
linguistic, disciplinary, and economic bibliodiversity, then frames recognition
of that activity as one modest part of a wider decolonization process. It is both
a central empirical source for the project's indexing-invisibility argument and
a useful map of the literature on academic dependency, multilingual publishing,
OA diamond infrastructure, and the risks of equating peripheral or open-access
publishing with predation.

## Research question and framing

- **Question or aim:** Map the scale of active JUOJS across country and region,
  language, discipline, and indexing, and use that evidence to challenge narrow
  estimates of worldwide scholarly publishing (pp. 913–914).
- **Conceptual framing:** Center–periphery relations, intellectual imperialism,
  academic and recognition dependency, bibliodiversity, and “moving the center”
  from a Western default toward multiple knowledge-producing spheres (pp.
  913–914). The authors treat decolonization as a historically grounded but
  explicitly limited framing, not as a synonym for better database coverage
  (p. 914, note 7).
- **Contribution claimed:** By counting publishing activity that dominant
  indexes and common estimates largely omit, the study argues that scholarly
  communication is already more global, multilingual, and institutionally
  diverse than the recognized literature suggests (pp. 913–914, 927–928).

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | Active journal using OJS; one OJS installation hosts 2.62 active journals on average (pp. 914–915). |
| Data source | Public 2020 PKP Beacon data, supplemented by ISSN, domain, geolocation, language-classification, field-classification, index, directory, list, and Google Scholar data (pp. 914–924). |
| Sample and coverage | 25,671 journals meeting the DOAJ-derived threshold of at least five items in 2020; 36.5% of 70,214 PKP beacons then operating. ISSN-dependent analyses use smaller subsets, including 22,809 journals for several index matches and 22,561 for language analysis (pp. 914, 918–923). |
| Time period | Journal sample and publication activity: 2020. External index snapshots vary from January 2021 to June 2022 (pp. 914–915, 923). |
| Geographic or linguistic scope | 136 countries; 20 journals lacked an identified country. Language analysis detected 60 languages in the ISSN-verified subset (pp. 915–919). |

## Methods

- **Design:** Descriptive mapping of the active 2020 Beacon sample, with
  separate procedures for country, language, discipline, index coverage, and a
  preliminary citation analysis (pp. 914–926).
- **Measures or classifications:** Country was assigned through a three-step
  combination of ISSN/MARC location, country-code top-level domain, and host-IP
  geolocation. The authors classified countries through both World Bank income
  groups and UN regional groups (pp. 915–917). Language was detected from up to
  100 recent article titles and abstracts per ISSN-verified journal using gcld3;
  reliable predictions were retained, multilingual status required at least
  five articles in a language, and heuristic checks led to 478 semimanual
  corrections (pp. 916–918). Discipline was inferred from the five most recent
  titles and abstracts, translated to English and passed to a neural classifier;
  the highest-probability ANZSRC field became the journal label (pp. 921–922).
- **Analysis:** The study reports counts and proportions by geography, language,
  discipline, and source coverage. Eleven indexes, directories, and journal
  lists were matched by ISSN and/or journal URL or domain. Google Scholar
  analysis operated at OJS-domain level and used roughly the first 10 returned
  articles per domain; a small follow-up compared citation sources for the
  leading English-, Indonesian-, and Portuguese-language articles (pp.
  922–926).
- **Validation or robustness:** The country procedure triangulated three
  location signals. Language predictions used the classifier's reliability
  flag, top-level-domain heuristics, semimanual corrections, and manual
  verification of an example for every detected language. Balochi and Faroese,
  unsupported by gcld3, were found through domain searches. Data and analysis
  notebooks are linked from the article (pp. 915–919, 928).

## Findings

### The recognized scale of scholarly publishing is too small

- **Source claim:** A sample of 25,671 active JUOJS alone makes estimates of
  roughly 30,000 journals worldwide untenable; the paper does not claim to
  produce a complete world journal count (pp. 914, 927).
- **Evidence:** The sample represents 36.5% of 70,214 PKP beacons. It produced
  about 996,000 items in 2020, averaging 38.1 per journal, and the body reports
  5.4 million items since journal inception (pp. 914–915).
- **Locator:** Section 2, pp. 914–915; Conclusion, p. 927.
- **Caveat:** The abstract reports 5.8 million cumulative items rather than the
  5.4 million reported in the body; the note treats the body value as the
  section-specific result and preserves the discrepancy for verification.

### OJS publishing is geographically concentrated in the Global South yet globally distributed

- **Source claim:** JUOJS make visible a research-publishing enterprise that is
  substantially based in the Global South and spans 136 countries (pp.
  915–917).
- **Evidence:** Indonesia accounts for 11,535 journals (45.0%) and Brazil for
  2,653 (10.3%); the top 10 countries account for 74.6%. The World Bank
  income-group operation places 81.6% in Global South countries, while the UN
  regional-group operation places 78.1% in three associated regions (pp.
  915–917).
- **Locator:** Section 3.2 and Figures 2–5, pp. 915–917.
- **Caveat:** The abstract's 79.9% is not separately derived in the body and
  appears to summarize the two operationalizations; country inference can also
  be skewed toward hosting-server and data-center locations (p. 915, note 10).

### The sample exposes substantial linguistic bibliodiversity

- **Source claim:** English remains prominent without exhausting the language
  of research: the JUOJS publish in 60 detected languages, and multilingual
  publishing is common (pp. 918–921).
- **Evidence:** Among 22,561 ISSN-verified journals, 49.7% primarily publish in
  English and 48.3% publish in more than one language. Large combinations
  include 4,431 Indonesian–English bilingual journals and 550
  Portuguese–Spanish–English trilingual journals (pp. 919–921).
- **Locator:** Section 4.2 and Figures 6–8, pp. 918–921.
- **Caveat:** Reliance on titles and abstracts may overestimate English because
  those fields are often translated; gcld3 does not support every language, and
  language estimates come from the ISSN-verified subset (pp. 917, 921).

### OJS publishing is broad across disciplines and often OA diamond

- **Source claim:** The journals are not confined to locally oriented humanities
  and social sciences; STEM is also substantial, and OJS supports a large
  noncommercial publishing alternative (pp. 921–922, 927).
- **Evidence:** The abstract reports 45.9% social sciences, 40.3% STEM, and 13.8%
  humanities. The paper estimates that 84.2% of JUOJS follow an OA diamond model
  charging neither readers nor authors (pp. 912–913).
- **Locator:** Abstract, pp. 912–913; Section 5.2, pp. 921–922; Conclusion, p. 927.
- **Caveat:** The 84.2% estimate is inferred from an earlier survey reporting
  97.8% open access and 13.6% using APCs; it is not measured directly in the
  2020 Beacon sample (p. 913).

### Selective indexes make most of this publishing invisible

- **Source claim:** Literature reviews and bibliometric studies that treat Web
  of Science, EBSCOHost, or Scopus as the scientific literature systematically
  underrepresent JUOJS; newer open aggregators and Google Scholar recover much
  more of it (pp. 923–924).
- **Evidence:** Table 3 reports coverage of 1.2% in Web of Science, 3.4% in
  EBSCOHost, 7.2% in Scopus, 54.5% in Dimensions, 63.8% in OpenAlex, and 88.3%
  in Google Scholar. Within participating Iberoamerican countries, Latindex
  covers 66.6% of JUOJS (pp. 923–926).
- **Locator:** Section 6, especially Table 3, pp. 923–926.
- **Caveat:** Coverage snapshots, match keys, and denominators vary by source.
  The abstract reports 5.7% Scopus coverage, which conflicts with Table 3's
  7.2% of the 22,809 ISSN-matched subset and should be checked against the
  archived analysis before reuse (pp. 912, 923).

### Low overlap with predatory lists does not support dismissing the stratum wholesale

- **Source claim:** Framing predatory publishing as a global threat can reinforce
  peripheralization when it collapses a large, diverse OA publishing stratum
  into suspicion; journal integrity should instead be evaluated through
  transparent standards (pp. 926–927).
- **Evidence:** Cabell's Predatory Reports includes 237 JUOJS (1.0%) and Beall's
  list 366 (1.4%), with 82 journals shared by both lists (pp. 923, 926).
- **Locator:** Section 6.2.3, pp. 926–927.
- **Caveat:** The study does not audit journal quality or validate either list;
  one list is proprietary and the other list's total is projected from a prior
  sample (p. 923, notes to Table 3).

### Recognition is framed as recentering, not completed decolonization

- **Source claim:** Making this already-existing, linguistically and
  geopolitically diverse publishing activity visible shifts the assumed center
  toward multiple knowledge-producing spheres and contributes to a broader
  decolonizing agenda (pp. 913–914, 927–928).
- **Evidence:** The empirical findings demonstrate publishing across 136
  countries and 60 languages, with high Global South participation and much
  broader coverage in open aggregators than in selective indexes (pp. 915–924).
- **Locator:** Introduction, pp. 913–914; Conclusion, pp. 927–928.
- **Caveat:** Following Tuck and Yang, the authors warn that metaphorical
  decolonization is not the repatriation of Indigenous land and life and may
  itself further settler colonialism; they call for additional study rather
  than presenting database inclusion as decolonization achieved (p. 914,
  note 7).

## Limitations

### Source-reported limitations

- The paper does not estimate the total number of journals worldwide and calls
  the work preliminary rescaling rather than a complete account (p. 927).
- Country inference may capture server or data-center location instead of a
  journal's organizational origin (p. 915, note 10).
- Title-and-abstract analysis may overestimate English, and unsupported or
  underresourced languages require alternative discovery procedures (pp.
  917, 921).
- The citation analysis is preliminary: Google Scholar results are grouped by
  installation domain, and the cross-language comparison uses only the most
  cited article in three languages. The authors call for systematic citation,
  policy, and professional-practice studies (pp. 924–927).
- The decolonization framing may obscure or further colonial relations if used
  metaphorically; the authors explicitly identify this as requiring further
  research (p. 914, note 7).

### Reviewer assessment

- The optional Beacon and five-items-per-year rule select active, transmitting
  OJS installations rather than all OJS journals. The paper notes that 75.7% of
  DOAJ-listed OJS journals transmitted Beacon data, but the missingness process
  for the full OJS population is not established (p. 914, notes 8–9).
- Several analyses use only ISSN-verified journals, so coverage and language
  findings do not share one denominator. Index snapshots also span 18 months,
  limiting strict comparisons (pp. 918–924).
- Translating five recent titles and abstracts into English, applying an
  English-trained classifier, and retaining only the most probable ANZSRC label
  compress multilingual and multidisciplinary journals into a single field
  (pp. 921–922).
- The cumulative item total differs between abstract and body, and Scopus
  coverage differs between abstract and Table 3. Exact figures should be
  reopened and reconciled before quotation or downstream quantitative reuse
  (pp. 912, 914, 923).
- All four authors are associated with PKP, the developer of OJS. The paper
  discloses this competing interest, but it remains relevant when interpreting
  platform-level claims (p. 928).

## Project relevance

- **Source supports:** The claim that selective indexes miss a large and
  distinctive portion of global scholarly publishing; the need to measure
  invisibility as source-specific metadata coverage rather than equate absence
  with nonexistence or low quality; and the importance of geography, language,
  discipline, OA model, and infrastructure in interpreting OJS journals.
- **Project interpretation:** The enrichment pipeline should preserve every PKP
  journal row and report unmatched OpenAlex Sources as coverage evidence, not
  failed or invalid journals. ISSN matching is necessary but incomplete, and
  later analysis should test whether missingness varies by country, language,
  discipline, and identifier availability. The note also justifies keeping
  OpenAlex as a first open enrichment source while treating its reported 63.8%
  coverage as a historical benchmark rather than a current expectation.
- **Does not establish:** Current OpenAlex coverage, causal predictors of
  indexing, journal quality, a complete population of OJS or world journals,
  or that increased discoverability alone constitutes decolonization. It also
  does not grant this note or the project's enrichment work Paper Analysis
  authority.

## Literature-review connections

- **Themes:** Hidden scale of scholarly publishing; center–periphery and academic
  dependency; Global South research infrastructure; bibliodiversity and
  multilingualism; OA diamond publishing; index construction and invisibility;
  predatory-publishing discourse; decolonization and its conceptual limits.
- **Agreements or tensions:** The paper extends earlier OJS and OA diamond
  mappings while challenging claims of excessive or inherently suspect
  peripheral publishing. Its empirical recentering aligns with bibliodiversity
  scholarship, but Tuck and Yang's warning places a boundary around its use of
  decolonization.

| Follow-up source | Why follow it | Role |
|---|---|---|
| Altbach, P. G. (1981). “The university as center and periphery.” | Establishes the center–periphery account of research capability, publishing outlets, and dependency that Khanna et al. revisit. | Framing |
| Alatas, S. F. (2022). “Political economies of knowledge production: On and around academic dependency.” | Specifies academic and recognition dependency, including the conflict between high-ranked international journals and local-language publishing. | Framing |
| Thiong'o, N. (1993). *Moving the Centre: The Struggle for Cultural Freedoms*. | Supplies the paper's central recentering image and the phrase “vast decolonization process.” | Framing |
| Tuck, E., & Yang, K. W. (2012). “Decolonization is not a metaphor.” | Sets the essential limit on translating index inclusion or Eurocentric-bias reduction into a claim of decolonization. | Tension |
| Cetto, A. M., & Alonso-Gamboa, O. (1998). “Scientific and scholarly journals in Latin America and the Caribbean.” | Provides historical evidence of index marginalization and the institutional rationale for Latindex. | Evidence |
| Alperin, J. P., Stranack, K., & Garnett, A. (2016). “On the peripheries of scholarly infrastructure: A look at the journals using Open Journal Systems.” | Gives the earlier OJS population estimate and direct empirical predecessor to the 2022 study. | Evidence |
| Bosman, J., Frantsvåg, J. E., Kramer, B., Langlais, P.-C., & Proudman, V. (2021). *The OA Diamond Journals Study*. | Offers a comparative estimate of OA diamond publishing and documents its weak integration into scholarly infrastructure. | Evidence |
| Berger, M. (2021). “Bibliodiversity at the centre: Decolonizing Open Access.” | Connects bibliodiversity, noncommercial OA, and decolonization more directly than the focal paper's descriptive analysis. | Framing |
| Canagarajah, S. (2022). “Language diversity in academic writing: Toward decolonizing scholarly publishing.” | Develops multilingual scholarly practice as a challenge to linguistic hierarchy. | Framing |
| Navarro, F., et al. (2022). “Rethinking English as a lingua franca in scientific-academic contexts.” | States the knowledge-production costs of English-only norms and the case for multilingual transnational dialogue. | Framing |
| Vera-Baceta, M. A., Thelwall, M., & Kousha, K. (2019). “Web of Science and Scopus language coverage.” | Supplies a direct benchmark for the linguistic selectivity of the dominant indexes. | Evidence |
| Krawczyk, F., & Kulczycki, E. (2021). “How is open access accused of being predatory?” | Tests how Beall's lists shaped the conflation of OA with predatory publishing that Khanna et al. contest. | Tension |

## Open questions

- Which archived data or notebook version explains 5.8 versus 5.4 million
  cumulative items and 5.7% versus 7.2% Scopus coverage?
- How much of current PKP-to-OpenAlex noncoverage is explained by missing or
  malformed ISSNs, and how much remains after title and URL matching?
- Does OpenAlex noncoverage vary systematically by country, primary language,
  multilingual status, discipline, or journal age?
- How should the review distinguish discoverability, index inclusion, citation
  circulation, epistemic recognition, and decolonization rather than treating
  them as one outcome?
- Which of the follow-up seeds are already in Zotero, and which should be added
  before the literature-review synthesis begins?
