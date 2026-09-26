"""
unit tests for network allocation lp optimization model
"""

import pandas as pd
import pytest
from optimization import solve_allocation


def test_solve_allocation_p1():
    alloc_df, opt_cost, naive_cost, status = solve_allocation("P1")
    assert status == "Optimal"
    assert isinstance(alloc_df, pd.DataFrame)
    assert not alloc_df.empty
    assert opt_cost > 0
    assert naive_cost > opt_cost  # optimized cost must be cheaper than naive baseline
