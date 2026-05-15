# Chapter 4: Pendulum

[← Chapter 3: Joints](chapter-03-joints.md) | [Chapter 5: Collisions →](chapter-05-collisions.md)

---

## Pymunk Concept: Pivot Joint Pendulum

A pendulum is a body that swings under gravity, constrained to rotate around a fixed point. In pymunk, we use a `PivotJoint` connecting a dynamic body (the bob) to the static body at the pivot location.

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# The bob — a heavy circle
mass, radius = 5, 15
moment = pymunk.moment_for_circle(mass, 0, radius)
bob = pymunk.Body(mass, moment)
bob.position = (150, 0)  # start displaced to the right

bob_shape = pymunk.Circle(bob, radius)
bob_shape.elasticity = 0.0

# PivotJoint pins the bob to a fixed point in world space
pivot_point = (0, 100)
pivot = pymunk.PivotJoint(space.static_body, bob, pivot_point)
pivot.max_bias = 0  # disable joint correction drift

space.add(bob, bob_shape, pivot)
```

The bob swings because gravity pulls it down, but the pivot constraint keeps it at a fixed distance from `(0, 100)`. Energy converts between potential (height) and kinetic (speed).

`max_bias = 0` prevents the joint from "correcting" small drift — keeps the pendulum smooth.

## Manim Rendering

We draw a `Line` from pivot to bob (the rod) and use `TracedPath` to show the arc. A `Text` mobject displays kinetic energy, updating each frame.

```python
from manim import *

SCALE = 100

class PendulumVis(Scene):
    def construct(self):
        pivot_pos = np.array([0, 1, 0])  # pivot at (0,100) / SCALE
        bob_dot = Dot(radius=0.18, color=YELLOW)
        rod = Line(pivot_pos, bob_dot.get_center(), color=WHITE)
        trace = TracedPath(bob_dot.get_center,
                           stroke_color=YELLOW_A, stroke_width=1.5)
        pivot_dot = Dot(pivot_pos, radius=0.06, color=WHITE)

        energy_text = Text("KE: 0.0", font_size=24).to_corner(UR)

        self.add(trace, rod, bob_dot, pivot_dot, energy_text)
```

The rod updates with `put_start_and_end_on` each frame. Energy text shows `0.5 * mass * v²`.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class Pendulum(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        mass, radius = 5, 15
        moment = pymunk.moment_for_circle(mass, 0, radius)
        bob = pymunk.Body(mass, moment)
        bob.position = (150, 0)
        bob_shape = pymunk.Circle(bob, radius)
        pivot_pt = (0, 100)
        joint = pymunk.PivotJoint(space.static_body, bob, pivot_pt)
        joint.max_bias = 0
        space.add(bob, bob_shape, joint)

        pivot_pos = np.array([pivot_pt[0]/SCALE, pivot_pt[1]/SCALE, 0])
        bob_dot = Dot(radius=0.18, color=YELLOW)
        rod = Line(pivot_pos, ORIGIN, color=WHITE, stroke_width=2)
        trace = TracedPath(bob_dot.get_center, stroke_color=YELLOW_A,
                           stroke_width=1.5, dissipating_time=2)
        pivot_dot = Dot(pivot_pos, radius=0.06, color=WHITE)
        ke_label = Text("KE: 0", font_size=22).to_corner(UR)
        self.add(trace, rod, bob_dot, pivot_dot, ke_label)

        def update(mob, dt):
            for _ in range(10):
                space.step(dt / 10)
            pos = [bob.position.x / SCALE, bob.position.y / SCALE, 0]
            bob_dot.move_to(pos)
            rod.put_start_and_end_on(pivot_pos, pos)
            speed = bob.velocity.length
            ke = 0.5 * mass * (speed ** 2)
            ke_label.become(Text(f"KE: {ke:.0f}", font_size=22).to_corner(UR))

        bob_dot.add_updater(update)
        self.wait(8)
```

## What You Learned

- `PivotJoint` constrains a body to rotate around a fixed world point
- Setting `max_bias = 0` prevents joint drift correction for smoother motion
- A pendulum converts potential energy (height) to kinetic energy (speed) and back
- `TracedPath` with `dissipating_time` fades old trail segments for cleaner visuals
- `Text.become()` replaces text content each frame for live data display
- The rod is just a `Line` that re-draws between pivot and bob every frame

---

[← Chapter 3: Joints](chapter-03-joints.md) | [Chapter 5: Collisions →](chapter-05-collisions.md)
