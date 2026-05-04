"""
Matplotlib 101 — Episode 05: "Show Me the Distribution"
Karen: "What's the typical order size? Are most orders small or big?"

Run: python ep05_histogram.py
"""
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
order_sizes = np.concatenate([
    np.random.normal(50, 15, 800),     # Most orders ~$50
    np.random.normal(150, 30, 200),    # Some big orders ~$150
])

# ══════════════════════════════════════════════════
# ACT 1: Basic Histogram
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

ax.hist(order_sizes, bins=30, color="#007acc", edgecolor="white", linewidth=0.5)

ax.set_title("Order Size Distribution", fontweight="bold")
ax.set_xlabel("Order Size ($)")
ax.set_ylabel("Count")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# Karen: "What's the average? And the median?"

# ══════════════════════════════════════════════════
# ACT 2: With Mean & Median Lines
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

ax.hist(order_sizes, bins=40, color="#007acc", edgecolor="white",
        linewidth=0.5, alpha=0.7)

mean_val = np.mean(order_sizes)
median_val = np.median(order_sizes)

ax.axvline(mean_val, color="#ff5f57", linewidth=2, linestyle="--",
           label=f"Mean: ${mean_val:.0f}")
ax.axvline(median_val, color="#28c840", linewidth=2, linestyle="-.",
           label=f"Median: ${median_val:.0f}")

ax.legend(fontsize=10)
ax.set_title("Order Size Distribution with Mean & Median", fontweight="bold")
ax.set_xlabel("Order Size ($)")
ax.set_ylabel("Count")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Overlapping Histograms (compare two groups)
# ══════════════════════════════════════════════════
# Karen: "Compare NYC orders vs LA orders."

nyc_orders = np.random.normal(65, 20, 500)
la_orders = np.random.normal(50, 15, 500)

fig, ax = plt.subplots(figsize=(8, 4))

ax.hist(nyc_orders, bins=30, alpha=0.6, color="#007acc", label="NYC", edgecolor="white")
ax.hist(la_orders, bins=30, alpha=0.6, color="#ff5f57", label="LA", edgecolor="white")

ax.legend()
ax.set_title("Order Size: NYC vs LA", fontweight="bold")
ax.set_xlabel("Order Size ($)")
ax.set_ylabel("Count")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • ax.hist(data, bins=30) — basic histogram
# • alpha=0.6 — transparency for overlapping
# • ax.axvline(x) — vertical reference line
# • Overlapping histograms: two hist() calls with alpha
