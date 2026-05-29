---
title: "Chapter 3: Data Cleaning"
description: "Handling missing data, duplicates, and type conversions"
---

# Chapter 3: Data Cleaning

## Handling Missing Values

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "name": ["Alice", "Bob", None, "Diana"],
    "age": [25, np.nan, 35, 28],
    "salary": [50000, 60000, np.nan, np.nan]
})

print(df.isnull().sum())       # count nulls per column
df_dropped = df.dropna()       # drop rows with any null
df_filled = df.fillna({"age": df["age"].mean(), "salary": 0})
df["salary"] = df["salary"].interpolate()
```

## Removing Duplicates

```python
df = pd.DataFrame({
    "id": [1, 2, 2, 3, 3],
    "value": [10, 20, 20, 30, 30]
})

df_unique = df.drop_duplicates()
df_unique_id = df.drop_duplicates(subset=["id"], keep="last")
```

## Type Conversion

```python
df = pd.DataFrame({
    "price": ["10.5", "20.3", "15.0"],
    "date": ["2024-01-01", "2024-02-01", "2024-03-01"],
    "active": ["1", "0", "1"]
})

df["price"] = pd.to_numeric(df["price"])
df["date"] = pd.to_datetime(df["date"])
df["active"] = df["active"].astype(bool)
print(df.dtypes)
```

## String Operations

```python
df = pd.DataFrame({"name": ["  Alice ", "BOB", "charlie"]})
df["name"] = df["name"].str.strip().str.title()
print(df)
```

## Exercises

1. Load a dataset with missing values. Report the percentage of nulls per column and fill them with appropriate strategies.
2. Find and remove duplicate rows from a transaction dataset, keeping the most recent entry.
3. Convert a column of mixed date formats into a uniform datetime type.

---

[← prev](./chapter-02-indexing.md) | [next →](./chapter-04-groupby.md)
