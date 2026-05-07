# Episode 3: "Make It a Bar Chart"

> Run the code: `python ep03_bar_charts.py`

Karen: "Line charts are for trends. I need to compare categories." She wants to see which city sells the most — side by side, no ambiguity.

---

## Vertical Bars

```python
fig, ax = plt.subplots(figsize=(8, 4))

cities = ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
sales = [45000, 38000, 29000, 22000, 18000]
colors = ["#007acc", "#ff5f57", "#28c840", "#e6a700", "#c678dd"]

bars = ax.bar(cities, sales, color=colors, width=0.6,
              edgecolor="white", linewidth=0.5)
```

`ax.bar()` takes categories and values. Each bar gets its own color from the list.

## Value Labels on Bars

Bars without numbers make people squint. Add labels:

```python
for bar, val in zip(bars, sales):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
            f"${val:,}", ha="center", va="bottom", fontsize=9, fontweight="bold")
```

This places text centered above each bar. The math: `bar.get_x() + bar.get_width() / 2` finds the horizontal center.

## Horizontal Bars

When labels are long, flip the chart:

```python
sorted_idx = np.argsort(sales)
sorted_cities = [cities[i] for i in sorted_idx]
sorted_sales = [sales[i] for i in sorted_idx]

bars = ax.barh(sorted_cities, sorted_sales, color=sorted_colors, height=0.6)
```

Pro tip: sort the data before plotting. A ranked horizontal bar chart is one of the most readable chart types.

## Grouped Bars (Comparing Two Things)

Karen: "Show me Q1 vs Q2 for each city."

The trick is offsetting x positions:

```python
x = np.arange(len(cities))   # [0, 1, 2, 3, 4]
width = 0.35

bars1 = ax.bar(x - width/2, q1, width, label="Q1", color="#007acc")
bars2 = ax.bar(x + width/2, q2, width, label="Q2", color="#28c840")

ax.set_xticks(x)
ax.set_xticklabels(cities)
ax.legend()
```

`np.arange` gives you numeric positions. Shift left for group 1, right for group 2. Set tick labels manually.

## Stacked Bars

Show totals broken down by component:

```python
ax.bar(cities, q1, label="Q1", color="#007acc")
ax.bar(cities, q2, bottom=q1, label="Q2", color="#28c840")
```

The `bottom=` parameter is the key. It tells the second set of bars where to start — on top of the first.

## When to Use Which

| Type | Use When |
|------|----------|
| Vertical bars | Few categories, short labels |
| Horizontal bars | Many categories or long labels |
| Grouped bars | Comparing sub-groups side by side |
| Stacked bars | Showing composition of a total |

---

## Exercise

Create a grouped bar chart:
1. Pick 4-5 categories (teams, products, cities)
2. Create two data series (e.g., Q1 and Q2, or Plan vs Actual)
3. Use `np.arange` + width offset for grouping
4. Add value labels on top of each bar
5. Include a legend and title

Bonus: Create a stacked version of the same data.

## Quick Reference

| Function | Purpose |
|----------|---------|
| `ax.bar(x, y)` | Vertical bar chart |
| `ax.barh(y, x)` | Horizontal bar chart |
| `width=0.6` | Bar width |
| `bottom=values` | Stack bars |
| `ax.text(x, y, s)` | Value label |
| `np.arange(n)` | Numeric positions for grouping |
| `ax.set_xticks(positions)` | Set tick positions |
| `ax.set_xticklabels(labels)` | Set tick labels |
| `edgecolor="white"` | White border between bars |
