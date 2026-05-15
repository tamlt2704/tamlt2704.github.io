# Chapter 7: Forces & Impulses

[← Chapter 6: Shapes](chapter-06-shapes.md) | [Chapter 8: Friction →](chapter-08-friction.md)

---

## Pymunk Concept: Forces vs Impulses

Forces and impulses both change a body's velocity, but they work differently:

| | Force | Impulse |
|---|---|---|
| Duration | Applied continuously (per step) | Instant, one-shot |
| Units | Newtons (mass × acceleration) | kg⋅m/s (mass × velocity change) |
| Use case | Thrusters, wind, magnets | Explosions, jumps, bullets |

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

mass = 2
body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, 15))
body.position = (0, 0)
shape = pymunk.Circle(body, 15)
space.add(body, shape)

# Force — applied at body's local center, persists until removed
body.apply_force_at_local_point((0, 2000), (0, 0))

# Impulse — instant velocity change at a world point
body.apply_impulse_at_world_point((500, 0), body.position)

# Force at offset creates torque (rotation)
body.apply_force_at_local_point((100, 0), (0, 15))  # push right at top
```

Key details:
- `apply_force_at_local_point(force, point)` — force and point in body-local coords
- `apply_impulse_at_world_point(impulse, point)` — impulse in world coords, point in world coords
- Forces off-center create torque (spin). Centered forces only translate.
- Forces reset each step — you must re-apply them in an updater or callback

## Manim Rendering

An `Arrow` shows force direction and magnitude. We scale the arrow length by force magnitude and point it in the force direction. The arrow follows the body.

```python
from manim import *
import numpy as np

SCALE = 100
FORCE_SCALE = 0.0003  # shrink force vector to fit screen

class ForceArrow(Scene):
    def construct(self):
        dot = Dot(radius=0.15, color=BLUE)
        force_arrow = Arrow(ORIGIN, UP, color=YELLOW, buff=0)

        def update_arrow(arrow):
            pos = dot.get_center()
            force = np.array([fx, fy, 0]) * FORCE_SCALE
            if np.linalg.norm(force) > 0.05:
                arrow.become(Arrow(pos, pos + force,
                             color=YELLOW, buff=0, stroke_width=3))
            else:
                arrow.become(Dot(pos, radius=0.01, fill_opacity=0))

        force_arrow.add_updater(update_arrow)
        self.add(dot, force_arrow)
```

When force is near zero, we hide the arrow by replacing it with an invisible dot.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class ForceDemo(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -400)
        body = pymunk.Body(2, pymunk.moment_for_circle(2, 0, 15))
        body.position = (0, -100)
        shape = pymunk.Circle(body, 15)
        shape.elasticity = 0.7
        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.elasticity = 0.5
        space.add(body, shape, floor)

        dot = Dot(radius=0.15, color=BLUE)
        arrow = Arrow(ORIGIN, UP, color=YELLOW, buff=0)
        floor_line = Line(LEFT*4, RIGHT*4, color=WHITE).shift(DOWN*2.5)
        self.add(floor_line, dot, arrow)

        thrust = [0, 1800]  # upward thrust
        elapsed = [0.0]

        def update(mob, dt):
            elapsed[0] += dt
            # Pulse thrust on/off every 1.5 seconds
            if int(elapsed[0] / 1.5) % 2 == 0:
                body.apply_force_at_local_point((thrust[0], thrust[1]), (0, 0))
                active = True
            else:
                active = False
            for _ in range(10):
                space.step(dt / 10)
            pos = [body.position.x/SCALE, body.position.y/SCALE, 0]
            dot.move_to(pos)
            if active:
                end = [pos[0], pos[1] + 0.5, 0]
                arrow.become(Arrow(pos, end, color=YELLOW, buff=0, stroke_width=3))
            else:
                arrow.become(Dot(pos, radius=0.01, fill_opacity=0))

        dot.add_updater(update)
        self.wait(8)
```

## What You Learned

- `apply_force_at_local_point` applies continuous force (resets each step)
- `apply_impulse_at_world_point` applies an instant velocity change
- Off-center forces create torque — the body spins
- Forces need to be re-applied every frame; impulses are fire-and-forget
- In manim, `Arrow` visualizes force direction and magnitude
- Scale force vectors down (÷ thousands) to fit manim's coordinate frame
- Pulsing forces on/off creates a thruster or jetpack effect

---

[← Chapter 6: Shapes](chapter-06-shapes.md) | [Chapter 8: Friction →](chapter-08-friction.md)
