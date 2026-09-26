"""
demand forecasting using simple exponential smoothing (ses)
calculates mae, mape, and forecast bias
"""

import sqlite3
from typing import Dict, List

import numpy as np
import pandas as pd

from config import DB_PATH, DEFAULT_ALPHA


def simple_exponential_smoothing(series: pd.Series, alpha: float = DEFAULT_ALPHA) -> float:
    """
    simple exponential smoothing forecast for one period ahead
    formula: f_(t+1) = alpha * d_t + (1 - alpha) * f_t
    """
    if series.empty:
        return 0.0
    forecast = float(series.iloc[0])
    for actual in series.iloc[1:]:
        forecast = alpha * actual + (1 - alpha) * forecast
    return forecast


def forecast_all_products(db_path: str = str(DB_PATH), alpha: float = DEFAULT_ALPHA) -> pd.DataFrame:
    """
    runs ses forecast for all skus and evaluates 30-day performance (mae, mape, bias)
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        """
        SELECT sale_date, product_id, SUM(units_demanded) AS units_demanded
        FROM daily_sales
        GROUP BY sale_date, product_id
        ORDER BY product_id, sale_date
        """,
        conn,
    )
    conn.close()

    df["sale_date"] = pd.to_datetime(df["sale_date"])

    results: List[Dict] = []
    for product_id, grp in df.groupby("product_id"):
        grp = grp.sort_values("sale_date")
        series = grp["units_demanded"]

        next_period_forecast = simple_exponential_smoothing(series, alpha=alpha)

        # evaluate last 30 days performance
        errors_naive, errors_ses = [], []
        mape_ses_list, bias_list = [], []
        history = series.iloc[:-30].copy()

        for actual in series.iloc[-30:]:
            naive_pred = history.mean()
            ses_pred = simple_exponential_smoothing(history, alpha=alpha)

            errors_naive.append(abs(actual - naive_pred))
            errors_ses.append(abs(actual - ses_pred))
            if actual > 0:
                mape_ses_list.append(abs(actual - ses_pred) / actual * 100)
            bias_list.append(ses_pred - actual)

            history = pd.concat([history, pd.Series([actual])], ignore_index=True)

        results.append({
            "product_id": product_id,
            "next_period_forecast_total_demand": round(next_period_forecast, 1),
            "naive_avg_MAE_last_30d": round(float(np.mean(errors_naive)), 1),
            "ses_MAE_last_30d": round(float(np.mean(errors_ses)), 1),
            "ses_MAPE_pct": round(float(np.mean(mape_ses_list)), 1),
            "forecast_bias": round(float(np.mean(bias_list)), 1),
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    result_df = forecast_all_products()
    print(result_df.to_string(index=False))
    improvement = (
        (result_df["naive_avg_MAE_last_30d"] - result_df["ses_MAE_last_30d"])
        / result_df["naive_avg_MAE_last_30d"] * 100
    )
    print(f"\naverage forecast error reduction vs naive baseline: {improvement.mean():.1f}%")
