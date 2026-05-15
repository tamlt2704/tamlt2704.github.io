import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Friction & Materials: Ramps and Conveyor Belts"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={8}
            prevSlug="pymunk-manim-07-forces"
            prevTitle="Forces & Impulses: Push Things Around"
            nextSlug="pymunk-manim-09-chain"
            nextTitle="Ragdoll & Chain: Linked Bodies"
        >
            <Section title="Shape Friction">
                <Paragraph>
                    Friction controls how much shapes resist sliding against each other. A value of 0 means frictionless ice. A value of 1.0 means high grip. The effective friction between two shapes is their product: shape_a.friction * shape_b.friction.
                </Paragraph>
                <Code lang="python" title="Friction values">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Three blocks on a ramp with different friction
ramp = pymunk.Segment(space.static_body, (-300, 100), (200, -200), 5)
ramp.friction = 0.7
space.add(ramp)

# Ice block: slides freely
ice = pymunk.Body(1, pymunk.moment_for_poly(1, [(-15,-10),(15,-10),(15,10),(-15,10)]))
ice.position = (-250, 150)
ice_s = pymunk.Poly(ice, [(-15,-10),(15,-10),(15,10),(-15,10)])
ice_s.friction = 0.05  # nearly frictionless
space.add(ice, ice_s)

# Rubber block: grips hard
rubber = pymunk.Body(1, pymunk.moment_for_poly(1, [(-15,-10),(15,-10),(15,10),(-15,10)]))
rubber.position = (-200, 180)
rubber_s = pymunk.Poly(rubber, [(-15,-10),(15,-10),(15,10),(-15,10)])
rubber_s.friction = 0.95  # high grip
space.add(rubber, rubber_s)

# Wood block: moderate
wood = pymunk.Body(1, pymunk.moment_for_poly(1, [(-15,-10),(15,-10),(15,10),(-15,10)]))
wood.position = (-150, 210)
wood_s = pymunk.Poly(wood, [(-15,-10),(15,-10),(15,10),(-15,10)])
wood_s.friction = 0.4
space.add(wood, wood_s)`}</Code>
            </Section>

            <Section title="Surface Velocity: Conveyor Belts">
                <Paragraph>
                    surface_velocity on a shape makes its surface move relative to the body — like a conveyor belt. Objects touching it get pushed along by friction.
                </Paragraph>
                <Code lang="python" title="Conveyor belt">{`# Conveyor belt: static segment with surface velocity
belt = pymunk.Segment(space.static_body, (-150, -200), (150, -200), 5)
belt.friction = 0.9  # high friction to grip objects
belt.surface_velocity = (-200, 0)  # surface moves left at 200 px/s
space.add(belt)

# Drop a box onto the belt — it gets pushed left
box = pymunk.Body(1, pymunk.moment_for_poly(1, [(-12,-12),(12,-12),(12,12),(-12,12)]))
box.position = (0, -100)
box_s = pymunk.Poly(box, [(-12,-12),(12,-12),(12,12),(-12,12)])
box_s.friction = 0.7
space.add(box, box_s)

# The box slides left because the belt surface
# drags it via friction. Lower box friction = less drag.`}</Code>
                <Note>
                    surface_velocity is relative to the shape&apos;s body. For a static body, it&apos;s in world coordinates. For a moving body, it adds to the body&apos;s own velocity.
                </Note>
            </Section>

            <Section title="Sliding Block Scene">
                <Paragraph>
                    Visualize blocks sliding down a ramp at different speeds based on their friction. Color-code them: blue for ice, brown for wood, red for rubber.
                </Paragraph>
                <Code lang="python" title="Ramp race scene">{`from manim import *
import pymunk

SCALE = 100

class RampRace(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        ramp = pymunk.Segment(space.static_body, (-300, 100), (200, -200), 5)
        ramp.friction = 0.7
        space.add(ramp)

        blocks = []
        configs = [
            ((-250, 160), 0.05, BLUE, "Ice"),
            ((-220, 180), 0.4, GOLD, "Wood"),
            ((-190, 200), 0.95, RED, "Rubber"),
        ]
        verts = [(-12, -8), (12, -8), (12, 8), (-12, 8)]
        for pos, fric, color, name in configs:
            b = pymunk.Body(1, pymunk.moment_for_poly(1, verts))
            b.position = pos
            s = pymunk.Poly(b, verts)
            s.friction = fric
            space.add(b, s)
            blocks.append((b, verts, color))

        ramp_line = Line([-3, 1, 0], [2, -2, 0], color=GREY)
        self.add(ramp_line)

        mobs = VGroup()
        for b, v, color in blocks:
            mobs.add(Polygon(*[[p[0]/SCALE, p[1]/SCALE, 0] for p in v],
                             color=color, fill_opacity=0.7))
        self.add(mobs)

        def sync(group, dt):
            for _ in range(3):
                space.step(dt/3)
            for mob, (b, v, c) in zip(group, blocks):
                pts = [b.local_to_world(p) for p in v]
                mob.become(Polygon(*[[p.x/SCALE, p.y/SCALE, 0]
                           for p in pts], color=c, fill_opacity=0.7))

        mobs.add_updater(sync)
        self.wait(4)`}</Code>
            </Section>

            <Section title="Conveyor Belt Animation">
                <Paragraph>
                    Render the conveyor belt as a dashed line with small arrows indicating direction. Objects landing on it slide along automatically.
                </Paragraph>
                <Code lang="python" title="Conveyor visual">{`# Conveyor belt visual with direction arrows
belt_line = Line(LEFT*1.5, RIGHT*1.5, color=YELLOW).shift(DOWN*2)
arrows = VGroup(*[
    Arrow(start=[x, -2, 0], end=[x-0.3, -2, 0],
          color=YELLOW_A, stroke_width=2, max_tip_length_to_length_ratio=0.5)
    for x in [-1.0, -0.3, 0.4, 1.1]
])
self.add(belt_line, arrows)

# The arrows show surface_velocity direction
# Objects on the belt drift left, matching the arrows`}</Code>
            </Section>
        </BlogPost>
    );
}
