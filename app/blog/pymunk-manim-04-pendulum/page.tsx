import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Pendulum: Pivot Joints and Energy Visualization"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={4}
            prevSlug="pymunk-manim-03-joints"
            prevTitle="Constraints: Pin Joints, Slide Joints, Springs"
            nextSlug="pymunk-manim-05-collisions"
            nextTitle="Collisions & Callbacks: Flash on Impact"
        >
            <Section title="PivotJoint: Rotation Around a Point">
                <Paragraph>
                    A PivotJoint pins two bodies at a single world-space point. The bob rotates freely around the pivot. Unlike PinJoint (which constrains distance between anchors), PivotJoint constrains a shared point.
                </Paragraph>
                <Code lang="python" title="Pendulum setup">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Bob: heavy circle
bob = pymunk.Body(5, pymunk.moment_for_circle(5, 0, 15))
bob.position = (150, 0)  # offset from pivot to start swinging

bob_shape = pymunk.Circle(bob, 15)
bob_shape.elasticity = 0.0
space.add(bob, bob_shape)

# PivotJoint: bob rotates around (0, 100)
pivot = pymunk.PivotJoint(space.static_body, bob, (0, 100))
space.add(pivot)

# The bob swings because gravity pulls it down
# and the pivot constrains it to a circular arc`}</Code>
            </Section>

            <Section title="Swinging Bob Scene">
                <Paragraph>
                    Render the pendulum with a rod (Line) from pivot to bob, and a TracedPath showing the arc.
                </Paragraph>
                <Code lang="python" title="Pendulum animation">{`from manim import *
import pymunk

SCALE = 100

class Pendulum(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        bob = pymunk.Body(5, pymunk.moment_for_circle(5, 0, 15))
        bob.position = (200, 100)  # start displaced
        bob_s = pymunk.Circle(bob, 15)
        pivot_pt = (0, 100)
        pj = pymunk.PivotJoint(space.static_body, bob, pivot_pt)
        space.add(bob, bob_s, pj)

        dot = Dot(radius=0.15, color=YELLOW)
        pivot_dot = Dot([0, 1, 0], radius=0.05, color=WHITE)
        rod = Line(ORIGIN, ORIGIN, color=GREY, stroke_width=3)
        trail = TracedPath(dot.get_center, stroke_color=YELLOW_A,
                           stroke_opacity=0.4)
        self.add(pivot_dot, rod, trail, dot)

        def sync(mob, dt):
            for _ in range(4):
                space.step(dt / 4)
            p = [bob.position.x/SCALE, bob.position.y/SCALE, 0]
            dot.move_to(p)
            rod.put_start_and_end_on([0, 1, 0], p)

        dot.add_updater(sync)
        self.wait(6)`}</Code>
            </Section>

            <Section title="Energy Bar Visualization">
                <Paragraph>
                    Show kinetic and potential energy as stacked bars. Kinetic energy peaks at the bottom of the swing, potential energy peaks at the top. Total energy stays roughly constant (minus damping).
                </Paragraph>
                <Code lang="python" title="Energy bars">{`# Inside the updater, compute energies:
def sync(mob, dt):
    for _ in range(4):
        space.step(dt / 4)
    p = [bob.position.x/SCALE, bob.position.y/SCALE, 0]
    dot.move_to(p)
    rod.put_start_and_end_on([0, 1, 0], p)

    # Kinetic energy: 0.5 * m * v^2
    ke = 0.5 * bob.mass * bob.velocity.length**2
    # Potential energy: m * g * h (relative to lowest point)
    h = bob.position.y - (pivot_pt[1] - 200)  # height above bottom
    pe = bob.mass * 900 * h

    # Normalize for display
    max_e = bob.mass * 900 * 400
    ke_bar.stretch_to_fit_height(max(ke/max_e * 2, 0.01), about_edge=DOWN)
    pe_bar.stretch_to_fit_height(max(pe/max_e * 2, 0.01), about_edge=DOWN)`}</Code>
                <Note>
                    The energy bars show conservation of energy in real time. As the bob swings down, the blue KE bar grows while the green PE bar shrinks — and vice versa at the top.
                </Note>
            </Section>

            <Section title="Double Pendulum (Bonus)">
                <Paragraph>
                    Chain two PivotJoints for chaotic motion. The second bob&apos;s path is wildly unpredictable — a classic demonstration of chaos theory.
                </Paragraph>
                <Code lang="python" title="Double pendulum">{`# Second bob attached to first
bob2 = pymunk.Body(3, pymunk.moment_for_circle(3, 0, 12))
bob2.position = (300, 0)
bob2_s = pymunk.Circle(bob2, 12)

# Pivot at bob1's current position (they share a point)
pj2 = pymunk.PivotJoint(bob, bob2, bob.position)
space.add(bob2, bob2_s, pj2)

# Render with a second rod and dot
dot2 = Dot(radius=0.12, color=RED)
rod2 = Line(ORIGIN, ORIGIN, color=GREY, stroke_width=2)
trail2 = TracedPath(dot2.get_center, stroke_color=RED_A,
                    stroke_opacity=0.3)`}</Code>
            </Section>
        </BlogPost>
    );
}
