"""
Intro to Manim — 01: Basic Elements
Covers: Scene structure, Mobjects, self.add, self.play, self.wait, class animations.
Source: https://docs.devtaoism.com/docs/html/contents/_1_basic_elements.html

Render: manim -pql 01_basic_elements.py BasicElements
"""
from manim import *


class BasicElements(Scene):
    """Demonstrates every concept from the Basic Elements section."""

    def construct(self):
        # ── 1. Basic Structure ───────────────────
        # The simplest Manim script: create an object, animate it, wait.
        title = Text("01: Basic Elements", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait()
        self.play(FadeOut(title))

        # ── 2. Mobjects ──────────────────────────
        # The 3 main types: VMobject (vector), ImageMobject (raster), Group
        section = Text("Mobject Types", font_size=28, color=YELLOW)
        section.to_edge(UP)
        self.play(Write(section))

        # VMobjects — vector shapes (most common)
        circle = Circle(color=BLUE)
        square = Square(color=RED)
        line = Line(LEFT * 2, RIGHT * 2, color=GREEN)

        circle.shift(LEFT * 3)
        square.shift(RIGHT * 3)

        labels = VGroup(
            Text("Circle", font_size=16).next_to(circle, DOWN),
            Text("Square", font_size=16).next_to(square, DOWN),
            Text("Line", font_size=16).next_to(line, DOWN, buff=0.3),
        )

        self.play(Create(circle), Create(square), Create(line))
        self.play(FadeIn(labels))
        self.wait()
        self.play(*[FadeOut(m) for m in self.mobjects])

        # ── 3. Adding Mobjects (no animation) ────
        section2 = Text("self.add() — Instant, No Animation", font_size=24, color=YELLOW)
        section2.to_edge(UP)
        self.play(Write(section2))

        dot = Dot(color=RED).scale(3)
        # self.add() places it instantly — no animation, no duration
        self.add(dot)
        self.wait()

        note = Text("self.add() = instant\nself.play() = animated",
                     font_size=18, color=GREY).to_edge(DOWN)
        self.play(FadeIn(note))
        self.wait()
        self.play(*[FadeOut(m) for m in self.mobjects])

        # ── 4. Class Animations ──────────────────
        section3 = Text("Class Animations", font_size=28, color=YELLOW)
        section3.to_edge(UP)
        self.play(Write(section3))

        # Creation animations
        c = Circle(color=BLUE)
        self.play(Create(c))
        self.wait(0.5)

        # Indication animations
        self.play(Indicate(c))
        self.wait(0.5)

        self.play(FocusOn(c))
        self.wait(0.5)

        # Transformation (rotate)
        self.play(Rotate(c, PI / 2))
        self.wait(0.5)

        # Removal animations
        self.play(FadeOut(c))
        self.wait(0.5)
        self.play(FadeOut(section3))

        # ── 5. Animation Arguments ───────────────
        section4 = Text("Animation Arguments", font_size=28, color=YELLOW)
        section4.to_edge(UP)
        self.play(Write(section4))

        # run_time and rate_func
        c1 = Circle(color=BLUE).shift(LEFT * 3)
        s1 = Square(color=RED)
        t1 = Triangle(color=GREEN).shift(RIGHT * 3)

        self.play(
            Create(c1, run_time=3, rate_func=smooth),
            FadeIn(s1, run_time=2, rate_func=there_and_back),
            GrowFromCenter(t1),  # default run_time=1
        )
        self.wait()

        # ── 6. Multiple Animations ───────────────
        # Multiple objects in one self.play() = simultaneous
        self.play(
            c1.animate.shift(RIGHT * 2),
            s1.animate.shift(UP),
            t1.animate.shift(LEFT * 2),
            run_time=1.5,
        )
        self.wait()

        # ── 7. Sequential Animations ─────────────
        # Separate self.play() calls = sequential
        self.play(FadeOut(c1))
        self.play(FadeOut(s1))
        self.play(FadeOut(t1))
        self.play(FadeOut(section4))

        # ── Recap ────────────────────────────────
        recap = VGroup(
            Text("Recap:", font_size=28, color=BLUE),
            Text("• from manim import *", font_size=18),
            Text("• class MyScene(Scene): def construct(self):", font_size=18),
            Text("• self.add() = instant, self.play() = animated", font_size=18),
            Text("• Create, FadeIn, FadeOut, Indicate, Rotate", font_size=18),
            Text("• run_time, rate_func per animation", font_size=18),
            Text("• Multiple anims in one play() = simultaneous", font_size=18),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.play(FadeIn(recap))
        self.wait(3)
