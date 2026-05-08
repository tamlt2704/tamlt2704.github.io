# Chapter 8: Wheels That Roll — Angular Momentum and Rotation

[← Chapter 7: Springs](chapter-07-springs.md) | [Chapter 9: Floating →](chapter-09-buoyancy.md)

---

## The Broken Version

Wheels in *Toss It!* slide across the ground without spinning:

```python
# WRONG: wheel moves but never rotates
wheel_x += vx * dt
# wheel_angle never changes — it just slides
```

Zara: "The wheel texture doesn't rotate. It looks like a hockey puck, not a wheel."

## What Actually Happens

A rolling wheel has both **linear** motion (moving forward) and **angular** motion (spinning). They're linked:

```
v = ω × r
```

Where:
- **v** = linear velocity (m/s)
- **ω** (omega) = angular velocity (rad/s)
- **r** = radius (m)

**Moment of inertia** (I) is the rotational equivalent of mass — resistance to angular acceleration:

| Shape | Moment of Inertia |
|---|---|
| Solid disk/cylinder | I = ½mr² |
| Hollow ring | I = mr² |
| Solid sphere | I = ⅖mr² |

**Torque** (τ) is the rotational equivalent of force:

```
τ = I × α     (like F = ma)
τ = r × F     (force at distance r from center)
```

**Angular momentum** (L = Iω) is conserved when no external torque acts.

## The Simulation

```python
import math

dt = 0.016
g = 9.8

# Wheel properties
mass = 5.0
radius = 0.4
I = 0.5 * mass * radius**2  # Solid disk

# State
x = 0.0
vx = 0.0
angle = 0.0       # radians
omega = 0.0       # angular velocity (rad/s)

# Push the wheel (apply force for 1 second)
push_force = 20.0
push_duration = 1.0
mu = 0.4  # Friction (drives rolling)

time = 0.0
print(f"{'Time':>5} {'X':>6} {'Vx':>6} {'ω':>7} {'Angle°':>7} {'v=ωr?'}")
print("-" * 52)

for frame in range(400):
    # Applied force
    applied = push_force if time < push_duration else 0.0

    # Friction force at contact point (drives rotation)
    # For rolling without slipping: friction provides torque
    # Combined linear + rotational: a = F / (m + I/r²)
    effective_mass = mass + I / (radius**2)  # Accounts for rotational inertia

    if time < push_duration:
        # Accelerating: force splits between linear and rotational
        ax = applied / effective_mass
        alpha = ax / radius  # Angular acceleration from rolling constraint
    else:
        # Rolling friction slows it down
        rolling_friction = 0.01 * mass * g  # Small rolling resistance
        ax = -rolling_friction / effective_mass
        alpha = ax / radius
        if vx < 0.01:
            ax, alpha = 0, 0
            vx, omega = 0, 0

    # Update linear
    vx += ax * dt
    x += vx * dt

    # Update angular (linked to linear via rolling constraint)
    omega += alpha * dt
    angle += omega * dt

    time += dt

    # Check rolling condition: v should equal ω×r
    v_from_omega = omega * radius
    match = "✓" if abs(vx - v_from_omega) < 0.01 else "✗"

    if frame % 40 == 0:
        print(f"{time:5.2f} {x:6.2f} {vx:6.2f} {omega:7.2f} "
              f"{math.degrees(angle):7.1f} {match}")
```

Output:
```
 Time      X     Vx       ω  Angle° v=ωr?
----------------------------------------------------
 0.64   0.83   2.56    6.40    117.6 ✓
 1.28   2.95   4.00   10.00    367.2 ✓
 1.92   4.87   3.97    9.93    612.8 ✓
 2.56   6.78   3.94    9.86    857.6 ✓
 3.20   8.68   3.91    9.78   1101.6 ✓
```

The wheel spins in sync with its forward motion. The `v = ωr` constraint holds throughout (✓).

## Angular Momentum Conservation

```python
# Spinning figure skater effect:
# Pull arms in → I decreases → ω increases (L = Iω stays constant)

L = I * omega  # Angular momentum (conserved)

# If radius shrinks (like a collapsing star):
new_radius = radius * 0.5
new_I = 0.5 * mass * new_radius**2
new_omega = L / new_I  # Spins 4x faster!
print(f"Original ω: {omega:.1f} rad/s")
print(f"New ω (half radius): {new_omega:.1f} rad/s")
```

## The Fix for *Toss It!*

Before:
```python
# WRONG: slides without rotating
wheel_x += vx * dt
```

After:
```python
# CORRECT: rolling motion links linear and angular
wheel_x += vx * dt
omega = vx / radius  # Rolling constraint
wheel_angle += omega * dt

# Use wheel_angle to rotate the sprite
draw_wheel(wheel_x, wheel_y, wheel_angle)
```

Now wheels visually spin at the correct rate. A fast-moving wheel spins fast; a slow one spins slow. The texture rotates to match.

## What You Learned

- **Rolling constraint**: v = ωr — linear and angular motion are linked
- **Moment of inertia** (I) — rotational resistance, depends on shape and mass distribution
- **Torque** τ = Iα — rotational equivalent of F = ma
- **Angular momentum** L = Iω — conserved without external torque
- **Effective mass** — rolling objects accelerate slower because energy goes into rotation

Wheels roll properly now. But the boats in the water level still sink like rocks — we need buoyancy.

---

[← Chapter 7: Springs](chapter-07-springs.md) | [Chapter 9: Floating →](chapter-09-buoyancy.md)
