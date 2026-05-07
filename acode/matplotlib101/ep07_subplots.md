# Episode 7: "Put Them All on One Page"

> Run the code: `python ep07_subplots.py`

Karen: "I need line chart, bar chart, pie chart, and scatter — one slide." The board meeting is in an hour. Time to build a dashboard.

---

## The 2×2 Grid

```python
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
```

This creates a figure with 4 subplots arranged in a 2×2 grid. `axes` is a 2D array — access each subplot by row and column:

```python
axes[0][0]  # Top-left
axes[0][1]  # Top-right
axes[1][0]  # Bottom-left
axes[1][1]  # Bottom-right
```

Each `ax` works exactly like a single chart. Plot on it, style it, label it:

```python
ax = axes[0][0]
ax.plot(months, sales, color="#007acc", marker="o", linewidth=2)
ax.set_title("Monthly Trend", fontweight="bold", fontsize=11)

ax = axes[0][1]
ax.bar(cities, city_sales, color=colors)
ax.set_title("Sales by City", fontweight="bold", fontsize=11)
```

## Overall Title

```python
fig.suptitle("ShopZilla Q2 Dashboard", fontsize=14, fontweight="bold")
```

`fig.suptitle()` adds a title for the entire figure, above all subplots.

## Preventing Overlap

Subplots often overlap. Two fixes:

```python
plt.tight_layout()                    # Auto-adjust spacing
# OR
fig, axes = plt.subplots(2, 2, constrained_layout=True)  # Built-in
```

`tight_layout()` is the quick fix. `constrained_layout=True` is more robust for complex layouts.

## GridSpec: Unequal Sizes

Karen: "Make the line chart bigger — it's the most important."

```python
fig = plt.figure(figsize=(10, 6))
gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)

# Big chart: top row, spans all 3 columns
ax_main = fig.add_subplot(gs[0, :])

# Bottom row: 3 small charts
ax1 = fig.add_subplot(gs[1, 0])
ax2 = fig.add_subplot(gs[1, 1])
ax3 = fig.add_subplot(gs[1, 2])
```

`gs[0, :]` means "row 0, all columns" — the chart spans the full width. This is how you build real dashboards with a hero chart and supporting visuals.

## Different Chart Types Together

The power of subplots: mix any chart types on one page.

```python
# Line chart in one panel
axes[0][0].plot(months, sales, marker="o")

# Bar chart in another
axes[0][1].bar(cities, city_sales, color=colors)

# Pie chart
axes[1][0].pie(city_sales, labels=cities, autopct="%1.0f%%")

# Scatter
axes[1][1].scatter(x, y, alpha=0.6)
```

Each subplot is independent — different data, different chart type, different styling.

## Common Patterns

| Layout | Use Case |
|--------|----------|
| `subplots(1, 3)` | Compare 3 things side by side |
| `subplots(2, 2)` | Dashboard with 4 panels |
| `subplots(3, 1)` | Stacked time series |
| GridSpec | Hero chart + supporting panels |

---

## Exercise

Create a 2×2 dashboard:
1. Top-left: Line chart (monthly trend)
2. Top-right: Bar chart (category comparison)
3. Bottom-left: Pie or donut chart (distribution)
4. Bottom-right: Scatter plot (correlation)

Requirements:
- Use `fig, axes = plt.subplots(2, 2, figsize=(10, 7))`
- Add a `fig.suptitle()` for the overall title
- Style each subplot (remove spines, add titles)
- Use `plt.tight_layout()` to prevent overlap

Bonus: Recreate it with GridSpec, making the top chart span both columns.

## Quick Reference

| Function | Purpose |
|----------|---------|
| `plt.subplots(rows, cols)` | Create grid of subplots |
| `axes[row][col]` | Access a specific subplot |
| `fig.suptitle(s)` | Overall figure title |
| `plt.tight_layout()` | Auto-fix spacing |
| `constrained_layout=True` | Better auto-spacing |
| `fig.add_gridspec(r, c)` | Unequal grid layout |
| `fig.add_subplot(gs[0, :])` | Span multiple cells |
| `hspace=`, `wspace=` | Grid spacing control |
