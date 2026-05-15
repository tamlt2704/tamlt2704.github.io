import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note, BlogImage } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Pymunk + Manim: Physics Animations from Python"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={0}
            nextSlug="pymunk-manim-01-gravity"
            nextTitle="Gravity & Bouncing"
        >
            <Section title="Setup">
                <Paragraph>
                    We&apos;re combining two Python libraries: Pymunk (2D physics engine) and Manim (math animation). Pymunk simulates. Manim renders. The result: physics-accurate animations with beautiful visuals.
                </Paragraph>
                <Code lang="bash" title="Project setup">{`uv python install 3.12
uv init pymunk-manim --python 3.12
cd pymunk-manim
uv add pymunk manim`}</Code>
                <Paragraph>
                    Verify everything works:
                </Paragraph>
                <Code lang="bash">{`uv run python -c "import pymunk; import manim; print('Ready')"
# Ready`}</Code>
            </Section>

            <Section title="Pymunk: Space + Body + Shape">
                <Paragraph>
                    Pymunk has three core objects. A Space holds everything and applies gravity. A Body carries position, velocity, and mass. A Shape defines collision geometry attached to a body.
                </Paragraph>
                <Code lang="python" title="Pymunk basics">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)  # pixels/sec², downward

body = pymunk.Body(mass=1, moment=10)
body.position = (0, 300)

circle = pymunk.Circle(body, radius=20)
circle.elasticity = 0.8  # bounciness

space.add(body, circle)
space.step(1/60)  # advance one frame
print(body.position)  # ball has fallen`}</Code>
            </Section>

            <Section title="The Coordinate Bridge">
                <Paragraph>
                    Pymunk uses large pixel values. Manim uses scene units (roughly -4 to 4). We scale between them with a constant:
                </Paragraph>
                <Code lang="python" title="SCALE bridge">{`SCALE = 100  # 100 pymunk pixels = 1 manim unit

def pymunk_to_manim(pos):
    return [pos.x / SCALE, pos.y / SCALE, 0]

def manim_to_pymunk(point):
    return (point[0] * SCALE, point[1] * SCALE)`}</Code>
                <Note>
                    Every chapter uses SCALE=100. Pymunk coordinates divided by 100 give manim coordinates. This is the single most important pattern in the series.
                </Note>
            </Section>

            <Section title="First Ball Drop Scene">
                <Paragraph>
                    The pattern: pymunk simulates physics, an updater syncs positions to manim every frame.
                </Paragraph>
                <Code lang="python" title="chapter_00.py">{`from manim import *
import pymunk

SCALE = 100

class PhysicsBall(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        body = pymunk.Body(mass=1, moment=10)
        body.position = (0, 300)
        shape = pymunk.Circle(body, radius=20)
        shape.elasticity = 0.9
        space.add(body, shape)

        floor_shape = pymunk.Segment(
            space.static_body, (-400, -250), (400, -250), 5
        )
        floor_shape.elasticity = 0.9
        space.add(floor_shape)

        ball = Dot(radius=0.2, color=BLUE)
        floor = Line(LEFT * 4, RIGHT * 4).shift(DOWN * 2.5)
        self.add(ball, floor)

        def sync(mob, dt):
            space.step(dt)
            mob.move_to([body.position.x / SCALE,
                         body.position.y / SCALE, 0])

        ball.add_updater(sync)
        self.wait(4)`}</Code>
                <Paragraph>
                    Render it:
                </Paragraph>
                <Code lang="bash">{`uv run manim -pqh chapter_00.py PhysicsBall`}</Code>
                <Paragraph>
                    A blue ball drops, hits the floor, and bounces — physics-accurate, beautifully rendered.
                </Paragraph>
                <BlogImage src="/blog/images/pymunk-manim-00-ball-drop.png" alt="Ball dropping and bouncing — rendered with Pymunk + Manim" />
            </Section>
        </BlogPost>
    );
}
