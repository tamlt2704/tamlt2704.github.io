import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Fluid-like Particles: Hundreds of Tiny Circles"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={11}
            prevSlug="pymunk-manim-10-gears"
            prevTitle="Gears & Motors: Constant Rotation"
            nextSlug="pymunk-manim-12-rube-goldberg"
            nextTitle="Rube Goldberg Machine: The Full Capstone"
        >
            <Section title="Many Small Circles">
                <Paragraph>
                    Pymunk handles hundreds of small circles efficiently. Spawn them in a grid or stream, give them low elasticity and some friction, and they behave like a granular fluid — piling up, flowing through gaps, and settling.
                </Paragraph>
                <Code lang="python" title="Spawning particles">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

particles = []
RADIUS = 4

for row in range(20):
    for col in range(15):
        mass = 0.1
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, RADIUS))
        body.position = (-60 + col * 9, 100 + row * 9)
        shape = pymunk.Circle(body, RADIUS)
        shape.elasticity = 0.1  # low bounce = fluid-like
        shape.friction = 0.3
        space.add(body, shape)
        particles.append(body)

# 300 particles — pymunk handles this fine
print(f"Particles: {len(particles)}")`}</Code>
            </Section>

            <Section title="Container Walls">
                <Paragraph>
                    Build a container from static segments. Add a narrow opening at the bottom for an hourglass effect, or a funnel shape to channel flow.
                </Paragraph>
                <Code lang="python" title="Container with opening">{`# Box container with narrow opening at bottom
walls = [
    ((-150, -250), (-150, 150)),   # left wall
    ((150, -250), (150, 150)),     # right wall
    ((-150, -250), (-20, -250)),   # floor left
    ((20, -250), (150, -250)),     # floor right (gap in middle)
]

for a, b in walls:
    seg = pymunk.Segment(space.static_body, a, b, 3)
    seg.friction = 0.5
    seg.elasticity = 0.2
    space.add(seg)

# Funnel walls to guide particles toward the gap
funnel_l = pymunk.Segment(space.static_body, (-150, -150), (-20, -240), 3)
funnel_r = pymunk.Segment(space.static_body, (150, -150), (20, -240), 3)
funnel_l.friction = 0.3
funnel_r.friction = 0.3
space.add(funnel_l, funnel_r)`}</Code>
            </Section>

            <Section title="Velocity Coloring">
                <Paragraph>
                    Color each particle by its speed. Fast particles glow warm (red/orange), slow ones cool (blue). This reveals flow patterns — fast streams through narrow gaps, slow piles at rest.
                </Paragraph>
                <Code lang="python" title="Particle scene with coloring">{`from manim import *
import pymunk

SCALE = 100

class ParticleFlow(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        # Container walls
        for a, b in [( (-150,-250),(-150,200) ), ( (150,-250),(150,200) ),
                     ( (-150,-250),(-15,-250) ), ( (15,-250),(150,-250) )]:
            seg = pymunk.Segment(space.static_body, a, b, 3)
            seg.friction = 0.4
            space.add(seg)

        particles = []
        for row in range(15):
            for col in range(12):
                b = pymunk.Body(0.1, pymunk.moment_for_circle(0.1, 0, 4))
                b.position = (-50 + col*9, 50 + row*9)
                s = pymunk.Circle(b, 4)
                s.elasticity = 0.1
                s.friction = 0.3
                space.add(b, s)
                particles.append(b)

        dots = VGroup(*[Dot(radius=0.04, color=BLUE) for _ in particles])
        walls_mob = VGroup(
            Line([-1.5,-2.5,0],[-1.5,2,0], color=GREY),
            Line([1.5,-2.5,0],[1.5,2,0], color=GREY),
            Line([-1.5,-2.5,0],[-0.15,-2.5,0], color=GREY),
            Line([0.15,-2.5,0],[1.5,-2.5,0], color=GREY),
        )
        self.add(walls_mob, dots)

        def sync(group, dt):
            for _ in range(4):
                space.step(dt/4)
            for dot, body in zip(group, particles):
                dot.move_to([body.position.x/SCALE,
                             body.position.y/SCALE, 0])
                speed = body.velocity.length
                t = min(speed / 600, 1.0)
                dot.set_color(interpolate_color(BLUE, RED, t))

        dots.add_updater(sync)
        self.wait(6)`}</Code>
                <Note>
                    With 180 particles, rendering is smooth. For 500+, consider reducing manim&apos;s frame rate or using simpler mobjects (points instead of Dots).
                </Note>
            </Section>

            <Section title="Performance Tips">
                <Paragraph>
                    For large particle counts, optimize both physics and rendering:
                </Paragraph>
                <Code lang="python" title="Performance optimizations">{`# Physics: use space.use_spatial_hash for many same-size shapes
space.use_spatial_hash(dim=RADIUS * 2, count=len(particles))

# Physics: fewer sub-steps (trade accuracy for speed)
space.step(dt)  # single step instead of sub-stepping

# Rendering: use a single updater for all particles (VGroup)
# Avoid: individual updaters per dot (slow with 300+)

# Rendering: skip frames for visual update
frame_count = [0]
def sync(group, dt):
    space.step(dt)  # always step physics
    frame_count[0] += 1
    if frame_count[0] % 2 != 0:  # update visuals every other frame
        return
    for dot, body in zip(group, particles):
        dot.move_to([body.position.x/SCALE, body.position.y/SCALE, 0])`}</Code>
            </Section>
        </BlogPost>
    );
}
