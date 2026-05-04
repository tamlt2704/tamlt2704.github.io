"""
Intro to Manim — 07: Groups & VGroups
Covers: Group, VGroup, arrange, as arrays, list comprehension.
Source: https://docs.devtaoism.com/docs/html/contents/_7_groups.html

Render: manim -pql 07_groups.py GroupsScene
"""
from manim import *


class GroupsScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"

        title = Text("07: Groups & VGroups", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # ── VGroup basics ────────────────────────
        c = Circle(color=RED)
        s = Square(color=BLUE)
        t = Triangle(color=GREEN)

        group = VGroup(c, s, t)
        group.arrange(RIGHT, buff=0.5)

        code = Text("VGroup(c, s, t).arrange(RIGHT, buff=0.5)",
                     font_size=14, color=GREY)
        code.to_edge(DOWN)

        self.play(FadeIn(group), FadeIn(code))
        self.wait()

        # Arrange DOWN
        code2 = Text(".arrange(DOWN, buff=0.3)", font_size=14, color=GREY)
        code2.to_edge(DOWN)
        self.play(group.animate.arrange(DOWN, buff=0.3), Transform(code, code2))
        self.wait()

        # Move entire group
        code3 = Text("group.shift(LEFT * 3)", font_size=14, color=GREY)
        code3.to_edge(DOWN)
        self.play(group.animate.shift(LEFT * 3), Transform(code, code3))
        self.wait()

        # Scale entire group
        code4 = Text("group.scale(0.5)", font_size=14, color=GREY)
        code4.to_edge(DOWN)
        self.play(group.animate.scale(0.5), Transform(code, code4))
        self.wait()
        self.play(FadeOut(group), FadeOut(code))

        # ── As arrays ───────────────────────────
        section = Text("VGroup as Array", font_size=22, color=BLUE)
        section.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(section))

        dots = VGroup(*[Dot(color=interpolate_color(BLUE, RED, i / 9))
                        .scale(2) for i in range(10)])
        dots.arrange(RIGHT, buff=0.3)

        self.play(FadeIn(dots))
        self.wait(0.5)

        # Access by index
        self.play(dots[0].animate.set_color(YELLOW).scale(1.5))
        self.play(dots[-1].animate.set_color(GREEN).scale(1.5))
        self.wait(0.5)

        # Iterate
        for dot in dots[1:-1]:
            self.play(dot.animate.shift(UP * 0.3), run_time=0.1)
        self.wait()
        self.play(*[FadeOut(m) for m in self.mobjects])

        # ── List comprehension ───────────────────
        section2 = Text("List Comprehension", font_size=22, color=BLUE)
        section2.to_edge(UP)
        self.play(Write(section2))

        code5 = Code(
            code=(
                'grid = VGroup(*[\n'
                '    Square(side_length=0.5, fill_opacity=0.8,\n'
                '           fill_color=interpolate_color(BLUE, RED, i/24))\n'
                '    for i in range(25)\n'
                '])\n'
                'grid.arrange_in_grid(rows=5, buff=0.1)'
            ),
            language="python", font_size=13,
            background="rectangle", style="monokai",
            insert_line_no=False, background_stroke_color="#333",
        )
        code5.scale(0.7).to_edge(LEFT, buff=0.3).shift(DOWN * 0.5)
        self.play(FadeIn(code5))

        grid = VGroup(*[
            Square(side_length=0.5, fill_opacity=0.8,
                   fill_color=interpolate_color(BLUE, RED, i / 24))
            for i in range(25)
        ])
        grid.arrange_in_grid(rows=5, buff=0.1)
        grid.move_to(RIGHT * 3)

        self.play(LaggedStart(*[FadeIn(sq) for sq in grid], lag_ratio=0.03),
                  run_time=1)
        self.wait(2)
