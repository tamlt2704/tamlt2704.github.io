# Chapter 5: Graphs & Plots

[prev: Text & LaTeX](chapter-04-text.md) | [next: 3D Scenes](chapter-06-3d.md)

Manim provides `Axes` and `NumberPlane` for plotting functions, parametric curves, and data.

## Basic Axes and Plot

```python
from manim import *

class BasicPlot(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 8, 2],
            axis_config={"include_numbers": True},
        )
        graph = axes.plot(lambda x: x**2, color=BLUE)
        label = axes.get_graph_label(graph, label="x^2")

        self.play(Create(axes), Create(graph), Write(label))
        self.wait()
```

```bash
manim -pql scene.py BasicPlot
```

## NumberPlane

```python
from manim import *

class NumberPlaneExample(Scene):
    def construct(self):
        plane = NumberPlane()
        graph = plane.plot(lambda x: 0.5 * x**2 - 1, color=YELLOW)

        self.play(Create(plane), Create(graph))
        self.wait()
```

```bash
manim -pql scene.py NumberPlaneExample
```

## Area Under Curve

```python
from manim import *

class AreaUnderCurve(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 10, 2])
        graph = axes.plot(lambda x: 0.4 * x**2, color=BLUE)
        area = axes.get_area(graph, x_range=[1, 4], color=GREEN, opacity=0.5)

        self.play(Create(axes), Create(graph))
        self.play(FadeIn(area))
        self.wait()
```

```bash
manim -pql scene.py AreaUnderCurve
```

## Parametric Curves

```python
from manim import *
import numpy as np

class ParametricCurveExample(Scene):
    def construct(self):
        axes = Axes(x_range=[-3, 3], y_range=[-3, 3])
        curve = axes.plot_parametric_curve(
            lambda t: np.array([np.cos(t), np.sin(t), 0]),
            t_range=[0, 2 * PI],
            color=RED,
        )

        self.play(Create(axes), Create(curve))
        self.wait()
```

```bash
manim -pql scene.py ParametricCurveExample
```

## Polar Plots

```python
from manim import *
import numpy as np

class PolarPlotExample(Scene):
    def construct(self):
        plane = PolarPlane(radius_max=3).add_coordinates()
        graph = plane.plot_polar_graph(
            lambda theta: 2 * np.cos(3 * theta),
            theta_range=[0, 2 * PI],
            color=ORANGE,
        )

        self.play(Create(plane), Create(graph))
        self.wait()
```

```bash
manim -pql scene.py PolarPlotExample
```

## Bar Chart

```python
from manim import *

class BarChartExample(Scene):
    def construct(self):
        chart = BarChart(
            values=[3, 5, 2, 8, 4],
            bar_names=["A", "B", "C", "D", "E"],
            y_range=[0, 10, 2],
            bar_colors=[BLUE, GREEN, RED, YELLOW, PURPLE],
        )

        self.play(Create(chart))
        self.wait()
```

```bash
manim -pql scene.py BarChartExample
```

## Labels and Dots on Graphs

```python
from manim import *

class DotsOnGraph(Scene):
    def construct(self):
        axes = Axes(x_range=[-1, 5, 1], y_range=[-1, 10, 2])
        graph = axes.plot(lambda x: x**2, x_range=[0, 3], color=BLUE)

        dot = Dot(axes.c2p(2, 4), color=RED)
        label = MathTex("(2, 4)").next_to(dot, UR, buff=0.1)

        self.play(Create(axes), Create(graph))
        self.play(Create(dot), Write(label))
        self.wait()
```

```bash
manim -pql scene.py DotsOnGraph
```

## TracedPath

```python
from manim import *

class TracedPathExample(Scene):
    def construct(self):
        dot = Dot(color=RED)
        trace = TracedPath(dot.get_center, stroke_color=YELLOW)

        self.add(trace, dot)
        self.play(dot.animate(run_time=3, rate_func=linear).shift(RIGHT * 4))
        self.play(dot.animate(run_time=2).shift(UP * 2 + LEFT * 2))
        self.wait()
```

```bash
manim -pql scene.py TracedPathExample
```

## ValueTracker for Animated Parameters

```python
from manim import *

class ValueTrackerExample(Scene):
    def construct(self):
        axes = Axes(x_range=[-3, 3, 1], y_range=[-1, 5, 1])
        tracker = ValueTracker(1)

        graph = always_redraw(
            lambda: axes.plot(
                lambda x: tracker.get_value() * x**2,
                color=BLUE,
            )
        )
        label = always_redraw(
            lambda: MathTex(f"a = {tracker.get_value():.1f}").to_edge(UR)
        )

        self.play(Create(axes), Create(graph), Write(label))
        self.play(tracker.animate.set_value(3), run_time=3)
        self.play(tracker.animate.set_value(0.5), run_time=3)
        self.wait()
```

```bash
manim -pql scene.py ValueTrackerExample
```
