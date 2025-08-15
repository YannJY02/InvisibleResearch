# Cursor AI Agent Workflow Examples

## 🎯 How to Use These Examples

These are practical examples demonstrating how to interact with the enhanced multi-agent system. Use them as a reference for structuring your own requests. The AI's responses are formatted according to the mandatory protocols in `multi-agent-workflow.md`.

---

## Example 1: Comprehensive Literature Review

**User Prompt**:
`"I need a comprehensive literature review on social media echo chambers and their effect on political polarization. Focus on research from the last 5 years."`

**Expected AI Response**:
```markdown
**[🔍 Research Agent Activated]**
- **Task**: Comprehensive Literature Review
- **Topic**: Social media echo chambers and their effect on political polarization
- **Scope**: Focusing on research published between 2019-2024.
- **Discipline Focus**: Communication Science, with cross-references to Political Science and Social Psychology.

---
**1. Search Strategy:**
   - **Primary Databases**: Communication & Mass Media Complete, Google Scholar, Scopus.
   - **Keywords**:
     - *Core*: "echo chamber", "filter bubble", "political polarization", "social media", "selective exposure"
     - *Secondary*: "partisan media", "confirmation bias", "affective polarization", "algorithmic curation"
   - **Inclusion Criteria**: Peer-reviewed empirical studies (quantitative or qualitative).
   - **Exclusion Criteria**: Opinion pieces, unpublished manuscripts, news articles.

**2. Analysis & Synthesis Framework:**
   - **Identify Core Theories**: The primary theoretical lens will be Selective Exposure Theory, supplemented by Social Identity Theory to explain in-group/out-group dynamics.
   - **Map Methodological Trends**: The review will categorize studies by methodology: (1) network analysis of user data, (2) survey-based studies, and (3) experimental designs testing information choice.
   - **Synthesize Key Findings**: The synthesis will focus on: (a) evidence for and against the prevalence of echo chambers, (b) the causal link between echo chamber exposure and increased polarization, and (c) platform-specific differences (e.g., Twitter vs. Facebook).
   - **Identify Research Gaps**: A key gap is the long-term behavioral impact of echo chamber exposure beyond self-reported attitudes.

**3. Deliverables:**
   - **Thematic Synthesis Report**: A 1500-word report summarizing the key themes, debates, and findings in the literature.
   - **Annotated Bibliography**: A list of the 15 most influential articles from the period, with a 3-sentence summary and APA 7th edition citation for each.
   - **Future Research Directions**:
     - How do different social media affordances (e.g., 'likes' vs. 'shares') contribute to echo chamber formation?
     - What are the most effective interventions (algorithmic or educational) to mitigate echo chamber effects?
     - To what extent do offline social networks moderate the effects of online echo chambers?
```

---

## 🔍 Research Agent Examples

### Example 1: Literature Review Request
```
User: "I need a comprehensive literature review on social media echo chambers and political polarization"

Expected AI Response:
🔍 RESEARCH AGENT: Literature Review

**Task**: Comprehensive literature review on social media echo chambers and political polarization
**Scope**: Communication science and political science literature, 2015-2024
**Focus**: Effects on democratic discourse and opinion formation

**Search Strategy**:
1. **Databases**: Communication & Mass Media Complete, Political Science Database, PsycINFO
2. **Keywords**: 
   - Primary: "echo chamber", "filter bubble", "political polarization", "social media"
   - Secondary: "selective exposure", "confirmation bias", "political communication"
3. **Timeframe**: 2015-2024 (peak social media political influence period)
4. **Language**: English, with key non-English studies if highly cited

**Analysis Framework**:
- Theoretical foundations (selective exposure theory, motivated reasoning)
- Methodological approaches (experimental, observational, computational)
- Key findings and effect sizes
- Platform-specific differences (Facebook, Twitter, YouTube)
- Demographic and contextual moderators

[Detailed literature synthesis follows...]
```

