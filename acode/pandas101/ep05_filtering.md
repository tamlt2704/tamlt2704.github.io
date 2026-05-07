# Episode 5: "Filtering Rows"

> Run the code: `python ep05_filtering.py`

## The Setup

Karen pings you at 4:55 PM: *"I need a list of everyone in NYC making over $80K. Also everyone in NYC OR LA. Oh, and anyone making between $70K and $85K. Can you have that by 5?"*

Three filters. Five minutes. Pandas makes this trivial.

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

## Single Condition

```python
# Everyone in NYC
nyc = df[df["City"] == "NYC"]
print(nyc)
#       Name  Age City  Salary   Department
# 0    Alice   30  NYC   85000  Engineering
# 2  Charlie   35  NYC   90000  Engineering
# 5    Frank   45  NYC   95000  Engineering
```

How it works: `df["City"] == "NYC"` creates a boolean Series (True/False for each row). Passing that into `df[...]` keeps only the True rows.

## Multiple Conditions

Use `&` (and), `|` (or), `~` (not). **Wrap each condition in parentheses.**

```python
# NYC AND salary > 80K
high_earners_nyc = df[(df["City"] == "NYC") & (df["Salary"] > 80000)]
print(high_earners_nyc)
#       Name  Age City  Salary   Department
# 0    Alice   30  NYC   85000  Engineering
# 2  Charlie   35  NYC   90000  Engineering
# 5    Frank   45  NYC   95000  Engineering

# NYC OR LA
coastal = df[(df["City"] == "NYC") | (df["City"] == "LA")]
print(coastal)
#       Name  Age City  Salary   Department
# 0    Alice   30  NYC   85000  Engineering
# 1      Bob   25   LA   72000    Marketing
# 2  Charlie   35  NYC   90000  Engineering
# 4      Eve   32   LA   78000    Marketing
# 5    Frank   45  NYC   95000  Engineering

# NOT in Engineering
non_eng = df[~(df["Department"] == "Engineering")]
```

## isin() — Multiple Values for One Column

Instead of chaining `|` conditions, use `isin()`:

```python
# Much cleaner than (df["City"] == "NYC") | (df["City"] == "LA")
coastal = df[df["City"].isin(["NYC", "LA"])]

# Exclude specific values
not_coastal = df[~df["City"].isin(["NYC", "LA"])]
```

## between() — Range Filtering

```python
# Salary between 70K and 85K (inclusive on both ends)
mid_range = df[df["Salary"].between(70000, 85000)]
print(mid_range)
#     Name  Age City  Salary   Department
# 0  Alice   30  NYC   85000  Engineering
# 1    Bob   25   LA   72000    Marketing
# 4    Eve   32   LA   78000    Marketing
```

## String Filtering

```python
# Names that start with a vowel
vowel_names = df[df["Name"].str.startswith(("A", "E"))]

# City contains "C" (case-insensitive)
has_c = df[df["City"].str.contains("c", case=False)]

# Department name length > 5
long_dept = df[df["Department"].str.len() > 5]
```

## query() — SQL-Like Syntax

```python
# Same as df[(df["City"] == "NYC") & (df["Salary"] > 80000)]
result = df.query("City == 'NYC' and Salary > 80000")

# Can reference variables with @
min_salary = 80000
result = df.query("Salary > @min_salary")
```

## Resetting the Index After Filtering

```python
filtered = df[df["City"] == "NYC"]
print(filtered.index)  # Int64Index([0, 2, 5])

# Reset to 0, 1, 2...
filtered = filtered.reset_index(drop=True)
print(filtered.index)  # RangeIndex(start=0, stop=3, step=1)
```

## Karen's Three Requests — Solved

```python
# 1. NYC and over $80K
print(df[(df["City"] == "NYC") & (df["Salary"] > 80000)])

# 2. NYC or LA
print(df[df["City"].isin(["NYC", "LA"])])

# 3. Between $70K and $85K
print(df[df["Salary"].between(70000, 85000)])
```

## Karen's Reaction

*"Great, now can you filter out everyone who started after 2020? Oh wait, we don't have start dates. Never mind."*

Classic Karen.

## Quick Reference

| Operation | Code |
|---|---|
| Single condition | `df[df["col"] == value]` |
| AND | `df[(cond1) & (cond2)]` |
| OR | `df[(cond1) \| (cond2)]` |
| NOT | `df[~(condition)]` |
| Multiple values | `df[df["col"].isin([v1, v2])]` |
| Range | `df[df["col"].between(lo, hi)]` |
| String contains | `df[df["col"].str.contains("x")]` |
| String starts with | `df[df["col"].str.startswith("x")]` |
| SQL-like | `df.query("col > 5 and col2 == 'x'")` |
| Reset index | `df.reset_index(drop=True)` |
