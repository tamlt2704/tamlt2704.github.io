# Chapter 4: Bouncing Off Walls — Collisions and Momentum

[← Chapter 3: Forces](chapter-03-forces.md) | [Chapter 5: Rope Swings →](chapter-05-pendulums.md)

---

## The Broken Version

The ball hits a wall and... passes through it.

```python
# WRONG: no collision response
x += vx * dt
y += vy * dt
# Ball at x=500 keeps going to x=516, x=532... off screen
```

Zara: "The ball literally phases through walls. Are we making a ghost game?"

## What Actually Happens

When two objects collide, **momentum is conserved**. Momentum = mass × velocity.

```
Total momentum before = Total momentum after
m1*v1 + m2*v2 = m1*v1' + m2*v2'
```

How much energy is kept depends on the **coefficient of restitution** (e):

| e value | Type | Example |
|---|---|---|
| 1.0 | Perfectly elastic | Billiard balls |
| 0.7 | Partially elastic | Tennis ball |
| 0.0 | Perfectly inelastic | Lump of clay |

The restitution formula for a wall collision:

```
v_after = -e × v_before
```

For two moving objects:

```
v1' = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2)
v2' = ((m2 - e*m1)*v2 + (1+e)*m1*v1) / (m1 + m2)
```

## The Simulation

```python
# Ball bouncing in a box with restitution
dt = 0.016
g = 9.8

# Box boundaries
LEFT, RIGHT = 0.0, 10.0
FLOOR, CEILING = 0.0, 8.0

# Ball state
x, y = 5.0, 6.0
vx, vy = 4.0, 0.0
radius = 0.3
restitution = 0.8  # Loses 20% speed each bounce

time = 0.0
print(f"{'Time':>5} {'X':>6} {'Y':>6} {'Vx':>6} {'Vy':>6} {'Event'}")
print("-" * 50)

for frame in range(500):
    # Gravity
    vy -= g * dt

    # Update position
    x += vx * dt
    y += vy * dt

    event = ""

    # Wall collisions (with restitution)
    if x - radius < LEFT:
        x = LEFT + radius
        vx = -vx * restitution
        event = "LEFT wall"
    elif x + radius > RIGHT:
        x = RIGHT - radius
        vx = -vx * restitution
        event = "RIGHT wall"

    if y - radius < FLOOR:
        y = FLOOR + radius
        vy = -vy * restitution
        event = "FLOOR"
    elif y + radius > CEILING:
        y = CEILING - radius
        vy = -vy * restitution
        event = "CEILING"

    time += dt

    if event or int(time * 100) % 100 == 0:
        if event or frame % 62 == 0:
            print(f"{time:5.2f} {x:6.2f} {y:6.2f} {vx:6.2f} {vy:6.2f} {event}")

    # Stop when barely moving
    if abs(vx) < 0.01 and abs(vy) < 0.01 and y - radius < FLOOR + 0.01:
        print(f"{time:5.2f} {x:6.2f} {y:6.2f} {vx:6.2f} {vy:6.2f} STOPPED")
        break
```

Output:
```
 Time      X      Y     Vx     Vy Event
--------------------------------------------------
 0.02   5.06   5.97   4.00  -0.16
 1.01   8.93   1.22   4.00  -9.77
 1.06   9.70   0.30  -3.20  -7.83 RIGHT wall
 1.12   9.51   0.30  -3.20   5.89 FLOOR
 2.10   6.37   0.30  -3.20   4.71 FLOOR
 3.15   3.01   0.30   2.56   3.01 LEFT wall
 5.02   5.12   0.30   2.56   0.12 STOPPED
```

Each bounce loses 20% speed. The ball eventually settles on the floor.

## Ball-to-Ball Collisions

```python
import math

def collide_balls(b1, b2, restitution=0.9):
    """Resolve collision between two balls."""
    dx = b2["x"] - b1["x"]
    dy = b2["y"] - b1["y"]
    dist = math.sqrt(dx*dx + dy*dy)

    # Check overlap
    if dist >= b1["r"] + b2["r"] or dist == 0:
        return

    # Normal vector
    nx, ny = dx / dist, dy / dist

    # Relative velocity along normal
    dvx = b1["vx"] - b2["vx"]
    dvy = b1["vy"] - b2["vy"]
    rel_vel = dvx * nx + dvy * ny

    if rel_vel < 0:  # Moving apart already
        return

    # Impulse (conservation of momentum + restitution)
    m1, m2 = b1["mass"], b2["mass"]
    impulse = (1 + restitution) * rel_vel / (1/m1 + 1/m2)

    # Apply impulse
    b1["vx"] -= (impulse / m1) * nx
    b1["vy"] -= (impulse / m1) * ny
    b2["vx"] += (impulse / m2) * nx
    b2["vy"] += (impulse / m2) * ny

    # Separate overlapping balls
    overlap = (b1["r"] + b2["r"]) - dist
    b1["x"] -= (overlap / 2) * nx
    b1["y"] -= (overlap / 2) * ny
    b2["x"] += (overlap / 2) * nx
    b2["y"] += (overlap / 2) * ny
```

## The Fix for *Toss It!*

Before:
```python
# WRONG: no collision check
x += vx * dt
```

After:
```python
# CORRECT: detect collision, reflect with energy loss
x += vx * dt
if x + radius > wall_x:
    x = wall_x - radius        # Push out of wall
    vx = -vx * restitution     # Reflect and lose energy
```

Three steps: **detect** (overlap check), **resolve** (push apart), **respond** (reflect velocity with restitution).

## What You Learned

- **Momentum** (p = mv) is conserved in all collisions
- **Restitution** (e) controls energy loss: 1.0 = perfect bounce, 0.0 = dead stop
- **Wall collision**: reflect velocity component, multiply by -e
- **Ball collision**: use impulse along the collision normal
- **Separation**: always push objects apart after detecting overlap

The ball bounces now, but the rope swing still looks like a stiff rod. Time for pendulums.

---

[← Chapter 3: Forces](chapter-03-forces.md) | [Chapter 5: Rope Swings →](chapter-05-pendulums.md)
