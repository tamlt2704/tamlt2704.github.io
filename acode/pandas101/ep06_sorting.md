# Episode 6: "Sorting"

> Run the code: `python ep06_sorting.py`

## The Setup

Karen's email, 8:47 AM: *"I need the employee list sorted by salary, highest first. Actually wait — sort by city alphabetically, and WITHIN each city sort by salary highest first. The board meeting is in an hour."*

Two sorts, one line of code. Let's go.

## The Dataset

```python
import pandas as pd

df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"],
    "Age":        [30, 25, 35, 28, 32, 45, 29],
    "City":       ["NYC", "LA", "NYC", "Chicago", "LA", "NYC", "Chicago"],
    "Salary":     [85000, 72000, 90000, 65000, 78000, 95000, 68000],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing", "Engineering", "HR"]
})
```

## sort_values() — Sort by Column

### Single Column

```python
# Sort by salary, lowest first (default: ascending=True)
df_sorted = df.sort_values("Salary")
print(df_sorted[["Name", "Salary"]])
#       Name  Salary
# 3    Diana   65000
# 6    Grace   68000
# 1      Bob   72000
# 4      Eve   78000
# 0    Alice   85000
# 2  Charlie   90000
# 5    Frank   95000

# Highest first
df_sorted = df.sort_values("Salary", ascending=False)
```

### Multiple Columns

```python
# Sort by City (A→Z), then by Salary within each city (high→low)
df_sorted = df.sort_values(["City", "Salary"], ascending=[True, False])
print(df_sorted[["Name", "City", "Salary"]])
#       Name     City  Salary
# 6    Grace  Chicago   68000
# 3    Diana  Chicago   65000
# 4      Eve       LA   78000
# 1      Bob       LA   72000
# 5    Frank      NYC   95000
# 2  Charlie      NYC   90000
# 0    Alice      NYC   85000
```

The `ascending` parameter takes a list — one value per column.

## sort_index() — Sort by Row Index

```python
# After filtering, your index might be jumbled
filtered = df[df["Salary"] > 70000]
print(filtered.index)  # Int64Index([0, 1, 2, 4, 5])

# Sort by index to restore order
filtered_sorted = filtered.sort_index()
```

## Sorting with NaN Values

```python
import numpy as np

df.loc[2, "Salary"] = np.nan

# NaN goes to the end by default
df.sort_values("Salary")

# Put NaN first
df.sort_values("Salary", na_position="first")
```

## In-Place Sorting

```python
# Returns a new DataFrame (original unchanged)
df_sorted = df.sort_values("Salary")

# Modifies the original DataFrame
df.sort_values("Salary", inplace=True)
```

## Sorting by String Length or Custom Logic

```python
# Sort by name length
df_sorted = df.iloc[df["Name"].str.len().argsort()]

# Or use a key function (pandas 1.1+)
df_sorted = df.sort_values("Name", key=lambda x: x.str.len())
```

## Ranking Instead of Sorting

Sometimes you want to add a rank column without reordering:

```python
df["Salary_Rank"] = df["Salary"].rank(ascending=False)
print(df[["Name", "Salary", "Salary_Rank"]])
#       Name  Salary  Salary_Rank
# 0    Alice   85000          3.0
# 1      Bob   72000          5.0
# 2  Charlie   90000          2.0
# 3    Diana   65000          7.0
# 4      Eve   78000          4.0
# 5    Frank   95000          1.0
# 6    Grace   68000          6.0
```

## nlargest / nsmallest — Quick Top/Bottom N

```python
# Top 3 salaries (faster than sort + head for large DataFrames)
print(df.nlargest(3, "Salary"))
#       Name  Age City  Salary   Department
# 5    Frank   45  NYC   95000  Engineering
# 2  Charlie   35  NYC   90000  Engineering
# 0    Alice   30  NYC   85000  Engineering

# Bottom 2 salaries
print(df.nsmallest(2, "Salary"))
```

## Karen's Request — Solved

```python
# City alphabetical, salary descending within each city
result = df.sort_values(["City", "Salary"], ascending=[True, False])
result.to_csv("for_the_board.csv", index=False)
```

## Karen's Reaction

*"This is perfect. Can you also sort by 'vibes'? Like who has the best energy?"*

That's not a column, Karen.

## Quick Reference

| Operation | Code |
|---|---|
| Sort by one column (ascending) | `df.sort_values("col")` |
| Sort descending | `df.sort_values("col", ascending=False)` |
| Sort by multiple columns | `df.sort_values(["A", "B"], ascending=[True, False])` |
| Sort by index | `df.sort_index()` |
| NaN position | `df.sort_values("col", na_position="first")` |
| Sort in place | `df.sort_values("col", inplace=True)` |
| Rank values | `df["col"].rank(ascending=False)` |
| Top N | `df.nlargest(n, "col")` |
| Bottom N | `df.nsmallest(n, "col")` |
| Sort by key function | `df.sort_values("col", key=lambda x: x.str.len())` |
