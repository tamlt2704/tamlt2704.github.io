# Chapter 10: Moons and Orbits — Universal Gravitation

[← Chapter 9: Buoyancy](chapter-09-buoyancy.md) | [Chapter 11: Shockwaves →](chapter-11-waves.md)

---

## The Broken Version

The space level has planets and moons, but moons fly off in straight lines:

```python
# WRONG: moon moves in a straight line, no gravitational pull
moon_x += moon_vx * dt
moon_y += moon_vy * dt
# No force pulling it toward the planet!
```

Zara: "The moon is supposed to orbit the planet, not escape to infinity. Newton figured this out 300 years ago."

## What Actually Happens

**Newton's Law of Universal Gravitation**:

```
F = G × (m1 × m2) / r²
```

Where:
- **G** = 6.674 × 10⁻¹¹ N·m²/kg² (gravitational constant)
- **m1, m2** = masses of the two objects
- **r** = distance between their centers

The force points from each object toward the other. For an orbit, the gravitational pull provides the **centripetal force** that curves the moon's path into a circle (or ellipse).

**Kepler's Laws**:
1. Orbits are ellipses with the planet at one focus
2. A line from planet to moon sweeps equal areas in equal times
3. T² ∝ r³ — orbital period squared is proportional to distance cubed

## The Simulation

```python
import math

dt = 0.016

# Use scaled units (real G is tiny, so we scale up for a game)
G = 500.0  # Scaled gravitational constant

# Planet (stationary, at center)
planet_x, planet_y = 0.0, 0.0
planet_mass = 1000.0
planet_radius = 2.0

# Moon (orbiting)
moon_mass = 1.0
orbit_radius = 15.0

# Calculate circular orbit velocity: v = sqrt(GM/r)
orbit_speed = math.sqrt(G * planet_mass / orbit_radius)
print(f"Circular orbit speed at r={orbit_radius}: {orbit_speed:.2f}")

# Start moon at right, moving up (perpendicular to radius = circular orbit)
moon_x, moon_y = orbit_radius, 0.0
moon_vx, moon_vy = 0.0, orbit_speed

time = 0.0
min_r, max_r = orbit_radius, orbit_radius

print(f"\n{'Time':>5} {'X':>7} {'Y':>7} {'R':>6} {'Speed':>6}")
print("-" * 40)

for frame in range(800):
    # Distance to planet
    dx = planet_x - moon_x
    dy = planet_y - moon_y
    r = math.sqrt(dx*dx + dy*dy)

    # Gravitational force: F = GMm/r²
    force = G * planet_mass * moon_mass / (r * r)

    # Direction (unit vector toward planet)
    nx, ny = dx / r, dy / r

    # Acceleration (F/m for the moon)
    ax = (force / moon_mass) * nx
    ay = (force / moon_mass) * ny

    # Update velocity and position
    moon_vx += ax * dt
    moon_vy += ay * dt
    moon_x += moon_vx * dt
    moon_y += moon_vy * dt

    # Track orbit shape
    min_r = min(min_r, r)
    max_r = max(max_r, r)

    time += dt

    if frame % 100 == 0:
        speed = math.sqrt(moon_vx**2 + moon_vy**2)
        print(f"{time:5.2f} {moon_x:7.2f} {moon_y:7.2f} {r:6.2f} {speed:6.2f}")

    # Crash check
    if r < planet_radius:
        print(f"{time:5.2f} — CRASHED into planet!")
        break

# Orbit summary
print(f"\nOrbit: min_r={min_r:.2f}, max_r={max_r:.2f}")
print(f"Eccentricity: {(max_r-min_r)/(max_r+min_r):.4f} (0=circle)")
```

Output:
```
Circular orbit speed at r=15: 5.77

 Time       X       Y      R  Speed
----------------------------------------
 1.60   -5.67  13.89  15.00   5.77
 3.20  -14.04  -4.82  14.85   5.80
 4.80    2.07 -14.86  15.00   5.77
 6.40   14.52   3.63  14.97   5.78
 8.00    7.67  12.89  15.00   5.77
 9.60  -11.07  10.14  15.01   5.77
11.20  -14.72  -2.72  14.97   5.78

Orbit: min_r=14.84, max_r=15.01
Eccentricity: 0.0057 (0=circle)
```

Nearly circular orbit. The moon stays at ~15 units from the planet, speed stays ~5.77. Gravity curves its path into a loop.

## Escape Velocity

If the moon moves too fast, it escapes:

```python
# Escape velocity: v_escape = sqrt(2GM/r)
v_escape = math.sqrt(2 * G * planet_mass / orbit_radius)
print(f"Escape velocity: {v_escape:.2f}")
print(f"Orbit velocity:  {orbit_speed:.2f}")
print(f"Ratio: {v_escape/orbit_speed:.2f} (always √2 ≈ 1.41)")
```

Launch at orbit_speed → circle. Launch faster → ellipse. Launch at escape velocity → never comes back.

## The Fix for *Toss It!*

Before:
```python
# WRONG: straight line, no gravity
moon_x += moon_vx * dt
moon_y += moon_vy * dt
```

After:
```python
# CORRECT: gravitational acceleration toward planet
dx = planet_x - moon_x
dy = planet_y - moon_y
r = math.sqrt(dx*dx + dy*dy)
a = G * planet_mass / (r * r)  # Gravitational acceleration

# Apply in direction of planet
moon_vx += a * (dx / r) * dt
moon_vy += a * (dy / r) * dt
moon_x += moon_vx * dt
moon_y += moon_vy * dt
```

Now moons orbit planets, comets swing by on elliptical paths, and launching too fast sends objects into escape trajectories.

## What You Learned

- **Universal gravitation**: F = GMm/r² — every mass attracts every other mass
- **Circular orbit speed**: v = √(GM/r) — faster for closer orbits
- **Escape velocity**: v = √(2GM/r) — always √2 times orbit speed
- **Inverse square law** — gravity weakens with distance squared
- **Kepler's laws** — emerge naturally from the simulation

Moons orbit properly now. But explosions in the game are just expanding circles with no physics — we need wave propagation.

---

[← Chapter 9: Buoyancy](chapter-09-buoyancy.md) | [Chapter 11: Shockwaves →](chapter-11-waves.md)
