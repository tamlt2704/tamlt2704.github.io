"""
Emacs 101 (Manim) — Episode 10: "The Config That Rocks"
Build init.el from scratch. Each package transforms Emacs visually.

Render: manim -pqh ep10_the_config.py TheConfig
"""
from manim import *
from helpers import *


class TheConfig(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.bare_emacs()
        self.add_packages()
        self.the_final_form()
        self.cheat_sheet()

    def intro(self):
        t = Text("Episode 10: The Config That Rocks", font=FONT, font_size=28, color=TEAL)
        sub = Text("From bare Emacs to a modern IDE in 30 lines",
                    font=FONT, font_size=16, color=DIM)
        sub.next_to(t, DOWN, buff=0.3)
        self.play(Write(t), FadeIn(sub), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(t), FadeOut(sub))

    def bare_emacs(self):
        title = Text("Before: Stock Emacs", font=FONT, font_size=20, color=RED)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Ugly default Emacs
        frame = RoundedRectangle(width=9, height=5, corner_radius=0.1,
                                  fill_color="#f0f0f0", fill_opacity=1,
                                  stroke_color=DIM, stroke_width=1)
        frame.shift(DOWN * 0.3)

        # Menu bar (ugly)
        menu = Rectangle(width=9, height=0.3, fill_color="#e0e0e0",
                         fill_opacity=1, stroke_width=0)
        menu.move_to(frame.get_top() + DOWN * 0.15)
        menu_text = Text("File  Edit  Options  Buffers  Tools  Help",
                         font=FONT, font_size=9, color="#333")
        menu_text.move_to(menu.get_center())

        # Toolbar (ugly)
        toolbar = Rectangle(width=9, height=0.3, fill_color="#d0d0d0",
                            fill_opacity=1, stroke_width=0)
        toolbar.next_to(menu, DOWN, buff=0)
        toolbar_text = Text("📄 💾 ✂️ 📋 ↩️ 🔍", font_size=10)
        toolbar_text.move_to(toolbar.get_center())

        # Scrollbar
        scrollbar = Rectangle(width=0.2, height=4, fill_color="#ccc",
                              fill_opacity=1, stroke_width=0)
        scrollbar.move_to(frame.get_right() + LEFT * 0.1)

        # Splash screen text
        splash = Text("Welcome to GNU Emacs", font_size=14, color="#333")
        splash.move_to(frame.get_center())

        ugly = VGroup(frame, menu, menu_text, toolbar, toolbar_text, scrollbar, splash)
        self.play(FadeIn(ugly), run_time=0.5)

        problems = VGroup(
            Text("✗ Menu bar", font=FONT, font_size=11, color=RED),
            Text("✗ Toolbar", font=FONT, font_size=11, color=RED),
            Text("✗ Scrollbar", font=FONT, font_size=11, color=RED),
            Text("✗ Splash screen", font=FONT, font_size=11, color=RED),
            Text("✗ No line numbers", font=FONT, font_size=11, color=RED),
            Text("✗ No theme", font=FONT, font_size=11, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        problems.to_edge(RIGHT, buff=0.3)
        self.play(FadeIn(problems), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def add_packages(self):
        title = Text("Building init.el — One Package at a Time",
                      font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        packages = [
            ("(tool-bar-mode -1)", "Remove toolbar", RED),
            ("(menu-bar-mode -1)", "Remove menu bar", RED),
            ("(scroll-bar-mode -1)", "Remove scrollbar", RED),
            ("(setq inhibit-startup-message t)", "No splash screen", RED),
            ("(global-display-line-numbers-mode 1)", "Line numbers", GREEN),
            ("(load-theme 'doom-one t)", "Dark theme", TEAL),
            ("(doom-modeline-mode 1)", "Pretty modeline", TEAL),
            ("(vertico-mode)", "Fuzzy completion", CURSOR_COLOR),
            ("(which-key-mode)", "Key hints", YELLOW),
            ("(global-company-mode)", "Autocomplete", GREEN),
        ]

        items = VGroup()
        for code, desc, color in packages:
            code_t = Text(code, font=FONT, font_size=10, color=color)
            desc_t = Text(f"  ; {desc}", font=FONT, font_size=10, color=DIM)
            row = VGroup(code_t, desc_t).arrange(RIGHT, buff=0.1)
            items.add(row)
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        items.move_to(DOWN * 0.5)

        # Each line appears with a visual transformation
        for i, item in enumerate(items):
            self.play(FadeIn(item, shift=RIGHT * 0.3), run_time=0.15)

        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def the_final_form(self):
        title = Text("After: Modern Emacs", font=FONT, font_size=20, color=GREEN)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Beautiful dark Emacs
        frame = RoundedRectangle(width=10, height=5.5, corner_radius=0.1,
                                  fill_color=EMACS_BG, fill_opacity=1,
                                  stroke_color="#333", stroke_width=1)
        frame.shift(DOWN * 0.2)

        # Line numbers
        line_nums = VGroup()
        for i in range(12):
            n = Text(f"{i+1:3d}", font=FONT, font_size=9, color=DIM)
            n.move_to(frame.get_corner(UL) + RIGHT * 0.3 + DOWN * (0.3 + i * 0.25))
            line_nums.add(n)

        # Code with syntax highlighting
        code_lines = [
            ("def ", CURSOR_COLOR, "hello_world", TEAL, "():", WHITE),
            ('    """', GREEN, "Greet the world.", GREEN, '"""', GREEN),
            ("    name", WHITE, " = ", WHITE, '"Emacs"', YELLOW),
            ("    print", CURSOR_COLOR, "(", WHITE, "f'Hello {name}'", YELLOW),
            ("    ", WHITE, "return", CURSOR_COLOR, " True", TEAL),
        ]

        code_group = VGroup()
        for i, parts in enumerate(code_lines):
            line = VGroup()
            x_offset = 0
            for j in range(0, len(parts), 2):
                text = parts[j]
                color = parts[j + 1]
                t = Text(text, font=FONT, font_size=10, color=color)
                t.move_to(frame.get_corner(UL) + RIGHT * (0.7 + x_offset) +
                          DOWN * (0.3 + i * 0.25))
                x_offset += len(text) * 0.07
                line.add(t)
            code_group.add(line)

        # Modeline (doom style)
        modeline = Rectangle(width=10, height=0.3, fill_color="#21242b",
                             fill_opacity=1, stroke_width=0)
        modeline.move_to(frame.get_bottom() + UP * 0.45)
        mode_text = Text(" ● main  hello.py  Python  L3:C12  UTF-8 ",
                         font=FONT, font_size=9, color=WHITE)
        mode_text.move_to(modeline.get_center())

        # Which-key popup
        which_key = RoundedRectangle(width=4, height=1.2, corner_radius=0.06,
                                      fill_color="#252526", fill_opacity=0.95,
                                      stroke_color="#444", stroke_width=0.5)
        which_key.move_to(frame.get_bottom() + UP * 1.2)
        wk_text = VGroup(
            Text("C-x →  C-f: find file  C-s: save  b: buffer",
                 font=FONT, font_size=8, color=TEAL),
            Text("       C-c: quit       k: kill    2: split",
                 font=FONT, font_size=8, color=TEAL),
        ).arrange(DOWN, buff=0.04)
        wk_text.move_to(which_key.get_center())

        self.play(FadeIn(frame), run_time=0.3)
        self.play(FadeIn(line_nums), FadeIn(code_group), run_time=0.3)
        self.play(FadeIn(modeline), FadeIn(mode_text), run_time=0.2)
        self.play(FadeIn(which_key), FadeIn(wk_text), run_time=0.3)

        features = VGroup(
            Text("✓ Dark theme", font=FONT, font_size=11, color=GREEN),
            Text("✓ Line numbers", font=FONT, font_size=11, color=GREEN),
            Text("✓ Syntax highlighting", font=FONT, font_size=11, color=GREEN),
            Text("✓ Pretty modeline", font=FONT, font_size=11, color=GREEN),
            Text("✓ Which-key hints", font=FONT, font_size=11, color=GREEN),
            Text("✓ No clutter", font=FONT, font_size=11, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        features.to_edge(RIGHT, buff=0.2)
        self.play(FadeIn(features), run_time=0.3)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def cheat_sheet(self):
        title = Text("The Emacs Cheat Sheet", font=FONT, font_size=24, color=TEAL)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.3)

        cols = [
            [("C-g", "Cancel"), ("C-x C-f", "Open"), ("C-x C-s", "Save"),
             ("C-x C-c", "Quit"), ("C-x b", "Buffer")],
            [("C-s", "Search"), ("M-%", "Replace"), ("C-k", "Kill line"),
             ("C-y", "Yank"), ("M-y", "Cycle ring")],
            [("C-x 2", "Split H"), ("C-x 3", "Split V"), ("C-x 1", "One win"),
             ("C-x g", "Magit"), ("C-x (", "Macro")],
        ]

        all_items = VGroup()
        for col_idx, col in enumerate(cols):
            col_group = VGroup()
            for keys, desc in col:
                kc = key_cap(keys, width=max(len(keys) * 0.1 + 0.3, 0.7))
                label = Text(desc, font=FONT, font_size=10, color=WHITE)
                row = VGroup(kc, label).arrange(RIGHT, buff=0.1)
                col_group.add(row)
            col_group.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            col_group.move_to(LEFT * 3.5 + RIGHT * col_idx * 3.5 + DOWN * 0.5)
            all_items.add(col_group)

        self.play(FadeIn(all_items), run_time=0.5)
        self.wait(3)

        # Final message
        self.play(FadeOut(all_items), FadeOut(title))

        final = VGroup(
            Text("10 episodes.", font=FONT, font_size=28, color=WHITE),
            Text("You now know more Emacs", font=FONT, font_size=22, color=TEAL),
            Text("than most people who've used it for years.", font=FONT,
                 font_size=22, color=TEAL),
        ).arrange(DOWN, buff=0.2)
        self.play(Write(final[0]), run_time=0.5)
        self.play(FadeIn(final[1]), FadeIn(final[2]), run_time=0.5)
        self.wait(3)
