#!/bin/bash
set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${1:-}" ]]; then
    if [[ "$1" == "database-stage" ]]; then
        shift
        exec bash "$PROJECT_ROOT/src/invisible_research/acquisition/database_stage.bash" "$@"
    fi
    case "$1" in
        openalex-merge) module="invisible_research.acquisition.openalex_merge" ;;
        database-sample) module="invisible_research.acquisition.database_sample" ;;
        database-extract) module="invisible_research.acquisition.database_extract" ;;
        openalex-download) module="invisible_research.acquisition.openalex_download" ;;
        author-names-llm) module="invisible_research.processing.author_names_llm" ;;
        author-names-rules) module="invisible_research.processing.author_names_rules" ;;
        title-language) module="invisible_research.processing.title_language" ;;
        validation) module="invisible_research.validation.start" ;;
        *) module="" ;;
    esac
fi

if [[ -n "${module:-}" ]]; then
    shift
    export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    exec python -m "$module" "$@"
fi

echo "=== Invisible Research Data Processing Pipeline ==="
echo "Start time: $(date)"

# Check virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "⚠️  Recommend activating virtual environment: source environments/venv/bin/activate"
fi

# 1. Environment check
echo "Step 1: Checking dependencies..."
python -c "import pandas, openai, fasttext; print('✅ Core dependencies check passed')" || {
    echo "❌ Dependency check failed, please run: pip install -r requirements.txt"
    exit 1
}

# 2. Database connection test (optional)
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
if python -m invisible_research.acquisition.database_sample 2>/dev/null; then
    echo "✅ Database connection successful"
else
    echo "⚠️  Database connection failed, will skip data extraction step"
fi

# 3. Data extraction
if [ -f "${DATA_ROOT:?Set DATA_ROOT to the external InvisibleResearch data directory}/processed/data_for_analysis.parquet" ]; then
    echo "Step 2: Main data file exists, skipping extraction"
else
    echo "Step 2: Data extraction..."
    python -m invisible_research.acquisition.database_extract
fi

# 4. Author analysis
echo "Step 3: Author field analysis..."
python scripts/03_analysis/judge_creator.py

echo "Step 4: Creating author samples..."
python scripts/03_analysis/test_LLM_name_detect_parquet.py

# 5. Intelligent processing (requires API key)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set, skipping LLM processing"
else
    echo "Step 5: LLM author name parsing..."
    python -m invisible_research.processing.author_names_llm
fi

# 6. Language detection
echo "Step 6: Language detection..."
python -m invisible_research.processing.title_language

echo "✅ Pipeline completed! End time: $(date)"
echo "📊 Result files are located in $DATA_ROOT/final/ folder"
