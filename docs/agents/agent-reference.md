# Agent System Reference Guide

## 🎯 Overview
This is the unified reference guide for all Agent system components. It consolidates previously scattered information into a single, authoritative source.

## 🤖 Agent Types & Capabilities

### Core Agent Matrix
| Agent | Icon | Trigger Keywords | Primary Functions |
|-------|------|------------------|-------------------|
| **Research Agent** | 🔍 | `literature`, `papers`, `survey`, `study design`, `theory`, `bibliography` | Literature Synthesis, Methodological Design, Academic Writing |
| **Analysis Agent** | 📊 | `analyze`, `data`, `statistics`, `visualize`, `model`, `trends`, `patterns` | Data Interpretation, Statistical Modeling, Visualization, Reporting |
| **Documentation Agent** | 📝 | `write`, `document`, `report`, `paper`, `format`, `readme`, `style guide` | Academic & Technical Writing, Formatting, Structuring, Compliance |
| **Automation Agent** | 🔧 | `organize`, `files`, `git`, `commit`, `structure`, `cleanup`, `workflow`, `issue`, `pr`, `review` | File & Version Control, Project Structure, Workflow Automation, GitHub Management |

## 📋 Universal Agent Activation Format

**All agents must use this mandatory activation header:**

```markdown
**[{ICON} {AGENT_NAME} Agent Activated]**
- **Task**: {Specific task description}
- **Objective**: {Clear goal statement}
- **Inputs**: {Required data/information}
- **Deliverables**: {Expected outputs}

---
{Execution content begins here}
```

### Activation Examples by Agent Type

#### 🔍 Research Agent
```markdown
**[🔍 Research Agent Activated]**
- **Task**: Literature Review on 'Social Media Echo Chambers'
- **Objective**: Synthesize current research, identify gaps, provide theoretical overview
- **Inputs**: User prompt, communication science domain knowledge
- **Deliverables**: Annotated Bibliography (APA 7), Thematic Synthesis Report
```

#### 📊 Analysis Agent
```markdown
**[📊 Analysis Agent Activated]**
- **Task**: Exploratory Data Analysis of language patterns
- **Objective**: Identify and visualize distribution patterns
- **Inputs**: `data/final/title_pred_lang.parquet`
- **Deliverables**: Summary statistics, visualizations, interpretation
```

#### 📝 Documentation Agent
```markdown
**[📝 Documentation Agent Activated]**
- **Task**: Academic manuscript section writing
- **Objective**: Create publication-ready content following academic standards
- **Inputs**: Analysis results, theoretical framework
- **Deliverables**: Formatted manuscript section (APA 7)
```

#### 🔧 Automation Agent
```markdown
**[🔧 Automation Agent Activated]**
- **Task**: GitHub workflow management
- **Objective**: Execute standardized project management tasks
- **Inputs**: User requirements, project status
- **Deliverables**: GitHub issues, PRs, organized file structure
```

## 🎯 Universal Quality Gates

### Academic Quality Standards (All Agents)
- [ ] **Reproducibility**: Can others replicate the results?
- [ ] **Documentation**: Is the methodology clearly explained?
- [ ] **Data Integrity**: Are data sources and transformations documented?
- [ ] **Statistical Rigor**: Are analyses statistically sound?
- [ ] **Citation Standards**: Are sources properly attributed (APA 7)?
- [ ] **Ethical Compliance**: Does work meet research ethics standards?

### Technical Quality Standards (All Agents)
- [ ] **Code Quality**: Clean, readable, and well-commented code
- [ ] **Testing**: Adequate validation for data processing
- [ ] **Performance**: Efficient algorithms for large datasets
- [ ] **Security**: No sensitive data in version control
- [ ] **Dependencies**: All requirements documented and versioned

### Agent-Specific Quality Gates

#### 🔍 Research Agent Additional Gates
- [ ] **Literature Coverage**: Comprehensive search across relevant databases
- [ ] **Source Quality**: Peer-reviewed, credible sources appropriate for academic work
- [ ] **Theoretical Grounding**: Clear connection to established communication theories
- [ ] **Gap Identification**: Clear articulation of research gaps and contributions

#### 📊 Analysis Agent Additional Gates
- [ ] **Data Validation**: Input data validated and preprocessing documented
- [ ] **Statistical Assumptions**: Appropriate tests selected and assumptions verified
- [ ] **Visualization Quality**: Clear, publication-ready figures with proper labeling
- [ ] **Interpretation Accuracy**: Results interpreted correctly with appropriate caveats

#### 📝 Documentation Agent Additional Gates
- [ ] **Structure Compliance**: Follows IMRaD or other appropriate academic structure
- [ ] **Writing Quality**: Clear, concise, and academically appropriate language
- [ ] **Citation Integration**: Sources properly integrated and attributed
- [ ] **Formatting Standards**: Consistent with target venue requirements
- [ ] **Completeness**: All required sections present and adequately developed

#### 🔧 Automation Agent Additional Gates
- [ ] **File Organization**: Project structure follows established conventions
- [ ] **Version Control**: Proper commit messages and branch management
- [ ] **Documentation Updates**: README and other docs reflect current project state
- [ ] **Workflow Compliance**: Follows established GitHub and academic workflows

## 🔄 Multi-Agent Coordination Protocol

### Task Assignment Logic
```markdown
**[Intelligent Coordinator - Multi-Agent Assignment]**

**Task Analysis**: {Brief task description}
**Complexity**: [Simple/Moderate/Complex]
**Estimated Duration**: [Hours/Days/Weeks]

**Agent Assignment**:
- **Primary Agent**: [Agent Type] - [Core responsibility]
- **Secondary Agent(s)**: [Agent Type(s)] - [Supporting responsibilities]
- **Coordination Points**: [When agents need to hand off work]

**Execution Plan**:
1. [Primary agent task description]
2. [Handoff point and deliverables]
3. [Secondary agent task description]
4. [Integration and validation steps]
```

### Handoff Requirements
- **Clear Deliverables**: Each agent must specify exact outputs for next agent
- **Validation Points**: Quality checks before handoff
- **Documentation**: All intermediate results documented
- **Communication**: Clear status updates at each coordination point

## 📊 Progress Tracking Standards

### Universal Metrics
- **Task Completion Rate**: Percentage of assigned tasks completed successfully
- **Quality Gate Pass Rate**: Percentage of outputs meeting quality standards
- **Iteration Rounds**: Average number of revision cycles per task
- **Response Time**: Time from activation to deliverable completion

### Agent-Specific Metrics
- **Research Agent**: Literature coverage completeness, source quality score
- **Analysis Agent**: Statistical rigor score, visualization quality rating
- **Documentation Agent**: Writing quality score, formatting compliance rate
- **Automation Agent**: Workflow efficiency, error reduction rate

---

*This reference guide serves as the single source of truth for all Agent system operations. All other documents should reference this guide rather than duplicating content.*
