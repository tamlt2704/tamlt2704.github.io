"""
Emacs 101 (Manim) — Episode 03: "Buffers, Windows, and Frames"
The mental model that makes Emacs click. Animated split/switch/close.

Render: manim -pqh ep03_buffers_windows.py BuffersWindows
"""
from manim import *
from helpers import *


class BuffersWindows(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.the_mental_model()
        self.split_windows()
        self.switch_buffers()
        self.recap()

    def intro(self):
        title = Text("Emacs 101", font=FONT, font_size=40, color=TEAL)
        sub = Text("Episode 03: Buffers, Windows & Frames",
                    font=FONT, font_size=22, color=DIM)
        sub.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), FadeIn(sub), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(sub))

    # ── The Mental Model (40s) ───────────────────
    def the_mental_model(self):
        title = Text("Three Concepts", font=FONT, font_size=22, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.3)

        # Frame (OS window)
        frame_box = RoundedRectangle(width=9, height=5, corner_radius=0.15,
                                      fill_color="#111", fill_opacity=1,
                                      stroke_color=DIM, stroke_width=2)
        frame_label = Text("Frame (OS window)", font=FONT, font_size=12, color=DIM)
        frame_label.next_to(frame_box, UP, buff=0.1)

        # Window (visible pane)
        win1 = RoundedRectangle(width=4, height=3.5, corner_radius=0.08,
                                 fill_color=EMACS_BG, fill_opacity=1,
                                 stroke_color=TEAL, stroke_width=1.5)
        win1.move_to(frame_box.get_center() + LEFT * 2.2)
        win1_label = Text("Window", font=FONT, font_size=11, color=TEAL)
        win1_label.next_to(win1, UP, buff=0.05)

        win2 = RoundedRectangle(width=4, height=3.5, corner_radius=0.08,
                                 fill_color=EMACS_BG, fill_opacity=1,
                                 stroke_color=TEAL, stroke_width=1.5)
        win2.move_to(frame_box.get_center() + RIGHT * 2.2)
        win2_label = Text("Window", font=FONT, font_size=11, color=TEAL)
        win2_label.next_to(win2, UP, buff=0.05)

        # Buffers inside windows
        buf1 = Text("main.py", font=FONT, font_size=14, color=GREEN)
        buf1.move_to(win1.get_center())
        buf2 = Text("test.py", font=FONT, font_size=14, color=YELLOW)
        buf2.move_to(win2.get_center())

        self.play(FadeIn(frame_box), FadeIn(frame_label), run_time=0.3)
        self.play(FadeIn(win1), FadeIn(win1_label), FadeIn(buf1), run_time=0.3)
        self.play(FadeIn(win2), FadeIn(win2_label), FadeIn(buf2), run_time=0.3)

        # Explanation
        explain = VGroup(
            Text("Buffer = an open file (or anything)", font=FONT, font_size=13, color=WHITE),
            Text("Window = a visible pane showing a buffer", font=FONT, font_size=13, color=WHITE),
            Text("Frame  = an OS window with 1+ windows", font=FONT, font_size=13, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        explain.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(explain), run_time=0.3)

        # Hidden buffers
        hidden = VGroup(
            Text("Hidden buffers:", font=FONT, font_size=11, color=DIM),
            Text("*scratch*  *Messages*  utils.py  README.md",
                 font=FONT, font_size=10, color=DIM),
        ).arrange(DOWN, buff=0.05)
        hidden.move_to(frame_box.get_bottom() + UP * 0.5)
        self.play(FadeIn(hidden), run_time=0.3)

        note = Text("50 buffers open, only 2 visible. Buffers are cheap.",
                     font=FONT, font_size=12, color=TEAL)
        note.next_to(explain, DOWN, buff=0.1)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Split Windows (40s) ──────────────────────
    def split_windows(self):
        title = Text("Window Splitting", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.3)

        # Start with one window
        win = RoundedRectangle(width=8, height=4, corner_radius=0.08,
                                fill_color=EMACS_BG, fill_opacity=1,
                                stroke_color=TEAL, stroke_width=1.5)
        win.shift(DOWN * 0.3)
        buf = Text("main.py", font=FONT, font_size=16, color=GREEN)
        buf.move_to(win.get_center())
        self.play(FadeIn(win), FadeIn(buf), run_time=0.3)
        self.wait(0.5)

        # C-x 2: split horizontal
        kc = key_combo("C-x 2")
        kc.to_edge(DOWN, buff=0.5)
        desc = Text("Split horizontal", font=FONT, font_size=12, color=DIM)
        desc.next_to(kc, DOWN, buff=0.1)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)

        # Animate split
        win_top = RoundedRectangle(width=8, height=1.9, corner_radius=0.08,
                                    fill_color=EMACS_BG, fill_opacity=1,
                                    stroke_color=TEAL, stroke_width=1.5)
        win_top.move_to(UP * 0.7)
        win_bot = RoundedRectangle(width=8, height=1.9, corner_radius=0.08,
                                    fill_color=EMACS_BG, fill_opacity=1,
                                    stroke_color=TEAL, stroke_width=1.5)
        win_bot.move_to(DOWN * 1.3)

        buf_top = Text("main.py", font=FONT, font_size=14, color=GREEN)
        buf_top.move_to(win_top.get_center())
        buf_bot = Text("main.py", font=FONT, font_size=14, color=GREEN)
        buf_bot.move_to(win_bot.get_center())

        self.play(FadeOut(win), FadeOut(buf),
                  FadeIn(win_top), FadeIn(win_bot),
                  FadeIn(buf_top), FadeIn(buf_bot), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(kc), FadeOut(desc), run_time=0.15)

        # C-x 3: split vertical (on top window)
        kc2 = key_combo("C-x 3")
        kc2.to_edge(DOWN, buff=0.5)
        desc2 = Text("Split vertical", font=FONT, font_size=12, color=DIM)
        desc2.next_to(kc2, DOWN, buff=0.1)
        self.play(FadeIn(kc2), FadeIn(desc2), run_time=0.2)

        win_tl = RoundedRectangle(width=3.9, height=1.9, corner_radius=0.08,
                                   fill_color=EMACS_BG, fill_opacity=1,
                                   stroke_color=TEAL, stroke_width=1.5)
        win_tl.move_to(LEFT * 2.05 + UP * 0.7)
        win_tr = RoundedRectangle(width=3.9, height=1.9, corner_radius=0.08,
                                   fill_color=EMACS_BG, fill_opacity=1,
                                   stroke_color=TEAL, stroke_width=1.5)
        win_tr.move_to(RIGHT * 2.05 + UP * 0.7)

        buf_tl = Text("main.py", font=FONT, font_size=12, color=GREEN)
        buf_tl.move_to(win_tl.get_center())
        buf_tr = Text("main.py", font=FONT, font_size=12, color=GREEN)
        buf_tr.move_to(win_tr.get_center())

        self.play(FadeOut(win_top), FadeOut(buf_top),
                  FadeIn(win_tl), FadeIn(win_tr),
                  FadeIn(buf_tl), FadeIn(buf_tr), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(kc2), FadeOut(desc2), run_time=0.15)

        # C-x 1: close all other windows
        kc3 = key_combo("C-x 1")
        kc3.to_edge(DOWN, buff=0.5)
        desc3 = Text("One window (close others)", font=FONT, font_size=12, color=DIM)
        desc3.next_to(kc3, DOWN, buff=0.1)
        self.play(FadeIn(kc3), FadeIn(desc3), run_time=0.2)

        single = RoundedRectangle(width=8, height=4, corner_radius=0.08,
                                   fill_color=EMACS_BG, fill_opacity=1,
                                   stroke_color=TEAL, stroke_width=1.5)
        single.shift(DOWN * 0.3)
        single_buf = Text("main.py", font=FONT, font_size=16, color=GREEN)
        single_buf.move_to(single.get_center())

        self.play(*[FadeOut(m) for m in [win_tl, win_tr, win_bot,
                    buf_tl, buf_tr, buf_bot]],
                  FadeIn(single), FadeIn(single_buf), run_time=0.5)
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Switch Buffers (30s) ─────────────────────
    def switch_buffers(self):
        title = Text("Switching Buffers", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.3)

        # Window showing main.py
        win = RoundedRectangle(width=8, height=3.5, corner_radius=0.08,
                                fill_color=EMACS_BG, fill_opacity=1,
                                stroke_color=TEAL, stroke_width=1.5)
        win.shift(DOWN * 0.2)
        buf_name = Text("main.py", font=FONT, font_size=18, color=GREEN)
        buf_name.move_to(win.get_center())
        self.play(FadeIn(win), FadeIn(buf_name), run_time=0.3)

        # C-x b
        kc = key_combo("C-x b")
        kc.to_edge(DOWN, buff=0.5)
        desc = Text("Switch buffer (type name, Tab completes)", font=FONT,
                     font_size=12, color=DIM)
        desc.next_to(kc, DOWN, buff=0.1)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)

        # Minibuffer prompt
        mini_prompt = Text("Switch to buffer: test.py", font=FONT,
                           font_size=12, color=WHITE)
        mini_prompt.move_to(win.get_bottom() + DOWN * 0.5)
        self.play(FadeIn(mini_prompt), run_time=0.3)
        self.wait(0.5)

        # Buffer switches
        new_buf = Text("test.py", font=FONT, font_size=18, color=YELLOW)
        new_buf.move_to(win.get_center())
        self.play(FadeOut(buf_name), FadeIn(new_buf),
                  FadeOut(mini_prompt), run_time=0.3)
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("Episode 03 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• Buffer = open file (many can exist)", font=FONT, font_size=15),
            Text("• Window = visible pane (shows one buffer)", font=FONT, font_size=15),
            Text("• C-x 2 / C-x 3 → split h / v", font=FONT, font_size=15),
            Text("• C-x 1 → close other windows", font=FONT, font_size=15),
            Text("• C-x o → switch to other window", font=FONT, font_size=15),
            Text("• C-x b → switch buffer by name", font=FONT, font_size=15),
            Text("• C-x k → kill (close) buffer", font=FONT, font_size=15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.12), run_time=1.2)
        self.wait(3)
