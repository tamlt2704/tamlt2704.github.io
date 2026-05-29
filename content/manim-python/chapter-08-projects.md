# Chapter 8: Projects

[prev: Advanced](chapter-07-advanced.md) | [next: Overview](chapter-00-overview.md)

Complete project examples combining everything learned.

## Visualize Bubble Sort

```python
from manim import *

class BubbleSort(Scene):
    def construct(self):
        values = [5, 3, 8, 1, 4]
        bars = VGroup(*[
            Rectangle(width=0.5, height=v * 0.5, fill_opacity=0.8, color=BLUE)
            for v in values
        ]).arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
        self.play(Create(bars))

        n = len(values)
        for i in range(n):
            for j in range(n - i - 1):
                bars[j].set_color(RED)
                bars[j + 1].set_color(RED)
                self.wait(0.3)
                if values[j] > values[j + 1]:
                    values[j], values[j + 1] = values[j + 1], values[j]
                    self.play(
                        bars[j].animate.move_to(bars[j + 1].get_center()),
                        bars[j + 1].animate.move_to(bars[j].get_center()),
                        run_time=0.5,
                    )
                    bars[j], bars[j + 1] = bars[j + 1], bars[j]
                bars[j].set_color(BLUE)
                bars[j + 1].set_color(BLUE)
            bars[n - i - 1].set_color(GREEN)
        self.wait()
```

```bash
manim -pql scene.py BubbleSort
```

## Fourier Transform Visualization

```python
from manim import *
import numpy as np

class FourierVisualization(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 4 * PI, PI], y_range=[-2, 2, 1])
        labels = axes.get_axis_labels(x_label="t", y_label="f(t)")

        # Sum of sine waves
        graph1 = axes.plot(lambda x: np.sin(x), color=BLUE)
        graph2 = axes.plot(lambda x: np.sin(x) + 0.5 * np.sin(3 * x), color=GREEN)
        graph3 = axes.plot(
            lambda x: np.sin(x) + 0.5 * np.sin(3 * x) + 0.25 * np.sin(5 * x),
            color=RED,
        )

        l1 = MathTex(r"\sin(t)", color=BLUE, font_size=28).to_edge(UR)
        l2 = MathTex(r"+ \frac{1}{2}\sin(3t)", color=GREEN, font_size=28).next_to(l1, DOWN)
        l3 = MathTex(r"+ \frac{1}{4}\sin(5t)", color=RED, font_size=28).next_to(l2, DOWN)

        self.play(Create(axes), Write(labels))
        self.play(Create(graph1), Write(l1))
        self.play(ReplacementTransform(graph1, graph2), Write(l2))
        self.play(ReplacementTransform(graph2, graph3), Write(l3))
        self.wait()
```

```bash
manim -pql scene.py FourierVisualization
```

## Linear Algebra: Vector Transformation

```python
from manim import *
import numpy as np

class LinearTransformation(Scene):
    def construct(self):
        plane = NumberPlane()
        vector = Arrow(ORIGIN, [2, 1, 0], buff=0, color=YELLOW)
        label = MathTex(r"\vec{v}", color=YELLOW).next_to(vector.get_end(), UR, buff=0.1)

        self.play(Create(plane), Create(vector), Write(label))
        self.wait()

        # Apply 2x2 matrix transformation
        matrix = [[2, 1], [0, 1]]
        new_end = np.array([
            matrix[0][0] * 2 + matrix[0][1] * 1,
            matrix[1][0] * 2 + matrix[1][1] * 1,
            0,
        ])
        new_vector = Arrow(ORIGIN, new_end, buff=0, color=RED)
        mat_label = MathTex(
            r"A = \begin{bmatrix} 2 & 1 \\ 0 & 1 \end{bmatrix}"
        ).to_edge(UL)

        self.play(Write(mat_label))
        self.play(
            plane.animate.apply_matrix(matrix),
            Transform(vector, new_vector),
            run_time=3,
        )
        self.wait()
```

