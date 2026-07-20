# Wang et al. (2017) — Bias against novelty

- **Citation:** Wang, J., Veugelers, R., & Stephan, P. (2017). Bias against novelty in science: A cautionary tale for users of bibliometric indicators. *Research Policy, 46*(8), 1416–1436. https://doi.org/10.1016/j.respol.2017.06.006
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/YYHMNKBW)
- **DOI or URL:** https://doi.org/10.1016/j.respol.2017.06.006
- **Reviewed:** 2026-07-20
- **Reading basis:** Full 55-page [accepted manuscript deposited by KU Leuven](https://lirias.kuleuven.be/1497410?limo=0); the manuscript identifies the published *Research Policy* citation and DOI. Bibliographic identity and the published abstract were cross-checked against Crossref, OpenAlex, AnySearch, and the KU Leuven repository record.

## Why this source matters

Wang et al. provide a direct content-and-timing explanation for uneven citation
recognition. Papers that make unprecedented combinations of referenced journals
have more variable citation outcomes and can look weak in short windows even
when their long-run citation probability is high, especially outside their home
fields.

The paper therefore warns against treating low early citation as evidence of low
long-run value. It does not, however, directly observe audience reluctance,
evaluator discrimination, or intrinsic paper quality. Its strongest evidence is
for a mismatch between a specific combinatorial-novelty measure and short-window
bibliometric indicators.

## Research question and framing

- **Question or aim:** Develop a paper-level measure of combinatorial novelty,
  compare novel and non-novel papers' citation profiles over time and across
  fields, and test whether short citation windows and Journal Impact Factor
  understate the later impact of measured novelty (pp. 3–4).
- **Conceptual framing:** Research is treated as recombination of existing
  knowledge components. Unprecedented and cognitively distant journal pairs in
  a paper's references operationalize exploration and novelty. The authors frame
  novel research as potentially “high risk/high gain” and offer two reasons for
  delay: resistance by incumbent paradigms and the time needed to recognize,
  diffuse, and incorporate unfamiliar work (pp. 2–7).
- **Contribution claimed:** The authors claim a novelty indicator distinct from
  general interdisciplinarity and show that measured novelty has higher outcome
  variance, greater long-run and cross-field citation upside, weaker early
  citation performance, and lower adjusted Journal Impact Factor (pp. 11–25).

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | A Web of Science research article, duplicated as an observation when assigned to multiple WoS subject categories (pp. 11–12). |
| Data source | Web of Science Core Collection publication, reference, journal, subject-category, citation, and Journal Impact Factor records (pp. 7–13). |
| Sample and coverage | 785,324 articles published in 2001; 661,910 cited at least two WoS journals. After removing 267 without subject categories, the analysis contains 661,643 unique publications and 1,038,238 field-category observations across 251 subject categories (p. 11). |
| Time period | Focal articles were published in 2001. Prior journal-pair history begins in 1980; distance uses 1998–2000 co-citation profiles; qualifying combinations must be reused in the next three years; citation outcomes run through 2015 (pp. 7–9, 13–21). |
| Geographic or linguistic scope | Not reported. Coverage is defined by WoS rather than a geographic or linguistic sampling frame, and the paper reports weaker database coverage for humanities and social sciences (pp. 21–22, Appendix III, pp. 49–50). |

## Methods

- **Design:** Retrospective observational bibliometric study of one publication
  cohort, using regression models for citation dispersion, citation classes,
  long-run top-citation status, cross-field reach, citation timing, and journal
  impact (pp. 7–21).
- **Measures or classifications:** A journal pair is new if it did not co-occur
  in references from 1980 through 2000. Its difficulty is `1 - cosine
  similarity` between the two journals' 1998–2000 co-citation profiles. A
  paper's novelty score sums difficulty over new pairs, after excluding the
  least-cited half of journals and requiring reuse within three years.
  Non-novel papers have no qualifying pair; highly novel papers are the top 1%
  within a subject category; other papers with qualifying pairs are moderately
  novel (Section 3.1, pp. 7–9; Section 4, pp. 11–12).
- **Analysis:** Generalized negative binomial models estimate citation means and
  dispersion. Multinomial and binary logit models estimate low-, high-, and top-
  citation outcomes; Poisson and OLS models estimate field breadth, foreign-field
  share and distance, and Journal Impact Factor. Main models include subject-
  category fixed effects and controls for references, authors, and international
  coauthorship. Citation-window models repeat top-1% estimation for each year
  from one through fifteen (Sections 5.1–5.5, pp. 13–20).
- **Validation or robustness:** The authors vary the novelty formula, journal
  exclusions, future-reuse condition, category threshold, continuous versus
  categorical scoring, multi-category treatment, and control for an atypicality
  measure. They also rerun models by broad field. Most findings persist, but
  dispersion, short-window disadvantage, and lower Journal Impact Factor are
  not all robust in arts, humanities, or social sciences; detailed robustness
  estimates are not reported and are available only from the authors (Section
  5.7, pp. 21–22; Appendix III, pp. 49–55).

## Findings

### Highly novel papers have higher citation variance in both tails

- **Source claim:** Highly, but not moderately, novel papers display a
  high-risk citation profile (pp. 13–14).
- **Evidence:** The generalized negative binomial model estimates 18% higher
  dispersion for highly novel than non-novel papers. In the multinomial model,
  their odds of landing in the top 10% rather than the middle 80% are 18%
  higher, while their odds of landing in the lowest 10% are 15% higher (Tables
  2–3, pp. 31–32).
- **Locator:** Section 5.1, pp. 13–14; Tables 2–3, pp. 31–32.
- **Caveat:** These are adjusted associations within an indexed 2001 cohort, not
  causal effects of novelty. Fifty subject categories with more than 10%
  uncited papers are dropped from the low-tail model under the primary coding,
  although the authors report a consistent random-assignment sensitivity check
  (Table 3 note, p. 32).

### Short windows reverse or hide the long-run association

- **Source claim:** Novel papers require longer citation windows before their
  relative citation advantage becomes visible (pp. 17–18).
- **Evidence:** For highly novel papers, logit coefficients for top-1% status
  are negative at one and two years, nonsignificant at three years, positive
  from year four, and rise to `0.45` at fifteen years. Moderately novel papers
  are negative through year four and become significantly positive only from
  year nine. At fifteen years, the adjusted odds of top-1% status are 57%
  higher for highly novel and 13% higher for moderately novel papers than for
  non-novel papers (Table 4, column 1; Table 5, pp. 33–34).
- **Locator:** Sections 5.2 and 5.4, pp. 14–18; Tables 4–5, pp. 33–34.
- **Caveat:** The changing coefficients establish a time-window interaction for
  this novelty classification. They do not identify whether early weakness is
  caused by cognitive resistance, slower knowledge use, journal placement,
  topic composition, or another unmeasured process.

### The delay combines home-field weakness with slower foreign-field diffusion

- **Source claim:** Novel work's long-run upside is disproportionately realized
  outside its home field, and diffusion beyond the home field takes time (pp.
  16–19).
- **Evidence:** At fifteen years, highly novel papers have no significant
  advantage in home-field top-1% status but have 95% higher adjusted odds of
  foreign-field top-1% status; the corresponding foreign-field advantage for
  moderately novel papers is 37%. Highly novel papers are disadvantaged in
  home-field top-1% status for the first seven years, while their foreign-field
  advantage becomes significant at year three and grows thereafter. Across all
  papers, average annual foreign-field citations remain below home-field
  citations for seven years before exceeding them (Table 4, columns 6–7;
  Appendix II Tables A4–A5 and Figures A1–A2, pp. 33, 44–49).
- **Locator:** Sections 5.3–5.4, pp. 16–19; Table 4, p. 33; Appendix II Tables
  A4–A5 and Figures A1–A2, pp. 44–49.
- **Caveat:** “Home” means sharing at least one WoS journal subject category;
  “foreign” means sharing none. This database classification does not observe
  readers' judgments, and broader or multi-category journals can blur cognitive
  and audience boundaries.

### Lower journal impact does not fully account for delayed recognition

- **Source claim:** Novel papers are placed in lower-impact journals than
  comparable non-novel papers, but journal placement does not explain the full
  citation delay (pp. 19–20).
- **Evidence:** With field and paper controls, Journal Impact Factor is about
  10% lower for moderately novel and 17% lower for highly novel papers. The
  association persists after controlling for journal age. Models interacting
  novelty with top-decile Journal Impact Factor still show delayed citation
  accumulation among novel papers in high-impact journals (Table 6, p. 35;
  Appendix II Table A6, pp. 46–47).
- **Locator:** Section 5.5, pp. 19–20; Table 6, p. 35; Appendix II Table A6,
  pp. 46–47.
- **Caveat:** The study does not observe submission choices, editorial strategy,
  peer-review decisions, or rejected manuscripts. Lower Journal Impact Factor
  therefore cannot be attributed specifically to gatekeeper bias rather than
  author selection, topic–journal fit, or other omitted differences.

### The measure is not interchangeable with interdisciplinarity or atypicality

- **Source claim:** New combinations are usually cross-disciplinary, but most
  cross-disciplinary combinations are not new; the proposed score also captures
  a different aspect of novelty from an atypicality measure (pp. 11–12,
  Appendix III).
- **Evidence:** About 96% of newly paired journals cross WoS category boundaries,
  but fewer than 8% of cross-disciplinary journal pairs are new. When novelty
  and atypicality enter the robustness models together, novelty retains its
  reported associations, while atypicality behaves inconsistently for short-term
  big hits and Journal Impact Factor (p. 12; Appendix III, pp. 53–55).
- **Locator:** Section 4, p. 12; Appendix III.3, pp. 53–55.
- **Caveat:** Both constructs are derived from journal-reference patterns and
  depend on WoS coverage. Neither directly measures semantic originality,
  cognitive difficulty for a reader, or ex ante research quality.

## Limitations

### Source-reported limitations

- The indicator captures only combinatorial novelty and treats referenced
  journals as bodies of knowledge; topic, keyword, text, bibliographic-coupling,
  and co-citation approaches could operationalize other forms of novelty
  (Discussion, p. 22).
- True paper quality is unobserved. The authors argue that simple low- or
  high-quality stories do not explain the entire trajectory, but explicitly
  state that they cannot rule out a relationship between novelty and quality
  (Section 5.6, pp. 20–21).
- Findings are less robust in arts, humanities, and social sciences, where WoS
  coverage and the number of observations are weaker. The source does not claim
  uniform field effects (Section 5.7, pp. 21–22; Appendix III.1, pp. 49–51).
- The paper leaves the mechanism behind lower-JIF placement unresolved: editors
  may anticipate short-term citations, peer review may be conservative, or
  authors may not submit novel work to high-impact journals (Discussion,
  pp. 22–23).
- The authors call for future research on critical moments and mechanisms in
  idea diffusion; the present study does not observe such triggers directly
  (Discussion, pp. 22–23).

### Reviewer assessment

- The central design is observational. Field fixed effects and controls for
  references, authors, and international collaboration reduce some confounding,
  but journal, topic, institution, author reputation, country, language, and
  prior-status differences remain possible. The evidence supports association
  and indicator sensitivity, not the causal claim that novelty itself produces
  delayed recognition.
- Requiring a “new” combination to be reused in the following three years uses
  future uptake to define the exposure (Section 3.1, p. 9). This ex post
  condition removes novel combinations that receive no near-term follow-up and
  can select on early survival. Robustness without the condition is reported but
  not shown, so its effect cannot be independently assessed from the article.
- The evidence does not distinguish audience reluctance from slower
  incorporation. The home/foreign split and time profile are consistent with
  both, and the paper itself presents both explanations. Treating paradigm
  resistance as demonstrated would be affirming the consequent.
- The analysis begins with WoS-indexed articles that cite at least two WoS
  journals and discards combinations involving the least-cited half of journals
  in the main measure. It cannot describe novel work outside selective indexes,
  work grounded in books or local journals, or combinations involving peripheral
  sources excluded by construction.
- Multi-category papers are duplicated in the main data. The authors report
  consistent alternative assignments, but the detailed estimates are not shown;
  the paper reports robust rather than publication-clustered standard errors.
- As an observational bibliometric cohort study, the source is Level IV in the
  ARS evidence hierarchy and overall Grade B for associational claims. It is not
  causal evidence of discrimination in peer review, funding, hiring, or citation
  choice.

## Project relevance

- **Source supports:** A measured association between combinatorial novelty and
  high-variance citation outcomes; direct evidence that short citation windows
  can reverse or conceal the later relative performance of that novelty class;
  and a decomposition showing that much of the long-run advantage is realized
  through slower cross-field citation.
- **Project interpretation:** Later synthesis can treat novelty and cognitive
  distance as a content-and-timing counter-explanation for low early visibility.
  The result cautions against reading weak short-run citation as low value and
  against assuming every uneven outcome reflects a discrete exclusion decision.
  It should remain separate from discoverability, index admission, evaluation,
  and non-academic use.
- **Does not establish:** That a particular low-cited paper is novel; that
  audience resistance rather than slow incorporation causes the delay; that
  bibliometric users actually made an unfair decision; that novelty explains
  OJS journal noncoverage; or that the relationships generalize outside WoS,
  across all disciplines, languages, countries, journals, authors, or
  communities. It does not grant this note or the corpus Paper Analysis
  authority.

## Literature-review connections

- **Themes:** Combinatorial novelty; cognitive distance; delayed recognition;
  high-risk/high-gain citation profiles; home- versus foreign-field uptake;
  short-window metric bias; content- and timing-based counter-explanations.
- **Agreements or tensions:** The source complements Larivière et al.'s
  article-level citation-dispersion countertrend: aggregate citation can spread
  more broadly while a measured content class has a delayed, high-variance
  trajectory. It does not test the selective-index admission mechanism in
  Khanna et al. and cannot show whether nonindexed work receives the same
  opportunity for delayed recognition.

| Follow-up source | Why follow it | Role |
|---|---|---|
| Wang, J., Thijs, B., & Glänzel, W. (2015). “Interdisciplinarity and impact: Distinct effects of variety, balance, and disparity.” | Separates dimensions of interdisciplinarity and their short- versus long-window citation associations; useful for testing whether the focal novelty effect is really cognitive disparity. | Method and tension |
| Boudreau, K. J., Guinan, E. C., Lakhani, K. R., & Riedl, C. (2016). “Looking across and looking beyond the knowledge frontier.” | Directly studies evaluator scores for proposals with greater intellectual distance, offering a closer test of audience reluctance than citation timing alone. | Supporting evidence and method |
| Foster, J. G., Rzhetsky, A., & Evans, J. A. (2015). “Tradition and innovation in scientists' research strategies.” | Examines strategic choice between traditional and innovative research and can test selection into novelty before publication. | Framing and tension |
| Uzzi, B., Mukherjee, S., Stringer, M., & Jones, B. (2013). “Atypical combinations and scientific impact.” | Supplies the atypicality construct against which the focal novelty indicator is compared; needed to distinguish first-ever combinations from unusual but existing ones. | Method |

## Open questions

- Does the delayed-recognition pattern survive when novelty is measured without
  future reuse, from article text or topics, and across open bibliographic data
  that include books, local journals, and non-English sources?
- Can submission, peer-review, or reader-level data distinguish paradigm
  resistance from slow incorporation, field diffusion, journal placement,
  author selection, and intrinsic quality?
- Do country, language, institution, journal prestige, career stage, or author
  identity moderate the novelty–recognition trajectory after the unit of
  analysis is held constant?
- Which citation window is adequate by field, and can evaluators identify novel
  work without selecting on future citation or reuse?

## Review provenance

AI-assisted research tools supported source discovery, metadata verification,
full-text extraction, and structured review. The bibliographic record was
verified against AnySearch academic metadata, Crossref, OpenAlex, and the KU
Leuven repository. The full 55-page accepted manuscript was read and matched to
the published citation and DOI printed in the document. Crossref reported no
update-to relation. No independent replication of the proprietary Web of
Science analysis was attempted.
