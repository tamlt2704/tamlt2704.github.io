# Episode 4: "Adding & Removing Columns"

> Run the code: `python ep04_add_remove_cols.py`

## The Setup

Karen sends a follow-up email: *"Can you add a bonus column? It's 10% of salary. Oh, and remove the Age column — HR said we can't share that anymore. Also, rename 'Name' to 'Employee' because Greg's report template needs that header."*

Three requests, three pandas operations. Let's go.

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

## Adding New Columns

### From a Calculation

```python
# New column based on existing data
df["Bonus"] = df["Salary"] * 0.1
print(df[["Name", "Salary", "Bonus"]])
#       Name  Salary   Bonus
# 0    Alice   85000  8500.0
# 1      Bob   72000  7200.0
# 2  Charlie   90000  9000.0
# 3    Diana   65000  6500.0
# 4      Eve   78000  7800.0
```

### From a Constant Value

```python
df["Country"] = "USA"
df["Active"] = True
```

### From a Condition

```python
import numpy as np

df["Senior"] = np.where(df["Age"] >= 30, "Yes", "No")
print(df[["Name", "Age", "Senior"]])
#       Name  Age Senior
# 0    Alice   30    Yes
# 1      Bob   25     No
# 2  Charlie   35    Yes
# 3    Diana   28     No
# 4      Eve   32    Yes
```

### Using insert() for Specific Position

```python
# Insert at position 1 (after Name)
df.insert(1, "Employee_ID", [101, 102, 103, 104, 105])
```

## Removing Columns

### drop() — The Standard Way

```python
# Drop a single column (returns new DataFrame)
df_no_age = df.drop("Age", axis=1)

# Drop multiple columns
df_clean = df.drop(["Age", "City"], axis=1)

# Drop in place (modifies the original)
df.drop("Age", axis=1, inplace=True)
```

### Using columns parameter (clearer)

```python
# Same thing, more readable
df_clean = df.drop(columns=["Age", "City"])
```

### del — Quick and Dirty

```python
# Deletes the column from the DataFrame directly
del df["Bonus"]
```

## Renaming Columns

### rename() — Selective Renaming

```python
# Rename specific columns
df = df.rename(columns={"Name": "Employee", "City": "Location"})
print(df.columns)
# Index(['Employee', 'Age', 'Location', 'Salary', 'Department'])
```

### Rename All Columns at Once

```python
# Set entirely new column names
df.columns = ["employee", "age", "city", "salary", "department"]

# Apply a function to all column names
df.columns = df.columns.str.upper()
df.columns = df.columns.str.replace(" ", "_")
```

## Reordering Columns

```python
# Specify the order you want
df = df[["Department", "Name", "Salary", "City", "Age"]]
```

## Putting It All Together — Karen's Request

```python
import pandas as pd

df = pd.DataFrame({
    "Name":       ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age":        [30, 25, 35, 28, 32],
    "City":       ["NYC", "LA", "NYC", "Chicago", "LA"],
    "Salary":     [85000, 72000, 90000, 65000, 78000],
    "Department": ["Engineering", "Marketing", "Engineering", "HR", "Marketing"]
})

# 1. Add bonus column
df["Bonus"] = df["Salary"] * 0.1

# 2. Remove Age
df = df.drop(columns=["Age"])

# 3. Rename Name → Employee
df = df.rename(columns={"Name": "Employee"})

print(df)
#   Employee     City  Salary   Department   Bonus
# 0    Alice      NYC   85000  Engineering  8500.0
# 1      Bob       LA   72000    Marketing  7200.0
# 2  Charlie      NYC   90000  Engineering  9000.0
# 3    Diana  Chicago   65000           HR  6500.0
# 4      Eve       LA   78000    Marketing  7800.0
```

## Karen's Reaction

*"Perfect. But can you also add a column that says 'Approved' for everyone? I need to pretend I reviewed these."*

```python
df["Status"] = "Approved"
```

Done.

## Quick Reference

| Operation | Code |
|---|---|
| Add column (calculated) | `df["New"] = df["Old"] * 2` |
| Add column (constant) | `df["Col"] = "value"` |
| Add column (conditional) | `df["Col"] = np.where(cond, "A", "B")` |
| Insert at position | `df.insert(pos, "Name", values)` |
| Drop column(s) | `df.drop(columns=["A", "B"])` |
| Drop in place | `df.drop(columns=["A"], inplace=True)` |
| Rename columns | `df.rename(columns={"old": "new"})` |
| Rename all | `df.columns = [...]` |
| Reorder | `df = df[["col2", "col1", "col3"]]` |
