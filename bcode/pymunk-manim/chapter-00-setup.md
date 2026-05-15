# Chapter 0: Setup & First Ball

[Next → Chapter 1: Gravity & Bouncing](chapter-01-gravity.md)

---

## Install

```bash
uv python install 3.12
uv init pymunk-manim --python 3.12
cd pymunk-manim
uv add pymunk manim
```

Verify:

```bash
uv run python -c "import pymunk; import manim; print('Ready')"
```

---

## Pymunk Concept: Space + Body + Shape

Pymunk has 3 core objects:

```python
import pymunk

# Space: the world (holds all bodies, applies gravity)
space = pymunk.Space()
space.gravity = (0, -900)  # pixels/sec², downward

# Body: position + velocity + mass (the physics)
body = pymunk.Body(mass=1, moment=10)
body.position = (400, 500)

# Shape: collision geometry attached to a body
circle = pymunk.Circle(body, radius=20)
circle.elasticity = 0.8  # bounciness (0=dead, 1=perfect)

# Add to space
space.add(body, circle)

# Step the simulation (call every frame)
space.step(1/60)  # advance 1/60th of a second
print(body.position)  # ball has fallen slightly
```

---

## Manim Concept: Scene + Updater

Manim draws things. An **updater** runs every frame to sync visuals with physics.

```python
from manim import *

class BallDrop(Scene):
    def construct(self):
        dot = Dot(point=UP * 2, radius=0.2, color=BLUE)
        self.add(dot)

        # Updater: move dot down every frame
        dot.add_updater(lambda m, dt: m.shift(DOWN * 3 * dt))
        self.wait(2)  # runs for 2 seconds
        dot.clear_updaters()
```

---

## Combining: Pymunk Drives Manim

The pattern: pymunk simulates, manim renders. Sync each frame via updater.

```python
from manim import *
import pymunk

class PhysicsBall(Scene):
    def construct(self):
        # --- Pymunk setup ---
        space = pymunk.Space()
        space.gravity = (0, -900)

        body = pymunk.Body(mass=1, moment=10)
        body.position = (0, 300)  # pymunk coords
        shape = pymunk.Circle(body, radius=20)
        shape.elasticity = 0.9
        space.add(body, shape)

        # Static floor
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, (-400, -250), (400, -250), 5)
        floor_shape.elasticity = 0.9
        space.add(floor_body, floor_shape)

        # --- Manim visuals ---
        ball = Dot(radius=0.3, color=BLUE)
        floor = Line(LEFT * 5, RIGHT * 5, color=WHITE).shift(DOWN * 2.5)
        self.add(ball, floor)

        # --- Sync: updater reads pymunk position ---
        def sync(mob, dt):
            space.step(dt)
            # Convert pymunk coords to manim coords (scale down)
            x = body.position.x / 100
            y = body.position.y / 100
            mob.move_to([x, y, 0])

        ball.add_updater(sync)
        self.wait(4)
```

---

## Render

```bash
uv run manim -pqh chapter_00.py PhysicsBall
```

You'll see a ball drop, hit the floor, and bounce — physics-accurate, beautifully rendered.

---

## The Coordinate Bridge

Pymunk uses pixels (large numbers). Manim uses scene units (~-4 to 4). Scale between them:

```python
SCALE = 100  # 100 pymunk pixels = 1 manim unit

def pymunk_to_manim(pos):
    return [pos.x / SCALE, pos.y / SCALE, 0]

def manim_to_pymunk(point):
    return (point[0] * SCALE, point[1] * SCALE)
```

---

## What You Learned

- **Pymunk**: Space holds bodies, bodies have shapes, `space.step(dt)` advances physics
- **Manim**: Scenes render mobjects, updaters run every frame
- **Bridge**: Updater calls `space.step(dt)`, reads body positions, moves manim objects
- **Coordinates**: Divide pymunk by 100 to get manim units

---

[Next → Chapter 1: Gravity & Bouncing](chapter-01-gravity.md)
