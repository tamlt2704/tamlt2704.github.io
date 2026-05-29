---
title: "Chapter 5: Merge & Join"
description: "Combining DataFrames with merge, join, and concat"
---

# Chapter 5: Merge & Join

## Concat

```python
import pandas as pd

df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
df2 = pd.DataFrame({"A": [5, 6], "B": [7, 8]})

vertical = pd.concat([df1, df2], ignore_index=True)
horizontal = pd.concat([df1, df2], axis=1)
```

## Merge (SQL-style Joins)

```python
orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4],
    "customer_id": [101, 102, 103, 104],
    "amount": [250, 150, 300, 200]
})

customers = pd.DataFrame({
    "customer_id": [101, 102, 103, 105],
    "name": ["Alice", "Bob", "Charlie", "Eve"]
})

# Inner join
inner = pd.merge(orders, customers, on="customer_id", how="inner")

# Left join (keep all orders)
left = pd.merge(orders, customers, on="customer_id", how="left")

# Outer join (keep everything)
outer = pd.merge(orders, customers, on="customer_id", how="outer")
print(left)
```

## Merge on Different Column Names

```python
df_a = pd.DataFrame({"id_a": [1, 2, 3], "val": [10, 20, 30]})
df_b = pd.DataFrame({"id_b": [1, 2, 4], "score": [90, 80, 70]})

merged = pd.merge(df_a, df_b, left_on="id_a", right_on="id_b", how="inner")
print(merged)
```

## Join on Index

```python
df1 = pd.DataFrame({"A": [1, 2, 3]}, index=["x", "y", "z"])
df2 = pd.DataFrame({"B": [4, 5, 6]}, index=["x", "y", "w"])

joined = df1.join(df2, how="outer")
print(joined)
```

## Exercises

1. Merge a products table with an orders table and calculate total revenue per product.
2. Concatenate 3 monthly DataFrames vertically and reset the index.
3. Perform a left join between employees and departments, identifying employees with no department.

---

[← prev](./chapter-04-groupby.md) | [next →](./chapter-06-timeseries.md)
