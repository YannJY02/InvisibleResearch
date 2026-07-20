# Morgan et al. (2018) — Prestige and idea diffusion

- **Citation:** Morgan, A. C., Economou, D. J., Way, S. F., & Clauset, A. (2018). Prestige drives epistemic inequality in the diffusion of scientific ideas. *EPJ Data Science, 7*, Article 40. https://doi.org/10.1140/epjds/s13688-018-0166-4
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/IMRZK3G5)
- **DOI or URL:** https://doi.org/10.1140/epjds/s13688-018-0166-4
- **Reviewed:** 2026-07-20
- **Reading basis:** Full version-of-record text, PDF pp. 1–16

## Why this source matters

Morgan et al. separate two questions that are easily collapsed: whether faculty
hiring can carry research topics between departments, and what a prestige-shaped
hiring network would do to otherwise comparable ideas. The first is tested with
publication and hiring histories for five computer-science topics; the second is
explored with epidemic simulations on the observed hiring network.

The paper therefore supplies a direct network mechanism for uneven scholarly
circulation, but not an empirical estimate of prestige bias among equally good
ideas. Its strongest contribution to this corpus is the distinction between an
observed hiring-associated transmission pathway and model-dependent claims about
origin, quality, and eventual diffusion.

## Research question and framing

- **Question or aim:** Test whether faculty hiring carries research ideas to new
  universities, then use the hiring network to examine how an idea's originating
  department and intrinsic transmissibility jointly shape how far and how long it
  spreads (pp. 2–3).
- **Conceptual framing:** Epistemic inequality may reflect merit, non-meritocratic
  advantages associated with an idea's origin, or both. The authors distinguish
  prestige-based network position from resource advantages, researcher
  reputation, and other visibility mechanisms, while treating hiring as one
  possible transmission route (pp. 1–3).
- **Contribution claimed:** The authors claim empirical evidence that hiring can
  transmit some research topics and a theoretical characterization of how the
  observed hiring network advantages ideas originating at prestigious
  departments, including a model-derived exchange relationship between prestige
  and idea transmissibility (pp. 3, 13–14).

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | Departments and directed faculty-placement edges in the network; faculty publications and department-level adoption events in the empirical topic analysis (pp. 3–8). |
| Data source | A hand-collected 2011–2012 census of 5,032 tenured or tenure-track faculty at 205 Ph.D.-granting CS departments, linked to DBLP publication histories for an in-sample subset (pp. 3–5). |
| Sample and coverage | 200,476 publications by 2,583 professors with known doctoral and first assistant-professor departments. Five manually defined topic sets contain 1,116 deep-learning, 217 topic-modeling, 71 incremental-computation, 167 quantum-computing, and 122 mechanism-design papers (pp. 5–6). |
| Time period | Faculty-employment network observed in the 2011–2012 academic year. A single start and end year for the linked publication histories is not reported (pp. 3–5). |
| Geographic or linguistic scope | All in-scope Ph.D.-granting computer-science departments in the United States and Canada; faculty trained or employed outside the sampled departments are excluded. Publication language is not reported (pp. 3–4). |

## Methods

- **Design:** Observational timing analysis of topic adoption and faculty hiring,
  followed by numerical SI-model simulations on the observed directed,
  multi-edge hiring network (pp. 5–13).
- **Measures or classifications:** Departmental prestige is the average rank
  across rankings that minimize upward-placement violations in the same hiring
  network; lower rank numbers mean higher prestige. Topic papers are identified
  by 7–56 expert-supplied keywords in titles and manually checked. A department
  counts as adopting through hiring when a new faculty member has topic work no
  later than two years after hiring, publishes on the topic subsequently, and no
  incumbent published on it earlier (pp. 4, 6–7).
- **Analysis:** A permutation test fixes each faculty member's publication years
  while randomly reassigning titles, then compares observed and expected shares
  of hiring-associated adoptions. In the simulations, departments move once from
  susceptible to infected; each hiring edge transmits independently with
  probability `p`, interpreted as intrinsic idea quality. Epidemic size and
  length are compared by origin prestige. A second model permits one uniform
  random jump to an otherwise unreachable department with probability `q`, and
  a data-collapse ansatz relates prestige decile, `p`, and epidemic size (pp.
  7–13).
