"""
pytest configuration and fixtures
"""

import sys
from pathlib import Path
import pytest
import sqlite3

# add src to python path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from generate_data import build_database
from config import DB_PATH


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """ensure test database exists before running tests"""
    build_database()
    assert DB_PATH.exists()
    yield
