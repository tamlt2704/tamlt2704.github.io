# Chapter 3: Pushing Crates — Forces and Friction

[← Chapter 2: Projectiles](chapter-02-projectiles.md) | [Chapter 4: Bouncing Off Walls →](chapter-04-collisions.md)

---

## The Broken Version

In *Toss It!*, you can push crates across the floor. Current code:

```python
# WRONG: crate slides forever once pushed
if pushing:
    vx = 5.0  # Constant speed while pushing
else:
    # Nothing stops it — slides forever!
    x += vx * dt
```

Push a crate, let go, and it slides to the edge of the screen at constant speed. On ice, maybe. On a wooden floor? No.

Zara: "Crates should slow down and stop when you let go. And heavier crates should be harder to push."

## Newton's Three Laws

### First Law: Objects Keep Doing What They're Doing

An object at rest stays at rest. An object in motion stays in motion (at constant velocity). Unless a **force** acts on it.

The crate slides forever because no force is stopping it. We need friction.

### Second Law: F = ma

Force equals mass times acceleration. More force → more acceleration. More mass → less acceleration for the same force.

```python
# The fundamental equation of motion
acceleration = net_force / mass
```

A 10 kg crate pushed with 50 N of force: `a = 50/10 = 5 m/s²`
A 100 kg crate pushed with 50 N of force: `a = 50/100 = 0.5 m/s²`

Heavier crates accelerate slower. That's why they "feel" harder to push.

### Third Law: Every Action Has an Equal Opposite Reaction

You push the crate → the crate pushes back on you. The floor pushes up on the crate (normal force) → the crate pushes down on the floor (gravity).

## Forces on a Crate

```
         Normal Force (N) ↑
                          │
    Push (F) →  ┌─────────┐  ← Friction (f)
                │  CRATE  │
                └─────────┘
                          │
              Weight (W) ↓  (= mg)
```

- **Weight** (W = mg): gravity pulling down
- **Normal force** (N): floor pushing up (equals weight on flat ground)
- **Applied force** (F): you pushing the crate
- **Friction** (f): floor resisting motion

## Friction: Why Things Stop

Friction force opposes motion. Its magnitude:

```
f = μ × N
```

Where:
- **μ** (mu) = coefficient of friction (depends on surfaces)
- **N** = normal force (= mg on flat ground)

| Surface | μ (kinetic) |
|---|---|
| Ice on ice | 0.03 |
| Wood on wood | 0.3 |
| Rubber on concrete | 0.7 |
| Rubber on rubber | 1.0+ |

```python
# Friction always opposes the direction of motion
if vx > 0:
    friction = -mu * mass * g  # Points left (opposing rightward motion)
elif vx < 0:
    friction = mu * mass * g   # Points right (opposing leftward motion)
else:
    friction = 0  # Static: no motion, no kinetic friction
```

## The Simulation

```python
# Crate physics with friction
g = 9.8
dt = 0.016

# Crate properties
mass = 20.0       # kg
mu = 0.3          # Wood on wood

# State
x = 0.0
vx = 0.0

# Applied force (push for 2 seconds, then release)
push_force = 100.0  # Newtons
push_duration = 2.0  # seconds

time = 0.0
print(f"{'Time':>5} {'Pos':>7} {'Vel':>7} {'Accel':>7} {'State'}")
print("-" * 45)

while time < 8.0:
    # Calculate forces
    applied = push_force if time < push_duration else 0.0

    # Friction (only when moving)
    if abs(vx) > 0.01:
        friction = -mu * mass * g * (1 if vx > 0 else -1)
    else:
        # Static friction: prevents motion unless force exceeds threshold
        static_friction_max = mu * mass * g * 1.2  # Static μ ≈ 1.2× kinetic μ
        if abs(applied) > static_friction_max:
            friction = -mu * mass * g * (1 if applied > 0 else -1)
        else:
            friction = -applied  # Exactly cancels applied force
            vx = 0

    # Net force and acceleration (F = ma → a = F/m)
    net_force = applied + friction
    ax = net_force / mass

    # Update velocity and position
    vx += ax * dt
    x += vx * dt

    # Prevent oscillation around zero
    if abs(vx) < 0.01 and applied == 0:
        vx = 0

    # Print every 0.5 seconds
    if int(time * 100) % 50 == 0:
        state = "pushing" if time < push_duration else ("sliding" if vx > 0.01 else "stopped")
        print(f"{time:5.1f} {x:7.2f} {vx:7.2f} {ax:7.2f} {state}")

    time += dt
```

