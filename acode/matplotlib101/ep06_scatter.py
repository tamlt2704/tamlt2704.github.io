"""
Matplotlib 101 — Episode 06: "Is There a Correlation?"
Karen: "Do higher-priced products sell more or less?"

Run: python ep06_scatter.py
"""
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
n = 100
prices = np.random.uniform(10, 200, n)
units_sold = 500 - 2 * prices + np.random.normal(0, 50, n)
units_sold = np.clip(units_sold, 0, None)
revenue = prices * units_sold

# ══════════════════════════════════════════════════
# ACT 1: Basic Scatter
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 5))

ax.scatter(prices, units_sold, color="#007acc", alpha=0.6, edgecolors="white", linewidth=0.5)

ax.set_title("Price vs Units Sold", fontweight="bold")
ax.set_xlabel("Price ($)")
ax.set_ylabel("Units Sold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# Karen: "Higher price = fewer sales. Makes sense. But which ones make the most money?"

# ══════════════════════════════════════════════════
# ACT 2: Size = Revenue, Color = Category
# ══════════════════════════════════════════════════

categories = np.random.choice(["Electronics", "Home", "Clothing"], n)
cat_colors = {"Electronics": "#007acc", "Home": "#28c840", "Clothing": "#ff5f57"}
colors = [cat_colors[c] for c in categories]

fig, ax = plt.subplots(figsize=(8, 5))

scatter = ax.scatter(
    prices, units_sold,
    s=revenue / 100,                     # Size = revenue (scaled down)
    c=colors,                            # Color = category
    alpha=0.6,
    edgecolors="white",
    linewidth=0.5,
)

ax.set_title("Price vs Units Sold (size = revenue, color = category)", fontweight="bold")
ax.set_xlabel("Price ($)")
ax.set_ylabel("Units Sold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Manual legend for categories
for cat, color in cat_colors.items():
    ax.scatter([], [], c=color, s=60, label=cat, edgecolors="white")
ax.legend(title="Category", loc="upper right")

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Colorbar (continuous color scale)
# ══════════════════════════════════════════════════
# Karen: "Color by revenue — I want to see the money."

fig, ax = plt.subplots(figsize=(8, 5))

scatter = ax.scatter(
    prices, units_sold,
    c=revenue,                           # Color = revenue (continuous)
    cmap="YlOrRd",                       # Yellow → Orange → Red
    s=50,
    alpha=0.7,
    edgecolors="white",
    linewidth=0.5,
)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Revenue ($)")

ax.set_title("Price vs Units Sold (color = revenue)", fontweight="bold")
ax.set_xlabel("Price ($)")
ax.set_ylabel("Units Sold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • ax.scatter(x, y) — basic scatter
# • s= for dot size (encode a third variable)
# • c= for color (list of colors or continuous values)
# • cmap="YlOrRd" — color map for continuous data
# • plt.colorbar() — add a color scale legend
# • alpha= for transparency when dots overlap
