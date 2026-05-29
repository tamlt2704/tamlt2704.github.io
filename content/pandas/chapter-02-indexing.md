---
title: "Chapter 2: Indexing & Selection"
description: "Selecting, filtering, and slicing data"
---

# Chapter 2: Indexing & Selection

## Column Selection

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["NYC", "LA", "Chicago"]
})

print(df["name"])           # single column (Series)
print(df[["name", "age"]])  # multiple columns (DataFrame)
```

## Row Selection with loc and iloc

```python
# loc: label-based
print(df.loc[0])              # first row
print(df.loc[0:1, "name"])    # rows 0-1, name column

# iloc: integer-based
print(df.iloc[0])             # first row
print(df.iloc[:2, :2])        # first 2 rows, first 2 cols
```

## Boolean Filtering

```python
df = pd.DataFrame({
    "product": ["A", "B", "C", "D", "E"],
    "price": [10, 25, 15, 40, 5],
    "stock": [100, 0, 50, 20, 200]
})

expensive = df[df["price"] > 15]
in_stock = df[df["stock"] > 0]
combined = df[(df["price"] > 10) & (df["stock"] > 0)]
print(combined)
```

## Setting and Resetting Index

```python
df = df.set_index("product")
print(df.loc["B"])

df = df.reset_index()
```

## Exercises

1. Create a DataFrame of 10 employees. Select those in the "Engineering" department with salary > 80k.
2. Use `.iloc` to select every other row from a 20-row DataFrame.
3. Set a multi-level index (department, name) and select all rows for one department.

---

[← prev](./chapter-01-basics.md) | [next →](./chapter-03-cleaning.md)
