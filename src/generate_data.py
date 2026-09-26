"""
generate synthetic sales and inventory data for sqlite db
"""

import os
import sqlite3
from datetime import date, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd

from config import DB_PATH, SCHEMA_PATH

np.random.seed(42)

# master data setup
PRODUCTS: List[Tuple[str, str, float, float, float]] = [
    # (product_id, name, unit_cost, ordering_cost, holding_cost_pct_annual)
    ("P1", "Classic Potato Chips 52g", 12.0, 6000.0, 0.20),
    ("P2", "Masala Namkeen 200g", 35.0, 7000.0, 0.22),
    ("P3", "Cream Biscuits 100g", 20.0, 6500.0, 0.20),
    ("P4", "Premium Trail Mix 150g", 60.0, 9000.0, 0.25),
    ("P5", "Multigrain Crackers 90g", 25.0, 6800.0, 0.18),
]

WAREHOUSES: List[Tuple[str, str, int]] = [
    ("W1", "North Distribution Center", 220000),
    ("W2", "West Distribution Center", 190000),
    ("W3", "South Distribution Center", 160000),
]

DISTRIBUTORS: List[Tuple[str, str, str]] = [
    ("D1", "Delhi Distributor", "North"),
    ("D2", "Chandigarh Distributor", "North"),
    ("D3", "Mumbai Distributor", "West"),
    ("D4", "Pune Distributor", "West"),
    ("D5", "Bangalore Distributor", "South"),
    ("D6", "Hyderabad Distributor", "South"),
]

REGION_OF_WAREHOUSE = {"W1": "North", "W2": "West", "W3": "South"}


def calculate_shipping_cost(w_id: str, d_region: str) -> float:
    """calculate shipping cost per unit based on region match"""
    base = 2.0
    same_region = REGION_OF_WAREHOUSE[w_id] == d_region
    if same_region:
        return round(base + np.random.uniform(0, 0.5), 2)
    return round(base + np.random.uniform(2.5, 5.0), 2)


def generate_sales_and_inventory_data(n_days: int = 270) -> Tuple[List[Tuple], List[Tuple]]:
    """generate daily sales records with seasonality and inventory snapshots"""
    start_date = date(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]

    sales_rows = []
    for d_id, _, region in DISTRIBUTORS:
        region_multiplier = {"North": 1.2, "West": 1.4, "South": 1.0}[region]
        for p_id, _, _, _, _ in PRODUCTS:
            base_demand = {"P1": 500, "P2": 300, "P3": 260, "P4": 90, "P5": 140}[p_id]
            base_demand *= region_multiplier

            for i, d in enumerate(dates):
                seasonal = 1.0 + 0.35 * np.sin(2 * np.pi * (i - 150) / 270)
                weekday_boost = 1.15 if d.weekday() in (4, 5) else 1.0
                noise = np.random.normal(1.0, 0.12)
                demand = max(0, int(base_demand * seasonal * weekday_boost * noise))

                # simulate occasional stockout days
                stockout_prob = 0.10 if p_id == "P4" else 0.05
                if np.random.rand() < stockout_prob:
                    sold = int(demand * np.random.uniform(0.5, 0.85))
                else:
                    sold = demand

                sales_rows.append((d.isoformat(), p_id, d_id, sold, demand))

    inv_rows = []
    recent_dates = dates[-30:]
    for w_id, _, cap in WAREHOUSES:
        for p_id, _, _, _, _ in PRODUCTS:
            level = np.random.randint(int(cap * 0.05), int(cap * 0.15))
            for d in recent_dates:
                level = max(0, level + np.random.randint(-500, 400))
                inv_rows.append((d.isoformat(), p_id, w_id, level))

    return sales_rows, inv_rows


def build_database() -> None:
    """initialize sqlite db and insert master tables and transaction rows"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cur.executescript(f.read())

    cur.executemany("INSERT OR REPLACE INTO products VALUES (?,?,?,?,?)", PRODUCTS)
    cur.executemany("INSERT OR REPLACE INTO warehouses VALUES (?,?,?)", WAREHOUSES)
    cur.executemany("INSERT OR REPLACE INTO distributors VALUES (?,?,?)", DISTRIBUTORS)

    ship_rows = [
        (w_id, d_id, calculate_shipping_cost(w_id, d_region))
        for w_id, _, _ in WAREHOUSES
        for d_id, _, d_region in DISTRIBUTORS
    ]
    cur.executemany("INSERT OR REPLACE INTO shipping_cost VALUES (?,?,?)", ship_rows)

    sales_rows, inv_rows = generate_sales_and_inventory_data()
    cur.executemany("INSERT OR REPLACE INTO daily_sales VALUES (?,?,?,?,?)", sales_rows)
    cur.executemany("INSERT OR REPLACE INTO inventory_levels VALUES (?,?,?,?)", inv_rows)

    conn.commit()
    conn.close()
    print(f"[+] database built successfully at: {DB_PATH}")
    print(f"    - daily_sales: {len(sales_rows)} records")
    print(f"    - inventory_levels: {len(inv_rows)} records")


if __name__ == "__main__":
    build_database()
