# Agent Prompt Templates for Cursor AI

## 🎯 Template Usage Guidelines

When the user's request triggers an agent, you **must** use the corresponding template below to structure your response. Fill in the bracketed placeholders `[ ]` with the specific details from the user's request. These templates are not suggestions; they are mandatory operational protocols.

---

## 🔍 Research Agent Templates

### Template 1.1: Comprehensive Literature Review
```markdown
**[🔍 Research Agent Activated]**
- **Task**: Comprehensive Literature Review
- **Topic**: [Specific Topic from User Request]
- **Scope**: [Temporal, geographical, or methodological boundaries, e.g., "2018-2024", "focusing on North American context"]
- **Discipline Focus**: Communication Science, integrating [cross-reference other fields like Political Science, Sociology if relevant].

---
**1. Search Strategy:**
   - **Primary Databases**: Communication & Mass Media Complete, Google Scholar, Scopus.
   - **Keywords**:
     - *Core*: [List 3-5 core keywords]
     - *Secondary*: [List 5-7 related keywords]
   - **Inclusion Criteria**: [e.g., "Peer-reviewed articles", "empirical studies"]
   - **Exclusion Criteria**: [e.g., "Blog posts", "non-academic sources"]

**2. Analysis & Synthesis Framework:**
   - **Identify Core Theories**: [e.g., "Agenda-Setting", "Framing Theory", "Selective Exposure"]. Reference `communication-science.md`.
   - **Map Methodological Trends**: Identify dominant methods (e.g., "Survey Research", "Content Analysis", "Network Analysis").
   - **Synthesize Key Findings**: Group findings by major themes.
   - **Identify Research Gaps**: Explicitly state what is not yet known or where contradictions exist.

**3. Deliverables:**
   - **Thematic Synthesis Report**: A structured narrative (approx. 1500 words) organized by the themes identified.
   - **Annotated Bibliography**: A list of the 15-20 most relevant articles, with a 2-3 sentence summary for each, in APA 7th edition format.
   - **Future Research Directions**: A bulleted list of 3-5 specific, actionable research questions that emerge from the gaps.
```

### Template 1.2: Survey/Questionnaire Design
```markdown
**[🔍 Research Agent Activated]**
- **Task**: Survey/Questionnaire Design
- **Research Question**: [Primary Research Question to be Answered]
- **Target Population**: [e.g., "Undergraduate students", "social media users aged 18-35"]
- **Key Constructs**: [List the main concepts to be measured, e.g., "Media Trust", "News Consumption Habits", "Political Efficacy"]

---
**1. Survey Structure:**
   - **Part 1: Consent & Introduction**: Briefing on the study's purpose, duration, and data privacy.
   - **Part 2: Screener Questions**: [If needed, to qualify participants].
   - **Part 3: Core Constructs**: Measurement items for each key construct.
   - **Part 4: Demographics**: [e.g., "Age", "Gender", "Education Level", "Political Affiliation"].
   - **Part 5: Debrief & Thank You**: Explanation and contact information.

**2. Measurement & Scale Development:**
   - **Validated Scales**: For each construct, I will first attempt to source a validated scale from the literature (e.g., "using the Media Trust Scale from Tsfati & Cappella, 2003").
   - **Custom Questions**: For constructs without a standard scale, I will develop clear, non-leading questions using a 7-point Likert scale (Strongly Disagree to Strongly Agree).
   - **Attention Checks**: Embed at least one validation question (e.g., "Please select 'Strongly Agree' for this item").

**3. Deliverables:**
   - **Complete Questionnaire**: A full draft of the survey in a text or markdown format.
   - **Data Collection Protocol**: Recommendations for platform (e.g., Qualtrics, Google Forms) and sampling strategy (e.g., "convenience sampling via university email lists").
   - **Pre-analysis Plan**: An outline of the statistical tests to be performed once data is collected (e.g., "correlation analysis between Media Trust and News Consumption scores").
```

---

## 📊 Analysis Agent Templates

