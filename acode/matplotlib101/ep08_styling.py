"""
Matplotlib 101 — Episode 08: "Make It Look Professional"
Karen: "This looks like a homework assignment. Make it board-ready."

Run: python ep08_styling.py
"""
import matplotlib.pyplot as plt
import numpy as np

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
sales = [12000, 15000, 13000, 18000, 22000, 19000]

# ══════════════════════════════════════════════════
# ACT 1: Built-in Styles
# ══════════════════════════════════════════════════
# See all: print(plt.style.available)

styles = ["default", "seaborn-v0_8", "ggplot", "dark_background", "fivethirtyeight"]

fig, axes = plt.subplots(1, len(styles), figsize=(18, 3))

for ax, style_name in zip(axes, styles):
    with plt.style.context(style_name):
        ax.plot(months, sales, marker="o")
        ax.set_title(style_name, fontsize=9)
        ax.tick_params(labelsize=7)

fig.suptitle("Built-in Styles Comparison", fontweight="bold")
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 2: Dark Theme (Captain Deadline's favorite)
# ══════════════════════════════════════════════════

with plt.style.context("dark_background"):
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(months, sales, color="#4ec9b0", linewidth=2.5, marker="o",
            markerfacecolor="white", markeredgecolor="#4ec9b0", markersize=8)
    ax.fill_between(months, sales, alpha=0.1, color="#4ec9b0")

    ax.set_title("Monthly Sales — Dark Theme", fontweight="bold", fontsize=14)
    ax.set_ylabel("Revenue ($)", fontsize=11)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.grid(True, alpha=0.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Custom rcParams (full control)
# ══════════════════════════════════════════════════
# Karen: "Use the company colors. Exactly."

custom_params = {
    "figure.facecolor": "#1e1e1e",
    "axes.facecolor": "#1e1e1e",
    "axes.edgecolor": "#3c3c3c",
    "axes.labelcolor": "#cccccc",
    "text.color": "#cccccc",
    "xtick.color": "#888888",
    "ytick.color": "#888888",
    "grid.color": "#333333",
    "grid.alpha": 0.3,
    "font.family": "monospace",
    "font.size": 11,
}

with plt.rc_context(custom_params):
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(months, sales, color="#007acc", linewidth=2.5, marker="o",
            markerfacecolor="#007acc", markeredgecolor="white", markersize=7)
    ax.fill_between(months, sales, alpha=0.08, color="#007acc")

    ax.set_title("ShopZilla Monthly Sales", fontweight="bold", fontsize=13,
                 color="white")
    ax.set_ylabel("Revenue ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.grid(True, axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • plt.style.use("dark_background") — built-in themes
# • plt.style.context("style") — temporary style (with block)
# • plt.rc_context({...}) — custom rcParams
# • Key params: figure.facecolor, axes.facecolor, text.color
# • ax.spines["top"].set_visible(False) — remove borders
# • font.family, font.size — typography
