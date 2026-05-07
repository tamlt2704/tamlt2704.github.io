"""
Emacs 101 (Manim) — Episode 04: "Search & Replace"
Incremental search narrows as you type. Query replace with y/n.

Render: manim -pqh ep04_search_replace.py SearchReplace
"""
from manim import *
from helpers import *


class SearchReplace(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.incremental_search()
        self.query_replace()
        self.recap()

    def intro(self):
        t = Text("Episode 04: Search & Replace", font=FONT, font_size=28, color=TEAL)
        self.play(Write(t), run_time=0.6)
        self.wait(1)
        self.play(FadeOut(t))

    def incremental_search(self):
        title = Text("C-s → Incremental Search", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.3)

        frame = emacs_frame(title="main.py").scale(0.8)
        self.play(FadeIn(frame), run_time=0.3)

        lines_data = [
            "def hello_world():",
            '    print("hello")',
            "",
            "def hello_emacs():",
            '    print("hello emacs")',
            "",
            "def goodbye():",
            '    print("bye")',
        ]
        start = frame.editor.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.25
        lines = VGroup()
        for i, line in enumerate(lines_data):
            t = Text(line or " ", font=FONT, font_size=10, color=WHITE)
            t.move_to(start + DOWN * i * 0.24)
            t.align_to(start, LEFT)
            lines.add(t)
        self.play(FadeIn(lines), run_time=0.3)

        # Press C-s
        kc = key_combo("C-s")
        kc.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(kc), run_time=0.2)

        # Type "hel" incrementally — highlights narrow
        search_chars = ["h", "e", "l"]
        highlights = []

        # All positions containing "hello" (lines 0,1,3,4)
        match_lines = [0, 1, 3, 4]

        for ci, ch in enumerate(search_chars):
            query = "".join(search_chars[:ci + 1])
            mini_text = Text(f"I-search: {query}", font=FONT, font_size=10, color=WHITE)
            mini_text.move_to(frame.mini.get_center())

            # Clear old highlights
            for h in highlights:
                self.remove(h)
            highlights = []

            # Highlight matches
            for li in match_lines:
                hl = Rectangle(width=len(query) * 0.08, height=0.2,
                               fill_color=REGION_COLOR, fill_opacity=0.6, stroke_width=0)
                # Position at start of "hello" in each line
                hl.move_to(lines[li].get_left() + RIGHT * (0.35 + len(query) * 0.04))
                highlights.append(hl)
                self.add(hl)

            self.play(FadeIn(mini_text), run_time=0.15)
            self.wait(0.3)
            self.remove(mini_text)

        # C-s again jumps to next match
        jump_note = Text("C-s again → jump to next match", font=FONT, font_size=11, color=DIM)
        jump_note.next_to(frame, DOWN, buff=0.1)
        self.play(FadeIn(jump_note), run_time=0.2)
        self.wait(1.5)

        for h in highlights:
            self.remove(h)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def query_replace(self):
        title = Text("M-% → Query Replace", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.3)

        frame = emacs_frame(title="main.py").scale(0.8)
        self.play(FadeIn(frame), run_time=0.3)

        lines_data = ["hello world", "hello emacs", "hello there", "goodbye"]
        start = frame.editor.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.3
        lines = VGroup()
        for i, line in enumerate(lines_data):
            t = Text(line, font=FONT, font_size=12, color=WHITE)
            t.move_to(start + DOWN * i * 0.3)
            t.align_to(start, LEFT)
            lines.add(t)
        self.play(FadeIn(lines), run_time=0.3)

        # Show the prompt
        prompt = Text('Query replace: hello → hi  (y/n/!)', font=FONT,
                      font_size=10, color=WHITE)
        prompt.move_to(frame.mini.get_center())
        self.play(FadeIn(prompt), run_time=0.2)

        # Process each match
        replacements = [("hello world", "hi world", "y"),
                        ("hello emacs", "hello emacs", "n"),
                        ("hello there", "hi there", "y")]

        for i, (old, new, choice) in enumerate(replacements):
            # Highlight current match
            hl = Rectangle(width=0.6, height=0.22, fill_color=REGION_COLOR,
                           fill_opacity=0.6, stroke_width=0)
            hl.move_to(lines[i].get_left() + RIGHT * 0.3)
            self.play(FadeIn(hl), run_time=0.15)

            # Show y or n
            choice_key = key_cap(choice)
            choice_key.to_edge(DOWN, buff=0.3)
            color = GREEN if choice == "y" else RED
            choice_label = Text("replace" if choice == "y" else "skip",
                                font=FONT, font_size=10, color=color)
            choice_label.next_to(choice_key, RIGHT, buff=0.1)
            self.play(FadeIn(choice_key), FadeIn(choice_label), run_time=0.15)

            if choice == "y":
                new_text = Text(new, font=FONT, font_size=12, color=GREEN)
                new_text.move_to(lines[i].get_center())
                new_text.align_to(start, LEFT)
                self.play(Transform(lines[i], new_text), run_time=0.2)

            self.play(FadeOut(hl), FadeOut(choice_key), FadeOut(choice_label),
                      run_time=0.15)

        done = Text("Replaced 2 occurrences", font=FONT, font_size=11, color=GREEN)
        done.move_to(frame.mini.get_center())
        self.play(Transform(prompt, done), run_time=0.2)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("Episode 04 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• C-s → incremental search (narrows as you type)", font=FONT, font_size=14),
            Text("• C-r → search backward", font=FONT, font_size=14),
            Text("• C-s again → next match", font=FONT, font_size=14),
            Text("• M-% → query replace (y/n per match)", font=FONT, font_size=14),
            Text("• ! → replace all remaining", font=FONT, font_size=14),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
