"""
Matplotlib 101 — Episode 10: "Show It Over Time"
Karen: "I have 365 days of data. Show me the trend."

Run: python ep10_time_series.py
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

# ══════════════════════════════════════════════════
# Generate fake daily sales data for 2026
# ══════════════════════════════════════════════════
np.random.seed(42)
dates = pd.date_range("2026-01-01", periods=365, freq="D")
base = 10000 + np.sin(np.arange(365) / 365 * 2 * np.pi) * 3000  # seasonal
noise = np.random.normal(0, 800, 365)
trend = np.arange(365) * 10  # slight upward trend
daily_sales = base + noise + trend

# ══════════════════════════════════════════════════
# ACT 1: Raw Daily Data (noisy)
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(dates, daily_sales, color="#007acc", linewidth=0.5, alpha=0.5)

ax.set_title("Daily Sales — 2026 (raw)", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# Karen: "It's too noisy. Smooth it out."

# ══════════════════════════════════════════════════
# ACT 2: Rolling Average
# ══════════════════════════════════════════════════

df = pd.DataFrame({"date": dates, "sales": daily_sales})
df["rolling_7"] = df["sales"].rolling(7).mean()
df["rolling_30"] = df["sales"].rolling(30).mean()

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(df["date"], df["sales"], color="#007acc", linewidth=0.4, alpha=0.3,
        label="Daily")
ax.plot(df["date"], df["rolling_7"], color="#e6a700", linewidth=1.5,
        label="7-day avg")
ax.plot(df["date"], df["rolling_30"], color="#ff5f57", linewidth=2,
        label="30-day avg")

ax.legend()
ax.set_title("Daily Sales with Rolling Averages", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Highlight a Period
# ══════════════════════════════════════════════════
# Karen: "Highlight Black Friday week."

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(df["date"], df["rolling_7"], color="#007acc", linewidth=2)

# Shade Black Friday week
bf_start = pd.Timestamp("2026-11-23")
bf_end = pd.Timestamp("2026-11-30")
ax.axvspan(bf_start, bf_end, alpha=0.2, color="#28c840", label="Black Friday")

# Annotate peak
peak_idx = df["sales"].idxmax()
peak_date = df.loc[peak_idx, "date"]
peak_val = df.loc[peak_idx, "sales"]
ax.annotate(f"Peak: ${peak_val:,.0f}",
            xy=(peak_date, peak_val),
            xytext=(peak_date + pd.Timedelta(days=30), peak_val + 2000),
            fontsize=9, color="#28c840",
            arrowprops=dict(arrowstyle="->", color="#28c840"))

ax.legend()
ax.set_title("2026 Sales — Black Friday Highlighted", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • mdates.DateFormatter("%b") — format x-axis as month names
# • mdates.MonthLocator() — one tick per month
# • pandas .rolling(n).mean() — smoothing
# • ax.axvspan(start, end) — shade a date range
# • Plot raw + rolling on same axes for context
