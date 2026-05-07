# Episode 8: "Missing Data"

> Run the code: `python ep08_missing_data.py`

## The Setup

Karen's spreadsheet arrives with gaps everywhere. Her email: *"Some cells are blank, some say 'N/A', and one says 'ask Greg'. Can you clean this up? The board can't see empty cells."*

Missing data is the most common real-world problem. Pandas represents it as `NaN` (Not a Number) and gives you tools to detect, fill, or remove it.

## The Messy Dataset

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"],
    "Age":        [30, np.nan, 35, 28, 32, np.nan, 29],
    "City":       ["NYC", "LA", None, "Chicago", "LA", "NYC", np.nan],
    "Salary":     [85000, 72000, 90000, np.nan, 78000, 95000, 68000],
    "Department": ["Engineering", "Marketing", "Engineering", np.nan, "Marketing", "Engineering", "HR"]
})
print(df)
```

Output:
```
      Name   Age     City   Salary   Department
0    Alice  30.0      NYC  85000.0  Engineering
1      Bob   NaN       LA  72000.0    Marketing
2  Charlie  35.0     None  90000.0  Engineering
3    Diana  28.0  Chicago      NaN          NaN
4      Eve  32.0       LA  78000.0    Marketing
5    Frank   NaN      NYC  95000.0  Engineering
6    Grace  29.0     None  68000.0           HR
```

## Detecting Missing Data

### isna() / isnull() — Find the Gaps

```python
# Boolean mask: True where data is missing
print(df.isna())

# Count missing values per column
print(df.isna().sum())
# Name          0
# Age           2
# City          2
# Salary        1
# Department    1

# Total missing values
print(df.isna().sum().sum())  # 6

# Percentage missing per column
print(df.isna().mean() * 100)
# Age           28.57%
# City          28.57%
# Salary        14.29%
# Department    14.29%
```

### notna() — Find the Non-Gaps

```python
# Rows where Salary is NOT missing
has_salary = df[df["Salary"].notna()]
```

## Filling Missing Data

### fillna() — Replace NaN with a Value

```python
# Fill with a constant
df["Age"] = df["Age"].fillna(0)

# Fill with the column mean
df["Salary"] = df["Salary"].fillna(df["Salary"].mean())

# Fill with the column median (more robust to outliers)
df["Age"] = df["Age"].fillna(df["Age"].median())

# Fill strings with a placeholder
df["City"] = df["City"].fillna("Unknown")
df["Department"] = df["Department"].fillna("Unassigned")
```

### Fill with Forward/Backward Fill

```python
# Forward fill: use the previous row's value
df["City"] = df["City"].ffill()

# Backward fill: use the next row's value
df["City"] = df["City"].bfill()
```

### Fill with Group-Specific Values

```python
# Fill missing salary with department average
df["Salary"] = df.groupby("Department")["Salary"].transform(
    lambda x: x.fillna(x.mean())
)
```

## Dropping Missing Data

### dropna() — Remove Rows/Columns with NaN

```python
# Drop any row that has ANY missing value
df_clean = df.dropna()

# Drop rows only if specific columns are missing
df_clean = df.dropna(subset=["Salary", "Department"])

# Drop rows where ALL values are missing
df_clean = df.dropna(how="all")

# Drop columns with any missing values
df_clean = df.dropna(axis=1)

# Keep rows with at least 4 non-null values
df_clean = df.dropna(thresh=4)
```

## Interpolation — Smart Filling for Numeric Data

```python
# Linear interpolation (great for time series)
df["Salary"] = df["Salary"].interpolate()

# Method options: linear, polynomial, time, etc.
df["Age"] = df["Age"].interpolate(method="linear")
```

## Replacing Specific Values with NaN

Karen's data has "N/A", "ask Greg", and "-" instead of proper blanks:

```python
# Replace specific strings with NaN
df = df.replace(["N/A", "ask Greg", "-", ""], np.nan)

# Replace in specific columns
df["Salary"] = df["Salary"].replace(0, np.nan)
```

## A Complete Cleaning Workflow

```python
import pandas as pd
import numpy as np

# Load Karen's messy data
df = pd.read_csv("karen_data.csv", na_values=["N/A", "", "ask Greg", "-"])

# 1. See what's missing
print(df.isna().sum())

# 2. Fill numeric columns with median
df["Age"] = df["Age"].fillna(df["Age"].median())
df["Salary"] = df["Salary"].fillna(df["Salary"].median())

# 3. Fill categorical columns with mode or placeholder
df["City"] = df["City"].fillna("Unknown")
df["Department"] = df["Department"].fillna(df["Department"].mode()[0])

# 4. Verify no missing data remains
print(df.isna().sum())  # All zeros

# 5. Save
df.to_csv("cleaned_data.csv", index=False)
```

## Karen's Reaction

*"Why did you put 'Unknown' for the city? Can't you just guess?"*

No, Karen. We don't guess. We document what's missing and handle it transparently.

## Quick Reference

| Operation | Code |
|---|---|
| Detect missing | `df.isna()` or `df.isnull()` |
| Count missing per column | `df.isna().sum()` |
| Percent missing | `df.isna().mean() * 100` |
| Fill with value | `df["col"].fillna(value)` |
| Fill with mean | `df["col"].fillna(df["col"].mean())` |
| Forward fill | `df["col"].ffill()` |
| Backward fill | `df["col"].bfill()` |
| Drop rows with NaN | `df.dropna()` |
| Drop if specific cols NaN | `df.dropna(subset=["A", "B"])` |
| Interpolate | `df["col"].interpolate()` |
| Replace values with NaN | `df.replace("N/A", np.nan)` |
