---
title: "Chapter 4: GroupBy & Aggregation"
description: "Split-apply-combine operations"
---

# Chapter 4: GroupBy & Aggregation

## Basic GroupBy

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "department": ["Sales", "Sales", "Engineering", "Engineering", "HR"],
    "employee": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "salary": [50000, 55000, 80000, 85000, 60000]
})

grouped = df.groupby("department")["salary"]
print(grouped.mean())
print(grouped.agg(["mean", "min", "max", "count"]))
```

## Multiple Aggregations

```python
df = pd.DataFrame({
    "category": ["A", "A", "B", "B", "C"],
    "revenue": [100, 150, 200, 250, 300],
    "cost": [50, 60, 80, 100, 120]
})

result = df.groupby("category").agg(
    total_revenue=("revenue", "sum"),
    avg_cost=("cost", "mean"),
    count=("revenue", "count")
)
print(result)
```

## Transform and Apply

```python
# transform: returns same-shaped result
df["salary_pct"] = df.groupby("department")["salary"].transform(
    lambda x: x / x.sum() * 100
)

# apply: flexible group operations
def top_earner(group):
    return group.nlargest(1, "salary")

print(df.groupby("department").apply(top_earner))
```

## Pivot Tables

```python
df = pd.DataFrame({
    "date": ["2024-01", "2024-01", "2024-02", "2024-02"],
    "product": ["A", "B", "A", "B"],
    "sales": [100, 200, 150, 250]
})

pivot = df.pivot_table(values="sales", index="date", columns="product", aggfunc="sum")
print(pivot)
```

## Exercises

1. Group a sales dataset by region and compute total revenue, average order size, and order count.
2. Use `transform` to add a column showing each employee's salary as a percentage of their department total.
3. Create a pivot table showing monthly sales by product category.

---

[← prev](./chapter-03-cleaning.md) | [next →](./chapter-05-merge.md)
