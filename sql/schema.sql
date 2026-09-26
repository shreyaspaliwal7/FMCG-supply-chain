-- fmcg supply chain relational database schema
-- models products, warehouses, distributors, shipping costs, daily sales, and inventory snapshots

CREATE TABLE IF NOT EXISTS products (
    product_id          TEXT PRIMARY KEY,
    product_name        TEXT NOT NULL,       -- product name
    unit_cost           REAL NOT NULL,       -- unit cost
    ordering_cost       REAL NOT NULL,       -- ordering batch cost
    holding_cost_pct    REAL NOT NULL        -- annual holding cost %
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id        TEXT PRIMARY KEY,
    warehouse_name      TEXT NOT NULL,       -- warehouse name
    monthly_capacity_units INTEGER NOT NULL  -- monthly shipping capacity
);

CREATE TABLE IF NOT EXISTS distributors (
    distributor_id      TEXT PRIMARY KEY,
    distributor_name    TEXT NOT NULL,       -- distributor name
    region              TEXT NOT NULL        -- region (north, west, south)
);

-- shipping cost per unit from warehouse to distributor
CREATE TABLE IF NOT EXISTS shipping_cost (
    warehouse_id        TEXT NOT NULL,
    distributor_id      TEXT NOT NULL,
    cost_per_unit       REAL NOT NULL,
    PRIMARY KEY (warehouse_id, distributor_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (distributor_id) REFERENCES distributors(distributor_id)
);

-- daily sales history per distributor per product
CREATE TABLE IF NOT EXISTS daily_sales (
    sale_date           TEXT NOT NULL,
    product_id          TEXT NOT NULL,
    distributor_id      TEXT NOT NULL,
    units_sold          INTEGER NOT NULL,    -- units fulfilled
    units_demanded      INTEGER NOT NULL,    -- total units demanded
    PRIMARY KEY (sale_date, product_id, distributor_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (distributor_id) REFERENCES distributors(distributor_id)
);

-- daily inventory snapshot per warehouse per product
CREATE TABLE IF NOT EXISTS inventory_levels (
    snapshot_date       TEXT NOT NULL,
    product_id          TEXT NOT NULL,
    warehouse_id        TEXT NOT NULL,
    units_on_hand       INTEGER NOT NULL,    -- stock on hand
    PRIMARY KEY (snapshot_date, product_id, warehouse_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);
