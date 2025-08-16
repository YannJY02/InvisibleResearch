# Agent Workflow Examples & Case Studies

## 🎯 How to Use This Guide

This comprehensive guide provides both quick reference examples and detailed case studies for the enhanced multi-agent system. Use these examples to structure your requests and understand expected AI responses.

**Quick Navigation:**
- **[Quick Reference Examples](#quick-reference-examples)**: Fast lookup for common tasks
- **[Complete Case Studies](#complete-case-studies)**: End-to-end workflow demonstrations
- **[Multi-Agent Coordination](#multi-agent-coordination-examples)**: Complex task management
- **[Interaction Tips](#tips-for-effective-agent-interaction)**: Best practices guide

---

# Quick Reference Examples

## 🔍 Research Agent Examples

### Literature Review Request
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

### Survey Design Request
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

### Dataset Analysis Request
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

## 📝 Documentation Agent Examples

### Research Report Request
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

[Continues with full academic report structure...]
```

## 🔧 Automation Agent Examples

### File Organization Request
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

---

# Complete Case Studies

## 📖 Case Study 1: Complete GitHub-Integrated Academic Workflow

### 🎯 Scenario: Language Pattern Analysis Request

This example demonstrates the complete workflow from user dialogue to final integration, showcasing the new GitHub management capabilities.

### Phase 1: User Dialogue & Issue Creation

**User Request**:
> "I want to analyze the language patterns in our `data/final/title_pred_lang.parquet` dataset. Specifically, I need to identify the top 10 most frequent languages, create visualizations, and write a Results section for our paper. This should include statistical analysis and proper academic formatting."

**AI Coordinator Response**:

#### 🎯 Task Analysis & Planning

**User Goal**: Comprehensive language pattern analysis with academic documentation
**Task Complexity**: Complex - requires multi-agent coordination and GitHub workflow
**Confidence Score**: 90% - requirements are clear and specific
**GitHub Integration**: Required - Issue creation and PR workflow needed

**Agent Assignment**:
- **Primary Agent**: 📊 **Analysis Agent** - data analysis and visualization
- **Secondary Agent**: 📝 **Documentation Agent** - Results section writing  
- **Support Agent**: 🔧 **Automation Agent** - GitHub management and project organization

[Continues with complete workflow demonstration...]

---

# Multi-Agent Coordination Examples

## Example: Complex Multi-Step Research Task
```
User: "I want to research misinformation spread in academic contexts, design a study, and create preliminary analysis tools"

Expected AI Response:
🤖 MULTI-AGENT COORDINATION ACTIVATED

**Task Breakdown**: 3 agents required for comprehensive execution
**Timeline**: Parallel and sequential task execution

[Detailed coordination example follows...]
```

---

# Tips for Effective Agent Interaction

## 1. Be Specific About Scope
❌ Vague: "Analyze some data"
✅ Clear: "Perform network analysis on the author collaboration data in creator_sample_clean.parquet"

## 2. Specify Output Requirements
❌ Generic: "Write something about this"
✅ Detailed: "Create a 2,000-word literature review in APA format with at least 30 recent references"

[Additional tips follow...]

---

*This comprehensive guide serves as your complete reference for agent interactions, from simple tasks to complex multi-agent workflows. All examples follow the enhanced two-round confirmation protocol and GitHub integration standards.*
