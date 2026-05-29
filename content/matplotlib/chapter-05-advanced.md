---
title: "Chapter 5: Real-World Dashboards"
description: "Building complete data dashboards with Matplotlib"
---

# Chapter 5: Real-World Dashboards

## Sales Dashboard

```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

np.random.seed(42)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
revenue = np.random.randint(50, 150, 12)
expenses = np.random.randint(30, 100, 12)
categories = ["Electronics", "Clothing", "Food", "Services"]
cat_sales = [45, 25, 18, 12]

fig = plt.figure(figsize=(14, 10))
gs = GridSpec(2, 3, figure=fig)

# Revenue vs Expenses
ax1 = fig.add_subplot(gs[0, :2])
ax1.bar(months, revenue, label="Revenue", alpha=0.8)
ax1.bar(months, expenses, label="Expenses", alpha=0.6)
ax1.legend()
ax1.set_title("Monthly Revenue vs Expenses ($k)")
ax1.set_ylabel("Amount ($k)")

# Category Pie
ax2 = fig.add_subplot(gs[0, 2])
ax2.pie(cat_sales, labels=categories, autopct="%1.0f%%", startangle=90)
ax2.set_title("Sales by Category")

# Profit Trend
ax3 = fig.add_subplot(gs[1, :2])
profit = np.array(revenue) - np.array(expenses)
colors = ["green" if p > 0 else "red" for p in profit]
ax3.bar(months, profit, color=colors)
ax3.axhline(0, color="black", linewidth=0.5)
ax3.set_title("Monthly Profit")
ax3.set_ylabel("Profit ($k)")

# KPI Summary
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis("off")
kpis = f"Total Revenue: ${revenue.sum()}k\nTotal Expenses: ${expenses.sum()}k\nNet Profit: ${profit.sum()}k\nBest Month: {months[np.argmax(profit)]}"
ax4.text(0.1, 0.5, kpis, fontsize=14, verticalalignment="center",
         fontfamily="monospace", transform=ax4.transAxes)
ax4.set_title("KPIs")

plt.suptitle("Annual Sales Dashboard", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.show()
```

## Stock Price Dashboard

```python
days = 252
dates = np.arange(days)
price = 100 + np.random.randn(days).cumsum() * 2
volume = np.random.randint(1_000_000, 10_000_000, days)
ma_20 = np.convolve(price, np.ones(20)/20, mode="valid")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8),
                                gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

ax1.plot(dates, price, label="Price", linewidth=1)
ax1.plot(dates[19:], ma_20, label="20-day MA", linewidth=2, color="orange")
ax1.fill_between(dates, price.min(), price, alpha=0.1)
ax1.legend()
ax1.set_title("Stock Price with Moving Average")
ax1.set_ylabel("Price ($)")

ax2.bar(dates, volume, width=1, color="steelblue", alpha=0.7)
ax2.set_title("Trading Volume")
ax2.set_xlabel("Trading Day")
ax2.set_ylabel("Volume")

plt.tight_layout()
plt.show()
```

## Exercises

1. Build a weather dashboard showing temperature, humidity, and wind speed for a week.
2. Create a portfolio tracker with asset allocation pie chart, performance line chart, and risk metrics.
3. Design a multi-page PDF report with `PdfPages` containing 4 different chart pages.

---

[← prev](./chapter-04-3d-animations.md) | [Overview](./chapter-00-overview.md)
