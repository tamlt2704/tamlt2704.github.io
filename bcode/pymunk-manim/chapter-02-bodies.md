# Chapter 2: Multiple Bodies

[← Chapter 1: Gravity](chapter-01-gravity.md) | [Chapter 3: Joints →](chapter-03-joints.md)

---

## Pymunk Concept: Body Types

Pymunk has three body types that control how physics affects them:

| Type | Moves? | Affected by forces? | Use case |
|------|--------|---------------------|----------|
| `DYNAMIC` | Yes | Yes | Balls, boxes, anything that falls |
| `STATIC` | No | No | Walls, floors, platforms |
| `KINEMATIC` | Yes (scripted) | No | Moving platforms, elevators |

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# DYNAMIC — physics drives it
dynamic_body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
dynamic_body.position = (0, 200)
dynamic_shape = pymunk.Circle(dynamic_body, 10)
space.add(dynamic_body, dynamic_shape)

# STATIC — never moves (use space.static_body or create one)
wall = pymunk.Segment(space.static_body, (-300, -200), (300, -200), 5)
space.add(wall)

# KINEMATIC — you control its velocity, ignores gravity
platform = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
platform.position = (-200, 0)
platform.velocity = (50, 0)  # moves right at 50 units/sec
plat_shape = pymunk.Segment(platform, (-50, 0), (50, 0), 5)
space.add(platform, plat_shape)
```

Key difference: kinematic bodies have velocity but zero mass. They push dynamic bodies around but nothing pushes them back. Perfect for conveyor belts or moving platforms.

## Manim Rendering

With multiple bodies, we use a `VGroup` and a single updater that syncs all dots to their pymunk counterparts. Store body-dot pairs in a list.

```python
from manim import *

SCALE = 100
COLORS = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE]

class MultipleBodies(Scene):
    def construct(self):
        # pairs = [(pymunk_body, manim_dot), ...]
        dots = VGroup()
        for i, (body, dot) in enumerate(pairs):
            dots.add(dot)

        def sync_all(group, dt):
            for _ in range(10):
                space.step(dt / 10)
            for body, dot in pairs:
                dot.move_to([body.position.x / SCALE,
                             body.position.y / SCALE, 0])

        dots.add_updater(sync_all)
        self.add(dots)
        self.wait(5)
```

Using a VGroup updater instead of per-dot updaters is cleaner and avoids stepping the space multiple times per frame.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class MultipleBodies(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.elasticity = 0.7
        space.add(floor)

        pairs = []
        colors = [RED, GREEN, BLUE, YELLOW, ORANGE]
        for i, color in enumerate(colors):
            mass = 1
            body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, 10))
            body.position = (-200 + i * 80, 100 + i * 50)
            shape = pymunk.Circle(body, 10)
            shape.elasticity = 0.8
            space.add(body, shape)
            dot = Dot(radius=0.12, color=color)
            pairs.append((body, dot))

        dots = VGroup(*[d for _, d in pairs])
        floor_line = Line(LEFT * 4, RIGHT * 4, color=WHITE).shift(DOWN * 2.5)
        self.add(floor_line, dots)

        def sync_all(group, dt):
            for _ in range(10):
                space.step(dt / 10)
            for body, dot in pairs:
                dot.move_to([body.position.x / SCALE, body.position.y / SCALE, 0])

        dots.add_updater(sync_all)
        self.wait(6)
```

## What You Learned

- `DYNAMIC` bodies are driven by forces and gravity — the default for game objects
- `STATIC` bodies never move — use for walls, floors, boundaries
- `KINEMATIC` bodies move at a set velocity but ignore forces — use for platforms
- A `VGroup` updater syncs all manim dots in one pass, stepping physics once per frame
- Store `(body, dot)` pairs to keep the pymunk↔manim mapping clean
- Different starting positions create staggered drops for visual interest

---

[← Chapter 1: Gravity](chapter-01-gravity.md) | [Chapter 3: Joints →](chapter-03-joints.md)
