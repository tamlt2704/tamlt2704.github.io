# Episode 1: "What is a DataFrame?"

> Run the code: `python ep01_dataframe.py`

## The Setup

Karen from accounting sends you a Slack message: *"Hey, I need you to organize this employee data. I've got names, ages, cities, salaries, and departments. Can you put it in something... structured?"*

You open Python, import pandas, and show Karen what a real data structure looks like.

## Series — A Single Column

A **Series** is a one-dimensional labeled array. Think of it as a single column in a spreadsheet.

```python
import pandas as pd
import numpy as np

# A simple Series
names = pd.Series(["Alice", "Bob", "Charlie", "Diana", "Eve"])
print(names)
# 0      Alice
# 1        Bob
# 2    Charlie
# 3      Diana
# 4        Eve
# dtype: object

# Series with a custom index
salaries = pd.Series([85000, 72000, 90000, 65000, 78000],
                     index=["Alice", "Bob", "Charlie", "Diana", "Eve"])
print(salaries["Charlie"])  # 90000
```

A Series has an **index** (labels on the left) and **values** (the data). Every column in a DataFrame is a Series.

## DataFrame — The Whole Table

A **DataFrame** is a two-dimensional table — rows and columns, like a spreadsheet but with superpowers.

### Creating from a Dictionary

Each key becomes a column name, each value is a list of data:

```python
df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age":        [30, 25, 35, 28, 32],
    "City":       ["NYC", "LA", "NYC", "Chicago", "LA"],
    "Salary":     [85000, 72000, 90000, 65000, 78000],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing"]
})
print(df)
```

Output:
```
      Name  Age     City  Salary   Department
0    Alice   30      NYC   85000  Engineering
1      Bob   25       LA   72000    Marketing
2  Charlie   35      NYC   90000  Engineering
3    Diana   28  Chicago   65000           HR
4      Eve   32       LA   78000    Marketing
```

### Creating from a List of Lists

Each inner list becomes a row:

```python
data = [
    ["Alice", 30, "NYC", 85000, "Engineering"],
    ["Bob", 25, "LA", 72000, "Marketing"],
    ["Charlie", 35, "NYC", 90000, "Engineering"],
]
df2 = pd.DataFrame(data, columns=["Name", "Age", "City", "Salary", "Department"])
```

### Creating from a List of Dictionaries

Each dict becomes a row — great for JSON-like data:

```python
records = [
    {"Name": "Alice", "Age": 30, "City": "NYC"},
    {"Name": "Bob", "Age": 25, "City": "LA"},
]
df3 = pd.DataFrame(records)
```

## Series vs DataFrame — The Key Difference

```python
# Pulling a single column gives you a Series
ages = df["Age"]
print(type(ages))  # <class 'pandas.core.series.Series'>

# Pulling multiple columns gives you a DataFrame
subset = df[["Name", "Age"]]
print(type(subset))  # <class 'pandas.core.frame.DataFrame'>
```

## Inspecting Your DataFrame

```python
print(df.shape)    # (5, 5) — 5 rows, 5 columns
print(df.dtypes)   # data type of each column
print(df.columns)  # Index(['Name', 'Age', 'City', 'Salary', 'Department'])
print(df.index)    # RangeIndex(start=0, stop=5, step=1)
print(len(df))     # 5
```

## Karen's Reaction

*"Wait, so it's like Excel but in code? And I can't accidentally delete a formula? ...I'm interested."*

## Quick Reference

| Function / Attribute | What It Does |
|---|---|
| `pd.Series([...])` | Create a 1D labeled array |
| `pd.DataFrame({...})` | Create a table from a dictionary |
| `pd.DataFrame([...], columns=[...])` | Create a table from a list of lists |
| `df["col"]` | Get a single column (returns Series) |
| `df[["col1", "col2"]]` | Get multiple columns (returns DataFrame) |
| `df.shape` | Tuple of (rows, columns) |
| `df.dtypes` | Data type of each column |
| `df.columns` | Column names |
| `df.index` | Row labels |
| `len(df)` | Number of rows |
