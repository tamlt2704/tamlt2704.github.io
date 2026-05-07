"""
Intro to Manim — 14: Basic Updaters
Covers: always_redraw, .become, ValueTracker, DecimalNumber, group updaters.
Source: https://docs.devtaoism.com/docs/html/contents/_14_basic_updaters.html

Render: manim -pql 14_updaters.py UpdatersScene
"""
from manim import *
import numpy as np


class UpdatersScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"
        self.basic_theory()
        self.become_demo()
        self.value_tracker_demo()
        self.decimal_number_demo()
        self.group_updater_demo()
        self.recap()

    # ── Basic Theory ─────────────────────────────
    def basic_theory(self):
        title = Text("14: Updaters", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        theory = VGroup(
            Text("Updaters = functions that run every frame", font_size=18, color=BLUE),
            Text("Two types:", font_size=16),
            Text("  1. always_redraw(lambda: ...) — rebuild object each frame",
                 font_size=14, color=GREY),
            Text("  2. mob.add_updater(func) — modify object each frame",
                 font_size=14, color=GREY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        theory.move_to(DOWN * 0.3)
        self.play(FadeIn(theory))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── .become ──────────────────────────────────
    def become_demo(self):
        title = Text(".become() — Instant Replacement", font_size=24, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # A dot that follows a sine wave using .become
        t = ValueTracker(0)
        dot = Dot(color=BLUE, radius=0.1)

        dot.add_updater(lambda m: m.become(
            Dot(color=BLUE, radius=0.1).move_to(
                [t.get_value(), np.sin(t.get_value()), 0]
            )
        ))

        # Trace
        path = TracedPath(dot.get_center, stroke_color=BLUE, stroke_width=2)

        self.add(dot, path)
        self.play(t.animate.set_value(4 * PI), run_time=4, rate_func=linear)
        self.wait()
        dot.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── ValueTracker ─────────────────────────────
    def value_tracker_demo(self):
        title = Text("ValueTracker — Animate a Number", font_size=24, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        t = ValueTracker(0)

        # Display the value
        value_text = always_redraw(lambda: Text(
            f"t = {t.get_value():.2f}", font_size=24, color=GREEN,
        ).to_edge(DOWN))

        # Circle that grows with t
        circle = always_redraw(lambda: Circle(
            radius=0.5 + t.get_value() * 0.3,
            color=interpolate_color(BLUE, RED, t.get_value() / 5),
            stroke_width=3,
        ))

        self.add(circle, value_text)
        self.play(t.animate.set_value(5), run_time=3)
        self.wait()
        self.play(t.animate.set_value(0), run_time=2)
        self.wait()
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── DecimalNumber ────────────────────────────
    def decimal_number_demo(self):
        title = Text("DecimalNumber — Auto-updating Counter", font_size=22, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        t = ValueTracker(0)

        # DecimalNumber automatically updates when linked to a ValueTracker
        number = DecimalNumber(0, num_decimal_places=1, font_size=64, color=WHITE)
        number.add_updater(lambda m: m.set_value(t.get_value()))

        label = Text("Counter:", font_size=20, color=GREY)
        label.next_to(number, UP, buff=0.3)

        self.add(number, label)
        self.play(t.animate.set_value(100), run_time=3, rate_func=smooth)
        self.wait()
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Group Updaters ───────────────────────────
    def group_updater_demo(self):
        title = Text("Group Updaters — Linked Objects", font_size=24, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # A line that always connects two dots
        dot_a = Dot(LEFT * 3, color=RED, radius=0.12)
        dot_b = Dot(RIGHT * 3, color=BLUE, radius=0.12)

        line = always_redraw(lambda: Line(
            dot_a.get_center(), dot_b.get_center(),
            color=WHITE, stroke_width=2,
        ))

        # Midpoint label
        mid_label = always_redraw(lambda: Text(
            f"d = {np.linalg.norm(dot_a.get_center() - dot_b.get_center()):.1f}",
            font_size=16, color=GREY,
        ).move_to((dot_a.get_center() + dot_b.get_center()) / 2 + UP * 0.4))

        self.add(line, dot_a, dot_b, mid_label)

        # Move dots around — line and label follow automatically
        self.play(dot_a.animate.move_to(UP * 2 + LEFT), run_time=1)
        self.play(dot_b.animate.move_to(DOWN * 2 + RIGHT * 2), run_time=1)
        self.play(
            dot_a.animate.move_to(LEFT * 2 + DOWN),
            dot_b.animate.move_to(RIGHT * 3 + UP * 2),
            run_time=1.5,
        )
        self.wait()

        # Orbit demo
        t = ValueTracker(0)
        dot_a.add_updater(lambda m: m.move_to(
            [2 * np.cos(t.get_value()), 2 * np.sin(t.get_value()), 0]))
        dot_b.add_updater(lambda m: m.move_to(
            [3 * np.cos(-t.get_value() * 0.7), 3 * np.sin(-t.get_value() * 0.7), 0]))

        self.play(t.animate.set_value(TAU * 2), run_time=6, rate_func=linear)
        dot_a.clear_updaters()
        dot_b.clear_updaters()
        self.wait()
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap ────────────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("Recap — The Full Updater Toolkit:", font_size=24, color=BLUE),
            Text("• always_redraw(lambda: ...) — rebuild each frame",
                 font_size=15, color=WHITE),
            Text("• mob.add_updater(func) — modify each frame",
                 font_size=15, color=WHITE),
            Text("• .become() — instant replacement inside updater",
                 font_size=15, color=WHITE),
            Text("• ValueTracker — animatable number",
                 font_size=15, color=WHITE),
            Text("• DecimalNumber — auto-updating counter",
                 font_size=15, color=WHITE),
            Text("• TracedPath — leave a trail behind a moving object",
                 font_size=15, color=WHITE),
            Text("• Group updaters — linked objects (line between dots)",
                 font_size=15, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.12), run_time=1.5)
        self.wait(4)

        # Course complete
        self.play(FadeOut(recap))
        done = VGroup(
            Text("Course Complete! 🎉", font_size=36, color=GREEN),
            Text("14 episodes. Every core Manim concept.", font_size=20, color=GREY),
        ).arrange(DOWN, buff=0.3)
        self.play(Write(done[0]), FadeIn(done[1]))
        self.wait(3)
