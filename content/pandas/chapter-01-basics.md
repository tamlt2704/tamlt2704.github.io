---
title: "Chapter 1: Setup & Series/DataFrame"
description: "Core Pandas data structures"
---

# Chapter 1: Setup & Series/DataFrame

## Series

```python
import pandas as pd
import numpy as np

s = pd.Series([10, 20, 30, 40], index=["a", "b", "c", "d"])
print(s)
print(s["b"])        # 20
print(s[s > 15])     # filter
```

## DataFrame Creation

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Diana"],
    "age": [25, 30, 35, 28],
    "salary": [50000, 60000, 70000, 55000]
})
print(df)
print(df.dtypes)
print(df.describe())
```

## Reading Data

```python
# CSV
df = pd.read_csv("data.csv")

# Excel
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# JSON
df = pd.read_json("data.json")

# From dict of lists
df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
```

## Basic Operations

```python
df = pd.DataFrame({
    "product": ["A", "B", "C"],
    "price": [10, 20, 15],
    "quantity": [100, 50, 75]
})

df["revenue"] = df["price"] * df["quantity"]
print(df.shape)       # (3, 4)
print(df.columns)     # column names
print(df.head(2))     # first 2 rows
print(df.info())      # summary
```

## Exercises

1. Create a Series of 7 days' temperatures and compute the mean.
2. Build a DataFrame of 5 students with name, grade, and score columns. Filter students with score > 80.
3. Read a CSV from a URL (e.g., Iris dataset) and display `.describe()`.

---

[← prev](./chapter-00-overview.md) | [next →](./chapter-02-indexing.md)
