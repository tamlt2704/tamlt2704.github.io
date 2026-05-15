import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Polygons & Segments: Beyond Circles"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={6}
            prevSlug="pymunk-manim-05-collisions"
            prevTitle="Collisions & Callbacks: Flash on Impact"
            nextSlug="pymunk-manim-07-forces"
            nextTitle="Forces & Impulses: Push Things Around"
        >
            <Section title="Poly Vertices">
                <Paragraph>
                    pymunk.Poly takes a body and a list of vertices (local coordinates, counter-clockwise). The physics engine handles convex polygons natively. For concave shapes, decompose into multiple convex polys.
                </Paragraph>
                <Code lang="python" title="Creating polygon shapes">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Triangle
tri_verts = [(-20, -15), (20, -15), (0, 20)]
tri_body = pymunk.Body(2, pymunk.moment_for_poly(2, tri_verts))
tri_body.position = (-100, 200)
tri_shape = pymunk.Poly(tri_body, tri_verts)
tri_shape.elasticity = 0.6
tri_shape.friction = 0.5
space.add(tri_body, tri_shape)

# Box (rectangle)
box_verts = [(-25, -15), (25, -15), (25, 15), (-25, 15)]
box_body = pymunk.Body(3, pymunk.moment_for_poly(3, box_verts))
box_body.position = (100, 250)
box_shape = pymunk.Poly(box_body, box_verts)
box_shape.elasticity = 0.4
space.add(box_body, box_shape)

# Pentagon
import math
pent_verts = [(20*math.cos(a), 20*math.sin(a))
              for a in [i*2*math.pi/5 for i in range(5)]]
pent_body = pymunk.Body(2, pymunk.moment_for_poly(2, pent_verts))
pent_body.position = (0, 300)
space.add(pent_body, pymunk.Poly(pent_body, pent_verts))`}</Code>
            </Section>

            <Section title="Segment Shapes">
                <Paragraph>
                    pymunk.Segment creates a line with thickness — useful for walls, ramps, and thin platforms. Unlike Poly, segments have no interior volume.
                </Paragraph>
                <Code lang="python" title="Segment shapes">{`# Angled ramp
ramp = pymunk.Segment(space.static_body, (-300, 100), (-50, -50), 4)
ramp.elasticity = 0.5
ramp.friction = 0.7
space.add(ramp)

# V-shaped funnel
left_wall = pymunk.Segment(space.static_body, (-200, 200), (-50, 0), 3)
right_wall = pymunk.Segment(space.static_body, (200, 200), (50, 0), 3)
left_wall.friction = 0.3
right_wall.friction = 0.3
space.add(left_wall, right_wall)`}</Code>
            </Section>

            <Section title="Rotating Polygon Mobject">
                <Paragraph>
                    To render a rotating polygon in manim, transform local vertices to world space each frame using body.local_to_world(). Then rebuild the Polygon mobject.
                </Paragraph>
                <Code lang="python" title="Syncing rotated polygons">{`from manim import *
import pymunk

SCALE = 100

class PolyScene(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        verts = [(-25, -15), (25, -15), (25, 15), (-25, 15)]
        body = pymunk.Body(3, pymunk.moment_for_poly(3, verts))
        body.position = (0, 250)
        body.angular_velocity = 2.0  # spin it
        shape = pymunk.Poly(body, verts)
        shape.elasticity = 0.5
        shape.friction = 0.6
        space.add(body, shape)

        floor = pymunk.Segment(space.static_body, (-400,-250),(400,-250), 5)
        floor.friction = 0.8
        space.add(floor)

        poly_mob = Polygon(*[[v[0]/SCALE, v[1]/SCALE, 0] for v in verts],
                           color=GREEN, fill_opacity=0.5)
        floor_line = Line(LEFT*4, RIGHT*4).shift(DOWN*2.5)
        self.add(floor_line, poly_mob)

        def sync(mob, dt):
            for _ in range(3):
                space.step(dt/3)
            world_pts = [body.local_to_world(v) for v in verts]
            manim_pts = [[p.x/SCALE, p.y/SCALE, 0] for p in world_pts]
            mob.become(Polygon(*manim_pts, color=GREEN, fill_opacity=0.5))

        poly_mob.add_updater(sync)
        self.wait(5)`}</Code>
                <Note>
                    body.local_to_world() applies both translation and rotation. This is the key function for rendering any non-circular shape correctly.
                </Note>
            </Section>

            <Section title="Mixed Shape Scene">
                <Paragraph>
                    Combine circles, polygons, and segments in one scene. Each shape type needs its own rendering approach: Dot for circles, Polygon for polys, Line for segments.
                </Paragraph>
                <Code lang="python" title="Mixed shapes falling">{`# Create a mix of shapes
shapes_data = []

# Circles
for i in range(5):
    b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 12))
    b.position = (-150 + i*60, 350)
    s = pymunk.Circle(b, 12)
    s.elasticity = 0.7
    space.add(b, s)
    shapes_data.append(("circle", b, 12))

# Boxes
for i in range(3):
    v = [(-15, -10), (15, -10), (15, 10), (-15, 10)]
    b = pymunk.Body(2, pymunk.moment_for_poly(2, v))
    b.position = (-80 + i*80, 400)
    b.angular_velocity = 1.5
    s = pymunk.Poly(b, v)
    s.elasticity = 0.5
    space.add(b, s)
    shapes_data.append(("poly", b, v))`}</Code>
            </Section>
        </BlogPost>
    );
}
