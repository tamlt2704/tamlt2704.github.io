# Episode 3: "Selecting Data"

> Run the code: `python ep03_selecting.py`

## The Setup

Karen walks over to your desk: *"I don't need ALL the data. I just need names and salaries for the first three people. Can you do that without printing the whole thing?"*

Yes, Karen. Pandas has three ways to slice and dice.

## The Dataset

```python
import pandas as pd

df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age":        [30, 25, 35, 28, 32],
    "City":       ["NYC", "LA", "NYC", "Chicago", "LA"],
    "Salary":     [85000, 72000, 90000, 65000, 78000],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing"]
})
```

## Selecting Columns

```python
# Single column → returns a Series
names = df["Name"]
print(type(names))  # pandas.core.series.Series

# Multiple columns → returns a DataFrame
subset = df[["Name", "Salary"]]
print(subset)
#       Name  Salary
# 0    Alice   85000
# 1      Bob   72000
# 2  Charlie   90000
# 3    Diana   65000
# 4      Eve   78000
```

## loc — Label-Based Selection

`loc` uses **labels** (column names, index labels). Both start and end are **inclusive**.

```python
# Single row by index label
print(df.loc[0])  # First row as a Series

# Rows 0 through 2, columns "Name" through "City"
print(df.loc[0:2, "Name":"City"])
#       Name  Age City
# 0    Alice   30  NYC
# 1      Bob   25   LA
# 2  Charlie   35  NYC

# Specific rows and columns
print(df.loc[[0, 3], ["Name", "Salary"]])
#     Name  Salary
# 0  Alice   85000
# 3  Diana   65000
```

Key point: `loc[0:2]` includes row 2. It's **inclusive** on both ends.

## iloc — Integer-Based Selection

`iloc` uses **integer positions**. End is **exclusive** (like Python slicing).

```python
# First 3 rows, first 2 columns
print(df.iloc[0:3, 0:2])
#       Name  Age
# 0    Alice   30
# 1      Bob   25
# 2  Charlie   35

# Last row
print(df.iloc[-1])

# Every other row
print(df.iloc[::2])
#       Name  Age City  Salary   Department
# 0    Alice   30  NYC   85000  Engineering
# 2  Charlie   35  NYC   90000  Engineering
# 4      Eve   32   LA   78000    Marketing
```

Key point: `iloc[0:3]` gives rows 0, 1, 2 — row 3 is **excluded**.

## Boolean Indexing — Filter by Condition

```python
# Create a boolean mask
mask = df["Age"] > 30
print(mask)
# 0    False
# 1    False
# 2     True
# 3    False
# 4     True

# Apply the mask to filter rows
print(df[mask])
#       Name  Age City  Salary   Department
# 2  Charlie   35  NYC   90000  Engineering
# 4      Eve   32   LA   78000    Marketing

# Inline (most common style)
print(df[df["Age"] > 30])
```

## Combining Techniques

```python
# Boolean filter + column selection
print(df.loc[df["Age"] > 30, ["Name", "Salary"]])
#       Name  Salary
# 2  Charlie   90000
# 4      Eve   78000

# This is the pandas way: filter rows, pick columns, one line
senior_salaries = df.loc[df["Age"] > 30, "Salary"]
print(senior_salaries.mean())  # 84000.0
```

## loc vs iloc — When to Use Which

| | `loc` | `iloc` |
|---|---|---|
| **Uses** | Labels (names) | Integer positions |
| **End** | Inclusive | Exclusive |
| **Best for** | Named columns, custom indexes | Positional slicing |

## Karen's Reaction

*"So loc is like saying 'give me Name through City' and iloc is like saying 'give me columns 0, 1, 2'? Why do you need both?"*

Because sometimes you know the names, sometimes you know the positions. Different tools for different jobs.

## Quick Reference

| Syntax | What It Does |
|---|---|
| `df["col"]` | Single column (Series) |
| `df[["col1", "col2"]]` | Multiple columns (DataFrame) |
| `df.loc[row, col]` | Label-based selection (inclusive) |
| `df.iloc[row, col]` | Position-based selection (exclusive end) |
| `df[df["col"] > val]` | Boolean filter |
| `df.loc[mask, cols]` | Filter rows + select columns |
| `df.iloc[0:3, 0:2]` | First 3 rows, first 2 columns |
| `df.iloc[-1]` | Last row |
