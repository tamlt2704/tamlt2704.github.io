# Chapter 6: Shapes — Polygons & Segments

[← Chapter 5: Collisions](chapter-05-collisions.md) | [Chapter 7: Forces →](chapter-07-forces.md)

---

## Pymunk Concept: Shape Types

Beyond circles, pymunk supports polygons and segments. Each has its own moment-of-inertia function.

| Shape | Constructor | Moment function |
|-------|------------|-----------------|
| `Circle` | `Circle(body, radius)` | `moment_for_circle(mass, 0, r)` |
| `Poly` | `Poly(body, vertices)` | `moment_for_poly(mass, vertices)` |
| `Segment` | `Segment(body, a, b, radius)` | `moment_for_segment(mass, a, b, r)` |

```python
import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# A box (polygon) — vertices are local to the body
mass = 2
vertices = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
moment = pymunk.moment_for_poly(mass, vertices)
box_body = pymunk.Body(mass, moment)
box_body.position = (0, 200)
box_shape = pymunk.Poly(box_body, vertices)
box_shape.elasticity = 0.4
box_shape.friction = 0.7

# A triangle
tri_verts = [(0, 30), (-25, -15), (25, -15)]
tri_moment = pymunk.moment_for_poly(1, tri_verts)
tri_body = pymunk.Body(1, tri_moment)
tri_body.position = (100, 250)
tri_shape = pymunk.Poly(tri_body, tri_verts)

space.add(box_body, box_shape, tri_body, tri_shape)
```

Vertices are in **local coordinates** relative to the body's center. When the body rotates, the vertices rotate with it. Use `shape.get_vertices()` to get world-space positions for rendering.

## Manim Rendering

To render a rotating polygon, create a manim `Polygon` and update its vertices each frame. We transform local pymunk vertices to world coordinates using the body's position and angle.

```python
from manim import *
import pymunk

SCALE = 100

def pymunk_to_manim_verts(body, local_verts):
    """Convert local pymunk vertices to manim world coords."""
    world_verts = []
    for v in local_verts:
        rotated = body.local_to_world(v)
        world_verts.append([rotated.x / SCALE, rotated.y / SCALE, 0])
    return world_verts

class ShapeVis(Scene):
    def construct(self):
        box_mob = Polygon(*initial_verts, color=GREEN, fill_opacity=0.4)

        def update_poly(mob):
            new_verts = pymunk_to_manim_verts(box_body, vertices)
            mob.become(Polygon(*new_verts, color=GREEN, fill_opacity=0.4))

        box_mob.add_updater(update_poly)
        self.add(box_mob)
```

`body.local_to_world(v)` handles rotation and translation in one call — no manual trig needed.

## Full Scene

```python
from manim import *
import pymunk

SCALE = 100

class FallingShapes(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)
        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.elasticity = 0.3
        floor.friction = 0.8
        space.add(floor)

        box_verts = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
        box_body = pymunk.Body(2, pymunk.moment_for_poly(2, box_verts))
        box_body.position = (-50, 250)
        box_body.angle = 0.3
        box_shape = pymunk.Poly(box_body, box_verts)
        box_shape.elasticity = 0.3
        box_shape.friction = 0.7
        space.add(box_body, box_shape)

        tri_verts = [(0, 25), (-20, -12), (20, -12)]
        tri_body = pymunk.Body(1, pymunk.moment_for_poly(1, tri_verts))
        tri_body.position = (80, 300)
        tri_shape = pymunk.Poly(tri_body, tri_verts)
        tri_shape.elasticity = 0.5
        space.add(tri_body, tri_shape)

        def make_poly(body, verts, color):
            pts = [[body.local_to_world(v).x/SCALE,
                    body.local_to_world(v).y/SCALE, 0] for v in verts]
            return Polygon(*pts, color=color, fill_opacity=0.4)

        box_mob = make_poly(box_body, box_verts, GREEN)
        tri_mob = make_poly(tri_body, tri_verts, ORANGE)
        floor_line = Line(LEFT*4, RIGHT*4, color=WHITE).shift(DOWN*2.5)
        self.add(floor_line, box_mob, tri_mob)

        def update(group, dt):
            for _ in range(10):
                space.step(dt / 10)
            for body, verts, mob, color in [(box_body, box_verts, box_mob, GREEN),
                                             (tri_body, tri_verts, tri_mob, ORANGE)]:
                pts = [[body.local_to_world(v).x/SCALE,
                        body.local_to_world(v).y/SCALE, 0] for v in verts]
                mob.become(Polygon(*pts, color=color, fill_opacity=0.4))

        VGroup(box_mob, tri_mob).add_updater(update)
        self.wait(5)
```

## What You Learned

- `Poly(body, vertices)` creates convex polygon shapes from local-coordinate vertices
- `Segment(body, a, b, radius)` creates thick line shapes — good for walls and platforms
- `moment_for_poly` calculates rotational inertia for polygon mass distribution
- `body.local_to_world(v)` converts a local vertex to world position (handles rotation)
- In manim, `mob.become(Polygon(...))` rebuilds the polygon each frame to match rotation
- Polygons must be **convex** in pymunk — decompose concave shapes into multiple convex parts

---

[← Chapter 5: Collisions](chapter-05-collisions.md) | [Chapter 7: Forces →](chapter-07-forces.md)
