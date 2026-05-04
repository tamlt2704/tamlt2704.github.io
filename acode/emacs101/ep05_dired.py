"""
Emacs 101 (Manim) — Episode 05: "Dired — The File Manager"
Directory listing as an editable buffer. Mark, delete, rename.

Render: manim -pqh ep05_dired.py DiredScene
"""
from manim import *
from helpers import *


class DiredScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.open_dired()
        self.navigate()
        self.mark_and_delete()
        self.wdired()
        self.recap()

    def intro(self):
        t = Text("Episode 05: Dired — The File Manager", font=FONT, font_size=26, color=TEAL)
        self.play(Write(t), run_time=0.6)
        self.wait(1)
        self.play(FadeOut(t))

    def open_dired(self):
        kc = key_combo("C-x d")
        desc = Text("Open directory listing", font=FONT, font_size=14, color=DIM)
        desc.next_to(kc, DOWN, buff=0.2)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.3)
        self.wait(0.5)
        self.play(FadeOut(kc), FadeOut(desc))

        # Dired buffer
        frame = emacs_frame(title="/home/user/project/").scale(0.85)
        self.play(FadeIn(frame), run_time=0.3)

        files = [
            ("d", "drwxr-xr-x", ".", TEAL),
            ("d", "drwxr-xr-x", "..", TEAL),
            ("d", "drwxr-xr-x", "src/", TEAL),
            (" ", "-rw-r--r--", "README.md", WHITE),
            (" ", "-rw-r--r--", "main.py", GREEN),
            (" ", "-rw-r--r--", "test.py", YELLOW),
            (" ", "-rw-r--r--", "old_backup.py", DIM),
            (" ", "-rw-r--r--", "temp.log", DIM),
        ]

        start = frame.editor.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.25
        file_texts = VGroup()
        for i, (flag, perms, name, color) in enumerate(files):
            line = f"  {flag} {perms}  {name}"
            t = Text(line, font=FONT, font_size=10, color=color)
            t.move_to(start + DOWN * i * 0.24)
            t.align_to(start, LEFT)
            file_texts.add(t)

        self.play(LaggedStart(*[FadeIn(f) for f in file_texts], lag_ratio=0.05),
                  run_time=0.5)
        self.wait(1)

        self.frame = frame
        self.file_texts = file_texts
        self.play(FadeOut(frame.modeline))  # keep editor visible

    def navigate(self):
        title = Text("Navigate: RET=open, ^=up", font=FONT, font_size=16, color=YELLOW)
        title.to_edge(UP, buff=0.2)
        self.play(FadeIn(title), run_time=0.2)

        # Cursor on main.py
        cur = cursor_block()
        cur.move_to(self.file_texts[4].get_left() + RIGHT * 0.1)
        self.play(FadeIn(cur), run_time=0.2)

        # RET opens file
        kc = key_cap("RET")
        kc.to_edge(DOWN, buff=0.5)
        desc = Text("Open main.py", font=FONT, font_size=11, color=GREEN)
        desc.next_to(kc, RIGHT, buff=0.2)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)
        self.wait(1)
        self.play(FadeOut(kc), FadeOut(desc), FadeOut(cur), FadeOut(title))

    def mark_and_delete(self):
        title = Text("Mark & Delete: d=mark, x=execute", font=FONT, font_size=16, color=YELLOW)
        title.to_edge(UP, buff=0.2)
        self.play(FadeIn(title), run_time=0.2)

        # Mark old_backup.py and temp.log for deletion
        for idx in [6, 7]:
            # Show "D" flag appearing
            d_flag = Text("D", font=FONT, font_size=10, color=RED)
            d_flag.move_to(self.file_texts[idx].get_left() + LEFT * 0.05)

            kc = key_cap("d")
            kc.to_edge(DOWN, buff=0.5)
            self.play(FadeIn(kc), run_time=0.1)
            self.play(FadeIn(d_flag),
                      self.file_texts[idx].animate.set_color(RED), run_time=0.2)
            self.play(FadeOut(kc), run_time=0.1)

        self.wait(0.5)

        # Execute with x
        kc_x = key_cap("x")
        kc_x.to_edge(DOWN, buff=0.5)
        desc = Text("Execute deletions", font=FONT, font_size=11, color=RED)
        desc.next_to(kc_x, RIGHT, buff=0.2)
        self.play(FadeIn(kc_x), FadeIn(desc), run_time=0.2)

        # Files disappear
        self.play(FadeOut(self.file_texts[6]), FadeOut(self.file_texts[7]),
                  run_time=0.3)

        done = Text("2 files deleted", font=FONT, font_size=11, color=RED)
        done.move_to(self.frame.mini.get_center())
        self.play(FadeIn(done), FadeOut(kc_x), FadeOut(desc), run_time=0.2)
        self.wait(1)
        self.play(FadeOut(done), FadeOut(title))

    def wdired(self):
        title = Text("Wdired: Edit Filenames Like Text!", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.2)
        self.play(FadeIn(title), run_time=0.2)

        kc = key_combo("C-x C-q")
        desc = Text("Enter wdired mode", font=FONT, font_size=11, color=DIM)
        kc.to_edge(DOWN, buff=0.5)
        desc.next_to(kc, DOWN, buff=0.1)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)

        # Highlight filenames as editable
        for i in [3, 4, 5]:
            self.play(self.file_texts[i].animate.set_color(TEAL), run_time=0.1)

        self.wait(0.5)

        # "Rename" main.py → app.py
        old = self.file_texts[4]
        new_text = Text("  -rw-r--r--  app.py", font=FONT, font_size=10, color=GREEN)
        new_text.move_to(old.get_center())
        new_text.align_to(old, LEFT)
        self.play(Transform(old, new_text), run_time=0.3)

        # Apply
        kc2 = key_combo("C-c C-c")
        kc2.to_edge(DOWN, buff=0.5)
        desc2 = Text("Apply renames", font=FONT, font_size=11, color=GREEN)
        desc2.next_to(kc2, DOWN, buff=0.1)
        self.play(FadeOut(kc), FadeOut(desc), FadeIn(kc2), FadeIn(desc2), run_time=0.2)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("Episode 05 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• C-x d → open dired", font=FONT, font_size=14),
            Text("• RET → open file, ^ → go up", font=FONT, font_size=14),
            Text("• d → mark for deletion, x → execute", font=FONT, font_size=14),
            Text("• R → rename, C → copy, + → new dir", font=FONT, font_size=14),
            Text("• C-x C-q → wdired (edit names as text!)", font=FONT, font_size=14, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
