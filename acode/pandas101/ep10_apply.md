# Episode 10: "Apply & Lambda"

> Run the code: `python ep10_apply.py`

## The Setup

Karen's latest request: *"I need a tax column. If salary is over $80K, tax is 30%. Otherwise it's 20%. Oh, and make all the names uppercase. And add a column that says 'Senior' if they're over 30 and in Engineering."*

This is custom logic territory. When built-in pandas methods aren't enough, `apply()` and `lambda` let you run any function on your data.

## The Dataset

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age":        [30, 25, 35, 28, 32],
    "City":       ["NYC", "LA", "NYC", "Chicago", "LA"],
    "Salary":     [85000, 72000, 90000, 65000, 78000],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing"]
})
```

## Lambda — Quick Anonymous Functions

A lambda is a one-line function without a name:

```python
# Regular function
def double(x):
    return x * 2

# Same thing as a lambda
double = lambda x: x * 2
```

## apply() on a Series (Column)

Apply a function to every value in a column:

```python
# Uppercase all names
df["Name_Upper"] = df["Name"].apply(lambda x: x.upper())
print(df["Name_Upper"])
# 0      ALICE
# 1        BOB
# 2    CHARLIE
# 3      DIANA
# 4        EVE

# Tax calculation
df["Tax"] = df["Salary"].apply(lambda x: x * 0.3 if x > 80000 else x * 0.2)
print(df[["Name", "Salary", "Tax"]])
#       Name  Salary      Tax
# 0    Alice   85000  25500.0
# 1      Bob   72000  14400.0
# 2  Charlie   90000  27000.0
# 3    Diana   65000  13000.0
# 4      Eve   78000  15600.0
```

## apply() on a DataFrame (Row-wise)

Use `axis=1` to apply a function to each **row**:

```python
# Complex logic using multiple columns
def classify(row):
    if row["Age"] > 30 and row["Department"] == "Engineering":
        return "Senior Engineer"
    elif row["Age"] > 30:
        return "Senior"
    else:
        return "Junior"

df["Level"] = df.apply(classify, axis=1)
print(df[["Name", "Age", "Department", "Level"]])
#       Name  Age   Department            Level
# 0    Alice   30  Engineering           Junior
# 1      Bob   25    Marketing           Junior
# 2  Charlie   35  Engineering  Senior Engineer
# 3    Diana   28           HR           Junior
# 4      Eve   32    Marketing           Senior
```

## map() — For Series Only

`map()` works on a Series and is great for value mapping:

```python
# Map values using a dictionary
city_codes = {"NYC": "NY", "LA": "CA", "Chicago": "IL"}
df["State"] = df["City"].map(city_codes)
print(df[["City", "State"]])
#      City State
# 0     NYC    NY
# 1      LA    CA
# 2     NYC    NY
# 3 Chicago    IL
# 4      LA    CA

# Map with a function (same as apply for Series)
df["Name_Length"] = df["Name"].map(len)
```

## Vectorized Operations — The Fast Way

Before reaching for `apply()`, check if pandas/numpy can do it natively:

```python
# SLOW: apply with lambda
df["Bonus"] = df["Salary"].apply(lambda x: x * 0.1)

# FAST: vectorized (same result, 10-100x faster)
df["Bonus"] = df["Salary"] * 0.1

# SLOW: apply for conditional
df["Tax"] = df["Salary"].apply(lambda x: x * 0.3 if x > 80000 else x * 0.2)

# FAST: np.where (vectorized conditional)
df["Tax"] = np.where(df["Salary"] > 80000, df["Salary"] * 0.3, df["Salary"] * 0.2)

# FAST: np.select (multiple conditions)
conditions = [
    df["Salary"] > 90000,
    df["Salary"] > 70000,
    df["Salary"] <= 70000
]
choices = [0.35, 0.30, 0.20]
df["Tax_Rate"] = np.select(conditions, choices)
```

## When to Use What

| Situation | Best Tool |
|---|---|
| Simple math on columns | Vectorized: `df["A"] * 2` |
| Simple condition | `np.where(cond, val1, val2)` |
| Multiple conditions | `np.select(conditions, choices)` |
| Value mapping (dict) | `df["col"].map(dict)` |
| Custom logic, one column | `df["col"].apply(func)` |
| Custom logic, multiple columns | `df.apply(func, axis=1)` |

## String Methods — No apply() Needed

```python
# These are vectorized and fast
df["Name"].str.upper()
df["Name"].str.lower()
df["Name"].str.len()
df["Name"].str.contains("a")
df["Name"].str.replace("Alice", "Alicia")
df["City"].str.strip()  # remove whitespace
```

## Karen's Three Requests — Solved

```python
# 1. Tax column (30% if over 80K, else 20%)
df["Tax"] = np.where(df["Salary"] > 80000, df["Salary"] * 0.3, df["Salary"] * 0.2)

# 2. Uppercase names
df["Name"] = df["Name"].str.upper()

# 3. Senior Engineer flag
df["Level"] = df.apply(
    lambda row: "Senior" if row["Age"] > 30 and row["Department"] == "Engineering" else "Other",
    axis=1
)
```

## Karen's Reaction

*"Can you apply a function that makes everyone's salary higher? Asking for a friend."*

That's called a raise, Karen. Talk to HR.

## Quick Reference

| Operation | Code |
|---|---|
| Apply to column | `df["col"].apply(func)` |
| Apply to row | `df.apply(func, axis=1)` |
| Lambda (inline) | `df["col"].apply(lambda x: x * 2)` |
| Map with dict | `df["col"].map({"a": 1, "b": 2})` |
| Vectorized math | `df["col"] * 2` |
| Vectorized condition | `np.where(cond, val_true, val_false)` |
| Multiple conditions | `np.select(conditions, choices)` |
| String methods | `df["col"].str.upper()` |
