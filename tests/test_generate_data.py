"""
unit tests for synthetic data generation and database schema integrity
"""

import sqlite3
import pytest
from config import DB_PATH
from generate_data import PRODUCTS, WAREHOUSES, DISTRIBUTORS


def test_database_table_counts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products")
    assert cur.fetchone()[0] == len(PRODUCTS)

    cur.execute("SELECT COUNT(*) FROM warehouses")
    assert cur.fetchone()[0] == len(WAREHOUSES)

    cur.execute("SELECT COUNT(*) FROM distributors")
    assert cur.fetchone()[0] == len(DISTRIBUTORS)

    cur.execute("SELECT COUNT(*) FROM daily_sales")
    assert cur.fetchone()[0] > 0

    conn.close()