- **Validation or robustness:** The empirical topic sets receive manual relevance
  checks and the adoption shares are tested against a temporal permutation null.
  The simulation analysis compares prestige with several other network measures,
  varies `p`, adds a non-hiring jump process, and reports 10,000 runs per origin in
  the methods. The public [replication repository](https://github.com/allisonmorgan/epistemic_inequality)
  contains the topic files, permutation notebook, network data, simulation code,
  cached results, and plotting code (pp. 4, 6–13, 15).

## Findings

### Hiring is associated with a substantial minority of observed topic adoptions

- **Source claim:** Faculty hiring can act as a transmission mechanism for some
  research topics, but not necessarily for every topic (pp. 7–8).
- **Evidence:** Across 241 department-level adoption events, 88 (37%) met the
  hiring-adoption definition; 81% of those moved from a higher-prestige doctoral
  institution to a lower-prestige employer. The observed hiring share exceeded
  the permutation expectation for all five topics and was significant for topic
  modeling (0.35 versus 0.23), incremental computation (0.39 versus 0.20),
  quantum computing (0.32 versus 0.22), and mechanism design (0.48 versus 0.21),
  each reported as `p = 0.01 ± 0.01`. Deep learning was not significant (0.35
  versus 0.34; `p = 0.34 ± 0.01`) (pp. 7–8).
- **Locator:** Section 3, Figure 4 and Table 1, pp. 7–8.
- **Caveat:** The test identifies topic work temporally aligned with a hire, not a
  randomized causal effect of hiring or a direct observation that an idea was
  learned through the doctoral-to-faculty edge. The 81% downward flow also
  reflects the steep placement hierarchy: only about 9–14% of placements move
  upward in prestige (p. 7).

### Equal-quality origin comparisons are simulation results, not empirical estimates

- **Source claim:** On the observed hiring network, ideas assigned the same
  transmissibility spread farther when they originate at more prestigious
  departments, with the advantage strongest for low-transmissibility ideas (pp.
  9–10).
- **Evidence:** In the SI simulations, epidemic size increases with origin
  prestige at fixed `p` (Figure 5). High-`p` ideas approach broad diffusion from
  many origins, whereas low-`p` ideas from prestigious origins reach more
  departments and circulate longer than the same `p` from peripheral origins
  (Figures 5–6) (pp. 9–11).
- **Locator:** Sections 4.1–4.2.1 and Figures 5–6, pp. 9–11.
- **Caveat:** `p` is an assumed, homogeneous edge-transmission probability and is
  not measured from the five topics, citations, peer review, or content. Its
  independence from prestige is imposed by the model, so the simulations isolate
  a network-position effect by construction rather than showing that real ideas
  of equal quality received different diffusion outcomes (pp. 9, 14).

### A uniform non-hiring route does not remove the simulated prestige advantage

- **Source claim:** Allowing diffusion outside hiring links modestly helps ideas
  originating at the least prestigious institutions but leaves the simulated
  advantage of the most prestigious institutions largely intact (pp. 11–12).
- **Evidence:** At fixed `p = 0.1`, increasing jump probability `q` raises
  epidemic size for peripheral origins while changing outcomes for elite origins
  only marginally; even high `q` values do not eliminate the gap in Figure 7
  (pp. 11–12).
- **Locator:** Section 4.2.2 and Figure 7, pp. 11–12.
- **Caveat:** The jump is a deliberately coarse assumption: each infected
  department gets at most one uniformly selected unreachable target. Conferences,
  collaboration, reading, social media, and citation networks are neither
  observed nor modeled with their own structured, potentially prestige-correlated
  pathways (pp. 11, 13–14).

### The prestige–quality exchange rate is a fitted property of the model

- **Source claim:** Lower-prestige origins require exponentially greater idea
  transmissibility to reach the same simulated epidemic size, and the lowest
  prestige decile may not reach the entire network even at the largest modeled
  `p` (pp. 12–13).
- **Evidence:** Logistic curves by prestige decile are rescaled with
  `p* = -p / log(1-d)`, collapsing simulated epidemic sizes onto a common fitted
  function in Figure 8 (pp. 12–13).
- **Locator:** Section 4.2.3 and Figure 8, pp. 12–13.
- **Caveat:** The transformation is an ansatz fitted to simulations on this one
  network. It is not an observed substitution rate between institutional
  prestige and empirical research quality, and the paper does not validate the
  collapsed function against later topic diffusion (pp. 12–14).

## Limitations

### Source-reported limitations

- Title keywords under-classify topic-relevant work and may misclassify hiring
  transmissions as non-hiring events; abstracts or full text could improve topic
  detection (pp. 6, 13).
- Five computer-science topics are not exhaustive, and deep learning shows that
  hiring need not be statistically important for every idea. The authors make no
  claim about how much all academic idea diffusion occurs through hiring (p. 8).
- The data cover only U.S. and Canadian computer-science departments. Extension
  to other fields and available hiring networks is needed (p. 13).
- Faculty hiring is privileged as the main conduit, while all other diffusion is
  compressed into a small, uniform jump probability. More realistic work would
  measure and model those pathways directly (pp. 13–14).
- Objective empirical idea quality is not measured. If quality and prestigious
  origin are correlated, quality confounds the proposed hiring-network mechanism;
  perceived quality may also contain a prestige halo effect (p. 14).

### Reviewer assessment

- The empirical and simulated results have different authority. The timing and
  permutation evidence supports hiring as one plausible adoption route; only the
  simulation supports the equal-quality origin comparison, diffusion gap, and
  prestige–quality exchange function.
- Prestige is calculated from the same placement network over which simulated
  ideas spread. Its strong relationship to epidemic reach partly captures network
  centrality and faculty-production volume, so the study does not isolate a
  separately manipulable causal effect of prestige from the topology used to
  define it (pp. 4, 9–13).
- The permutation null breaks topical and hiring-time alignment by reassigning
  titles but cannot rule out selection into growing topics, collaboration,
  advisors, conferences, common field trends, or other communication pathways
  that covary with hiring. “Transmission” is an operational classification, not
  direct evidence of knowledge transfer (pp. 6–8).
- The adoption rule allows work published up to two years after hiring to count
  as prior work, a defensible publication-lag allowance that can also blur whether
  the topic was carried from doctoral training or developed at the employing
  institution (p. 6).
- The methods report 10,000 SI simulations per department, whereas Figures 5, 6,
  and 8 describe averages over 1,000 trials. The replication repository README
  agrees with the captions: its SI caches contain 1,000 trials per node–`p` pair,
  its random-jump caches contain 500, and the topic permutation tests contain
  10,000. The 10,000 in the article's SI-method paragraph is therefore best
  treated as a reporting error unless the authors document additional runs (pp.
  9–12).
- As a peer-reviewed computational observational study plus theoretical
  simulation, the source is useful supporting evidence for a plausible network
  mechanism. It is not causal evidence that prestige itself drives observed
  diffusion of equally good real ideas.

## Project relevance

- **Source supports:** Faculty hiring as a directly studied pathway through which
  some CS topics appear at new departments; a prestige-correlated network
  topology that can generate unequal simulated diffusion even when ideas are
  assigned identical transmissibility; and the need to distinguish empirical
  topic adoption from model-based structural consequences.
- **Project interpretation:** Later synthesis can treat prestige-structured
  mobility as one mechanism linking institutional hierarchy to scholarly
  circulation. It should keep network origin, discoverability, citation,
  evaluation, and journal-index admission separate, and label the claimed
  prestige–quality trade-off as theoretical rather than observed.
- **Does not establish:** That two real ideas of equal quality diffuse differently
  because of institutional prestige; that hiring is the dominant diffusion route;
  an objective measure of idea quality; causal prestige bias; generalization
  beyond North American computer science; or an explanation for OJS journal
  noncoverage. It does not grant this note or the corpus Paper Analysis authority.

## Literature-review connections

- **Themes:** Institutional prestige; faculty hiring and mobility networks;
  diffusion of research topics; epistemic inequality; cumulative advantage;
  model-based quality–origin separation; structural versus content explanations.
- **Agreements or tensions:** The source adds a network pathway to the evaluation
  and index mechanisms already represented in the corpus. It can coexist with
  Larivière et al.'s finding of declining aggregate citation concentration because
  Morgan et al. model institution-level topic diffusion rather than measuring the
  distribution of citations. It also does not test Khanna et al.'s selective-index
  undercoverage, so the two mechanisms should not be merged without evidence.

| Follow-up source | Why follow it | Role |
|---|---|---|
| Clauset, A., Arbesman, S., & Larremore, D. B. (2015). “Systematic inequality and hierarchy in faculty hiring networks.” | Supplies the faculty census, prestige ranking, and hiring-network structure reused by the focal study; necessary for auditing how prestige is constructed from placements. | Method and framing |
| Cole, S., & Cole, J. R. (1968). “Visibility and the structural bases of awareness of scientific research.” | Provides the earlier empirical visibility account used to connect institutional position to awareness and reception. | Framing and evidence |
| Gerow, A., Hu, Y., Boyd-Graber, J., Blei, D. M., & Evans, J. A. (2018). “Measuring discursive influence across scholarship.” | Offers a text-based approach that could improve on title-keyword topic detection and distinguish idea content from adoption proxies. | Method |
| Rotabi, R., Danescu-Niculescu-Mizil, C., & Kleinberg, J. M. (2017). “Tracing the use of practices through networks of collaboration.” | Gives a neighboring network-diffusion design against which hiring-based transmission could be compared. | Method and tension |

## Open questions

- Does an empirical design that measures idea content or quality find different
  diffusion outcomes by institutional origin after controlling for field,
  collaboration, publication venue, resources, and researcher reputation?
- How much apparent transmission remains when adoption is detected from abstracts
  or full text and when collaboration and advisor networks are modeled alongside
  hiring?
- Does the prestige–diffusion relationship persist in fields with less hierarchical
  hiring, outside the United States and Canada, or in non-departmental scholarly
  communities?
- Which part of the simulated advantage comes from prestige rank itself versus
  out-degree, department size, closeness, or other network features derived from
  the same hiring graph?
- Did the authors run an unarchived 10,000-trial SI analysis, or does the methods
  paragraph mistakenly carry over the 10,000 topic-permutation count?

## Review provenance

AI-assisted research tools supported source discovery, metadata verification,
full-text extraction, and structured review. The bibliographic record was
verified against the DOI and Springer Nature version-of-record page. Every
substantive finding above was checked against the complete 16-page open-access
PDF. The public replication repository was checked to resolve the simulation
trial-count discrepancy; no empirical analysis or simulation was rerun.
