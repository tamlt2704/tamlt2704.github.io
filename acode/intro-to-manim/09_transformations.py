"""
Intro to Manim — 09: Transformations
Covers: Transform, ReplacementTransform, FadeTransform, TransformMatchingShapes/Tex.
Source: https://docs.devtaoism.com/docs/html/contents/_9_transformations.html

Render: manim -pql 09_transformations.py TransformScene
"""
from manim import *


class TransformScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"

        title = Text("09: Transformations", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # ── Transform ────────────────────────────
        label = Text("Transform(A, B) — A morphs into B, A is replaced",
                      font_size=14, color=GREY)
        label.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label))

        a = Circle(color=BLUE, fill_opacity=0.5).shift(LEFT * 2)
        b = Square(color=RED, fill_opacity=0.5).shift(LEFT * 2)
        a_label = Text("A (Circle)", font_size=12).next_to(a, DOWN)
        self.play(Create(a), FadeIn(a_label))
        self.play(Transform(a, b), run_time=1.5)
        # Note: after Transform, `a` IS the square now
        self.wait()
        self.play(FadeOut(a), FadeOut(a_label), FadeOut(label))

        # ── ReplacementTransform ─────────────────
        label2 = Text("ReplacementTransform(A, B) — A removed, B added",
                       font_size=14, color=GREY)
        label2.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label2))

        c = Circle(color=BLUE, fill_opacity=0.5)
        s = Square(color=RED, fill_opacity=0.5)
        self.play(Create(c))
        self.play(ReplacementTransform(c, s), run_time=1.5)
        # Now `s` is on screen, `c` is gone
        self.wait()
        self.play(FadeOut(s), FadeOut(label2))

        # ── Transform vs ReplacementTransform ────
        label3 = Text("Key difference: which variable is on screen after",
                       font_size=14, color=GREY)
        label3.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label3))

        comparison = VGroup(
            Text("Transform(a, b):", font_size=16, color=BLUE),
            Text("  a is still the scene object (looks like b)", font_size=14),
            Text("ReplacementTransform(a, b):", font_size=16, color=RED),
            Text("  a is removed, b is the scene object", font_size=14),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        comparison.move_to(DOWN * 0.5)
        self.play(FadeIn(comparison))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # ── FadeTransform ────────────────────────
        title.to_edge(UP)
        self.play(Write(title))
        label4 = Text("FadeTransform — cross-fade between shapes",
                       font_size=14, color=GREY)
        label4.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label4))

        t1 = Text("Hello", font_size=48, color=BLUE)
        t2 = Text("World", font_size=48, color=RED)
        self.play(Write(t1))
        self.play(FadeTransform(t1, t2), run_time=1.5)
        self.wait()
        self.play(FadeOut(t2), FadeOut(label4))

        # ── TransformMatchingShapes ──────────────
        label5 = Text("TransformMatchingShapes — matches similar parts",
                       font_size=14, color=GREY)
        label5.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label5))

        text_a = Text("Manim", font_size=48, color=BLUE)
        text_b = Text("Animations", font_size=48, color=GREEN)
        self.play(Write(text_a))
        self.play(TransformMatchingShapes(text_a, text_b), run_time=1.5)
        self.wait()

        # ── TransformMatchingTex ─────────────────
        tex_a = MathTex("x^2", "+", "y^2", "=", "1")
        tex_b = MathTex("x^2", "=", "1", "-", "y^2")
        self.play(FadeOut(text_b), FadeOut(label5))

        label6 = Text("TransformMatchingTex — matches LaTeX parts by string",
                       font_size=14, color=GREY)
        label6.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(label6))

        self.play(Write(tex_a))
        self.play(TransformMatchingTex(tex_a, tex_b), run_time=1.5)
        self.wait(2)
