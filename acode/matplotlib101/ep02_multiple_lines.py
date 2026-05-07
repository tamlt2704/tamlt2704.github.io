"""
Matplotlib 101 — Episode 02: "Compare the Two Products"
Karen: "Show me Widget A vs Widget B sales. On the same chart."

Run: python ep02_multiple_lines.py
"""
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
widget_a = [12000, 15000, 13000, 18000, 22000, 19000]
widget_b = [8000, 9000, 14000, 16000, 15000, 21000]

# ══════════════════════════════════════════════════
# ACT 1: Two Lines, Same Axes
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

ax.plot(months, widget_a, label="Widget A",
        color="#007acc", linewidth=2, marker="o", markersize=6)
ax.plot(months, widget_b, label="Widget B",
        color="#ff5f57", linewidth=2, marker="s", markersize=6)

# Legend — tells you which line is which
ax.legend()

ax.set_title("Widget A vs Widget B — 2026", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", alpha=0.2)

plt.tight_layout()
plt.show()

# Karen: "When did B overtake A?"

# ══════════════════════════════════════════════════
# ACT 2: Highlight the Crossover
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

ax.plot(months, widget_a, label="Widget A",
        color="#007acc", linewidth=2, marker="o")
ax.plot(months, widget_b, label="Widget B",
        color="#ff5f57", linewidth=2, marker="s")

# Fill between: green where A > B, red where B > A
ax.fill_between(months, widget_a, widget_b,
                where=[a > b for a, b in zip(widget_a, widget_b)],
                alpha=0.15, color="#007acc", label="A leads")
ax.fill_between(months, widget_a, widget_b,
                where=[b >= a for a, b in zip(widget_a, widget_b)],
                alpha=0.15, color="#ff5f57", label="B leads")

ax.legend(loc="upper left")
ax.set_title("Widget A vs B — Crossover Point", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", alpha=0.2)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Line Styles & Markers
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

# Different line styles
styles = [
    {"linestyle": "-",  "marker": "o", "label": "Solid + circle"},
    {"linestyle": "--", "marker": "s", "label": "Dashed + square"},
    {"linestyle": "-.", "marker": "^", "label": "Dash-dot + triangle"},
    {"linestyle": ":",  "marker": "D", "label": "Dotted + diamond"},
]

for i, style in enumerate(styles):
    data = [10000 + i * 3000 + j * 1500 for j in range(6)]
    ax.plot(months, data, linewidth=2, markersize=6, **style)

ax.legend()
ax.set_title("Line Styles & Markers Reference", fontweight="bold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • Multiple ax.plot() calls = multiple lines on same chart
# • label="..." + ax.legend() = legend
# • fill_between(x, y1, y2, where=...) = shaded comparison
# • linestyle: "-", "--", "-.", ":"
# • marker: "o", "s", "^", "D", "v", "*", "+"
# • legend(loc="upper left") = position the legend
