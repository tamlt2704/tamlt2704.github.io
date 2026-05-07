# Episode 9: "Merge & Join"

> Run the code: `python ep09_merge_join.py`

## The Setup

Karen sends two separate spreadsheets: *"Here's the employee list and here's the department budgets. Can you combine them? They both have a Department column so it should be easy, right?"*

It IS easy — with `merge`. This is pandas' equivalent of SQL JOINs.

## The Datasets

```python
import pandas as pd

# Employee data
employees = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age":        [30, 25, 35, 28, 32],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing"],
    "Salary":     [85000, 72000, 90000, 65000, 78000]
})

# Department budgets
departments = pd.DataFrame({
    "Department": ["Engineering", "Marketing", "HR", "Sales"],
    "Budget":     [500000, 200000, 150000, 300000],
    "Manager":    ["Sarah", "Tom", "Lisa", "Jake"]
})
```

## merge() — The Main Tool

### Inner Join (Default)

Only keeps rows where the key exists in **both** DataFrames:

```python
result = pd.merge(employees, departments, on="Department")
print(result)
#       Name  Age   Department  Salary  Budget Manager
# 0    Alice   30  Engineering   85000  500000   Sarah
# 1  Charlie   35  Engineering   90000  500000   Sarah
# 2      Bob   25    Marketing   72000  200000     Tom
# 3      Eve   32    Marketing   78000  200000     Tom
# 4    Diana   28           HR   65000  150000    Lisa
```

Note: "Sales" from departments is gone (no employees in Sales).

### Left Join

Keep ALL rows from the left DataFrame, fill NaN where no match:

```python
result = pd.merge(employees, departments, on="Department", how="left")
# All 5 employees kept, matched with department info
```

### Right Join

Keep ALL rows from the right DataFrame:

```python
result = pd.merge(employees, departments, on="Department", how="right")
# All 4 departments kept, Sales row has NaN for employee fields
```

### Outer Join

Keep ALL rows from both:

```python
result = pd.merge(employees, departments, on="Department", how="outer")
# All employees + Sales department (with NaN for employee fields)
```

## Merging on Different Column Names

```python
# When the key columns have different names
employees2 = employees.rename(columns={"Department": "Dept"})
result = pd.merge(employees2, departments, left_on="Dept", right_on="Department")
```

## Merging on Multiple Keys

```python
# Match on multiple columns
orders = pd.DataFrame({
    "Name": ["Alice", "Alice", "Bob"],
    "Year": [2023, 2024, 2024],
    "Amount": [1000, 1500, 800]
})

targets = pd.DataFrame({
    "Name": ["Alice", "Alice", "Bob"],
    "Year": [2023, 2024, 2024],
    "Target": [1200, 1400, 900]
})

result = pd.merge(orders, targets, on=["Name", "Year"])
```

## concat() — Stacking DataFrames

### Vertical Stack (Adding Rows)

```python
# Two DataFrames with the same columns
team_a = pd.DataFrame({"Name": ["Alice", "Bob"], "Salary": [85000, 72000]})
team_b = pd.DataFrame({"Name": ["Charlie", "Diana"], "Salary": [90000, 65000]})

# Stack them
all_teams = pd.concat([team_a, team_b], ignore_index=True)
print(all_teams)
#       Name  Salary
# 0    Alice   85000
# 1      Bob   72000
# 2  Charlie   90000
# 3    Diana   65000
```

### Horizontal Stack (Adding Columns)

```python
names = pd.DataFrame({"Name": ["Alice", "Bob", "Charlie"]})
ages = pd.DataFrame({"Age": [30, 25, 35]})

combined = pd.concat([names, ages], axis=1)
```

## join() — Merge on Index

```python
# When the key is the index, not a column
dept_info = departments.set_index("Department")
emp_indexed = employees.set_index("Department")

result = emp_indexed.join(dept_info)
```

## Handling Duplicate Column Names

```python
# Both DataFrames have a "Manager" column
result = pd.merge(df1, df2, on="Department", suffixes=("_emp", "_dept"))
# Creates: Manager_emp, Manager_dept
```

## Validating Merges

```python
# Ensure the merge key is unique in the right DataFrame
result = pd.merge(employees, departments, on="Department", validate="many_to_one")

# Options: "one_to_one", "one_to_many", "many_to_one", "many_to_many"
```

## Indicator — See Where Rows Came From

```python
result = pd.merge(employees, departments, on="Department", how="outer", indicator=True)
print(result["_merge"].value_counts())
# both          5
# right_only    1  (Sales — no employees)
```

## Karen's Reaction

*"So you just... connected them? Like a VLOOKUP but it actually works? I've been copy-pasting between sheets for months."*

## Quick Reference

| Operation | Code |
|---|---|
| Inner join | `pd.merge(df1, df2, on="key")` |
| Left join | `pd.merge(df1, df2, on="key", how="left")` |
| Right join | `pd.merge(df1, df2, on="key", how="right")` |
| Outer join | `pd.merge(df1, df2, on="key", how="outer")` |
| Different key names | `pd.merge(df1, df2, left_on="A", right_on="B")` |
| Multiple keys | `pd.merge(df1, df2, on=["A", "B"])` |
| Stack rows | `pd.concat([df1, df2], ignore_index=True)` |
| Stack columns | `pd.concat([df1, df2], axis=1)` |
| Join on index | `df1.join(df2)` |
| Handle duplicates | `pd.merge(..., suffixes=("_x", "_y"))` |
| Validate | `pd.merge(..., validate="many_to_one")` |
| Indicator | `pd.merge(..., indicator=True)` |
