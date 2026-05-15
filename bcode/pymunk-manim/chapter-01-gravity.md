# Chapter 1: Gravity & Bouncing

[← Overview](README.md) | [Chapter 2: Multiple Bodies →](chapter-02-bodies.md)

---

## Pymunk Concept: Gravity & Elasticity

Pymunk simulates physics in a `Space`. Gravity is a vector applied every step — `(0, -900)` pulls everything down. Bodies fall until they hit something.

**Elasticity** (restitution) controls bounciness. `1.0` = perfect bounce, `0.0` = dead stop. A static body makes an immovable floor.

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Static floor — never moves
floor_body = space.static_body
floor_shape = pymunk.Segment(floor_body, (-300, -200), (300, -200), 5)
floor_shape.elasticity = 0.8

# Dynamic ball — affected by gravity
mass, radius = 1, 15
moment = pymunk.moment_for_circle(mass, 0, radius)
ball_body = pymunk.Body(mass, moment)
ball_body.position = (0, 200)
ball_shape = pymunk.Circle(ball_body, radius)
ball_shape.elasticity = 0.9

space.add(ball_body, ball_shape, floor_shape)
```

Key points:
- `space.gravity` is a tuple `(x, y)` — negative y means "down"
- `moment_for_circle` calculates rotational inertia from mass and radius
- Static bodies don't need mass or moment — they're infinitely heavy
- Elasticity is per-shape, so different surfaces can bounce differently

## Manim Rendering

The bridge between pymunk and manim is a **scale factor**. Pymunk works in pixels/units; manim's frame is roughly ±7 horizontally. We divide pymunk coordinates by `SCALE = 100`.

`TracedPath` records every position the ball visits, creating a fading trajectory line. We color the ball by speed using `interpolate_color`.

```python
from manim import *

SCALE = 100  # pymunk units → manim units

class GravityBounce(Scene):
    def construct(self):
        # Convert pymunk position to manim coordinates
        def to_manim(pos):
            return np.array([pos[0] / SCALE, pos[1] / SCALE, 0])

        ball_dot = Dot(radius=0.15, color=BLUE)
        trace = TracedPath(ball_dot.get_center,
                           stroke_color=BLUE_A, stroke_width=2)
        floor = Line(LEFT * 3, RIGHT * 3, color=WHITE).shift(DOWN * 2)

        self.add(floor, trace, ball_dot)
        # Update ball_dot position each frame from pymunk
```

The updater pattern: each frame, step the physics, then move the manim Dot to match the pymunk body's position.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class GravityBounce(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        floor_shape = pymunk.Segment(space.static_body, (-300, -200), (300, -200), 5)
        floor_shape.elasticity = 0.8
        mass, radius = 1, 15
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (0, 200)
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.9
        space.add(body, shape, floor_shape)

        dot = Dot(radius=0.15, color=BLUE)
        trace = TracedPath(dot.get_center, stroke_color=BLUE_A, stroke_width=2)
        floor_line = Line(LEFT * 3, RIGHT * 3, color=WHITE).shift(DOWN * 2)
        self.add(floor_line, trace, dot)

        def update_dot(mob, dt):
            for _ in range(10):
                space.step(dt / 10)
            speed = body.velocity.length
            mob.move_to([body.position.x / SCALE, body.position.y / SCALE, 0])
            mob.set_color(interpolate_color(BLUE, RED, min(speed / 800, 1)))

        dot.add_updater(update_dot)
        self.wait(5)
```

**Why 10 sub-steps?** Manim runs at 60 fps (dt ≈ 0.016s). Splitting each frame into 10 physics steps gives smoother, more stable simulation.

## What You Learned

- `space.gravity` sets the global gravity vector for all dynamic bodies
- `elasticity` on shapes controls how much energy is preserved on bounce (0–1)
- Static bodies (`space.static_body`) are immovable walls/floors
- `SCALE = 100` bridges pymunk coordinates to manim's ±7 frame
- `TracedPath` records a mobject's movement as a fading trail
- `interpolate_color` maps a numeric value to a color gradient
- Sub-stepping (multiple `space.step()` per frame) improves simulation stability

---

[← Overview](README.md) | [Chapter 2: Multiple Bodies →](chapter-02-bodies.md)
