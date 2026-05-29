# Chapter 7: Advanced

[prev: 3D Scenes](chapter-06-3d.md) | [next: Projects](chapter-08-projects.md)

Advanced techniques: custom animations, updaters, ValueTracker, SVG import, and rendering pipeline.

## Updaters with always_redraw

```python
from manim import *

class AlwaysRedrawExample(Scene):
    def construct(self):
        tracker = ValueTracker(0)
        dot = always_redraw(
            lambda: Dot(point=RIGHT * tracker.get_value(), color=RED)
        )
        line = always_redraw(
            lambda: Line(ORIGIN, RIGHT * tracker.get_value(), color=BLUE)
        )

        self.add(dot, line)
        self.play(tracker.animate.set_value(4), run_time=3)
        self.play(tracker.animate.set_value(-2), run_time=2)
        self.wait()
```

```bash
manim -pql scene.py AlwaysRedrawExample
```

## add_updater

```python
from manim import *

class AddUpdaterExample(Scene):
    def construct(self):
        dot = Dot(color=RED)
        label = Text("here", font_size=20)
        label.add_updater(lambda m: m.next_to(dot, UP))

        self.add(dot, label)
        self.play(dot.animate.shift(RIGHT * 3), run_time=2)
        self.play(dot.animate.shift(UP * 2 + LEFT * 4), run_time=2)
        self.wait()
```

```bash
manim -pql scene.py AddUpdaterExample
```

## ValueTracker with Updater

```python
from manim import *
import numpy as np

class ValueTrackerUpdater(Scene):
    def construct(self):
        axes = Axes(x_range=[-4, 4], y_range=[-2, 2])
        freq = ValueTracker(1)

        graph = always_redraw(
            lambda: axes.plot(
                lambda x: np.sin(freq.get_value() * x),
                color=BLUE,
            )
        )
        freq_label = always_redraw(
            lambda: Text(f"freq = {freq.get_value():.1f}", font_size=28).to_edge(UR)
        )

        self.play(Create(axes), Create(graph), Write(freq_label))
        self.play(freq.animate.set_value(4), run_time=4)
        self.play(freq.animate.set_value(0.5), run_time=3)
        self.wait()
```

```bash
manim -pql scene.py ValueTrackerUpdater
```

## Custom Animation Subclass

```python
from manim import *

class Pulse(Animation):
    def __init__(self, mobject, scale_factor=1.5, **kwargs):
        self.scale_factor = scale_factor
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        if alpha < 0.5:
            scale = 1 + (self.scale_factor - 1) * (alpha * 2)
        else:
            scale = self.scale_factor - (self.scale_factor - 1) * ((alpha - 0.5) * 2)
        self.mobject.become(self.starting_mobject.copy().scale(scale))


class CustomAnimationExample(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        self.play(Create(circle))
        self.play(Pulse(circle, scale_factor=2, run_time=1.5))
        self.wait()
```

```bash
manim -pql scene.py CustomAnimationExample
```

## Custom Rate Function

```python
from manim import *
import numpy as np

def bounce(t):
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - (2 * (1 - t)) ** 2 / 2


class CustomRateFunc(Scene):
    def construct(self):
        dot = Dot(color=RED).to_edge(LEFT)
        self.play(dot.animate(rate_func=bounce, run_time=3).to_edge(RIGHT))
        self.wait()
```

```bash
manim -pql scene.py CustomRateFunc
```

## SVG Import

```python
from manim import *

class SVGExample(Scene):
    def construct(self):
        # Place an SVG file in the same directory
        svg = SVGMobject("icon.svg").scale(2)
        self.play(DrawBorderThenFill(svg))
        self.play(svg.animate.set_color(BLUE))
        self.wait()
```

```bash
manim -pql scene.py SVGExample
```

## ImageMobject

```python
from manim import *

class ImageExample(Scene):
    def construct(self):
        img = ImageMobject("photo.png").scale(0.5)
        border = SurroundingRectangle(img, color=WHITE)

        self.play(FadeIn(img), Create(border))
        self.play(img.animate.shift(LEFT * 2))
        self.wait()
```

```bash
manim -pql scene.py ImageExample
```

## Scene Composition

```python
from manim import *

class PartOne(Scene):
    def construct(self):
        self.play(Write(Text("Part 1")))
        self.wait()


class PartTwo(Scene):
    def construct(self):
        self.play(Write(Text("Part 2")))
        self.wait()
```

Render multiple scenes and concatenate:

```bash
manim -pql scene.py PartOne
manim -pql scene.py PartTwo
# Combine with ffmpeg:
ffmpeg -f concat -i filelist.txt -c copy output.mp4
```

## Rendering Pipeline

Manim rendering steps:

1. Scene `construct()` is called
2. Each `self.play()` generates animation frames
3. Frames are written as PNG images to `media/images/`
4. ffmpeg combines frames into video
5. Output saved to `media/videos/<filename>/<quality>/`

Useful flags:

- `--disable_caching` — re-render everything
- `-n 5,10` — render only frames 5 through 10
- `--write_all` — render all scenes in a file