```bash
manim -pql scene.py LinearTransformation
```

## Calculus: Derivative Visualization

```python
from manim import *

class DerivativeVisualization(Scene):
    def construct(self):
        axes = Axes(x_range=[-1, 4, 1], y_range=[-1, 10, 2])
        graph = axes.plot(lambda x: x**2, color=BLUE)
        graph_label = axes.get_graph_label(graph, label="x^2")

        tracker = ValueTracker(1)
        dot = always_redraw(
            lambda: Dot(axes.c2p(tracker.get_value(), tracker.get_value() ** 2), color=RED)
        )
        tangent = always_redraw(
            lambda: axes.get_secant_slope_group(
                x=tracker.get_value(),
                graph=graph,
                dx=0.01,
                secant_line_length=3,
                secant_line_color=YELLOW,
            )
        )
        slope_label = always_redraw(
            lambda: MathTex(
                f"f'(x) = {2 * tracker.get_value():.1f}", font_size=28
            ).to_edge(UR)
        )

        self.play(Create(axes), Create(graph), Write(graph_label))
        self.play(Create(dot), Create(tangent), Write(slope_label))
        self.play(tracker.animate.set_value(3), run_time=4)
        self.play(tracker.animate.set_value(0.5), run_time=3)
        self.wait()
```

```bash
manim -pql scene.py DerivativeVisualization
```

## Physics: Projectile Motion

```python
from manim import *
import numpy as np

class ProjectileMotion(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 5, 1])
        labels = axes.get_axis_labels(x_label="x", y_label="y")

        v0 = 7
        angle = 45 * DEGREES
        g = 9.8
        t_max = 2 * v0 * np.sin(angle) / g

        path = axes.plot_parametric_curve(
            lambda t: np.array([
                v0 * np.cos(angle) * t,
                v0 * np.sin(angle) * t - 0.5 * g * t**2,
                0,
            ]),
            t_range=[0, t_max],
            color=YELLOW,
        )

        dot = Dot(color=RED)
        self.play(Create(axes), Write(labels))
        self.play(MoveAlongPath(dot, path, run_time=3, rate_func=linear))
        self.play(Create(path))
        self.wait()
```

```bash
manim -pql scene.py ProjectileMotion
```

## Fractal: Koch Snowflake Zoom

```python
from manim import *
import numpy as np

class KochSnowflake(Scene):
    def construct(self):
        def koch_points(p1, p2, depth):
            if depth == 0:
                return [p1]
            d = (p2 - p1) / 3
            a = p1 + d
            b = p1 + 2 * d
            # Rotate d by 60 degrees for peak
            peak = a + np.array([
                d[0] * np.cos(PI / 3) - d[1] * np.sin(PI / 3),
                d[0] * np.sin(PI / 3) + d[1] * np.cos(PI / 3),
                0,
            ])
            pts = []
            pts += koch_points(p1, a, depth - 1)
            pts += koch_points(a, peak, depth - 1)
            pts += koch_points(peak, b, depth - 1)
            pts += koch_points(b, p2, depth - 1)
            return pts

        # Triangle vertices
        s = 4
        p1 = np.array([-s / 2, -s * np.sqrt(3) / 6, 0])
        p2 = np.array([s / 2, -s * np.sqrt(3) / 6, 0])
        p3 = np.array([0, s * np.sqrt(3) / 3, 0])

        for depth in range(5):
            pts = koch_points(p1, p2, depth)
            pts += koch_points(p2, p3, depth)
            pts += koch_points(p3, p1, depth)
            pts.append(pts[0])
            snowflake = VMobject(color=BLUE)
            snowflake.set_points_as_corners(pts)
            if depth == 0:
                self.play(Create(snowflake))
            else:
                self.play(Transform(prev, snowflake), run_time=1.5)
            prev = snowflake if depth == 0 else prev
            self.wait(0.5)
        self.wait()
```

```bash
manim -pql scene.py KochSnowflake
```
