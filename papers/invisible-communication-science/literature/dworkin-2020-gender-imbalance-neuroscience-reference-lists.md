# Dworkin et al. (2020) — Gender imbalance in neuroscience reference lists

- **Citation:** Dworkin, J. D., Linn, K. A., Teich, E. G., Zurn, P., Shinohara, R. T., & Bassett, D. S. (2020). The extent and drivers of gender imbalance in neuroscience reference lists. *Nature Neuroscience, 23*(8), 918–926. https://doi.org/10.1038/s41593-020-0658-y
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/IFQXIEB4)
- **DOI or URL:** https://doi.org/10.1038/s41593-020-0658-y
- **Reviewed:** 2026-07-20
- **Reading basis:** Full published article, pp. 918–926 and online Methods, plus the official Supplementary Information, pp. 1–15

## Why this source matters

Dworkin et al. measure gender imbalance in the act of selecting references,
rather than inferring citation behavior from authors' accumulated citation
counts. Within five high-Eigenfactor neuroscience journals, they compare the
observed gender composition of reference lists with two expected-composition
baselines and then examine whether imbalance varies with the gendered-name
category of the citing team.

The study also tests one candidate mechanism: the gender composition of local
co-authorship networks. Those network measures are associated with only part
of the link between citing-team category and overcitation of papers with
men as both first and last author. The residual is compatible with several
individual and systemic explanations; it does not identify conscious or
implicit bias as the cause.

## Research question and framing

- **Question or aim:** Determine whether neuroscience reference lists contain
  fewer women-led papers than expected from the available literature and
  relevant paper characteristics; whether the imbalance is larger in men-led
  reference lists; how it changes over time; and whether local co-authorship
  networks partly account for citing-team differences (pp. 918–919).
- **Conceptual framing:** Citations are treated as acts of scholarly engagement
  that can influence perceived centrality, visibility, and career rewards. The
  authors distinguish being the object of undercitation from being an agent
  whose reference choices reproduce it, and discuss Matilda-effect, systemic,
  individual, network-homophily, upstream-exposure, and awareness mechanisms
  (pp. 918, 923–925).
- **Contribution claimed:** The paper introduces a graph-preserving expected-
  citation model for four first-/last-author gendered-name categories and shows
  that reference-list imbalance is concentrated in men-led teams, grows as the
  sampled field diversifies, and is only partly associated with local
  co-authorship-network composition (pp. 919–925).

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | A citation from a 2009–2018 citing article to an earlier article in the sampled journal corpus; article-level reference lists and first-/last-author teams are used for subgroup and network analyses (pp. 919–924; Methods). |
| Data source | Web of Science records, supplemented with Crossref and journal pages for missing given names; the analysis matches cited and citing papers by DOI (Methods). |
| Sample and coverage | 61,416 articles, reviews, and proceedings papers published in *Brain*, *Journal of Neuroscience*, *Nature Neuroscience*, *NeuroImage*, and *Neuron* from 1995–2018. Gendered-name categories were assigned to both first and last authors for 88% of papers; the main overall model uses 303,886 citations, while citing-team comparisons use 277,030 citations (pp. 919–920; Fig. 3; Reporting Summary). |
| Time period | Potential cited papers: 1995–2018. Reference-list behavior: citing papers published 2009–2018. Data were collected 3–11 February 2019 (p. 919; Methods; Reporting Summary). |
| Geographic or linguistic scope | Not bounded by study site or language, but the corpus is restricted to five Web of Science-indexed, high-Eigenfactor neuroscience journals. Name-gender assignment uses US Social Security data first and Gender API for names not resolved there (Methods). |

## Methods

- **Design:** Quantitative cross-sectional bibliometric study with temporal
  trend analysis and a temporal co-authorship-network model (Reporting
  Summary).
