# Traag et al. (2025) — Replication of funding Matthew effects

- **Citation:** Traag, V. A., Brady, E., Vincent-Lamarre, P., Bidel, F., Lopes-Bento, C., Andersen, J. P., & Bloch, C. (2025). The Matthew effect and early-career setbacks in research funding—a replication study. *eLife, 14*, RP109042. https://doi.org/10.7554/eLife.109042.1
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/9QSVE7KL)
- **DOI or URL:** https://doi.org/10.7554/eLife.109042
- **Reviewed:** 2026-07-20
- **Reading basis:** Full 45-page eLife Reviewed Preprint v1, including the Methods, supplementary data and results, and public peer reviews; version dated 2025-10-13 and marked “Not revised”

## Why this source matters

Traag et al. test two findings from earlier threshold studies using 109,624
applications from 14 programmes and six funders. For the funding Matthew effect,
the paper reproduces the near-threshold comparison used by Bol et al. and adds a
whole-population Bayesian model that separates later application from later
review scores.

The result changes the mechanism emphasis. Prior funding consistently predicts
another application, while a positive review-score effect does not survive the
paper's sensitivity analyses. The evidence therefore supports an application-
side cumulative process more clearly than an evaluator-status mechanism. It
still does not show why funded applicants return more often or establish a
universal causal effect outside the threshold comparison.

## Research question and framing

- **Question or aim:** Test whether the funding Matthew effect reported by Bol
  et al. (2018) and the early-career setback effect reported by Wang et al.
  (2019) replicate across funders, remain robust under different assumptions,
  and generalize from near-threshold applicants to the full applicant
  population (Introduction, pp. 2–3).
- **Conceptual framing:** The source treats cumulative funding advantage as the
  combined result of an application process and a review process. It also
  reframes the apparent citation advantage among rejected applicants who later
  reapply as possible selection on a collider rather than evidence that
  rejection improves their research (Introduction, pp. 2–3; Results, pp. 6–9).
- **Contribution claimed:** Harmonized data from diverse funding systems allow
  the authors to reproduce local near-hit/miss comparisons, model the full
  application population with a latent-quality Bayesian model, and compare the
  two effects within one analytical framework (Introduction, pp. 2–3; Methods,
  pp. 12–15).

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | Early- and later-career funding applications and applicants observed within the same funder. Outcomes are later application, later award receipt, later review score, and Mean Field Citation Rate (MFCR) in four career periods (pp. 3–8, 10–15). |
| Data source | Application and review records held by six funders, linked by name and affiliation to Dimensions publication data using a common extraction script. The Bayesian analyses used RoRI's Funder Data Platform and Leiden University's ALICE cluster (Methods, p. 12). |
| Sample and coverage | 109,624 funded and unfunded applications across 14 programmes; 40,369 early-career application records enter the pooled descriptive later-funding and citation comparisons, and 1,699 enter the pooled near-hit/miss comparison (Introduction, p. 2; Figures 3–4, pp. 5 and 7; Table S1, p. 17). Applicant matching to Dimensions was 96% overall, 97% for funded and 95% for unfunded applicants (Methods, p. 12). |
| Time period | Programme-specific windows range from 1992 to 2024. Coverage differs by funder and programme rather than forming one common observation window (Appendix A, pp. 16 and 20–21; Tables S1–S2, pp. 17–18). |
| Geographic or linguistic scope | Six funders headquartered in Canada, Luxembourg, Austria, and the United Kingdom: CIHR, SSHRC, Health Research BC, FNR, FWF, and Wellcome Trust. The authors frame the study as North American and European; Wellcome also funds applicants in Ireland and low- and middle-income countries. Language is not reported (Methods, p. 12; Appendix A, pp. 16 and 20–21). |

## Methods

- **Design:** A near-hit/miss comparison identifies the five funded and five
  unfunded applications closest to a model-estimated funding threshold within
  each call. Because most programmes lack a hard score cutoff, this is a fuzzy
  analogue of regression discontinuity rather than an exact replication of
  Bol et al.'s sharp design (Methods, pp. 12–13).
- **Measures or classifications:** Later funding is any later-career award at
  the same funder. The model separates the rate of another application from the
  review score on that application. Publication impact is Dimensions MFCR for
  pre-application, between-application, post-early, and post-later periods;
  “quality” is a latent variable inferred only from review scores and MFCR
  (Figures 1–2, p. 4; Methods, pp. 12–15).
