# Literature Evidence Note Specification

A Literature Evidence Note is a reusable reading record for one publication. It
supports later literature-review synthesis without becoming that synthesis or
granting the source, note, or related analysis Paper Analysis authority.

## Required qualities

- **Traceable:** Link to the Zotero bibliographic item and give a page, section,
  figure, table, or appendix locator for every substantive finding.
- **Attributable:** Keep what the source reports separate from project
  interpretation. Never present an inference as an author's claim.
- **Complete:** Keep every template section. Write `Not reported`, `Not
  assessed`, or `None identified` when evidence is unavailable.
- **Readable:** Lead with why the source matters, use short paragraphs, and use
  tables only for repeated fields or comparisons.
- **Reusable:** Record methods, limitations, and follow-up sources precisely
  enough that a later reviewer need not reopen the paper to decide whether it
  is relevant. Reopen the paper before quoting or relying on exact wording.

## File and source identity

Store notes at:

```text
papers/<publication-compendium>/literature/<first-author>-<year>-<short-title>.md
```

The identity block must include:

- a complete bibliographic citation;
- `[Open source item in Zotero](zotero://select/library/items/<ITEM_KEY>)`;
- a DOI or stable public URL when available;
- the review date; and
- the reading basis: full text, abstract only, or named sections.

Link to the parent bibliographic item, not only its PDF attachment, so the
reader returns to the source's metadata, notes, and attachments in Zotero.

## Evidence rules

1. Paraphrase by default. Put any exact quotation in quotation marks and attach
   a precise locator.
2. A finding contains a source claim, its supporting evidence, a locator, and
   any caveat needed to interpret it.
3. Put author-stated limitations under **Source-reported limitations**. Put
   limitations noticed during review under **Reviewer assessment**.
4. Under **Project relevance**, distinguish what the source supports, how the
   project may use it, and what the source does not establish.
5. List a follow-up source only when its role is clear: framing, method,
   supporting evidence, tension, or review lead.
6. Do not copy an abstract into the note as a substitute for reading or
   synthesis.

## Copyable template

```markdown
# <First author et al. (Year)> — <Short title>

- **Citation:** <Complete bibliographic citation>
- **Zotero:** [Open source item in Zotero](zotero://select/library/items/<ITEM_KEY>)
- **DOI or URL:** <Stable link or Not available>
- **Reviewed:** <YYYY-MM-DD>
- **Reading basis:** <Full text | Abstract only | Named sections>

## Why this source matters

<Two to four sentences: topic, distinctive contribution, and reason it belongs
in the review corpus.>

## Research question and framing

- **Question or aim:** <Source-reported question or aim>
- **Conceptual framing:** <Theory, concepts, or debate used by the source>
- **Contribution claimed:** <What the authors say the study adds>

## Data and scope

| Element | Source-reported detail |
|---|---|
| Unit of analysis | <Value or Not reported> |
| Data source | <Value or Not reported> |
| Sample and coverage | <Value or Not reported> |
| Time period | <Value or Not reported> |
| Geographic or linguistic scope | <Value or Not reported> |

## Methods

- **Design:** <Study design>
- **Measures or classifications:** <Key operational choices>
- **Analysis:** <Analytical procedure>
- **Validation or robustness:** <Checks reported by the source or Not reported>

## Findings

### <Finding name>

- **Source claim:** <What the authors conclude>
- **Evidence:** <Result, comparison, estimate, or qualitative basis>
- **Locator:** <Page, section, figure, table, or appendix>
- **Caveat:** <Constraint or None identified>

<!-- Repeat the finding block only for findings relevant to the review. -->

## Limitations

### Source-reported limitations

- <Limitation and locator, or None identified>

### Reviewer assessment

- <Clearly marked assessment, verification need, or None identified>

## Project relevance

- **Source supports:** <Claims or framing this source can support>
- **Project interpretation:** <How it may inform the current project>
- **Does not establish:** <Overclaims or decisions this source cannot support>

## Literature-review connections

- **Themes:** <Review themes this source informs>
- **Agreements or tensions:** <Relationship to other reviewed sources, or Not assessed>

| Follow-up source | Why follow it | Role |
|---|---|---|
| <Citation or source named in this paper> | <Specific reason> | <Framing, method, evidence, tension, or review lead> |

## Open questions

- <Question, missing evidence, or verification task>
```

## Completion check

- The Zotero link opens the intended bibliographic item.
- Every substantive finding has evidence and a locator.
- Source claims and reviewer or project interpretation are visibly separate.
- Missing information is explicit rather than silently omitted.
- Follow-up references have a stated reason for inclusion.
- The note can be skimmed from relevance to evidence without reading duplicate
  summaries.
