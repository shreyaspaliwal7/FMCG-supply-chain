"""
inventory policy calculations: eoq, safety stock, reorder point, inventory turns, days of supply
"""

import sqlite3
import numpy as np
import pandas as pd

from config import DB_PATH, Z_SCORE_95, DEFAULT_LEAD_TIME_DAYS, ANNUAL_DAYS


def calculate_eoq(annual_demand: float, ordering_cost: float, unit_cost: float, holding_cost_pct: float) -> float:
    """
    eoq formula = sqrt((2 * D * S) / H)
    minimizes sum of ordering cost and inventory holding cost
    """
    holding_cost_per_unit = unit_cost * holding_cost_pct
    if holding_cost_per_unit <= 0 or annual_demand <= 0:
        return 0.0
    return float(np.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit))


def calculate_safety_stock(stddev_daily_demand: float, lead_time_days: float = DEFAULT_LEAD_TIME_DAYS, z_score: float = Z_SCORE_95) -> float:
    """
    safety stock formula = Z * stddev_d * sqrt(lead_time)
    buffers against demand variability during replenishment lead time
    """
    return float(z_score * stddev_daily_demand * np.sqrt(lead_time_days))


def compute_policy(db_path: str = str(DB_PATH), lead_time_days: float = DEFAULT_LEAD_TIME_DAYS) -> pd.DataFrame:
    """
    computes inventory policy parameters (eoq, safety stock, rop, turns, days of supply) for all products
    """
    conn = sqlite3.connect(db_path)
    products = pd.read_sql_query("SELECT * FROM products", conn)
    demand_stats = pd.read_sql_query(
        """
        SELECT product_id,
               AVG(units_demanded) AS avg_daily_demand,
               SQRT(AVG(units_demanded * units_demanded) - AVG(units_demanded) * AVG(units_demanded)) AS stddev_daily_demand
        FROM daily_sales
        GROUP BY product_id
        """,
        conn,
    )
    conn.close()

    df = products.merge(demand_stats, on="product_id")
    df["annual_demand"] = df["avg_daily_demand"] * ANNUAL_DAYS

    df["eoq_units"] = df.apply(
        lambda r: calculate_eoq(r["annual_demand"], r["ordering_cost"], r["unit_cost"], r["holding_cost_pct"]),
        axis=1,
    ).round(0)

    df["safety_stock_units"] = df["stddev_daily_demand"].apply(
        lambda s: calculate_safety_stock(s, lead_time_days=lead_time_days, z_score=Z_SCORE_95)
    ).round(0)

    df["reorder_point_units"] = (
        df["avg_daily_demand"] * lead_time_days + df["safety_stock_units"]
    ).round(0)

    # inventory turnover & days of supply metrics
    df["avg_inventory_units"] = (df["eoq_units"] / 2.0) + df["safety_stock_units"]
    df["inventory_turns"] = (df["annual_demand"] / df["avg_inventory_units"]).round(1)
    df["days_of_supply"] = (ANNUAL_DAYS / df["inventory_turns"]).round(1)

    out_cols = [
        "product_id",
        "product_name",
        "avg_daily_demand",
        "eoq_units",
        "safety_stock_units",
        "reorder_point_units",
        "inventory_turns",
        "days_of_supply",
    ]
    return df[out_cols]


if __name__ == "__main__":
    policy_df = compute_policy()
    print(policy_df.to_string(index=False))
