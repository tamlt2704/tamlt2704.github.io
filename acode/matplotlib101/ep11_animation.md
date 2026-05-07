# Episode 11: "Make It Move"

> Run the code: `python ep11_animation.py`

Karen: "Can the chart animate? Like those YouTube videos?" She wants the line to draw itself, the bars to race. Matplotlib can do it — with `FuncAnimation`.

---

## How Animation Works

Matplotlib animation is frame-based. You define:
1. A figure with empty plot elements
2. An `update(frame)` function that redraws each frame
3. `FuncAnimation` that calls `update` repeatedly

```python
import matplotlib.animation as animation
```

## Animated Line (Drawing Itself)

```python
fig, ax = plt.subplots(figsize=(8, 4))

months = list(range(1, 13))
sales = [12, 15, 13, 18, 22, 19, 24, 28, 25, 30, 35, 32]

line, = ax.plot([], [], color="#007acc", linewidth=2, marker="o")
ax.set_xlim(0.5, 12.5)
ax.set_ylim(0, 40)

def init():
    line.set_data([], [])
    return (line,)

def update(frame):
    x = months[:frame + 1]
    y = sales[:frame + 1]
    line.set_data(x, y)
    return (line,)

ani = animation.FuncAnimation(fig, update, frames=12,
                               init_func=init, interval=300,
                               blit=True, repeat=False)
plt.show()
```

Key concepts:
- `line, = ax.plot([], [])` — create an empty line (note the comma — it unpacks the list)
- `init()` — sets the starting state
- `update(frame)` — called for each frame number (0, 1, 2, ...)
- `interval=300` — milliseconds between frames
- `blit=True` — only redraw changed elements (faster)

## Bar Chart Race

A popular format: bars that grow and re-sort over time.

```python
def update_bars(frame):
    ax.clear()
    values = data[frame]
    sorted_idx = np.argsort(values)

    sorted_langs = [languages[i] for i in sorted_idx]
    sorted_vals = values[sorted_idx]
    sorted_colors = [colors[i] for i in sorted_idx]

    ax.barh(range(len(languages)), sorted_vals, color=sorted_colors)
    ax.set_yticks(range(len(languages)))
    ax.set_yticklabels(sorted_langs)
    ax.set_xlim(0, data.max() + 5)
    ax.set_title(f"Step {frame + 1}", fontweight="bold")

ani = animation.FuncAnimation(fig, update_bars, frames=20,
                               interval=400, repeat=False)
```

For bar races, `ax.clear()` each frame and redraw everything. It's simpler than updating individual bars.

## Saving Animations

```python
# Save as GIF
ani.save("chart.gif", writer="pillow", fps=10)

# Save as MP4 (requires ffmpeg)
ani.save("chart.mp4", writer="ffmpeg", fps=30)
```

Requirements:
- GIF: `pip install pillow` (usually already installed)
- MP4: install [ffmpeg](https://ffmpeg.org/) on your system

## Traveling Wave (Continuous Animation)

```python
x = np.linspace(0, 4 * np.pi, 200)
line, = ax.plot([], [], color="#4ec9b0", linewidth=2)
ax.set_xlim(0, 4 * np.pi)
ax.set_ylim(-1.5, 1.5)

def update_wave(frame):
    y = np.sin(x - frame * 0.1)
    line.set_data(x, y)
    return (line,)

ani = animation.FuncAnimation(fig, update_wave, frames=100,
                               interval=30, blit=True)
```

## Interactive Widgets (Sliders)

For exploration rather than presentation:

```python
from matplotlib.widgets import Slider

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

# Create slider
ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
slider = Slider(ax_slider, "Bins", 5, 100, valinit=30, valstep=1)

def update_slider(val):
    ax.clear()
    ax.hist(data, bins=int(slider.val))
    fig.canvas.draw_idle()

slider.on_changed(update_slider)
```

## Animation Tips

- Keep `interval` above 30ms (below that, frames may drop)
- Use `blit=True` for line/scatter animations (faster)
- Use `ax.clear()` for bar charts (simpler to redraw)
- Set axis limits before animating (prevents jumping)
- `repeat=False` stops after one cycle

---

## Exercise

Create an animated line chart that draws itself:
1. Define 12 data points (monthly sales, temperature, anything)
2. Set up an empty line with `ax.plot([], [])`
3. Write an `update(frame)` that reveals one more point each frame
4. Use `FuncAnimation` with `interval=300`
5. Save it as a GIF with `ani.save("my_chart.gif", writer="pillow")`

Bonus: Add a text element that updates with the current value each frame.

## Quick Reference

| Function | Purpose |
|----------|---------|
| `animation.FuncAnimation(fig, update, frames=N)` | Create animation |
| `interval=300` | Milliseconds between frames |
| `blit=True` | Only redraw changed parts |
| `repeat=False` | Stop after one cycle |
| `init_func=init` | Initial empty state |
| `line.set_data(x, y)` | Update line data |
| `ani.save("out.gif", writer="pillow")` | Save as GIF |
| `ani.save("out.mp4", writer="ffmpeg")` | Save as MP4 |
| `Slider(ax, label, min, max)` | Interactive slider |
