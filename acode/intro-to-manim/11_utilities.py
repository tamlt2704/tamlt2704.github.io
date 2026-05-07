"""
Intro to Manim — 11: Manim Utilities
Covers: Helpful methods, VMobjects (Arrow, Brace, SurroundingRectangle), more animations.
Source: https://docs.devtaoism.com/docs/html/contents/_11_manim_utils.html

Render: manim -pql 11_utilities.py UtilitiesScene
"""
from manim import *


class UtilitiesScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"

        title = Text("11: Manim Utilities", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # ── Helpful VMobjects ────────────────────
        label = Text("Helpful VMobjects", font_size=20, color=BLUE)
        label.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label))

        # Arrow
        arrow = Arrow(LEFT * 3, RIGHT * 0, color=WHITE)
        arrow_label = Text("Arrow", font_size=14, color=GREY).next_to(arrow, DOWN)
        self.play(GrowArrow(arrow), FadeIn(arrow_label))

        # DoubleArrow
        darrow = DoubleArrow(LEFT * 3, RIGHT * 0, color=TEAL).shift(DOWN)
        darrow_label = Text("DoubleArrow", font_size=14, color=GREY).next_to(darrow, DOWN)
        self.play(GrowArrow(darrow), FadeIn(darrow_label))
        self.wait()
        self.play(FadeOut(arrow), FadeOut(darrow), FadeOut(arrow_label), FadeOut(darrow_label))

        # Brace
        sq = Square(color=BLUE, side_length=2)
        brace_r = Brace(sq, RIGHT, color=YELLOW)
        brace_label = brace_r.get_text("2 units", font_size=16)
        brace_d = Brace(sq, DOWN, color=GREEN)
        brace_label_d = brace_d.get_text("2 units", font_size=16)

        self.play(Create(sq))
        self.play(GrowFromCenter(brace_r), FadeIn(brace_label))
        self.play(GrowFromCenter(brace_d), FadeIn(brace_label_d))
        self.wait()

        # SurroundingRectangle
        surr = SurroundingRectangle(sq, color=RED, buff=0.2)
        self.play(Create(surr))
        self.wait()
        self.play(*[FadeOut(m) for m in [sq, brace_r, brace_label, brace_d,
                    brace_label_d, surr, label]])

        # ── More Class Animations ────────────────
        label2 = Text("More Animations", font_size=20, color=BLUE)
        label2.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label2))

        c = Circle(color=BLUE, fill_opacity=0.5)
        self.play(DrawBorderThenFill(c))
        self.wait(0.3)

        self.play(Wiggle(c))
        self.wait(0.3)

        self.play(Flash(c.get_center(), color=YELLOW))
        self.wait(0.3)

        self.play(Circumscribe(c, color=RED))
        self.wait(0.3)

        self.play(ShowPassingFlash(c.copy().set_color(YELLOW), run_time=1))
        self.wait(0.3)

        self.play(Uncreate(c))
        self.wait()
