"""
Episode 05: Filtering Rows
~5 min | Concepts: df[condition], df[(A) & (B)], .isin(), .between()

Render: manim -pqh ep05_filtering.py FilteringScene
"""
from manim import *
from helpers import *


class FilteringScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_base_table()
        self.intro()
        self.single_condition()
        self.multiple_conditions()
        self.isin_filter()
        self.between_filter()
        self.outro()

    def build_base_table(self):
        """Build the table used throughout the episode."""
        self.headers = ["Name", "Age", "City", "Salary"]
        self.rows = [
            ["Alice", "25", "NYC", "70000"],
            ["Bob", "30", "LA", "80000"],
            ["Charlie", "35", "Chicago", "90000"],
            ["Diana", "28", "NYC", "75000"],
            ["Eve", "32", "LA", "85000"],
        ]

    def show_table(self, position=RIGHT * 1.5 + DOWN * 0.3, scale=0.75):
        table, h, d = make_table(self.headers, self.rows, col_width=1.5)
        table.scale(scale).move_to(position)
        self.table, self.h_cells, self.d_cells = table, h, d
        return table

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 5: Filtering Rows",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Single condition (~60s) ──────────────────
    def single_condition(self):
        title = section_title("df[condition]")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('mask = df["Salary"] > 75000\ndf[mask]')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show True/False mask column
        salaries = [70000, 80000, 90000, 75000, 85000]
        mask_texts = VGroup()
        for i, sal in enumerate(salaries):
            result = sal > 75000
            color = GREEN if result else RED
            t = Text(str(result), font=CODE_FONT, font_size=12, color=color)
            t.next_to(self.d_cells[i][-1], RIGHT, buff=0.3)
            mask_texts.add(t)

        mask_label = Text("mask:", font=CODE_FONT, font_size=12, color=DIM)
        mask_label.next_to(mask_texts, UP, buff=0.2)
        self.play(FadeIn(mask_label),
                  LaggedStart(*[FadeIn(t) for t in mask_texts], lag_ratio=0.1),
                  run_time=0.8)
        self.wait(1)

        # Highlight matching rows (Bob=80k, Charlie=90k, Eve=85k)
        true_rows = [1, 2, 4]
        true_cells = [self.d_cells[r][c] for r in true_rows for c in range(4)]
        self.play(highlight_cells(true_cells, color=GREEN), run_time=0.5)

        # Dim non-matching rows
        false_rows = [0, 3]
        false_cells = [self.d_cells[r][c] for r in false_rows for c in range(4)]
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in false_cells]
        self.play(*dim_anims, run_time=0.5)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Multiple conditions (~60s) ───────────────
    def multiple_conditions(self):
        title = section_title("Multiple Conditions: & and |")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df[(df["Age"] > 28) & (df["City"] == "LA")]')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show two masks side by side
        ages = [25, 30, 35, 28, 32]
        cities = ["NYC", "LA", "Chicago", "NYC", "LA"]
        mask1 = [a > 28 for a in ages]
        mask2 = [c == "LA" for c in cities]
        combined = [m1 and m2 for m1, m2 in zip(mask1, mask2)]

        # Highlight rows where both conditions are True (Bob=30/LA, Eve=32/LA)
        true_rows = [i for i, v in enumerate(combined) if v]
        true_cells = [self.d_cells[r][c] for r in true_rows for c in range(4)]
        self.play(highlight_cells(true_cells, color=GREEN), run_time=0.5)

        # Show the combined mask
        mask_group = VGroup()
        for i, val in enumerate(combined):
            color = GREEN if val else RED
            t = Text(str(val), font=CODE_FONT, font_size=12, color=color)
            t.next_to(self.d_cells[i][-1], RIGHT, buff=0.3)
            mask_group.add(t)
        self.play(LaggedStart(*[FadeIn(t) for t in mask_group], lag_ratio=0.1),
                  run_time=0.5)

        note = Text("Use & (and), | (or) — wrap each condition in parentheses!",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── .isin() filter (~50s) ────────────────────
    def isin_filter(self):
        title = section_title(".isin()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df[df["City"].isin(["NYC", "LA"])]')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight City column values that match
        cities = ["NYC", "LA", "Chicago", "NYC", "LA"]
        match_rows = [i for i, c in enumerate(cities) if c in ["NYC", "LA"]]

        # Highlight matching city cells first
        city_cells = [self.d_cells[r][2] for r in match_rows]
        self.play(highlight_cells(city_cells, color=TEAL), run_time=0.5)
        self.wait(0.5)

        # Then highlight full matching rows
        all_match = [self.d_cells[r][c] for r in match_rows for c in range(4)]
        self.play(highlight_cells(all_match, color=GREEN), run_time=0.5)

        # Dim Chicago row
        dim_cells = [self.d_cells[2][c] for c in range(4)]
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in dim_cells]
        self.play(*dim_anims, run_time=0.5)

        note = Text(".isin() is cleaner than chaining multiple == with |",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── .between() filter (~50s) ─────────────────
    def between_filter(self):
        title = section_title(".between()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df[df["Age"].between(28, 32)]')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight Age column, then matching rows
        ages = [25, 30, 35, 28, 32]
        match_rows = [i for i, a in enumerate(ages) if 28 <= a <= 32]

        # Show range indicator
        range_text = Text("28 ≤ Age ≤ 32 (inclusive)", font=CODE_FONT,
                          font_size=16, color=YELLOW)
        range_text.to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(range_text), run_time=0.3)

        # Highlight matching rows (Bob=30, Diana=28, Eve=32)
        match_cells = [self.d_cells[r][c] for r in match_rows for c in range(4)]
        self.play(highlight_cells(match_cells, color=GREEN), run_time=0.5)

        # Dim non-matching
        non_match = [0, 2]
        dim_cells = [self.d_cells[r][c] for r in non_match for c in range(4)]
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in dim_cells]
        self.play(*dim_anims, run_time=0.5)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• df[df["col"] > val] → single condition',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df[(A) & (B)] → combine with & (and), | (or)',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• .isin([...]) → match any value in a list',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• .between(lo, hi) → inclusive range filter',
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Sorting →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
