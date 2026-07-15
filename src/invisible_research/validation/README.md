# LLM Validation Suite

The validation suite compares `$DATA_ROOT/processed/creator_sample.parquet`
with `$DATA_ROOT/derived/creator_sample_clean_v2.parquet` and stores human
review state under `$DATA_ROOT/validation/`.

```bash
export DATA_ROOT=/path/to/InvisibleResearch/data
export PYTHONPATH=src

# Check dependencies, inputs, configuration, and output directories.
python -m invisible_research.validation.start --check

# Start the Streamlit review interface on http://localhost:8501.
python -m invisible_research.validation.start
```

The default evaluation dimensions, sampling rules, and external lookup
templates are defined in `validation_config.yaml`. Review progress is a human
record and must not be replaced by an AI-generated conclusion.
