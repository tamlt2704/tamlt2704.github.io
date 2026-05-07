# Chapter 1: The CSV is a Mess

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Why is Tuesday Weird? →](chapter-02-eda.md)

---

## The Task

It's Monday morning. Priya drops a Slack message:

> "Dustin left a CSV export in the shared drive. 18 months of daily sales data across 12 restaurants. Load it, tell me what we're working with. I need a summary by end of day."

You open the file. It's 8,000 rows. Some columns have headers like `rev.` and `temp (C)`. There are blank cells, a column that's entirely `#N/A`, and one row where the revenue is negative forty thousand dollars.

Welcome to real data.

---

## Generate the Dataset

First, let's create the messy dataset we'll use throughout the series. This simulates what Dustin's export actually looks like — warts and all.

```python
# generate_data.py
"""Generate the GreenLeaf restaurant dataset (intentionally messy)."""
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

RESTAURANTS = [f"greenleaf_{i:03d}" for i in range(1, 13)]
START_DATE = "2023-01-01"
END_DATE = "2024-06-30"

dates = pd.date_range(START_DATE, END_DATE, freq="D")
rows = []

for restaurant in RESTAURANTS:
    base_revenue = np.random.uniform(2000, 6000)
    base_covers = int(base_revenue / 25)

    for date in dates:
        dow = date.day_name()
        month = date.month

        # Seasonal effect
        seasonal = 1.0 + 0.15 * np.sin(2 * np.pi * (month - 6) / 12)

        # Day-of-week effect (weekends busier)
        dow_mult = {"Monday": 0.7, "Tuesday": 0.75, "Wednesday": 0.85,
                    "Thursday": 0.95, "Friday": 1.3, "Saturday": 1.4,
                    "Sunday": 1.1}[dow]

        # Temperature (correlated with season)
        temp = 10 + 15 * np.sin(2 * np.pi * (month - 3) / 12) + np.random.normal(0, 3)

        # Holiday (random ~3% of days)
        is_holiday = np.random.random() < 0.03

        staff = np.random.randint(4, 12)
        menu_items = np.random.randint(25, 45)
        marketing = max(0, np.random.normal(100, 50))

        # Revenue depends on features
        noise = np.random.normal(1.0, 0.15)
        revenue = (base_revenue * seasonal * dow_mult * noise
                   + marketing * 2.5
                   + (500 if is_holiday else 0)
                   + temp * 15)

        covers = int(revenue / np.random.uniform(20, 30))
        waste = max(0, covers * np.random.uniform(0.04, 0.12))

        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "restaurant_id": restaurant,
            "day_of_week": dow,
            "temperature_c": round(temp, 1),
            "is_holiday": is_holiday,
            "menu_items_available": menu_items,
            "staff_count": staff,
            "marketing_spend": round(marketing, 2),
            "covers": covers,
            "revenue": round(revenue, 2),
            "food_waste_kg": round(waste, 1),
        })

df = pd.DataFrame(rows)

# ── Now make it messy (like real data) ──────────────────

# 1. Random missing values (~5%)
for col in ["temperature_c", "staff_count", "marketing_spend", "food_waste_kg"]:
    mask = np.random.random(len(df)) < 0.05
    df.loc[mask, col] = np.nan

# 2. Some revenues as strings with dollar signs
bad_rows = np.random.choice(df.index, size=50, replace=False)
df.loc[bad_rows, "revenue"] = df.loc[bad_rows, "revenue"].apply(lambda x: f"${x}")

# 3. One catastrophic typo: negative revenue
df.loc[42, "revenue"] = -40000.0

# 4. Tuesday data entry error: one restaurant has doubled covers on Tuesdays
tuesday_mask = (df["day_of_week"] == "Tuesday") & (df["restaurant_id"] == "greenleaf_007")
df.loc[tuesday_mask, "covers"] = df.loc[tuesday_mask, "covers"] * 2

# 5. A column that's entirely useless
df["legacy_code"] = "#N/A"

# 6. Inconsistent column names
df = df.rename(columns={
    "temperature_c": "temp (C)",
    "revenue": "rev.",
    "food_waste_kg": "waste_kg",
})

# Save
Path("data").mkdir(exist_ok=True)
df.to_csv("data/restaurant_sales_raw.csv", index=False)
print(f"Generated {len(df)} rows → data/restaurant_sales_raw.csv")
```

Run it:

```bash
python generate_data.py
```

You now have a CSV that looks exactly like what Dustin left behind.

---

## Load and Inspect

```python
# chapter_01.py
"""Chapter 1: Loading and cleaning the raw CSV."""
import pandas as pd
import numpy as np

# ── Load ─────────────────────────────────────────
df = pd.read_csv("data/restaurant_sales_raw.csv")

print(df.shape)          # (6,588 rows, 12 columns)
print(df.columns.tolist())
```

