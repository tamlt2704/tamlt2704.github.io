"""
Episode 10: Apply & Lambda
~5 min | Concepts: .apply(), lambda, axis=0/1, vectorized operations

Render: manim -pqh ep10_apply.py ApplyScene
"""
from manim import *
from helpers import *


class ApplyScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_base_table()
        self.intro()
        self.simple_apply()
        self.lambda_section()
        self.row_apply()
        self.vectorized_comparison()
        self.outro()

    def build_base_table(self):
        """Build the table used throughout the episode."""
        self.headers = ["Name", "Age", "Salary"]
        self.rows = [
            ["Alice", "25", "70000"],
            ["Bob", "30", "80000"],
            ["Charlie", "35", "90000"],
            ["Diana", "28", "75000"],
            ["Eve", "32", "85000"],
        ]

    def show_table(self, position=RIGHT * 1.5 + DOWN * 0.3, scale=0.75):
        table, h, d = make_table(self.headers, self.rows, col_width=1.8)
        table.scale(scale).move_to(position)
        self.table, self.h_cells, self.d_cells = table, h, d
        return table

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 10: Apply & Lambda",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Simple apply (~60s) ──────────────────────
    def simple_apply(self):
        title = section_title(".apply(func)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('def double(x):\n    return x * 2\n\ndf["Salary"].apply(double)')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show function box processing each cell
        func_box = Rectangle(width=1.2, height=0.6, color=TEAL,
                             fill_opacity=0.2, stroke_width=2)
        func_label = Text("×2", font=CODE_FONT, font_size=16, color=TEAL)
        func_label.move_to(func_box.get_center())
        func_group = VGroup(func_box, func_label)
        func_group.move_to(self.d_cells[0][2].get_center() + RIGHT * 2)

        self.play(FadeIn(func_group), run_time=0.3)

        # Animate each salary cell passing through the function
        results = ["140000", "160000", "180000", "150000", "170000"]
        result_texts = VGroup()
        for i in range(5):
            # Highlight current cell
            self.play(highlight_cells([self.d_cells[i][2]], color=YELLOW),
                      run_time=0.2)

            # Show result
            result = Text(results[i], font=CODE_FONT, font_size=12, color=GREEN)
            result.next_to(func_group, RIGHT, buff=0.3).shift(
                DOWN * i * 0.35 - DOWN * 0.7)
            result_texts.add(result)
            self.play(FadeIn(result), run_time=0.2)

            # Unhighlight
            self.play(unhighlight_cells([self.d_cells[i][2]]), run_time=0.1)

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Lambda functions (~50s) ──────────────────
    def lambda_section(self):
        title = section_title("Lambda Functions")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df["Salary"].apply(lambda x: x * 1.1)')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show inline function explanation
        explanation = VGroup(
            Text("lambda x: x * 1.1", font=CODE_FONT, font_size=18, color=YELLOW),
            Text("↓", font=CODE_FONT, font_size=18, color=DIM),
            Text("Anonymous function: take x, return x × 1.1",
                 font=CODE_FONT, font_size=14, color=WHITE),
        ).arrange(DOWN, buff=0.2)
        explanation.to_edge(LEFT, buff=0.5).shift(DOWN * 1)
        self.play(FadeIn(explanation), run_time=0.5)

        # Highlight salary column and show results
        sal_cells = [self.d_cells[r][2] for r in range(5)]
        self.play(highlight_cells(sal_cells, color=TEAL), run_time=0.5)

        results = ["77000", "88000", "99000", "82500", "93500"]
        result_group = VGroup()
        for i, val in enumerate(results):
            t = Text(val, font=CODE_FONT, font_size=12, color=GREEN)
            t.next_to(self.d_cells[i][2], RIGHT, buff=0.4)
            result_group.add(t)
        self.play(LaggedStart(*[FadeIn(t) for t in result_group],
                              lag_ratio=0.1), run_time=0.5)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Row-wise apply (axis=1) (~60s) ───────────
    def row_apply(self):
        title = section_title("apply(axis=1) — Row-wise")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df["Summary"] = df.apply(\n    lambda row: f"{row.Name} (age {row.Age})",\n    axis=1\n)')
        code.scale(0.55).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show axis explanation
        axis_note = VGroup(
            Text("axis=0 → apply to each column (default)", font=CODE_FONT,
                 font_size=14, color=DIM),
            Text("axis=1 → apply to each row", font=CODE_FONT,
                 font_size=14, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        axis_note.to_edge(LEFT, buff=0.3).shift(DOWN * 1.5)
        self.play(FadeIn(axis_note), run_time=0.3)

        # Highlight rows one by one
        summaries = ["Alice (age 25)", "Bob (age 30)", "Charlie (age 35)",
                     "Diana (age 28)", "Eve (age 32)"]
        for i in range(5):
            row_cells = [self.d_cells[i][c] for c in range(3)]
            self.play(highlight_cells(row_cells, color=TEAL), run_time=0.2)

            result = Text(summaries[i], font=CODE_FONT, font_size=11, color=GREEN)
            result.next_to(self.d_cells[i][-1], RIGHT, buff=0.3)
            self.play(FadeIn(result), run_time=0.2)
            self.play(unhighlight_cells(row_cells), run_time=0.1)

        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Vectorized vs apply (~50s) ───────────────
    def vectorized_comparison(self):
        title = section_title("Vectorized vs .apply()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show two approaches side by side
        slow_code = make_code_block('# Slow: apply\ndf["Salary"].apply(lambda x: x * 2)')
        slow_code.scale(0.6).move_to(LEFT * 3 + UP * 0.5)

        fast_code = make_code_block('# Fast: vectorized\ndf["Salary"] * 2')
        fast_code.scale(0.6).move_to(RIGHT * 3 + UP * 0.5)

        self.play(FadeIn(slow_code), FadeIn(fast_code), run_time=0.5)

        # Speed comparison bars
        slow_bar = Rectangle(width=4, height=0.4, fill_color=RED,
                             fill_opacity=0.7, stroke_width=0)
        slow_bar.move_to(LEFT * 1 + DOWN * 1)
        slow_label = Text("apply(): ~100ms", font=CODE_FONT,
                          font_size=14, color=WHITE)
        slow_label.next_to(slow_bar, RIGHT, buff=0.2)

        fast_bar = Rectangle(width=0.8, height=0.4, fill_color=GREEN,
                             fill_opacity=0.7, stroke_width=0)
        fast_bar.move_to(LEFT * 2.6 + DOWN * 1.8)
        fast_label = Text("vectorized: ~2ms", font=CODE_FONT,
                          font_size=14, color=WHITE)
        fast_label.next_to(fast_bar, RIGHT, buff=0.2)

        self.play(GrowFromEdge(slow_bar, LEFT), FadeIn(slow_label), run_time=0.5)
        self.play(GrowFromEdge(fast_bar, LEFT), FadeIn(fast_label), run_time=0.5)

        note = Text("Use vectorized operations when possible — apply() for complex logic",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text("• .apply(func) → apply function to each element",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• lambda x: expr → inline anonymous function",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• axis=1 → apply row-wise instead of column-wise",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• Prefer vectorized ops (df * 2) over apply()",
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Pivot Tables →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
