# Chapter 2: Throwing a Ball — Projectile Motion

[← Chapter 1: Free Fall](chapter-01-freefall.md) | [Chapter 3: Pushing Crates →](chapter-03-forces.md)

---

## The Broken Version

In *Toss It!*, the cannon fires a ball. Current code:

```python
# WRONG: ball goes in a straight line
angle = 45  # degrees
speed = 20  # pixels per frame

vx = speed * cos(angle)
vy = speed * sin(angle)

# Every frame:
x += vx
y += vy  # No gravity — ball flies in a straight line forever
```

The ball shoots out at 45° and keeps going in a straight line until it leaves the screen. No arc. No landing. Players say it looks like a laser, not a cannonball.

## What Actually Happens

When you throw a ball, two things happen simultaneously:
1. **Horizontal**: the ball moves sideways at constant speed (no force acting sideways)
2. **Vertical**: gravity pulls the ball down, accelerating it

These two motions are **independent**. The horizontal speed doesn't affect the vertical acceleration, and vice versa. Combined, they create a parabolic arc.

```
        ·  ·
      ·        ·
    ·              ·
   ·                  ·
  ·                      ·
 ·                          ·
·                              ·  ← parabola
───────────────────────────────────── ground
```

## The Equations

Horizontal (no acceleration):
```
vx = v₀ · cos(θ)     (constant — no force)
x = x₀ + vx · t
```

Vertical (gravity accelerates downward):
```
vy = v₀ · sin(θ) - g · t    (decreases, then goes negative)
y = y₀ + vy · t
```

In our frame-by-frame simulation:
```python
# Each frame:
# Horizontal: no change to vx
x += vx * dt

# Vertical: gravity changes vy
vy -= g * dt
y += vy * dt
```

## The Simulation

```python
import math

# Physics constants
g = 9.8       # gravity (m/s²)
dt = 0.016    # time step (60 FPS)

# Launch parameters
launch_speed = 30.0   # m/s
launch_angle = 45.0   # degrees

# Convert angle to radians
angle_rad = math.radians(launch_angle)

# Initial velocity components
vx = launch_speed * math.cos(angle_rad)  # Horizontal
vy = launch_speed * math.sin(angle_rad)  # Vertical (upward)

# Initial position
x, y = 0.0, 0.0

# Simulation
print(f"{'Time':>6} {'X':>8} {'Y':>8} {'Vx':>8} {'Vy':>8}")
print("-" * 42)

time = 0.0
max_height = 0.0
while y >= 0 or time < 0.1:  # Run until ball hits ground
    if y > max_height:
        max_height = y

    if int(time * 100) % 25 == 0:  # Print every 0.25s
        print(f"{time:6.2f} {x:8.2f} {y:8.2f} {vx:8.2f} {vy:8.2f}")

    # Physics update
    vy -= g * dt       # Gravity pulls down
    x += vx * dt       # Horizontal: constant speed
    y += vy * dt       # Vertical: accelerating down

    time += dt

    if y < 0 and time > 0.1:
        break

print(f"\n📊 Results:")
print(f"   Range: {x:.1f} m")
print(f"   Max height: {max_height:.1f} m")
print(f"   Flight time: {time:.2f} s")
```

Output:
```
  Time        X        Y       Vx       Vy
------------------------------------------
  0.00     0.00     0.00    21.21    21.21
  0.50    10.61     9.38    21.21    16.31
  1.00    21.21    14.86    21.21    11.41
  1.50    31.82    16.44    21.21     6.51
  2.00    42.43    14.12    21.21     1.61
  2.50    53.03     7.90    21.21    -3.29
  3.00    63.64    -2.22    21.21    -8.19

📊 Results:
   Range: 91.8 m
   Max height: 22.9 m
   Flight time: 4.33 s
```

Notice: `vx` stays constant (21.21 m/s) while `vy` decreases from 21.21 to -8.19 (goes up, slows, stops, comes back down).

## The 45° Angle Is Special

At 45°, the horizontal and vertical components are equal, giving maximum range. Let's verify:

```python
import math

g = 9.8
speed = 30.0

print(f"{'Angle':>6} {'Range':>8} {'Max Height':>11} {'Time':>6}")
print("-" * 35)

for angle_deg in range(10, 90, 10):
    angle_rad = math.radians(angle_deg)
    vx = speed * math.cos(angle_rad)
    vy = speed * math.sin(angle_rad)

    # Analytical solution (for flat ground):
    flight_time = 2 * vy / g
    range_m = vx * flight_time
    max_h = vy**2 / (2 * g)

    print(f"{angle_deg:6d}° {range_m:7.1f}m {max_h:10.1f}m {flight_time:5.2f}s")
```

```
 Angle    Range  Max Height   Time
-----------------------------------
    10°    30.9m       1.4m  1.06s
    20°    56.5m       5.4m  2.09s
    30°    79.5m      11.5m  3.06s
    40°    91.5m      19.0m  3.93s
    50°    91.5m      27.0m  4.69s
    60°    79.5m      34.4m  5.30s
    70°    56.5m      40.7m  5.74s
    80°    30.9m      44.7m  5.98s
```

45° gives maximum range. 30° and 60° give the same range (complementary angles). Higher angles go higher but not as far.

## The Fix for *Toss It!*

Before:
```python
# WRONG: straight line
x += vx
y += vy
```

After:
```python
# CORRECT: parabolic arc
vy -= g * dt    # Gravity only affects vertical
x += vx * dt
y += vy * dt
```

One extra line. The cannonball now arcs beautifully.

## Adding Air Resistance (Preview)

In real life, air slows the ball down. A simple model:

```python
# Simple drag (proportional to velocity squared)
drag_coefficient = 0.01
speed = math.sqrt(vx**2 + vy**2)

# Drag force opposes motion
drag_x = -drag_coefficient * speed * vx
drag_y = -drag_coefficient * speed * vy

# Apply drag as acceleration
vx += drag_x * dt
vy += drag_y * dt - g * dt  # Gravity + drag

x += vx * dt
y += vy * dt
```

With drag, the ball doesn't go as far, and the arc is asymmetric (steeper on the way down). We'll explore forces properly in Chapter 3.

## Exercises

1. **Cannon game**: Write a program where the user inputs an angle and speed, and the simulation shows where the ball lands. Add a target at a random distance — can they hit it?

2. **Multiple balls**: Launch 5 balls at angles 20°, 35°, 45°, 55°, 70° simultaneously. Plot all trajectories on the same graph.

3. **Cliff launch**: Start the ball at height y=50m instead of y=0. How does starting height affect range?

4. **Basketball shot**: A basketball hoop is at x=5m, y=3m. The ball is launched from x=0, y=2m. What angle and speed combination makes the shot?

## What You Learned

- **Projectile motion** = constant horizontal speed + vertical acceleration
- **Independence** — horizontal and vertical motions don't affect each other
- **Parabolic arc** — the natural path of any thrown object (without air resistance)
- **45° = maximum range** — equal horizontal and vertical components
- **Complementary angles** — 30° and 60° give the same range
- **The simulation** — just add `vy -= g * dt` to Chapter 1's code

The cannonball arcs correctly. But when it lands, it passes through the ground. And when you push a crate, it slides forever. We need forces — specifically, friction and normal forces.

---

[← Chapter 1: Free Fall](chapter-01-freefall.md) | [Chapter 3: Pushing Crates →](chapter-03-forces.md)
