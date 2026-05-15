# Chapter 5: Collisions & Callbacks

[← Chapter 4: Pendulum](chapter-04-pendulum.md) | [Chapter 6: Shapes →](chapter-06-shapes.md)

---

## Pymunk Concept: Collision Handlers

Every shape has a `collision_type` (an integer). You register handlers that fire when two types collide. Callbacks let you trigger game logic — scoring, damage, sound effects.

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

BALL_TYPE = 1
WALL_TYPE = 2

# Create ball
ball_body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
ball_body.position = (0, 200)
ball_shape = pymunk.Circle(ball_body, 10)
ball_shape.collision_type = BALL_TYPE
ball_shape.elasticity = 0.9

# Create floor
floor = pymunk.Segment(space.static_body, (-300, -200), (300, -200), 5)
floor.collision_type = WALL_TYPE
floor.elasticity = 1.0

# Register collision handler
handler = space.add_collision_handler(BALL_TYPE, WALL_TYPE)
handler.begin = lambda arb, space, data: on_hit(arb)

def on_hit(arbiter):
    print(f"Impact! velocity: {arbiter.total_impulse.length:.1f}")
    return True  # True = process collision normally

space.add(ball_body, ball_shape, floor)
```

Callback phases: `begin` (first touch), `pre_solve` (each step while overlapping), `post_solve` (after impulse applied), `separate` (stopped touching). Return `False` from `begin` to ignore the collision.

## Manim Rendering

On collision, we trigger a `Flash` effect at the impact point and briefly change the ball's color. We track collisions with a shared list that the updater reads.

```python
from manim import *

SCALE = 100

class CollisionVis(Scene):
    def construct(self):
        collisions = []  # shared state: [(position, impulse), ...]

        def on_hit(arbiter):
            pos = arbiter.contact_point_set.points[0].point_a
            collisions.append((pos, arbiter.total_impulse.length))
            return True

        # In the updater, check for new collisions:
        def update(mob, dt):
            for pos, impulse in collisions:
                flash_pos = [pos.x / SCALE, pos.y / SCALE, 0]
                self.add(Flash(flash_pos, color=ORANGE, flash_radius=0.3))
            collisions.clear()
```

The `Flash` mobject creates a burst of lines radiating outward — perfect for impact effects. It auto-removes after playing.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class CollisionFlash(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        BALL, WALL = 1, 2
        collisions = []

        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.elasticity = 0.9
        floor.collision_type = WALL
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 12))
        body.position = (50, 300)
        shape = pymunk.Circle(body, 12)
        shape.elasticity = 0.9
        shape.collision_type = BALL
        space.add(body, shape, floor)

        handler = space.add_collision_handler(BALL, WALL)
        handler.post_solve = lambda arb, sp, d: collisions.append(
            (arb.contact_point_set.points[0].point_a, arb.total_impulse.length))

        dot = Dot(radius=0.14, color=BLUE)
        floor_line = Line(LEFT * 4, RIGHT * 4, color=WHITE).shift(DOWN * 2.5)
        hit_count = Text("Hits: 0", font_size=24).to_corner(UL)
        self.add(floor_line, dot, hit_count)
        hits = [0]

        def update(mob, dt):
            for _ in range(10):
                space.step(dt / 10)
            dot.move_to([body.position.x/SCALE, body.position.y/SCALE, 0])
            for pos, impulse in collisions:
                self.add(Flash([pos.x/SCALE, pos.y/SCALE, 0],
                         color=ORANGE, flash_radius=0.2+impulse/5000))
                dot.set_color(RED)
                hits[0] += 1
                hit_count.become(Text(f"Hits: {hits[0]}", font_size=24).to_corner(UL))
            collisions.clear()
            dot.set_color(interpolate_color(RED, BLUE, 0.1))

        dot.add_updater(update)
        self.wait(6)
```

## What You Learned

- `collision_type` is an integer tag you assign to shapes for handler matching
- `add_collision_handler(type_a, type_b)` registers callbacks for that pair
- Four phases: `begin`, `pre_solve`, `post_solve`, `separate`
- Return `False` from `begin` to make shapes pass through each other
- `arbiter.total_impulse` gives the force of impact (available in `post_solve`)
- `Flash` in manim creates a radial burst effect — great for impact visualization
- Use a shared list to pass collision events from pymunk callbacks to manim updaters

---

[← Chapter 4: Pendulum](chapter-04-pendulum.md) | [Chapter 6: Shapes →](chapter-06-shapes.md)
