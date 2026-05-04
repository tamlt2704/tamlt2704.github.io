"""
Matplotlib 101 — Episode 09: "Add Error Bars and Annotations"
Karen: "The board wants confidence intervals. And highlight the anomaly in March."

Run: python ep09_annotations.py
"""
import matplotlib.pyplot as plt
import numpy as np

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
sales = [12000, 15000, 9000, 18000, 22000, 19000]
errors = [1500, 1200, 3000, 1800, 2000, 1600]

# ══════════════════════════════════════════════════
# ACT 1: Error Bars
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

ax.errorbar(months, sales, yerr=errors,
            fmt="o-",                     # Line with dots
            color="#007acc",
            ecolor="#007acc",             # Error bar color
            elinewidth=1.5,
            capsize=4,                    # Cap width on error bars
            capthick=1.5,
            linewidth=2,
            markersize=6)

ax.set_title("Monthly Sales with Confidence Intervals", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 2: Annotations
# ══════════════════════════════════════════════════
# Karen: "What happened in March? Highlight it."

fig, ax = plt.subplots(figsize=(8, 4))

ax.plot(months, sales, color="#007acc", linewidth=2, marker="o", markersize=6)

# Annotate the anomaly
ax.annotate(
    "Supply chain\ndisruption",
    xy=("Mar", 9000),                    # Point to annotate
    xytext=("Apr", 6000),               # Text position
    fontsize=10, color="#ff5f57",
    arrowprops=dict(arrowstyle="->", color="#ff5f57", lw=1.5),
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#2a0a0a", edgecolor="#ff5f57"),
)

# Horizontal reference line (target)
ax.axhline(y=15000, color="#28c840", linestyle="--", linewidth=1, alpha=0.7,
           label="Target: $15,000")

# Shaded region (acceptable range)
ax.fill_between(months, 13000, 17000, alpha=0.08, color="#28c840",
                label="Target range")

ax.legend(loc="upper left")
ax.set_title("Monthly Sales — Anomaly Highlighted", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • ax.errorbar(x, y, yerr=...) — error bars
# • capsize= — width of error bar caps
# • ax.annotate(text, xy=, xytext=, arrowprops=) — callout
# • ax.axhline(y=) — horizontal reference line
# • ax.fill_between(x, y1, y2) — shaded region
# • bbox=dict(...) — text box background
