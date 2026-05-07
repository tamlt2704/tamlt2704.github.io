"""
Matplotlib 101 — Episode 11: "Make It Move"
Karen: "Can the chart animate? Like those YouTube videos?"

Run: python ep11_animation.py
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# ══════════════════════════════════════════════════
# ACT 1: Animated Line (data appearing over time)
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))

months = list(range(1, 13))
sales = [12, 15, 13, 18, 22, 19, 24, 28, 25, 30, 35, 32]

line, = ax.plot([], [], color="#007acc", linewidth=2, marker="o", markersize=5)
ax.set_xlim(0.5, 12.5)
ax.set_ylim(0, 40)
ax.set_title("Monthly Sales — Animated", fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($K)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, alpha=0.2)

def init():
    line.set_data([], [])
    return (line,)

def update(frame):
    x = months[:frame + 1]
    y = sales[:frame + 1]
    line.set_data(x, y)
    return (line,)

ani = animation.FuncAnimation(fig, update, frames=12, init_func=init,
                               interval=300, blit=True, repeat=False)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 2: Animated Bar Chart Race
# ══════════════════════════════════════════════════

np.random.seed(42)
languages = ["Python", "JavaScript", "Java", "C++", "Rust"]
colors = ["#007acc", "#e6a700", "#ff5f57", "#28c840", "#c678dd"]

# Generate 20 time steps
data = np.zeros((20, 5))
data[0] = [10, 12, 15, 8, 3]
for i in range(1, 20):
    data[i] = data[i - 1] + np.random.randint(0, 5, 5)

fig, ax = plt.subplots(figsize=(8, 4))

def update_bars(frame):
    ax.clear()
    values = data[frame]
    sorted_idx = np.argsort(values)

    y_pos = range(len(languages))
    sorted_langs = [languages[i] for i in sorted_idx]
    sorted_vals = values[sorted_idx]
    sorted_colors = [colors[i] for i in sorted_idx]

    ax.barh(y_pos, sorted_vals, color=sorted_colors, height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_langs)
    ax.set_xlim(0, data.max() + 5)
    ax.set_title(f"Language Popularity — Step {frame + 1}", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for i, (val, lang) in enumerate(zip(sorted_vals, sorted_langs)):
        ax.text(val + 0.5, i, f"{val:.0f}", va="center", fontsize=9)

ani2 = animation.FuncAnimation(fig, update_bars, frames=20,
                                interval=400, repeat=False)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# ACT 3: Sine Wave Animation
# ══════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 4))
x = np.linspace(0, 4 * np.pi, 200)
line, = ax.plot([], [], color="#4ec9b0", linewidth=2)
ax.set_xlim(0, 4 * np.pi)
ax.set_ylim(-1.5, 1.5)
ax.set_title("Traveling Wave", fontweight="bold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, alpha=0.2)

def update_wave(frame):
    y = np.sin(x - frame * 0.1)
    line.set_data(x, y)
    return (line,)

ani3 = animation.FuncAnimation(fig, update_wave, frames=100,
                                interval=30, blit=True)
plt.tight_layout()
plt.show()

# ══════════════════════════════════════════════════
# RECAP
# ══════════════════════════════════════════════════
# • FuncAnimation(fig, update, frames=N, interval=ms)
# • update(frame) — called each frame, redraws the chart
# • init_func — sets up empty state
# • blit=True — only redraw changed parts (faster)
# • interval — milliseconds between frames
# • Save: ani.save("output.mp4", writer="ffmpeg", fps=30)