### Example 2: Survey Design Request
```
User: "Create a survey to measure news consumption habits and media trust among college students"

Expected AI Response:
🔍 RESEARCH AGENT: Survey Design

**Research Question**: How do news consumption patterns relate to media trust among college students?
**Target Population**: Undergraduate students, ages 18-24, diverse academic backgrounds
**Study Design**: Cross-sectional survey with experimental manipulation component

**Survey Structure**:
1. **Demographics Section** (5 items): Age, gender, academic year, major, political orientation
2. **News Consumption Patterns** (12 items): Sources, frequency, platform preferences
3. **Media Trust Scale** (8 items): Adapted from established measures
4. **Information Processing** (6 items): Verification behaviors, sharing patterns
5. **Experimental Vignette** (3 conditions): Source credibility manipulation

**Question Examples**:
- "How often do you get news from social media?" (1=Never to 7=Daily)
- "How much do you trust information from mainstream news outlets?" (1=Not at all to 7=Completely)

[Complete questionnaire with validation items follows...]
```

## 📊 Analysis Agent Examples

### Example 3: Dataset Analysis Request
```
User: "Analyze the data/final/title_pred_lang.parquet file to understand language patterns in academic titles"

Expected AI Response:
📊 ANALYSIS AGENT: Exploratory Data Analysis

**Dataset**: title_pred_lang.parquet (Language predictions for academic titles)
**Objective**: Understand linguistic diversity and patterns in academic publishing
**Variables**: title, language_db (metadata), language_pred (GlotLID predictions)

**Data Assessment**:
1. **Structure**: 1,958,232 records × 4 variables
2. **Quality**: 98.7% complete data, minimal missing values
3. **Language Distribution**: 127 unique languages detected

**Key Findings**:
- **Dominant Languages**: English (78.2%), Spanish (6.1%), Portuguese (4.3%)
- **Language Accuracy**: 89.4% agreement between metadata and predictions
- **Regional Patterns**: Strong geographic clustering in language use
- **Disciplinary Variation**: STEM fields more English-dominant

**Visualizations Created**:
- Language frequency distribution (bar chart)
- Geographic language mapping (world map)
- Accuracy comparison (confusion matrix)
- Temporal language trends (time series)

[Detailed statistical analysis follows...]
```

### Example 4: Network Analysis Request
```
User: "Create a collaboration network from the author data to identify research communities"

Expected AI Response:
📊 ANALYSIS AGENT: Network Analysis

**Network Type**: Author collaboration network
**Data Source**: creator_sample_clean.parquet (author and affiliation data)
**Research Focus**: Research community identification and collaboration patterns

**Network Construction**:
- **Nodes**: Authors (n=1,247)
- **Edges**: Co-authorship relationships (weighted by frequency)
- **Direction**: Undirected (symmetric collaboration)

**Key Network Metrics**:
- **Density**: 0.003 (sparse network, typical for academic collaboration)
- **Components**: 89 connected components, largest contains 45% of nodes
- **Average Clustering**: 0.61 (high local clustering)
- **Diameter**: 12 steps (reasonable for academic network)

**Community Detection Results**:
- **7 major communities** identified using modularity optimization
- Communities align with disciplinary boundaries and geographic regions
- Cross-community bridges indicate interdisciplinary collaboration

[Network visualization and interpretation follows...]
```

## 📝 Documentation Agent Examples

### Example 5: Research Report Request
```
User: "Write a comprehensive research report summarizing our invisible research project findings"

Expected AI Response:
📝 DOCUMENTATION AGENT: Academic Report

**Report Type**: Research summary report
**Audience**: Academic and policy stakeholders
**Length**: 3,000-4,000 words

# Invisible Research: Uncovering Hidden Academic Scholarship
## Executive Summary

This report presents findings from a comprehensive analysis of academic invisibility in global research output. Using advanced computational methods and a dataset of 20 million OAI-PMH records, we identified significant patterns of linguistic marginalization and institutional bias in academic publishing...

## Introduction

The phenomenon of "invisible research" represents one of the most pressing challenges in contemporary academia. Despite unprecedented global expansion of research output, dominant indexing systems and citation databases systematically marginalize scholarship produced outside established academic centers...

[Continues with full academic report structure...]
```