### Template 2.1: Exploratory Data Analysis (EDA)
```markdown
**[📊 Analysis Agent Activated]**
- **Task**: Exploratory Data Analysis (EDA)
- **Dataset**: [Full path to the dataset file, e.g., `data/final/title_pred_lang.parquet`]
- **Objective**: To uncover initial patterns, distributions, and relationships within the data.

---
**1. Data Assessment & Cleaning:**
   - **Load Data**: Read the dataset into a pandas DataFrame.
   - **Inspect Structure**: Report `df.info()`, `df.shape`, and `df.columns`.
   - **Check for Missing Values**: Report `df.isnull().sum()` and suggest an imputation strategy if necessary (e.g., "mean imputation for numeric columns").
   - **Identify Outliers**: Use boxplots or IQR method to identify potential outliers in key numeric variables.

**2. Descriptive Statistics & Visualization:**
   - **Numeric Variables**: Generate and report summary statistics (`df.describe()`). Create histograms or density plots to visualize distributions.
   - **Categorical Variables**: Generate and report frequency counts (`.value_counts()`). Create bar charts to visualize distributions.
   - **Correlations**: For numeric variables, compute a correlation matrix and visualize it as a heatmap.

**3. Deliverables:**
   - **EDA Summary Report**: A markdown report detailing the findings from steps 1 & 2.
   - **Visualizations**: Generate and save key plots (histograms, bar charts, heatmap) to the `outputs/visualizations/` directory with descriptive filenames.
   - **Initial Insights**: A bulleted list of 3-5 key observations or patterns (e.g., "The 'language' column is heavily skewed towards English," "A moderate positive correlation exists between variable X and Y").
```

### Template 2.2: Statistical Hypothesis Testing
```markdown
**[📊 Analysis Agent Activated]**
- **Task**: Statistical Hypothesis Testing
- **Dataset**: [Full path to the dataset file]
- **Research Hypothesis**: [State the H1 and H0 hypotheses clearly, e.g., "H1: There is a significant difference in media trust scores between high and low social media users."]

---
**1. Analysis Plan:**
   - **Variables**:
     - *Independent Variable (IV)*: [Name and operationalization of the IV]
     - *Dependent Variable (DV)*: [Name and operationalization of the DV]
   - **Statistical Test**: [Select appropriate test based on data types, e.g., "Independent Samples t-test", "ANOVA", "Chi-Square Test"]. Justify the choice.
   - **Assumptions**: List the assumptions of the chosen test (e.g., "Normality", "Homogeneity of variances") and the plan to check them.

**2. Execution & Interpretation:**
   - **Check Assumptions**: Perform and report the results of assumption tests (e.g., "Shapiro-Wilk test for normality," "Levene's test for homogeneity").
   - **Run Test**: Execute the primary statistical test.
   - **Report Results**: Report the test statistic, p-value, and effect size in APA 7th edition format (e.g., "t(98) = 2.34, p = .021, d = 0.47").
   - **Interpret**: State the conclusion in plain language, referencing the hypothesis (e.g., "The results indicate a statistically significant difference... We therefore reject the null hypothesis.").

**3. Deliverables:**
   - **Analysis Report**: A full report detailing the plan, assumption checks, results, and interpretation.
   - **Visualization**: A plot that visualizes the results (e.g., a bar chart with error bars showing the means of the two groups).
   - **Code Snippet**: The Python code (using `scipy.stats` or `statsmodels`) used to conduct the analysis.
```

---

## 📝 Documentation Agent Templates

### Template 3.1: Academic Report Section
```markdown
**[📝 Documentation Agent Activated]**
- **Task**: Write a section for an academic paper.
- **Section**: [e.g., "Introduction", "Methodology", "Discussion"]
- **Target Journal Style**: [e.g., "Journal of Communication (APA 7)"]
- **Core Inputs**: [e.g., "Results from Analysis Agent", "Themes from Research Agent's literature review"]

---
**1. Structure & Content Outline:**
   - [Develop a 3-5 point outline for the section. For a Discussion section, this would be:]
   - 1. Summary of key findings.
   - 2. Interpretation of findings in light of existing literature and theory (from `communication-science.md`).
   - 3. Theoretical and practical implications.
   - 4. Limitations of the study.
   - 5. Directions for future research.

**2. Writing Execution:**
   - **Tone**: Maintain a formal, objective, and scholarly tone.
   - **Citations**: Integrate citations appropriately in APA 7 format.
   - **Flow & Transitions**: Use clear topic sentences and transition phrases to ensure logical flow between paragraphs.
   - **Compliance**: Adhere strictly to the target journal's style guide for formatting headings, tables, and figures.

**3. Deliverable:**
   - **Formatted Text**: The complete, formatted text for the requested section as a markdown block.
```

---

## 🔧 Automation Agent Templates

