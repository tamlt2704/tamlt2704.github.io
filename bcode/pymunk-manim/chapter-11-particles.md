# Chapter 11: Fluid-like Particles

[← Chapter 10: Gears](chapter-10-gears.md) | [Chapter 12: Rube Goldberg →](chapter-12-rube-goldberg.md)

---

## Pymunk Concept: Particle Systems

Simulating fluid-like behavior with pymunk means spawning hundreds of small circles with low friction. They pile up, flow, and interact through collisions. No special fluid solver — just many tiny bodies.

```python
import pymunk
import random

space = pymunk.Space()
space.gravity = (0, -900)

# Container walls
left = pymunk.Segment(space.static_body, (-150, -250), (-150, 200), 5)
right = pymunk.Segment(space.static_body, (150, -250), (150, 200), 5)
bottom = pymunk.Segment(space.static_body, (-150, -250), (150, -250), 5)
for wall in [left, right, bottom]:
    wall.elasticity = 0.2
    wall.friction = 0.1
space.add(left, right, bottom)

# Spawn particles from the top
particles = []
for i in range(200):
    mass, radius = 0.1, 4
    body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
    body.position = (random.uniform(-100, 100), 200 + i * 3)
    shape = pymunk.Circle(body, radius)
    shape.friction = 0.05
    shape.elasticity = 0.3
    space.add(body, shape)
    particles.append(body)
```

Tips for fluid-like behavior:
- Small radius (3–5 units) with low mass
- Very low friction (0.01–0.1) so particles slide past each other
- Moderate elasticity (0.2–0.4) prevents energy explosion
- Stagger spawn positions to avoid initial overlap (pymunk hates overlapping shapes)

## Manim Rendering

With hundreds of particles, individual `Dot` mobjects get expensive. Use a `VGroup` of dots with a batch updater. Color each dot by its velocity magnitude for a heat-map effect.

```python
from manim import *

SCALE = 100

class ParticleVis(Scene):
    def construct(self):
        dots = VGroup()
        for body in particles:
            dot = Dot(radius=0.04, color=BLUE)
            dots.add(dot)

        def update_particles(group, dt):
            for _ in range(5):
                space.step(dt / 5)
            for dot, body in zip(group, particles):
                dot.move_to([body.position.x/SCALE, body.position.y/SCALE, 0])
                speed = body.velocity.length
                dot.set_color(interpolate_color(BLUE, RED, min(speed/400, 1)))

        dots.add_updater(update_particles)
        self.add(dots)
```

For better performance with 200+ particles, reduce sub-steps to 3–5 and accept slightly less accurate physics.

## Full Scene

```python
from manim import *
import pymunk, random

SCALE = 100

class ParticlePour(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        walls = [
            pymunk.Segment(space.static_body, (-150, -250), (-150, 200), 5),
            pymunk.Segment(space.static_body, (150, -250), (150, 200), 5),
            pymunk.Segment(space.static_body, (-150, -250), (150, -250), 5),
        ]
        for w in walls:
            w.elasticity = 0.2
            w.friction = 0.1
        space.add(*walls)

        particles = []
        for i in range(150):
            b = pymunk.Body(0.1, pymunk.moment_for_circle(0.1, 0, 4))
            b.position = (random.uniform(-80, 80), 200 + i * 4)
            s = pymunk.Circle(b, 4)
            s.friction = 0.05
            s.elasticity = 0.3
            space.add(b, s)
            particles.append(b)

        # Manim container
        container = VGroup(
            Line([-1.5, -2.5, 0], [-1.5, 2, 0], color=GREY),
            Line([1.5, -2.5, 0], [1.5, 2, 0], color=GREY),
            Line([-1.5, -2.5, 0], [1.5, -2.5, 0], color=GREY),
        )
        dots = VGroup(*[Dot(radius=0.04, color=BLUE) for _ in particles])
        count_text = Text("n=150", font_size=20).to_corner(UL)
        self.add(container, dots, count_text)

        def update(group, dt):
            for _ in range(5):
                space.step(dt / 5)
            for dot, body in zip(group, particles):
                dot.move_to([body.position.x/SCALE, body.position.y/SCALE, 0])
                speed = body.velocity.length
                dot.set_color(interpolate_color(BLUE_D, ORANGE, min(speed/300, 1)))

        dots.add_updater(update)
        self.wait(8)
```

## What You Learned

- Fluid-like behavior emerges from many small circles with low friction
- Low friction (0.01–0.1) lets particles slide past each other like liquid
- Stagger spawn Y-positions to prevent initial overlap explosions
- Batch-update all dots in one `VGroup` updater for cleaner code
- Color by velocity creates a heat-map showing flow patterns
- Fewer sub-steps (3–5) trades accuracy for performance with many bodies
- Container walls are just static segments forming a box shape

---

[← Chapter 10: Gears](chapter-10-gears.md) | [Chapter 12: Rube Goldberg →](chapter-12-rube-goldberg.md)
