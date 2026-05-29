# Manim - Mathematical Animation Engine

Create beautiful math animations with Python. Manim is the library 3Blue1Brown uses to produce stunning mathematical visualizations.

## Chapters

- [Chapter 1: Setup](chapter-01-setup.md) - Installation, first scene, running animations
- [Chapter 2: Shapes & Mobjects](chapter-02-shapes.md) - Circles, squares, positioning, groups
- [Chapter 3: Animations](chapter-03-animations.md) - FadeIn, Transform, timing, rate functions
- [Chapter 4: Text & LaTeX](chapter-04-text.md) - Text rendering, math equations, formatting
- [Chapter 5: Graphs & Plots](chapter-05-graphs.md) - Axes, functions, parametric curves, bar charts
- [Chapter 6: 3D Scenes](chapter-06-3d.md) - 3D objects, surfaces, camera rotation
- [Chapter 7: Advanced](chapter-07-advanced.md) - Custom animations, updaters, SVG import
- [Chapter 8: Projects](chapter-08-projects.md) - Sorting, Fourier, linear algebra, calculus

## What You Can Build

- Explanatory math videos like 3Blue1Brown
- Algorithm visualizations
- Physics simulations
- Data visualizations with animated transitions
- Educational content with step-by-step equation reveals

## Quick Start

```python
from manim import *

class HelloManim(Scene):
    def construct(self):
        text = Text("Hello, Manim!")
        self.play(Write(text))
        self.wait()
```

Render it:

```bash
manim -pql scene.py HelloManim
```