- **Measures or classifications:** Papers are classified by probabilistically
  inferred first- and last-author gendered names as MM, WM, MW, or WW. The main
  expected-composition model is a multinomial generalized additive model (GAM)
  using publication month/year, journal, team size, review status, and combined
  first-/last-author seniority. Citation imbalance is the percentage difference
  between observed and expected category shares. Two time-indexed network
  measures capture local overrepresentation of men authors and MM papers
  (pp. 919–924; Methods).
- **Analysis:** The authors compare observed citations with (1) the gender
  composition of all earlier papers in the sampled corpus and (2) GAM-estimated
  gender composition among papers with similar modeled characteristics. They
  bootstrap citing papers for confidence intervals, use 10,000 gender-category
  randomizations in a citation-graph-preserving null model for P values, apply
  Holm–Bonferroni correction, and use weighted median quantile regression for
  the network analysis (pp. 919–924; Methods; Supplementary Fig. 3 and Table
  S10).
- **Validation or robustness:** The paper validates automated gendered-name
  assignment against 200 manually assessed authors; imputes the 12% missing
  cases under a conservative null; varies self-citation definitions, reference-
  list weighting, GAM specification, and quantile versus linear regression;
  checks subfield classifications in a *Journal of Neuroscience* subset; and
  separates highly and less-cited papers and more- and less-productive teams
  (Methods; Supplementary Text, Figs. S1–S6, Tables S1–S11).

## Findings

### The expected-citation baseline materially changes the estimated magnitude

- **Source claim:** The sampled reference lists contain more MM papers and fewer
  women-led papers than expected under both a simple literature-composition
  baseline and a baseline conditioned on selected paper characteristics.
- **Evidence:** Against the full earlier-paper pool, MM papers were cited 11.6%
  more than expected and WW papers 30.2% less. After conditioning on publication
  date, journal, team size, review status, and author seniority, the estimates
  fell to +5.2% for MM, -6.7% for WM, -4.6% for MW, and -13.9% for WW. Under the
  graph-preserving null, MM, WM, and WW differed from expectation, while the MW
  estimate did not (P = 0.86) (pp. 919–920; Fig. 2).
- **Locator:** Results, “Citation imbalance relative to overall authorship
  proportions” and “Citation imbalance after accounting for relevant
  characteristics of papers,” pp. 919–920; Fig. 2.
- **Caveat:** The adjusted baseline substantially reduces the apparent gap and
  is conditional only on included covariates. It does not match papers on topic,
  citation relevance, methods, quality, institutional prestige, or all
  subfields. The result is therefore model-relative evidence of imbalance, not
  a gender-only causal effect.

### Imbalance is concentrated in reference lists from men-led teams

- **Source claim:** Undercitation of women-led work is greater in reference
  lists whose first and last authors are both classified as men.
- **Evidence:** MM reference lists cited MM papers 8.0% more than expected and
  WM, MW, and WW papers 9.3%, 9.0%, and 23.4% less than expected. Reference
  lists with a woman in at least one primary authorship position cited the same
  categories +2.5%, -4.6%, -0.1%, and -4.2% relative to expectation. The four
  between-group differences were significant under the graph-preserving null
  (P < 0.0001) (pp. 920–921; Fig. 3).
- **Locator:** Results, “The effect of author gender on citation behavior,” pp.
  920–921; Fig. 3.
- **Caveat:** The grouping associates citing-team gendered-name composition
  with reference-list composition; it does not observe who selected each
  reference, authors' self-identified gender, awareness of cited-author gender,
  or evaluative intent.

### The growing gap reflects stable observed choices against a diversifying baseline

- **Source claim:** Reference lists became increasingly unrepresentative of the
  sampled literature as the first-/last-author composition of that literature
  diversified.
- **Evidence:** The absolute observed-minus-expected share of MM citations grew
  by about 0.41 percentage points per year overall. The increase was 0.54 points
  per year in MM reference lists and 0.29 points in reference lists with a woman
  in at least one primary authorship position. Observed MM citation shares were
  relatively stable while their expected share declined (pp. 921–923; Fig. 4).
