import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Collisions & Callbacks: Flash on Impact"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={5}
            prevSlug="pymunk-manim-04-pendulum"
            prevTitle="Pendulum: Pivot Joints and Energy Visualization"
            nextSlug="pymunk-manim-06-shapes"
            nextTitle="Polygons & Segments: Beyond Circles"
        >
            <Section title="Collision Types">
                <Paragraph>
                    Every shape has a collision_type integer. Pymunk fires callbacks when shapes with specific types collide. Set collision_type on shapes, then register a handler on the space.
                </Paragraph>
                <Code lang="python" title="Setting collision types">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

BALL_TYPE = 1
FLOOR_TYPE = 2

ball = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 12))
ball.position = (0, 300)
ball_shape = pymunk.Circle(ball, 12)
ball_shape.elasticity = 0.8
ball_shape.collision_type = BALL_TYPE
space.add(ball, ball_shape)

floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
floor.elasticity = 0.9
floor.collision_type = FLOOR_TYPE
space.add(floor)`}</Code>
            </Section>

            <Section title="The Collision Handler">
                <Paragraph>
                    Register a handler with space.add_collision_handler(type_a, type_b). It returns a handler object with callbacks: begin, pre_solve, post_solve, separate. The begin callback fires once when contact starts.
                </Paragraph>
                <Code lang="python" title="Registering a callback">{`# Track collisions for visual effects
collisions = []

def on_hit(arbiter, space, data):
    # arbiter.contact_point_set gives collision details
    cp = arbiter.contact_point_set.points[0]
    pos = cp.point_a  # world-space collision point
    impulse = arbiter.total_impulse.length
    collisions.append((pos, impulse))
    return True  # return True to process collision normally

handler = space.add_collision_handler(BALL_TYPE, FLOOR_TYPE)
handler.begin = on_hit`}</Code>
                <Note>
                    Returning True from begin means &quot;process this collision normally.&quot; Return False to ignore the collision (the shapes pass through each other). Useful for one-way platforms or trigger zones.
                </Note>
            </Section>

            <Section title="Flash Effect on Impact">
                <Paragraph>
                    Each frame, check if new collisions occurred. If so, spawn a Flash animation at the collision point. The flash intensity scales with impact force.
                </Paragraph>
                <Code lang="python" title="Flash on collision scene">{`from manim import *
import pymunk

SCALE = 100
BALL_TYPE, FLOOR_TYPE = 1, 2

class FlashOnHit(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        ball_b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 12))
        ball_b.position = (0, 300)
        ball_s = pymunk.Circle(ball_b, 12)
        ball_s.elasticity = 0.8
        ball_s.collision_type = BALL_TYPE
        space.add(ball_b, ball_s)

        floor_s = pymunk.Segment(space.static_body, (-400,-250),(400,-250), 5)
        floor_s.elasticity = 0.9
        floor_s.collision_type = FLOOR_TYPE
        space.add(floor_s)

        hits = []
        def on_hit(arb, sp, data):
            pt = arb.contact_point_set.points[0].point_a
            hits.append(pt)
            return True
        h = space.add_collision_handler(BALL_TYPE, FLOOR_TYPE)
        h.begin = on_hit

        dot = Dot(radius=0.12, color=BLUE)
        floor_line = Line(LEFT*4, RIGHT*4).shift(DOWN*2.5)
        self.add(floor_line, dot)

        def sync(mob, dt):
            space.step(dt)
            mob.move_to([ball_b.position.x/SCALE,
                         ball_b.position.y/SCALE, 0])
            while hits:
                pt = hits.pop()
                pos = [pt.x/SCALE, pt.y/SCALE, 0]
                self.add(Flash(pos, color=YELLOW, line_length=0.2))

        dot.add_updater(sync)
        self.wait(5)`}</Code>
            </Section>

            <Section title="Multiple Collision Pairs">
                <Paragraph>
                    Register different handlers for different collision pairs. Balls hitting walls can spark, balls hitting each other can play a sound cue or change color.
                </Paragraph>
                <Code lang="python" title="Multiple handlers">{`WALL_TYPE = 3

# Ball-floor: yellow flash
h1 = space.add_collision_handler(BALL_TYPE, FLOOR_TYPE)
h1.begin = lambda arb, sp, d: flash(arb, YELLOW)

# Ball-wall: red flash
h2 = space.add_collision_handler(BALL_TYPE, WALL_TYPE)
h2.begin = lambda arb, sp, d: flash(arb, RED)

# Ball-ball: both change color briefly
h3 = space.add_collision_handler(BALL_TYPE, BALL_TYPE)
h3.begin = lambda arb, sp, d: color_swap(arb)

def flash(arb, color):
    pt = arb.contact_point_set.points[0].point_a
    hits.append((pt, color))
    return True`}</Code>
            </Section>
        </BlogPost>
    );
}
