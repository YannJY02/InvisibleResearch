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
cp config/env.template .env

# 2. Edit .env with your actual API key
# OPENAI_API_KEY=your_api_key_here
# OPENAI_BASE_URL=https://your-proxy.com/v1  # Optional

# 3. The .env file is automatically ignored by git for security
```

📋 **See [Security Guide](docs/SECURITY_GUIDE.md) for detailed configuration instructions and best practices.**

### Run Pipeline
```bash
# Data extraction
python scripts/02_extraction/data_for_analysis_to_parquet.py

# Author analysis  
python scripts/03_analysis/judge_creator.py
python scripts/03_analysis/test_LLM_name_detect_parquet.py

# Intelligent processing (requires API configuration)
python scripts/04_processing/LLM_name_detect.py

# Language detection
python scripts/04_processing/result_GlotLID.py

# LLM validation (optional - for accuracy assessment)
python scripts/05_validation/start_validation.py
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
scripts/01_setup/      # Environment setup
scripts/02_extraction/ # Data extraction
scripts/03_analysis/   # Data analysis  
scripts/04_processing/ # Advanced processing
scripts/05_validation/ # LLM validation suite
notebooks/             # Interactive Jupyter notebooks (mirrors scripts structure)
├── 01_setup/          # Database setup and exploration notebooks
├── 02_extraction/     # Data extraction and conversion notebooks
├── 03_analysis/       # Interactive data analysis notebooks
├── 04_processing/     # Advanced processing notebooks
└── 05_validation/     # Data validation notebooks
data/raw/             # Raw data
data/processed/       # Intermediate results
data/final/           # Final outputs
data/validation/      # Validation data and reports
```

### 🔄 Scripts vs Notebooks
- **Scripts**: Production-ready, automated processing
- **Notebooks**: Interactive exploration, documentation, and experimentation
- **Structure**: Notebooks mirror scripts directory structure for consistency
- **Complementary**: Both can be used together without conflicts

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
python scripts/05_validation/start_validation.py
# Access: http://localhost:8501

# Launch data protection dashboard
python -m streamlit run scripts/05_validation/data_protection_dashboard.py --server.port 8502
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
