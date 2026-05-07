# Episode 10: "Show It Over Time"

> Run the code: `python ep10_time_series.py`

Karen: "I have 365 days of data. Show me the trend." Daily data is noisy. The trick is showing both the raw signal and the smoothed trend — and formatting dates so they're actually readable.

---

## The Problem with Daily Data

Plot 365 raw data points and you get a jagged mess. The signal is buried in noise. The solution: show the raw data faintly, then overlay a rolling average.

## Date Formatting with mdates

Matplotlib's `matplotlib.dates` module handles date axes:

```python
import matplotlib.dates as mdates
import pandas as pd

dates = pd.date_range("2026-01-01", periods=365, freq="D")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(dates, daily_sales, color="#007acc", linewidth=0.5, alpha=0.5)

# Format x-axis as month abbreviations
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
```

### Common Date Formats

| Format | Output |
|--------|--------|
| `"%b"` | Jan, Feb, Mar |
| `"%B"` | January, February |
| `"%m/%d"` | 01/15 |
| `"%Y-%m-%d"` | 2026-01-15 |
| `"%b %d"` | Jan 15 |

### Locators (Where Ticks Appear)

| Locator | Ticks Every |
|---------|-------------|
| `mdates.MonthLocator()` | Month |
| `mdates.WeekdayLocator()` | Week |
| `mdates.DayLocator(interval=7)` | 7 days |
| `mdates.YearLocator()` | Year |

## Rolling Average

Smooth the noise with pandas:

```python
df = pd.DataFrame({"date": dates, "sales": daily_sales})
df["rolling_7"] = df["sales"].rolling(7).mean()
df["rolling_30"] = df["sales"].rolling(30).mean()
```

Then layer them:

```python
ax.plot(df["date"], df["sales"], color="#007acc", linewidth=0.4, alpha=0.3,
        label="Daily")
ax.plot(df["date"], df["rolling_7"], color="#e6a700", linewidth=1.5,
        label="7-day avg")
ax.plot(df["date"], df["rolling_30"], color="#ff5f57", linewidth=2,
        label="30-day avg")

ax.legend()
```

The raw data provides context. The 7-day average shows weekly patterns. The 30-day average reveals the true trend.

## Highlighting a Time Period

Shade a date range to call attention to an event:

```python
bf_start = pd.Timestamp("2026-11-23")
bf_end = pd.Timestamp("2026-11-30")

ax.axvspan(bf_start, bf_end, alpha=0.2, color="#28c840", label="Black Friday")
```

`axvspan` shades a vertical band between two x-values. Works with dates just like numbers.

## Annotating Peaks

```python
peak_idx = df["sales"].idxmax()
peak_date = df.loc[peak_idx, "date"]
peak_val = df.loc[peak_idx, "sales"]

ax.annotate(f"Peak: ${peak_val:,.0f}",
            xy=(peak_date, peak_val),
            xytext=(peak_date + pd.Timedelta(days=30), peak_val + 2000),
            arrowprops=dict(arrowstyle="->", color="#28c840"))
```

Use `pd.Timedelta` to offset the text position by days.

## Generating Realistic Time Series Data

For practice, create data with trend + seasonality + noise:

```python
np.random.seed(42)
base = 10000 + np.sin(np.arange(365) / 365 * 2 * np.pi) * 3000  # seasonal
noise = np.random.normal(0, 800, 365)
trend = np.arange(365) * 10                                       # upward
daily_sales = base + noise + trend
```

---

## Exercise

1. Generate 30 days of fake daily data (use `np.random.normal`)
2. Create a pandas DataFrame with a date column
3. Calculate a 7-day rolling average
4. Plot both raw data (thin, transparent) and rolling average (thick, bold)
5. Format the x-axis with `mdates.DateFormatter("%b %d")`
6. Shade a 3-day period (e.g., a sale or event)
7. Annotate the peak day

## Quick Reference

| Function | Purpose |
|----------|---------|
| `mdates.DateFormatter("%b")` | Format dates on axis |
| `mdates.MonthLocator()` | Tick every month |
| `mdates.DayLocator(interval=N)` | Tick every N days |
| `df["col"].rolling(7).mean()` | 7-day rolling average |
| `ax.axvspan(start, end)` | Shade a date range |
| `pd.date_range(start, periods=N)` | Generate date sequence |
| `pd.Timedelta(days=N)` | Offset for annotations |
| `ax.xaxis.set_major_formatter()` | Set date format |
| `ax.xaxis.set_major_locator()` | Set tick frequency |
