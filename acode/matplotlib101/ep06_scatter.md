# Episode 6: "Is There a Correlation?"

> Run the code: `python ep06_scatter.py`

Karen: "Do higher-priced products sell more or less?" She suspects a relationship. A scatter plot will reveal it — and encode extra dimensions with size and color.

---

## Basic Scatter Plot

```python
fig, ax = plt.subplots(figsize=(8, 5))

ax.scatter(prices, units_sold,
           color="#007acc", alpha=0.6,
           edgecolors="white", linewidth=0.5)

ax.set_title("Price vs Units Sold", fontweight="bold")
ax.set_xlabel("Price ($)")
ax.set_ylabel("Units Sold")
```

Each dot is one data point. The pattern (or lack of one) tells the story. Here: higher price → fewer units sold. Classic inverse relationship.

## Size as a Third Variable (Bubble Chart)

Encode a third dimension using dot size:

```python
scatter = ax.scatter(
    prices, units_sold,
    s=revenue / 100,          # Size = revenue (scaled)
    c=colors,                 # Color = category
    alpha=0.6,
    edgecolors="white",
    linewidth=0.5,
)
```

The `s=` parameter controls dot area. Scale your values down — raw revenue numbers would make dots enormous.

## Color with Colormaps

For continuous variables, use a colormap instead of discrete colors:

```python
scatter = ax.scatter(
    prices, units_sold,
    c=revenue,               # Continuous color scale
    cmap="YlOrRd",           # Yellow → Orange → Red
    s=50,
    alpha=0.7,
    edgecolors="white",
)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Revenue ($)")
```

Popular colormaps:
- `"viridis"` — perceptually uniform (default, good for most data)
- `"YlOrRd"` — yellow to red (good for "heat")
- `"coolwarm"` — blue to red (good for diverging data)
- `"Blues"` — light to dark blue (sequential)

## Alpha for Dense Data

When dots overlap heavily, transparency reveals density:

```python
ax.scatter(x, y, alpha=0.3)   # Very transparent — dense clusters show darker
```

Low alpha (0.2-0.4) works for thousands of points. Higher alpha (0.6-0.8) for dozens.

## Adding a Trend Line

Show the overall relationship with a fitted line:

```python
# Fit a linear trend
z = np.polyfit(prices, units_sold, 1)   # degree=1 → linear
p = np.poly1d(z)

# Plot the trend line
x_line = np.linspace(prices.min(), prices.max(), 100)
ax.plot(x_line, p(x_line), "--", color="#ff5f57", linewidth=2, label="Trend")
```

`np.polyfit` with degree 1 gives a straight line. Degree 2 gives a curve.

## Manual Legend for Categories

When using color lists (not colormaps), build the legend manually:

```python
cat_colors = {"Electronics": "#007acc", "Home": "#28c840", "Clothing": "#ff5f57"}

for cat, color in cat_colors.items():
    ax.scatter([], [], c=color, s=60, label=cat, edgecolors="white")
ax.legend(title="Category", loc="upper right")
```

Plot empty scatter calls just to create legend entries.

---

## Exercise

Create a scatter plot with 4 encoded dimensions:
1. X-axis: one variable (e.g., hours studied)
2. Y-axis: another variable (e.g., test score)
3. Size: a third variable (e.g., number of practice tests)
4. Color: a fourth variable using a colormap (e.g., confidence level)
5. Add a colorbar
6. Add a trend line with `np.polyfit`
7. Set `alpha=0.6` for overlapping points

## Quick Reference

| Function | Purpose |
|----------|---------|
| `ax.scatter(x, y)` | Basic scatter plot |
| `s=values` | Dot size (bubble chart) |
| `c=values` | Dot color (continuous) |
| `cmap="viridis"` | Color map |
| `alpha=0.6` | Transparency |
| `plt.colorbar(scatter)` | Add color scale |
| `edgecolors="white"` | White dot borders |
| `np.polyfit(x, y, deg)` | Fit polynomial |
| `np.poly1d(coeffs)` | Create polynomial function |
