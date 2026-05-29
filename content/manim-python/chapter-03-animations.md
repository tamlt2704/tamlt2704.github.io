# Chapter 3: Animations

[prev: Shapes](chapter-02-shapes.md) | [next: Text & LaTeX](chapter-04-text.md)

Animations bring mobjects to life. Use `self.play()` to run them and `self.wait()` to pause.

## Creation Animations

```python
from manim import *

class CreationAnimations(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        square = Square(color=RED).shift(RIGHT * 3)
        triangle = Triangle(color=GREEN).shift(LEFT * 3)

        self.play(Create(circle))
        self.play(DrawBorderThenFill(square))
        self.play(GrowFromCenter(triangle))
        self.wait()
```

```bash
manim -pql scene.py CreationAnimations
```

## Fade Animations

```python
from manim import *

class FadeAnimations(Scene):
    def construct(self):
        square = Square(color=BLUE, fill_opacity=0.7)
        self.play(FadeIn(square))
        self.wait(0.5)
        self.play(FadeOut(square))

        circle = Circle(color=RED, fill_opacity=0.7)
        self.play(FadeIn(circle, shift=UP))
        self.play(FadeOut(circle, shift=DOWN))
        self.wait()
```

```bash
manim -pql scene.py FadeAnimations
```

## Write Animation

```python
from manim import *

class WriteAnimation(Scene):
    def construct(self):
        text = Text("Hello Manim!", font_size=72)
        self.play(Write(text))
        self.wait()
```

```bash
manim -pql scene.py WriteAnimation
```

## Transform

```python
from manim import *

class TransformExample(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)

        self.play(Create(circle))
        self.play(Transform(circle, square))
        self.wait()
```

```bash
manim -pql scene.py TransformExample
```

## ReplacementTransform

```python
from manim import *

class ReplacementTransformExample(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5)

        self.play(Create(circle))
        self.play(ReplacementTransform(circle, square))
        self.play(ReplacementTransform(square, triangle))
        self.wait()
```

```bash
manim -pql scene.py ReplacementTransformExample
```

## MoveToTarget

```python
from manim import *

class MoveToTargetExample(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        circle.generate_target()
        circle.target.shift(RIGHT * 3)
        circle.target.scale(0.5)
        circle.target.set_color(RED)

        self.play(Create(circle))
        self.play(MoveToTarget(circle))
        self.wait()
```

```bash
manim -pql scene.py MoveToTargetExample
```

## Rotate

```python
from manim import *

class RotateExample(Scene):
    def construct(self):
        square = Square(color=BLUE, fill_opacity=0.5)
        self.play(Create(square))
        self.play(Rotate(square, angle=PI / 2))
        self.play(Rotate(square, angle=PI, about_point=RIGHT * 2))
        self.wait()
```

```bash
manim -pql scene.py RotateExample
```

## Attention Animations

```python
from manim import *

class AttentionAnimations(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5).shift(RIGHT * 3)
        triangle = Triangle(color=GREEN, fill_opacity=0.5).shift(LEFT * 3)

        self.play(Create(VGroup(circle, square, triangle)))
        self.play(Indicate(circle))
        self.play(Flash(square))
        self.play(Circumscribe(triangle))
        self.wait()
```

```bash
manim -pql scene.py AttentionAnimations
```

## Timing: run_time and wait

```python
from manim import *

class TimingExample(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        self.play(Create(circle), run_time=3)
        self.wait(2)
        self.play(FadeOut(circle), run_time=0.5)
        self.wait()
```

```bash
manim -pql scene.py TimingExample
```

## Rate Functions

Rate functions control the easing/acceleration of animations.

```python
from manim import *

class RateFuncExample(Scene):
    def construct(self):
        funcs = [smooth, linear, rush_into, there_and_back]
        names = ["smooth", "linear", "rush_into", "there_and_back"]

        dots = VGroup()
        labels = VGroup()
        for i, (func, name) in enumerate(zip(funcs, names)):
            dot = Dot(color=BLUE).move_to(LEFT * 4 + DOWN * (i - 1.5))
            label = Text(name, font_size=20).next_to(dot, LEFT)
            dots.add(dot)
            labels.add(label)

        self.add(dots, labels)
        self.play(*[
            dot.animate(rate_func=func, run_time=3).shift(RIGHT * 8)
            for dot, func in zip(dots, funcs)
        ])
        self.wait()
```

```bash
manim -pql scene.py RateFuncExample
```

Available rate functions:

- `smooth` — default, ease in and out
- `linear` — constant speed
- `rush_into` — accelerate at the end
- `rush_from` — fast start, decelerate
- `there_and_back` — go forward then return
- `wiggle` — oscillate

## Playing Multiple Animations

```python
from manim import *

class SimultaneousAnimations(Scene):
    def construct(self):
        circle = Circle(color=BLUE).shift(LEFT * 2)
        square = Square(color=RED).shift(RIGHT * 2)

        self.play(Create(circle), Create(square))
        self.play(
            circle.animate.shift(RIGHT * 2),
            square.animate.shift(LEFT * 2),
        )
        self.wait()
```

```bash
manim -pql scene.py SimultaneousAnimations
```
