"""
Episode 07: GroupBy
~5 min | Concepts: groupby(), .mean(), .agg(), .transform()

Render: manim -pqh ep07_groupby.py GroupByScene
"""
from manim import *
from helpers import *


class GroupByScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_base_table()
        self.intro()
        self.split_phase()
        self.apply_phase()
        self.combine_phase()
        self.transform_section()
        self.outro()

    def build_base_table(self):
        """Build the table used throughout the episode."""
        self.headers = ["Name", "Dept", "Salary"]
        self.rows = [
            ["Alice", "Eng", "90000"],
            ["Bob", "Sales", "70000"],
            ["Charlie", "Eng", "95000"],
            ["Diana", "HR", "65000"],
            ["Eve", "Sales", "72000"],
            ["Frank", "Eng", "88000"],
        ]

    def show_table(self, position=RIGHT * 1.5 + DOWN * 0.3, scale=0.75):
        table, h, d = make_table(self.headers, self.rows, col_width=1.8)
        table.scale(scale).move_to(position)
        self.table, self.h_cells, self.d_cells = table, h, d
        return table

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 7: GroupBy",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Split phase (~60s) ───────────────────────
    def split_phase(self):
        title = section_title("Split: groupby()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table(position=ORIGIN + UP * 0.5)
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df.groupby("Dept")')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 2.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Color-code rows by department
        # Eng: rows 0, 2, 5 (TEAL), Sales: rows 1, 4 (YELLOW), HR: row 3 (GREEN)
        dept_colors = {
            "Eng": TEAL, "Sales": YELLOW, "HR": GREEN
        }
        dept_rows = {"Eng": [0, 2, 5], "Sales": [1, 4], "HR": [3]}

        # Highlight each group with its color
        for dept, rows in dept_rows.items():
            cells = [self.d_cells[r][c] for r in rows for c in range(3)]
            self.play(highlight_cells(cells, color=dept_colors[dept]), run_time=0.4)

        self.wait(1)

        # Animate rows separating into groups
        eng_group = VGroup(*[VGroup(*[self.d_cells[r][c] for c in range(3)])
                             for r in [0, 2, 5]])
        sales_group = VGroup(*[VGroup(*[self.d_cells[r][c] for c in range(3)])
                               for r in [1, 4]])
        hr_group = VGroup(*[VGroup(*[self.d_cells[r][c] for c in range(3)])
                            for r in [3]])

        self.play(
            eng_group.animate.shift(LEFT * 1.5 + DOWN * 1),
            sales_group.animate.shift(RIGHT * 0 + DOWN * 1),
            hr_group.animate.shift(RIGHT * 1.5 + DOWN * 1),
            run_time=1.5
        )

        # Labels
        for dept, pos in [("Eng", LEFT * 1.5), ("Sales", ORIGIN),
                          ("HR", RIGHT * 1.5)]:
            label = Text(dept, font=CODE_FONT, font_size=14,
                         color=dept_colors[dept])
            label.move_to(pos + DOWN * 3)
            self.play(FadeIn(label), run_time=0.2)

        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Apply phase (~60s) ───────────────────────
    def apply_phase(self):
        title = section_title("Apply: .mean() / .agg()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block('df.groupby("Dept")["Salary"].mean()')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show groups with their values
        groups_data = [
            ("Eng", ["90000", "95000", "88000"], "91000"),
            ("Sales", ["70000", "72000"], "71000"),
            ("HR", ["65000"], "65000"),
        ]

        group_vgs = VGroup()
        for i, (dept, vals, mean) in enumerate(groups_data):
            dept_label = Text(dept, font=CODE_FONT, font_size=16, color=TEAL)
            vals_text = Text(" + ".join(vals), font=CODE_FONT,
                             font_size=12, color=WHITE)
            arrow = Text("→", font=CODE_FONT, font_size=16, color=DIM)
            result = Text(mean, font=CODE_FONT, font_size=16, color=GREEN)

            row = VGroup(dept_label, vals_text, arrow, result)
            row.arrange(RIGHT, buff=0.3)
            group_vgs.add(row)

        group_vgs.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        group_vgs.move_to(RIGHT * 1 + DOWN * 0.5)
        self.play(LaggedStart(*[FadeIn(g) for g in group_vgs],
                              lag_ratio=0.3), run_time=1.5)
        self.wait(2)

        # Show .agg() for multiple functions
        code2 = make_code_block('df.groupby("Dept")["Salary"].agg(\n    ["mean", "max", "count"]\n)')
        code2.scale(0.6).to_edge(LEFT, buff=0.3).shift(DOWN * 1.5)
        self.play(FadeIn(code2), run_time=0.3)

        note = Text(".agg() applies multiple functions at once",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Combine phase (~40s) ─────────────────────
    def combine_phase(self):
        title = section_title("Combine: Results Table")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show the result table
        result_headers = ["Dept", "mean_salary"]
        result_rows = [
            ["Eng", "91000"],
            ["HR", "65000"],
            ["Sales", "71000"],
        ]
        result_table, rh, rd = make_table(result_headers, result_rows, col_width=2)
        result_table.scale(0.8).move_to(RIGHT * 1 + DOWN * 0.3)

        code = make_code_block('result = df.groupby("Dept")["Salary"].mean()')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)

        # Animate result table appearing
        self.play(FadeIn(result_table, shift=UP * 0.5), run_time=1)

        note = Text("GroupBy = Split → Apply → Combine",
                    font=CODE_FONT, font_size=18, color=YELLOW)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── .transform() (~50s) ──────────────────────
    def transform_section(self):
        title = section_title(".transform()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df["dept_mean"] = df.groupby("Dept")\n                    ["Salary"].transform("mean")')
        code.scale(0.55).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show that transform returns same-size Series
        # Each row gets its group's mean
        means = ["91000", "71000", "91000", "65000", "71000", "91000"]
        mean_cells = VGroup()
        for i, val in enumerate(means):
            t = Text(val, font=CODE_FONT, font_size=12, color=GREEN)
            t.next_to(self.d_cells[i][-1], RIGHT, buff=0.4)
            mean_cells.add(t)

        col_label = Text("dept_mean", font=CODE_FONT, font_size=12, color=TEAL)
        col_label.next_to(mean_cells, UP, buff=0.2)

        self.play(FadeIn(col_label),
                  LaggedStart(*[FadeIn(t, shift=LEFT * 0.2)
                                for t in mean_cells], lag_ratio=0.1),
                  run_time=1)

        note = Text("transform() → same shape as input (broadcasts group result)",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• groupby("col") → split into groups',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• .mean(), .sum(), .count() → aggregate',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• .agg([...]) → multiple aggregations',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• .transform() → same-size result',
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Missing Data →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
