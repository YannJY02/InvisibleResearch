# GitHub Management Protocol for Academic Projects

## 🎯 Overview
This protocol extends the multi-agent system to provide comprehensive GitHub-based project management for academic research workflows. It enables the complete cycle: **Dialogue → Issue → Implementation → Review → Integration**.

## 🛠️ GitHub CLI Integration Requirement

**MANDATORY**: All GitHub operations must use command-line automation rather than manual processes.

### Required Tools
- **GitHub CLI**: Install with `brew install gh` 
- **Authentication**: Configure with `gh auth login`
- **Repository Access**: Verify with `gh repo view`

### Automated Operations
- **Issue Creation**: Use `gh issue create` with structured templates
- **PR Management**: Use `gh pr create` with automatic issue linking
- **Project Tracking**: Complete CLI-based workflow for all GitHub operations

## 📋 Core GitHub Workflow Components

### 1. Issue Management Protocol

#### 1.1 Immediate Issue Creation After User Confirmation
**CRITICAL**: After the user's final confirmation in the two-round confirmation process, the AI must **immediately** create GitHub Issue(s):

```markdown
**[🔧 Automation Agent - Issue Creation Mode]**
- **Task**: Convert confirmed user requirements to GitHub Issue
- **Trigger**: User's final confirmation after two-round confirmation process
- **Timing**: IMMEDIATE - must occur before task execution begins
- **Process**:
  1. Extract confirmed requirements from two-round dialogue
  2. Classify issue type (enhancement, bug, research-task, documentation)
  3. Generate structured issue using appropriate template
  4. Use `gh issue create` command to upload immediately
  5. Provide GitHub Issue URL to user for tracking
  6. Create branch name suggestion following naming convention
  7. Only after Issue creation, begin task execution
```

#### 1.2 Issue Classification System
| Issue Type | Labels | Branch Prefix | Description |
|------------|---------|---------------|-------------|
| **Research Task** | `research`, `analysis` | `research/` | Literature review, data analysis, methodology |
| **Enhancement** | `enhancement`, `feature` | `feature/` | New functionality, tool improvements |
| **Bug Fix** | `bug`, `hotfix` | `hotfix/` | Error corrections, data cleaning |
| **Documentation** | `documentation`, `writing` | `docs/` | Papers, reports, README updates |
| **Data Management** | `data`, `pipeline` | `data/` | Data processing, ETL, validation |

#### 1.3 Issue Templates

**Research Task Template:**
```markdown
## 🔬 Research Task: [Title]

### 📋 Objective
[Clear statement of research goal]

### 📊 Data Requirements
- **Input Data**: [Specify files/databases needed]
- **Expected Output**: [Describe deliverables]
- **Dependencies**: [List prerequisite tasks]

### 🎯 Methodology
- **Approach**: [Quantitative/Qualitative/Mixed]
- **Tools**: [Statistical tests, software, libraries]
- **Standards**: [APA, reproducibility requirements]

### ✅ Acceptance Criteria
- [ ] Data analysis completed
- [ ] Results documented following academic standards
- [ ] Code reviewed and tested
- [ ] Findings integrated into project

### 🏷️ Labels
[Auto-assigned based on content]
```

### 2. Branch Management Strategy

#### 2.1 Academic GitFlow
```
main
├── develop
│   ├── feature/literature-review-echo-chambers
│   ├── feature/network-analysis-implementation
│   └── research/language-pattern-analysis
├── data/preprocessing-pipeline-v2
├── docs/methodology-update
└── hotfix/name-parsing-bug
```

#### 2.2 Branch Naming Conventions
- **Research**: `research/[topic-description]`
- **Features**: `feature/[functionality-name]`
- **Data**: `data/[processing-stage]`
- **Documentation**: `docs/[document-type]`
- **Hotfixes**: `hotfix/[issue-description]`

### 3. Pull Request Workflow

#### 3.1 PR Creation Protocol
```markdown
**[🔧 Automation Agent - PR Management Mode]**
- **Task**: Create and manage Pull Request
- **Inputs**: Completed work on feature branch, original issue reference
- **Process**:
  1. Generate PR title linking to original issue
  2. Auto-populate PR description with work summary
  3. Apply academic review checklist
  4. Assign reviewers based on content type
  5. Set merge conditions and quality gates
```

