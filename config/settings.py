"""
Project Configuration File
Contains all paths, database connections, and model parameter configurations
"""
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Database configuration
DATABASE_CONFIG = {
    'MYSQL_URI': "mysql+pymysql://root:secret@127.0.0.1:3306/invisible_research",
    'CHUNK_SIZE': 100_000,
    'MAX_WORKERS': 6
}

# Data paths configuration
DATA_PATHS = {
    # Raw data
    'raw_sample': PROJECT_ROOT / 'data/raw/sample_records_language_title_abstract.csv',
    'database_dump': PROJECT_ROOT / 'data/database.sql.gz',
    
    # Intermediate processed data
    'main_data': PROJECT_ROOT / 'data/processed/data_for_analysis.parquet',
    'creator_sample': PROJECT_ROOT / 'data/processed/creator_sample.parquet',
    'name_clean': PROJECT_ROOT / 'data/processed/name_clean.parquet',
    
    # Final output data
    'creator_clean': PROJECT_ROOT / 'data/final/creator_sample_clean.parquet',
    'title_language': PROJECT_ROOT / 'data/final/title_pred_lang.parquet'
}

# LLM configuration
LLM_CONFIG = {
    'MODEL': "gpt-4o",
    'BATCH_SIZE': 20,
    'MAX_CONCURRENT': 8,
    'RETRY_ATTEMPTS': 6
}

# Language detection configuration
LANGUAGE_CONFIG = {
    'GLOTLID_MODEL': "cis-lmu/glotlid",
    'BATCH_SIZE': 50_000
}

# Script paths configuration
SCRIPT_PATHS = {
    'setup': PROJECT_ROOT / 'scripts/01_setup',
    'extraction': PROJECT_ROOT / 'scripts/02_extraction', 
    'analysis': PROJECT_ROOT / 'scripts/03_analysis',
    'processing': PROJECT_ROOT / 'scripts/04_processing'
}
