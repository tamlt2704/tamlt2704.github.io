---
title: "Chapter 1: Setup & Basic Plots"
description: "Line, bar, and scatter plots with Matplotlib"
---

# Chapter 1: Setup & Basic Plots

## Installation

```python
pip install matplotlib numpy
```

## Your First Plot

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title("Sine Wave")
plt.xlabel("x")
plt.ylabel("sin(x)")
plt.show()
```

## Line Plot

```python
x = np.arange(0, 5, 0.1)
plt.plot(x, x**2, label="quadratic")
plt.plot(x, x**3, label="cubic")
plt.legend()
plt.grid(True)
plt.show()
```

## Bar Plot

```python
categories = ["A", "B", "C", "D"]
values = [23, 45, 12, 67]

plt.bar(categories, values, color="steelblue")
plt.title("Sales by Category")
plt.ylabel("Revenue ($k)")
plt.show()
```

## Scatter Plot

```python
np.random.seed(42)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100) * 0.5

plt.scatter(x, y, alpha=0.6, c=y, cmap="viridis")
plt.colorbar(label="y value")
plt.title("Scatter with Color Map")
plt.show()
```

## Exercises

1. Plot `cos(x)` and `sin(x)` on the same figure with a legend.
2. Create a horizontal bar chart of 5 programming languages and their popularity scores.
3. Generate a scatter plot of 200 random points colored by their distance from the origin.

---

[← prev](./chapter-00-overview.md) | [next →](./chapter-02-subplots.md)