### Example 6: Technical Documentation Request
```
User: "Document the LLM name detection pipeline for future researchers"

Expected AI Response:
📝 DOCUMENTATION AGENT: Technical Documentation

# LLM-Based Author Name Detection Pipeline

## Overview

This pipeline uses GPT-4 to intelligently parse complex author fields in academic metadata, separating individual names from institutional affiliations with high accuracy.

## Architecture

```
Raw Author Fields → Complexity Classification → Processing Route
                                           ├── Simple: Rule-based parsing
                                           └── Complex: LLM processing → Validation
```

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key
- Required packages: `pip install -r requirements.txt`

### Basic Usage
```python
from agents.processing.llm_name_detect import NameDetector

detector = NameDetector(api_key="your_key")
result = detector.process_creator_field("John Smith; Harvard University; Jane Doe, MIT")
# Returns: {"authors": ["John Smith", "Jane Doe"], "affiliations": ["Harvard University", "MIT"]}
```

[Continues with detailed technical guide...]
```

## 🔧 Automation Agent Examples

### Example 7: File Organization Request
```
User: "Organize project files according to academic research standards"

Expected AI Response:
🔧 AUTOMATION AGENT: File Organization

**Task**: Standardize project structure for academic research workflow
**Scope**: All project files and directories
**Standards**: Academic research best practices with reproducibility focus

**Current Assessment**:
- 847 files across 23 directories
- Mixed organization patterns
- Some temporary files present
- Documentation scattered

**Organization Strategy**:
```
InvisibleResearch/
├── data/
│   ├── raw/              # 3 original datasets moved here
│   ├── processed/        # 12 intermediate files organized
│   └── final/            # 5 analysis-ready datasets
├── scripts/
│   ├── 01_setup/         # 2 setup scripts
│   ├── 02_extraction/    # 1 main extraction script
│   ├── 03_analysis/      # 4 analysis scripts
│   └── 04_processing/    # 3 advanced processing scripts
├── docs/                 # 8 documentation files
├── outputs/              # 15 result files organized by type
└── archive/              # 23 old/backup files moved here
```

**Actions Completed**:
✅ Moved 156 files to appropriate directories
✅ Renamed 23 files for consistency
✅ Removed 8 temporary files
✅ Updated 12 path references in scripts
✅ Created standardized README files

[Detailed organization log follows...]
```

### Example 8: Git Management Request
```
User: "Commit the recent analysis changes with proper formatting"

Expected AI Response:
🔧 AUTOMATION AGENT: Git Management

**Operation**: Commit recent analysis improvements
**Scope**: Analysis scripts and documentation updates
**Message**: Following conventional commit standards

**Pre-commit Assessment**:
- Modified files: 5 analysis scripts, 2 documentation files
- New files: 3 visualization outputs
- Code quality: All scripts pass linting
- Documentation: Updated to reflect changes

**Commit Details**:
```bash
git add scripts/03_analysis/ docs/analysis_guide.md outputs/visualizations/
git commit -m "feat(analysis): enhance network analysis with community detection

- Add modularity-based community detection algorithm
- Implement interactive network visualizations
- Update analysis documentation with new methods
- Include statistical validation procedures

Resolves: Enhanced community identification capability"
```

**Branch Status**:
- Current branch: `feature/network-analysis`
- 3 commits ahead of main
- Ready for pull request creation

[Git workflow completion summary follows...]
```

## 🎯 Multi-Agent Coordination Examples

### Example 9: Complex Multi-Step Research Task
```
User: "I want to research misinformation spread in academic contexts, design a study, and create preliminary analysis tools"

Expected AI Response:
🤖 MULTI-AGENT COORDINATION ACTIVATED

**Task Breakdown**: 3 agents required for comprehensive execution
**Timeline**: Parallel and sequential task execution

**Phase 1: Research Foundation** (Research Agent)
🔍 Literature review on academic misinformation
- Scope: Scholarly communication, information quality, peer review
- Output: Theoretical framework and gap analysis

**Phase 2: Study Design** (Research Agent) 
🔍 Mixed-methods research design
- Quantitative: Survey of researchers' misinformation exposure
- Qualitative: Interviews with journal editors and reviewers
- Output: Complete study protocol with IRB considerations

**Phase 3: Analysis Tools** (Analysis Agent)
📊 Preliminary analysis pipeline development
- Text analysis for misinformation detection
- Network analysis for spread patterns
- Output: Analysis scripts and validation procedures

**Phase 4: Documentation** (Documentation Agent)
📝 Comprehensive project documentation
- Research proposal formatting
- Technical documentation for tools
- Output: Grant-ready research proposal

**Coordination Plan**:
1. Phases 1-2 execute sequentially (Research Agent)
2. Phase 3 runs parallel with Phase 2 completion
3. Phase 4 integrates all outputs

[Detailed execution follows for each phase...]
```

