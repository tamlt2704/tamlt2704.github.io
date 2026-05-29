---
title: "Chapter 3: Customization & Styling"
description: "Themes, annotations, and professional styling"
---

# Chapter 3: Customization & Styling

## Built-in Styles

```python
import matplotlib.pyplot as plt
import numpy as np

print(plt.style.available)  # list all styles

plt.style.use("seaborn-v0_8-darkgrid")
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title("Seaborn Style")
plt.show()
```

## Custom Colors and Markers

```python
plt.style.use("default")
x = np.arange(0, 10, 1)

plt.plot(x, x**2, "ro--", markersize=8, label="quadratic")
plt.plot(x, x * 5, "bs-.", markersize=6, label="linear")
plt.plot(x, np.sqrt(x) * 10, "g^-", markersize=7, label="sqrt")

plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()
```

## Annotations

```python
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

plt.plot(x, y)
plt.annotate("Maximum", xy=(np.pi/2, 1), xytext=(np.pi/2 + 1, 0.8),
             arrowprops=dict(arrowstyle="->", color="red"),
             fontsize=12, color="red")
plt.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
plt.title("Annotated Sine Wave")
plt.show()
```

## Custom rcParams

```python
plt.rcParams.update({
    "font.size": 14,
    "axes.labelsize": 12,
    "axes.titlesize": 16,
    "figure.figsize": (10, 6),
    "lines.linewidth": 2,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

plt.plot(np.random.randn(50).cumsum())
plt.title("Clean Minimal Style")
plt.xlabel("Time")
plt.ylabel("Value")
plt.show()
```

## Exercises

1. Recreate a plot using 3 different built-in styles and compare them side by side.
2. Create a line chart with custom annotations marking the min and max points.
3. Define a custom rcParams theme and apply it to a multi-panel figure.

---

[← prev](./chapter-02-subplots.md) | [next →](./chapter-04-3d-animations.md)
