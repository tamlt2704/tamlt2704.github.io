"""
Emacs 101 (Manim) — Episode 07: "Org Mode — The Killer Feature"
Headings fold, TODOs cycle, tables auto-align. Animated.

Render: manim -pqh ep07_org_mode.py OrgMode
"""
from manim import *
from helpers import *


class OrgMode(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.headings_and_folding()
        self.todo_cycling()
        self.tables()
        self.export()
        self.recap()

    def intro(self):
        t = Text("Episode 07: Org Mode", font=FONT, font_size=32, color=TEAL)
        sub = Text("Notes. TODOs. Tables. Publishing. All in plain text.",
                    font=FONT, font_size=16, color=DIM)
        sub.next_to(t, DOWN, buff=0.3)
        self.play(Write(t), FadeIn(sub), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(t), FadeOut(sub))

    def headings_and_folding(self):
        title = Text("Headings & Folding (Tab)", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Expanded view
        expanded = VGroup(
            Text("* Project Plan", font=FONT, font_size=14, color=TEAL),
            Text("** TODO Design the API", font=FONT, font_size=13, color=YELLOW),
            Text("   - REST endpoints", font=FONT, font_size=11, color=WHITE),
            Text("   - Authentication", font=FONT, font_size=11, color=WHITE),
            Text("** DONE Set up database", font=FONT, font_size=13, color=GREEN),
            Text("   CLOSED: [2026-05-03]", font=FONT, font_size=10, color=DIM),
            Text("** TODO Write tests", font=FONT, font_size=13, color=YELLOW),
            Text("   DEADLINE: <2026-05-10>", font=FONT, font_size=10, color=RED),
            Text("* Meeting Notes", font=FONT, font_size=14, color=TEAL),
            Text("  Discussed timeline with Karen.", font=FONT, font_size=11, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        expanded.move_to(LEFT * 1.5 + DOWN * 0.3)

        self.play(LaggedStart(*[FadeIn(l) for l in expanded], lag_ratio=0.05),
                  run_time=0.8)
        self.wait(1)

        # Press Tab → fold
        kc = key_cap("Tab")
        kc.to_edge(DOWN, buff=0.5)
        desc = Text("Fold/unfold heading", font=FONT, font_size=11, color=DIM)
        desc.next_to(kc, RIGHT, buff=0.2)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)

        # Fold: hide children of "Project Plan"
        folded = VGroup(
            Text("* Project Plan...", font=FONT, font_size=14, color=TEAL),
            Text("* Meeting Notes...", font=FONT, font_size=14, color=TEAL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        folded.move_to(LEFT * 1.5 + DOWN * 0.3)

        self.play(FadeOut(expanded), FadeIn(folded), run_time=0.5)

        note = Text("Tab cycles: folded → children → all expanded",
                     font=FONT, font_size=12, color=DIM)
        note.to_edge(DOWN, buff=0.2)
        self.play(FadeIn(note), run_time=0.2)
        self.wait(1.5)

        # Unfold
        self.play(FadeOut(folded), FadeIn(expanded), run_time=0.5)
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def todo_cycling(self):
        title = Text("C-c C-t → Cycle TODO State", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Show a heading cycling through states
        states = [
            ("** TODO Design the API", YELLOW),
            ("** DOING Design the API", CURSOR_COLOR),
            ("** DONE Design the API", GREEN),
            ("** Design the API", WHITE),  # back to no state
        ]

        heading = Text(states[0][0], font=FONT, font_size=16, color=states[0][1])
        heading.move_to(ORIGIN)
        self.play(FadeIn(heading), run_time=0.2)

        kc = key_combo("C-c C-t")
        kc.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(kc), run_time=0.2)

        for text, color in states[1:]:
            new = Text(text, font=FONT, font_size=16, color=color)
            new.move_to(ORIGIN)
            self.play(Transform(heading, new), run_time=0.4)
            self.wait(0.5)

        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def tables(self):
        title = Text("Tables — Auto-Align with Tab", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Show a table being built
        table_lines = [
            "| Item   | Price | Qty |",
            "|--------+-------+-----|",
            "| Apples |  1.50 |   4 |",
            "| Bread  |  3.00 |   1 |",
            "| Milk   |  2.50 |   2 |",
        ]

        table = VGroup()
        for i, line in enumerate(table_lines):
            color = DIM if i == 1 else WHITE
            t = Text(line, font=FONT, font_size=13, color=color)
            table.add(t)
        table.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        table.move_to(DOWN * 0.3)

        for line in table:
            self.play(FadeIn(line), run_time=0.15)

        note = Text("Tab in a table → jump to next cell + auto-align columns",
                     font=FONT, font_size=12, color=TEAL)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def export(self):
        title = Text("C-c C-e → Export", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title), run_time=0.2)

        # Org file → multiple formats
        org = RoundedRectangle(width=2, height=1.2, corner_radius=0.08,
                                fill_color=EMACS_BG, fill_opacity=1,
                                stroke_color=TEAL, stroke_width=1.5)
        org.move_to(LEFT * 3)
        org_label = Text(".org", font=FONT, font_size=14, color=TEAL)
        org_label.move_to(org.get_center())
        self.play(FadeIn(org), FadeIn(org_label), run_time=0.3)

        formats = [("HTML", GREEN), ("PDF", RED), ("LaTeX", YELLOW),
                   ("Markdown", CURSOR_COLOR), ("Slides", DIM)]

        for i, (fmt, color) in enumerate(formats):
            target = RoundedRectangle(width=1.5, height=0.5, corner_radius=0.06,
                                      fill_color=EMACS_BG, fill_opacity=1,
                                      stroke_color=color, stroke_width=1)
            target.move_to(RIGHT * 2 + UP * (1.2 - i * 0.6))
            label = Text(fmt, font=FONT, font_size=11, color=color)
            label.move_to(target.get_center())

            arrow = Arrow(org.get_right(), target.get_left(), color=color,
                          buff=0.1, stroke_width=1.5)
            self.play(GrowArrow(arrow), FadeIn(target), FadeIn(label), run_time=0.2)

        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("Episode 07 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• * heading, ** subheading", font=FONT, font_size=14),
            Text("• Tab → fold/unfold", font=FONT, font_size=14),
            Text("• C-c C-t → cycle TODO/DONE", font=FONT, font_size=14),
            Text("• C-c C-d → set deadline", font=FONT, font_size=14),
            Text("• | for tables, Tab to align", font=FONT, font_size=14),
            Text("• C-c C-e → export to HTML/PDF/LaTeX", font=FONT, font_size=14),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(recap))
        self.wait(3)
