# FMCG Supply Chain Analytics & Optimization — Interview Preparation Guide

This guide is designed to help you confidently present this project in **Supply Chain, Operations Research, Logistics, and Data Analytics interviews**.

---

## 🎯 1. 30-Second Elevator Pitch

> *"I built an end-to-end FMCG supply chain decision-support system in Python and SQL that optimizes multi-echelon inventory levels and regional distribution costs. The system performs ABC-XYZ demand segmentation, forecasts demand using Simple Exponential Smoothing, computes EOQ and 95% service-level safety stocks, and uses Linear Programming (PuLP) to optimize warehouse-to-distributor shipments—cutting logistics cost by ~49% vs baseline."*

---

## 📐 2. Key Supply Chain Frameworks & Formulas

### A. ABC-XYZ Demand Matrix
- **ABC Classification (Volume)**: Class A (top 80% demand volume), Class B (next 15%), Class C (bottom 5%). Uses SQL window functions (`SUM() OVER`).
- **XYZ Classification (Volatility)**: Based on Coefficient of Variation ($CV = \sigma / \mu$).
  - **X**: $CV \le 0.20$ (Very predictable demand)
  - **Y**: $0.20 < CV \le 0.40$ (Moderate variability)
  - **Z**: $CV > 0.40$ (High volatility / sporadic demand)

### B. Demand Forecasting & Error Tracking
- **Simple Exponential Smoothing (SES)**:
  $$F_{t+1} = \alpha D_t + (1 - \alpha) F_t \quad (\alpha = 0.3)$$
- **Forecast Evaluation Metrics**:
  - **MAE (Mean Absolute Error)**: $\frac{1}{n} \sum |D_t - F_t|$
  - **MAPE (Mean Absolute Percentage Error)**: $\frac{1}{n} \sum \frac{|D_t - F_t|}{D_t} \times 100\%$
  - **Forecast Bias**: $\frac{1}{n} \sum (F_t - D_t)$ *(Positive = Over-forecasting, Negative = Under-forecasting)*

### C. Multi-Echelon Inventory Optimization
- **Economic Order Quantity (EOQ)**: Balances ordering setup cost ($S$) vs unit holding cost ($H = \text{unit\_cost} \times h\%$).
  $$EOQ = \sqrt{\frac{2 \cdot D \cdot S}{H}}$$
- **Safety Stock ($SS$)**: Buffer for demand variability during lead time ($L = 7$ days) at 95% service level ($Z = 1.65$).
  $$SS = Z \cdot \sigma_d \sqrt{L}$$
- **Reorder Point ($ROP$)**: Trigger level for placing replenishment purchase orders.
  $$ROP = (\bar{d} \cdot L) + SS$$
- **Inventory Turnover Ratio (ITR)** & **Days of Supply (DOS)**:
  $$\text{Inventory Turns} = \frac{\text{Annual Demand}}{\frac{EOQ}{2} + SS}, \quad \text{DOS} = \frac{365}{\text{Inventory Turns}}$$

### D. Network Distribution Transportation Model (Linear Programming)
- **Objective**: $\min \sum_{w} \sum_{d} c_{w,d} \cdot x_{w,d}$
- **Supply Constraint**: $\sum_{d} x_{w,d} \le \text{Capacity}_w$
- **Demand Constraint**: $\sum_{w} x_{w,d} \ge \text{Demand}_d$

---

## ❓ 3. Top Supply Chain Interview Questions & Answers

### Q1: Why use Exponential Smoothing instead of a simple Moving Average or Machine Learning?
**Answer**: 
*"Moving averages treat old sales data with equal weight as yesterday's sales. In FMCG, demand changes dynamically due to seasonality and promotions. Exponential Smoothing applies exponentially decreasing weights to older observations via $\alpha = 0.3$, so recent demand trends drive the forecast without creating excessive noise. It outperforms flat averages while remaining lightweight and transparent for daily S&OP planning."*

### Q2: How did you handle trade-offs between holding costs and stockout risks?
**Answer**:
*"We used a two-part approach. EOQ formally balances ordering setup costs against holding costs to determine order batch size. To prevent stockouts caused by daily demand variance, we calculated safety stock using a 95% service level factor ($Z = 1.65$). This ensured high availability for Class-A high-volume SKUs without overbuilding working capital."*

### Q3: How did you formulate the network optimization model?
**Answer**:
*"We modeled warehouse-to-distributor allocation as a classic Linear Transportation Problem using Python's PuLP library with the COIN-OR CBC solver. Decision variables represented unit shipment quantities per lane. The objective function minimized total freight cost subject to distributor demand constraints and regional distribution center capacity limits."*

### Q4: What supply chain KPIs would you track in a live production system?
**Answer**:
*"I would monitor four key performance indicators:
1. **On-Time In-Full (OTIF) / Fill Rate**: Percentage of distributor orders fulfilled without stockouts.
2. **Forecast Accuracy & Bias (MAPE / Tracking Signal)**: Ensuring models aren't systematically over- or under-forecasting.
3. **Inventory Turnover / Days of Supply**: Monitoring working capital efficiency.
4. **Logistics Cost per Unit Shipped**: Evaluating freight route optimization effectiveness."*

---

## 📁 4. Project Highlights Checklist for Resume

- [x] **Relational SQL Diagnostic Engine**: Built windowed SQL queries for ABC-XYZ demand categorization & lost-sales stockout identification.
- [x] **Time-Series Forecasting**: Implemented Simple Exponential Smoothing in Python, reducing MAE by **~62%** vs historical baseline.
- [x] **Stochastic Inventory Policy**: Derived EOQ, Safety Stock, ROP, and Inventory Turnover metrics per SKU.
- [x] **Linear Programming Logistics Solver**: Formulated LP transportation problem in PuLP, achieving **~49% cost reduction** vs naive allocation.
- [x] **Software Engineering Quality**: Developed 9-test unit test suite (`pytest`) and clean modular code architecture.
