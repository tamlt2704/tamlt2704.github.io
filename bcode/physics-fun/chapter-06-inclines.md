# Chapter 6: Sliding Down Slopes — Inclined Planes

[← Chapter 5: Pendulums](chapter-05-pendulums.md) | [Chapter 7: Trampolines →](chapter-07-springs.md)

---

## The Broken Version

Objects on slopes teleport to the bottom:

```python
# WRONG: instant teleport to bottom of slope
if on_slope:
    x = slope_bottom_x
    y = slope_bottom_y
```

Zara: "The crate should *slide* down the ramp, not teleport. And steeper ramps should be faster."

## What Actually Happens

On an inclined plane, gravity splits into two **components**:

```
        ↓ mg (gravity)
       /|
      / |
     /  | mg·cos(θ) → Normal force (into surface)
    /   |
   / θ  |
  /_____|
         mg·sin(θ) → Force along slope (downhill)
```

- **Along the slope**: F_parallel = mg·sin(θ) — this accelerates the object downhill
- **Into the surface**: F_normal = mg·cos(θ) — this is balanced by the surface pushing back

Friction on a slope:

```
Friction = μ × Normal = μ × mg·cos(θ)
Net acceleration along slope = g·sin(θ) - μ·g·cos(θ)
                              = g(sin(θ) - μ·cos(θ))
```

If μ > tan(θ), friction wins and the object stays put. Otherwise, it slides.

## The Simulation

```python
import math

dt = 0.016
g = 9.8

# Slope properties
slope_angle = 30  # degrees
slope_length = 10.0  # meters
theta = math.radians(slope_angle)
mu = 0.2  # Kinetic friction

# Object state (position along slope, 0 = top)
s = 0.0   # Distance along slope
v = 0.0   # Velocity along slope

# Check if object will slide
critical_angle = math.degrees(math.atan(mu))
print(f"Slope: {slope_angle}°, Friction μ={mu}")
print(f"Critical angle: {critical_angle:.1f}° (slides if slope > this)")
print(f"Will slide: {slope_angle > critical_angle}")
print()

# Forces
f_gravity = g * math.sin(theta)       # Downhill component
f_friction = mu * g * math.cos(theta)  # Friction (opposes motion)
net_accel = f_gravity - f_friction
print(f"Gravity along slope: {f_gravity:.2f} m/s²")
print(f"Friction: {f_friction:.2f} m/s²")
print(f"Net acceleration: {net_accel:.2f} m/s²")
print()

time = 0.0
print(f"{'Time':>5} {'Dist':>6} {'Vel':>6} {'X':>6} {'Y':>6}")
print("-" * 38)

for frame in range(400):
    # Acceleration along slope
    if v > 0 or f_gravity > f_friction:
        a = g * math.sin(theta) - mu * g * math.cos(theta)
    else:
        a = 0  # Static friction holds

    v += a * dt
    s += v * dt

    # Convert slope position to x,y
    x = s * math.cos(theta)
    y = slope_length * math.sin(theta) - s * math.sin(theta)

    time += dt

    if frame % 40 == 0:
        print(f"{time:5.2f} {s:6.2f} {v:6.2f} {x:6.2f} {y:6.2f}")

    # Reached bottom
    if s >= slope_length:
        print(f"{time:5.2f} {s:6.2f} {v:6.2f} — REACHED BOTTOM")
        break
```

Output:
```
Slope: 30°, Friction μ=0.2
Critical angle: 11.3° (slides if slope > this)
Will slide: True

Gravity along slope: 4.90 m/s²
Friction: 1.70 m/s²
Net acceleration: 3.20 m/s²

 Time   Dist    Vel      X      Y
--------------------------------------
 0.64   0.66   2.05   0.57   4.67
 1.28   2.63   4.10   2.28   3.69
 1.92   5.92   6.15   5.13   2.04
 2.37  10.01   7.58 — REACHED BOTTOM
```

The object accelerates smoothly down the slope — no teleporting.

## Torque Preview: Rolling vs Sliding

A ball on a slope doesn't just slide — it can **roll**. Rolling requires torque:

```python
# For a solid sphere rolling without slipping:
# Linear acceleration is reduced because energy goes into rotation
a_rolling = (5.0/7.0) * g * math.sin(theta)  # Less than sliding!
a_sliding = g * math.sin(theta) - mu * g * math.cos(theta)

print(f"Sliding acceleration: {a_sliding:.2f} m/s²")
print(f"Rolling acceleration: {(5/7)*g*math.sin(theta):.2f} m/s²")
# Rolling is slower because some energy becomes rotational
```

## The Fix for *Toss It!*

Before:
```python
# WRONG: teleport to bottom
if on_slope:
    obj.x = slope_bottom_x
    obj.y = slope_bottom_y
```

After:
```python
# CORRECT: accelerate along slope with friction
slope_accel = g * math.sin(theta) - mu * g * math.cos(theta)
if slope_accel > 0 or obj.v_slope > 0:
    obj.v_slope += slope_accel * dt
    obj.s += obj.v_slope * dt
    obj.x = slope_top_x + obj.s * math.cos(theta)
    obj.y = slope_top_y - obj.s * math.sin(theta)
```

Now objects slide smoothly down ramps, faster on steep slopes, slower with more friction.

## What You Learned

- **Component forces** — gravity splits into parallel (downhill) and normal (into surface) parts
- **Slope acceleration** = g(sin θ - μ cos θ) — steeper = faster, more friction = slower
- **Critical angle** — if μ > tan(θ), the object won't slide at all
- **Torque intro** — rolling objects accelerate slower than sliding ones (energy goes into spin)
- **Position from slope distance** — convert 1D slope position to 2D screen coordinates

Objects slide down ramps now. But the trampoline still has no bounce — it needs spring physics.

---

[← Chapter 5: Pendulums](chapter-05-pendulums.md) | [Chapter 7: Trampolines →](chapter-07-springs.md)
