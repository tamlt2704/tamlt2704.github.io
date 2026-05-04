"""
Matplotlib 101 — Episode 07: "Put Them All on One Page"
Karen: "I need line chart, bar chart, pie chart, and scatter — one slide."

Run: python ep07_subplots.py
"""
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
sales = [12000, 15000, 13000, 18000, 22000, 19000]
cities = ["NYC", "LA", "Chicago", "Houston"]
city_sales = [45000, 38000, 29000, 22000]
colors = ["#007acc", "#ff5f57", "#28c840", "#e6a700"]

# ══════════════════════════════════════════════════
# ACT 1: 2×2 Grid
# ══════════════════════════════════════════════════

fig, axes = plt.subplots(2, 2, figsize=(10, 7))
# axes is a 2×2 array: axes[row][col]

# Top-left: Line chart
ax = axes[0][0]
ax.plot(months, sales, color="#007acc", marker="o", linewidth=2)
ax.set_title("Monthly Trend", fontweight="bold", fontsize=11)
ax.set_ylabel("Revenue ($)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Top-right: Bar chart
ax = axes[0][1]
ax.bar(cities, city_sales, color=colors)
ax.set_title("Sales by City", fontweight="bold", fontsize=11)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Bottom-left: Pie chart
ax = axes[1][0]
ax.pie(city_sales, labels=cities, colors=colors, autopct="%1.0f%%",
       textprops={"fontsize": 9})
ax.set_title("City Distribution", fontweight="bold", fontsize=11)

# Bottom-right: Scatter
ax = axes[1][1]
x = np.random.uniform(10, 100, 50)
y = 200 - 1.5 * x + np.random.normal(0, 20, 50)
ax.scatter(x, y, color="#c678dd", alpha=0.6, edgecolors="white")
ax.set_title("Price vs Volume", fontweight="bold", fontsize=11)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.suptitle("ShopZilla Q2 Dashboard", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 2: Uneven Grid with GridSpec
# ══════════════════════════════════════════════════
# Karen: "Make the line chart bigger — it's the most important."

fig = plt.figure(figsize=(10, 6))
gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)

# Big chart: top row, spans all 3 columns
ax_main = fig.add_subplot(gs[0, :])
ax_main.plot(months, sales, color="#007acc", marker="o", linewidth=2.5)
ax_main.fill_between(months, sales, alpha=0.1, color="#007acc")
ax_main.set_title("Monthly Sales Trend", fontweight="bold")
ax_main.set_ylabel("Revenue ($)")
ax_main.spines["top"].set_visible(False)
ax_main.spines["right"].set_visible(False)

# Bottom row: 3 small charts
ax1 = fig.add_subplot(gs[1, 0])
ax1.bar(cities, city_sales, color=colors)
ax1.set_title("By City", fontsize=10)
ax1.tick_params(axis="x", labelsize=8)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

ax2 = fig.add_subplot(gs[1, 1])
ax2.pie(city_sales, labels=cities, colors=colors, autopct="%1.0f%%",
        textprops={"fontsize": 8})
ax2.set_title("Distribution", fontsize=10)

ax3 = fig.add_subplot(gs[1, 2])
ax3.scatter(x, y, color="#c678dd", alpha=0.6, s=20, edgecolors="white")
ax3.set_title("Price vs Vol", fontsize=10)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)

plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • fig, axes = plt.subplots(rows, cols) — even grid
# • axes[row][col] — access each subplot
# • fig.add_gridspec(rows, cols) — uneven grid
# • fig.add_subplot(gs[row, col_slice]) — span multiple cells
# • fig.suptitle() — title for the whole figure
# • plt.tight_layout() — prevent overlap
