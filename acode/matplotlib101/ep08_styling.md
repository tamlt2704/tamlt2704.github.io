# Episode 8: "Make It Look Professional"

> Run the code: `python ep08_styling.py`

Karen: "This looks like a homework assignment. Make it board-ready." She wants company colors, clean typography, and a polished feel. Time to learn matplotlib's styling system.

---

## Built-in Styles

Matplotlib ships with pre-made themes. Apply one with a single line:

```python
plt.style.use("seaborn-v0_8")    # Apply globally
```

Or use it temporarily:

```python
with plt.style.context("dark_background"):
    fig, ax = plt.subplots()
    ax.plot(months, sales)
    plt.show()
```

The `with` block applies the style only inside it — your other charts stay unchanged.

### Popular Built-in Styles

| Style | Look |
|-------|------|
| `"default"` | Standard matplotlib |
| `"seaborn-v0_8"` | Clean, muted colors |
| `"ggplot"` | R's ggplot2 look |
| `"dark_background"` | Dark theme |
| `"fivethirtyeight"` | Bold, journalistic |
| `"bmh"` | Bayesian Methods for Hackers |

See all available: `print(plt.style.available)`

## Dark Theme

```python
with plt.style.context("dark_background"):
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(months, sales, color="#4ec9b0", linewidth=2.5, marker="o",
            markerfacecolor="white", markeredgecolor="#4ec9b0", markersize=8)
    ax.fill_between(months, sales, alpha=0.1, color="#4ec9b0")

    ax.set_title("Monthly Sales — Dark Theme", fontweight="bold")
    ax.grid(True, alpha=0.15)
```

Dark themes work well for dashboards and presentations on screens. Avoid them for printed reports.

## Custom rcParams (Full Control)

When built-in styles aren't enough, define every detail:

```python
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
    ax.plot(months, sales, color="#007acc", linewidth=2.5)
    # ... all text/colors follow your params
```

`plt.rc_context()` applies params temporarily. Use `plt.rcParams.update()` to set them globally.

## Removing Spines

The single biggest visual improvement:

```python
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
```

Two lines. Instant upgrade. The top and right borders add nothing — removing them reduces visual noise.

## Key rcParams to Know

| Parameter | Controls |
|-----------|----------|
| `figure.facecolor` | Background of the figure |
| `axes.facecolor` | Background of the plot area |
| `text.color` | All text color |
| `axes.labelcolor` | Axis label color |
| `xtick.color` / `ytick.color` | Tick mark colors |
| `grid.color` / `grid.alpha` | Grid appearance |
| `font.family` | Font (sans-serif, monospace, serif) |
| `font.size` | Base font size |

## Creating a Brand Style

For consistent charts across a project, define your style once:

```python
BRAND = {
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.alpha": 0.15,
}

# Use everywhere
with plt.rc_context(BRAND):
    # All your charts here
    pass
```

---

## Exercise

1. Try 3 different built-in styles on the same data (use `plt.style.context`)
2. Create a custom `rcParams` dictionary with:
   - A dark background
   - Light-colored text
   - A monospace font
   - Subtle grid
3. Apply your custom style to a line chart and a bar chart
4. Remove all four spines and use only grid lines for reference

## Quick Reference

| Function | Purpose |
|----------|---------|
| `plt.style.use("name")` | Apply style globally |
| `plt.style.context("name")` | Temporary style (with block) |
| `plt.rc_context(params)` | Custom params (temporary) |
| `plt.rcParams.update(params)` | Custom params (global) |
| `plt.style.available` | List all built-in styles |
| `ax.spines["top"].set_visible(False)` | Remove a border |
| `"figure.facecolor"` | Figure background |
| `"font.family"` | Font choice |
| `"font.size"` | Base text size |
