"""
Emacs 101 (Manim) — Episode 01: "Don't Panic"
Open Emacs, move around, type, save, quit. Animated.

Render: manim -pqh ep01_dont_panic.py DontPanic
"""
from manim import *
from helpers import *


class DontPanic(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.open_emacs()
        self.the_cursor()
        self.basic_movement()
        self.type_something()
        self.save_and_quit()
        self.recap()

    # ── Intro (10s) ──────────────────────────────
    def intro(self):
        title = Text("Emacs 101", font=FONT, font_size=48, color=TEAL)
        sub = Text("Episode 01: Don't Panic", font=FONT, font_size=24, color=DIM)
        sub.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(sub), run_time=0.4)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(sub))

    # ── Open Emacs (20s) ─────────────────────────
    def open_emacs(self):
        # Terminal prompt
        prompt = Text("$ emacs", font=FONT, font_size=20, color=GREEN)
        prompt.move_to(ORIGIN)
        self.play(Write(prompt), run_time=0.5)
        self.wait(0.5)

        # Keys pressed
        keys = key_combo("RET")
        keys.next_to(prompt, RIGHT, buff=0.5)
        self.play(FadeIn(keys), run_time=0.2)
        self.wait(0.3)

        # Transition to Emacs frame
        self.play(FadeOut(prompt), FadeOut(keys), run_time=0.3)

        frame = emacs_frame(title="*scratch*")
        frame.scale(0.85)
        self.play(FadeIn(frame), run_time=0.5)

        # Scratch buffer content
        lines = [
            ";; This buffer is for text that is not saved.",
            ";; To create a file, visit it with C-x C-f.",
        ]
        text = editor_text(lines, frame.editor.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.3,
                           font_size=11)
        self.play(FadeIn(text), run_time=0.3)

        # Cursor blinking
        cur = cursor_block()
        cur.move_to(frame.editor.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.8)
        self.play(FadeIn(cur), run_time=0.2)

        # Blink
        for _ in range(3):
            self.play(cur.animate.set_opacity(0.2), run_time=0.3)
            self.play(cur.animate.set_opacity(0.8), run_time=0.3)

        note = Text("You're in Emacs. The cursor is the blue block.",
                     font=FONT, font_size=13, color=DIM)
        note.to_edge(DOWN, buff=0.2)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(1)

        self.frame = frame
        self.cur = cur
        self.play(FadeOut(text), FadeOut(note))

    # ── The Cursor (20s) ─────────────────────────
    def the_cursor(self):
        title = Text("The Cursor = Point", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.3)

        # Show cursor terminology
        terms = VGroup(
            Text("Point = where the cursor is", font=FONT, font_size=13, color=WHITE),
            Text("Mark  = a saved position (for selections)", font=FONT, font_size=13, color=WHITE),
            Text("Region = text between Point and Mark", font=FONT, font_size=13, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        terms.move_to(self.frame.editor.get_center())

        self.play(LaggedStart(*[FadeIn(t) for t in terms], lag_ratio=0.3), run_time=0.8)
        self.wait(2)
        self.play(FadeOut(terms), FadeOut(title))

    # ── Basic Movement (50s) ─────────────────────
    def basic_movement(self):
        title = Text("Movement: C-f  C-b  C-n  C-p", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.3)

        # Show text in editor
        lines = [
            "The quick brown fox",
            "jumps over the lazy",
            "dog. Emacs is great.",
        ]
        text = editor_text(lines, self.frame.editor.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.4,
                           font_size=13)
        self.play(FadeIn(text), run_time=0.3)

        # Position cursor at start of line 1
        cur = self.cur
        start = text[0].get_left() + RIGHT * 0.07
        cur.move_to(start)

        # C-f: forward character
        keys_display = VGroup()

        def show_key_and_move(key_text, direction, desc, times=1):
            kc = key_combo(key_text)
            kc.to_edge(DOWN, buff=0.5)
            label = Text(desc, font=FONT, font_size=12, color=DIM)
            label.next_to(kc, DOWN, buff=0.1)
            self.play(FadeIn(kc), FadeIn(label), run_time=0.15)
            for _ in range(times):
                self.play(cur.animate.shift(direction), run_time=0.15)
            self.wait(0.3)
            self.play(FadeOut(kc), FadeOut(label), run_time=0.15)

        # C-f → forward
        show_key_and_move("C-f", RIGHT * 0.14, "forward char", 5)

        # C-b → backward
        show_key_and_move("C-b", LEFT * 0.14, "backward char", 3)

        # C-n → next line
        show_key_and_move("C-n", DOWN * 0.28, "next line", 1)

        # C-p → previous line
        show_key_and_move("C-p", UP * 0.28, "previous line", 1)

        # C-a → beginning of line
        show_key_and_move("C-a", LEFT * 0.14, "beginning of line", 8)

        # C-e → end of line
        show_key_and_move("C-e", RIGHT * 0.14, "end of line", 12)

        # Show the pattern
        pattern = VGroup(
            Text("C- = by character/line", font=FONT, font_size=14, color=TEAL),
            Text("M- = by word/paragraph", font=FONT, font_size=14, color=YELLOW),
        ).arrange(DOWN, buff=0.1)
        pattern.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(pattern), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in [text, title, pattern]])

    # ── Type Something (30s) ─────────────────────
    def type_something(self):
        title = Text("Just Type — Emacs Inserts", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.3)

        # Empty editor, cursor at top-left
        cur = self.cur
        start = self.frame.editor.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.4
        cur.move_to(start + RIGHT * 0.07)

        # Type "Hello, Emacs!" character by character
        typed_text = "Hello, Emacs!"
        chars = VGroup()

        for i, ch in enumerate(typed_text):
            char = Text(ch, font=FONT, font_size=13, color=WHITE)
            char.move_to(start + RIGHT * i * 0.12)
            chars.add(char)

            # Show key press
            kc = key_cap(ch if ch != " " else "SPC")
            kc.to_edge(DOWN, buff=0.5)
            self.play(FadeIn(kc), run_time=0.02)
            self.play(FadeIn(char), cur.animate.shift(RIGHT * 0.12), run_time=0.04)
            self.play(FadeOut(kc), run_time=0.02)

        self.wait(1)

        # Backspace
        bk = key_combo("DEL")
        bk.to_edge(DOWN, buff=0.5)
        bk_label = Text("DEL = backspace", font=FONT, font_size=12, color=DIM)
        bk_label.next_to(bk, DOWN, buff=0.1)
        self.play(FadeIn(bk), FadeIn(bk_label), run_time=0.2)
        self.play(FadeOut(chars[-1]), cur.animate.shift(LEFT * 0.12), run_time=0.15)
        self.play(FadeOut(bk), FadeOut(bk_label), run_time=0.15)

        self.wait(1)
        self.play(FadeOut(chars), FadeOut(title))

    # ── Save and Quit (30s) ──────────────────────
    def save_and_quit(self):
        title = Text("Save & Quit", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.3)

        actions = [
            ("C-x C-s", "Save the file", GREEN),
            ("C-x C-f", "Open a file", TEAL),
            ("C-x C-c", "Quit Emacs", RED),
            ("C-g", "CANCEL anything", YELLOW),
        ]

        items = VGroup()
        for keys, desc, color in actions:
            kc = key_combo(keys)
            label = Text(f"  {desc}", font=FONT, font_size=14, color=color)
            row = VGroup(kc, label).arrange(RIGHT, buff=0.2)
            items.add(row)

        items.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        items.move_to(self.frame.editor.get_center())

        for item in items:
            self.play(FadeIn(item, shift=RIGHT * 0.3), run_time=0.3)
            self.wait(0.3)

        # Highlight C-g
        box = SurroundingRectangle(items[-1], color=YELLOW, buff=0.1)
        note = Text("C-g is your panic button. Mash it when stuck.",
                     font=FONT, font_size=13, color=YELLOW)
        note.to_edge(DOWN, buff=0.3)
        self.play(Create(box), FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("Episode 01 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• C-f/b/n/p → move by char/line", font=FONT, font_size=15, color=WHITE),
            Text("• C-a/e → beginning/end of line", font=FONT, font_size=15, color=WHITE),
            Text("• Just type → text appears", font=FONT, font_size=15, color=WHITE),
            Text("• C-x C-s → save", font=FONT, font_size=15, color=WHITE),
            Text("• C-x C-f → open file", font=FONT, font_size=15, color=WHITE),
            Text("• C-x C-c → quit", font=FONT, font_size=15, color=WHITE),
            Text("• C-g → CANCEL (panic button)", font=FONT, font_size=15, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.12), run_time=1.2)
        self.wait(3)
