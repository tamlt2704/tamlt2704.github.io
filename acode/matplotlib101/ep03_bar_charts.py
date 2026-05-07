"""
Matplotlib 101 — Episode 03: "Make It a Bar Chart"
Karen: "Line charts are for trends. I need to compare categories."

Run: python ep03_bar_charts.py
"""
import matplotlib.pyplot as plt
import numpy as np

cities = ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
sales = [45000, 38000, 29000, 22000, 18000]
colors = ["#007acc", "#ff5f57", "#28c840", "#e6a700", "#c678dd"]

# ══════════════════════════════════════════════════
# ACT 1: Basic Vertical Bar Chart
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

bars = ax.bar(cities, sales, color=colors, width=0.6, edgecolor="white", linewidth=0.5)

ax.set_title("Sales by City — 2026", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Add value labels on top of each bar
for bar, val in zip(bars, sales):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
            f"${val:,}", ha="center", va="bottom", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 2: Horizontal Bar Chart (better for long labels)
# ══════════════════════════════════════════════════
# Karen: "The city names overlap. Flip it."

fig, ax = plt.subplots(figsize=(8, 4))

# Sort by value (largest at top)
sorted_idx = np.argsort(sales)
sorted_cities = [cities[i] for i in sorted_idx]
sorted_sales = [sales[i] for i in sorted_idx]
sorted_colors = [colors[i] for i in sorted_idx]

bars = ax.barh(sorted_cities, sorted_sales, color=sorted_colors, height=0.6)

# Value labels at end of each bar
for bar, val in zip(bars, sorted_sales):
    ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
            f"${val:,}", ha="left", va="center", fontsize=9)

ax.set_title("Sales by City — 2026 (Ranked)", fontweight="bold")
ax.set_xlabel("Revenue ($)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Grouped Bar Chart (compare two things)
# ══════════════════════════════════════════════════
# Karen: "Now show me Q1 vs Q2 for each city."

q1 = [20000, 18000, 14000, 10000, 8000]
q2 = [25000, 20000, 15000, 12000, 10000]

x = np.arange(len(cities))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 4))

bars1 = ax.bar(x - width / 2, q1, width, label="Q1", color="#007acc")
bars2 = ax.bar(x + width / 2, q2, width, label="Q2", color="#28c840")

ax.set_xticks(x)
ax.set_xticklabels(cities)
ax.legend()
ax.set_title("Q1 vs Q2 Sales by City", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 4: Stacked Bar Chart
# ══════════════════════════════════════════════════
# Karen: "Show me the total, but broken down by quarter."

fig, ax = plt.subplots(figsize=(8, 4))

ax.bar(cities, q1, label="Q1", color="#007acc")
ax.bar(cities, q2, bottom=q1, label="Q2", color="#28c840")

ax.legend()
ax.set_title("Total Sales by City (Stacked Q1 + Q2)", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • ax.bar(x, y) — vertical bars
# • ax.barh(y, x) — horizontal bars (better for long labels)
# • Grouped: offset x positions with np.arange + width
# • Stacked: use bottom= parameter
# • ax.text() on each bar for value labels
# • Sort data before plotting for ranked charts
