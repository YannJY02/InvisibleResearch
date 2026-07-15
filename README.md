# Invisible Research: Uncovering Hidden Academic Scholarship

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 📖 Project Overview

The Invisible Research project confronts the critical issue of academic invisibility, emphasizing the urgent need to identify, quantify, and elevate valuable research outputs overlooked due to language barriers, publication biases, institutional prestige hierarchies, and limited digital discoverability.

## 🚀 Quick Start

### Environment Setup
```bash
git clone https://github.com/theinvisiblelab/invisible-research.git
cd invisible-research
python -m venv environments/venv
source environments/venv/bin/activate
pip install -r requirements.txt
```

### 🔐 API Configuration
For LLM-based author processing, configure your API credentials:

```bash
# 1. Copy the configuration template
cp .env.example .env

# 2. Edit .env with your actual API key
# OPENAI_API_KEY=your_api_key_here
# OPENAI_BASE_URL=https://your-proxy.com/v1  # Optional

# 3. The .env file is automatically ignored by git for security
```

📋 **See [Security Guide](docs/SECURITY_GUIDE.md) for detailed configuration instructions and best practices.**

### Run Shared Capabilities
```bash
# Point commands at the external data workspace
export DATA_ROOT=/path/to/data
export PYTHONPATH=src

# Data extraction
export MYSQL_URI=mysql+pymysql://user:password@host/database
python -m invisible_research.acquisition.database_extract

# Author analysis
python research/author-name-sampling/analysis/inspect_creators.py
python research/author-name-sampling/analysis/sample_creators.py

# Intelligent processing (requires API configuration)
OPENAI_API_KEY=your_key python -m invisible_research.processing.author_names_llm

# Language detection
python -m invisible_research.processing.title_language

# LLM validation (optional - for accuracy assessment)
python -m invisible_research.validation.start
```

## 📊 Data Sources

### Core Database
- **Scale**: ~20 million OAI-PMH records
- **Time span**: 2000-2024  
- **Languages**: 100+ languages
- **Sources**: 7000+ academic repositories

### High-Performance ArticleInfo Database
- **Format**: Apache Parquet (compressed)
- **Records**: 29.9 million processed academic papers
- **Size**: 3.8 GB (73% compression from 14.2GB CSV)
- **Performance**: 5-20x faster queries vs CSV
- **Schema**: 16 optimized columns with proper data types
- **Integration**: Seamless compatibility with existing analysis pipeline

**📋 See detailed specification**: [`docs/ARTICLEINFO_DATABASE.md`](docs/ARTICLEINFO_DATABASE.md)

## 🔬 Methodology

1. **Data Extraction**: OAI-PMH batch harvesting, MySQL storage
2. **Author Parsing**: GPT-4o intelligent processing of complex author fields
3. **Language Detection**: GlotLID multilingual identification
4. **Validation System**: Comprehensive manual validation suite for LLM accuracy assessment

## 🛠️ Project Structure

```
src/invisible_research/acquisition/ # Shared acquisition
src/invisible_research/processing/  # Shared processing
src/invisible_research/validation/  # Shared validation
research/              # Question- and experiment-owned Exploratory Analysis
├── article-metadata-conversion/
├── author-name-sampling/
├── dimensions-dataset-construction/
├── openalex-dataset-construction/
└── scimago-openalex-coverage/
papers/                # Publication Compendia; placement grants no authority
└── invisible-communication-science/
meeting-reports/       # Project-wide Supervisor Meeting Reports
inbox/                 # Local-only, non-authoritative raw intake
$DATA_ROOT/raw/         # External raw data
$DATA_ROOT/processed/   # External intermediate results
$DATA_ROOT/derived/     # External derived outputs
$DATA_ROOT/validation/  # External validation data and reports
data/artifact-versions/ # Tracked portable records for external content identities
```

