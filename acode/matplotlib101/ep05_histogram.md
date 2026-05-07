# Episode 5: "Show Me the Distribution"

> Run the code: `python ep05_histogram.py`

Karen: "What's the typical order size? Are most orders small or big?" She doesn't want averages — she wants to see the shape of the data. Time for a histogram.

---

## What a Histogram Shows

A histogram groups continuous data into bins and counts how many values fall in each bin. It answers: "What's the most common range?" and "Is the data skewed?"

Unlike a bar chart (which compares categories), a histogram shows the frequency distribution of a single variable.

## Basic Histogram

```python
import numpy as np

np.random.seed(42)
order_sizes = np.concatenate([
    np.random.normal(50, 15, 800),    # Most orders ~$50
    np.random.normal(150, 30, 200),   # Some big orders ~$150
])

fig, ax = plt.subplots(figsize=(8, 4))

ax.hist(order_sizes, bins=30, color="#007acc",
        edgecolor="white", linewidth=0.5)

ax.set_title("Order Size Distribution", fontweight="bold")
ax.set_xlabel("Order Size ($)")
ax.set_ylabel("Count")
```

`bins=30` means "split the range into 30 equal buckets." More bins = more detail but noisier. Fewer bins = smoother but less precise.

## Choosing Bin Count

| Bins | Effect |
|------|--------|
| 10 | Very smooth, hides detail |
| 20-30 | Good default for most data |
| 50+ | Very detailed, can look noisy |

Rule of thumb: start with `bins=30` and adjust. For 1000 data points, 30-50 bins works well.

## Adding Mean and Median Lines

```python
mean_val = np.mean(order_sizes)
median_val = np.median(order_sizes)

ax.axvline(mean_val, color="#ff5f57", linewidth=2, linestyle="--",
           label=f"Mean: ${mean_val:.0f}")
ax.axvline(median_val, color="#28c840", linewidth=2, linestyle="-.",
           label=f"Median: ${median_val:.0f}")

ax.legend(fontsize=10)
```

When mean ≠ median, the data is skewed. The bigger the gap, the more skewed.

## Overlapping Histograms

Compare two groups on the same axes:

```python
nyc_orders = np.random.normal(65, 20, 500)
la_orders = np.random.normal(50, 15, 500)

ax.hist(nyc_orders, bins=30, alpha=0.6, color="#007acc",
        label="NYC", edgecolor="white")
ax.hist(la_orders, bins=30, alpha=0.6, color="#ff5f57",
        label="LA", edgecolor="white")

ax.legend()
```

The key is `alpha=0.6` — transparency lets you see both distributions. Without it, one hides the other.

## Density vs Count

By default, the y-axis shows count. For comparing distributions of different sizes, use density:

```python
ax.hist(data, bins=30, density=True)  # Y-axis = probability density
```

With `density=True`, the total area under the histogram equals 1. This makes distributions comparable regardless of sample size.

## When to Use Histograms

- Understanding the shape of your data (normal? skewed? bimodal?)
- Finding outliers
- Comparing distributions between groups
- Checking if data meets assumptions (e.g., normality)

---

## Exercise

1. Generate 1000 random values from a normal distribution (`np.random.normal(100, 25, 1000)`)
2. Plot three histograms of the same data with different bin counts (10, 30, 60)
3. Use subplots (1 row, 3 columns) to show them side by side
4. Add mean and median lines to each
5. Title each subplot with the bin count

Bonus: Overlay two distributions (e.g., "before" and "after" a change) with transparency.

## Quick Reference

| Function | Purpose |
|----------|---------|
| `ax.hist(data, bins=30)` | Basic histogram |
| `bins=N` | Number of buckets |
| `alpha=0.6` | Transparency (for overlapping) |
| `density=True` | Normalize to probability |
| `edgecolor="white"` | White borders between bars |
| `ax.axvline(x)` | Vertical reference line |
| `np.mean(data)` | Calculate mean |
| `np.median(data)` | Calculate median |