- **Analysis:** The authors report pooled and funder-specific near-hit/miss
  contrasts, then fit hierarchical Bayesian models of funding, review scores,
  citations, and time to another application. The models include field and
  affiliation effects, right censoring, and imputed missing review and citation
  data (Methods, pp. 13–15).
- **Validation or robustness:** Near-threshold groups are compared on age, PhD
  year, prior publications, and prior MFCR. Sensitivity analyses vary how
  strongly latent quality is assumed to relate to citations and review scores,
  repeat models by funder, restrict early applications to before 2015, test a
  10-year citation interval, apply Wang et al.'s conservative-removal method,
  and simulate reapplication selection (Results, pp. 5–9; Appendix B, pp.
  22–37).

## Findings

### The threshold-local funding effect replicates, but is smaller than the raw population gap

- **Source claim:** Applicants who narrowly received early-career funding were
  more likely to obtain later-career funding than narrowly rejected applicants,
  reproducing the direction of Bol et al.'s Matthew effect (Results, pp. 3–5).
- **Evidence:** In the full descriptive comparison, later funding was 26% among
  initially funded applicants and 15% among initially unfunded applicants. Near
  the estimated threshold, the corresponding rates were 20% and 18% (*p* =
  .087, *n* = 1,699). The authors estimate a local causal effect of about three
  percentage points and attribute most of the raw 11-point gap to confounding
  differences (Results, p. 3; Figure 3, p. 5).
- **Locator:** Results, “Matthew effect,” pp. 3–5; Figure 3.
- **Caveat:** The pooled near-threshold contrast is imprecise, and the fuzzy
  threshold requires stronger assumptions than Bol et al.'s sharp cutoff. The
  result identifies a local bundled funding effect, not a population-wide
  status effect.

### Whole-population generalization is model-based rather than design-identified

- **Source claim:** The Matthew effect remains positive across the full
  applicant population after accounting for inferred quality and is robust to
  most funder and parameter specifications (Results, pp. 5–6; Discussion, p.
  8).
- **Evidence:** For an applicant at average inferred quality, the modeled
  probability of another application within five years was 0.36 ± 0.007 after
  funding and 0.29 ± 0.006 after rejection. The application coefficient was
  positive across the sensitivity grid and across funders except Health
  Research BC (Results, pp. 5–6; Figure S9, p. 28). The full-sample 26% versus
  15% award contrast supplies descriptive scale, not a causal estimate.
- **Locator:** Results, “Matthew effect,” pp. 5–6; Discussion, pp. 8–10;
  Appendix B.1, pp. 22–23; Figure S9, p. 28.
- **Caveat:** Far from the threshold, the causal interpretation depends on the
  latent-quality model, which represents quality using review scores and
  citation impact only. Unmeasured merit, programme fit, institutional support,
  resources, mobility, and career exit can still affect both reapplication and
  later success.

### Reapplication, not better review scores, is the most robust measured pathway

- **Source claim:** The replicated Matthew effect is mainly driven by funded
  applicants applying again more often, not by their later proposals receiving
  higher review scores (Results, pp. 5–6; Discussion, pp. 8–9).
- **Evidence:** Prior funding had a consistently positive modeled effect on the
  application rate (theta = 0.26 ± 0.0045). Its modeled effect on later review
  scores was slightly negative in the main specification (lambda = -0.058 ±
  0.0016) and changed direction across assumptions and funders (Figure 3, p. 5;
  Appendix B.1, pp. 22–23; Figures S9–S10, p. 28).
- **Locator:** Figure 3, p. 5; Results, pp. 5–6; Appendix B.1, pp. 22–23;
  Figures S9–S10.
- **Caveat:** The paper models whether and when another application appears; it
  does not observe confidence, discouragement, mentoring, institutional
  retention, grant-writing support, or alternative funding applications. It
  therefore identifies an application pathway, not the behavioral or resource
  mechanism that produces it, and it does not formally decompose a mediated
  share of later awards.

### The apparent early-career setback is consistent with reapplicant selection

- **Source claim:** Higher between-application citation impact among rejected
  applicants who later reapply can arise because reapplication conditions on a
  collider, not because rejection causally strengthens researchers (Results,
  pp. 6–9).
