"""
Emacs 101 (Manim) — Episode 08: "Multiple Cursors"
Edit 10 lines at once. Animated cursor multiplication.

Render: manim -pqh ep08_multiple_cursors.py MultipleCursors
"""
from manim import *
from helpers import *


class MultipleCursors(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.mark_next()
        self.mark_all()
        self.edit_lines()
        self.recap()

    def intro(self):
        t = Text("Episode 08: Multiple Cursors", font=FONT, font_size=28, color=TEAL)
        self.play(Write(t), run_time=0.6)
        self.wait(1)
        self.play(FadeOut(t))

    def mark_next(self):
        title = Text("C-> → Mark Next Like This", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        lines_data = [
            'const name = "oldName";',
            'console.log(name);',
            'return oldName;',
            'if (oldName === "test") {',
            '    update(oldName);',
            '}',
        ]
        start = LEFT * 4 + UP * 1
        lines = VGroup()
        for i, line in enumerate(lines_data):
            t = Text(line, font=FONT, font_size=12, color=WHITE)
            t.move_to(start + DOWN * i * 0.3)
            t.align_to(start, LEFT)
            lines.add(t)
        self.play(FadeIn(lines), run_time=0.3)

        # Highlight "oldName" occurrences one by one
        positions = [0, 2, 3, 4]  # lines containing "oldName"
        cursors = VGroup()

        kc = key_combo("C->")
        kc.to_edge(DOWN, buff=0.5)
        desc = Text("Mark next occurrence", font=FONT, font_size=11, color=DIM)
        desc.next_to(kc, DOWN, buff=0.1)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)

        for idx in positions:
            hl = Rectangle(width=0.85, height=0.2, fill_color=REGION_COLOR,
                           fill_opacity=0.6, stroke_width=0)
            # Approximate position of "oldName" in each line
            hl.move_to(lines[idx].get_center() + RIGHT * 0.5)
            cur = cursor_block()
            cur.move_to(hl.get_right())
            cursors.add(VGroup(hl, cur))
            self.play(FadeIn(hl), FadeIn(cur), run_time=0.2)
            self.wait(0.2)

        # Type replacement — all cursors type simultaneously
        self.play(FadeOut(kc), FadeOut(desc), run_time=0.15)

        type_note = Text('Type "newName" → all 4 change at once',
                         font=FONT, font_size=13, color=GREEN)
        type_note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(type_note), run_time=0.2)

        # Replace text
        new_lines_data = [
            'const name = "newName";',
            'console.log(name);',
            'return newName;',
            'if (newName === "test") {',
            '    update(newName);',
            '}',
        ]
        new_lines = VGroup()
        for i, line in enumerate(new_lines_data):
            t = Text(line, font=FONT, font_size=12, color=WHITE if i != 1 else WHITE)
            t.move_to(start + DOWN * i * 0.3)
            t.align_to(start, LEFT)
            new_lines.add(t)

        self.play(*[Transform(lines[i], new_lines[i]) for i in range(len(lines))],
                  *[FadeOut(c) for c in cursors], run_time=0.5)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def mark_all(self):
        title = Text("C-c C-< → Mark ALL Like This", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        note = Text("Select a word → C-c C-< → every occurrence gets a cursor",
                     font=FONT, font_size=13, color=TEAL)
        note.move_to(ORIGIN)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(FadeOut(note), FadeOut(title))

    def edit_lines(self):
        title = Text("C-S-c C-S-c → One Cursor Per Line", font=FONT, font_size=16, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Show 5 lines, each gets a cursor
        lines = VGroup()
        for i in range(5):
            t = Text(f"item_{i+1}", font=FONT, font_size=14, color=WHITE)
            t.move_to(LEFT * 2 + DOWN * (i * 0.35 - 0.7))
            lines.add(t)
        self.play(FadeIn(lines), run_time=0.3)

        # Region highlight
        region = Rectangle(width=1.5, height=1.8, fill_color=REGION_COLOR,
                           fill_opacity=0.3, stroke_width=0)
        region.move_to(lines.get_center())
        self.play(FadeIn(region), run_time=0.2)

        # Cursors appear on each line
        cursors = VGroup()
        for line in lines:
            cur = cursor_block()
            cur.move_to(line.get_right() + RIGHT * 0.1)
            cursors.add(cur)
        self.play(FadeIn(cursors), FadeOut(region), run_time=0.3)

        # Type " = True" on all lines
        new_lines = VGroup()
        for i in range(5):
            t = Text(f"item_{i+1} = True", font=FONT, font_size=14, color=GREEN)
            t.move_to(LEFT * 2 + DOWN * (i * 0.35 - 0.7))
            new_lines.add(t)

        self.play(*[Transform(lines[i], new_lines[i]) for i in range(5)],
                  *[c.animate.shift(RIGHT * 0.8) for c in cursors],
                  run_time=0.5)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("Episode 08 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• C-> → mark next occurrence", font=FONT, font_size=14),
            Text("• C-< → mark previous", font=FONT, font_size=14),
            Text("• C-c C-< → mark ALL occurrences", font=FONT, font_size=14),
            Text("• C-S-c C-S-c → one cursor per line", font=FONT, font_size=14),
            Text("• Type once → all cursors type simultaneously", font=FONT, font_size=14, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
