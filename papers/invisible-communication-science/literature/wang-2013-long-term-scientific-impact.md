# Wang et al. (2013) — Long-term scientific impact

- **Citation:** Wang, D., Song, C., & Barabási, A.-L. (2013). Quantifying long-term scientific impact. *Science, 342*(6154), 127–132. https://doi.org/10.1126/science.1237825
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/G2ZV9VYT)
- **DOI or URL:** https://doi.org/10.1126/science.1237825
- **Reviewed:** 2026-07-20
- **Reading basis:** Full author manuscript and official supplementary materials, including Supplement sections S1–S4, Figures S1–S25, and Tables S1–S4

## Why this source matters

Wang et al. offer a non-discrete account of unequal citation trajectories: prior
citations raise the chance of further citations, papers differ in a latent
fitness inferred from community response, and attention decays with age. This
account belongs in the corpus as a competing explanation because large
differences can emerge without a single exclusion decision. Its fit to observed
citation histories does not, however, show that social or institutional
selection is absent; such processes can operate through the model's inputs and
latent parameters.

## Research question and framing

- **Question or aim:** Determine whether individual papers' long-run citation
  histories contain reproducible dynamics and whether a mechanistic model can
  estimate ultimate citation impact more reliably than journal impact factor or
  early citation counts (main text, pp. 127–132).
- **Conceptual framing:** Citation accumulation combines preferential
  attachment, time-dependent aging, and paper-specific fitness. Fitness is not
  an objective measure of intrinsic merit; the authors define it as a relative,
  collective measure of the research community's response (main text, Eqs.
  1–5; Supplement S2.1–S2.2, pp. 4–8).
- **Contribution claimed:** After paper-specific rescaling, citation histories
  from multiple journals and fields follow a common temporal curve. The fitted
  parameters separate ultimate impact, impact timing, and longevity and may
  support journal-independent long-term evaluation (main text, Figs. 1–4;
  Supplement S2.4–S4, pp. 11–29).

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | Individual papers and the time-stamped citation events or cumulative citation histories attached to them; journal-level analyses average paper histories (main text, pp. 127–132; Supplement S2 and S4). |
| Data source | American Physical Society Physical Review corpus and Thomson Reuters Web of Science (Supplement S1.1–S1.2, pp. 3–4). |
| Sample and coverage | Physical Review contains 463,348 papers across 11 journal series, with citations internal to that corpus (Table S1). Cross-field checks use articles and reviews published in 1990 by 11 prominent journals and one review journal; additional 1995 and 2000 cohorts and annual Cell and NEJM cohorts for 1995–2005 support supplementary analyses (Supplement S1.2, S4, and Table S4). |
| Time period | Supplement S1.1 describes the Physical Review data as 1893–2010, while the series in Table S1 end in 2009; the difference is not explained. Web of Science citation histories were collected through 2011, and the principal cross-journal cohort is 1990 (Supplement S1.1–S1.2 and Table S4). |
| Geographic or linguistic scope | Not reported. The study does not disaggregate papers or citations by country, language, institution, author identity, or scholarly community. |

## Methods

- **Design:** Longitudinal bibliometric analysis coupled to a stochastic,
  paper-level citation model. Model parameters are estimated separately for
  each paper and then used for within-sample fit, rescaling, model comparison,
  and future-citation prediction (main text, Eqs. 1–9; Supplement S2–S3).
- **Measures or classifications:** A paper's citation rate is proportional to
  its current citations plus initial attractiveness, relative fitness, and a
  lognormal aging function. The model assumes exponential growth in the paper
  population and fixes the typical reference count at `m = 30`. Paper-specific
  parameters are relative fitness (`lambda`), immediacy (`mu`), and longevity
  (`sigma`); system-wide terms include publication growth and normalization
  (Supplement S1.3, S2.1–S2.3, pp. 4–11).
