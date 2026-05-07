"""
Emacs 101 (Manim) — Episode 09: "Keyboard Macros — Automate Anything"
Record keystrokes, replay 100 times. Animated recording/playback.

Render: manim -pqh ep09_macros.py MacrosScene
"""
from manim import *
from helpers import *


class MacrosScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.record_macro()
        self.replay_macro()
        self.recap()

    def intro(self):
        t = Text("Episode 09: Keyboard Macros", font=FONT, font_size=28, color=TEAL)
        sub = Text("Record once. Replay forever.", font=FONT, font_size=18, color=DIM)
        sub.next_to(t, DOWN, buff=0.3)
        self.play(Write(t), FadeIn(sub), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(t), FadeOut(sub))

    def record_macro(self):
        title = Text("The Task: Convert Names to SQL", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Input data
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        start = LEFT * 4 + UP * 1
        input_lines = VGroup()
        for i, name in enumerate(names):
            t = Text(name, font=FONT, font_size=14, color=WHITE)
            t.move_to(start + DOWN * i * 0.35)
            t.align_to(start, LEFT)
            input_lines.add(t)
        self.play(FadeIn(input_lines), run_time=0.3)

        # Target
        target_label = Text("Goal:", font=FONT, font_size=12, color=DIM)
        target_label.move_to(RIGHT * 2 + UP * 1.5)
        target = Text("INSERT INTO users (name)\n  VALUES ('Alice');",
                       font=FONT, font_size=11, color=GREEN)
        target.next_to(target_label, DOWN, buff=0.1)
        self.play(FadeIn(target_label), FadeIn(target), run_time=0.3)
        self.wait(1)

        # Start recording
        rec_indicator = Text("● REC", font=FONT, font_size=12, color=RED)
        rec_indicator.to_corner(UR, buff=0.3)

        kc_start = key_combo("C-x (")
        kc_start.to_edge(DOWN, buff=0.5)
        desc = Text("Start recording macro", font=FONT, font_size=11, color=DIM)
        desc.next_to(kc_start, DOWN, buff=0.1)
        self.play(FadeIn(kc_start), FadeIn(desc), FadeIn(rec_indicator), run_time=0.2)
        self.wait(0.5)
        self.play(FadeOut(kc_start), FadeOut(desc), run_time=0.15)

        # Record steps on first line (Alice)
        steps = [
            ("C-a", "Go to beginning of line"),
            ("type prefix", "INSERT INTO users (name) VALUES ('"),
            ("C-e", "Go to end of line"),
            ("type suffix", "');"),
            ("C-n", "Move to next line"),
        ]

        # Animate the first line transforming
        result_line = Text("INSERT INTO users (name) VALUES ('Alice');",
                           font=FONT, font_size=11, color=GREEN)
        result_line.move_to(input_lines[0].get_center())
        result_line.align_to(start, LEFT)

        for key_text, description in steps:
            kc = key_cap(key_text, width=max(len(key_text) * 0.1 + 0.3, 0.5))
            kc.to_edge(DOWN, buff=0.5)
            step_desc = Text(description, font=FONT, font_size=10, color=DIM)
            step_desc.next_to(kc, DOWN, buff=0.1)
            self.play(FadeIn(kc), FadeIn(step_desc), run_time=0.1)
            self.wait(0.15)
            self.play(FadeOut(kc), FadeOut(step_desc), run_time=0.1)

        self.play(Transform(input_lines[0], result_line), run_time=0.3)

        # Stop recording
        kc_stop = key_combo("C-x )")
        kc_stop.to_edge(DOWN, buff=0.5)
        desc2 = Text("Stop recording", font=FONT, font_size=11, color=DIM)
        desc2.next_to(kc_stop, DOWN, buff=0.1)
        self.play(FadeIn(kc_stop), FadeIn(desc2), FadeOut(rec_indicator), run_time=0.2)
        self.wait(0.5)
        self.play(FadeOut(kc_stop), FadeOut(desc2))

        self.input_lines = input_lines
        self.start = start
        self.names = names
        self.play(FadeOut(target_label), FadeOut(target), FadeOut(title))

    def replay_macro(self):
        title = Text("C-u 4 C-x e → Replay 4 Times", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        kc = key_combo("C-u 4 C-x e")
        kc.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(kc), run_time=0.2)

        # Replay on remaining lines — each transforms
        for i in range(1, 5):
            result = Text(
                f"INSERT INTO users (name) VALUES ('{self.names[i]}');",
                font=FONT, font_size=11, color=GREEN)
            result.move_to(self.start + DOWN * i * 0.35)
            result.align_to(self.start, LEFT)
            self.play(Transform(self.input_lines[i], result), run_time=0.25)

        done = Text("4 lines transformed in 1 second ✓", font=FONT,
                     font_size=14, color=GREEN)
        done.next_to(self.input_lines, DOWN, buff=0.5)
        self.play(FadeIn(done), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("Episode 09 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• C-x ( → start recording", font=FONT, font_size=14),
            Text("• ... do stuff ...", font=FONT, font_size=14, color=DIM),
            Text("• C-x ) → stop recording", font=FONT, font_size=14),
            Text("• C-x e → replay once", font=FONT, font_size=14),
            Text("• C-u 100 C-x e → replay 100 times", font=FONT, font_size=14, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
