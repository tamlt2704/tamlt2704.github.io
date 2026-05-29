# Chapter 2: Shapes & Mobjects

[prev: Setup](chapter-01-setup.md) | [next: Animations](chapter-03-animations.md)

Everything you see on screen in Manim is a **Mobject** (mathematical object). Shapes are `VMobject` subclasses (vectorized mobjects).

## Basic Shapes

```python
from manim import *

class BasicShapes(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=1.5, color=RED)
        rect = Rectangle(width=3, height=1, color=GREEN)
        triangle = Triangle(color=YELLOW)
        dot = Dot(color=WHITE)

        shapes = VGroup(circle, square, rect, triangle, dot).arrange(RIGHT, buff=0.5)
        self.play(Create(shapes))
        self.wait()
```

```bash
manim -pql scene.py BasicShapes
```

## Lines and Arrows

```python
from manim import *

class LinesAndArrows(Scene):
    def construct(self):
        line = Line(LEFT * 3, RIGHT * 3, color=BLUE)
        arrow = Arrow(LEFT * 2, RIGHT * 2, color=RED)
        arc = Arc(radius=1, angle=PI, color=GREEN)

        group = VGroup(line, arrow, arc).arrange(DOWN, buff=0.8)
        self.play(Create(group))
        self.wait()
```

```bash
manim -pql scene.py LinesAndArrows
```

## Polygons

```python
from manim import *

class PolygonShapes(Scene):
    def construct(self):
        polygon = Polygon(
            [-2, 0, 0], [0, 2, 0], [2, 0, 0], [1, -1, 0], [-1, -1, 0],
            color=PURPLE
        )
        reg_poly = RegularPolygon(n=6, color=TEAL)
        star = Star(n=5, color=YELLOW, fill_opacity=0.5)

        group = VGroup(polygon, reg_poly, star).arrange(RIGHT, buff=1)
        self.play(Create(group))
        self.wait()
```

```bash
manim -pql scene.py PolygonShapes
```

## Properties

```python
from manim import *

class ShapeProperties(Scene):
    def construct(self):
        c1 = Circle(color=RED, fill_opacity=0.0)
        c2 = Circle(color=GREEN, fill_opacity=0.5)
        c3 = Circle(color=BLUE, fill_opacity=1.0)
        c4 = Circle(color=YELLOW, stroke_width=8)

        group = VGroup(c1, c2, c3, c4).arrange(RIGHT, buff=0.5)
        self.play(Create(group))
        self.wait()
```

```bash
manim -pql scene.py ShapeProperties
```

Key properties:

- `color` — stroke/border color
- `fill_opacity` — 0 (transparent) to 1 (solid fill)
- `stroke_width` — border thickness (default 4)

## Positioning

```python
from manim import *

class Positioning(Scene):
    def construct(self):
        c1 = Circle(radius=0.3, color=RED).move_to(LEFT * 3 + UP * 2)
        square = Square(side_length=0.5, color=BLUE)
        label = Text("Hi", font_size=24).next_to(square, UP)
        c2 = Circle(radius=0.3, color=GREEN).shift(RIGHT * 2)
        c3 = Circle(radius=0.3, color=YELLOW).to_edge(DOWN)
        c4 = Circle(radius=0.3, color=PURPLE).align_to(c1, UP)

        self.play(Create(VGroup(c1, square, label, c2, c3, c4)))
        self.wait()
```

```bash
manim -pql scene.py Positioning
```

Positioning methods:

- `move_to(point)` — move center to absolute position
- `next_to(obj, direction, buff=0.25)` — place next to another object
- `shift(vector)` — relative displacement
- `to_edge(direction, buff=0.5)` — snap to screen edge
- `align_to(obj, direction)` — align along an edge

## VGroup

Group mobjects together to transform them as one unit.

```python
from manim import *

class GroupExample(Scene):
    def construct(self):
        group = VGroup(
            Circle(color=RED),
            Square(color=GREEN),
            Triangle(color=BLUE),
        ).arrange(RIGHT, buff=0.5)

        self.play(Create(group))
        self.play(group.animate.shift(UP))
        self.play(group.animate.scale(0.5))
        self.play(group.animate.rotate(PI / 4))
        self.wait()
```

```bash
manim -pql scene.py GroupExample
```

VGroup supports indexing and iteration:

```python
from manim import *

class GroupIndexing(Scene):
    def construct(self):
        dots = VGroup(*[Dot(color=BLUE) for _ in range(10)]).arrange(RIGHT, buff=0.3)
        self.play(Create(dots))
        for i in range(0, 10, 2):
            dots[i].set_color(RED)
        self.play(dots.animate.shift(UP))
        self.wait()
```

```bash
manim -pql scene.py GroupIndexing
```
