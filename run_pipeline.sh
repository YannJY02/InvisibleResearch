#!/bin/bash
set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "openalex-merge" ]]; then
    shift
    export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    exec python -m invisible_research.openalex_merge "$@"
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
if python scripts/01_setup/read_database.py 2>/dev/null; then
    echo "✅ Database connection successful"
else
    echo "⚠️  Database connection failed, will skip data extraction step"
fi

# 3. Data extraction
if [ -f "data/processed/data_for_analysis.parquet" ]; then
    echo "Step 2: Main data file exists, skipping extraction"
else
    echo "Step 2: Data extraction..."
    python scripts/02_extraction/data_for_analysis_to_parquet.py
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
    python scripts/04_processing/LLM_name_detect.py
fi

# 6. Language detection
echo "Step 6: Language detection..."
python scripts/04_processing/result_GlotLID.py

echo "✅ Pipeline completed! End time: $(date)"
echo "📊 Result files are located in data/final/ folder"
