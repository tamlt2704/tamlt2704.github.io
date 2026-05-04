"""
Intro to Manim — 04: Layers
Covers: Scene.mobjects ordering, z_index.
Source: https://docs.devtaoism.com/docs/html/contents/_4_layers.html

Render: manim -pql 04_layers.py Layers
"""
from manim import *


class Layers(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"

        title = Text("04: Layers & z_index", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # ── Scene.mobjects ordering ──────────────
        section = Text("Add order = render order", font_size=20, color=BLUE)
        section.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(section))

        # Later objects appear on top
        c1 = Circle(radius=1.2, fill_color=RED, fill_opacity=0.8, stroke_width=0)
        c2 = Circle(radius=1.2, fill_color=BLUE, fill_opacity=0.8, stroke_width=0)
        c2.shift(RIGHT * 0.8)

        l1 = Text("added first (behind)", font_size=12, color=WHITE).next_to(c1, DOWN)
        l2 = Text("added second (on top)", font_size=12, color=WHITE).next_to(c2, DOWN)

        self.play(FadeIn(c1), FadeIn(l1))
        self.play(FadeIn(c2), FadeIn(l2))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in [c1, c2, l1, l2, section]])

        # ── z_index ─────────────────────────────
        section2 = Text("z_index overrides add order", font_size=20, color=BLUE)
        section2.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(section2))

        # Red has higher z_index → appears on top even though added first
        r = Circle(radius=1.2, fill_color=RED, fill_opacity=0.8, stroke_width=0)
        r.set_z_index(2)
        b = Circle(radius=1.2, fill_color=BLUE, fill_opacity=0.8, stroke_width=0)
        b.shift(RIGHT * 0.8)
        b.set_z_index(1)

        rl = Text("z_index=2 (on top)", font_size=12, color=WHITE).next_to(r, DOWN)
        bl = Text("z_index=1 (behind)", font_size=12, color=WHITE).next_to(b, DOWN)

        # Add blue first, red second — but red is on top due to z_index
        self.play(FadeIn(b), FadeIn(bl))
        self.play(FadeIn(r), FadeIn(rl))
        self.wait(1.5)

        # Animate z_index change
        note = Text("Swap: set red z_index=0", font_size=16, color=GREY)
        note.to_edge(DOWN)
        self.play(FadeIn(note))
        r.set_z_index(0)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # Recap
        recap = VGroup(
            Text("Recap:", font_size=24, color=BLUE),
            Text("• Objects added later render on top", font_size=16),
            Text("• z_index overrides add order", font_size=16),
            Text("• Higher z_index = closer to viewer", font_size=16),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
