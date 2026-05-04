"""
Matplotlib 101 — Episode 04: "What Percentage Is Each City?"
Karen: "The board thinks in percentages, not dollars."

Run: python ep04_pie_chart.py
"""
import matplotlib.pyplot as plt

cities = ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
sales = [45000, 38000, 29000, 22000, 18000]
colors = ["#007acc", "#ff5f57", "#28c840", "#e6a700", "#c678dd"]

# ══════════════════════════════════════════════════
# ACT 1: Basic Pie Chart
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(6, 6))

ax.pie(sales, labels=cities, colors=colors,
       autopct="%1.1f%%",                # Show percentage
       startangle=90)                     # Start from top

ax.set_title("Sales Distribution by City", fontweight="bold")
plt.show()

# Karen: "Highlight NYC — it's the biggest."

# ══════════════════════════════════════════════════
# ACT 2: Exploded Pie
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(6, 6))

explode = [0.08, 0, 0, 0, 0]            # Pull NYC out slightly

ax.pie(sales, labels=cities, colors=colors,
       autopct="%1.1f%%",
       startangle=90,
       explode=explode,
       shadow=True,
       textprops={"fontsize": 11})

ax.set_title("Sales Distribution (NYC highlighted)", fontweight="bold")
plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Donut Chart (modern look)
# ══════════════════════════════════════════════════
# Karen: "Pie charts are so 2010. Make it a donut."

fig, ax = plt.subplots(figsize=(6, 6))

wedges, texts, autotexts = ax.pie(
    sales, labels=cities, colors=colors,
    autopct="%1.1f%%", startangle=90,
    wedgeprops={"width": 0.4, "edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 10},
)

# Bold the percentages
for t in autotexts:
    t.set_fontweight("bold")

# Center text
ax.text(0, 0, f"Total\n${sum(sales):,}", ha="center", va="center",
        fontsize=14, fontweight="bold")

ax.set_title("Sales Distribution — Donut", fontweight="bold")
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • ax.pie(values, labels=..., autopct="%1.1f%%")
# • explode=[0.1, 0, 0, ...] — pull a slice out
# • wedgeprops={"width": 0.4} — donut chart
# • Center text with ax.text(0, 0, ...)
