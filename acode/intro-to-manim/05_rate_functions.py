"""
Intro to Manim — 05: Rate Functions
Covers: smooth, linear, rush_into, rush_from, there_and_back, wiggle, etc.
Source: https://docs.devtaoism.com/docs/html/contents/_5_rate_functions.html

Render: manim -pql 05_rate_functions.py RateFunctions
"""
from manim import *


class RateFunctions(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"

        title = Text("05: Rate Functions", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # Show all rate functions side by side
        funcs = [
            ("smooth", smooth),
            ("linear", linear),
            ("rush_into", rush_into),
            ("rush_from", rush_from),
            ("slow_into", slow_into),
            ("there_and_back", there_and_back),
            ("double_smooth", double_smooth),
            ("wiggle", wiggle),
        ]

        dots = VGroup()
        labels = VGroup()
        start_x = -5

        for i, (name, func) in enumerate(funcs):
            y = 2.5 - i * 0.7
            # Label
            label = Text(name, font_size=13, color=GREY)
            label.move_to([start_x + 1, y, 0])
            labels.add(label)
            # Dot
            dot = Dot(color=BLUE, radius=0.08)
            dot.move_to([start_x + 2.5, y, 0])
            dots.add(dot)
            # Track line
            track = Line([start_x + 2.5, y, 0], [start_x + 8, y, 0],
                         color=GREY, stroke_width=0.5, stroke_opacity=0.3)
            self.add(track)

        self.play(FadeIn(labels), FadeIn(dots), run_time=0.5)

        # Animate all dots simultaneously, each with its rate function
        anims = []
        for i, (name, func) in enumerate(funcs):
            y = 2.5 - i * 0.7
            anims.append(dots[i].animate(rate_func=func).move_to([start_x + 8, y, 0]))

        self.play(*anims, run_time=3)
        self.wait(1)

        # Reset and do it again
        for i, (name, func) in enumerate(funcs):
            y = 2.5 - i * 0.7
            dots[i].move_to([start_x + 2.5, y, 0])

        self.play(*[dots[i].animate(rate_func=funcs[i][1]).move_to(
            [start_x + 8, 2.5 - i * 0.7, 0]) for i in range(len(funcs))],
            run_time=3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # Usage example
        usage = Text("Usage:", font_size=24, color=YELLOW)
        usage.to_edge(UP)
        self.play(Write(usage))

        code = Code(
            code=(
                'self.play(\n'
                '    Create(circle),\n'
                '    run_time=2,\n'
                '    rate_func=there_and_back,\n'
                ')'
            ),
            language="python", font_size=16,
            background="rectangle", style="monokai",
            insert_line_no=False, background_stroke_color="#333",
        )
        code.scale(0.8)
        self.play(FadeIn(code))

        c = Circle(color=BLUE).shift(RIGHT * 3)
        self.play(Create(c), run_time=2, rate_func=there_and_back)
        self.wait()
        self.play(Create(c), run_time=2, rate_func=rush_into)
        self.wait(2)
