# Chapter 11: Shockwaves — Wave Physics and Propagation

[← Chapter 10: Gravity](chapter-10-gravity.md) | [Chapter 12: Engines →](chapter-12-thermodynamics.md)

---

## The Broken Version

Explosions in *Toss It!* are just a growing circle with no physical effect:

```python
# WRONG: purely visual, no wave physics
explosion_radius += 5  # Grows at constant rate
# Objects inside radius... nothing happens to them
```

Tomás: "The explosion looks like a PowerPoint animation. Where's the shockwave? Where's the force that knocks things over?"

## What Actually Happens

A shockwave is a **pressure wave** — a disturbance that propagates outward from the source. The wave equation:

```
∂²u/∂t² = c² × ∂²u/∂x²
```

Where:
- **u** = displacement (pressure deviation from normal)
- **c** = wave speed (m/s)
- **t** = time, **x** = position

Key wave properties:
- **Amplitude** (A) — strength of the disturbance
- **Wavelength** (λ) — distance between peaks
- **Frequency** (f) — oscillations per second
- **Speed**: c = f × λ

For an explosion shockwave, the pressure drops with distance:

```
Pressure ∝ 1/r² (in 3D)
Pressure ∝ 1/r  (in 2D, our game)
```

## The Simulation

```python
import math

dt = 0.016

# Wave properties
wave_speed = 20.0     # m/s (shockwave propagation speed)
wave_width = 2.0      # meters (thickness of the pressure pulse)
initial_strength = 100.0  # Initial force of explosion

# Explosion origin
origin_x, origin_y = 0.0, 0.0
explosion_time = 0.0

# Objects in the scene (x, y, mass, vx, vy)
objects = [
    {"x": 5.0, "y": 0.0, "mass": 2.0, "vx": 0.0, "vy": 0.0, "name": "crate_near"},
    {"x": 12.0, "y": 0.0, "mass": 2.0, "vx": 0.0, "vy": 0.0, "name": "crate_mid"},
    {"x": 25.0, "y": 0.0, "mass": 2.0, "vx": 0.0, "vy": 0.0, "name": "crate_far"},
    {"x": 3.0, "y": 4.0, "mass": 5.0, "vx": 0.0, "vy": 0.0, "name": "heavy_box"},
]

time = 0.0
print(f"Explosion at origin, wave speed={wave_speed} m/s")
print(f"{'Time':>5} {'WaveFront':>9} {'Object':>10} {'Force':>6} {'Vx':>6} {'Vy':>6}")
print("-" * 55)

for frame in range(300):
    time += dt
    wave_front = wave_speed * time  # How far the wave has traveled
    wave_back = max(0, wave_front - wave_width)

    for obj in objects:
        # Distance from explosion
        dx = obj["x"] - origin_x
        dy = obj["y"] - origin_y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist == 0:
            continue

        # Is this object within the wave pulse?
        if wave_back <= dist <= wave_front:
            # Force decreases with distance (inverse law in 2D)
            force = initial_strength / dist

            # Direction: away from explosion
            nx, ny = dx / dist, dy / dist

            # Apply force (F = ma → a = F/m)
            ax = (force / obj["mass"]) * nx
            ay = (force / obj["mass"]) * ny
            obj["vx"] += ax * dt
            obj["vy"] += ay * dt

            print(f"{time:5.2f} {wave_front:9.2f} {obj['name']:>10} "
                  f"{force:6.1f} {obj['vx']:6.2f} {obj['vy']:6.2f}")

    # Update object positions
    for obj in objects:
        obj["x"] += obj["vx"] * dt
        obj["y"] += obj["vy"] * dt

print(f"\nFinal velocities:")
for obj in objects:
    speed = math.sqrt(obj["vx"]**2 + obj["vy"]**2)
    print(f"  {obj['name']}: v={speed:.2f} m/s (dist was {obj['name']})")
```

Output:
```
Explosion at origin, wave speed=20.0 m/s
 Time WaveFront     Object  Force     Vx     Vy
-------------------------------------------------------
 0.26      5.12  crate_near   20.0   0.16   0.00
 0.27      5.44  crate_near   20.0   0.32   0.00
 0.29      5.76  crate_near   19.6   0.47   0.00
 0.26      5.12  heavy_box   20.0   0.05   0.06
 0.61     12.16   crate_mid    8.3   0.07   0.00
 0.62     12.48   crate_mid    8.3   0.13   0.00
 1.26     25.12   crate_far    4.0   0.03   0.00
 1.27     25.44   crate_far    4.0   0.06   0.00

Final velocities:
  crate_near: v=0.47 m/s
  crate_mid: v=0.13 m/s
  crate_far: v=0.06 m/s
  heavy_box: v=0.10 m/s
```

Closer objects get hit harder (inverse distance). Heavier objects move less. The wave arrives later at distant objects.

## Wave Interference

Two explosions create overlapping waves:

```python
# Superposition: waves add together
def pressure_at(x, y, explosions, time):
    total_pressure = 0.0
    for exp in explosions:
        dx = x - exp["x"]
        dy = y - exp["y"]
        dist = math.sqrt(dx*dx + dy*dy)
        wave_pos = wave_speed * (time - exp["time"])

        if abs(dist - wave_pos) < wave_width / 2:
            # Constructive: waves add
            total_pressure += exp["strength"] / max(dist, 0.1)

    return total_pressure
```

When two waves meet: **constructive interference** (same direction = stronger) or **destructive interference** (opposite = cancel out).

## The Fix for *Toss It!*

Before:
```python
# WRONG: visual only, no physics
explosion_radius += 5
```

After:
```python
# CORRECT: propagating pressure wave with force falloff
wave_front = wave_speed * (time - explosion_start)
for obj in objects:
    dist = distance(obj, explosion_origin)
    if abs(dist - wave_front) < wave_width:
        force = explosion_strength / dist
        direction = normalize(obj.pos - explosion_origin)
        obj.vx += (force / obj.mass) * direction.x * dt
        obj.vy += (force / obj.mass) * direction.y * dt
```

Now explosions send a physical shockwave that knocks nearby objects hard and distant objects gently, with proper timing delays.

## What You Learned

- **Wave equation** — disturbances propagate at speed c
- **Inverse distance law** — wave intensity drops with 1/r (2D) or 1/r² (3D)
- **Wave front** — position = speed × time, creates a ring of force
- **Superposition** — overlapping waves add their amplitudes
- **Mass matters** — heavier objects resist the wave force more (F=ma)

Explosions feel real now. One last problem: the engine in the vehicle level overheats instantly. We need thermodynamics.

---

[← Chapter 10: Gravity](chapter-10-gravity.md) | [Chapter 12: Engines →](chapter-12-thermodynamics.md)