- **Analysis:** Parameters are estimated through a non-homogeneous stochastic
  process and maximum likelihood. The fitted model implies that ultimate
  citations depend on fitness, while impact time is approximately `exp(mu)`.
  The authors compare rescaled histories, journal averages, weighted
  Kolmogorov–Smirnov (KS) fit, citation prediction envelopes, and alternative
  Logistic, Bass, Gompertz, and no-preferential-attachment Lognormal models
  (Supplement S2.2–S4.1, pp. 6–29).
- **Validation or robustness:** The authors report data collapse in Physical
  Review and 12 journals, a KS test of collapse, simulated-versus-observed
  histories, comparison with three equally parameterized diffusion models,
  5- and 10-year prediction windows, an analytic and empirical threshold for
  preferential attachment, and sensitivity of `lambda`—but not fitted or
  predicted citation histories—to the fixed `m` choice (main text, Figs. 1–4;
  Supplement S2.3–S3.4, pp. 9–25).

## Findings

### Preferential attachment, fitness, and aging can jointly separate citation trajectories

- **Source claim:** Unequal citation histories can be represented by three
  interacting mechanisms: accumulated citations increase subsequent visibility,
  a paper has a relative fitness reflecting community response, and its
  attractiveness decays over time (main text, pp. 129–130).
- **Evidence:** Attachment rates rise approximately linearly with accumulated
  citations; the time to the next citation at fixed prior citation counts is
  approximated by a lognormal distribution; and the combined model fits each
  paper with `lambda`, `mu`, and `sigma` (Supplement S2.1, Figs. S3–S4, pp.
  4–6, 37–38).
- **Locator:** Main text, Eqs. 1–5 and Fig. 1C–G; Supplement S2.1–S2.4 and
  Figs. S3–S8.
- **Caveat:** These components are a fitted generative account, not separately
  randomized causes. Fitness is latent and can absorb prestige, access,
  language, field, network position, author identity, or gatekeeping effects.

### Ultimate citation and citation timing are distinct model outcomes

- **Source claim:** Ultimate citation impact depends on relative fitness, while
  the characteristic impact time depends primarily on immediacy; early citation
  counts and journal impact factor therefore need not determine long-run
  citations (main text, pp. 130–131).
- **Evidence:** The model gives ultimate citations as a function of `lambda`
  and impact time as approximately `exp(mu)`. Papers from Cell, PNAS, and
  Physical Review B with similar fitted fitness converge in citation counts by
  year 20, whereas papers selected for the same year-two citations diverge
  (main text, Eqs. 6–7 and Fig. 2).
- **Locator:** Main text, Eqs. 6–7 and Fig. 2A–F; Supplement S2.2 and Figs.
  S2, S10–S11.
- **Caveat:** The outcome named “ultimate impact” is projected lifetime
  citations inside the observed citation system, not intrinsic scientific
  quality, discoverability, policy use, or community recognition.

### Preferential attachment matters most beyond the lowest-citation range

- **Source claim:** For papers with very low fitness, lognormal aging plus a
  single scale parameter is effectively indistinguishable from the full model;
  preferential attachment becomes consequential for higher-impact papers
  (main text, p. 132).
- **Evidence:** A Taylor expansion yields a theoretical boundary near
  `lambda < 0.25`, corresponding to fewer than about 8.5 ultimate citations.
  The Lognormal model tracks low-citation papers but increasingly
  underestimates medium- and high-citation histories (Supplement S3.4, pp.
  23–25; Fig. S20).
- **Locator:** Main text, Eq. 9; Supplement S3.4, Eqs. S44–S47 and Fig. S20.
- **Caveat:** The threshold is model-dependent, and the empirical comparison
  groups papers by realized 30-year citations. It does not identify why some
  papers enter the range where cumulative attention becomes stronger.

### The model fits diverse observed histories, subject to selective validation samples

- **Source claim:** Paper-specific rescaling collapses varied citation histories
  onto a common curve across disciplines and journals (main text, p. 130).
- **Evidence:** The primary collapse uses 7,775 Physical Review papers
  published from 1950 to 1980 that received more than 30 citations within 30
  years. Eighty-five percent have KS values below 0.1, and the null is not
  rejected at the 0.1 level for 97% of fits. The model also fits 1990 cohorts
  from 12 selected journals and outperforms Logistic, Bass, and Gompertz models
  on a weighted KS measure (main text, Figs. 1F and 4D; Supplement S2.4, S3.3,
  Figs. S5–S9 and S17–S19).
