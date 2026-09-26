"""
config file for paths and default constants
"""

from pathlib import Path

# base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# data paths
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "supply_chain.db"
SQL_DIR = BASE_DIR / "sql"
SCHEMA_PATH = SQL_DIR / "schema.sql"
ANALYSIS_QUERIES_PATH = SQL_DIR / "analysis_queries.sql"
OUTPUT_DIR = BASE_DIR / "output"

# default parameters
DEFAULT_ALPHA = 0.3          # simple exponential smoothing factor
Z_SCORE_95 = 1.65            # 95% service level z-factor
DEFAULT_LEAD_TIME_DAYS = 7   # lead time in days
ANNUAL_DAYS = 365
