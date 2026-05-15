# Chapter 3: Constraints — Joints

[← Chapter 2: Bodies](chapter-02-bodies.md) | [Chapter 4: Pendulum →](chapter-04-pendulum.md)

---

## Pymunk Concept: Joints

Joints (constraints) connect two bodies and restrict their relative motion. Pymunk offers several types:

| Joint | What it does |
|-------|-------------|
| `PinJoint` | Fixed distance between two anchor points |
| `SlideJoint` | Distance stays between min and max |
| `DampedSpring` | Spring force pulls bodies toward rest length |

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Two dynamic bodies
body_a = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
body_a.position = (-100, 100)
body_b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
body_b.position = (100, 100)

# PinJoint — fixed distance, like a rigid rod
pin = pymunk.PinJoint(body_a, body_b, (0, 0), (0, 0))

# SlideJoint — stretchy rope (min=50, max=200)
slide = pymunk.SlideJoint(body_a, body_b, (0, 0), (0, 0), 50, 200)

# DampedSpring — bouncy connection
spring = pymunk.DampedSpring(body_a, body_b, (0, 0), (0, 0),
                              rest_length=150, stiffness=50, damping=5)
space.add(body_a, body_b, spring)
```

Anchor points `(0, 0)` mean "center of body." You can offset them — e.g., `(10, 0)` attaches 10 units right of center. This matters for rotation.

## Manim Rendering

To visualize a joint, draw a `Line` between the two dots and update it every frame. The line's endpoints track each body's position.

```python
from manim import *

SCALE = 100

class JointVis(Scene):
    def construct(self):
        dot_a = Dot(color=RED)
        dot_b = Dot(color=BLUE)
        link = Line(dot_a.get_center(), dot_b.get_center(),
                    stroke_width=2, color=GREY)

        def update_link(line):
            line.put_start_and_end_on(
                dot_a.get_center(), dot_b.get_center()
            )

        link.add_updater(update_link)
        self.add(dot_a, dot_b, link)
```

For a `DampedSpring`, you can vary the line color or thickness based on how stretched it is compared to rest length — red when stretched, blue when compressed.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class SpringJoint(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.elasticity = 0.5
        space.add(floor)

        body_a = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body_a.position = (-80, 200)
        body_b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body_b.position = (80, 50)
        spring = pymunk.DampedSpring(body_a, body_b, (0,0), (0,0),
                                      rest_length=120, stiffness=60, damping=3)
        space.add(body_a, body_b, spring,
                  pymunk.Circle(body_a, 10), pymunk.Circle(body_b, 10))

        dot_a = Dot(radius=0.12, color=RED)
        dot_b = Dot(radius=0.12, color=BLUE)
        link = Line(ORIGIN, ORIGIN, stroke_width=3, color=GREY)
        floor_line = Line(LEFT * 4, RIGHT * 4, color=WHITE).shift(DOWN * 2.5)
        self.add(floor_line, link, dot_a, dot_b)

        def update(group, dt):
            for _ in range(10):
                space.step(dt / 10)
            pa = [body_a.position.x / SCALE, body_a.position.y / SCALE, 0]
            pb = [body_b.position.x / SCALE, body_b.position.y / SCALE, 0]
            dot_a.move_to(pa)
            dot_b.move_to(pb)
            link.put_start_and_end_on(pa, pb)
            stretch = abs((body_a.position - body_b.position).length - 120)
            link.set_color(interpolate_color(WHITE, RED, min(stretch / 100, 1)))

        VGroup(dot_a, dot_b, link).add_updater(update)
        self.wait(6)
```

## What You Learned

- `PinJoint` keeps two bodies at a fixed distance — like a rigid rod
- `SlideJoint` allows distance to vary between min and max — like a rope
- `DampedSpring` applies spring force with configurable stiffness and damping
- Anchor points are in local body coordinates — `(0,0)` = body center
- In manim, `Line.put_start_and_end_on()` redraws the line between two points each frame
- Color-coding stretch distance gives visual feedback on spring tension

---

[← Chapter 2: Bodies](chapter-02-bodies.md) | [Chapter 4: Pendulum →](chapter-04-pendulum.md)
