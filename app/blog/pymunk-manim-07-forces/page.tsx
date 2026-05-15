import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Forces & Impulses: Push Things Around"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={7}
            prevSlug="pymunk-manim-06-shapes"
            prevTitle="Polygons & Segments: Beyond Circles"
            nextSlug="pymunk-manim-08-friction"
            nextTitle="Friction & Materials: Ramps and Conveyor Belts"
        >
            <Section title="apply_force vs apply_impulse">
                <Paragraph>
                    Forces are continuous — they push every frame (like wind or a rocket). Impulses are instantaneous — a single kick (like a bat hitting a ball). Forces need to be applied every step; impulses are one-shot.
                </Paragraph>
                <Code lang="python" title="Forces and impulses">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

body = pymunk.Body(2, pymunk.moment_for_circle(2, 0, 15))
body.position = (0, 0)
shape = pymunk.Circle(body, 15)
space.add(body, shape)

# Force: applied continuously (call every step)
# Args: force vector, application point (local coords)
body.apply_force_at_local_point((500, 0), (0, 0))  # push right

# Impulse: instantaneous velocity change
# Args: impulse vector, application point (world coords)
body.apply_impulse_at_world_point((0, 1000), body.position)  # kick up

# Off-center impulse causes rotation
body.apply_impulse_at_local_point((200, 0), (0, 15))  # spin`}</Code>
            </Section>

            <Section title="Timed Impulse: Launch After Delay">
                <Paragraph>
                    Track elapsed time and fire an impulse at a specific moment. This creates a &quot;launch&quot; effect — the ball sits still, then gets kicked.
                </Paragraph>
                <Code lang="python" title="Delayed launch">{`from manim import *
import pymunk

SCALE = 100

class LaunchBall(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 12))
        body.position = (-200, -200)
        shape = pymunk.Circle(body, 12)
        shape.elasticity = 0.7
        floor = pymunk.Segment(space.static_body, (-400,-250),(400,-250), 5)
        floor.elasticity = 0.8
        space.add(body, shape, floor)

        dot = Dot(radius=0.12, color=RED)
        floor_line = Line(LEFT*4, RIGHT*4).shift(DOWN*2.5)
        self.add(floor_line, dot)

        launched = [False]
        elapsed = [0.0]

        def sync(mob, dt):
            elapsed[0] += dt
            if not launched[0] and elapsed[0] > 1.5:
                body.apply_impulse_at_world_point(
                    (400, 800), body.position)
                launched[0] = True
            space.step(dt)
            mob.move_to([body.position.x/SCALE,
                         body.position.y/SCALE, 0])

        dot.add_updater(sync)
        self.wait(5)`}</Code>
            </Section>

            <Section title="Arrow Visualization">
                <Paragraph>
                    Show the force or velocity as an Arrow mobject. Scale the arrow length proportional to the vector magnitude. Update it each frame.
                </Paragraph>
                <Code lang="python" title="Force arrow">{`# Arrow showing velocity direction and magnitude
arrow = Arrow(ORIGIN, RIGHT, color=ORANGE, buff=0)
self.add(arrow)

def sync(mob, dt):
    space.step(dt)
    pos = [body.position.x/SCALE, body.position.y/SCALE, 0]
    dot.move_to(pos)

    # Velocity arrow (scaled down for display)
    vx = body.velocity.x / 500
    vy = body.velocity.y / 500
    end = [pos[0] + vx, pos[1] + vy, 0]
    if abs(vx) + abs(vy) > 0.05:
        arrow.become(Arrow(pos, end, color=ORANGE, buff=0,
                           stroke_width=3, max_tip_length_to_length_ratio=0.2))
    else:
        arrow.become(Dot(pos, radius=0.01, fill_opacity=0))`}</Code>
                <Note>
                    The arrow shows where the ball is heading and how fast. Long arrow = fast. Short arrow = slow. It rotates naturally as the ball arcs through the air.
                </Note>
            </Section>

            <Section title="Continuous Force: Wind">
                <Paragraph>
                    Apply a sideways force every frame to simulate wind. The ball&apos;s trajectory curves instead of following a clean parabola.
                </Paragraph>
                <Code lang="python" title="Wind force">{`WIND = (300, 0)  # constant rightward wind

def sync(mob, dt):
    # Apply wind force every frame
    body.apply_force_at_world_point(WIND, body.position)
    space.step(dt)
    mob.move_to([body.position.x/SCALE,
                 body.position.y/SCALE, 0])

# The ball drifts right as it falls
# Increase WIND magnitude for stronger effect
# Use negative x for leftward wind
# Add randomness for turbulence:
# WIND = (300 + random.uniform(-50, 50), random.uniform(-20, 20))`}</Code>
            </Section>
        </BlogPost>
    );
}
