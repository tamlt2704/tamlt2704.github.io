"""
Intro to Manim — 02: Basic Attributes of Mobjects
Covers: Camera dimensions, position (move_to, shift, next_to, to_edge, to_corner,
align_to), width/height/scale, VMobject attributes (color, stroke, fill, opacity),
copies and setters.
Source: https://docs.devtaoism.com/docs/html/contents/_2_basic_mobjects.html

Render: manim -pql 02_basic_attributes.py BasicAttributes
"""
from manim import *


class BasicAttributes(Scene):
    def construct(self):
        self.camera_dimensions()
        self.absolute_position()
        self.relative_position()
        self.width_height_scale()
        self.vmobject_attributes()
        self.copies_and_setters()
        self.recap()

    # ── Camera Dimensions ────────────────────────
    def camera_dimensions(self):
        title = Text("Camera: 8 units tall, 14.2 wide", font_size=24, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # Show coordinate grid
        grid = NumberPlane(
            x_range=[-7, 7, 1], y_range=[-4, 4, 1],
            background_line_style={"stroke_color": GREY, "stroke_width": 0.5},
        )
        origin_dot = Dot(ORIGIN, color=RED)
        origin_label = Text("[0,0,0]", font_size=14, color=RED).next_to(origin_dot, UR, buff=0.1)

        self.play(FadeIn(grid), FadeIn(origin_dot), FadeIn(origin_label))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Absolute Position ────────────────────────
    def absolute_position(self):
        title = Text("Absolute Position: move_to & shift", font_size=24, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # move_to — always relative to ORIGIN
        r = Rectangle(color=BLUE, width=1.5, height=1)
        code1 = Text('r.move_to(LEFT*3 + UP*2)', font_size=14, color=GREY)
        code1.to_edge(DOWN)
        self.play(FadeIn(r), FadeIn(code1))
        self.play(r.animate.move_to(LEFT * 3 + UP * 2))
        self.wait()

        # shift — relative to CURRENT position
        c = Circle(color=RED, radius=0.5)
        code2 = Text('c.shift(RIGHT) — applied 4 times', font_size=14, color=GREY)
        code2.to_edge(DOWN)
        self.play(FadeIn(c), Transform(code1, code2))

        for _ in range(4):
            self.play(c.animate.shift(RIGHT), run_time=0.4)

        # Contrast: move_to(RIGHT) 4 times = same position
        s = Square(color=GREEN, side_length=0.8)
        s.shift(DOWN)
        self.add(s)
        for _ in range(4):
            s.move_to(RIGHT + DOWN)  # always same spot
        self.wait()

        note = Text("move_to = absolute | shift = relative to current",
                     font_size=16, color=GREY)
        note.to_edge(DOWN)
        self.play(Transform(code1, note))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # get_center, get_corner, etc.
        title2 = Text("Getters: get_center, get_corner, get_right...",
                       font_size=22, color=YELLOW)
        title2.to_edge(UP)
        self.play(Write(title2))

        rect = Rectangle(width=3, height=2, color=WHITE)
        self.play(Create(rect))

        points = {
            "C": rect.get_center(),
            "R": rect.get_right(),
            "L": rect.get_left(),
            "T": rect.get_top(),
            "B": rect.get_bottom(),
            "UR": rect.get_corner(UR),
            "UL": rect.get_corner(UL),
            "DR": rect.get_corner(DR),
            "DL": rect.get_corner(DL),
        }
        for name, pos in points.items():
            dot = Dot(pos, color=RED, radius=0.06)
            label = Text(name, font_size=12, color=RED).next_to(dot, UR, buff=0.05)
            self.play(FadeIn(dot), FadeIn(label), run_time=0.15)

        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Relative Position ────────────────────────
    def relative_position(self):
        title = Text("Relative Position: to_edge, to_corner, next_to, align_to",
                       font_size=20, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # to_edge
        r1 = Rectangle(color=BLUE, width=1.5, height=0.8)
        code = Text("r.to_edge(LEFT)", font_size=14, color=GREY).to_edge(DOWN)
        self.play(FadeIn(r1), FadeIn(code))
        self.play(r1.animate.to_edge(LEFT))
        self.wait(0.5)

        # to_corner
        r2 = Rectangle(color=RED, width=1.5, height=0.8)
        code2 = Text("r.to_corner(UR)", font_size=14, color=GREY).to_edge(DOWN)
        self.play(FadeIn(r2), Transform(code, code2))
        self.play(r2.animate.to_corner(UR))
        self.wait(0.5)

        # next_to
        ref = Circle(color=GREEN, radius=0.5)
        dot = Dot(color=YELLOW)
        code3 = Text("dot.next_to(circle, RIGHT)", font_size=14, color=GREY).to_edge(DOWN)
        self.play(FadeIn(ref), Transform(code, code3))
        dot.next_to(ref, RIGHT)
        self.play(FadeIn(dot))
        self.wait(0.5)

        # next_to with buff=0
        dot2 = Dot(color=RED)
        dot2.next_to(ref, LEFT, buff=0)
        code4 = Text("dot.next_to(circle, LEFT, buff=0)", font_size=14, color=GREY).to_edge(DOWN)
        self.play(FadeIn(dot2), Transform(code, code4))
        self.wait(0.5)

        # align_to
        c = Circle(color=ORANGE, radius=0.4).move_to(RIGHT * 3 + UP)
        r3 = Rectangle(color=PURPLE, width=1, height=0.6)
        r3.align_to(c, RIGHT)
        code5 = Text("r.align_to(circle, RIGHT)", font_size=14, color=GREY).to_edge(DOWN)
        self.play(FadeIn(c), FadeIn(r3), Transform(code, code5))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Width, Height, Scale ─────────────────────
    def width_height_scale(self):
        title = Text("Width, Height, Scale", font_size=24, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # Setting width
        c = Circle(color=BLUE)
        r = Rectangle(color=RED)
        self.play(Create(c), Create(r))

        code = Text("c.width = 3; r.width = 3", font_size=14, color=GREY).to_edge(DOWN)
        self.play(FadeIn(code))
        c.width = 3
        r.width = 3
        self.wait()

        # Scale
        self.play(FadeOut(c), FadeOut(r), FadeOut(code))

        originals = VGroup()
        for s, color in [(1, RED), (2, WHITE), (3, BLUE), (1/3, GREEN)]:
            c = Circle(color=color).scale(s)
            originals.add(c)

        labels = VGroup(
            Text("scale(1)", font_size=12, color=RED),
            Text("scale(2)", font_size=12, color=WHITE),
            Text("scale(3)", font_size=12, color=BLUE),
            Text("scale(1/3)", font_size=12, color=GREEN),
        )
        for i, label in enumerate(labels):
            label.to_edge(DOWN).shift(LEFT * 4.5 + RIGHT * i * 3)

        self.play(FadeIn(originals), FadeIn(labels))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── VMobject Attributes ──────────────────────
    def vmobject_attributes(self):
        title = Text("VMobject: Color, Stroke, Fill, Opacity", font_size=22, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # Color palette demo
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE, TEAL, ORANGE, PINK]
        dots = VGroup()
        for i, color in enumerate(colors):
            d = Dot(color=color).scale(3)
            d.move_to(LEFT * 3.5 + RIGHT * i)
            dots.add(d)
        self.play(FadeIn(dots))
        self.wait()
        self.play(FadeOut(dots))

        # Stroke and fill
        bg = Square(fill_opacity=1, fill_color=WHITE).scale(1.5)
        circle = Circle(
            stroke_width=20, stroke_color=TEAL, stroke_opacity=0.5,
            fill_opacity=0.5, fill_color=ORANGE,
        )
        code = Text("stroke_width=20, stroke_color=TEAL\nfill_color=ORANGE, fill_opacity=0.5",
                     font_size=12, color=GREY).to_edge(DOWN)
        self.play(FadeIn(bg), Create(circle), FadeIn(code))
        self.wait(1.5)

        # set_color overrides both
        self.play(circle.animate.set_color(RED))
        code2 = Text(".set_color(RED) — overrides stroke and fill",
                      font_size=14, color=GREY).to_edge(DOWN)
        self.play(Transform(code, code2))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Copies and Setters ───────────────────────
    def copies_and_setters(self):
        title = Text("Copies and Setters", font_size=24, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        original = Circle(
            radius=1, stroke_color=PINK, stroke_width=15,
            stroke_opacity=0.4, fill_opacity=0.6, fill_color=ORANGE,
        )
        original.to_edge(LEFT, buff=1.5)

        copy1 = original.copy().move_to(ORIGIN)
        copy1.set_color(RED)
        copy1.set_stroke(color=TEAL, width=25, opacity=1)
        copy1.set_fill(color=PURE_BLUE, opacity=1)

        copy2 = copy1.copy().to_edge(RIGHT, buff=1.5)
        copy2.set_style(
            stroke_width=15, stroke_color=WHITE, stroke_opacity=0.5,
            fill_color=PURE_GREEN, fill_opacity=0.3,
        )

        labels = VGroup(
            Text("original", font_size=14).next_to(original, DOWN),
            Text(".copy() + set_color/stroke/fill", font_size=11).next_to(copy1, DOWN),
            Text(".copy() + set_style()", font_size=11).next_to(copy2, DOWN),
        )

        self.play(Create(original))
        self.play(Create(copy1), FadeIn(labels[0]), FadeIn(labels[1]))
        self.play(Create(copy2), FadeIn(labels[2]))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap ────────────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("Recap:", font_size=28, color=BLUE),
            Text("• Camera: 8 units tall, [0,0,0] = center", font_size=16),
            Text("• move_to(pos) = absolute, shift(dir) = relative", font_size=16),
            Text("• to_edge, to_corner, next_to, align_to", font_size=16),
            Text("• .width, .height, .scale(n)", font_size=16),
            Text("• stroke_color/width/opacity, fill_color/opacity", font_size=16),
            Text("• .copy(), .set_color(), .set_stroke(), .set_fill()", font_size=16),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
