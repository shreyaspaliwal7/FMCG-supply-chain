-- sql analysis queries for supply chain diagnostics

-- 1. monthly regional demand trend
select
    strftime('%Y-%m', ds.sale_date) as month,
    p.product_name,
    d.region,
    sum(ds.units_demanded) as total_demand,
    sum(ds.units_sold)     as total_sold
from daily_sales ds
join products p     on p.product_id = ds.product_id
join distributors d on d.distributor_id = ds.distributor_id
group by month, p.product_name, d.region
order by month, p.product_name, d.region;


-- 2. abc analysis (pareto cumulative demand pareto 80/20)
with product_totals as (
    select
        p.product_id,
        p.product_name,
        sum(ds.units_demanded) as total_demand
    from daily_sales ds
    join products p on p.product_id = ds.product_id
    group by p.product_id, p.product_name
),
ranked as (
    select
        product_id,
        product_name,
        total_demand,
        sum(total_demand) over (order by total_demand desc) as running_total,
        sum(total_demand) over ()                            as grand_total
    from product_totals
)
select
    product_name,
    total_demand,
    round(100.0 * running_total / grand_total, 1) as cumulative_pct,
    case
        when running_total * 1.0 / grand_total <= 0.80 then 'A'
        when running_total * 1.0 / grand_total <= 0.95 then 'B'
        else 'C'
    end as abc_class
from ranked
order by total_demand desc;


-- 3. stockout analysis (units lost when demand exceeds sales)
select
    p.product_name,
    d.distributor_name,
    count(*) as stockout_days,
    sum(ds.units_demanded - ds.units_sold) as units_lost,
    round(100.0 * count(*) / (
        select count(*) from daily_sales ds2
        where ds2.product_id = ds.product_id
          and ds2.distributor_id = ds.distributor_id
    ), 1) as stockout_rate_pct
from daily_sales ds
join products p     on p.product_id = ds.product_id
join distributors d on d.distributor_id = ds.distributor_id
where ds.units_sold < ds.units_demanded
group by p.product_name, d.distributor_name
order by units_lost desc;


-- 4. average daily demand and standard deviation per product
select
    p.product_id,
    p.product_name,
    round(avg(ds.units_demanded), 1) as avg_daily_demand,
    round(
        sqrt(avg(ds.units_demanded * ds.units_demanded) - avg(ds.units_demanded) * avg(ds.units_demanded))
    , 1) as stddev_daily_demand
from daily_sales ds
join products p on p.product_id = ds.product_id
group by p.product_id, p.product_name
order by avg_daily_demand desc;


-- 5. abc-xyz demand matrix segmentation (volume vs volatility)
-- cv = coefficient of variation = stddev / mean
with stats as (
    select
        p.product_id,
        p.product_name,
        sum(ds.units_demanded) as total_demand,
        avg(ds.units_demanded) as mean_demand,
        sqrt(avg(ds.units_demanded * ds.units_demanded) - avg(ds.units_demanded) * avg(ds.units_demanded)) as stddev_demand
    from daily_sales ds
    join products p on p.product_id = ds.product_id
    group by p.product_id, p.product_name
),
totals as (
    select
        product_id,
        product_name,
        total_demand,
        mean_demand,
        stddev_demand,
        (stddev_demand / mean_demand) as cv,
        sum(total_demand) over (order by total_demand desc) as running_total,
        sum(total_demand) over () as grand_total
    from stats
)
select
    product_name,
    total_demand,
    round(cv, 2) as demand_cv,
    case
        when running_total * 1.0 / grand_total <= 0.80 then 'A'
        when running_total * 1.0 / grand_total <= 0.95 then 'B'
        else 'C'
    end as abc_class,
    case
        when (stddev_demand / mean_demand) <= 0.20 then 'X'
        when (stddev_demand / mean_demand) <= 0.40 then 'Y'
        else 'Z'
    end as xyz_class,
    (
        case when running_total * 1.0 / grand_total <= 0.80 then 'A' when running_total * 1.0 / grand_total <= 0.95 then 'B' else 'C' end ||
        case when (stddev_demand / mean_demand) <= 0.20 then 'X' when (stddev_demand / mean_demand) <= 0.40 then 'Y' else 'Z' end
    ) as segment
from totals
order by total_demand desc;