- **Evidence:** In the pooled near-hit/miss sample, between-application MFCR was
  6.35 for unfunded applicants and 3.90 for funded applicants, while pre-
  application and other-period differences were small or reversed (Figure 4,
  p. 7; Table S9, p. 32). The Bayesian funding-to-MFCR estimate changed sign
  under different quality assumptions, the 10-year analysis found no setback
  effect for any funder, and a simulation reproduced the pattern when only
  high-MFCR rejected applicants returned (Results, pp. 6–9; Methods, pp. 13 and
  15; Figure 5, p. 9).
- **Locator:** Results, “Early-career setback,” pp. 6–9; Figure 4, p. 7;
  Figure 5, p. 9; Appendix B.2, pp. 23–24.
- **Caveat:** Collider bias is a plausible explanation demonstrated by a
  simulation, not directly observed in individual publication and application
  trajectories. The source's aggregated citation data cannot establish which
  rejected applicants selected which later opportunities or why.

### Funding-system context changes the magnitude and sometimes the direction

- **Source claim:** The overall application-side Matthew effect is robust, but
  its visible size and the setback pattern vary with funder and programme
  context (Discussion, pp. 9–10; Appendix B, pp. 22–24).
- **Evidence:** Health Research BC's modeled application effect was close to
  zero. CIHR's near-threshold later-funding rates ran 38% for funded versus 50%
  for unfunded applicants, while FNR's ran 46% versus 14%; most funder-specific
  differences were not statistically clear. The setback pattern was strongest
  for FWF and weak or absent for Health Research BC and SSHRC (Appendix B.1–B.2,
  pp. 22–24).
- **Locator:** Discussion, pp. 9–10; Appendix B.1–B.2, pp. 22–24; Figures
  S6–S15, pp. 25–37.
- **Caveat:** Explanations involving CIHR bridge funding, FNR's encouragement
  of follow-up applications, review design, national career structures, or
  academic culture are post hoc boundary hypotheses. The study does not test
  those institutional features as moderators.

## Limitations

### Source-reported limitations

- The data cover participating funders rather than each applicant's complete
  funding portfolio, and applicants are not linked across funders. A rejected
  applicant who moves country or applies elsewhere may therefore appear as a
  non-reapplicant, potentially inflating the same-funder Matthew effect
  (Limitations, pp. 10–11).
- Most programmes lack an exact cutoff. The fuzzy threshold may retain
  confounders that affect both current and later decisions, even though the
  observed near-hit/miss covariates are similar (Limitations, p. 11; Figure S5,
  p. 23).
- Latent quality is unobserved and inferred only from review scores and MFCR.
  Other relevant dimensions of applicant or proposal quality may be omitted
  (Limitations, p. 11).
- Missing review scores and publication metrics are imputed. Dimensions
  matching is slightly lower for unfunded applicants, and MFCR uses citations
  accumulated through data collection rather than period-specific citation
  windows (Methods, p. 12; Limitations, p. 11).
- Privacy restrictions limited shared bibliometric data to applicant-level
  averages and totals. The study cannot inspect selection or citation change at
  the level of individual publications (Methods, p. 12; Limitations, p. 11).
- The source cannot determine why application rates differ. Confidence,
  institutional support, continued academic employment, and opportunity choice
  remain proposed mechanisms requiring individual longitudinal and qualitative
  evidence (Discussion and Future research, pp. 9 and 11–12).

### Reviewer assessment

- Under the Academic Research Suite hierarchy, the fuzzy near-hit/miss design
  is Level III quasi-experimental evidence and overall Grade A for the bounded
  threshold-local bundled funding effect. The same-funder whole-population
  generalization and specific behavioral mechanisms remain Grade B because
  they depend on latent-quality assumptions and incomplete career trajectories.
- “Replicates across funders” should not be read as 14 independently
  significant threshold effects. Several funder-specific contrasts are
  imprecise or reverse direction; the strongest cross-context evidence is the
  hierarchical application coefficient's robustness, not uniform raw effects.
- The source weakens a pure evaluator-status reading of Bol et al. because it
  finds no robust positive effect on later review scores. It does not rule out
  status, resource-enabled proposal quality, institutional support, or career
  retention operating before a later application is submitted.
- Generalization beyond the grey zone is not a second randomized or
  discontinuity result. It is an inference from a model whose latent quality
  distribution and citation/review relationships are deliberately varied but
  cannot be empirically identified with certainty.
- The early-career setback selection account is an inference to the best
  explanation, not a measured causal pathway. The five-year pattern is absent
  at ten years and appears especially concentrated in FWF; the public reviewers
  also requested clearer treatment of those boundaries (Methods, p. 13;
  Appendix B.2, pp. 23–24; public reviews, pp. 42–45).
