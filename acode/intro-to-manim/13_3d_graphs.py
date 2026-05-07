"""
Intro to Manim — 13: Basic 3D Graphs
Covers: ThreeDScene, camera, ThreeDAxes, parametric 3D, surfaces.
Source: https://docs.devtaoism.com/docs/html/contents/_13_3d_graphs.html

Render: manim -pql 13_3d_graphs.py Graphs3D
"""
from manim import *
import numpy as np


class Graphs3D(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"
        self.setting_camera()
        self.three_d_axes()
        self.parametric_3d()
        self.surfaces()

    def setting_camera(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)

        title = Text("13: 3D Graphs", font_size=28, color=YELLOW)
        self.add_fixed_in_frame_mobjects(title)
        title.to_edge(UP)
        self.play(Write(title))

        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-2, 2, 1],
            x_length=6, y_length=6, z_length=4,
            axis_config={"color": GREY},
        )
        self.play(Create(axes))

        # Move camera
        self.move_camera(phi=60 * DEGREES, theta=-30 * DEGREES, run_time=2)
        self.move_camera(phi=45 * DEGREES, theta=-90 * DEGREES, run_time=2)
        self.wait()
        self.play(FadeOut(axes), FadeOut(title))

    def three_d_axes(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        axes = ThreeDAxes(x_range=[-4, 4], y_range=[-4, 4], z_range=[-2, 2],
                          axis_config={"color": GREY, "stroke_width": 1})
        self.play(Create(axes))

        # Plot a 3D curve
        curve = ParametricFunction(
            lambda t: axes.c2p(2 * np.cos(t), 2 * np.sin(t), 0.3 * t),
            t_range=[0, 4 * PI], color=TEAL,
        )
        self.play(Create(curve), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(axes), FadeOut(curve))

    def parametric_3d(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)

        axes = ThreeDAxes(axis_config={"color": GREY, "stroke_width": 1})
        self.play(Create(axes))

        # Helix
        helix = ParametricFunction(
            lambda t: axes.c2p(np.cos(t), np.sin(t), 0.15 * t),
            t_range=[0, 6 * PI], color=YELLOW, stroke_width=2,
        )
        self.play(Create(helix), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(axes), FadeOut(helix))

    def surfaces(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        # Surface: z = sin(x) * cos(y)
        surface = Surface(
            lambda u, v: np.array([u, v, np.sin(u) * np.cos(v)]),
            u_range=[-3, 3], v_range=[-3, 3],
            resolution=(30, 30),
            fill_color=TEAL, fill_opacity=0.7,
            stroke_color=TEAL_A, stroke_width=0.3,
        )
        self.play(Create(surface), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(4)
        self.stop_ambient_camera_rotation()

        # Transform to another surface
        surface2 = Surface(
            lambda u, v: np.array([
                (2 + 0.5 * np.cos(v)) * np.cos(u),
                (2 + 0.5 * np.cos(v)) * np.sin(u),
                0.5 * np.sin(v),
            ]),
            u_range=[0, TAU], v_range=[0, TAU],
            resolution=(36, 18),
            fill_color=ORANGE, fill_opacity=0.8,
            stroke_color=ORANGE, stroke_width=0.3,
        )

        label = Text("Torus", font_size=20, color=ORANGE)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(DOWN)

        self.play(Transform(surface, surface2), FadeIn(label), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(4)
        self.stop_ambient_camera_rotation()
