# Chapter 12: Full Scene — Rube Goldberg Machine

[← Chapter 11: Particles](chapter-11-particles.md) | [Overview →](README.md)

---

## Pymunk Concept: Combining Everything

A Rube Goldberg machine chains simple mechanisms: ball drops → hits dominos → swings pendulum → launches projectile. Each stage triggers the next through natural physics — no explicit triggers needed.

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Stage 1: Ball on ramp
ball = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
ball.position = (-250, 250)
ball_shape = pymunk.Circle(ball, 10)
ball_shape.elasticity = 0.5

# Stage 2: Dominos — tall thin boxes
dominos = []
for i in range(5):
    verts = [(-3, -15), (3, -15), (3, 15), (-3, 15)]
    d = pymunk.Body(0.5, pymunk.moment_for_poly(0.5, verts))
    d.position = (-100 + i * 25, -180)
    s = pymunk.Poly(d, verts)
    s.friction = 0.7
    space.add(d, s)
    dominos.append(d)

# Stage 3: Pendulum hit by last domino
bob = pymunk.Body(3, pymunk.moment_for_circle(3, 0, 12))
bob.position = (80, -100)
pivot = pymunk.PivotJoint(space.static_body, bob, (80, 0))
```

## Manim Rendering

For a cinematic scene, use `MovingCameraScene` to pan and zoom. Stage labels narrate the action. For slow-motion replay, reduce the dt multiplier.

```python
from manim import *

SCALE = 100

class RubeGoldbergVis(MovingCameraScene):
    def construct(self):
        self.camera.frame.set(width=10)

        # Stage labels appear at key moments
        def show_label(text, pos):
            label = Text(text, font_size=20).move_to(pos)
            self.play(FadeIn(label), run_time=0.3)
            self.wait(1)
            self.play(FadeOut(label), run_time=0.3)

        # Slow-motion: step physics at half speed
        def slow_step(space, dt):
            for _ in range(5):
                space.step(dt * 0.5 / 5)
```

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class RubeGoldberg(MovingCameraScene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        # Ramp
        ramp = pymunk.Segment(space.static_body, (-300, 200), (-120, -150), 5)
        ramp.elasticity = 0.3
        ramp.friction = 0.4
        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.friction = 0.8
        space.add(ramp, floor)

        # Ball
        ball = pymunk.Body(1.5, pymunk.moment_for_circle(1.5, 0, 10))
        ball.position = (-280, 220)
        ball_s = pymunk.Circle(ball, 10)
        ball_s.elasticity = 0.4
        space.add(ball, ball_s)

        # Dominos
        dominos = []
        for i in range(5):
            verts = [(-3, -18), (3, -18), (3, 18), (-3, 18)]
            d = pymunk.Body(0.3, pymunk.moment_for_poly(0.3, verts))
            d.position = (-80 + i * 28, -232)
            s = pymunk.Poly(d, verts)
            s.friction = 0.6
            s.elasticity = 0.1
            space.add(d, s)
            dominos.append((d, verts))

        # Pendulum
        bob = pymunk.Body(3, pymunk.moment_for_circle(3, 0, 12))
        bob.position = (120, -150)
        bob_s = pymunk.Circle(bob, 12)
        bob_s.elasticity = 0.8
        pj = pymunk.PivotJoint(space.static_body, bob, (120, -50))
        pj.max_bias = 0
        space.add(bob, bob_s, pj)

        # Projectile
        proj = pymunk.Body(0.3, pymunk.moment_for_circle(0.3, 0, 6))
        proj.position = (160, -244)
        proj_s = pymunk.Circle(proj, 6)
        proj_s.elasticity = 0.9
        space.add(proj, proj_s)

        # --- Manim objects ---
        ramp_line = Line([-3, 2, 0], [-1.2, -1.5, 0], color=GREY)
        floor_line = Line(LEFT*4, RIGHT*4, color=WHITE).shift(DOWN*2.5)
        ball_dot = Dot(radius=0.1, color=RED)
        dom_mobs = VGroup(*[Rectangle(width=0.06, height=0.36,
                    color=GREEN, fill_opacity=0.6) for _ in dominos])
        bob_dot = Dot(radius=0.12, color=YELLOW)
        rod = Line(ORIGIN, ORIGIN, color=WHITE, stroke_width=2)
        proj_dot = Dot(radius=0.06, color=ORANGE)
        self.add(ramp_line, floor_line, ball_dot, dom_mobs, bob_dot, rod, proj_dot)
        self.camera.frame.set(width=12)

        elapsed = [0.0]
        def update(mob, dt):
            elapsed[0] += dt
            for _ in range(10):
                space.step(dt / 10)
            ball_dot.move_to([ball.position.x/SCALE, ball.position.y/SCALE, 0])
            for dm, (d, verts) in zip(dom_mobs, dominos):
                pts = [[d.local_to_world(v).x/SCALE,
                        d.local_to_world(v).y/SCALE, 0] for v in verts]
                dm.become(Polygon(*pts, color=GREEN, fill_opacity=0.6))
            bp = [bob.position.x/SCALE, bob.position.y/SCALE, 0]
            bob_dot.move_to(bp)
            rod.put_start_and_end_on([1.2, -0.5, 0], bp)
            proj_dot.move_to([proj.position.x/SCALE, proj.position.y/SCALE, 0])

        ball_dot.add_updater(update)
        self.wait(8)
```

## What You Learned

- A Rube Goldberg machine chains physics stages — momentum transfers naturally
- `MovingCameraScene` enables cinematic panning and zooming
- Dominos are tall thin polygons with high friction to grip the floor
- Combine all concepts: gravity, bodies, joints, collisions, shapes, forces
- Slow-motion: multiply dt by a factor < 1 before stepping the space
- No explicit triggers needed — physics handles causality between stages

---

[← Chapter 11: Particles](chapter-11-particles.md) | [Overview →](README.md)
