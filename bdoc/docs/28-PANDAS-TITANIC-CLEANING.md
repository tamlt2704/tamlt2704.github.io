# Chapter 28: Master Pandas — Clean the Titanic Dataset from Kaggle

## What you'll learn

- Pandas fundamentals: Series, DataFrame, indexing
- Loading and inspecting data (shape, dtypes, head, describe)
- Handling missing values (detect, fill, drop)
- Data cleaning: type conversion, string operations, outlier removal
- Feature engineering: creating new columns from existing data
- Grouping, aggregation, and pivot tables
- The full Titanic data cleaning pipeline (Kaggle competition ready)
- Exporting clean data for machine learning

---

## PART 1: Pandas Fundamentals

## 28.1 What is Pandas?

Pandas is Python's data manipulation library. Think of it as Excel/SQL in code — but faster, reproducible, and scriptable.

```python
import pandas as pd
import numpy as np
```

**Two core objects:**
- `Series` — a single column (1D labeled array)
- `DataFrame` — a table (2D labeled array = collection of Series)

```python
# Series — like a column in a spreadsheet
ages = pd.Series([22, 38, 26, 35], name="Age")
# 0    22
# 1    38
# 2    26
# 3    35
# Name: Age, dtype: int64

# DataFrame — like a whole spreadsheet
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Carol", "Dave"],
    "Age": [22, 38, 26, 35],
    "Survived": [1, 1, 0, 0],
})
#     Name  Age  Survived
# 0  Alice   22         1
# 1    Bob   38         1
# 2  Carol   26         0
# 3   Dave   35         0
```

## 28.2 Load the Titanic dataset

