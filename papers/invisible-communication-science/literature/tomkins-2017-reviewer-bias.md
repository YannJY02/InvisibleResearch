# Tomkins et al. (2017) — Reviewer bias in single- versus double-blind peer review

- **Citation:** Tomkins, A., Zhang, M., & Heavlin, W. D. (2017). Reviewer bias in single- versus double-blind peer review. *Proceedings of the National Academy of Sciences, 114*(48), 12708–12713. https://doi.org/10.1073/pnas.1707323114
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/QI8AXWN2)
- **DOI or URL:** https://doi.org/10.1073/pnas.1707323114
- **Reviewed:** 2026-07-20
- **Reading basis:** Full article and three-page Supporting Information via PubMed Central (PMCID: PMC5715744)

## Why this source matters

Tomkins et al. provide controlled evidence that revealing author and affiliation
information changes two stages of conference peer review: reviewers' bids for
papers and their recommendations for acceptance. The paper belongs in this
corpus because it identifies a direct prestige-cue mechanism in scholarly
evaluation while leaving open whether reviewers are applying an unfair status
halo, informative prior knowledge about quality, or a mixture of both.

The outcome is reviewer behavior at one computer-science conference. It is not
final publication, later citation, database discoverability, or a general
measure of scholarly visibility.

## Research question and framing

- **Question or aim:** Test whether single-blind reviewers, who see author names
  and affiliations, bid and score differently from double-blind reviewers who
  evaluate anonymized submissions (Introduction; Materials and Methods).
- **Conceptual framing:** The authors place visible identity cues within debates
  over the Matthew effect, institutional prestige, the Matilda effect, reviewer
  expertise, conflict detection, and the practicality of anonymization
  (Introduction; Discussion).
- **Contribution claimed:** A randomized reviewer-pool experiment shows that
  single-blind reviewers bid less broadly, favor top institutions when bidding,
  and recommend acceptance more often for papers linked to famous authors, top
  universities, or selected top companies, conditional on a blinded paper
  quality proxy (Results, Tables 2–3; Conclusion).

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | Reviewer–paper pairs for bid and positive-score models; papers are the objects reviewed (Materials and Methods; Results, “Modeling Reviews” and “Modeling Bids”). |
| Data source | EasyChair bidding, assignment, review-score, rank, affiliation, country, and conflict records for WSDM 2017; author prestige and affiliation features were added from conference history, DBLP, a global university ranking, and hand-built company categories (Materials and Methods). |
| Sample and coverage | 500 full-length submissions. Each paper was assigned two single-blind and two double-blind reviewers; 453 papers received four completed reviews and 47 received three after reviewer dereliction (Materials and Methods). |
| Time period | The WSDM 2017 submission, bidding, reviewing, and discussion cycle. The experiment ended before senior-program-committee recommendations and final program-chair decisions (Materials and Methods; Discussion, “Methodological Questions”). |
| Geographic or linguistic scope | One international computer-science conference. The source identifies 176 papers with the United States as the most common author country but does not report language or country-stratified outcomes (Materials and Methods, Table 1). |

## Methods

- **Design:** Controlled field experiment. Program-committee members were
  randomly split into disjoint single-blind and double-blind pools. Every paper
  was reviewed in both conditions, with two reviewers drawn from each pool, but
  separate bidding landscapes and assignment runs determined which reviewers
  reached each paper (Materials and Methods; Supporting Information,
  “Experimental Design Considerations”).
- **Measures or classifications:** A positive recommendation was any score
  above zero on the five-value review scale. “Famous author” meant at least
  three prior WSDM acceptances and at least 100 DBLP papers; “top university”
  meant a top-50 global computer-science university in the selected ranking;
  “top company” meant Google, Microsoft, Yahoo!, or Facebook. The paper also
  classified author gender, academic affiliation, U.S. location, and reviewer–
  author country match (Materials and Methods, Table 1).
- **Analysis:** Logistic regressions estimated positive-score and bid odds. The
  score model included seven cue variables and a blinded paper quality score
  derived from double-blind reviewers' scores and ranks. The bid model included
  the same cue family plus reviewer bid propensity and paper bid attractiveness
  derived from double-blind behavior (Materials and Methods; Results, Tables
  2–3).
- **Validation or robustness:** Alternative gender definitions did not produce
  a significant gender result. Aggregate score, rank, review length, discussion-
  stage score change, and detected-conflict comparisons were also null. A
  linear discriminant model fitted to releasable sufficient statistics produced
  coefficients with 99% correlation to the primary logistic-regression
  coefficients (Results; Supporting Information, “Raw Data and Privacy”).

## Findings

### Visible identities narrowed bidding while favoring prestigious affiliations

- **Source claim:** Single-blind reviewers entered fewer bids and directed a
  larger share of them toward papers from top universities and selected top
  companies (Results, “Modeling Bids”).
