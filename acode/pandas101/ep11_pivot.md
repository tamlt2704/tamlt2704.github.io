# Episode 11: "Pivot Tables"

> Run the code: `python ep11_pivot.py`

## The Setup

Karen forwards an email from the VP: *"I need a table showing average salary by city AND department. Cities as rows, departments as columns. Like a cross-tab. Can your Python thing do that?"*

This is exactly what pivot tables are for. Excel made them famous, pandas makes them programmable.

## The Dataset

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"],
    "Age":        [30, 25, 35, 28, 32, 45, 29],
    "City":       ["NYC", "LA", "NYC", "Chicago", "LA", "NYC", "Chicago"],
    "Salary":     [85000, 72000, 90000, 65000, 78000, 95000, 68000],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing", "Engineering", "HR"],
    "Q1_Sales":   [12000, 8000, 15000, 5000, 9000, 18000, 6000],
    "Q2_Sales":   [14000, 9500, 16000, 5500, 11000, 20000, 7000]
})
```

## pivot_table() — The Power Tool

```python
# Average salary: cities as rows, departments as columns
pivot = df.pivot_table(
    values="Salary",
    index="City",
    columns="Department",
    aggfunc="mean"
)
print(pivot)
# Department  Engineering       HR  Marketing
# City
# Chicago             NaN  66500.0        NaN
# LA                  NaN      NaN    75000.0
# NYC           90000.0      NaN        NaN
```

NaN appears where there's no data (no Engineers in Chicago, etc.).

### Fill Missing Values

```python
pivot = df.pivot_table(
    values="Salary",
    index="City",
    columns="Department",
    aggfunc="mean",
    fill_value=0
)
```

### Multiple Aggregations

```python
pivot = df.pivot_table(
    values="Salary",
    index="City",
    columns="Department",
    aggfunc=["mean", "count"]
)
```

### Add Margins (Totals)

```python
pivot = df.pivot_table(
    values="Salary",
    index="City",
    columns="Department",
    aggfunc="mean",
    margins=True,        # adds "All" row and column
    margins_name="Total"
)
```

## melt() — Unpivot (Wide → Long)

`melt()` is the reverse of pivot — it takes a wide table and makes it long:

```python
# We have Q1_Sales and Q2_Sales as separate columns (wide format)
# Convert to long format: one row per quarter per person
melted = pd.melt(
    df,
    id_vars=["Name", "Department"],    # columns to keep
    value_vars=["Q1_Sales", "Q2_Sales"],  # columns to unpivot
    var_name="Quarter",                # name for the new category column
    value_name="Sales"                 # name for the new value column
)
print(melted.head(6))
#       Name   Department  Quarter  Sales
# 0    Alice  Engineering  Q1_Sales  12000
# 1      Bob    Marketing  Q1_Sales   8000
# 2  Charlie  Engineering  Q1_Sales  15000
# 3    Diana           HR  Q1_Sales   5000
# 4      Eve    Marketing  Q1_Sales   9000
# 5    Frank  Engineering  Q1_Sales  18000
```

Now you can easily group by Quarter:
```python
melted.groupby("Quarter")["Sales"].mean()
```

## stack() and unstack()

These reshape the index levels:

```python
# Create a multi-index pivot
pivot = df.pivot_table(values="Salary", index="City", columns="Department", aggfunc="mean")

# stack: columns → index (wide → long)
stacked = pivot.stack()
print(stacked)
# City     Department
# Chicago  HR             66500.0
# LA       Marketing      75000.0
# NYC      Engineering    90000.0
# dtype: float64

# unstack: index → columns (long → wide)
unstacked = stacked.unstack()
# Back to the pivot table format
```

## pivot() vs pivot_table()

```python
# pivot() — simple reshape, no aggregation (fails if duplicates)
# Use when each combination of index/columns is unique
simple = df.pivot(index="Name", columns="Department", values="Salary")

# pivot_table() — handles duplicates with aggregation
# Use when you need to summarize
summary = df.pivot_table(values="Salary", index="City", columns="Department", aggfunc="mean")
```

## Real-World Example: Monthly Report

```python
# Sales data with dates
sales = pd.DataFrame({
    "Month": ["Jan", "Jan", "Feb", "Feb", "Mar", "Mar"] * 2,
    "Region": ["East", "West"] * 6,
    "Product": ["Widget", "Widget", "Widget", "Widget", "Widget", "Widget",
                "Gadget", "Gadget", "Gadget", "Gadget", "Gadget", "Gadget"],
    "Revenue": [100, 150, 120, 160, 130, 170, 80, 90, 85, 95, 90, 100]
})

# Monthly revenue by product and region
report = sales.pivot_table(
    values="Revenue",
    index="Product",
    columns="Month",
    aggfunc="sum",
    margins=True
)
print(report)
```

## Karen's Reaction

*"This looks exactly like my Excel pivot table! But I didn't have to drag anything into boxes? And it updates automatically when the data changes?"*

Yes. And you can version-control it.

## Quick Reference

| Operation | Code |
|---|---|
| Basic pivot table | `df.pivot_table(values="V", index="I", columns="C", aggfunc="mean")` |
| Fill NaN in pivot | `pivot_table(..., fill_value=0)` |
| Add totals | `pivot_table(..., margins=True)` |
| Multiple agg functions | `pivot_table(..., aggfunc=["mean", "sum"])` |
| Melt (wide → long) | `pd.melt(df, id_vars=[...], value_vars=[...])` |
| Stack (cols → index) | `df.stack()` |
| Unstack (index → cols) | `df.unstack()` |
| Simple pivot (no agg) | `df.pivot(index="A", columns="B", values="C")` |
