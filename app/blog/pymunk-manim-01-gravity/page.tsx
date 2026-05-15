import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Gravity & Bouncing: Your First Physics Animation"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={1}
            prevSlug="pymunk-manim-00-setup"
            prevTitle="Pymunk + Manim: Physics Animations from Python"
            nextSlug="pymunk-manim-02-bodies"
            nextTitle="Multiple Bodies"
        >
            <Section title="Gravity and Elasticity">
                <Paragraph>
                    Gravity is a vector on the space. Elasticity on shapes controls how much energy is preserved on bounce. An elasticity of 1.0 means perfect bounce — the ball returns to its original height. Below 1.0, energy is lost each bounce.
                </Paragraph>
                <Code lang="python" title="Tuning gravity and bounce">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)  # experiment: try -400, -1800

body = pymunk.Body(mass=1, moment=pymunk.moment_for_circle(1, 0, 15))
body.position = (0, 300)

shape = pymunk.Circle(body, 15)
shape.elasticity = 0.85  # loses 15% energy per bounce
shape.friction = 0.5

space.add(body, shape)`}</Code>
            </Section>

            <Section title="Static Floor">
                <Paragraph>
                    A static body never moves. Attach a segment shape to create an infinite floor. The ball bounces off it without pushing it.
                </Paragraph>
                <Code lang="python" title="Static floor segment">{`# Static floor — doesn't move, infinite mass
floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
floor.elasticity = 0.9
floor.friction = 0.7
space.add(floor)

# The combined elasticity of ball + floor determines bounce height
# Formula: min(ball.elasticity, floor.elasticity) roughly`}</Code>
            </Section>

            <Section title="TracedPath: Drawing the Trail">
                <Paragraph>
                    Manim&apos;s TracedPath draws a fading trail behind a moving object. It takes a function that returns the current position.
                </Paragraph>
                <Code lang="python" title="Bouncing ball with trail">{`from manim import *
import pymunk

SCALE = 100

class BouncingBall(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 15))
        body.position = (0, 300)
        shape = pymunk.Circle(body, 15)
        shape.elasticity = 0.85
        space.add(body, shape)

        floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
        floor.elasticity = 0.9
        space.add(floor)

        ball = Dot(radius=0.15, color=BLUE)
        trail = TracedPath(ball.get_center, stroke_color=BLUE_A,
                           stroke_opacity=0.6, stroke_width=2)
        floor_line = Line(LEFT * 4, RIGHT * 4).shift(DOWN * 2.5)
        self.add(floor_line, trail, ball)

        def sync(mob, dt):
            space.step(dt)
            mob.move_to([body.position.x / SCALE,
                         body.position.y / SCALE, 0])

        ball.add_updater(sync)
        self.wait(5)`}</Code>
            </Section>

            <Section title="Color by Speed">
                <Paragraph>
                    Map the ball&apos;s velocity magnitude to a color gradient. Fast = red, slow = blue. This gives instant visual feedback about energy.
                </Paragraph>
                <Code lang="python" title="Speed-based coloring">{`def sync(mob, dt):
    space.step(dt)
    mob.move_to([body.position.x / SCALE,
                 body.position.y / SCALE, 0])

    # Color by speed
    speed = body.velocity.length
    t = min(speed / 800, 1.0)  # normalize to 0-1
    color = interpolate_color(BLUE, RED, t)
    mob.set_color(color)

ball.add_updater(sync)`}</Code>
                <Note>
                    The ball glows red at peak speed (just before hitting the floor) and fades to blue at the apex of each bounce where velocity is near zero.
                </Note>
            </Section>
        </BlogPost>
    );
}