- **Evidence:** Single-blind reviewers averaged 19.9 bids versus 24.9 for
  double-blind reviewers, a 22% decrease (*P* = .0002). Conditional bid odds
  were higher for top-company papers (odds multiplier 1.17, *P* = .010) and
  top-university papers (1.13, *P* = .011); famous-author bidding was not
  significant (1.07, *P* = .287) (Results, Table 3).
- **Locator:** Results, “Modeling Bids,” Table 3; Figure 1.
- **Caveat:** The source does not observe why reviewers bid this way. Prestige
  could trigger a status heuristic, prior familiarity, anticipated relevance,
  or expected paper quality. Separate bid landscapes also changed subsequent
  reviewer assignment.

### Prestigious author and affiliation cues predicted more positive recommendations

- **Source claim:** After accounting for the blinded paper quality score,
  single-blind reviewers were more likely to recommend acceptance for papers
  with a famous author, a top-university affiliation, or a selected top-company
  affiliation (Results, “Modeling Reviews”).
- **Evidence:** Odds multipliers were 1.63 for famous author (*P* = .027), 1.58
  for top university (*P* = .012), and 2.10 for top company (*P* = .002). The
  authors translate these coefficients to 0.61, 0.57, and 0.92 SDs of their
  blinded paper quality score, respectively (Results, Table 2).
- **Locator:** Results, “Modeling Reviews,” Table 2.
- **Caveat:** These are reviewer recommendations, not final acceptance
  decisions. The model's quality control is an imperfect proxy built from two
  double-blind reviewers, and the prestige variables are coarse, potentially
  overlapping classifications rather than independently manipulated cues.

### The experiment identifies an end-to-end review-process difference, not a pure halo effect

- **Source claim:** Across bidding, assignment, and scoring, reviewers with
  identity information were more positive toward prestigious authors and
  institutions than reviewers without that information (Discussion,
  “Reviewing Behavior”).
- **Evidence:** Reviewer pools were randomized, each paper entered both
  conditions, and the status-related score differences remained conditional on
  the blinded quality proxy (Materials and Methods; Results, Table 2).
- **Locator:** Materials and Methods, experimental-design steps i–iv;
  Discussion, “Reviewing Behavior.”
- **Caveat:** The authors explicitly reject the stronger interpretation that
  two otherwise identical reviewers changed only because of the cue. Bidding
  affected assignment, so single- and double-blind reviewers reaching a paper
  were not identically distributed; greater topic or author familiarity could
  partly explain their different scores.

### Aggregate review severity did not differ between conditions

- **Source claim:** The prestige-conditioned differences did not appear as a
  general shift toward harsher or more favorable reviewing in either pool
  (Results, “Aggregate Review Statistics”).
- **Evidence:** Mean scores were −2.07 under single-blind review and −1.90 under
  double-blind review (*P* = .51); ranks, review lengths, discussion-stage score
  changes, and detected conflicts also showed no significant condition
  difference (Results, Table 4; “Changes During Discussion”; “Conflicts of
  Interest”).
- **Locator:** Results, Table 4 and the two following subsections.
- **Caveat:** A null aggregate difference can coexist with redistribution among
  prestige categories. These analyses do not test final decisions or rule out
  effects the study lacked power to detect.

### Gender results were inconclusive rather than evidence of no bias

- **Source claim:** Author gender was not statistically significant for bidding
  or reviewing in this experiment (Results, “The Matilda Effect”).
- **Evidence:** The positive-score odds multiplier for a paper with at least one
  woman author was 0.78 (*P* = .16), equivalent to −0.31 SD of the blinded
  quality score; bid odds were 1.05 (*P* = .27). First-author, majority-women,
  manually coded, and census-name variants were also nonsignificant (Results,
  Tables 2–3; “The Matilda Effect”).
- **Locator:** Results, “The Matilda Effect,” Tables 2–3; Supporting
  Information, “Raw Data and Privacy.”
- **Caveat:** The estimated review effect was nontrivial and the source points
  to broader evidence against women authors. This single study cannot support
  a claim that gender bias is absent.

## Limitations

### Source-reported limitations

- The experiment stops before senior-program-committee deliberation and final
  program-chair acceptance decisions, so it supports claims about bids and
  recommendations only (Discussion, opening and “Methodological Questions”).
- Separate bidding and assignment processes mean the reviewers who reached a
  paper were not identically distributed across conditions; observed score
  differences may combine cue effects with reviewer-selection effects
  (Discussion, “Reviewing Behavior”).
- All submitted manuscripts were anonymized, reviewers knew WSDM was testing a
  mixture of review models, and some double-blind reviewers may have inferred
  or searched for identities. These features may weaken the intended contrast
  (Discussion, “Methodological Questions” and “Practical Issues”).
- The paper reports no direct evidence for the mechanism behind prestige-
  selective bidding and treats quality inference as a hypothesis (Discussion,
  “Bidding Behavior”).
- Raw records could not be released without risking participant privacy. The
  released sufficient statistics support linear discriminant analysis, not an
  exact independent rerun of the logistic models (Materials and Methods, “Data
  Sharing”; Supporting Information, “Raw Data and Privacy”).
