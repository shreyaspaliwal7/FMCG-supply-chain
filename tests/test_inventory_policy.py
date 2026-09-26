"""
unit tests for inventory policy calculations (eoq, safety stock, rop, turns, days of supply)
"""

import pytest
import numpy as np
from inventory_policy import calculate_eoq, calculate_safety_stock, compute_policy


def test_calculate_eoq_known_values():
    # d = 10000, s = 50, c = 20, h = 0.25 => eoq = sqrt(2*10000*50 / 5) = 447.21
    eoq_val = calculate_eoq(10000, 50, 20, 0.25)
    assert pytest.approx(eoq_val, 0.01) == 447.21


def test_calculate_eoq_zero_demand():
    assert calculate_eoq(0, 50, 20, 0.25) == 0.0


def test_calculate_safety_stock():
    # sigma_d = 20, L = 9, Z = 1.65 => ss = 1.65 * 20 * 3 = 99.0
    ss = calculate_safety_stock(stddev_daily_demand=20.0, lead_time_days=9.0, z_score=1.65)
    assert pytest.approx(ss, 0.01) == 99.0


def test_compute_policy():
    df = compute_policy()
    assert not df.empty
    assert "eoq_units" in df.columns
    assert "safety_stock_units" in df.columns
    assert "reorder_point_units" in df.columns
    assert "inventory_turns" in df.columns
    assert "days_of_supply" in df.columns
    assert len(df) == 5
