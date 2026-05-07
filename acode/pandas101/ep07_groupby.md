# Episode 7: "GroupBy"

> Run the code: `python ep07_groupby.py`

## The Setup

Karen's 3 PM Slack: *"I need average salary by department. And also the highest salary in each city. And the headcount per department. Can pandas do all that at once?"*

Yes. GroupBy is the split-apply-combine pattern, and it's one of pandas' most powerful features.

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

## The Split-Apply-Combine Pattern

1. **Split** — divide the DataFrame into groups
2. **Apply** — perform a calculation on each group
3. **Combine** — merge results back together

```python
# Split by Department, apply mean to Salary, combine into a Series
avg_salary = df.groupby("Department")["Salary"].mean()
print(avg_salary)
# Department
# Engineering    90000.0
# HR             66500.0
# Marketing      75000.0
# Name: Salary, dtype: float64
```

## Basic Aggregations

```python
# Single aggregation
df.groupby("Department")["Salary"].mean()
df.groupby("Department")["Salary"].sum()
df.groupby("Department")["Salary"].max()
df.groupby("Department")["Salary"].min()
df.groupby("City")["Name"].count()  # headcount per city

# Multiple columns
df.groupby("Department")[["Salary", "Age"]].mean()
```

## agg() — Multiple Aggregations at Once

```python
# Different aggregations for different columns
result = df.groupby("Department").agg({
    "Salary": "mean",
    "Age": "max",
    "Name": "count"
})
print(result)
#              Salary  Age  Name
# Department
# Engineering   90000   45     3
# HR            66500   29     2
# Marketing     75000   32     2

# Multiple aggregations on one column
salary_stats = df.groupby("Department")["Salary"].agg(["mean", "min", "max", "count"])
print(salary_stats)
#                  mean    min    max  count
# Department
# Engineering  90000.0  85000  95000      3
# HR           66500.0  65000  68000      2
# Marketing    75000.0  72000  78000      2
```

## Named Aggregations (Clean Output)

```python
result = df.groupby("Department").agg(
    avg_salary=("Salary", "mean"),
    max_age=("Age", "max"),
    headcount=("Name", "count")
)
print(result)
#              avg_salary  max_age  headcount
# Department
# Engineering     90000.0       45          3
# HR              66500.0       29          2
# Marketing       75000.0       32          2
```

## Grouping by Multiple Columns

```python
# Group by City AND Department
result = df.groupby(["City", "Department"])["Salary"].mean()
print(result)
# City     Department
# Chicago  HR             66500.0
# LA       Marketing      75000.0
# NYC      Engineering    90000.0
# Name: Salary, dtype: float64
```

## transform() — Keep Original Shape

`agg()` reduces rows. `transform()` returns a value for every row (same shape as input).

```python
# Add a column with each person's department average
df["Dept_Avg_Salary"] = df.groupby("Department")["Salary"].transform("mean")
print(df[["Name", "Department", "Salary", "Dept_Avg_Salary"]])
#       Name   Department  Salary  Dept_Avg_Salary
# 0    Alice  Engineering   85000          90000.0
# 1      Bob    Marketing   72000          75000.0
# 2  Charlie  Engineering   90000          90000.0
# ...

# How much above/below department average?
df["vs_Dept_Avg"] = df["Salary"] - df.groupby("Department")["Salary"].transform("mean")
```

## filter() — Keep/Drop Entire Groups

```python
# Only keep departments with more than 2 people
big_depts = df.groupby("Department").filter(lambda x: len(x) > 2)
print(big_depts)  # Only Engineering (3 people)
```

## Iterating Over Groups

```python
for name, group in df.groupby("Department"):
    print(f"\n--- {name} ---")
    print(group[["Name", "Salary"]])
```

## Karen's Reaction

*"Wait, you got average salary, max salary, AND headcount in one line? I've been doing this manually in Excel for three years."*

Welcome to pandas, Karen.

## Quick Reference

| Operation | Code |
|---|---|
| Group + single agg | `df.groupby("col")["val"].mean()` |
| Group + multiple aggs | `df.groupby("col").agg({"A": "mean", "B": "max"})` |
| Named aggregations | `df.groupby("col").agg(name=("col", "func"))` |
| Multiple group keys | `df.groupby(["A", "B"])["C"].sum()` |
| Transform (keep shape) | `df.groupby("col")["val"].transform("mean")` |
| Filter groups | `df.groupby("col").filter(lambda x: len(x) > 2)` |
| Count per group | `df.groupby("col").size()` |
| Iterate groups | `for name, group in df.groupby("col"):` |
