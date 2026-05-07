"""
Intro to Manim — 08: Text & Tex
Covers: Text, MarkupText, Tex, MathTex.
Source: https://docs.devtaoism.com/docs/html/contents/_8_text_and_tex.html

Render: manim -pql 08_text_tex.py TextTexScene
"""
from manim import *


class TextTexScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"

        title = Text("08: Text & Tex", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # ── Text ─────────────────────────────────
        t1 = Text("Hello World", font_size=48, color=WHITE)
        t2 = Text("Custom Font", font="Courier New", font_size=36, color=BLUE)
        t3 = Text("Colored", font_size=36, color=RED)

        group = VGroup(t1, t2, t3).arrange(DOWN, buff=0.3)
        self.play(Write(t1), run_time=0.5)
        self.play(Write(t2), run_time=0.5)
        self.play(Write(t3), run_time=0.5)
        self.wait()
        self.play(FadeOut(group))

        # ── MarkupText ───────────────────────────
        section = Text("MarkupText (Pango markup)", font_size=20, color=BLUE)
        section.to_edge(UP, buff=1.2)
        self.play(FadeIn(section))

        markup = MarkupText(
            '<span foreground="yellow">Bold</span> and '
            '<span foreground="cyan"><i>italic</i></span> and '
            '<span foreground="red"><b>both</b></span>',
            font_size=28,
        )
        self.play(Write(markup))
        self.wait()
        self.play(FadeOut(markup), FadeOut(section))

        # ── Tex (LaTeX) ─────────────────────────
        section2 = Text("Tex & MathTex (LaTeX)", font_size=20, color=BLUE)
        section2.to_edge(UP, buff=1.2)
        self.play(FadeIn(section2))

        tex1 = MathTex(r"E = mc^2", font_size=48, color=WHITE)
        tex2 = MathTex(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}",
                       font_size=36, color=TEAL)
        tex3 = MathTex(r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}",
                       font_size=36, color=ORANGE)

        formulas = VGroup(tex1, tex2, tex3).arrange(DOWN, buff=0.4)
        self.play(Write(tex1), run_time=0.8)
        self.play(Write(tex2), run_time=0.8)
        self.play(Write(tex3), run_time=0.8)
        self.wait(2)
