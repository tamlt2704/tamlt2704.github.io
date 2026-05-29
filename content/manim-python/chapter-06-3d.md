# Chapter 6: 3D Scenes

[prev: Graphs & Plots](chapter-05-graphs.md) | [next: Advanced](chapter-07-advanced.md)

Manim supports 3D rendering with `ThreeDScene`, camera control, and parametric surfaces.

## Basic 3D Scene

```python
from manim import *

class Basic3D(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        sphere = Sphere(radius=1, color=BLUE)

        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.play(Create(axes), Create(sphere))
        self.wait()
```

```bash
manim -pql scene.py Basic3D
```

## 3D Primitives

```python
from manim import *

class Primitives3D(ThreeDScene):
    def construct(self):
        cube = Cube(side_length=1, fill_opacity=0.5, color=BLUE)
        sphere = Sphere(radius=0.7, color=RED).shift(RIGHT * 3)
        torus = Torus(major_radius=1, minor_radius=0.3, color=GREEN).shift(LEFT * 3)

        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.play(Create(cube), Create(sphere), Create(torus))
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(4)
```

```bash
manim -pql scene.py Primitives3D
```

## Parametric Surfaces

```python
from manim import *
import numpy as np

class ParametricSurfaceExample(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        surface = Surface(
            lambda u, v: axes.c2p(u * np.cos(v), u * np.sin(v), u),
            u_range=[0, 2],
            v_range=[0, 2 * PI],
            fill_opacity=0.7,
        )

        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.play(Create(axes), Create(surface))
        self.wait()
```

```bash
manim -pql scene.py ParametricSurfaceExample
```

## Camera Rotation

```python
from manim import *

class CameraRotation(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        cube = Cube(side_length=1.5, fill_opacity=0.7, color=BLUE)

        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        self.play(Create(axes), Create(cube))

        # Animate camera movement
        self.move_camera(phi=30 * DEGREES, theta=45 * DEGREES, run_time=3)
        self.move_camera(phi=60 * DEGREES, gamma=30 * DEGREES, run_time=2)
        self.wait()
```

```bash
manim -pql scene.py CameraRotation
```

Camera angles:

- `phi` — polar angle (tilt from top, 0=top-down, 90=side view)
- `theta` — azimuthal angle (rotation around z-axis)
- `gamma` — roll angle

## 3D Function Plot

```python
from manim import *
import numpy as np

class Surface3DPlot(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-1, 5])
        surface = Surface(
            lambda u, v: axes.c2p(u, v, np.sin(u) * np.cos(v)),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(30, 30),
            fill_opacity=0.7,
        )
        surface.set_style(fill_color=BLUE)

        self.set_camera_orientation(phi=60 * DEGREES, theta=-60 * DEGREES)
        self.play(Create(axes), Create(surface))
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(5)
```

```bash
manim -pql scene.py Surface3DPlot
```

## 3D Arrows and Text

```python
from manim import *

class Arrows3D(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        x_arrow = Arrow3D(start=ORIGIN, end=[3, 0, 0], color=RED)
        y_arrow = Arrow3D(start=ORIGIN, end=[0, 3, 0], color=GREEN)
        z_arrow = Arrow3D(start=ORIGIN, end=[0, 0, 3], color=BLUE)

        x_label = Text("X", color=RED, font_size=24).next_to(x_arrow, RIGHT)
        y_label = Text("Y", color=GREEN, font_size=24).next_to(y_arrow, UP)

        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.play(Create(axes))
        self.play(Create(x_arrow), Create(y_arrow), Create(z_arrow))
        self.add_fixed_in_frame_mobjects(x_label, y_label)
        self.wait()
```

```bash
manim -pql scene.py Arrows3D
```

## Ambient Camera Rotation

```python
from manim import *
import numpy as np

class AmbientRotation(ThreeDScene):
    def construct(self):
        torus = Torus(major_radius=2, minor_radius=0.5, color=PURPLE, fill_opacity=0.8)

        self.set_camera_orientation(phi=60 * DEGREES, theta=0)
        self.play(Create(torus))
        self.begin_ambient_camera_rotation(rate=0.5)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.wait()
```

```bash
manim -pql scene.py AmbientRotation
```
