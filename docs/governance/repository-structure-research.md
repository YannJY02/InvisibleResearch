# Academic and Computational Research Repository Organization

## Scope

This note compares four possible primary organization axes for a mixed R/Python research repository: research question or output, workflow stage, data source, and publication/research compendium. It draws only on official guidance and original papers. The sources do **not** prescribe one universal directory tree; they converge on separability, provenance, reproducibility, and a structure that matches the unit of scholarship.

## Findings

1. **The strongest cross-source convention is separation by artifact role, not by data provider.** The Turing Way recommends separating input (data), methods (scripts), and output (results, figures, manuscript). Its research-compendium guidance likewise identifies conventional structure, separation of data/method/output, and a specified computational environment as the three core principles. Marwick, Boettiger, and Mullen's original research-compendium paper adds that raw data should be read-only, transformations should be recorded in code, outputs should be regenerable, and the dependency relationship among data, code, and outputs should be explicit. ([The Turing Way: advanced repository structure](https://book.the-turing-way.org/project-design/pd-overview/project-repo/project-repo-advanced/); [The Turing Way: research compendia](https://book.the-turing-way.org/reproducible-research/compendia/); [Marwick, Boettiger, & Mullen, 2018](https://doi.org/10.1080/00031305.2017.1375986))

2. **Workflow-stage structure is mature for the shared data layer, but stage names do not express scientific status.** Cookiecutter Data Science (CCDS) uses `data/raw`, `data/external`, `data/interim`, and `data/processed`, with raw inputs immutable and transformations forming a directed acyclic graph. Crucially, CCDS says the exact folder names matter less than the data flow. This structure makes lineage legible, but `processed` means a lifecycle position, not “validated,” “confirmatory,” or “approved for publication.” ([CCDS directory structure](https://cookiecutter-data-science.drivendata.org/); [CCDS opinions](https://cookiecutter-data-science.drivendata.org/opinions/))

3. **Exploratory work and repeatable analysis should have different homes and expectations.** CCDS explicitly treats notebooks as suitable for exploration and communication, while recommending source files for repeatable work because they are easier to test, review, and port. It suggests `notebooks/exploratory/` versus polished reports and moving repeated or reusable logic into source modules. For long-running projects, CCDS documents a top-level `research/` adaptation containing one subdirectory per experiment, each potentially owning notebooks, code, and a Makefile. ([CCDS opinions](https://cookiecutter-data-science.drivendata.org/opinions/))

4. **A publication-centered research compendium is the mature unit for a paper's reproducibility package.** The Turing Way defines a research compendium as the collection of data, code, text, figures, and environment information needed to recreate a publication's results. Marwick et al. show both minimal and large compendia, including a manuscript directory, reusable functions, analysis code, data, environment metadata, and an executable dependency specification. The Zenodo Research Compendium community's curation policy similarly requires association with a public scholarly work and documentation for reproduction. ([The Turing Way: research compendia](https://book.the-turing-way.org/reproducible-research/compendia/); [Marwick et al., 2018](https://doi.org/10.1080/00031305.2017.1375986); [Zenodo Research Compendium curation policy](https://zenodo.org/communities/research-compendium/curation-policy))

5. **The right project boundary depends on overlap in data and code, not on a universal “one repo per paper” rule.** Wilson et al.'s original “Good enough practices” paper notes that researchers variously use one project per manuscript or group work by theme, dataset, or algorithm. Its rule of thumb is practical: independent efforts with little shared data/code should be separate; strongly overlapping efforts should remain together; reusable tools shared across projects may deserve their own project. Within a project, it recommends organizing primarily by file type, grouping publication-specific outputs together, and using subdirectories for raw-data metadata when needed. ([Wilson et al., 2017](https://doi.org/10.1371/journal.pcbi.1005510))

6. **Data source is important provenance metadata, but weak as the primary repository architecture.** The cited conventions place third-party sources under `data/external` or organize raw data by metadata relevant to the analysis; they do not elevate each provider into the main unit of scholarship. A source-centered top level can be reasonable for a pure acquisition/catalogue system, but in an analytical research project it fragments questions and outputs that combine several sources. This is a synthesis of the CCDS and Wilson et al. guidance, not a separately mandated standard. ([CCDS directory structure](https://cookiecutter-data-science.drivendata.org/); [Wilson et al., 2017](https://doi.org/10.1371/journal.pcbi.1005510))

7. **Large external data need durable identity and provenance, not necessarily Git storage.** CCDS defaults to excluding most data from source control and recommends external object storage for large datasets. The Turing Way's data-management guidance says storage should be chosen with size, backup, access, preservation, documentation, and future reuse in mind. FAIR requires persistent identifiers, rich metadata, licenses, and detailed provenance for reusable data; FAIR4RS applies analogous requirements to versioned research software. Neither FAIR nor FAIR4RS prescribes a folder tree. ([CCDS opinions](https://cookiecutter-data-science.drivendata.org/opinions/); [The Turing Way: data management plans](https://book.the-turing-way.org/reproducible-research/rdm/rdm-dmp/); [Wilkinson et al., 2016](https://doi.org/10.1038/sdata.2016.18); [Barker et al., 2022](https://doi.org/10.1038/s41597-022-01710-x))

8. **Directory placement cannot confer epistemic authority.** None of these standards treats movement into `paper/`, `processed/`, or `reports/` as evidence that an analysis is scientifically accepted. A mature governance layer therefore records status separately: the research question or protocol, responsible authors, exact code revision, data identifiers/checksums, approved outputs, and the decision date. Technical reproducibility can make an analysis eligible for review; author or collaborator approval remains a scientific decision. This is a governance inference from the sources' emphasis on provenance, versioning, collaboration, and publication-specific compendia.

## Comparison of primary organization axes

| Primary axis | Strengths | Failure mode | Best use |
|---|---|---|---|
| Research question / experiment / output | Matches scientific intent; keeps an exploration's notebooks, notes, and local runner together | Shared ingestion and reusable methods can be duplicated; boundaries change as questions evolve | Exploratory `research/` lanes or clearly bounded studies |
| Workflow stage / artifact role | Conventional and easy to navigate; makes raw-to-derived lineage and regenerability visible | Scatters one research question across directories; stage can be mistaken for scientific approval | Shared project infrastructure: data, source code, documentation, and generated results |
| Data source | Makes acquisition ownership, access rules, and source-specific metadata obvious | Treats an input provider as the unit of scholarship; fragments multi-source analyses | Secondary grouping inside raw/external data and acquisition adapters |
| Publication / research compendium | Aligns code, manuscript, figures, tables, data references, and environment with peer review and archival release | Premature during exploration; can duplicate shared assets across several papers | Approved or release-bound paper analysis and archived reproducibility packages |

## Recommendation framework

Use a **hybrid, two-layer model** rather than a single axis:

1. **Project workspace layer:** organize stable shared assets by role and lifecycle—immutable/external inputs, derived data, reusable R/Python source, documentation, and generated results. Preserve the dependency graph from input to output.
2. **Exploration layer:** organize active investigations by research question or experiment. Keep their notebooks, notes, and thin orchestration local, but promote repeated logic into shared source modules.
3. **Publication layer:** create one narrow executable compendium per manuscript or other scholarly output when it becomes a publication candidate. It should identify exact inputs, code revision, environment, manuscript, tables/figures, and the command or workflow that regenerates them.
4. **Provenance layer:** record data sources beneath the data lifecycle structure and in metadata/manifests. Use persistent identifiers where available; otherwise record retrieval date/version, license, access method, and checksum. Keep large bytes in appropriate external storage.
5. **Governance layer:** keep exploratory, candidate, and author-approved status in an auditable decision record. Do not infer status from a folder name. Promotion should require both technical reproducibility evidence and the designated authors' scientific decision.

### Decision test

- If the main question is **“where did this byte come from and how was it transformed?”**, navigate by lifecycle and provenance.
- If it is **“what are we currently trying to learn?”**, navigate by research question or experiment.
- If it is **“what exactly supports this scholarly claim?”**, navigate by publication compendium and its decision record.
- If two bodies of work share little data or code, split them; if they share most assets, retain one project workspace and separate only their exploration/publication layers.

## Source notes

- The Turing Way is a community-maintained official handbook, not a normative standard.
- CCDS is an official practitioner template for collaborative data science; it is intentionally adaptable.
- Marwick et al. (2018), Wilson et al. (2017), Wilkinson et al. (2016), and Barker et al. (2022) are original peer-reviewed sources.
- FAIR and FAIR4RS constrain identity, metadata, provenance, and reuse; they should not be cited as support for a particular directory name.
