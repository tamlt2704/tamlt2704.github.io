---
title: "Chapter 7: Real Projects"
description: "End-to-end data analysis projects"
---

# Chapter 7: Real Projects

## Project 1: Sales Analysis

```python
import pandas as pd
import numpy as np

np.random.seed(42)
n = 1000
sales = pd.DataFrame({
    "date": pd.date_range("2023-01-01", periods=n, freq="D"),
    "product": np.random.choice(["Laptop", "Phone", "Tablet"], n),
    "region": np.random.choice(["North", "South", "East", "West"], n),
    "units": np.random.randint(1, 50, n),
    "price": np.random.choice([999, 699, 499], n)
})
sales["revenue"] = sales["units"] * sales["price"]

# Top products by revenue
print(sales.groupby("product")["revenue"].sum().sort_values(ascending=False))

# Monthly trend
monthly = sales.set_index("date").resample("M")["revenue"].sum()
print(monthly)

# Region performance
region_stats = sales.groupby("region").agg(
    total_revenue=("revenue", "sum"),
    avg_units=("units", "mean")
).sort_values("total_revenue", ascending=False)
print(region_stats)
```

## Project 2: Data Cleaning Pipeline

```python
def clean_pipeline(filepath):
    df = pd.read_csv(filepath)

    # Standardize columns
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Handle missing values
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    # Remove duplicates
    df = df.drop_duplicates()

    # Parse dates
    date_cols = [c for c in df.columns if "date" in c]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

# Usage: clean_df = clean_pipeline("raw_data.csv")
```

## Project 3: Customer Cohort Analysis

```python
orders = pd.DataFrame({
    "customer_id": np.random.randint(1, 200, 2000),
    "order_date": pd.date_range("2023-01-01", periods=2000, freq="4H"),
    "amount": np.random.randint(10, 500, 2000)
})

# First purchase month per customer
orders["order_month"] = orders["order_date"].dt.to_period("M")
cohort = orders.groupby("customer_id")["order_month"].min().rename("cohort")
orders = orders.merge(cohort, on="customer_id")

# Cohort index (months since first purchase)
orders["cohort_index"] = (orders["order_month"] - orders["cohort"]).apply(lambda x: x.n)

# Retention table
cohort_data = orders.groupby(["cohort", "cohort_index"])["customer_id"].nunique().unstack()
cohort_pct = cohort_data.div(cohort_data[0], axis=0) * 100
print(cohort_pct.head())
```

## Exercises

1. Build a complete EDA notebook: load data, clean it, compute summary stats, and visualize key findings.
2. Create a customer segmentation using RFM (Recency, Frequency, Monetary) analysis.
3. Analyze a real CSV dataset (e.g., Kaggle Titanic) end-to-end: cleaning, feature engineering, and insights.

---

[← prev](./chapter-06-timeseries.md) | [Overview](./chapter-00-overview.md)
