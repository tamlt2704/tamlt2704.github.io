# Chapter 8: Friction & Materials

[← Chapter 7: Forces](chapter-07-forces.md) | [Chapter 9: Chain →](chapter-09-chain.md)

---

## Pymunk Concept: Friction & Surface Velocity

Friction controls how much shapes resist sliding against each other. Combined friction between two shapes is `shape_a.friction * shape_b.friction`.

`surface_velocity` makes a shape act like a conveyor belt — it adds tangential velocity at the contact point.

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Ramp — tilted static segment
ramp = pymunk.Segment(space.static_body, (-250, 50), (100, -150), 5)
ramp.friction = 0.3  # slippery ice-like surface

# Block sliding down the ramp
mass = 2
vertices = [(-15, -10), (15, -10), (15, 10), (-15, 10)]
block_body = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices))
block_body.position = (-200, 100)
block_shape = pymunk.Poly(block_body, vertices)
block_shape.friction = 0.5

# Conveyor belt — surface_velocity pushes objects sideways
belt = pymunk.Segment(space.static_body, (-100, -200), (200, -200), 5)
belt.friction = 1.0
belt.surface_velocity = (-100, 0)  # pushes objects left

space.add(block_body, block_shape, ramp, belt)
```

Friction values:
- `0.0` — frictionless ice
- `0.3` — slippery surface
- `0.7` — rubber on concrete
- `1.0+` — very grippy (values > 1 are valid)

## Manim Rendering

We show the block sliding down a ramp with a speed indicator — a horizontal bar that grows with velocity. Color shifts from green (slow) to red (fast).

```python
from manim import *

SCALE = 100

class FrictionVis(Scene):
    def construct(self):
        block = Square(side_length=0.3, color=BLUE, fill_opacity=0.6)
        speed_bar = Rectangle(width=0.01, height=0.15, color=GREEN,
                              fill_opacity=0.8).to_corner(DL).shift(UP*0.5)
        speed_label = Text("Speed: 0", font_size=20).next_to(speed_bar, RIGHT)

        def update_bar(bar):
            speed = body.velocity.length
            width = min(speed / 300, 3.0)
            color = interpolate_color(GREEN, RED, min(speed / 500, 1))
            bar.become(Rectangle(width=max(width, 0.01), height=0.15,
                       color=color, fill_opacity=0.8).to_corner(DL).shift(UP*0.5))

        speed_bar.add_updater(update_bar)
        self.add(block, speed_bar, speed_label)
```

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class FrictionRamp(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        ramp = pymunk.Segment(space.static_body, (-250, 50), (150, -180), 5)
        ramp.friction = 0.3
        ramp.elasticity = 0.1
        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.friction = 1.0
        floor.surface_velocity = (-80, 0)  # conveyor pushes left
        space.add(ramp, floor)

        verts = [(-15, -10), (15, -10), (15, 10), (-15, 10)]
        body = pymunk.Body(2, pymunk.moment_for_poly(2, verts))
        body.position = (-200, 100)
        shape = pymunk.Poly(body, verts)
        shape.friction = 0.5
        shape.elasticity = 0.1
        space.add(body, shape)

        ramp_line = Line([-2.5, 0.5, 0], [1.5, -1.8, 0], color=GREY)
        floor_line = Line(LEFT*4, RIGHT*4, color=YELLOW_D).shift(DOWN*2.5)
        belt_label = Text("← conveyor", font_size=18, color=YELLOW_D).shift(DOWN*2.8)
        block = Square(side_length=0.3, color=BLUE, fill_opacity=0.6)
        speed_text = Text("v=0", font_size=20).to_corner(UR)
        self.add(ramp_line, floor_line, belt_label, block, speed_text)

        def update(mob, dt):
            for _ in range(10):
                space.step(dt / 10)
            pts = [[body.local_to_world(v).x/SCALE,
                    body.local_to_world(v).y/SCALE, 0] for v in verts]
            block.become(Polygon(*pts, color=BLUE, fill_opacity=0.6))
            speed = body.velocity.length
            color = interpolate_color(GREEN, RED, min(speed / 400, 1))
            speed_text.become(Text(f"v={speed:.0f}", font_size=20,
                             color=color).to_corner(UR))

        block.add_updater(update)
        self.wait(7)
```

## What You Learned

- `shape.friction` controls sliding resistance (multiplied between two contacting shapes)
- `surface_velocity` adds tangential speed at contact — creates conveyor belt behavior
- Friction `0.0` = ice, `0.7` = rubber, `1.0+` = very grippy
- A tilted `Segment` makes a ramp — gravity's component along the surface drives sliding
- Speed indicators (bars or text) give visual feedback on velocity changes
- `interpolate_color(GREEN, RED, t)` maps speed to a color gradient for intuitive display

---

[← Chapter 7: Forces](chapter-07-forces.md) | [Chapter 9: Chain →](chapter-09-chain.md)