#### 3.2 Academic PR Template
```markdown
## 📝 Pull Request: [Title]

### 🔗 Related Issue
Closes #[issue-number]

### 📋 Changes Summary
- [List of changes made]
- [Files modified/added]
- [Methodology updates]

### 🧪 Testing & Validation
- [ ] Code tested with sample data
- [ ] Results reproducible
- [ ] Documentation updated
- [ ] Academic standards verified

### 📊 Academic Review Checklist
- [ ] **Methodology Sound**: Approach follows academic standards
- [ ] **Reproducible**: Code can be run by others
- [ ] **Documented**: Clear comments and documentation
- [ ] **Data Quality**: Input/output data validated
- [ ] **Citation Ready**: Proper attribution and references

### 🎯 Impact Assessment
**Research Impact**: [How this affects ongoing research]
**Data Pipeline**: [Changes to data processing]
**Documentation**: [Updates to papers/reports needed]
```

### 4. Review & Iteration Protocol

#### 4.1 Multi-Round Review Cycle
```mermaid
graph LR
    A[AI Implementation] --> B[Create PR]
    B --> C[Human Review]
    C --> D{Approved?}
    D -->|No| E[AI Iteration]
    E --> F[Update PR]
    F --> C
    D -->|Yes| G[Merge & Close Issue]
    G --> H[Update Documentation]
```

#### 4.2 Review Response Protocol
When human reviewer provides feedback, AI must:
1. **Acknowledge**: Confirm understanding of feedback
2. **Plan**: Outline specific changes to be made
3. **Implement**: Make requested changes
4. **Validate**: Test changes against acceptance criteria
5. **Update**: Push changes and update PR description

### 5. Project Management Integration

#### 5.1 Milestone Tracking
```markdown
**Research Phase Milestones:**
- 🔍 **Data Collection** (Issues: #1-5)
- 📊 **Analysis** (Issues: #6-12)
- 📝 **Documentation** (Issues: #13-18)
- 🚀 **Publication** (Issues: #19-25)
```

#### 5.2 Progress Visualization
Use GitHub Projects with columns:
- **Backlog**: Identified tasks not yet started
- **In Progress**: Active development
- **Review**: Awaiting human review
- **Testing**: Validation and quality checks
- **Done**: Completed and integrated

## 🛠️ Implementation Templates

### Template 1: Immediate Issue Creation After Confirmation
```markdown
**[🔧 Automation Agent - GitHub Integration]**
- **Task**: Create GitHub Issue immediately after user's final confirmation
- **Input**: Confirmed requirements from two-round dialogue
- **Timing**: BEFORE task execution begins
- **Output**: Structured GitHub Issue with proper classification and tracking URL

**Process**:
1. **Extract Confirmed Requirements**: [From final confirmation dialogue]
2. **Classify Task Type**: [Research/Enhancement/Bug/Documentation]
3. **Generate Issue Content**: [Use appropriate template with full requirements]
4. **Execute CLI Command**: [Use `gh issue create` to upload immediately]
5. **Provide Tracking**: [Share GitHub Issue URL with user]
6. **Create Branch Strategy**: [Suggest branch name and workflow]
7. **Proceed to Execution**: [Begin task only after Issue creation]

**Deliverable**: GitHub Issue URL for immediate tracking, then task execution
```

### Template 2: PR Review Integration
```markdown
**[🔧 Automation Agent - Review Integration]**
- **Task**: Process human review feedback and iterate
- **Input**: PR review comments and suggestions
- **Output**: Updated implementation addressing all feedback

**Process**:
1. **Parse Feedback**: [Categorize comments by type and priority]
2. **Plan Changes**: [Create specific action items]
3. **Implement Updates**: [Make code/documentation changes]
4. **Self-Review**: [Validate changes against academic standards]
5. **Update PR**: [Push changes with clear commit messages]

**Deliverable**: Updated PR with addressed feedback and summary of changes
```

## 📊 Quality Gates & Standards

**Universal Quality Standards**: See [Agent Reference Guide](agent-reference.md) for complete academic and technical quality checklists.

**GitHub-Specific Quality Requirements**:
- [ ] **Issue Clarity**: Clear, actionable issue descriptions
- [ ] **PR Completeness**: All required sections filled in PR template
- [ ] **Review Responsiveness**: Timely response to review feedback
- [ ] **Documentation Sync**: All changes reflected in project documentation

---

*This protocol ensures that every research task follows a structured, reviewable, and academically rigorous development process while maintaining the flexibility needed for iterative research workflows.*
