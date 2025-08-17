# Multi-Agent Research Workflow for Cursor AI

## 🎯 Purpose & Scope

This document provides the operational framework for coordinating multiple AI agents in academic research workflows. It implements the enhanced two-round confirmation system and multi-task breakdown capabilities.

**Core Protocol**: See [Core Workflow](core-workflow.md) for detailed coordination protocol.

## 🤖 Agent System Overview

**Agent Capabilities**: See [Agent Reference Guide](agent-reference.md) for complete agent specifications, activation formats, and quality gates.

### Quick Agent Selection Guide
- **🔍 Research Tasks**: Literature reviews, study design, theoretical frameworks
- **📊 Analysis Tasks**: Data processing, statistical analysis, visualization
- **📝 Documentation Tasks**: Academic writing, formatting, reporting
- **🔧 Automation Tasks**: File management, GitHub workflows, project organization

## 🔄 Enhanced Two-Round Confirmation System

### Implementation Overview
All user requests now require **mandatory two-round confirmation** before execution:

1. **Round 1**: AI analyzes request and identifies information gaps
2. **Round 2**: AI presents complete understanding and waits for explicit approval

**Details**: See [Core Workflow](core-workflow.md) for complete confirmation protocols and multi-task breakdown procedures.

## 📋 Multi-Task Breakdown System

### Automatic Detection Triggers
The system automatically identifies multiple tasks when requests contain:
- **Conjunction words**: "and", "then", "also", "additionally"
- **Multiple domains**: Research + Analysis + Documentation
- **Sequential dependencies**: Tasks requiring ordered execution

### Task Management
- **Independent tasks**: Separate GitHub issues with no dependencies
- **Related tasks**: Linked issues with clear dependency chains  
- **Priority assignment**: Automatic ranking based on dependencies and complexity

**Details**: See [Core Workflow](core-workflow.md) for complete breakdown protocols.

## 🔗 Integration Points

### GitHub Workflow Integration
- **Issue Creation**: IMMEDIATE after user's final confirmation (before task execution)
- **PR Management**: For completed work requiring review
- **Review Processing**: For feedback integration and iteration

**Details**: See [GitHub Management](github-management.md) for complete workflows.

### Quality Assurance
- **Universal Standards**: Applied to all agent outputs
- **Agent-Specific Gates**: Tailored validation for each agent type
- **Academic Compliance**: Built-in checks for research standards

**Details**: See [Agent Reference Guide](agent-reference.md) for complete quality frameworks.

---

*This enhanced workflow ensures systematic, user-confirmed execution while maintaining academic rigor and efficient GitHub integration.*
