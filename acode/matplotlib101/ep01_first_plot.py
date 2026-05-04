"""
Matplotlib 101 — Episode 01: "Just Show Me the Numbers"
Karen has monthly sales data. She wants to see the trend. You have 5 minutes.

Run: python ep01_first_plot.py
"""
import matplotlib.pyplot as plt

# ══════════════════════════════════════════════════
# ACT 1: The Wrong Way
# ══════════════════════════════════════════════════
# Karen emails you a list of numbers:
#   "Jan: 12000, Feb: 15000, Mar: 13000, Apr: 18000, May: 22000, Jun: 19000"
# You print them. She stares at you. "I said SHOW me."

sales = [12000, 15000, 13000, 18000, 22000, 19000]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

# ══════════════════════════════════════════════════
# ACT 2: The Simplest Plot
# ══════════════════════════════════════════════════
# Two lines. That's all it takes.

plt.plot(months, sales)
plt.show()

# Karen: "What am I looking at? There's no title. No labels."

# ══════════════════════════════════════════════════
# ACT 3: Add Labels and Title
# ══════════════════════════════════════════════════

plt.plot(months, sales)
plt.title("Monthly Sales — 2026")      # What the chart is about
plt.xlabel("Month")                      # What the x-axis means
plt.ylabel("Revenue ($)")                # What the y-axis means
plt.show()

# Karen: "Better. But it looks like a default Excel chart."

# ══════════════════════════════════════════════════
# ACT 4: The Figure and Axes (The Real Way)
# ══════════════════════════════════════════════════
# plt.plot() is a shortcut. The real API uses Figure and Axes.
#
#   Figure = the entire canvas (the window)
#   Axes   = one chart inside the figure
#
# Think of it as: Figure is the whiteboard, Axes is one drawing on it.

fig, ax = plt.subplots()                 # Create figure + one axes

ax.plot(months, sales,
        color="#007acc",                  # Line color
        linewidth=2,                      # Line thickness
        marker="o",                       # Dot at each data point
        markersize=6)                     # Dot size

ax.set_title("Monthly Sales — 2026", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")

# Format y-axis as currency
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Add grid (subtle)
ax.grid(True, alpha=0.3)

plt.tight_layout()                        # Prevent label clipping
plt.show()

# Karen: "Now THAT'S a chart."

# ══════════════════════════════════════════════════
# ACT 5: Customize Everything
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))   # Custom size (inches)

ax.plot(months, sales,
        color="#28c840",
        linewidth=2.5,
        marker="o",
        markerfacecolor="white",          # White dot center
        markeredgecolor="#28c840",         # Green dot border
        markeredgewidth=2,
        markersize=8)

# Fill area under the line
ax.fill_between(months, sales, alpha=0.1, color="#28c840")

ax.set_title("Monthly Sales — 2026", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month", fontsize=11)
ax.set_ylabel("Revenue ($)", fontsize=11)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Remove top and right borders (cleaner look)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.grid(True, axis="y", alpha=0.2)

# Annotate the peak
peak_idx = sales.index(max(sales))
ax.annotate(f"Peak: ${max(sales):,}",
            xy=(months[peak_idx], max(sales)),
            xytext=(months[peak_idx], max(sales) + 2000),
            fontsize=10, color="#28c840",
            arrowprops=dict(arrowstyle="->", color="#28c840"))

plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# What you learned:
# • plt.plot(x, y) — the simplest chart
# • fig, ax = plt.subplots() — the real API
# • ax.set_title(), ax.set_xlabel(), ax.set_ylabel()
# • color, linewidth, marker, markersize
# • ax.fill_between() — shaded area
# • ax.spines — remove borders
# • ax.annotate() — point out important values
# • plt.tight_layout() — prevent clipping
# • plt.show() — display the chart