- **Locator:** Results, “Temporal trends of citation imbalance,” pp. 921–923;
  Fig. 4.
- **Caveat:** The trend is a widening mismatch relative to a time-varying
  expectation. It should not be paraphrased simply as researchers actively
  citing fewer women each year; the observed MM share was mostly stable.

### Local co-authorship networks are associated with part of the citing-team difference

- **Source claim:** Gendered local network composition is associated with MM
  overcitation but does not fully account for it.
- **Evidence:** A one-percentage-point increase in local MM-paper
  overrepresentation was associated with a 0.24-point increase in median MM
  overcitation; the corresponding association for man-author
  overrepresentation was 0.09 points. Median MM-team overcitation fell from
  about 5.5 percentage points unadjusted to 3.5 points when model estimates were
  conditioned on locally gender-balanced networks. The authors summarize this
  as roughly one-third of MM overcitation associated with network imbalance
  and two-thirds remaining (pp. 922–924; Figs. 5–6).
- **Locator:** Results, “The relationship between social networks and citation
  behavior,” pp. 921–924; Figs. 5–6; Supplementary Table S11.
- **Caveat:** This is not a causal mediation analysis. The constructed network
  includes only earlier co-authorships visible in the five-journal corpus and
  only its first/last authors; it omits reading, mentoring, conference,
  institutional, search, and topic networks. The residual is not a direct
  estimate of individual bias.

### Main patterns survive the reported sensitivity checks

- **Source claim:** Missing gendered-name classifications, self-citation rules,
  reference-list weighting, GAM specification, subfield, citation concentration,
  productivity, and regression choice do not account for the central pattern.
- **Evidence:** Conservative null imputation for missing cases produced similar
  estimates; broader self-citation exclusions were nearly unchanged; unweighted
  article-level results retained the main direction; a more complex GAM gave
  similar estimates; the *Journal of Neuroscience* subfield check changed little;
  high- and low-citation strata showed comparable directions; and linear models
  attenuated but did not reverse the network findings (Supplementary Text, Figs.
  S1–S6, Tables S3–S11).
- **Locator:** Supplementary Information, pp. 2–15.
- **Caveat:** These checks probe specified alternatives within the same five-
  journal, DOI-matched observational corpus. They do not validate the expected-
  citation model against judgments of substantive relevance or paper quality.

## Limitations

### Source-reported limitations

- Restricting the study to five high-Eigenfactor journals reduces variation in
  journal prestige but limits generalization to neuroscience as a whole (p.
  925).
- Binary, probabilistic gendered-name assignments do not identify authors'
  actual gender and do not accommodate intersex, transgender, or nonbinary
  identities (p. 925; Methods).
- The study investigates only gender; it does not test race, class, sexuality,
  disability, citizenship, or their intersections (p. 925).
### Reviewer assessment

- The observable citation system is narrower than “neuroscience citations” in
  general: eligible cited and citing works must be DOI-matched articles in the
  same five-journal corpus. Citations to books, other journals, non-DOI work,
  and work outside the 1995–2018 window are not part of the modeled outcome.
- Institutional prestige is not modeled, so gendered hiring patterns combined
  with prestige-based citation could affect estimates.
- Expected citation is not deserved citation. The GAM asks what gendered-name
  composition would be expected among papers similar on five recorded
  characteristics, not which works were substantively relevant or of equal
  scientific quality. Unmeasured topic and quality differences remain live
  counter-explanations, although one-journal subfield and citation-stratum checks
  reduce some narrower versions of those concerns.
- Citing-team composition, local network composition, and citation selection are
  distinct variables. The observational associations cannot separate implicit
  or explicit bias, upstream exposure through syllabi or conferences, topical
  specialization, deliberate corrective searching by women-led teams, prestige,
  or other search and attention processes.
