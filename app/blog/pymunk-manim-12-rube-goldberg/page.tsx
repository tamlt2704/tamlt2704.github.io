import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Rube Goldberg Machine: The Full Capstone"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={12}
            prevSlug="pymunk-manim-11-particles"
            prevTitle="Fluid-like Particles: Hundreds of Tiny Circles"
        >
            <Section title="The Concept">
                <Paragraph>
                    A Rube Goldberg machine chains simple mechanisms: ball rolls down ramp → hits dominos → last domino swings pendulum → pendulum launches projectile. Each stage triggers the next through natural physics — no explicit triggers needed.
                </Paragraph>
                <Code lang="python" title="Stage layout">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

# Stage 1: Ramp — ball rolls down
ramp = pymunk.Segment(space.static_body, (-300, 200), (-120, -150), 5)
ramp.elasticity = 0.3
ramp.friction = 0.4
space.add(ramp)

ball = pymunk.Body(1.5, pymunk.moment_for_circle(1.5, 0, 10))
ball.position = (-280, 220)
ball_s = pymunk.Circle(ball, 10)
ball_s.elasticity = 0.4
space.add(ball, ball_s)

# Stage 2: Dominos — tall thin boxes
dominos = []
for i in range(5):
    verts = [(-3, -18), (3, -18), (3, 18), (-3, 18)]
    d = pymunk.Body(0.3, pymunk.moment_for_poly(0.3, verts))
    d.position = (-80 + i * 28, -232)
    s = pymunk.Poly(d, verts)
    s.friction = 0.6
    s.elasticity = 0.1
    space.add(d, s)
    dominos.append((d, verts))`}</Code>
            </Section>

            <Section title="Pendulum and Projectile">
                <Paragraph>
                    The last domino hits a pendulum bob. The bob swings and strikes a small projectile, launching it across the scene. Each stage transfers momentum to the next.
                </Paragraph>
                <Code lang="python" title="Pendulum and projectile stages">{`# Stage 3: Pendulum — hit by last domino
bob = pymunk.Body(3, pymunk.moment_for_circle(3, 0, 12))
bob.position = (120, -150)
bob_s = pymunk.Circle(bob, 12)
bob_s.elasticity = 0.8
pj = pymunk.PivotJoint(space.static_body, bob, (120, -50))
pj.max_bias = 0
space.add(bob, bob_s, pj)

# Stage 4: Projectile — launched by pendulum swing
proj = pymunk.Body(0.3, pymunk.moment_for_circle(0.3, 0, 6))
proj.position = (160, -244)
proj_s = pymunk.Circle(proj, 6)
proj_s.elasticity = 0.9
space.add(proj, proj_s)

# Floor to keep everything grounded
floor = pymunk.Segment(space.static_body, (-400, -250), (400, -250), 5)
floor.friction = 0.8
space.add(floor)`}</Code>
                <Note>
                    No explicit triggers between stages. The ball&apos;s momentum topples the first domino, which topples the next, which hits the bob, which swings into the projectile. Physics handles causality.
                </Note>
            </Section>

            <Section title="MovingCameraScene">
                <Paragraph>
                    Use MovingCameraScene to pan the camera and follow the action. Start wide, then zoom into each stage as it activates.
                </Paragraph>
                <Code lang="python" title="Full Rube Goldberg scene">{`from manim import *
import pymunk

SCALE = 100

class RubeGoldberg(MovingCameraScene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        # --- Build all stages (ramp, dominos, pendulum, projectile) ---
        ramp = pymunk.Segment(space.static_body, (-300,200),(-120,-150), 5)
        ramp.friction = 0.4
        floor = pymunk.Segment(space.static_body, (-400,-250),(400,-250), 5)
        floor.friction = 0.8
        space.add(ramp, floor)

        ball = pymunk.Body(1.5, pymunk.moment_for_circle(1.5, 0, 10))
        ball.position = (-280, 220)
        ball_s = pymunk.Circle(ball, 10)
        ball_s.elasticity = 0.4
        space.add(ball, ball_s)

        dominos = []
        for i in range(5):
            v = [(-3,-18),(3,-18),(3,18),(-3,18)]
            d = pymunk.Body(0.3, pymunk.moment_for_poly(0.3, v))
            d.position = (-80 + i*28, -232)
            s = pymunk.Poly(d, v)
            s.friction = 0.6
            space.add(d, s)
            dominos.append((d, v))

        bob = pymunk.Body(3, pymunk.moment_for_circle(3, 0, 12))
        bob.position = (120, -150)
        bob_s = pymunk.Circle(bob, 12)
        bob_s.elasticity = 0.8
        space.add(bob, bob_s, pymunk.PivotJoint(space.static_body, bob, (120,-50)))

        proj = pymunk.Body(0.3, pymunk.moment_for_circle(0.3, 0, 6))
        proj.position = (160, -244)
        space.add(proj, pymunk.Circle(proj, 6))`}</Code>
            </Section>

            <Section title="Rendering and Camera">
                <Paragraph>
                    Create manim mobjects for each element and sync them in a single updater. The camera starts wide, then follows the ball down the ramp.
                </Paragraph>
                <Code lang="python" title="Visuals and updater">{`        # --- Manim visuals ---
        ramp_line = Line([-3,2,0], [-1.2,-1.5,0], color=GREY)
        floor_line = Line(LEFT*4, RIGHT*4).shift(DOWN*2.5)
        ball_dot = Dot(radius=0.1, color=RED)
        dom_mobs = VGroup(*[Rectangle(width=0.06, height=0.36,
                    color=GREEN, fill_opacity=0.6) for _ in dominos])
        bob_dot = Dot(radius=0.12, color=YELLOW)
        rod = Line(ORIGIN, ORIGIN, stroke_width=2)
        proj_dot = Dot(radius=0.06, color=ORANGE)
        self.add(ramp_line, floor_line, ball_dot, dom_mobs,
                 bob_dot, rod, proj_dot)
        self.camera.frame.set(width=12)

        def update(mob, dt):
            for _ in range(10):
                space.step(dt / 10)
            ball_dot.move_to([ball.position.x/SCALE,
                              ball.position.y/SCALE, 0])
            for dm, (d, v) in zip(dom_mobs, dominos):
                pts = [[d.local_to_world(p).x/SCALE,
                        d.local_to_world(p).y/SCALE, 0] for p in v]
                dm.become(Polygon(*pts, color=GREEN, fill_opacity=0.6))
            bp = [bob.position.x/SCALE, bob.position.y/SCALE, 0]
            bob_dot.move_to(bp)
            rod.put_start_and_end_on([1.2, -0.5, 0], bp)
            proj_dot.move_to([proj.position.x/SCALE,
                              proj.position.y/SCALE, 0])

        ball_dot.add_updater(update)
        self.wait(8)`}</Code>
                <Paragraph>
                    The full scene runs for 8 seconds. The ball rolls, dominos topple in sequence, the pendulum swings, and the projectile launches — all from a single initial condition.
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