### Example 10: Data Analysis to Publication Pipeline
```
User: "Take our invisible research dataset through complete analysis and prepare publication materials"

Expected AI Response:
🤖 COMPREHENSIVE RESEARCH PIPELINE ACTIVATED

**Objective**: Complete data-to-publication workflow
**Dataset**: Multiple files in data/final/
**Target**: Peer-reviewed publication in communication science

**Stage 1: Data Integration** (Analysis Agent)
📊 Comprehensive dataset analysis
- Merge multiple data sources
- Quality assessment and cleaning
- Exploratory analysis across all variables

**Stage 2: Hypothesis Testing** (Analysis Agent)
📊 Confirmatory statistical analysis
- Test specific hypotheses about research invisibility
- Advanced modeling (multilevel, network analysis)
- Effect size calculation and validation

**Stage 3: Visualization Suite** (Analysis Agent)
📊 Publication-quality graphics
- Interactive and static visualizations
- Network diagrams and flow charts
- Statistical graphics with confidence intervals

**Stage 4: Manuscript Preparation** (Documentation Agent)
📝 Academic manuscript writing
- Structure according to journal requirements
- APA formatting and citation management
- Integration of analysis results

**Stage 5: Supplementary Materials** (Documentation Agent)
📝 Supporting documentation
- Data and code availability statements
- Methodology appendices
- Replication instructions

**Stage 6: Project Management** (Automation Agent)
🔧 Organization and version control
- Final file organization
- Version control for submission
- Archive creation for reproducibility

[Detailed execution plan with milestones follows...]
```

## 💡 Tips for Effective Agent Interaction

### 1. Be Specific About Scope
❌ Vague: "Analyze some data"
✅ Clear: "Perform network analysis on the author collaboration data in creator_sample_clean.parquet"

### 2. Specify Output Requirements
❌ Generic: "Write something about this"
✅ Detailed: "Create a 2,000-word literature review in APA format with at least 30 recent references"

### 3. Provide Context
❌ Minimal: "Organize files"
✅ Contextual: "Organize project files according to academic research standards, separating raw data from processed results"

### 4. Use Domain Language
❌ General: "Look at relationships"
✅ Specific: "Conduct social network analysis to identify opinion leaders and information brokers"

### 5. Specify Quality Standards
❌ Unclear: "Make it good"
✅ Clear: "Follow APA style guidelines with proper statistical reporting and effect sizes"

## 🚀 Quick Reference Commands

**Research Tasks**:
- "Find literature on [topic] from [timeframe]"
- "Design a [type] study for [population] measuring [variables]"
- "Create a research plan for investigating [phenomenon]"

**Analysis Tasks**:
- "Analyze [dataset] for [specific patterns/relationships]"
- "Create [visualization type] showing [specific comparison]"
- "Test the hypothesis that [specific prediction]"

**Documentation Tasks**:
- "Write a [document type] summarizing [content] for [audience]"
- "Document the [process/tool] with [level of detail]"
- "Create [format] following [style guide] standards"

**Automation Tasks**:
- "Organize [scope] according to [standards]"
- "Commit [changes] with [type] message"
- "Setup [workflow/structure] for [purpose]"

---

## Example 2: From Data Analysis to Report Section (Multi-Agent Coordination)

**User Prompt**:
`"Analyze the 'data/final/title_pred_lang.parquet' file to find the top 10 most frequent languages. Then, write a 'Results' section for a research paper summarizing these findings, including a bar chart."`