- The conflict-detection result depends on the capabilities and configuration
  of the conference-management software and does not cover conflicts tied to
  author funding or professional interests (Discussion, “Conflict of
  Interest”).

### Reviewer assessment

- The randomized reviewer-pool design is strong evidence that information
  visibility changed this WSDM workflow, but one selective computer-science
  conference cannot establish the effect's direction or magnitude in journals,
  book-centered fields, less selective venues, other years, or other review
  cultures.
- The blinded paper quality score is not an external measure of intrinsic
  quality. Its between-reviewer correlation was 0.38, and the Supporting
  Information reports single-reviewer agreement around 0.37–0.40. Residual
  quality differences and reviewer noise therefore remain viable explanations.
- Seven cue variables were examined in the main score model. The article does
  not report preregistration or a multiple-testing correction, so the smaller
  *P* values—especially the famous-author result at .027—should be treated as
  single-study evidence rather than a universal or fully confirmatory estimate.
- “Famous,” “top university,” and “top company” are researcher-defined proxies.
  They combine reputation, resources, field fit, prior output, and potential
  familiarity; the experiment does not independently manipulate those
  constructs or show which component reviewers used.
- The authors disclose that Tomkins and Heavlin were paid Google employees and
  that Google funded conferences including WSDM; Google was also one of four
  organizations classified as a top company. The disclosure does not invalidate
  the analysis, but it is relevant when interpreting that category and the
  design team's institutional position.
- Under the Academic Research Suite hierarchy, this is a Level II randomized
  controlled field experiment and overall Grade A evidence for the bounded
  claim about reviewer behavior in this setting. Its general visibility claim
  remains preliminary because external replication and outcome transfer are
  limited.

## Project relevance

- **Source supports:** A direct, controlled prestige-cue mechanism in which
  visible author and affiliation information changes reviewer attention during
  bidding and positive recommendations during evaluation; it also supports
  distinguishing aggregate review severity from redistribution among status
  groups.
- **Project interpretation:** Prestige can operate before a paper is published:
  cues may alter who volunteers to review it, which expertise reaches it, and
  how strongly reviewers recommend it. Later synthesis should model this as a
  conditional evaluation mechanism, not as a synonym for discoverability,
  citation, quality, or final publication.
- **Does not establish:** That prestige cues always reduce decision quality;
  that lower-status work was objectively equal; that double-blind review
  eliminates identity inference or produces better final decisions; that the
  same effects hold beyond WSDM 2017; or that prestige explains journal
  noncoverage in the OJS population. It does not grant this note or the corpus
  Paper Analysis authority.

## Literature-review connections

- **Themes:** Prestige cues; Matthew effect; peer-review gatekeeping; reviewer
  attention and bidding; institutional status; reviewer assignment; quality
  uncertainty; anonymization; competing explanations for uneven recognition.
- **Agreements or tensions:** The result complements policy- and index-mediated
  visibility mechanisms by locating inequality inside evaluation itself. Its
  strongest internal tension is between a status-halo account and a quality-
  information account: the experimental workflow difference is observed, but
  the study cannot determine whether prestige supplied irrelevant bias, useful
  prior information, different reviewer expertise, or some combination.

| Follow-up source | Why follow it | Role |
|---|---|---|
| Blank, R. M. (1991). “The effects of double-blind versus single-blind reviewing: Experimental evidence from the American Economic Review.” | Provides the major prior randomized study and different institutional-prestige findings in economics. | Tension and method |
| Okike, K., Hug, K. T., Kocher, M. S., & Leopold, S. S. (2016). “Single-blind vs double-blind peer review in the setting of author prestige.” | Manipulates prestigious author identity on a fabricated manuscript, offering a cleaner author-prestige comparison in a different field. | Supporting evidence and method |
| Peters, D. P., & Ceci, S. J. (1982). “Peer-review practices of psychological journals: The fate of published articles, submitted again.” | Tests reputation and institutional cues by resubmitting already-published work under invented low-prestige identities, while raising ethical and reproducibility concerns. | Framing and tension |
| Snodgrass, R. (2006). “Single- versus double-blind reviewing: An analysis of the literature.” | Supplies the broad review of reviewer blindness used to situate this experiment and its inconsistent prior evidence. | Review lead |

## Open questions

- Does the prestige effect replicate when the same reviewers assess comparable
  manuscripts under randomized identity cues, eliminating bid-mediated
  reviewer selection?
- Do prestige-conditioned recommendation differences survive discussion and
  change final publication decisions?
- How much of the effect reflects valid prior information about quality,
  familiarity with prior work, topic expertise, institutional resources, or an
  irrelevant status halo?
- Do journals, humanities and social-science venues, multilingual conferences,
  and less selective or regionally oriented venues show the same bidding and
  evaluation pattern?

## Review provenance

AI-assisted research tools supported DOI discovery, metadata verification,
full-text extraction, and structured review. Crossref and Europe PMC metadata
matched the Zotero parent record; the complete PubMed Central article and its
three-page Supporting Information were read before this note was created. The
source was marked as not retracted in the PubMed Central open-access record.