- The main text reports 54,225 fully classified papers, whereas the
  Supplementary Information reports 54,226. This one-record discrepancy does
  not plausibly affect the estimates but should be preserved rather than silently
  harmonized (p. 919; Supplementary Information, p. 2).
- Bootstrap confidence intervals and graph-randomization P values answer
  different inferential questions; the MW adjusted estimate, for example, has a
  bootstrap interval below zero but P = 0.86 under the graph-preserving null.
  Later reuse should report the paper's stated inferential procedure rather than
  infer significance from the interval alone (p. 920; Methods).
- Under the Academic Research Suite hierarchy, this is Level IV observational
  evidence and overall Grade B for the descriptive pattern within the sampled
  journals: the corpus is large, methods and code are documented, and robustness
  checks are extensive. It is not causal evidence that individual or systemic
  bias produced the residual imbalance.
- DOI, title, authors, venue, date, volume, issue, and pages matched the published
  PDF, Crossref, PubMed, OpenAlex, and Zotero records on 2026-07-20. No competing
  interests were declared, and no retraction or correction alert surfaced in the
  verification checks.

## Project relevance

- **Source supports:** Article-level evidence that reference-list composition in
  a bounded neuroscience corpus differs from both raw and covariate-adjusted
  gendered-name expectations; that the difference is larger for MM citing teams;
  and that local co-authorship-network composition is associated with only part
  of that
  association.
- **Project interpretation:** Later synthesis can treat citation selection as a
  visibility mechanism distinct from index discoverability, publication output,
  per-paper citation reception, and career-total citations. The two expected-
  composition baselines also show why a visibility gap must be defined relative
  to an explicit eligible-source model rather than raw workforce shares.
- **Does not establish:** A universal neuroscience or science-wide citation
  penalty; author intent; the scientific quality or relevance of omitted works;
  a causal effect of author gender; the size of implicit or explicit bias; career-
  total citation disadvantage; or effects on hiring, funding, promotion, or
  journal inclusion. It does not grant this note or later exploratory analysis
  Paper Analysis authority.

## Literature-review connections

- **Themes:** Citation selection; gendered scholarly visibility; Matilda effect;
  expected-citation baselines; citing-team composition; network homophily;
  upstream exposure; systemic and individual bias; visibility versus quality.
- **Agreements or tensions:** The study supplies a direct article-level selection
  mechanism for uneven visibility, but its own baseline sensitivity and network
  results resist a single-cause account. It should be paired with evidence that
  distinguishes reference-list selection, per-paper reception, publication
  output, and career-total citations rather than treating all “gender citation
  gaps” as the same outcome.

| Follow-up source | Why follow it | Role |
|---|---|---|
| Dion, Sumner, and Mitchell (2018), “Gendered citation patterns across political science and social science methodology fields” | Provides the reference-list modeling approach on which the focal paper builds and a cross-field comparison for citing-team differences. | Method and evidence |
| Holman and Morandin (2019), “Researchers collaborate with same-gendered colleagues more often than expected across the life sciences” | Tests the collaboration-homophily premise used to motivate the local-network mechanism. | Supporting evidence |
| Wu (2024), “The gender citation gap: Approaches, explanations, and implications” | Distinguishes per-paper, per-author, reference-ratio, and career-output explanations needed to prevent denominator drift when synthesizing the focal result. | Tension and review lead |

## Open questions

- Do the adjusted reference-list patterns replicate in specialized neuroscience
  journals and when candidate citations include the wider neuroscience
  literature rather than only five high-Eigenfactor journals?
- How do estimates change when matching on topic, semantic relevance,
  institutional prestige, methods, and measures of paper quality?
- Can longitudinal within-author or quasi-experimental designs distinguish
  network exposure, team composition, deliberate corrective searching, and
  evaluator bias?
- How should expected citation composition be defined when historical
  underrepresentation affects both the candidate pool and the features used for
  matching?
- Do patterns persist for self-identified gender and at intersections with race,
  class, disability, sexuality, citizenship, geography, and language?
