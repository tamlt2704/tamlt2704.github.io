# Chapter 10: Gears & Motors

[← Chapter 9: Chain](chapter-09-chain.md) | [Chapter 11: Particles →](chapter-11-particles.md)

---

## Pymunk Concept: Motors & Gear Joints

A `SimpleMotor` applies constant angular velocity to a body — like an electric motor. A `GearJoint` locks two bodies' rotation at a fixed ratio (e.g., 2:1 means one spins twice as fast).

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, 0)  # top-down view, no gravity

# Gear A — driven by motor
gear_a = pymunk.Body(5, pymunk.moment_for_circle(5, 0, 40))
gear_a.position = (0, 0)
shape_a = pymunk.Circle(gear_a, 40)

# Gear B — driven by gear joint (half the size, spins 2x faster)
gear_b = pymunk.Body(2, pymunk.moment_for_circle(2, 0, 20))
gear_b.position = (65, 0)
shape_b = pymunk.Circle(gear_b, 20)

# Pin both gears in place (they rotate but don't translate)
pin_a = pymunk.PivotJoint(space.static_body, gear_a, (0, 0))
pin_b = pymunk.PivotJoint(space.static_body, gear_b, (65, 0))

# Motor drives gear_a at 2 rad/s
motor = pymunk.SimpleMotor(space.static_body, gear_a, 2.0)

# Gear joint: ratio = -2.0 (negative = opposite direction, 2x speed)
gear_joint = pymunk.GearJoint(gear_a, gear_b, 0.0, -2.0)

space.add(gear_a, shape_a, gear_b, shape_b, pin_a, pin_b, motor, gear_joint)
```

Key parameters:
- `SimpleMotor(body_a, body_b, rate)` — rate in radians/second
- `GearJoint(body_a, body_b, phase, ratio)` — negative ratio = opposite direction

## Manim Rendering

Rotating gears look best as polygons with "teeth." We create a regular polygon and rotate it by the body's angle each frame. A small tick mark shows rotation clearly.

```python
from manim import *

SCALE = 100

class GearVis(Scene):
    def construct(self):
        # Gear with 8 teeth = 16-sided polygon (alternating radii)
        def make_gear(radius, teeth, color):
            points = []
            for i in range(teeth * 2):
                angle = i * PI / teeth
                r = radius if i % 2 == 0 else radius * 0.75
                points.append([r * np.cos(angle), r * np.sin(angle), 0])
            return Polygon(*points, color=color, fill_opacity=0.3)

        gear_mob = make_gear(0.4, 8, BLUE)

        def update_gear(mob):
            mob.rotate(body.angle - mob.get_angle_of_rotation())
            # Simpler: just set rotation directly
```

The tick mark (a small line from center to edge) makes slow rotation visible even on circular gears.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class GearsAndMotor(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, 0)

        gear_a = pymunk.Body(5, pymunk.moment_for_circle(5, 0, 40))
        gear_a.position = (-60, 0)
        gear_b = pymunk.Body(2, pymunk.moment_for_circle(2, 0, 20))
        gear_b.position = (60, 0)
        pin_a = pymunk.PivotJoint(space.static_body, gear_a, (-60, 0))
        pin_b = pymunk.PivotJoint(space.static_body, gear_b, (60, 0))
        motor = pymunk.SimpleMotor(space.static_body, gear_a, 2.0)
        gear_j = pymunk.GearJoint(gear_a, gear_b, 0, -2.0)
        space.add(gear_a, pymunk.Circle(gear_a, 40),
                  gear_b, pymunk.Circle(gear_b, 20),
                  pin_a, pin_b, motor, gear_j)

        def make_gear_mob(pos, radius, teeth, color):
            pts = []
            for i in range(teeth * 2):
                a = i * PI / teeth
                r = radius if i % 2 == 0 else radius * 0.7
                pts.append([pos[0] + r*np.cos(a), pos[1] + r*np.sin(a), 0])
            return Polygon(*pts, color=color, fill_opacity=0.3)

        ga_mob = make_gear_mob([-0.6, 0], 0.4, 8, BLUE)
        gb_mob = make_gear_mob([0.6, 0], 0.2, 8, GREEN)
        tick_a = Line([-0.6,0,0], [-0.2,0,0], color=WHITE, stroke_width=2)
        tick_b = Line([0.6,0,0], [0.8,0,0], color=WHITE, stroke_width=2)
        label = Text("ratio = -2:1", font_size=22).shift(DOWN*1.5)
        self.add(ga_mob, gb_mob, tick_a, tick_b, label)

        prev_angles = [0.0, 0.0]
        def update(mob, dt):
            for _ in range(5):
                space.step(dt / 5)
            da = gear_a.angle - prev_angles[0]
            db = gear_b.angle - prev_angles[1]
            ga_mob.rotate(da)
            tick_a.rotate(da, about_point=[-0.6, 0, 0])
            gb_mob.rotate(db)
            tick_b.rotate(db, about_point=[0.6, 0, 0])
            prev_angles[0] = gear_a.angle
            prev_angles[1] = gear_b.angle

        ga_mob.add_updater(update)
        self.wait(8)
```

## What You Learned

- `SimpleMotor` drives a body at constant angular velocity — no force calculation needed
- `GearJoint` locks rotation ratio between two bodies (negative = counter-rotate)
- `PivotJoint` to static body pins a gear in place so it only rotates
- Gear teeth visuals: alternate inner/outer radii on a polygon
- Track `prev_angle` and rotate by the delta each frame for smooth animation
- `rotate(angle, about_point=...)` spins a mobject around a specific center
- Zero gravity + pivot joints = top-down mechanical simulation

---

[← Chapter 9: Chain](chapter-09-chain.md) | [Chapter 11: Particles →](chapter-11-particles.md)