### 🔄 Shared capabilities vs research owners
- **Shared capabilities**: Reusable acquisition, processing, and validation under `src/`
- **Research owners**: Question-specific orchestration and instructions under `research/`
- **Notebooks**: Interactive adapters over the analysis command owned by the same lane
- **Artifacts**: Regenerable owner outputs stay ignored under `research/*/artifacts/`
- **Publication Compendium**: Active paper sources and governance boundaries live under `papers/`
- **Supervisor Meeting Reports**: Date-named project updates live under `meeting-reports/`
- **Intake Inbox**: Raw communications and papers remain ignored under `inbox/`

The current paper-facing source and its external input verification command are
documented in [`papers/invisible-communication-science/`](papers/invisible-communication-science/README.md).

Project-level supervisor and group-meeting updates are indexed in
[`meeting-reports/`](meeting-reports/README.md).

**📋 For detailed data-script relationships**: See [`docs/DATA_SCRIPT_MAPPING.md`](docs/DATA_SCRIPT_MAPPING.md)

## 🔍 LLM Validation Suite

The project includes a comprehensive validation system for assessing the accuracy of GPT-4o's named entity extraction in author processing.

### Features
- **Interactive Web Interface**: Streamlit-based validation dashboard
- **External Verification**: Integration with CrossRef, ORCID, and Google Scholar
- **Multilingual Support**: Chinese/English interface and report generation
- **Data Protection**: Multi-layer backup system with automatic recovery
- **Comprehensive Reporting**: HTML, CSV, and JSON output formats with statistical analysis

### Quick Start
```bash
# Launch validation interface
DATA_ROOT=/path/to/data PYTHONPATH=src python -m invisible_research.validation.start
# Access: http://localhost:8501

# Launch data protection dashboard
DATA_ROOT=/path/to/data PYTHONPATH=src python -m streamlit run src/invisible_research/validation/protection_dashboard.py --server.port 8502
# Access: http://localhost:8502
```

### System Requirements
```bash
pip install streamlit matplotlib seaborn plotly jinja2
```

## 🤖 Multi-Agent Research Workflow

This project is enhanced with a **protocol-driven, multi-agent research system** designed for Cursor AI. It transforms natural language requests into rigorous, academic-standard outputs.

**🎯 How it Works**: The system acts as an intelligent coordinator. It analyzes your request, clarifies ambiguities, assigns expert agent roles (e.g., Research, Analysis, Documentation), and executes tasks using structured, professional protocols.

**💬 Natural Language Interface**: Simply describe your high-level goal. The system handles the rest.
- `"Find literature on social media's impact on political trust."`
- `"Analyze our dataset for language patterns and write a results section."`
- `"Organize the project files and commit the recent changes."`

**📖 System Documentation & Examples**:
- **Core AI Protocol**: The AI's behavior is governed by high-level rules in [`.cursor/rules/`](.cursor/rules/).
- **Detailed Agent Guides**: For a full breakdown of the agent workflows, templates, and examples, please see the [Agent Documentation Hub](docs/agents/).
- **GitHub Integration**: Complete GitHub project management workflow - see [GitHub Management Protocol](docs/agents/github-management.md).
- **Iteration Workflow**: Multi-round review and refinement process - see [Iteration & Review Workflow](docs/agents/iteration-workflow.md).

**📊 Data Documentation**:
- **MySQL Database Schema**: Complete relational database structure - see [Database Documentation](docs/README.md).
- **ArticleInfo Parquet Database**: High-performance analytical database - see [ArticleInfo Database Guide](docs/ARTICLEINFO_DATABASE.md).
- **Data Processing Pipeline**: Complete script-data mapping - see [Data Script Mapping](docs/DATA_SCRIPT_MAPPING.md).

## 📝 Citation

```bibtex
@software{invisible_research_2024,
  title={Invisible Research: Uncovering Hidden Academic Scholarship},
  year={2024},
  url={https://github.com/theinvisiblelab/invisible-research}
}
```

See `docs/` folder for detailed documentation.

### Unused Code Policy
See the policy for handling unused but potentially reusable code: [docs/unused-code-policy.md](docs/unused-code-policy.md).
