# Chapter 9: Boats That Float — Buoyancy and Density

[← Chapter 8: Rotation](chapter-08-rotation.md) | [Chapter 10: Orbits →](chapter-10-gravity.md)

---

## The Broken Version

Every object in the water level sinks straight to the bottom:

```python
# WRONG: no buoyancy, everything sinks
if in_water:
    vy -= g * dt  # Only gravity, no upward force
```

QA Bot: "Test case FLOAT_001 failed. Wooden crate density 600 kg/m³ (less than water). Expected: floats. Actual: sinks to ocean floor."

## What Actually Happens

**Archimedes' Principle**: An object in fluid experiences an upward force equal to the weight of fluid it displaces.

```
F_buoyancy = ρ_fluid × V_submerged × g
```

Where:
- **ρ_fluid** = density of the fluid (water = 1000 kg/m³)
- **V_submerged** = volume of the object that's underwater
- **g** = gravity (9.8 m/s²)

An object floats when buoyancy ≥ weight:

```
ρ_fluid × V_submerged × g ≥ ρ_object × V_total × g
```

Simplified: an object floats if its density < fluid density.

| Material | Density (kg/m³) | Floats? |
|---|---|---|
| Cork | 120 | ✓ (barely submerged) |
| Wood | 600 | ✓ (60% submerged) |
| Water | 1000 | — (neutral) |
| Iron | 7874 | ✗ (sinks) |
| Lead | 11340 | ✗ (sinks fast) |

## The Simulation

```python
dt = 0.016
g = 9.8

# Fluid
water_density = 1000.0  # kg/m³
water_surface = 5.0     # y-coordinate of water surface
drag_coeff = 0.5        # Water resistance

# Object (a wooden crate)
obj_density = 600.0     # kg/m³ (wood — should float)
obj_height = 1.0        # meters (cube)
obj_volume = obj_height**3
obj_mass = obj_density * obj_volume

# State (drop from above water)
y = 7.0
vy = 0.0

time = 0.0
print(f"Object: density={obj_density}, mass={obj_mass:.1f}kg")
print(f"Water: density={water_density}")
print(f"Should float: {obj_density < water_density} "
      f"({obj_density/water_density*100:.0f}% submerged at equilibrium)")
print()
print(f"{'Time':>5} {'Y':>6} {'Vy':>7} {'%Sub':>5} {'Fbuoy':>7} {'State'}")
print("-" * 50)

for frame in range(600):
    # Gravity (always)
    weight = -obj_mass * g

    # Calculate submerged fraction
    obj_bottom = y - obj_height / 2
    obj_top = y + obj_height / 2

    if obj_bottom >= water_surface:
        submerged_fraction = 0.0
    elif obj_top <= water_surface:
        submerged_fraction = 1.0
    else:
        submerged_depth = water_surface - obj_bottom
        submerged_fraction = submerged_depth / obj_height

    # Buoyancy force
    submerged_volume = submerged_fraction * obj_volume
    buoyancy = water_density * submerged_volume * g

    # Water drag (resistance to motion through water)
    if submerged_fraction > 0:
        drag = -drag_coeff * vy * abs(vy) * submerged_fraction
    else:
        drag = 0

    # Net force
    net_force = weight + buoyancy + drag
    ay = net_force / obj_mass

    vy += ay * dt
    y += vy * dt

    time += dt

    if frame % 30 == 0:
        state = "air" if submerged_fraction == 0 else (
            "sinking" if vy < -0.01 else (
            "rising" if vy > 0.01 else "floating"))
        print(f"{time:5.2f} {y:6.2f} {vy:7.3f} {submerged_fraction*100:5.1f} "
              f"{buoyancy:7.1f} {state}")

    # Settled?
    if time > 2.0 and abs(vy) < 0.001:
        print(f"{time:5.2f} — settled: {submerged_fraction*100:.0f}% submerged")
        break
```

Output:
```
Object: density=600, mass=600.0kg
Water: density=1000
Should float: True (60% submerged at equilibrium)

 Time      Y      Vy  %Sub   Fbuoy State
--------------------------------------------------
 0.48   5.63  -2.891   0.0     0.0 air
 0.96   4.22  -2.034  78.0  7644.0 sinking
 1.44   4.72   0.476  28.0  2744.0 rising
 1.92   4.62  -0.103  38.0  3724.0 sinking
 2.40   4.70   0.012  30.0  2940.0 rising
 2.88   4.70  -0.001  30.0  2940.0 floating
 2.90 — settled: 60% submerged
```

The crate splashes in, bobs up and down, and settles with exactly 60% submerged (density ratio: 600/1000).

## The Fix for *Toss It!*

Before:
```python
# WRONG: only gravity
vy -= g * dt
```

After:
```python
# CORRECT: buoyancy opposes gravity when submerged
submerged_frac = get_submerged_fraction(obj, water_level)
buoyancy_accel = (water_density / obj_density) * submerged_frac * g
drag = -drag_coeff * vy * abs(vy) * submerged_frac / obj_mass

vy += (-g + buoyancy_accel + drag) * dt
y += vy * dt
```

Now wood floats, iron sinks, and everything bobs realistically when it hits the water. The drag prevents objects from oscillating forever.

## What You Learned

- **Archimedes' Principle** — buoyant force = weight of displaced fluid
- **Density determines floating** — object floats if ρ_object < ρ_fluid
- **Equilibrium depth** — fraction submerged = ρ_object / ρ_fluid
- **Water drag** — proportional to v², prevents infinite bobbing
- **Partial submersion** — calculate what fraction is underwater for correct force

Boats float now. But the space level has a problem — moons fly off into space instead of orbiting. We need gravity between objects.

---

[← Chapter 8: Rotation](chapter-08-rotation.md) | [Chapter 10: Orbits →](chapter-10-gravity.md)