Download from [Kaggle](https://www.kaggle.com/c/titanic/data) or use:

```python
# Read CSV
df = pd.read_csv("train.csv")

# Quick overview
print(df.shape)        # (891, 12) — 891 rows, 12 columns
print(df.columns)      # Index(['PassengerId', 'Survived', 'Pclass', ...])
print(df.dtypes)       # data types per column
```

## 28.3 Inspect the data

```python
# First 5 rows
df.head()

# Last 5 rows
df.tail()

# Random sample
df.sample(5)

# Statistical summary (numeric columns)
df.describe()
#        PassengerId    Survived      Pclass         Age       SibSp       Parch        Fare
# count   891.000000  891.000000  891.000000  714.000000  891.000000  891.000000  891.000000
# mean    446.000000    0.383838    2.308642   29.699118    0.523008    0.381594   32.204208
# std     257.353842    0.486592    0.836071   14.526497    1.102743    0.806057   49.693429
# min       1.000000    0.000000    1.000000    0.420000    0.000000    0.000000    0.000000
# max     891.000000    1.000000    3.000000   80.000000    8.000000    6.000000  512.329200

# Info: column names, non-null counts, data types
df.info()
# <class 'pandas.DataFrame'>
# RangeIndex: 891 entries, 0 to 890
# Data columns (total 12 columns):
#  #   Column       Non-Null Count  Dtype
# ---  ------       --------------  -----
#  0   PassengerId  891 non-null    int64
#  1   Survived     891 non-null    int64
#  2   Pclass       891 non-null    int64
#  3   Name         891 non-null    object
#  4   Sex          891 non-null    object
#  5   Age          714 non-null    float64   ← 177 missing!
#  6   SibSp        891 non-null    int64
#  7   Parch        891 non-null    int64
#  8   Ticket       891 non-null    object
#  9   Fare         891 non-null    float64
# 10   Cabin        204 non-null    object    ← 687 missing!
# 11   Embarked     889 non-null    object    ← 2 missing
```

## 28.4 Selecting data

```python
# Single column (returns Series)
df["Age"]
df.Age  # same thing (dot notation — doesn't work for column names with spaces)

# Multiple columns (returns DataFrame)
df[["Name", "Age", "Survived"]]

# Rows by index position
df.iloc[0]        # first row (as Series)
df.iloc[0:5]      # first 5 rows (as DataFrame)
df.iloc[0, 3]     # row 0, column 3 (single value)

# Rows by label/condition
df.loc[0]                           # row with index label 0
df.loc[df["Age"] > 50]             # all rows where Age > 50
df.loc[df["Sex"] == "female", "Name"]  # Names of all females

# Boolean filtering (most common)
survived = df[df["Survived"] == 1]
young_females = df[(df["Age"] < 30) & (df["Sex"] == "female")]
first_or_second_class = df[df["Pclass"].isin([1, 2])]
```

## 28.5 Column operations

```python
# Create new column
df["FamilySize"] = df["SibSp"] + df["Parch"] + 1

# Apply function to column
df["AgeGroup"] = df["Age"].apply(lambda x: "Child" if x < 18 else "Adult")

# Vectorized operations (faster than apply)
df["FarePerPerson"] = df["Fare"] / df["FamilySize"]

# Replace values
df["Sex"] = df["Sex"].map({"male": 0, "female": 1})

# Rename columns
df = df.rename(columns={"Pclass": "TicketClass", "SibSp": "Siblings"})

# Drop columns
df = df.drop(columns=["Ticket", "PassengerId"])
```

---

## PART 2: Handling Missing Values

## 28.6 Detect missing values

```python
# Count missing per column
df.isnull().sum()
# PassengerId      0
# Survived         0
# Pclass           0
# Name             0
# Sex              0
# Age            177   ← 19.9% missing
# SibSp            0
# Parch            0
# Ticket           0
# Fare             0
# Cabin          687   ← 77.1% missing
# Embarked         2   ← 0.2% missing

# Percentage missing
(df.isnull().sum() / len(df) * 100).round(1)

# Visualize missing pattern
df.isnull().sum().plot(kind="bar")
```

## 28.7 Strategies for missing values

| Strategy | When to use | Example |
|----------|-------------|---------|
| **Drop rows** | Few missing, random pattern | Embarked (only 2 missing) |
| **Drop column** | >50% missing, low predictive value | Cabin (77% missing) |
| **Fill with mean/median** | Numeric, roughly normal distribution | Age (use median — robust to outliers) |
| **Fill with mode** | Categorical | Embarked (most common port) |
| **Fill with group statistic** | Missing correlates with another variable | Age by (Pclass, Sex) |
| **Flag as missing** | Missingness itself is informative | Create "HasCabin" column before dropping Cabin |

## 28.8 Fill missing values

```python
# Strategy 1: Drop rows (Embarked — only 2 missing)
df = df.dropna(subset=["Embarked"])

# Strategy 2: Drop column (Cabin — too many missing)
# But first, extract useful info!
df["HasCabin"] = df["Cabin"].notna().astype(int)  # 1 if has cabin, 0 if not
df["CabinDeck"] = df["Cabin"].str[0]              # extract first letter (deck)
df = df.drop(columns=["Cabin"])

# Strategy 3: Fill with median (Age)
df["Age"].fillna(df["Age"].median(), inplace=True)

# Strategy 4: Fill with group median (smarter — Age varies by class/sex)
df["Age"] = df.groupby(["Pclass", "Sex"])["Age"].transform(
    lambda x: x.fillna(x.median())
)
# This fills each person's missing age with the median age of
# people with the same class and sex. Much more accurate!

# Verify no more missing
assert df.isnull().sum().sum() == 0
```

---

## PART 3: Data Cleaning

## 28.9 Type conversion

```python
# Check current types
df.dtypes

# Convert to category (saves memory, enables categorical operations)
df["Pclass"] = df["Pclass"].astype("category")
df["Sex"] = df["Sex"].astype("category")
df["Embarked"] = df["Embarked"].astype("category")

# Convert to numeric (handle errors)
df["Fare"] = pd.to_numeric(df["Fare"], errors="coerce")  # invalid → NaN

# Convert to datetime (if you have date columns)
# df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
```

## 28.10 String operations

```python
# Extract title from Name: "Braund, Mr. Owen Harris" → "Mr"
df["Title"] = df["Name"].str.extract(r",\s*(\w+)\.")

# Check unique titles
df["Title"].value_counts()
# Mr          517
# Miss        182
# Mrs         125
# Master       40
# Dr            7
# Rev           6
# ...

# Consolidate rare titles
title_map = {
    "Mr": "Mr", "Miss": "Miss", "Mrs": "Mrs", "Master": "Master",
    "Dr": "Rare", "Rev": "Rare", "Col": "Rare", "Major": "Rare",
    "Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs",
    "Sir": "Rare", "Lady": "Rare", "Capt": "Rare",
    "Countess": "Rare", "Jonkheer": "Rare", "Don": "Rare", "Dona": "Rare"
}
df["Title"] = df["Title"].map(title_map).fillna("Rare")

# String cleaning
df["Name"] = df["Name"].str.strip()           # remove whitespace
df["Name"] = df["Name"].str.lower()           # lowercase
df["Ticket"] = df["Ticket"].str.replace(r"[^0-9]", "", regex=True)  # keep only digits
```

## 28.11 Outlier detection and handling

```python
# Detect outliers with IQR (Interquartile Range)
Q1 = df["Fare"].quantile(0.25)
Q3 = df["Fare"].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df["Fare"] < lower_bound) | (df["Fare"] > upper_bound)]
print(f"Found {len(outliers)} fare outliers")

# Option 1: Cap outliers (winsorize)
df["Fare"] = df["Fare"].clip(lower=lower_bound, upper=upper_bound)

# Option 2: Log transform (reduces skewness)
df["LogFare"] = np.log1p(df["Fare"])  # log(1 + x) handles zeros

# Option 3: Remove (be careful — only if clearly erroneous)
df = df[df["Fare"] <= upper_bound]
```

## 28.12 Handling duplicates

```python
# Check for duplicates
df.duplicated().sum()

# Find duplicate rows
df[df.duplicated(keep=False)]  # shows ALL duplicates (both copies)

# Remove duplicates
df = df.drop_duplicates()

# Remove duplicates by specific columns
df = df.drop_duplicates(subset=["Name", "Age", "Ticket"], keep="first")
```

---

## PART 4: Feature Engineering

## 28.13 Creating meaningful features

```python
# Family features
df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

# Age binning
df["AgeBin"] = pd.cut(df["Age"], bins=[0, 12, 18, 35, 60, 80],
                       labels=["Child", "Teen", "Young Adult", "Adult", "Senior"])

# Fare binning (quantile-based — equal number of passengers in each bin)
df["FareBin"] = pd.qcut(df["Fare"], q=4, labels=["Low", "Medium", "High", "Very High"])

# Title-based features (from Part 3)
# Already have: df["Title"]

# Deck from cabin (already extracted)
# df["CabinDeck"] — A, B, C, D, E, F, G, or NaN

# Ticket frequency (shared tickets = travelling together)
ticket_counts = df["Ticket"].value_counts()
df["TicketFreq"] = df["Ticket"].map(ticket_counts)
```

## 28.14 Encoding categorical variables

```python
# One-Hot Encoding (creates binary columns)
df = pd.get_dummies(df, columns=["Embarked", "Title"], drop_first=True)
# Embarked_Q, Embarked_S (dropped C as reference)
# Title_Miss, Title_Mr, Title_Mrs, Title_Rare (dropped Master as reference)

# Label Encoding (for ordinal categories)
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df["Sex"] = le.fit_transform(df["Sex"])  # female=0, male=1

# Or manual mapping (more explicit)
df["Sex"] = df["Sex"].map({"female": 0, "male": 1})
```

## 28.15 Grouping and aggregation

```python
# Survival rate by class
df.groupby("Pclass")["Survived"].mean()
# Pclass
# 1    0.629630
# 2    0.472826
# 3    0.242363

# Survival rate by class AND sex
df.groupby(["Pclass", "Sex"])["Survived"].mean()

# Multiple aggregations
df.groupby("Pclass").agg(
    avg_age=("Age", "mean"),
    avg_fare=("Fare", "mean"),
    survival_rate=("Survived", "mean"),
    count=("Survived", "count"),
)

# Pivot table (like Excel pivot tables)
pd.pivot_table(df, values="Survived", index="Pclass", columns="Sex", aggfunc="mean")
# Sex        female      male
# Pclass
# 1        0.968085  0.368852
# 2        0.921053  0.157407
# 3        0.500000  0.135447
```

---

## PART 5: The Complete Titanic Pipeline

## 28.16 Full cleaning pipeline

```python
import pandas as pd
import numpy as np

def clean_titanic(filepath: str) -> pd.DataFrame:
    """Complete Titanic data cleaning pipeline."""

    # 1. Load
    df = pd.read_csv(filepath)
    print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # 2. Extract features before dropping columns
    # Title from Name
    df["Title"] = df["Name"].str.extract(r",\s*(\w+)\.")
    title_map = {
        "Mr": "Mr", "Miss": "Miss", "Mrs": "Mrs", "Master": "Master",
        "Dr": "Rare", "Rev": "Rare", "Col": "Rare", "Major": "Rare",
        "Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs", "Sir": "Rare",
        "Lady": "Rare", "Capt": "Rare", "Countess": "Rare",
        "Jonkheer": "Rare", "Don": "Rare", "Dona": "Rare",
    }
    df["Title"] = df["Title"].map(title_map).fillna("Rare")

    # Cabin → HasCabin + Deck
    df["HasCabin"] = df["Cabin"].notna().astype(int)
    df["Deck"] = df["Cabin"].str[0].fillna("Unknown")

    # Family
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

    # Ticket frequency
    ticket_counts = df["Ticket"].value_counts()
    df["TicketFreq"] = df["Ticket"].map(ticket_counts)

    # 3. Handle missing values
    # Age: fill with median by (Pclass, Title) — Title correlates strongly with age
    df["Age"] = df.groupby(["Pclass", "Title"])["Age"].transform(
        lambda x: x.fillna(x.median())
    )
    # If still NaN (rare group has no data), use global median
    df["Age"] = df["Age"].fillna(df["Age"].median())

    # Embarked: fill with mode
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Fare: fill with median by Pclass (one test row has missing fare)
    df["Fare"] = df.groupby("Pclass")["Fare"].transform(
        lambda x: x.fillna(x.median())
    )

    # 4. Feature engineering
    # Age bins
    df["AgeBin"] = pd.cut(df["Age"], bins=[0, 12, 18, 35, 60, 100],
                           labels=["Child", "Teen", "YoungAdult", "Adult", "Senior"])

    # Fare: log transform (reduce skewness)
    df["LogFare"] = np.log1p(df["Fare"])

    # 5. Encode categoricals
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    df = pd.get_dummies(df, columns=["Embarked", "Title", "AgeBin", "Deck"], drop_first=True)

    # 6. Drop unnecessary columns
    df = df.drop(columns=["Name", "Ticket", "Cabin", "PassengerId"])

    # 7. Verify clean
    assert df.isnull().sum().sum() == 0, f"Still has {df.isnull().sum().sum()} missing values!"
    print(f"Clean: {df.shape[0]} rows, {df.shape[1]} columns, 0 missing values")

    return df


# Run the pipeline
train_clean = clean_titanic("train.csv")
test_clean = clean_titanic("test.csv")

# Save for ML
train_clean.to_csv("train_clean.csv", index=False)
test_clean.to_csv("test_clean.csv", index=False)

print("\n=== Final columns ===")
print(train_clean.columns.tolist())
print(f"\n=== Survival rate: {train_clean['Survived'].mean():.1%} ===")
```

## 28.17 Quick ML model (verify cleaning worked)

```python
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier

# Prepare features and target
X = train_clean.drop(columns=["Survived"])
y = train_clean["Survived"]

# Train/test split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Train
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
print(f"Training accuracy: {model.score(X_train, y_train):.3f}")
print(f"Validation accuracy: {model.score(X_val, y_val):.3f}")

# Cross-validation (more robust)
scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"CV accuracy: {scores.mean():.3f} ± {scores.std():.3f}")
# Typical result: 0.82 ± 0.03 (good baseline!)

# Feature importance
importance = pd.Series(model.feature_importances_, index=X.columns)
print("\nTop 10 features:")
print(importance.sort_values(ascending=False).head(10))
```

---

## 28.18 Pandas cheat sheet

### Reading/writing
```python
pd.read_csv("file.csv")
pd.read_excel("file.xlsx")
pd.read_json("file.json")
df.to_csv("out.csv", index=False)
df.to_parquet("out.parquet")  # faster + smaller than CSV
```

### Inspection
```python
df.shape                # (rows, cols)
df.head(n)              # first n rows
df.info()               # types + non-null counts
df.describe()           # statistics
df.value_counts("col")  # frequency table
df.nunique()            # unique values per column
```

### Selection
```python
df["col"]               # single column
df[["a", "b"]]          # multiple columns
df.loc[condition]       # filter rows
df.iloc[0:5]            # slice by position
df.query("Age > 30")    # SQL-like filtering
```

### Missing values
```python
df.isnull().sum()       # count per column
df.dropna()             # drop rows with any NaN
df.fillna(value)        # fill with value
df.interpolate()        # interpolate (for time series)
```

### Transformation
```python
df["col"].apply(fn)     # apply function element-wise
df.assign(new=expr)     # add column (returns new df)
df.rename(columns={})   # rename columns
df.drop(columns=[])     # remove columns
df.sort_values("col")   # sort
df.reset_index()        # reset to 0,1,2,...
```

### Aggregation
```python
df.groupby("col").mean()
df.groupby("col").agg({"a": "sum", "b": "mean"})
df.pivot_table(values="y", index="a", columns="b", aggfunc="mean")
pd.crosstab(df["a"], df["b"])
```

### Merging
```python
pd.merge(df1, df2, on="key")                    # inner join
pd.merge(df1, df2, on="key", how="left")        # left join
pd.concat([df1, df2])                           # stack vertically
pd.concat([df1, df2], axis=1)                   # stack horizontally
```

---

## Summary

✅ Pandas fundamentals: Series, DataFrame, indexing, filtering
✅ Data inspection: shape, dtypes, describe, info, value_counts
✅ Missing values: detect, fill (median, mode, group-based), drop
✅ String operations: extract (regex), map, replace, strip
✅ Outlier handling: IQR method, clipping, log transforms
✅ Feature engineering: binning, family size, title extraction, one-hot encoding
✅ Grouping and aggregation: groupby, agg, pivot_table
✅ Complete Titanic pipeline: raw CSV → clean, ML-ready DataFrame
✅ Verified with RandomForest: ~82% accuracy confirms good cleaning

## Key takeaway

**Data cleaning is 80% of data science.** The Titanic dataset is small (891 rows) but teaches every cleaning pattern you'll encounter in real datasets: missing values, mixed types, string parsing, outliers, categorical encoding, and feature engineering. Master these patterns here — they scale to millions of rows unchanged.

---

→ [Back to Chapter 27: Kafka Messaging Patterns](./27-KAFKA-MESSAGING-PATTERNS.md)
