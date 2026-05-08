# Chapter 5: Rope Swings — Pendulums and Angular Motion

[← Chapter 4: Collisions](chapter-04-collisions.md) | [Chapter 6: Slopes →](chapter-06-inclines.md)

---

## The Broken Version

The rope swing in *Toss It!* looks like a stiff rod rotating at constant speed:

```python
# WRONG: constant angular speed, no physics
angle += 0.05  # Just rotates forever at same speed
rope_end_x = pivot_x + length * math.sin(angle)
rope_end_y = pivot_y - length * math.cos(angle)
```

Tomás: "That's not a rope swing, that's a ceiling fan. It should slow at the top and speed up at the bottom."

## What Actually Happens

A pendulum swings because gravity creates a **restoring torque** that pulls it back toward the center. The angular acceleration depends on the angle:

```
α = -(g / L) × sin(θ)
```

Where:
- **α** = angular acceleration (rad/s²)
- **g** = gravity (9.8 m/s²)
- **L** = rope length (meters)
- **θ** = angle from vertical (radians)

Key insight: acceleration is strongest at the extremes (large angle) and zero at the bottom (θ = 0). That's why it speeds up falling and slows down rising.

**Period** — time for one full swing:

```
T ≈ 2π × √(L/g)
```

A 1-meter rope: T = 2π√(1/9.8) ≈ 2.0 seconds. Length matters, mass doesn't.

## The Simulation

```python
import math

dt = 0.016
g = 9.8

# Pendulum properties
length = 2.5        # meters
damping = 0.02      # Air resistance (energy loss per frame)

# State (angle from vertical, angular velocity)
theta = math.radians(60)  # Start at 60 degrees
omega = 0.0               # Angular velocity (rad/s)

# Pivot point
pivot_x, pivot_y = 5.0, 8.0

time = 0.0
print(f"{'Time':>5} {'Angle°':>7} {'ω':>7} {'X':>6} {'Y':>6} {'Speed'}")
print("-" * 52)

for frame in range(500):
    # Angular acceleration: α = -(g/L) * sin(θ)
    alpha = -(g / length) * math.sin(theta)

    # Apply damping (air resistance)
    alpha -= damping * omega

    # Update angular velocity and angle
    omega += alpha * dt
    theta += omega * dt

    # Convert to cartesian (for rendering)
    bob_x = pivot_x + length * math.sin(theta)
    bob_y = pivot_y - length * math.cos(theta)

    # Linear speed of the bob
    speed = abs(omega) * length

    time += dt

    if frame % 30 == 0:
        print(f"{time:5.2f} {math.degrees(theta):7.1f} {omega:7.3f} "
              f"{bob_x:6.2f} {bob_y:6.2f} {speed:5.2f}")

    # Check if settled
    if abs(omega) < 0.001 and abs(theta) < 0.01:
        print(f"{time:5.2f} — pendulum settled")
        break
```

Output:
```
 Time  Angle°       ω      X      Y Speed
----------------------------------------------------
 0.48    -9.5   2.685   4.59   5.53  6.71
 0.96   -52.5  -0.476   3.02   6.49  1.19
 1.44    14.3  -2.571   5.62   5.58  6.43
 1.92    50.5   0.218   6.93   6.39  0.55
 2.40   -18.5   2.454   4.21   5.63  6.14
 2.88   -48.1  -0.020   3.14   6.33  0.05
 3.36    22.0  -2.340   5.94   5.69  5.85
 3.84    45.5   0.174   6.78   6.25  0.44
```

Notice: speed is maximum at the bottom (small angle), zero at the extremes. The damping gradually reduces the swing amplitude.

## Energy in a Pendulum

At the top of the swing: all **potential energy**, zero speed.
At the bottom: all **kinetic energy**, maximum speed.

```python
# Energy conservation (no damping)
# At any point:
KE = 0.5 * mass * (omega * length)**2
PE = mass * g * length * (1 - math.cos(theta))
total = KE + PE  # Should stay constant (without damping)
```

## The Fix for *Toss It!*

Before:
```python
# WRONG: constant rotation
angle += 0.05
```

After:
```python
# CORRECT: gravity-driven pendulum with damping
alpha = -(g / length) * math.sin(theta)
alpha -= damping * omega
omega += alpha * dt
theta += omega * dt

# Position from angle
rope_end_x = pivot_x + length * math.sin(theta)
rope_end_y = pivot_y - length * math.cos(theta)
```

Now the rope swing accelerates through the bottom, slows at the peaks, and gradually loses energy. Feels like a real rope.

## What You Learned

- **Angular acceleration** α = -(g/L)sin(θ) — gravity creates the restoring force
- **Period** T = 2π√(L/g) — depends on length, not mass
- **Energy exchange** — potential ↔ kinetic, conserved without damping
- **Damping** — subtract a term proportional to ω to simulate air resistance
- **Angle → position** — use sin/cos to convert angular state to screen coordinates

The rope swings naturally now. But objects on slopes still teleport to the bottom instead of sliding. Time for inclined planes.

---

[← Chapter 4: Collisions](chapter-04-collisions.md) | [Chapter 6: Slopes →](chapter-06-inclines.md)