- **Locator:** Supplement S2.4, pp. 11–12; S3.3, pp. 21–23; Table S4.
- **Caveat:** Each paper receives three fitted parameters, and the collapse is
  mainly an in-sample fit. The Physical Review collapse excludes low-citation
  and shorter-history papers, while cross-field validation uses prominent,
  selectively indexed journals.

### The original long-horizon prediction claim is contested

- **Source claim:** With a five-year training history, the model's prediction
  envelope contained 93.5% of the selected Physical Review papers at year 30;
  prediction improved with longer training and outperformed three diffusion
  models (main text, pp. 131–132).
- **Evidence:** The test set contains 4,492 Physical Review papers from the
  1960s with at least 10 citations in their first five years. The source reports
  only 6.5% more than two model-estimated standard deviations from the
  year-30 prediction, better weighted KS fit, and less systematic
  underprediction than Logistic, Bass, and Gompertz models (main text, Fig. 4;
  Supplement S2.6 and S3.3).
- **Locator:** Main text, Fig. 4A–F; Supplement S2.6, pp. 15–17; S3.3, pp.
  21–23; Figs. S13–S19.
- **Caveat:** The uncertainty calculation omits stochastic-process fluctuation
  and evaluates coverage without penalizing wide envelopes (Supplement S2.6,
  p. 16). Wang, Mei, and Hicks (2014) found unstable extreme parameters and
  worse performance than a naive citation-count benchmark for five-year
  training. Wang, Song, Shen, and Barabási (2014) attributed those errors to
  overfitting and reported better results after a conjugate prior or uncertainty
  filter. The published exchange leaves the original unregularized policy-use
  claim contested.

## Limitations

### Source-reported limitations

- The Physical Review corpus covers physics and only citations internal to the
  corpus, systematically undercounting interdisciplinary citations. The authors
  therefore add Web of Science checks (Supplement S1.1, p. 3).
- Web of Science lacks exact pre-1985 publication dates, and the authors'
  institutional subscription covers a subset of Thomson Reuters sources. Their
  operational definition of citable items also differs from Journal Citation
  Reports (Supplement S1.2, p. 4; S4.1, pp. 27–28).
- The model cannot represent exogenous “second acts” or extreme delayed
  recognition caused by later developments, such as renewed attention to old
  work after a new field emerges (main text, p. 132).
- Citation-envelope uncertainty includes parameter-estimation uncertainty but
  neglects fluctuation from the stochastic citation process itself
  (Supplement S2.6, p. 16).

### Reviewer assessment

- **Evidence grade:** This is a large, peer-reviewed computational
  bibliometric study with strong longitudinal data and explicit model checks,
  but it remains a single observational modeling study. It is Grade B for
  describing and fitting within-corpus dynamics and Grade C for individual
  long-horizon prediction or policy evaluation because the latter is contested
  by the 2014 replication exchange.
- The model does not compare preferential attachment, fitness, and aging with
  measured social or institutional covariates. A good fit cannot identify these
  reduced-form components as exclusive causes or rule out discrimination,
  prestige signaling, network closure, strategic citation, resource inequality,
  editorial selection, or index admission.
- Treating no-citation papers as zero-fitness papers makes observed attention
  and latent fitness difficult to distinguish. A paper can receive no observed
  citations because it was undiscovered or outside the database, not because
  its scientific contribution had no fitness.
- The lognormal aging argument is based on citation timing after holding prior
  citations and publication cohort approximately fixed, but paper fitness is
  unknown before fitting. The authors acknowledge that aggregation mixes
  paper-specific aging distributions (Supplement S2.1, pp. 4–6).
- The validation datasets condition on publication in Physical Review or 12
  prominent Web of Science journals. They cannot test journals, languages,
  communities, or outputs missing from those sources, and the results should
  not be generalized to index admission or global scholarly visibility.
