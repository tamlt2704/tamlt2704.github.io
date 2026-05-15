# Chapter 9: Ragdoll / Chain

[← Chapter 8: Friction](chapter-08-friction.md) | [Chapter 10: Gears →](chapter-10-gears.md)

---

## Pymunk Concept: Linked Bodies

A chain is multiple bodies connected end-to-end with `PinJoint`s. Each link is a small dynamic body. The first link attaches to a static anchor point, and gravity makes the whole chain swing and drape.

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

NUM_LINKS = 8
LINK_LENGTH = 30
anchor = (0, 200)  # fixed point in world

bodies = []
prev_body = space.static_body
prev_anchor = anchor

for i in range(NUM_LINKS):
    mass = 0.5
    body = pymunk.Body(mass, pymunk.moment_for_segment(mass, (0, 0), (0, -LINK_LENGTH), 2))
    body.position = (anchor[0], anchor[1] - (i + 1) * LINK_LENGTH)
    shape = pymunk.Segment(body, (0, 0), (0, -LINK_LENGTH), 2)
    shape.elasticity = 0.2

    joint = pymunk.PinJoint(prev_body, body, prev_anchor, (0, 0))
    space.add(body, shape, joint)

    bodies.append(body)
    prev_body = body
    prev_anchor = (0, -LINK_LENGTH)  # bottom of this link
```

Each joint connects the bottom of the previous link to the top of the next. The static body anchor keeps the chain hanging. For a ragdoll, add `RotaryLimitJoint` to restrict joint angles.

## Manim Rendering

Draw each link as a `Line` segment. Every frame, read each body's position and the transformed endpoints, then update the lines.

```python
from manim import *

SCALE = 100

class ChainVis(Scene):
    def construct(self):
        lines = VGroup()
        for body in bodies:
            top = body.local_to_world((0, 0))
            bot = body.local_to_world((0, -LINK_LENGTH))
            line = Line(
                [top.x/SCALE, top.y/SCALE, 0],
                [bot.x/SCALE, bot.y/SCALE, 0],
                stroke_width=3, color=GOLD
            )
            lines.add(line)

        def update_chain(group, dt):
            for line, body in zip(group, bodies):
                top = body.local_to_world((0, 0))
                bot = body.local_to_world((0, -LINK_LENGTH))
                line.put_start_and_end_on(
                    [top.x/SCALE, top.y/SCALE, 0],
                    [bot.x/SCALE, bot.y/SCALE, 0])

        lines.add_updater(update_chain)
        self.add(lines)
```

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100
NUM_LINKS = 10
LINK_LEN = 25

class SwingingChain(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        space.damping = 0.95
        anchor = (0, 200)

        bodies = []
        prev_body = space.static_body
        prev_pt = anchor
        for i in range(NUM_LINKS):
            mass = 0.5
            b = pymunk.Body(mass, pymunk.moment_for_segment(mass, (0,0), (0,-LINK_LEN), 2))
            b.position = (anchor[0] + (i+1)*5, anchor[1] - (i+1)*LINK_LEN)
            s = pymunk.Segment(b, (0,0), (0,-LINK_LEN), 2)
            s.elasticity = 0.2
            j = pymunk.PinJoint(prev_body, b, prev_pt, (0,0))
            space.add(b, s, j)
            bodies.append(b)
            prev_body = b
            prev_pt = (0, -LINK_LEN)

        anchor_dot = Dot([anchor[0]/SCALE, anchor[1]/SCALE, 0],
                         radius=0.08, color=WHITE)
        lines = VGroup()
        for _ in bodies:
            lines.add(Line(ORIGIN, ORIGIN, stroke_width=3, color=GOLD))
        self.add(anchor_dot, lines)

        def update(group, dt):
            for _ in range(10):
                space.step(dt / 10)
            for line, body in zip(group, bodies):
                top = body.local_to_world((0, 0))
                bot = body.local_to_world((0, -LINK_LEN))
                line.put_start_and_end_on(
                    [top.x/SCALE, top.y/SCALE, 0],
                    [bot.x/SCALE, bot.y/SCALE, 0])
                speed = body.velocity.length
                line.set_color(interpolate_color(GOLD, RED, min(speed/300, 1)))

        lines.add_updater(update)
        self.wait(8)
```

## What You Learned

- A chain is a sequence of bodies connected by `PinJoint`s end-to-end
- The first joint attaches to `space.static_body` to anchor the chain
- `moment_for_segment` calculates inertia for rod-shaped links
- `space.damping` (0–1) globally reduces velocity — simulates air resistance
- Offset initial positions to break symmetry and trigger natural swinging
- Color each link by speed to visualize energy flowing through the chain

---

[← Chapter 8: Friction](chapter-08-friction.md) | [Chapter 10: Gears →](chapter-10-gears.md)
