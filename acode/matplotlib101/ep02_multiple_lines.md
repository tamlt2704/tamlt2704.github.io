# Episode 2: "Compare the Two Products"

> Run the code: `python ep02_multiple_lines.py`

Karen's back. "Show me Widget A vs Widget B sales. On the same chart." She wants to see which product is winning — and when the crossover happened.

---

## Multiple Lines on One Chart

The trick is simple: call `ax.plot()` more than once.

```python
fig, ax = plt.subplots(figsize=(8, 4))

ax.plot(months, widget_a, label="Widget A",
        color="#007acc", linewidth=2, marker="o", markersize=6)
ax.plot(months, widget_b, label="Widget B",
        color="#ff5f57", linewidth=2, marker="s", markersize=6)

ax.legend()
```

Each `plot()` call adds a line. The `label=` parameter feeds into the legend. Without `ax.legend()`, the labels exist but nobody sees them.

## Legend Placement

```python
ax.legend(loc="upper left")    # Manual position
ax.legend(loc="best")          # Let matplotlib decide (default)
```

Options: `upper left`, `upper right`, `lower left`, `lower right`, `center`, `best`.

## Colors and Line Styles

Matplotlib supports four line styles:

```python
styles = [
    {"linestyle": "-",  "marker": "o", "label": "Solid + circle"},
    {"linestyle": "--", "marker": "s", "label": "Dashed + square"},
    {"linestyle": "-.", "marker": "^", "label": "Dash-dot + triangle"},
    {"linestyle": ":",  "marker": "D", "label": "Dotted + diamond"},
]

for style in styles:
    ax.plot(months, data, linewidth=2, markersize=6, **style)
```

Common markers: `o` (circle), `s` (square), `^` (triangle up), `v` (triangle down), `D` (diamond), `*` (star), `+` (plus).

## Highlighting the Crossover

When two lines cross, `fill_between` with a `where` condition makes it visual:

```python
ax.fill_between(months, widget_a, widget_b,
                where=[a > b for a, b in zip(widget_a, widget_b)],
                alpha=0.15, color="#007acc", label="A leads")

ax.fill_between(months, widget_a, widget_b,
                where=[b >= a for a, b in zip(widget_a, widget_b)],
                alpha=0.15, color="#ff5f57", label="B leads")
```

The shaded regions instantly show who's winning at any point in time. Karen loves this.

## When to Use Multiple Lines

- Comparing trends over the same time period
- Showing actual vs target
- Before/after comparisons
- Multiple categories on the same scale

If the scales are wildly different (e.g., revenue vs units), use twin axes or subplots instead.

---

## Exercise

Create a chart comparing 3 products over 6 months:
1. Use different colors, line styles, and markers for each
2. Add a legend (try `loc="upper left"`)
3. Use `fill_between` to shade the region where Product C leads
4. Add a title and axis labels
5. Remove top/right spines

Bonus: Add a horizontal dashed line showing the team target.

## Quick Reference

| Function | Purpose |
|----------|---------|
| `ax.plot(x, y, label="...")` | Add a labeled line |
| `ax.legend()` | Show the legend |
| `ax.legend(loc="upper left")` | Position the legend |
| `linestyle="-"` | Solid line |
| `linestyle="--"` | Dashed line |
| `linestyle="-."` | Dash-dot line |
| `linestyle=":"` | Dotted line |
| `marker="o"` | Circle marker |
| `marker="s"` | Square marker |
| `marker="^"` | Triangle marker |
| `fill_between(x, y1, y2, where=)` | Conditional shading |
