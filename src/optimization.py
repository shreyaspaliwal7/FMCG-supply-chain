"""
linear programming model to optimize warehouse to distributor allocation
"""

import sqlite3
from typing import Dict, Tuple

import pandas as pd
import pulp

from config import DB_PATH


def load_network_inputs(product_id: str = "P1", db_path: str = str(DB_PATH)) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """load warehouse capacities, distributor demand, and shipping costs"""
    conn = sqlite3.connect(db_path)
    warehouses = pd.read_sql_query("SELECT * FROM warehouses", conn)
    distributors = pd.read_sql_query("SELECT * FROM distributors", conn)
    costs = pd.read_sql_query("SELECT * FROM shipping_cost", conn)

    demand = pd.read_sql_query(
        f"""
        SELECT distributor_id, AVG(units_demanded) * 30 AS monthly_demand
        FROM daily_sales
        WHERE product_id = '{product_id}'
        GROUP BY distributor_id
        """,
        conn,
    )
    conn.close()

    demand["monthly_demand"] = demand["monthly_demand"].round(0)
    return warehouses, distributors, costs, demand


def solve_allocation(product_id: str = "P1", db_path: str = str(DB_PATH)) -> Tuple[pd.DataFrame, float, float, str]:
    """
    solves classic transportation problem using pulp
    minimizes shipping cost subject to warehouse capacity and distributor demand
    """
    warehouses, distributors, costs, demand = load_network_inputs(product_id, db_path)

    w_ids = warehouses["warehouse_id"].tolist()
    d_ids = distributors["distributor_id"].tolist()
    capacity = dict(zip(warehouses["warehouse_id"], warehouses["monthly_capacity_units"]))
    dem = dict(zip(demand["distributor_id"], demand["monthly_demand"]))
    cost = {(r.warehouse_id, r.distributor_id): r.cost_per_unit for r in costs.itertuples()}

    # define linear programming problem
    prob = pulp.LpProblem(f"Warehouse_Allocation_{product_id}", pulp.LpMinimize)

    # decision variables: units shipped from warehouse w to distributor d
    x = {
        (w, d): pulp.LpVariable(f"x_{w}_{d}", lowBound=0)
        for w in w_ids for d in d_ids
    }

    # objective: minimize total shipping cost
    prob += pulp.lpSum(cost[(w, d)] * x[(w, d)] for w in w_ids for d in d_ids)

    # supply constraints: warehouse capacity
    for w in w_ids:
        prob += pulp.lpSum(x[(w, d)] for d in d_ids) <= capacity[w], f"Capacity_{w}"

    # demand constraints: distributor requirement
    for d in d_ids:
        prob += pulp.lpSum(x[(w, d)] for w in w_ids) >= dem[d], f"Demand_{d}"

    # solve using cbc solver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    # extract allocation results
    allocation = []
    for w in w_ids:
        for d in d_ids:
            units = x[(w, d)].value()
            if units and units > 0.5:
                allocation.append({
                    "warehouse": w,
                    "distributor": d,
                    "units": round(units, 0),
                    "cost_per_unit": cost[(w, d)],
                    "line_cost": round(units * cost[(w, d)], 2),
                })

    total_cost = float(pulp.value(prob.objective))

    # baseline cost using naive equal split across warehouses
    naive_cost = 0.0
    for d in d_ids:
        share = dem[d] / len(w_ids)
        for w in w_ids:
            naive_cost += share * cost[(w, d)]

    return pd.DataFrame(allocation), total_cost, naive_cost, pulp.LpStatus[prob.status]


if __name__ == "__main__":
    alloc_df, opt_cost, naive_cost, status = solve_allocation("P1")
    print(f"solver status: {status}")
    print(alloc_df.to_string(index=False))
    print(f"\noptimized total shipping cost:  Rs {opt_cost:,.2f}")
    print(f"naive baseline shipping cost:   Rs {naive_cost:,.2f}")
    savings_pct = (naive_cost - opt_cost) / naive_cost * 100
    print(f"logistics savings vs baseline:  {savings_pct:.1f}%")
