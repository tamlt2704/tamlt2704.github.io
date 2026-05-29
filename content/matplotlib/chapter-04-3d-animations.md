---
title: "Chapter 4: 3D Plots & Animations"
description: "Three-dimensional visualization and animated plots"
---

# Chapter 4: 3D Plots & Animations

## 3D Surface Plot

```python
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8)
ax.set_title("3D Surface: sin(sqrt(x² + y²))")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()
```

## 3D Scatter Plot

```python
fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection="3d")

n = 300
x = np.random.randn(n)
y = np.random.randn(n)
z = np.random.randn(n)
colors = np.sqrt(x**2 + y**2 + z**2)

scatter = ax.scatter(x, y, z, c=colors, cmap="plasma", alpha=0.6)
plt.colorbar(scatter, label="Distance from origin")
ax.set_title("3D Scatter Plot")
plt.show()
```

## Basic Animation

```python
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
x = np.linspace(0, 2 * np.pi, 100)
line, = ax.plot(x, np.sin(x))
ax.set_ylim(-1.5, 1.5)

def update(frame):
    line.set_ydata(np.sin(x + frame / 10))
    return line,

ani = FuncAnimation(fig, update, frames=100, interval=50, blit=True)
plt.title("Animated Sine Wave")
plt.show()
# ani.save("sine_wave.gif", writer="pillow")
```

## Animated Scatter

```python
fig, ax = plt.subplots()
scat = ax.scatter([], [], c=[], cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)

def update(frame):
    n = frame * 5
    x = np.random.randn(n)
    y = np.random.randn(n)
    scat.set_offsets(np.column_stack([x, y]))
    scat.set_array(x * y)
    return scat,

ani = FuncAnimation(fig, update, frames=60, interval=100, blit=True)
plt.title("Growing Scatter")
plt.show()
```

## Exercises

1. Create a 3D wireframe plot of `cos(x) * sin(y)`.
2. Animate a bar chart where bar heights change each frame.
3. Create a 3D parametric curve (helix) and rotate the view angle in an animation.

---

[← prev](./chapter-03-styling.md) | [next →](./chapter-05-advanced.md)