Output:

```
(6588, 12)
['date', 'restaurant_id', 'day_of_week', 'temp (C)', 'is_holiday',
 'menu_items_available', 'staff_count', 'marketing_spend', 'covers',
 'rev.', 'waste_kg', 'legacy_code']
```

Already problems:
- `temp (C)` has spaces and parentheses — annoying to type
- `rev.` has a period — will break attribute access
- `legacy_code` is entirely `#N/A`

### First Look

```python
print(df.info())
```

```
 #   Column                Non-Null Count  Dtype
---  ------                --------------  -----
 0   date                  6588 non-null   object    ← not datetime!
 1   restaurant_id         6588 non-null   object
 2   day_of_week           6588 non-null   object
 3   temp (C)              6260 non-null   float64   ← missing values
 4   is_holiday            6588 non-null   bool
 5   staff_count           6260 non-null   float64   ← should be int
 6   marketing_spend       6260 non-null   float64   ← missing values
 7   covers                6588 non-null   int64
 8   rev.                  6588 non-null   object    ← should be float!
 9   waste_kg              6260 non-null   float64   ← missing values
 10  legacy_code           6588 non-null   object    ← useless
```

The `rev.` column is `object` (string) instead of `float64`. That means some values aren't numbers. Let's find them.

---

## Clean It Up

### Step 1: Fix Column Names

```python
# Rename to clean, snake_case names
df = df.rename(columns={
    "temp (C)": "temperature_c",
    "rev.": "revenue",
    "waste_kg": "food_waste_kg",
})
```

Rule: column names should be valid Python identifiers. No spaces, no dots, no parentheses.

### Step 2: Drop Useless Columns

```python
# legacy_code is entirely #N/A — it tells us nothing
df = df.drop(columns=["legacy_code"])
```

### Step 3: Fix the Revenue Column

```python
# Some values have dollar signs, one is -40000
df["revenue"] = pd.to_numeric(df["revenue"].str.replace("$", "", regex=False), errors="coerce")

# Check for absurd values
print(df["revenue"].describe())
```

```
count    6538.000000
mean     4127.340000
std      1456.780000
min    -40000.000000   ← the typo
25%      3102.450000
50%      4015.230000
75%      5034.670000
max      9876.540000
```

That `-40000` is clearly a typo. For now, we'll mark it as missing:

```python
df.loc[df["revenue"] < 0, "revenue"] = np.nan
```

### Step 4: Fix Data Types

```python
# Date should be datetime
df["date"] = pd.to_datetime(df["date"])

# staff_count should be integer (but has NaN — use nullable int)
df["staff_count"] = df["staff_count"].astype("Int64")
```

### Step 5: Check Missing Values

```python
print(df.isnull().sum())
```

```
date                     0
restaurant_id            0
day_of_week              0
temperature_c          328
is_holiday               0
menu_items_available     0
staff_count            328
marketing_spend        328
covers                   0
revenue                 51   ← 50 from dollar signs + 1 typo
food_waste_kg          328
```

About 5% missing in several columns. We'll deal with imputation strategies in Chapter 5. For now, we know what we're working with.

---

## Save the Clean Version

```python
# Save cleaned data for future chapters
df.to_csv("data/restaurant_sales_clean.csv", index=False)
print(f"Cleaned: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Missing values: {df.isnull().sum().sum()} total")
```

---

## The Summary for Priya

You send Priya a message:

> **Dataset summary:**
> - 6,588 rows × 10 useful columns (dropped 1 junk column)
> - 12 restaurants, 18 months of daily data (Jan 2023 – Jun 2024)
> - ~5% missing values in temperature, staff, marketing, waste
> - Revenue column had formatting issues (dollar signs) + 1 obvious typo (−$40k)
> - One restaurant (greenleaf_007) has suspicious Tuesday numbers — investigating tomorrow
>
> Cleaned version saved. Ready for exploration.

Priya replies: "Good. Now tell me why Tuesday is weird."

---

## What You Learned

- `pd.read_csv()` loads data but doesn't fix it — always check `df.info()` and `df.describe()`
- Column names with spaces/dots are a pain — rename immediately
- `pd.to_numeric(errors="coerce")` converts bad strings to `NaN` instead of crashing
- `astype("Int64")` (capital I) is pandas' nullable integer — handles `NaN` in int columns
- Always check for absurd values before trusting statistics
- Real data is never clean. Budget time for this.

---

[Next: Chapter 2 — "Why is Tuesday Weird?" →](chapter-02-eda.md)
