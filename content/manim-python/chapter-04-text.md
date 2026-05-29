# Chapter 4: Text & LaTeX

[prev: Animations](chapter-03-animations.md) | [next: Graphs & Plots](chapter-05-graphs.md)

Manim supports plain text, Pango markup, and full LaTeX rendering for mathematical equations.

## Text

```python
from manim import *

class TextExample(Scene):
    def construct(self):
        t1 = Text("Hello Manim", font_size=72, color=BLUE)
        t2 = Text("Custom Font", font="Courier New", font_size=48).shift(DOWN)
        t3 = Text("Colored", color=RED, weight=BOLD, font_size=48).shift(DOWN * 2)

        self.play(Write(t1))
        self.play(Write(t2))
        self.play(Write(t3))
        self.wait()
```

```bash
manim -pql scene.py TextExample
```

## MarkupText (Pango Markup)

```python
from manim import *

class MarkupTextExample(Scene):
    def construct(self):
        text = MarkupText(
            'This is <b>bold</b>, <i>italic</i>, and <span foreground="red">red</span>',
            font_size=36
        )
        self.play(Write(text))
        self.wait()
```

```bash
manim -pql scene.py MarkupTextExample
```

## MathTex (LaTeX Math Mode)

Requires LaTeX installed. Renders math expressions.

```python
from manim import *

class MathTexExample(Scene):
    def construct(self):
        eq1 = MathTex(r"e^{i\pi} + 1 = 0")
        eq2 = MathTex(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}").shift(DOWN)
        eq3 = MathTex(r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}").shift(DOWN * 2)

        self.play(Write(eq1))
        self.play(Write(eq2))
        self.play(Write(eq3))
        self.wait()
```

```bash
manim -pql scene.py MathTexExample
```

## Tex (Full LaTeX)

```python
from manim import *

class TexExample(Scene):
    def construct(self):
        tex = Tex(r"This is \textbf{bold} and $x^2 + y^2 = r^2$ is math.")
        self.play(Write(tex))
        self.wait()
```

```bash
manim -pql scene.py TexExample
```

## TransformMatchingTex

Smoothly transforms one equation into another, matching corresponding parts.

```python
from manim import *

class TransformMatchingTexExample(Scene):
    def construct(self):
        eq1 = MathTex(r"a^2 + b^2 = c^2")
        eq2 = MathTex(r"c = \sqrt{a^2 + b^2}")

        self.play(Write(eq1))
        self.wait()
        self.play(TransformMatchingTex(eq1, eq2))
        self.wait()
```

```bash
manim -pql scene.py TransformMatchingTexExample
```

## Step-by-Step Equations

```python
from manim import *

class StepByStep(Scene):
    def construct(self):
        steps = VGroup(
            MathTex(r"2x + 3 = 7"),
            MathTex(r"2x = 7 - 3"),
            MathTex(r"2x = 4"),
            MathTex(r"x = 2"),
        ).arrange(DOWN, buff=0.5)

        for step in steps:
            self.play(Write(step))
            self.wait(0.5)
        self.wait()
```

```bash
manim -pql scene.py StepByStep
```

## Aligning Equations

```python
from manim import *

class AlignedEquations(Scene):
    def construct(self):
        equations = MathTex(
            r"3x + 2y &= 7 \\",
            r"x - y &= 1 \\",
            r"x &= 2 \\",
            r"y &= \frac{1}{2}",
        )
        self.play(Write(equations))
        self.wait()
```

```bash
manim -pql scene.py AlignedEquations
```

## BulletedList and Title

```python
from manim import *

class TitleAndBullets(Scene):
    def construct(self):
        title = Title("Key Concepts")
        bullets = BulletedList(
            "Mobjects are on-screen objects",
            "Animations transform mobjects",
            "Scenes compose the final video",
            font_size=36
        ).shift(DOWN * 0.5)

        self.play(Write(title))
        for item in bullets:
            self.play(FadeIn(item, shift=RIGHT))
        self.wait()
```

```bash
manim -pql scene.py TitleAndBullets
```

## Coloring Parts of Equations

```python
from manim import *

class ColoredEquation(Scene):
    def construct(self):
        eq = MathTex(r"e", r"^{i\pi}", r"+", r"1", r"=", r"0")
        eq[0].set_color(RED)
        eq[1].set_color(BLUE)
        eq[3].set_color(GREEN)
        eq[5].set_color(YELLOW)

        self.play(Write(eq))
        self.wait()
```

```bash
manim -pql scene.py ColoredEquation
```
