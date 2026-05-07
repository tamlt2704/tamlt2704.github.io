# Intro to Manim — Step by Step

A runnable Manim script for every section of the [DevTaoism Manim course](https://docs.devtaoism.com/docs/html/index.html). Each file is a self-contained lesson — render it, watch it, read the code.

## Render Any Episode

```bash
pip install manim
manim -pql 01_basic_elements.py BasicElements
```

Replace `-pql` (low quality, fast) with `-pqh` (high quality) for final renders.

## Episodes

| # | DevTaoism Section | File | What You See |
|---|---|---|---|
| 01 | Basic Elements | `01_basic_elements.py` | Scene structure, Mobjects, add, play, wait |
| 02 | Basic Attributes | `02_basic_attributes.py` | Camera coords, move_to, shift, next_to, scale, color |
| 03 | Camera & Render | `03_camera_render.py` | Resolution, background color, CLI flags |
| 04 | Layers | `04_layers.py` | z_index, Scene.mobjects ordering |
| 05 | Rate Functions | `05_rate_functions.py` | smooth, linear, rush_into, there_and_back, all visualized |
| 06 | Import Assets | `06_assets.py` | Images, SVG, sounds |
| 07 | Groups & VGroups | `07_groups.py` | Group, VGroup, arrange, list comprehension |
| 08 | Text & Tex | `08_text_tex.py` | Text, MarkupText, Tex, MathTex |
| 09 | Transformations | `09_transformations.py` | Transform, ReplacementTransform, FadeTransform, matching |
| 10 | Methods as Animations | `10_methods_animations.py` | .animate, MoveToTarget, ApplyFunction, rotation |
| 11 | Manim Utilities | `11_utilities.py` | Helpful methods, VMobjects, class animations |
| 12 | 2D Graphs | `12_2d_graphs.py` | Axes, plot, parametric, NumberPlane, Riemann |
| 13 | 3D Graphs | `13_3d_graphs.py` | ThreeDScene, camera, surfaces, parametric 3D |
| 14 | Updaters | `14_updaters.py` | always_redraw, ValueTracker, DecimalNumber, dt |
