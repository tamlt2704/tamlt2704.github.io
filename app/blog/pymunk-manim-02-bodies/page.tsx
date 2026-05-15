import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Multiple Bodies: Dynamic, Static, and Kinematic"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={2}
            prevSlug="pymunk-manim-01-gravity"
            prevTitle="Gravity & Bouncing"
            nextSlug="pymunk-manim-03-joints"
            nextTitle="Constraints: Pin Joints, Slide Joints, Springs"
        >
            <Section title="Body Types">
                <Paragraph>
                    Pymunk has three body types. Dynamic bodies respond to forces and collisions. Static bodies never move (floors, walls). Kinematic bodies move on a set path but aren&apos;t affected by collisions — think moving platforms.
                </Paragraph>
                <Code lang="python" title="Three body types">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Dynamic: affected by gravity and collisions
ball = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
ball.position = (0, 300)
ball_shape = pymunk.Circle(ball, 10)
space.add(ball, ball_shape)

# Static: immovable (walls, floors)
wall = pymunk.Body(body_type=pymunk.Body.STATIC)
wall_shape = pymunk.Segment(wall, (-300, -200), (300, -200), 5)
space.add(wall, wall_shape)

# Kinematic: moves at set velocity, ignores forces
platform = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
platform.position = (-200, 0)
platform.velocity = (100, 0)  # slides right
plat_shape = pymunk.Segment(platform, (-50, 0), (50, 0), 5)
space.add(platform, plat_shape)`}</Code>
            </Section>

            <Section title="Raining Balls">
                <Paragraph>
                    Spawn many dynamic bodies at random positions. Each gets its own mass, radius, and color. The physics engine handles all collisions automatically.
                </Paragraph>
                <Code lang="python" title="Spawning many bodies">{`import random

bodies = []
for i in range(30):
    r = random.uniform(8, 20)
    mass = r * 0.1
    body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, r))
    body.position = (random.uniform(-250, 250), 300 + i * 30)
    shape = pymunk.Circle(body, r)
    shape.elasticity = 0.7
    shape.friction = 0.3
    space.add(body, shape)
    bodies.append((body, r))`}</Code>
            </Section>

            <Section title="VGroup Batch Sync">
                <Paragraph>
                    With many bodies, create a VGroup of Dots and sync them all in one updater. This is more efficient than individual updaters.
                </Paragraph>
                <Code lang="python" title="Batch sync with VGroup">{`from manim import *
import pymunk, random

SCALE = 100

class RainingBalls(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.elasticity = 0.6
        space.add(floor)

        bodies = []
        dots = VGroup()
        colors = [RED, BLUE, GREEN, YELLOW, ORANGE, PURPLE]
        for i in range(30):
            r = random.uniform(8, 18)
            mass = r * 0.1
            b = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, r))
            b.position = (random.uniform(-250, 250), 300 + i * 25)
            s = pymunk.Circle(b, r)
            s.elasticity = 0.7
            space.add(b, s)
            bodies.append(b)
            dots.add(Dot(radius=r/SCALE, color=random.choice(colors)))

        floor_line = Line(LEFT * 4, RIGHT * 4).shift(DOWN * 2.5)
        self.add(floor_line, dots)

        def sync(group, dt):
            for _ in range(3):
                space.step(dt / 3)
            for dot, body in zip(group, bodies):
                dot.move_to([body.position.x / SCALE,
                             body.position.y / SCALE, 0])

        dots.add_updater(sync)
        self.wait(6)`}</Code>
                <Note>
                    Sub-stepping (stepping 3 times at dt/3) improves stability when many bodies collide simultaneously. More sub-steps = more accurate but slower.
                </Note>
            </Section>

            <Section title="Kinematic Platform Scene">
                <Paragraph>
                    A kinematic body slides back and forth. Balls land on it and ride along. Sync the platform visual with a Line mobject.
                </Paragraph>
                <Code lang="python" title="Moving platform">{`# Kinematic platform that reverses direction
platform = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
platform.position = (0, -100)
platform.velocity = (150, 0)
plat_shape = pymunk.Segment(platform, (-60, 0), (60, 0), 4)
plat_shape.friction = 0.9
space.add(platform, plat_shape)

# In the updater, reverse at edges:
def sync(mob, dt):
    space.step(dt)
    if abs(platform.position.x) > 250:
        platform.velocity = (-platform.velocity.x, 0)
    # Sync platform line
    px = platform.position.x / SCALE
    py = platform.position.y / SCALE
    plat_line.put_start_and_end_on(
        [px - 0.6, py, 0], [px + 0.6, py, 0]
    )`}</Code>
            </Section>
        </BlogPost>
    );
}
