---
title: "Chapter 6: Time Series"
description: "Working with dates, resampling, and rolling windows"
---

# Chapter 6: Time Series

## Date Ranges and Indexing

```python
import pandas as pd
import numpy as np

dates = pd.date_range("2024-01-01", periods=365, freq="D")
ts = pd.Series(np.random.randn(365).cumsum(), index=dates)
print(ts.head())
print(ts["2024-03"])  # select March
```

## Resampling

```python
# Daily to monthly
monthly = ts.resample("M").mean()
print(monthly)

# Daily to weekly sum
weekly = ts.resample("W").sum()
```

## Rolling Windows

```python
df = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=100),
    "price": 100 + np.random.randn(100).cumsum()
})
df = df.set_index("date")

df["ma_7"] = df["price"].rolling(7).mean()
df["ma_30"] = df["price"].rolling(30).mean()
df["std_7"] = df["price"].rolling(7).std()
print(df.tail())
```

## Shifting and Percent Change

```python
df["prev_day"] = df["price"].shift(1)
df["daily_return"] = df["price"].pct_change()
df["7d_return"] = df["price"].pct_change(7)
```

## Exercises

1. Create a year of daily stock prices and plot the 20-day and 50-day moving averages.
2. Resample hourly sensor data to daily min, max, and mean.
3. Compute weekly returns and identify the week with the highest volatility.

---

[← prev](./chapter-05-merge.md) | [next →](./chapter-06-projects.md)