- The paper is an eLife Reviewed Preprint v1 with a public assessment of
  “convincing” evidence, not a revised Version of Record. RoRI is funded by a
  consortium that includes several funders studied, and coauthors are affiliated
  with CIHR and FNR. These relationships are disclosed in the affiliations and
  acknowledgements and are relevant to interpretation, though they do not by
  themselves invalidate the analysis (pp. 38–41).

## Project relevance

- **Source supports:** A replicated, moderate, application-side cumulative
  advantage in repeated grant competition; a threshold-local funding effect
  across a wider set of systems than Bol et al.; and the need to distinguish
  later application, review score, award receipt, and citation impact as
  separate outcomes.
- **Project interpretation:** Uneven scholarly recognition can be amplified
  when an early decision changes who remains visible to the same gatekeeper by
  returning to compete. This mechanism need not begin with later reviewers
  rewarding prestige: participation, retention, and opportunity selection can
  generate cumulative inequality before a new proposal is evaluated.
- **Does not establish:** A universal causal effect for all applicants or
  funders; a status halo in review; the psychological reason for reapplication;
  the causal effect of funding on citation impact; complete career exit;
  disadvantage across an applicant's full funding ecosystem; or transfer to
  journal publication, citation selection, index coverage, policy use, or other
  scholarly-visibility outcomes. It does not grant this note or the corpus Paper
  Analysis authority.

## Literature-review connections

- **Themes:** Matthew effect; cumulative funding advantage; early-career
  setbacks; reapplication; applicant selection; collider bias; grant peer
  review; latent quality; institutional support; career retention; funding-
  system boundary conditions.
- **Agreements or tensions:** The source reproduces Bol et al.'s local effect
  direction and strengthens its cross-system relevance, but changes the leading
  mechanism from a bundled status/resource interpretation to an application-
  side process. It also challenges the causal “setbacks improve researchers”
  interpretation by showing how selective reapplication can generate the same
  citation pattern.

| Follow-up source | Why follow it | Role |
|---|---|---|
| Bol, T., de Vaan, M., & van de Rijt, A. (2018). “The Matthew effect in science funding.” | Supplies the sharp Dutch threshold result that Traag et al. replicate and reinterpret. | Framing, evidence, and tension |
| Wang, Y., Jones, B. F., Wang, D. (2019). “Early-career setback and future career impact.” | Supplies the original setback finding and conservative-removal strategy challenged by the collider account. | Tension and method |
| Jacob, B. A., & Lefgren, L. (2011). “The impact of research grant funding on scientific productivity.” | Tests grant effects on later output in a different funding system and outcome frame. | Evidence and tension |
| Ghirelli, C., Havari, E., Meroni, E. C., & Verzillo, S. (2023). “The long-term causal effects of winning an ERC grant.” | Offers a separate European causal design for longer-term grant and career outcomes. | Supporting evidence and method |
| Woods, H. B., & Wilsdon, J. (2022). “Experiments with randomisation in research funding.” | Develops the funding-lottery policy route raised for grey-zone decisions. | Policy and method |

## Open questions

- Does the application-side effect persist when applicants are linked across
  funders, countries, institutions, and non-grant sources of support?
- Which pathways—confidence, feedback, grant-writing help, protected time,
  institutional retention, mobility, or opportunity choice—cause funded and
  rejected applicants to reapply at different rates?
- Do bridge grants, targeted feedback, mentorship, or randomized encouragement
  causally increase reapplication and later success among strong rejected
  applicants?
- How do the whole-population results change with individual publication
  histories, preregistered quality measures, exact funding cutoffs, and longer
  common observation windows?

## Review provenance

AI-assisted research tools supported DOI verification, source retrieval,
full-text extraction, and structured review. AnySearch's academic DOI and
Crossref-backed metadata matched the live eLife record. Zotero parent item
`9QSVE7KL` and attachment `KIUU5C5N` were created from that record; the attached
PDF's SHA-256 matches the 45-page PDF downloaded from eLife. The canonical DOI
resolves to the versioned Reviewed Preprint DOI `10.7554/eLife.109042.1`, which
is dated 2025-10-13 and marked “Not revised.” Semantic Scholar did not resolve
either DOI at review time; the source was retained because Crossref, eLife, the
full public text, and byte-identical Zotero attachment independently establish
its identity.
