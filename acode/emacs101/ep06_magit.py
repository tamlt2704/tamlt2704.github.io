"""
Emacs 101 (Manim) — Episode 06: "Magit — Git That Doesn't Suck"
Stage hunks, commit, push — all animated.

Render: manim -pqh ep06_magit.py MagitScene
"""
from manim import *
from helpers import *


class MagitScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.magit_status()
        self.stage_and_commit()
        self.the_diff()
        self.recap()

    def intro(self):
        t = Text("Episode 06: Magit", font=FONT, font_size=32, color=TEAL)
        sub = Text("The best Git interface. Period.", font=FONT, font_size=18, color=DIM)
        sub.next_to(t, DOWN, buff=0.3)
        self.play(Write(t), FadeIn(sub), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(t), FadeOut(sub))

    def magit_status(self):
        kc = key_combo("C-x g")
        desc = Text("Open magit status", font=FONT, font_size=14, color=DIM)
        desc.next_to(kc, DOWN, buff=0.2)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.3)
        self.wait(0.5)
        self.play(FadeOut(kc), FadeOut(desc))

        frame = emacs_frame(title="magit: project").scale(0.85)
        self.play(FadeIn(frame), run_time=0.3)

        # Magit status sections
        sections = [
            ("Head:", "main  Add user authentication", DIM, WHITE),
            ("", "", DIM, DIM),
            ("Unstaged changes (2)", "", YELLOW, YELLOW),
            ("  modified", "  src/main.py", RED, WHITE),
            ("  modified", "  src/utils.py", RED, WHITE),
            ("", "", DIM, DIM),
            ("Staged changes (1)", "", GREEN, GREEN),
            ("  modified", "  README.md", GREEN, WHITE),
            ("", "", DIM, DIM),
            ("Recent commits", "", DIM, DIM),
            ("  abc1234", "  Fix login bug", DIM, DIM),
            ("  def5678", "  Add tests", DIM, DIM),
        ]

        start = frame.editor.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.2
        status_lines = VGroup()
        for i, (prefix, suffix, pc, sc) in enumerate(sections):
            line = VGroup()
            if prefix:
                p = Text(prefix, font=FONT, font_size=10, color=pc)
                p.move_to(start + DOWN * i * 0.2)
                p.align_to(start, LEFT)
                line.add(p)
            if suffix:
                s = Text(suffix, font=FONT, font_size=10, color=sc)
                s.move_to(start + DOWN * i * 0.2 + RIGHT * 1.5)
                s.align_to(start + RIGHT * 1.5, LEFT)
                line.add(s)
            status_lines.add(line)

        self.play(LaggedStart(*[FadeIn(l) for l in status_lines if l.submobjects],
                  lag_ratio=0.04), run_time=0.8)
        self.wait(1)

        self.frame = frame
        self.status_lines = status_lines

    def stage_and_commit(self):
        title = Text("Stage & Commit", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.2)
        self.play(FadeIn(title), run_time=0.2)

        # Stage: press s on unstaged file
        actions = [
            ("s", "Stage file (or hunk)", GREEN),
            ("u", "Unstage", YELLOW),
            ("c c", "Commit → type message → C-c C-c", TEAL),
            ("P p", "Push to remote", CURSOR_COLOR),
            ("F p", "Pull from remote", CURSOR_COLOR),
        ]

        items = VGroup()
        for keys, desc, color in actions:
            kc = key_cap(keys, width=0.8)
            label = Text(f"  {desc}", font=FONT, font_size=12, color=color)
            row = VGroup(kc, label).arrange(RIGHT, buff=0.1)
            items.add(row)
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        items.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.5)

        for item in items:
            self.play(FadeIn(item, shift=LEFT * 0.2), run_time=0.2)
            self.wait(0.2)

        # Animate: s on main.py → moves from unstaged to staged
        note = Text("Press s on a file → it moves from Unstaged to Staged",
                     font=FONT, font_size=11, color=GREEN)
        note.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note), run_time=0.2)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def the_diff(self):
        title = Text("Tab → Expand Diff (Stage Individual Hunks!)",
                      font=FONT, font_size=16, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.3)

        # Show a diff
        diff_lines = [
            ("  modified  src/main.py", WHITE),
            ("", DIM),
            ("@@ -10,6 +10,8 @@", TEAL),
            ("  def login(user, password):", WHITE),
            ("-     return check(user)", RED),
            ("+     if not user:", GREEN),
            ("+         raise ValueError", GREEN),
            ("+     return check(user, password)", GREEN),
            ("  ", WHITE),
        ]

        diff_group = VGroup()
        for i, (text, color) in enumerate(diff_lines):
            t = Text(text or " ", font=FONT, font_size=11, color=color)
            diff_group.add(t)
        diff_group.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        diff_group.move_to(DOWN * 0.3)

        self.play(FadeIn(diff_group), run_time=0.5)

        # Highlight a hunk
        hunk_box = SurroundingRectangle(
            VGroup(diff_group[4], diff_group[5], diff_group[6], diff_group[7]),
            color=YELLOW, buff=0.05, stroke_width=1)
        hunk_label = Text("← This is a hunk. Press s to stage just this part.",
                          font=FONT, font_size=11, color=YELLOW)
        hunk_label.next_to(hunk_box, RIGHT, buff=0.2)
        self.play(Create(hunk_box), FadeIn(hunk_label), run_time=0.3)

        note = Text("Surgical commits: stage exactly the lines you want",
                     font=FONT, font_size=12, color=TEAL)
        note.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("Episode 06 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• C-x g → magit status", font=FONT, font_size=14),
            Text("• s → stage, u → unstage", font=FONT, font_size=14),
            Text("• Tab → expand diff, stage individual hunks", font=FONT, font_size=14),
            Text("• c c → commit, P p → push, F p → pull", font=FONT, font_size=14),
            Text("• b b → switch branch, l l → log", font=FONT, font_size=14),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
