import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Ragdoll & Chain: Linked Bodies"
            date="May 14, 2026"
            series="Pymunk + Manim"
            chapter={9}
            prevSlug="pymunk-manim-08-friction"
            prevTitle="Friction & Materials: Ramps and Conveyor Belts"
            nextSlug="pymunk-manim-10-gears"
            nextTitle="Gears & Motors: Constant Rotation"
        >
            <Section title="Chain of PinJoints">
                <Paragraph>
                    A chain is a series of bodies connected by PinJoints. Each link connects to the next at its edge. Pin the first link to a static body to create a hanging chain.
                </Paragraph>
                <Code lang="python" title="Building a chain">{`import pymunk

space = pymunk.Space()
space.gravity = (0, -900)

NUM_LINKS = 8
LINK_LEN = 30
links = []

for i in range(NUM_LINKS):
    body = pymunk.Body(0.5, pymunk.moment_for_segment(0.5, (0, 0), (0, -LINK_LEN), 2))
    body.position = (0, 200 - i * LINK_LEN)
    shape = pymunk.Segment(body, (0, 0), (0, -LINK_LEN), 2)
    shape.friction = 0.5
    space.add(body, shape)
    links.append(body)

# Pin first link to ceiling (static body)
space.add(pymunk.PinJoint(space.static_body, links[0], (0, 200), (0, 0)))

# Connect each link to the next
for i in range(NUM_LINKS - 1):
    joint = pymunk.PinJoint(links[i], links[i+1], (0, -LINK_LEN), (0, 0))
    space.add(joint)`}</Code>
            </Section>

            <Section title="Rendering Chain Links">
                <Paragraph>
                    Each link is a Line segment from its top to bottom in world space. Update all lines each frame using local_to_world.
                </Paragraph>
                <Code lang="python" title="Chain visualization">{`from manim import *
import pymunk

SCALE = 100

class ChainScene(Scene):
    def construct(self):
        space = pymunk.Space()
        space.gravity = (0, -900)

        NUM_LINKS = 8
        LINK_LEN = 30
        links = []
        for i in range(NUM_LINKS):
            b = pymunk.Body(0.5, pymunk.moment_for_segment(0.5, (0,0), (0,-LINK_LEN), 2))
            b.position = (0, 200 - i * LINK_LEN)
            s = pymunk.Segment(b, (0, 0), (0, -LINK_LEN), 2)
            space.add(b, s)
            links.append(b)

        space.add(pymunk.PinJoint(space.static_body, links[0], (0, 200), (0, 0)))
        for i in range(NUM_LINKS - 1):
            space.add(pymunk.PinJoint(links[i], links[i+1], (0, -LINK_LEN), (0, 0)))

        # Give it a push to start swinging
        links[-1].apply_impulse_at_world_point((300, 0), links[-1].position)

        line_mobs = VGroup(*[Line(ORIGIN, DOWN*0.3, color=WHITE, stroke_width=3)
                             for _ in links])
        anchor = Dot([0, 2, 0], radius=0.05, color=YELLOW)
        self.add(anchor, line_mobs)

        def sync(group, dt):
            for _ in range(4):
                space.step(dt/4)
            for line, body in zip(group, links):
                top = body.local_to_world((0, 0))
                bot = body.local_to_world((0, -LINK_LEN))
                line.put_start_and_end_on(
                    [top.x/SCALE, top.y/SCALE, 0],
                    [bot.x/SCALE, bot.y/SCALE, 0])

        line_mobs.add_updater(sync)
        self.wait(6)`}</Code>
            </Section>

            <Section title="Ragdoll Structure">
                <Paragraph>
                    A ragdoll uses the same principle — bodies for limbs connected by PinJoints at joint positions. Add rotation limits with RotaryLimitJoint to prevent unnatural bending.
                </Paragraph>
                <Code lang="python" title="Simple ragdoll">{`# Torso
torso = pymunk.Body(3, pymunk.moment_for_segment(3, (0, 0), (0, -60), 4))
torso.position = (0, 100)
torso_s = pymunk.Segment(torso, (0, 0), (0, -60), 4)
space.add(torso, torso_s)

# Head
head = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 12))
head.position = (0, 120)
head_s = pymunk.Circle(head, 12)
space.add(head, head_s)

# Connect head to torso top
space.add(pymunk.PinJoint(torso, head, (0, 0), (0, -12)))

# Left arm
l_arm = pymunk.Body(0.5, pymunk.moment_for_segment(0.5, (0,0), (-40,-20), 2))
l_arm.position = (-5, 95)
l_arm_s = pymunk.Segment(l_arm, (0, 0), (-40, -20), 2)
space.add(l_arm, l_arm_s)
space.add(pymunk.PinJoint(torso, l_arm, (0, -5), (0, 0)))

# Limit rotation so arm doesn't bend backward
limit = pymunk.RotaryLimitJoint(torso, l_arm, -1.5, 1.5)
space.add(limit)`}</Code>
                <Note>
                    RotaryLimitJoint constrains the relative angle between two bodies. The min/max values are in radians. Without limits, ragdoll limbs can spin freely — which looks unnatural.
                </Note>
            </Section>

            <Section title="Wrecking Ball">
                <Paragraph>
                    Attach a heavy ball to the end of a chain. Swing it into a stack of boxes. The chain transfers momentum from the pivot through each link to the ball.
                </Paragraph>
                <Code lang="python" title="Wrecking ball setup">{`# Heavy ball at end of chain
wrecking_ball = pymunk.Body(10, pymunk.moment_for_circle(10, 0, 20))
wrecking_ball.position = links[-1].position + (0, -LINK_LEN)
wb_shape = pymunk.Circle(wrecking_ball, 20)
wb_shape.elasticity = 0.3
space.add(wrecking_ball, wb_shape)

# Connect to last chain link
space.add(pymunk.PinJoint(links[-1], wrecking_ball, (0, -LINK_LEN), (0, 0)))

# Stack of boxes to smash
for row in range(4):
    for col in range(3):
        v = [(-12,-12),(12,-12),(12,12),(-12,12)]
        b = pymunk.Body(0.5, pymunk.moment_for_poly(0.5, v))
        b.position = (200 + col*26, -226 + row*26)
        s = pymunk.Poly(b, v)
        s.friction = 0.6
        space.add(b, s)`}</Code>
            </Section>
        </BlogPost>
    );
}
