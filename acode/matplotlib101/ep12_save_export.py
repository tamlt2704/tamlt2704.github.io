"""
Matplotlib 101 — Episode 12: "Save It for the Presentation"
Karen: "Email me the chart. As a PNG. And a PDF. High resolution."

Run: python ep12_save_export.py
"""
import matplotlib.pyplot as plt
import numpy as np

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
sales = [12000, 15000, 13000, 18000, 22000, 19000]

# ══════════════════════════════════════════════════
# ACT 1: Basic savefig
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(months, sales, color="#007acc", linewidth=2, marker="o")
ax.set_title("Monthly Sales — 2026", fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()

# Save as PNG (default 100 DPI)
fig.savefig("sales_chart.png")
print("Saved: sales_chart.png")

# ══════════════════════════════════════════════════
# ACT 2: High Resolution
# ══════════════════════════════════════════════════
# Karen: "It's blurry when I zoom in."

fig.savefig("sales_chart_hd.png", dpi=300)
print("Saved: sales_chart_hd.png (300 DPI)")

# ══════════════════════════════════════════════════
# ACT 3: Transparent Background
# ══════════════════════════════════════════════════
# Karen: "I need it on a dark slide. Remove the white background."

fig.savefig("sales_chart_transparent.png", dpi=300, transparent=True)
print("Saved: sales_chart_transparent.png")

# ══════════════════════════════════════════════════
# ACT 4: PDF (vector — infinite zoom)
# ══════════════════════════════════════════════════
# Karen: "The CEO prints everything. Make it crisp."

fig.savefig("sales_chart.pdf", bbox_inches="tight")
print("Saved: sales_chart.pdf (vector)")

# ══════════════════════════════════════════════════
# ACT 5: SVG (for web)
# ══════════════════════════════════════════════════

fig.savefig("sales_chart.svg", bbox_inches="tight")
print("Saved: sales_chart.svg")

plt.close(fig)  # Close without showing (for batch processing)

# ══════════════════════════════════════════════════
# ACT 6: The Board-Ready Chart (everything combined)
# ══════════════════════════════════════════════════

custom = {
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "sans-serif",
    "font.size": 11,
}

with plt.rc_context(custom):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(months, sales, color="#1a73e8", linewidth=2.5, marker="o",
            markerfacecolor="white", markeredgecolor="#1a73e8",
            markeredgewidth=2, markersize=8)
    ax.fill_between(months, sales, alpha=0.06, color="#1a73e8")

    ax.set_title("ShopZilla — Monthly Revenue 2026",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_ylabel("Revenue ($)", fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", alpha=0.15)

    # Annotate peak
    peak_idx = sales.index(max(sales))
    ax.annotate(f"${max(sales):,}", xy=(months[peak_idx], max(sales)),
                xytext=(months[peak_idx], max(sales) + 1500),
                fontsize=11, fontweight="bold", color="#1a73e8", ha="center")

    # Source footnote
    ax.text(0.99, -0.12, "Source: ShopZilla Analytics",
            transform=ax.transAxes, fontsize=8, color="grey", ha="right")

    fig.savefig("board_ready.png", dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    fig.savefig("board_ready.pdf", bbox_inches="tight")
    print("Saved: board_ready.png + board_ready.pdf")

plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • fig.savefig("file.png") — save as PNG
# • dpi=300 — high resolution for print
# • transparent=True — no background
# • bbox_inches="tight" — crop whitespace
# • .pdf — vector format (infinite zoom)
# • .svg — vector for web
# • plt.close(fig) — close without showing (batch)
# • Always save BEFORE plt.show() (show clears the figure)
#
# Karen's checklist:
#   ✓ PNG at 300 DPI for email
#   ✓ PDF for printing
#   ✓ Transparent PNG for dark slides
#   ✓ SVG for the website