### Template 4.1: File Organization & Cleanup
```markdown
**[🔧 Automation Agent Activated]**
- **Task**: Organize project files.
- **Scope**: [e.g., "The entire project directory", "The `outputs/` folder"]
- **Standard**: Adhere to the project's established file structure (as defined in `README.md` or other documentation).

---
**1. Assessment of Current State:**
   - **Scan**: Recursively list files in the target scope.
   - **Categorize**: Classify files by type (e.g., `.py`, `.ipynb`, `.csv`, `.png`, `.md`).
   - **Identify Misplaced Files**: Find files that are not in their conventional locations (e.g., data files outside `data/`, plots outside `outputs/visualizations/`).
   - **Identify Temporary Files**: Find and list files to be deleted (e.g., `__pycache__`, `*.tmp`, `.DS_Store`).

**2. Proposed Action Plan (Requires User Confirmation):**
   - **Move Operations**:
     - [List each file/directory to be moved and its destination. `mv source -> destination`]
   - **Rename Operations**:
     - [List each file to be renamed. `mv old_name -> new_name`]
   - **Delete Operations**:
     - [List all temporary/unnecessary files to be deleted. `rm path/to/file`]

**3. Execution:**
   - Upon user confirmation, execute the `mv` and `rm` commands as a shell script.

**4. Deliverable:**
   - **Action Log**: A summary of all actions taken (files moved, renamed, deleted).
   - **Confirmation**: A final message confirming "Project files have been successfully organized."
```

### Template 4.2: Git Commit & Push
```markdown
**[🔧 Automation Agent Activated]**
- **Task**: Git Commit and Push
- **Changes**: [Briefly describe the changes, e.g., "Updated analysis scripts and added new visualizations"]
- **Branch**: [Target branch, e.g., `main`, `feature/new-analysis`]

---
**1. Pre-Commit Checklist:**
   - **Staging**: `git status` to review modified and untracked files. I will stage all relevant files.
   - **Linting**: Run linter on changed Python files to ensure code quality.
   - **Documentation**: Verify that related `README.md` or other docs are updated.

**2. Conventional Commit Message Construction:**
   - **Type**: Select from `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
   - **Scope**: Identify the part of the codebase affected (e.g., `analysis`, `data`, `docs`).
   - **Subject**: Write a concise, imperative-mood summary (e.g., "Add community detection to network analysis").
   - **Body (Optional)**: Provide more context on the changes.

**3. Execution (Requires User Confirmation):**
   - **Staging Command**: `git add [file1] [file2] ...`
   - **Commit Command**: `git commit -m "type(scope): subject"`
   - **Push Command**: `git push origin [branch]`

**4. Deliverable:**
   - **Action Log**: The exact git commands executed.
   - **Confirmation**: A link to the commit on the remote repository if possible.
```

### Template 4.3: GitHub Issue Creation
```markdown
**[🔧 Automation Agent - GitHub Integration]**
- **Task**: Create GitHub Issue from user dialogue
- **Input**: User research request or project need
- **Output**: Structured GitHub Issue with proper classification and metadata

---
**1. Requirement Analysis:**
   - **Extract Core Need**: Identify the main research goal or project requirement from user dialogue
   - **Classify Issue Type**: Determine appropriate category (research-task, enhancement, bug, documentation, data-management)
   - **Assess Complexity**: Evaluate scope and determine if task should be broken into sub-issues
   - **Identify Dependencies**: List prerequisite tasks or data requirements

**2. Issue Content Generation:**
   - **Title**: Create clear, descriptive title following pattern: "[TYPE] Brief description"
   - **Description**: Use appropriate academic template based on issue type
   - **Labels**: Auto-assign based on content analysis (research, analysis, documentation, etc.)
   - **Milestone**: Link to relevant research phase or project milestone
   - **Assignee**: Suggest appropriate team member or leave for manual assignment

**3. Branch Strategy:**
   - **Branch Name**: Generate following convention: `[type]/[descriptive-name]`
   - **Base Branch**: Determine appropriate base (main, develop, or feature branch)
   - **Workflow**: Outline expected development workflow for this issue

**4. Deliverable:**
   - **Issue Draft**: Complete GitHub issue content ready for creation
   - **Branch Command**: `git checkout -b [branch-name]` command
   - **Next Steps**: Clear outline of implementation approach
```

### Template 4.4: Pull Request Management
```markdown
**[🔧 Automation Agent - PR Workflow]**
- **Task**: Create and manage Pull Request for completed work
- **Input**: Completed work on feature branch, original issue reference
- **Output**: Structured PR with academic review checklist and merge strategy

