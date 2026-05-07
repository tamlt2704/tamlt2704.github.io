# Episode 2: "Reading & Writing Data"

> Run the code: `python ep02_read_write.py`

## The Setup

Karen emails you a CSV file called `employees.csv`. The subject line reads: *"Here's the data. Don't ask me what format it's in, I just exported it from somewhere."*

You download the file. Time to load it into pandas.

## Reading a CSV File

```python
import pandas as pd

# The most common way to get data into pandas
df = pd.read_csv("employees.csv")
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

### Useful read_csv Parameters

```python
# Skip rows, use different separator, handle missing values
df = pd.read_csv("messy_file.csv",
                 sep=";",              # semicolon-separated
                 header=0,             # first row is header (default)
                 skiprows=2,           # skip first 2 rows
                 na_values=["N/A", ""],# treat these as NaN
                 usecols=["Name", "Salary"])  # only load these columns
```

## First Look at Your Data

Karen's files are never clean. Before doing anything, inspect what you've got:

```python
# First 5 rows (default)
print(df.head())

# Last 3 rows
print(df.tail(3))

# Shape: (rows, columns)
print(df.shape)  # (5, 5)

# Column names, types, non-null counts
print(df.info())
```

`df.info()` output:
```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 5 entries, 0 to 4
Data columns (total 5 columns):
 #   Column      Non-Null Count  Dtype
---  ------      --------------  -----
 0   Name        5 non-null      object
 1   Age         5 non-null      int64
 2   City        5 non-null      object
 3   Salary      5 non-null      int64
 4   Department  5 non-null      object
dtypes: int64(2), object(3)
memory usage: 328.0+ bytes
```

## Statistical Summary

```python
# Quick stats for numeric columns
print(df.describe())
```

Output:
```
             Age        Salary
count   5.000000      5.000000
mean   30.000000  78000.000000
std     3.807887   9617.692031
min    25.000000  65000.000000
25%    28.000000  72000.000000
50%    30.000000  78000.000000
75%    32.000000  85000.000000
max    35.000000  90000.000000
```

## Writing Data Back Out

After you clean Karen's mess, you need to save it:

```python
# Save to CSV (no index column)
df.to_csv("cleaned_employees.csv", index=False)

# Save to Excel
df.to_excel("cleaned_employees.xlsx", index=False, sheet_name="Employees")

# Save to JSON
df.to_json("employees.json", orient="records", indent=2)
```

## Other File Formats

```python
# Excel files
df = pd.read_excel("file.xlsx", sheet_name="Sheet1")

# JSON
df = pd.read_json("file.json")

# From a URL
df = pd.read_csv("https://example.com/data.csv")

# Clipboard (paste from Excel/Google Sheets)
df = pd.read_clipboard()
```

## Karen's Reaction

*"Can you make it a CSV again when you're done? I need to email it to Greg. He only understands spreadsheets."*

Done. `to_csv("for_greg.csv", index=False)`.

## Quick Reference

| Function | What It Does |
|---|---|
| `pd.read_csv("file.csv")` | Load a CSV into a DataFrame |
| `pd.read_excel("file.xlsx")` | Load an Excel file |
| `pd.read_json("file.json")` | Load a JSON file |
| `df.head(n)` | First n rows (default 5) |
| `df.tail(n)` | Last n rows (default 5) |
| `df.shape` | (rows, columns) tuple |
| `df.info()` | Column types, non-null counts, memory |
| `df.describe()` | Statistical summary of numeric columns |
| `df.to_csv("out.csv", index=False)` | Save to CSV without row numbers |
| `df.to_excel("out.xlsx")` | Save to Excel |
| `df.to_json("out.json")` | Save to JSON |
