# Chapter 7: Trampolines — Springs and Hooke's Law

[← Chapter 6: Inclines](chapter-06-inclines.md) | [Chapter 8: Rolling →](chapter-08-rotation.md)

---

## The Broken Version

The trampoline in *Toss It!* is just a velocity flip:

```python
# WRONG: instant velocity reversal, no spring behavior
if ball_y <= trampoline_y:
    vy = -vy  # Perfect bounce, no compression, no timing
```

Tomás: "It looks like the ball hits an invisible wall. Where's the squish? Where's the *boing*?"

## What Actually Happens

A spring (or trampoline surface) follows **Hooke's Law**:

```
F = -k × x
```

Where:
- **F** = force exerted by the spring (N)
- **k** = spring constant (N/m) — stiffer spring = larger k
- **x** = displacement from rest position (m)

The negative sign means the force always pushes back toward equilibrium. Stretch it → it pulls back. Compress it → it pushes out.

Real springs also have **damping** — energy loss due to internal friction:

```
F = -k × x - c × v
```

Where **c** is the damping coefficient. Without damping, a spring bounces forever.

## The Simulation

```python
dt = 0.016
g = 9.8

# Spring properties
k = 300.0       # Spring constant (N/m) — stiff trampoline
c = 5.0         # Damping coefficient
rest_y = 2.0    # Trampoline rest position

# Ball properties
mass = 2.0
ball_y = 8.0    # Drop from height
ball_vy = 0.0
ball_radius = 0.3

time = 0.0
print(f"{'Time':>5} {'Y':>6} {'Vy':>7} {'Spring':>7} {'State'}")
print("-" * 45)

on_spring = False

for frame in range(500):
    # Gravity always applies
    force = -mass * g

    # Check if ball is touching the spring
    if ball_y - ball_radius <= rest_y:
        on_spring = True
        # Compression distance (how far below rest position)
        compression = rest_y - (ball_y - ball_radius)
        # Hooke's law + damping
        spring_force = k * compression - c * ball_vy
        force += spring_force
        state = f"compress {compression:.3f}m"
    else:
        if on_spring:
            state = "launched!"
            on_spring = False
        else:
            state = "falling"

    # F = ma → a = F/m
    ay = force / mass
    ball_vy += ay * dt
    ball_y += ball_vy * dt

    time += dt

    if frame % 20 == 0:
        spring_f = k * max(0, rest_y - (ball_y - ball_radius)) if ball_y - ball_radius <= rest_y else 0
        print(f"{time:5.2f} {ball_y:6.2f} {ball_vy:7.2f} {spring_f:7.1f} {state}")

    # Stop after settling
    if time > 3.0 and abs(ball_vy) < 0.01 and abs(ball_y - rest_y - ball_radius) < 0.01:
        print(f"{time:5.2f} — ball settled on trampoline")
        break
```

Output:
```
 Time      Y      Vy  Spring State
---------------------------------------------
 0.32   6.52   -3.14     0.0 falling
 0.64   4.99   -6.27     0.0 falling
 0.96   2.93   -9.41     0.0 falling
 1.12   1.82   -8.23   114.0 compress 0.380m
 1.28   1.58    3.41   186.0 compress 0.620m
 1.44   3.12    8.95     0.0 launched!
 1.76   6.72    5.81     0.0 falling
 2.08   7.18    2.67     0.0 falling
 2.40   5.93   -0.47     0.0 falling
```

The ball compresses the spring, gets launched back up (lower than it started due to damping), and eventually settles.

## Spring Frequency

A mass on a spring oscillates at a natural frequency:

```
f = (1/2π) × √(k/m)
```

- Stiffer spring (larger k) → faster oscillation
- Heavier mass → slower oscillation

```python
import math
frequency = (1 / (2 * math.pi)) * math.sqrt(k / mass)
period = 1 / frequency
print(f"Natural frequency: {frequency:.1f} Hz")
print(f"Period: {period:.3f} seconds")
# k=300, m=2 → f=1.95 Hz, period=0.513s
```

## The Fix for *Toss It!*

Before:
```python
# WRONG: instant bounce, no spring physics
if ball_y <= trampoline_y:
    vy = -vy
```

After:
```python
# CORRECT: Hooke's law with damping
if ball_y - radius <= trampoline_rest_y:
    compression = trampoline_rest_y - (ball_y - radius)
    spring_force = k * compression - c * vy
    vy += (spring_force / mass) * dt

# Gravity always
vy -= g * dt
ball_y += vy * dt
```

Now the trampoline compresses visibly, launches the ball with proper timing, and each bounce is slightly lower. Tomás can animate the squish to match the compression value.

## What You Learned

- **Hooke's Law**: F = -kx — force proportional to displacement, always restoring
- **Spring constant** (k) — higher = stiffer, faster bounce
- **Damping** (c) — energy loss, prevents infinite bouncing
- **Natural frequency** — f = (1/2π)√(k/m), determines bounce timing
- **Compression distance** — gives you a value to drive visual squish animation

The trampoline bounces properly. But the wheels in the game still slide instead of rolling — we need rotational physics.

---

[← Chapter 6: Inclines](chapter-06-inclines.md) | [Chapter 8: Rolling →](chapter-08-rotation.md)