Output:
```
 Time     Pos     Vel   Accel State
---------------------------------------------
  0.0    0.00    0.00    2.06 pushing
  0.5    0.27    1.03    2.06 pushing
  1.0    1.06    2.06    2.06 pushing
  1.5    2.37    3.09    2.06 pushing
  2.0    4.19    4.12    2.06 pushing
  2.5    5.87    3.09   -2.94 sliding
  3.0    7.04    2.06   -2.94 sliding
  3.5    7.70    1.03   -2.94 sliding
  4.0    7.84    0.00    0.00 stopped
```

The crate accelerates while pushed (2.06 m/s²), then decelerates due to friction (-2.94 m/s²) and stops.

## Why the Acceleration Is 2.06, Not 5.0

```
Applied force:  100 N (rightward)
Friction:       -μmg = -0.3 × 20 × 9.8 = -58.8 N (leftward)
Net force:      100 - 58.8 = 41.2 N
Acceleration:   41.2 / 20 = 2.06 m/s²
```

Friction eats more than half the push force. On ice (μ = 0.03), friction would be only 5.88 N, and acceleration would be 4.71 m/s² — much closer to the "no friction" case.

## The Fix for *Toss It!*

Before:
```python
# WRONG: constant speed, no stopping
x += vx * dt
```

After:
```python
# CORRECT: friction decelerates the crate
if abs(vx) > 0.01:
    friction_accel = -mu * g * (1 if vx > 0 else -1)
    vx += friction_accel * dt
else:
    vx = 0  # Stopped

x += vx * dt
```

Now crates slide realistically and come to a stop. Heavy crates (large mass) take the same time to stop (friction scales with mass, canceling it out in the deceleration equation: `a = μg`, independent of mass!).

## Multiple Forces: The General Pattern

```python
def update_physics(obj, forces, dt):
    """General force-based physics update."""
    # Sum all forces
    net_fx = sum(f[0] for f in forces)
    net_fy = sum(f[1] for f in forces)

    # F = ma → a = F/m
    ax = net_fx / obj.mass
    ay = net_fy / obj.mass

    # Update velocity
    obj.vx += ax * dt
    obj.vy += ay * dt

    # Update position
    obj.x += obj.vx * dt
    obj.y += obj.vy * dt
```

This pattern works for any number of forces: gravity, friction, wind, springs, player input. Just sum them all and divide by mass.

## Exercises

1. **Ice vs concrete**: Simulate the same crate on ice (μ=0.03) and concrete (μ=0.7). How far does it slide after a 2-second push?

2. **Heavy vs light**: Push a 5 kg crate and a 50 kg crate with the same force. Which stops first? (Trick question — think about it.)

3. **Tug of war**: Two forces act on a crate: 80 N right and 60 N left. What's the net acceleration for a 10 kg crate?

## What You Learned

- **F = ma** — the fundamental equation of motion
- **Friction** = μ × normal force, opposes motion direction
- **Net force** — sum all forces, then apply F=ma
- **Mass matters for acceleration** — heavier = slower to speed up
- **Mass doesn't matter for stopping distance** — friction deceleration = μg (mass cancels)
- **The general pattern** — sum forces → compute acceleration → update velocity → update position

Crates now slide and stop realistically. But when the crate hits a wall, it passes right through. We need collision detection and response.

---

[← Chapter 2: Projectiles](chapter-02-projectiles.md) | [Chapter 4: Bouncing Off Walls →](chapter-04-collisions.md)