---
**1. PR Preparation:**
   - **Branch Status**: Verify all changes committed and pushed to feature branch
   - **Issue Linkage**: Confirm PR addresses original issue requirements
   - **Conflict Check**: Identify any merge conflicts with target branch
   - **Quality Validation**: Run pre-PR checklist (tests, linting, documentation)

**2. PR Content Generation:**
   - **Title**: Format as "Fix #[issue-number]: [descriptive title]"
   - **Description**: Comprehensive summary using academic PR template
   - **Changes Summary**: List all files modified, added, or deleted
   - **Testing Evidence**: Document validation and testing performed
   - **Impact Assessment**: Describe effects on research pipeline and documentation

**3. Review Setup:**
   - **Reviewers**: Suggest appropriate reviewers based on content type
   - **Review Checklist**: Apply academic quality standards checklist
   - **Merge Conditions**: Set requirements for safe merge (tests pass, reviews approved)
   - **Documentation Updates**: Identify related documentation that needs updating

**4. Deliverable:**
   - **PR Draft**: Complete pull request content ready for creation
   - **Review Assignment**: Suggested reviewers and review criteria
   - **Merge Strategy**: Recommended merge approach (squash, rebase, or merge commit)
```

### Template 4.5: Review Response & Iteration
```markdown
**[🔧 Automation Agent - Review Integration]**
- **Task**: Process human review feedback and implement requested changes
- **Input**: PR review comments, suggestions, and change requests
- **Output**: Updated implementation addressing all feedback with clear documentation

---
**1. Feedback Analysis:**
   - **Categorize Comments**: Sort feedback by type (bugs, improvements, questions, style)
   - **Prioritize Changes**: Rank feedback by importance and complexity
   - **Clarification Needs**: Identify comments requiring clarification from reviewer
   - **Scope Assessment**: Determine if changes require additional research or data

**2. Implementation Planning:**
   - **Change Strategy**: Outline approach for each requested modification
   - **Testing Plan**: Define how changes will be validated
   - **Documentation Impact**: Identify documentation updates needed
   - **Timeline Estimate**: Provide realistic timeline for implementing changes

**3. Change Implementation:**
   - **Code Updates**: Make requested changes with clear, descriptive commits
   - **Testing**: Validate changes against original requirements and new feedback
   - **Documentation**: Update comments, docstrings, and related documentation
   - **Self-Review**: Verify changes meet academic and technical standards

**4. Response Communication:**
   - **Change Summary**: Document what was changed in response to each comment
   - **Testing Evidence**: Provide proof that changes work as expected
   - **Clarification Requests**: Ask for clarification on ambiguous feedback
   - **Ready for Re-review**: Clearly indicate PR is ready for another review cycle

**5. Deliverable:**
   - **Updated PR**: All changes implemented and pushed to feature branch
   - **Response Comments**: Detailed response to each review comment
   - **Change Documentation**: Clear record of what was modified and why
```

### Template 4.6: Project Milestone Management
```markdown
**[🔧 Automation Agent - Project Management]**
- **Task**: Manage GitHub project milestones and track research progress
- **Input**: Project status, completed tasks, upcoming deadlines
- **Output**: Updated project board and milestone tracking

---
**1. Progress Assessment:**
   - **Completed Issues**: Review recently closed issues and their impact
   - **Active Work**: Assess progress on current issues and PRs
   - **Blocked Tasks**: Identify issues waiting on dependencies or review
   - **Milestone Status**: Calculate progress toward current milestone goals

**2. Project Board Update:**
   - **Move Cards**: Update issue status on project board (Backlog → In Progress → Review → Done)
   - **Priority Adjustment**: Reorder tasks based on research priorities and dependencies
   - **Capacity Planning**: Assess workload and suggest task redistribution
   - **Bottleneck Identification**: Identify process bottlenecks and suggest solutions

**3. Milestone Management:**
   - **Progress Reporting**: Generate milestone progress report with completion percentages
   - **Timeline Adjustment**: Suggest milestone date adjustments if needed
   - **Scope Management**: Recommend issue additions/removals based on research priorities
   - **Next Milestone**: Prepare and plan next research phase milestone

**4. Communication:**
   - **Status Update**: Generate project status summary for stakeholders
   - **Risk Assessment**: Identify potential delays or resource needs
   - **Success Metrics**: Report on research output and quality metrics
   - **Next Steps**: Clear action items for maintaining project momentum

**5. Deliverable:**
   - **Updated Project Board**: Current status reflected accurately
   - **Milestone Report**: Progress summary with key metrics
   - **Action Plan**: Specific steps to maintain or improve project velocity
```
