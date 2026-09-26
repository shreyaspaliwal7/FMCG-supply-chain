"""
unit tests for demand forecasting module
"""

import pandas as pd
import pytest
from forecast import simple_exponential_smoothing, forecast_all_products


def test_simple_exponential_smoothing_constant_series():
    series = pd.Series([100.0, 100.0, 100.0, 100.0])
    forecast = simple_exponential_smoothing(series, alpha=0.3)
    assert pytest.approx(forecast, 0.01) == 100.0


def test_simple_exponential_smoothing_empty():
    series = pd.Series([], dtype=float)
    assert simple_exponential_smoothing(series) == 0.0


def test_forecast_all_products():
    results = forecast_all_products()
    assert isinstance(results, pd.DataFrame)
    assert not results.empty
    assert "product_id" in results.columns
    assert "next_period_forecast_total_demand" in results.columns
    assert len(results) == 5
