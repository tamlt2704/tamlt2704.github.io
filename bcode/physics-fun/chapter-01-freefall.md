# Chapter 1: Dropping Things — Free Fall

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Throwing a Ball →](chapter-02-projectiles.md)

---

## The Broken Version

In *Toss It!*, when you drop an object, it falls like this:

```python
# Current code (WRONG)
y = y - 5  # Move down 5 pixels every frame
```

Every frame, the object moves down by the same amount. It falls at constant speed — like an elevator, not like a rock.

Players notice immediately. "Why does the bowling ball fall like it's in slow motion?" Because constant speed isn't how gravity works.

## What Actually Happens

When you drop something, it **accelerates**. It starts slow and gets faster every moment. That's what makes falling feel like falling — the increasing speed, the sense of urgency.

On Earth, gravity accelerates everything at **9.81 m/s²** (we'll use g = 9.8). This means:

- After 0 seconds: velocity = 0 m/s (just released)
- After 1 second: velocity = 9.8 m/s (falling)
- After 2 seconds: velocity = 19.6 m/s (falling fast)
- After 3 seconds: velocity = 29.4 m/s (falling very fast)

Every second, the velocity increases by 9.8 m/s. That's what "acceleration" means — the rate at which velocity changes.

## The Equations

Two equations describe free fall:

```
velocity = velocity + acceleration × time
position = position + velocity × time
```

Or in physics notation:

```
v = v₀ + g·t
y = y₀ + v·t + ½·g·t²
```

For our simulation, we update every frame (every `dt` seconds):

```
v_new = v_old + g × dt
y_new = y_old + v_new × dt
```

That's it. Two lines of math. Let's code it.

## The Simulation

```python
# Free fall simulation
g = 9.8      # Acceleration due to gravity (m/s²)
dt = 0.016   # Time step (~60 FPS)

# Initial state: object at height 100m, at rest
y = 100.0    # Position (meters above ground)
vy = 0.0     # Velocity (m/s, positive = up)

print(f"{'Time':>6} {'Height':>8} {'Velocity':>10}")
print(f"{'(s)':>6} {'(m)':>8} {'(m/s)':>10}")
print("-" * 28)

time = 0.0
while y > 0:
    print(f"{time:6.2f} {y:8.2f} {vy:10.2f}")

    # Physics update
    vy = vy - g * dt    # Gravity pulls down (negative direction)
    y = y + vy * dt     # Update position

    time += dt

print(f"\n💥 Hit the ground after {time:.2f} seconds")
print(f"   Impact velocity: {abs(vy):.1f} m/s")
```

Output (abbreviated):
```
  Time   Height   Velocity
   (s)      (m)      (m/s)
----------------------------
  0.00   100.00       0.00
  0.50    98.77      -4.90
  1.00    95.08      -9.80
  2.00    80.36     -19.60
  3.00    55.84     -29.40
  4.00    21.52     -39.20
  4.52     0.12     -44.30

💥 Hit the ground after 4.52 seconds
   Impact velocity: 44.3 m/s
```

The object starts slow (0 m/s) and accelerates. By the time it hits the ground, it's moving at 44.3 m/s (about 160 km/h). That's what makes falling dangerous.

## Comparing: Constant Speed vs Acceleration

```python
import time as time_module

g = 9.8
dt = 0.016
frames = 300  # 5 seconds

# Method 1: Constant speed (WRONG)
y_const = 100.0
speed_const = 20.0  # Arbitrary constant speed

# Method 2: Acceleration (CORRECT)
y_accel = 100.0
vy_accel = 0.0

print(f"{'Frame':>6} {'Constant':>10} {'Accelerated':>12}")
for frame in range(0, frames, 30):  # Print every 30 frames (0.5s)
    print(f"{frame:6d} {y_const:10.2f} {y_accel:12.2f}")

    # Simulate 30 frames
    for _ in range(30):
        # Constant speed
        y_const -= speed_const * dt

        # Acceleration
        vy_accel -= g * dt
        y_accel += vy_accel * dt
```

The constant-speed version moves at the same rate forever. The accelerated version starts slow, then overtakes — just like real life.

## Why This Matters for Games

The difference between constant speed and acceleration is the difference between "feels like a game" and "feels like real life." Players can't articulate it, but they feel it:

- **Constant speed**: mechanical, robotic, unsatisfying
- **Acceleration**: natural, weighty, satisfying

This is why every physics engine (Unity, Unreal, Box2D) uses acceleration, not constant speed.

## The Fix for *Toss It!*

Before:
```python
# WRONG: constant speed
y = y - 5
```

After:
```python
# CORRECT: acceleration
vy = vy - g * dt
y = y + vy * dt
```

Two lines. The object now falls realistically.

## Bonus: Different Masses?

Galileo's insight: **all objects fall at the same rate** (ignoring air resistance). A bowling ball and a feather dropped in a vacuum hit the ground at the same time.

```python
# Both use the same g = 9.8 m/s²
# Mass doesn't appear in the equations!
bowling_ball_vy = 0 - g * dt  # Same
feather_vy = 0 - g * dt       # Same
```

Mass matters for forces (Chapter 3), but not for free fall. This surprises people — but it's been experimentally verified since 1971 when astronaut David Scott dropped a hammer and feather on the Moon.

## Exercises

1. **Drop from different heights**: Modify the simulation to drop from 10m, 50m, and 200m. How does impact velocity scale with height?

2. **Different planets**: Mars has g = 3.7 m/s², Moon has g = 1.6 m/s². How long does it take to fall 100m on each?

3. **Terminal velocity** (preview of Chapter 3): In real life, air resistance limits falling speed. Add a simple drag force: `drag = 0.01 * vy * vy`. Subtract drag from the acceleration. What's the maximum speed?

## What You Learned

- **Constant speed ≠ falling** — real objects accelerate
- **g = 9.8 m/s²** — velocity increases by 9.8 m/s every second
- **Two update lines** — `vy += g*dt`, `y += vy*dt`
- **Mass doesn't matter** — all objects fall the same (in vacuum)
- **Euler integration** — update velocity, then position, every frame

The object falls correctly now. But it only falls straight down. What if you throw it sideways?

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Throwing a Ball →](chapter-02-projectiles.md)
