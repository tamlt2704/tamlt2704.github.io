"""
Intro to Manim — 12: Basic 2D Graphs
Covers: Axes, plot, line graph, parametric, NumberPlane, Riemann rectangles.
Source: https://docs.devtaoism.com/docs/html/contents/_12_2d_graphs.html

Render: manim -pql 12_2d_graphs.py Graphs2D
"""
from manim import *
import numpy as np


class Graphs2D(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"
        self.axes_demo()
        self.function_plot()
        self.parametric_demo()
        self.number_plane()
        self.riemann_demo()

    def axes_demo(self):
        title = Text("Axes", font_size=28, color=YELLOW).to_edge(UP)
        self.play(Write(title))

        axes = Axes(
            x_range=[-3, 3, 1], y_range=[-2, 2, 1],
            x_length=8, y_length=4,
            axis_config={"color": GREY, "include_numbers": True,
                         "font_size": 18},
        )
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def function_plot(self):
        title = Text("f(x) Plots", font_size=28, color=YELLOW).to_edge(UP)
        self.play(Write(title))

        axes = Axes(x_range=[-4, 4, 1], y_range=[-1.5, 1.5, 0.5],
                    x_length=8, y_length=3,
                    axis_config={"color": GREY, "stroke_width": 1})
        self.play(Create(axes))

        # sin(x)
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        sin_label = axes.get_graph_label(sin_graph, label="\\sin(x)",
                                          x_val=3, color=BLUE)
        self.play(Create(sin_graph), FadeIn(sin_label))
        self.wait()

        # cos(x)
        cos_graph = axes.plot(lambda x: np.cos(x), color=RED)
        cos_label = axes.get_graph_label(cos_graph, label="\\cos(x)",
                                          x_val=2, color=RED)
        self.play(Create(cos_graph), FadeIn(cos_label))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def parametric_demo(self):
        title = Text("Parametric Functions", font_size=28, color=YELLOW).to_edge(UP)
        self.play(Write(title))

        axes = Axes(x_range=[-3, 3, 1], y_range=[-3, 3, 1],
                    x_length=5, y_length=5,
                    axis_config={"color": GREY, "stroke_width": 1})
        self.play(Create(axes))

        # Lissajous curve
        curve = axes.plot_parametric_curve(
            lambda t: [2 * np.sin(3 * t), 2 * np.sin(2 * t)],
            t_range=[0, TAU], color=TEAL,
        )
        label = Text("Lissajous: (sin(3t), sin(2t))", font_size=14, color=GREY)
        label.to_edge(DOWN)
        self.play(Create(curve), FadeIn(label), run_time=2)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def number_plane(self):
        title = Text("NumberPlane", font_size=28, color=YELLOW).to_edge(UP)
        self.play(Write(title))

        plane = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-3, 3, 1],
            background_line_style={"stroke_color": BLUE_D, "stroke_width": 1},
        )
        self.play(Create(plane), run_time=1.5)

        # Apply a transformation
        def transform(point):
            x, y, z = point
            return [x + 0.5 * y, y + 0.2 * np.sin(x), z]

        self.play(ApplyPointwiseFunction(transform, plane), run_time=2)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def riemann_demo(self):
        title = Text("Riemann Rectangles", font_size=28, color=YELLOW).to_edge(UP)
        self.play(Write(title))

        axes = Axes(x_range=[0, 5, 1], y_range=[0, 10, 2],
                    x_length=7, y_length=4,
                    axis_config={"color": GREY, "stroke_width": 1})
        graph = axes.plot(lambda x: 0.4 * x ** 2, color=BLUE)
        self.play(Create(axes), Create(graph))

        # Increasing number of rectangles
        for n in [4, 8, 20, 50]:
            rects = axes.get_riemann_rectangles(
                graph, x_range=[0, 4], dx=4 / n,
                color=[BLUE, GREEN], fill_opacity=0.5,
            )
            label = Text(f"n = {n}", font_size=16, color=GREY).to_edge(DOWN)
            self.play(Create(rects), FadeIn(label), run_time=0.8)
            self.wait(0.5)
            if n < 50:
                self.play(FadeOut(rects), FadeOut(label), run_time=0.3)

        self.wait(2)