**Expected AI Response**:
```markdown
This is a complex task that requires a multi-agent approach. I will coordinate the following agents to fulfill your request:

- **Primary Agent**: 📊 **Analysis Agent** will perform the data analysis and create the visualization.
- **Secondary Agent**: 📝 **Documentation Agent** will then write the 'Results' section based on the analysis output.
- **Support Agent**: 🔧 **Automation Agent** will ensure the generated chart is saved to the correct directory.

---
**Phase 1: Analysis Agent Execution**
---

**[📊 Analysis Agent Activated]**
- **Task**: Exploratory Data Analysis (EDA)
- **Dataset**: `data/final/title_pred_lang.parquet`
- **Objective**: To identify and visualize the top 10 most frequent languages based on the 'language_pred' column.

**1. Data Assessment & Cleaning:**
   - Loading the Parquet file into a pandas DataFrame.
   - The 'language_pred' column is the target for analysis. No significant data cleaning is required for this task.

**2. Descriptive Statistics & Visualization:**
   - Calculating frequency counts for the 'language_pred' column using `.value_counts()`.
   - Creating a bar chart of the top 10 languages with clear labels and title.
   - Saving the chart to `outputs/visualizations/language_distribution_top10.png`.

**3. Handoff to Documentation Agent:**
   - **Key Finding**: A summary table of the top 10 languages and their record counts.
   - **Visualization Path**: `outputs/visualizations/language_distribution_top10.png`.

---
**Phase 2: Documentation Agent Execution**
---

**[📝 Documentation Agent Activated]**
- **Task**: Write a 'Results' section for an academic paper.
- **Section**: Results
- **Target Journal Style**: APA 7th Edition
- **Core Inputs**: The frequency table and bar chart from the Analysis Agent.

**1. Structure & Content Outline:**
   - 1. Brief statement introducing the analysis of language distribution.
   - 2. Presentation of the top 10 languages and their frequencies in the text.
   - 3. Reference to the bar chart (Figure 1).
   - 4. A concluding sentence summarizing the distribution's key characteristic (e.g., skewness).

**2. Deliverable:**

### Results

An analysis of the predicted languages for all 19.8 million academic titles in the dataset revealed a highly concentrated distribution. Table 1 presents the top 10 most frequent languages, which collectively account for over 92% of the entire corpus.

English is the overwhelmingly dominant language, appearing in 15.5 million titles (78.2%). Following English, Spanish (6.1%) and Portuguese (4.3%) are the next most common languages. The distribution, as visualized in Figure 1, highlights the significant skew towards a small number of languages in global academic publishing.

*(Instruction to Automation Agent: Please ensure the bar chart created by the Analysis Agent is available at `outputs/visualizations/language_distribution_top10.png` and can be referenced as Figure 1 in the manuscript.)*
```
---

## Example 3: Git Commit and File Cleanup (Automation Agent)

**User Prompt**:
`"I've finished my script updates in the analysis folder. Please clean up any temporary files and commit the changes with an appropriate message."`

**Expected AI Response**:
```markdown
**[🔧 Automation Agent Activated]**
- **Task**: Git Commit and File Cleanup
- **Scope**: The `scripts/03_analysis/` directory and project root for temporary files.
- **Standard**: Adhere to project file structure and conventional commit standards.

---
**1. Assessment of Current State:**
   - **Scan**: Scanning project for temporary files and checking `git status`.
   - **Identify Misplaced Files**: No misplaced files found.
   - **Identify Temporary Files**: Found `__pycache__/` directories and one `.DS_Store` file.
   - **Identify Git Changes**: Found 2 modified files in `scripts/03_analysis/`.

**2. Proposed Action Plan:**

   - **Delete Operations**:
     - `rm -rf **/__pycache__`
     - `rm .DS_Store`
   - **Git Staging**:
     - `git add scripts/03_analysis/judge_creator.py`
     - `git add scripts/03_analysis/test_LLM_name_detect_parquet.py`
   - **Git Commit Message**:
     - `feat(analysis): Refine author analysis and sampling logic`
       - `- Improves statistical output in judge_creator.py.`
       - `- Optimizes sampling strategy in test_LLM_name_detect_parquet.py.`

**This plan will now be executed.**

---
**Execution Log:**

- ✅ Temporary files and directories successfully removed.
- ✅ Git staging completed for 2 files.
- ✅ Commit successfully created with message: `feat(analysis): Refine author analysis and sampling logic`.

**The changes have been committed locally. You can push them to the remote repository by running `git push`**
```