- The paper discloses support from Lockheed Martin, the U.S. Army Research
  Laboratory, DARPA, and the European Commission. No author financial interest
  in a citation-evaluation product is reported, but the funding context should
  remain visible when considering policy applications (Acknowledgements,
  author manuscript p. 11).

## Project relevance

- **Source supports:** A plausible system-dynamics account in which cumulative
  attention, heterogeneous community response, and time-dependent decay can
  produce strongly unequal citation trajectories without a discrete exclusion
  decision; the need to distinguish citation amount, citation timing, and
  projected lifetime citations; and the danger of treating early citations or
  journal averages as stable paper-level impact measures.
- **Project interpretation:** Later synthesis should retain this model as a
  competing explanation, not as a null model that erases exclusion. Its three
  mechanisms can coexist with institutional and social processes: prestige or
  database inclusion can seed preferential attachment, gatekeeping can shape
  observed fitness, and field or language structures can affect aging.
- **Does not establish:** That citation inequality is fair, meritocratic, or
  socially neutral; that preferential attachment, fitness, and aging exhaust
  the causes of citation trajectories; that excluded or nonindexed scholarship
  has zero fitness; that the original unregularized model is a reliable policy
  tool; or that citations measure discoverability, evaluation, policy use,
  professional uptake, or intrinsic scientific quality. It creates no Paper
  Analysis designation.

## Literature-review connections

- **Themes:** Cumulative advantage; preferential attachment; attention decay;
  latent fitness; delayed recognition; citation prediction; early- versus
  long-run visibility; journal effects; system dynamics as a competing
  explanation; index and unit-of-analysis boundaries.
- **Agreements or tensions:** The model gives a mechanism through which
  citation inequality can persist even without a discrete gatekeeper, but it
  does not contradict work on institutional or identity-conditioned exclusion
  because those processes can alter exposure, early citations, and inferred
  fitness. Its long-run prediction claim is directly challenged by Wang, Mei,
  and Hicks (2014) and partially defended through later regularization and
  uncertainty filtering by Wang, Song, Shen, and Barabási (2014).

| Follow-up source | Why follow it | Role |
|---|---|---|
| Wang, J., Mei, Y., & Hicks, D. (2014). “Comment on ‘Quantifying long-term scientific impact.’” | Replicates the prediction exercise, identifies extreme parameter estimates and wide-envelope problems, and benchmarks against observed early citations. | Tension |
| Wang, D., Song, C., Shen, H.-W., & Barabási, A.-L. (2014). “Response to Comment on ‘Quantifying long-term scientific impact.’” | Defends the regularity claim and reports regularized and uncertainty-filtered prediction results not present in the 2013 paper. | Tension and method |
| Eom, Y.-H., & Fortunato, S. (2011). “Characterizing and modeling citation dynamics.” | Supplies the prior empirical result used to corroborate the low-citation threshold below which initial attractiveness masks preferential attachment. | Supporting evidence |
| Bianconi, G., & Barabási, A.-L. (2001). “Competition and multiscaling in evolving networks.” | Provides the fitness-model foundation from which the paper adds aging and publication growth. | Framing |

## Open questions

- Can independent replications separate descriptive fit from out-of-sample
  prediction using preregistered baselines, regularization, and calibrated
  interval scores rather than envelope coverage alone?
- How much of inferred fitness and early preferential attachment is explained
  by journal, author, institution, language, country, network position, open
  access, or index inclusion?
- Do the same dynamics hold for books, humanities and social-science outputs,
  regional indexes, multilingual publishing, and journals outside selective
  citation databases?
- Can a model jointly represent endogenous cumulative attention and exogenous
  shocks, including delayed recognition, field formation, retraction,
  controversy, and policy events?

## Review provenance

AI-assisted research tools supported retrieval, text extraction, source
verification, and structured review. The bibliographic identity was verified
against Crossref, OpenAlex, Semantic Scholar, PubMed, and the DOI landing page.
The complete author manuscript in Zotero and the 67-page supplementary PDF
linked by the first author's publication page were read. The 2014 published
Comment and Response were checked to preserve the strongest documented
challenge to the original prediction claim.
