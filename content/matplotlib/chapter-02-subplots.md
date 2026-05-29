---
title: "Chapter 2: Subplots & Layouts"
description: "Creating multi-panel figures with Matplotlib"
---

# Chapter 2: Subplots & Layouts

## Basic Subplots

```python
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
x = np.linspace(0, 2 * np.pi, 100)

axes[0, 0].plot(x, np.sin(x))
axes[0, 0].set_title("sin(x)")

axes[0, 1].plot(x, np.cos(x), color="orange")
axes[0, 1].set_title("cos(x)")

axes[1, 0].plot(x, np.tan(x), color="green")
axes[1, 0].set_ylim(-5, 5)
axes[1, 0].set_title("tan(x)")

axes[1, 1].plot(x, np.exp(-x), color="red")
axes[1, 1].set_title("exp(-x)")

plt.tight_layout()
plt.show()
```

## GridSpec for Complex Layouts

```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(12, 8))
gs = GridSpec(3, 3, figure=fig)

ax1 = fig.add_subplot(gs[0, :])  # top row, full width
ax2 = fig.add_subplot(gs[1, :2])  # middle row, 2/3 width
ax3 = fig.add_subplot(gs[1, 2])   # middle row, 1/3 width
ax4 = fig.add_subplot(gs[2, :])   # bottom row, full width

ax1.plot(np.random.randn(50).cumsum())
ax1.set_title("Full Width - Time Series")

ax2.bar(range(5), np.random.randint(1, 10, 5))
ax2.set_title("2/3 Width - Bar")

ax3.pie([30, 70], labels=["A", "B"], autopct="%1.0f%%")
ax3.set_title("1/3 Width - Pie")

ax4.hist(np.random.randn(1000), bins=30)
ax4.set_title("Full Width - Histogram")

plt.tight_layout()
plt.show()
```

## Shared Axes

```python
fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(10, 4))

data1 = np.random.randn(1000)
data2 = np.random.randn(1000) + 2

ax1.hist(data1, bins=30, color="skyblue")
ax1.set_title("Distribution A")

ax2.hist(data2, bins=30, color="salmon")
ax2.set_title("Distribution B")

plt.show()
```

## Exercises

1. Create a 3x1 layout showing line, bar, and scatter plots stacked vertically.
2. Use GridSpec to create a dashboard with one large plot on the left and two smaller plots stacked on the right.
3. Create 4 histograms with shared x and y axes comparing different distributions.

---

[← prev](./chapter-01-basics.md) | [next →](./chapter-03-styling.md)
