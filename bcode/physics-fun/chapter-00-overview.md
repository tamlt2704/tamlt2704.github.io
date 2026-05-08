# Chapter 0: Before You Start

[Chapter 1: Dropping Things →](chapter-01-freefall.md)

---

## The Story

You're a game developer at **GravityLab Studios**, a small indie team building a physics sandbox game called *Toss It!* — a game where players throw, drop, bounce, and launch objects in increasingly ridiculous scenarios.

The problem: your game's physics are fake. Objects fall at constant speed. Balls don't bounce — they stick to walls. Cannonballs fly in straight lines. The rope swing looks like a stiff rod. Players keep leaving reviews: "physics feel wrong."

Your lead designer, **Zara**, drops a gif in the team chat — a ball falling through the floor:

"This is embarrassing. Real physics or I'm switching to Unity."

You don't want to switch to Unity. You want to understand the physics well enough to simulate them yourself. Over 12 chapters, you'll add real physics to *Toss It!* — gravity, collisions, springs, orbits, waves — one broken mechanic at a time.

Every chapter is a Python simulation you can run and see. The math is real. The code is simple. The results are visual.

## How This Works

Each chapter follows the same loop:

1. **The broken version** — what the game currently does (wrong)
2. **The physics** — what should actually happen (equations, intuition)
3. **The simulation** — Python code that implements it correctly
4. **The result** — before/after comparison

You don't need a physics background. You need to be comfortable with:
- Basic algebra (solve for x)
- Coordinates (x, y)
- The idea that velocity = how fast position changes

Everything else is introduced when you need it.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Gameplay Programmer | "I'll just fake it" → "okay I need real physics" |
| **Zara** | Lead Designer | Obsessed with "game feel." Notices 1-pixel errors. |
| **Tomás** | Artist | "Why does the ball squish wrong on bounce?" |
| **QA Bot** | Automated tester | Finds edge cases where physics break |

## Prerequisites

### Python 3.10+

```bash
python3 --version
# Python 3.10.x or higher
```

### matplotlib (optional but recommended)

For visualizing simulations:

```bash
pip install matplotlib
```

Without matplotlib, you'll see numerical output. With it, you'll see animated plots.

### The Simulation Loop

Every physics simulation in this course uses the same structure:

```python
import time

dt = 0.016  # Time step: ~60 FPS (1/60 seconds)

# Initial state
x, y = 0.0, 100.0  # Position
vx, vy = 0.0, 0.0  # Velocity

# Simulation loop
for frame in range(300):  # 5 seconds at 60 FPS
    # 1. Apply forces (changes velocity)
    # 2. Update velocity
    # 3. Update position
    # 4. Check collisions
    # 5. Draw/print

    x += vx * dt
    y += vy * dt
```

This is **Euler integration** — the simplest way to step physics forward in time. It's not perfect (we'll discuss why), but it's good enough for a game and easy to understand.

## Units

We use SI units throughout:

| Quantity | Unit | Symbol |
|---|---|---|
| Distance | meters | m |
| Time | seconds | s |
| Velocity | meters/second | m/s |
| Acceleration | meters/second² | m/s² |
| Mass | kilograms | kg |
| Force | newtons | N (= kg·m/s²) |

Gravity on Earth: **g = 9.81 m/s²** (we'll round to 9.8 or 10 when it makes the math cleaner).

## The Roadmap

| Ch | The Broken Mechanic | The Physics Fix |
|---|---|---|
| 1 | Objects fall at constant speed | Gravity as acceleration |
| 2 | Cannonball goes straight | Projectile motion (2D) |
| 3 | Crates slide forever | Forces, friction, Newton's laws |
| 4 | Ball passes through wall | Collision detection and response |
| 5 | Rope is a stiff rod | Pendulum motion |
| 6 | Objects teleport down slopes | Inclined plane forces |
| 7 | Trampoline has no bounce | Springs and Hooke's law |
| 8 | Wheels slide, don't roll | Rotational physics |
| 9 | Boats sink like rocks | Buoyancy and density |
| 10 | Moons fly away | Orbital mechanics |
| 11 | Explosions are silent circles | Wave propagation |
| 12 | Engine overheats instantly | Thermodynamics |

Let's drop something.

---

[Chapter 1: Dropping Things →](chapter-01-freefall.md)
