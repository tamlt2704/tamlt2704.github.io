import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Constraints: Pin Joints, Slide Joints, Springs"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={3}
            prevSlug="pymunk-manim-02-bodies"
            prevTitle="Multiple Bodies"
            nextSlug="pymunk-manim-04-pendulum"
            nextTitle="Pendulum: Pivot Joints and Energy Visualization"
        >
            <Section title="PinJoint: Fixed Distance">
                <Paragraph>
                    A PinJoint connects two bodies at anchor points, keeping them at a fixed distance. Think of it as a rigid rod between two points.
                </Paragraph>
                <Code lang="python" title="PinJoint basics">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Two balls connected by a pin joint
a = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
a.position = (0, 200)
b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
b.position = (80, 200)

sa = pymunk.Circle(a, 10)
sb = pymunk.Circle(b, 10)

# Pin joint: anchors at body centers, fixed distance
joint = pymunk.PinJoint(a, b, (0, 0), (0, 0))

space.add(a, sa, b, sb, joint)`}</Code>
            </Section>

            <Section title="SlideJoint: Min/Max Distance">
                <Paragraph>
                    A SlideJoint is like a PinJoint but allows the distance to vary between a minimum and maximum. The bodies can get closer or farther apart within limits.
                </Paragraph>
                <Code lang="python" title="SlideJoint with limits">{`# SlideJoint: bodies can be 50-150 pixels apart
slide = pymunk.SlideJoint(a, b, (0, 0), (0, 0), min=50, max=150)
space.add(slide)

# The joint only applies force when the distance
# exceeds max or goes below min — otherwise bodies move freely`}</Code>
            </Section>

            <Section title="DampedSpring: Springy Connection">
                <Paragraph>
                    A DampedSpring pulls bodies toward a rest length with configurable stiffness and damping. High stiffness = snappy. High damping = less oscillation.
                </Paragraph>
                <Code lang="python" title="Spring between bodies">{`# DampedSpring: rest_length=100, stiffness=200, damping=5
spring = pymunk.DampedSpring(
    a, b,
    anchor_a=(0, 0), anchor_b=(0, 0),
    rest_length=100,
    stiffness=200,  # force per unit displacement
    damping=5       # energy loss per oscillation
)
space.add(spring)

# Pull body b away — it springs back toward rest_length
b.position = (200, 200)`}</Code>
            </Section>

            <Section title="Visualizing with Lines">
                <Paragraph>
                    Draw a Line between connected bodies each frame. For springs, use a DashedLine to suggest elasticity.
                </Paragraph>
                <Code lang="python" title="Joint visualization scene">{`from manim import *
import pymunk

SCALE = 100

class SpringScene(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        anchor = space.static_body
        bob = pymunk.Body(2, pymunk.moment_for_circle(2, 0, 12))
        bob.position = (150, 0)
        bob_s = pymunk.Circle(bob, 12)
        spring = pymunk.DampedSpring(
            anchor, bob, (0, 0), (0, 0),
            rest_length=100, stiffness=150, damping=3
        )
        space.add(bob, bob_s, spring)

        dot = Dot(radius=0.12, color=YELLOW)
        pivot = Dot(ORIGIN, radius=0.05, color=WHITE)
        line = DashedLine(ORIGIN, RIGHT, color=GREEN)
        self.add(pivot, line, dot)

        def sync(mob, dt):
            space.step(dt)
            p = [bob.position.x/SCALE, bob.position.y/SCALE, 0]
            dot.move_to(p)
            line.become(DashedLine(ORIGIN, p, color=GREEN))

        dot.add_updater(sync)
        self.wait(5)`}</Code>
                <Note>
                    Using line.become() each frame recreates the line with the new endpoint. For performance with many joints, consider updating start/end directly with put_start_and_end_on().
                </Note>
            </Section>
        </BlogPost>
    );
}
