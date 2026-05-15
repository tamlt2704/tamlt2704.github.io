import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Gears & Motors: Constant Rotation"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={10}
            prevSlug="pymunk-manim-09-chain"
            prevTitle="Ragdoll & Chain: Linked Bodies"
            nextSlug="pymunk-manim-11-particles"
            nextTitle="Fluid-like Particles: Hundreds of Tiny Circles"
        >
            <Section title="SimpleMotor: Constant Angular Velocity">
                <Paragraph>
                    A SimpleMotor applies torque to maintain a target angular velocity between two bodies. Pin one body to static_body and the motor spins it at a constant rate — like an electric motor.
                </Paragraph>
                <Code lang="python" title="SimpleMotor basics">{`import pymunk
import math

space = pymunk.Space()
space.gravity = (0, -900)

# Spinning wheel pinned at center
wheel = pymunk.Body(5, pymunk.moment_for_circle(5, 0, 40))
wheel.position = (0, 0)
wheel_shape = pymunk.Circle(wheel, 40)
space.add(wheel, wheel_shape)

# Pin it in place so it can only rotate
pivot = pymunk.PivotJoint(space.static_body, wheel, (0, 0))
space.add(pivot)

# Motor: spins wheel at 2 radians/sec
motor = pymunk.SimpleMotor(space.static_body, wheel, rate=2.0)
space.add(motor)

# The wheel now rotates at constant speed
# regardless of friction or collisions (within torque limits)`}</Code>
            </Section>

            <Section title="GearJoint: Linked Rotation">
                <Paragraph>
                    A GearJoint forces two bodies to rotate at a fixed ratio. A ratio of 2.0 means body_b rotates twice for every rotation of body_a — like meshing gears of different sizes.
                </Paragraph>
                <Code lang="python" title="Gear joint">{`# Second wheel, half the size
wheel2 = pymunk.Body(2, pymunk.moment_for_circle(2, 0, 20))
wheel2.position = (65, 0)  # adjacent to first wheel
wheel2_shape = pymunk.Circle(wheel2, 20)
space.add(wheel2, wheel2_shape)

# Pin it in place
pivot2 = pymunk.PivotJoint(space.static_body, wheel2, (65, 0))
space.add(pivot2)

# Gear joint: ratio = -2.0 (opposite direction, double speed)
# Negative ratio = opposite rotation direction
gear = pymunk.GearJoint(wheel, wheel2, phase=0.0, ratio=-2.0)
space.add(gear)

# wheel rotates at 2 rad/s → wheel2 rotates at 4 rad/s (opposite)`}</Code>
                <Note>
                    The phase parameter offsets the initial angle relationship. A phase of 0 means they start aligned. Adjust phase to mesh gear teeth visually.
                </Note>
            </Section>

            <Section title="Rotating Polygon Gears">
                <Paragraph>
                    Render gears as polygons with &quot;teeth&quot; — star-shaped vertices. Rotate the manim Polygon by reading body.angle each frame.
                </Paragraph>
                <Code lang="python" title="Gear visualization">{`from manim import *
import pymunk, math

SCALE = 100

class GearScene(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, 0)  # no gravity for gear demo

        # Gear 1: 8 teeth
        def gear_verts(radius, teeth):
            verts = []
            for i in range(teeth * 2):
                angle = i * math.pi / teeth
                r = radius if i % 2 == 0 else radius * 0.7
                verts.append((r * math.cos(angle), r * math.sin(angle)))
            return verts

        v1 = gear_verts(40, 8)
        g1 = pymunk.Body(5, pymunk.moment_for_poly(5, v1))
        g1.position = (-50, 0)
        space.add(g1, pymunk.Poly(g1, v1))
        space.add(pymunk.PivotJoint(space.static_body, g1, (-50, 0)))

        v2 = gear_verts(25, 5)
        g2 = pymunk.Body(2, pymunk.moment_for_poly(2, v2))
        g2.position = (30, 0)
        space.add(g2, pymunk.Poly(g2, v2))
        space.add(pymunk.PivotJoint(space.static_body, g2, (30, 0)))

        motor = pymunk.SimpleMotor(space.static_body, g1, rate=1.5)
        gear = pymunk.GearJoint(g1, g2, 0, -1.6)
        space.add(motor, gear)

        p1 = Polygon(*[[x/SCALE, y/SCALE, 0] for x,y in v1],
                     color=BLUE, fill_opacity=0.4)
        p2 = Polygon(*[[x/SCALE, y/SCALE, 0] for x,y in v2],
                     color=RED, fill_opacity=0.4)
        self.add(p1, p2)

        def sync(mob, dt):
            space.step(dt)
            pts1 = [g1.local_to_world(v) for v in v1]
            p1.become(Polygon(*[[p.x/SCALE, p.y/SCALE, 0] for p in pts1],
                              color=BLUE, fill_opacity=0.4))
            pts2 = [g2.local_to_world(v) for v in v2]
            p2.become(Polygon(*[[p.x/SCALE, p.y/SCALE, 0] for p in pts2],
                              color=RED, fill_opacity=0.4))

        p1.add_updater(sync)
        self.wait(6)`}</Code>
            </Section>

            <Section title="Motor-Driven Conveyor">
                <Paragraph>
                    Combine a motor with a gear train to drive a conveyor system. The motor spins a wheel, gears transfer rotation to a second wheel, and objects ride between them.
                </Paragraph>
                <Code lang="python" title="Motor-driven system">{`# Motor drives wheel1, gear transfers to wheel2
# Objects placed between wheels get carried along

# Wheel 1 (driven by motor)
w1 = pymunk.Body(5, pymunk.moment_for_circle(5, 0, 30))
w1.position = (-100, -150)
space.add(w1, pymunk.Circle(w1, 30))
space.add(pymunk.PivotJoint(space.static_body, w1, (-100, -150)))
space.add(pymunk.SimpleMotor(space.static_body, w1, rate=3.0))

# Wheel 2 (linked by gear joint, same direction)
w2 = pymunk.Body(5, pymunk.moment_for_circle(5, 0, 30))
w2.position = (100, -150)
space.add(w2, pymunk.Circle(w2, 30))
space.add(pymunk.PivotJoint(space.static_body, w2, (100, -150)))
space.add(pymunk.GearJoint(w1, w2, 0, 1.0))  # same speed, same dir

# Belt surface between wheels (kinematic, surface_velocity)
belt = pymunk.Segment(space.static_body, (-100, -120), (100, -120), 3)
belt.friction = 0.9
belt.surface_velocity = (-90, 0)  # matches wheel surface speed
space.add(belt)`}</Code>
            </Section>
        </BlogPost>
    );
}
