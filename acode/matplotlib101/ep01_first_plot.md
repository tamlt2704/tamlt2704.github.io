# Episode 1: "Just Show Me the Numbers"

> Run the code: `python ep01_first_plot.py`

Karen emails you a list of numbers. "Jan: 12000, Feb: 15000, Mar: 13000..." You print them to the console. She stares at you. "I said SHOW me."

Time to learn matplotlib.

---

## What Is Matplotlib?

Matplotlib is Python's foundational plotting library. Nearly every chart you've seen in a Python blog post, Jupyter notebook, or data science paper was made with it (or something built on top of it).

```bash
pip install matplotlib numpy
```

That's it. You're ready.

## The Two APIs

Matplotlib has two ways to make charts:

**1. pyplot (quick and dirty)**

```python
import matplotlib.pyplot as plt

sales = [12000, 15000, 13000, 18000, 22000, 19000]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

plt.plot(months, sales)
plt.show()
```

Two lines. A chart appears. Karen is unimpressed — there's no title, no labels.

**2. Figure/Axes (the proper way)**

```python
fig, ax = plt.subplots()

ax.plot(months, sales, color="#007acc", linewidth=2, marker="o", markersize=6)
ax.set_title("Monthly Sales — 2026", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

The mental model:
- **Figure** = the entire canvas (the window)
- **Axes** = one chart inside the figure

Think of it as: Figure is the whiteboard, Axes is one drawing on it. Always use `fig, ax = plt.subplots()` — it scales to multiple charts later.

## Making It Look Good

### Markers, Colors, and Line Width

```python
ax.plot(months, sales,
        color="#28c840",        # Any hex color
        linewidth=2.5,          # Thicker line
        marker="o",             # Circle at each point
        markerfacecolor="white",
        markeredgecolor="#28c840",
        markeredgewidth=2,
        markersize=8)
```

### Fill Under the Line

```python
ax.fill_between(months, sales, alpha=0.1, color="#28c840")
```

This adds a subtle shaded area — makes the chart feel more polished.

### Remove Clutter (Spines)

```python
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
```

Two lines that instantly make any chart look cleaner.

### Annotate Important Points

```python
peak_idx = sales.index(max(sales))
ax.annotate(f"Peak: ${max(sales):,}",
            xy=(months[peak_idx], max(sales)),
            xytext=(months[peak_idx], max(sales) + 2000),
            arrowprops=dict(arrowstyle="->", color="#28c840"))
```

### Format Axis Labels

```python
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
```

Now the y-axis reads `$12,000` instead of `12000`.

## The Pattern

Every matplotlib chart follows the same rhythm:

1. Create figure and axes: `fig, ax = plt.subplots()`
2. Plot data: `ax.plot(x, y, ...)`
3. Style it: title, labels, colors, spines
4. Show or save: `plt.show()` or `fig.savefig()`

---

## Exercise

Plot your own data. Pick one:
- Daily step count for a week
- Temperature highs for the past 7 days
- Hours of sleep each night

Requirements:
1. Use `fig, ax = plt.subplots()`
2. Add a title, x-label, and y-label
3. Use a custom color and markers
4. Remove the top and right spines
5. Add `fill_between` for the shaded area
6. Annotate the highest value

## Quick Reference

| Function | Purpose |
|----------|---------|
| `plt.subplots()` | Create figure + axes |
| `ax.plot(x, y)` | Line chart |
| `ax.set_title(s)` | Chart title |
| `ax.set_xlabel(s)` | X-axis label |
| `ax.set_ylabel(s)` | Y-axis label |
| `ax.grid(True)` | Show grid |
| `ax.fill_between(x, y)` | Shaded area |
| `ax.annotate(text, xy=)` | Callout arrow |
| `ax.spines["top"].set_visible(False)` | Remove border |
| `plt.tight_layout()` | Prevent clipping |
| `plt.show()` | Display the chart |
