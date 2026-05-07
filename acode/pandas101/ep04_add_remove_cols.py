"""
Episode 04: Adding & Removing Columns
~5 min | Concepts: df["new"] = values, df.drop(), df.rename(), calculated columns

Render: manim -pqh ep04_add_remove_cols.py AddRemoveColsScene
"""
from manim import *
from helpers import *


class AddRemoveColsScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_base_table()
        self.intro()
        self.add_column()
        self.calculated_column()
        self.drop_column()
        self.rename_column()
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
        subtitle = Text("Episode 4: Adding & Removing Columns",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Add a new column (~60s) ──────────────────
    def add_column(self):
        title = section_title('df["new_col"] = values')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df["Dept"] = ["Eng", "Sales",\n             "Eng", "HR", "Sales"]')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # New column slides in from the right
        new_header = make_cell("Dept", width=1.5 * 0.75, height=0.5 * 0.75,
                               bg=HEADER_BG, text_color=TEAL, font_size=14)
        new_cells = []
        dept_vals = ["Eng", "Sales", "Eng", "HR", "Sales"]
        for i, val in enumerate(dept_vals):
            cell = make_cell(val, width=1.5 * 0.75, height=0.5 * 0.75, font_size=15)
            new_cells.append(cell)

        # Position new column to the right of existing table
        new_col = VGroup(new_header, *new_cells)
        new_col.arrange(DOWN, buff=0)
        new_col.next_to(self.table, RIGHT, buff=0)

        # Slide in from off-screen right
        new_col.shift(RIGHT * 3)
        self.play(new_col.animate.shift(LEFT * 3), run_time=1)

        note = Text("Assign a list/Series to create a new column",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Calculated column (~60s) ─────────────────
    def calculated_column(self):
        title = section_title("Calculated Columns")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df["Bonus"] = df["Salary"] * 0.1')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show formula arrow
        formula = Text("Salary × 0.1 = Bonus", font=CODE_FONT,
                       font_size=16, color=YELLOW)
        formula.to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(formula), run_time=0.3)

        # Highlight salary column
        salary_cells = [self.d_cells[r][3] for r in range(5)]
        self.play(highlight_cells(salary_cells, color=YELLOW), run_time=0.5)
        self.wait(0.5)

        # New bonus column appears with calculated values
        bonus_vals = ["7000", "8000", "9000", "7500", "8500"]
        bonus_header = make_cell("Bonus", width=1.5 * 0.75, height=0.5 * 0.75,
                                 bg=HEADER_BG, text_color=TEAL, font_size=14)
        bonus_cells = []
        for val in bonus_vals:
            cell = make_cell(val, width=1.5 * 0.75, height=0.5 * 0.75, font_size=15)
            bonus_cells.append(cell)

        bonus_col = VGroup(bonus_header, *bonus_cells)
        bonus_col.arrange(DOWN, buff=0)
        bonus_col.next_to(self.table, RIGHT, buff=0)

        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2)
                                for c in bonus_col], lag_ratio=0.1), run_time=1)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Drop column (~50s) ───────────────────────
    def drop_column(self):
        title = section_title("df.drop(columns=...)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df = df.drop(columns=["City"])')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight the City column (col index 2)
        city_cells = [self.h_cells[2]] + [self.d_cells[r][2] for r in range(5)]
        self.play(highlight_cells(city_cells, color=RED), run_time=0.5)
        self.wait(0.5)

        # Column fades out
        self.play(*[FadeOut(cell, shift=DOWN * 0.5) for cell in city_cells],
                  run_time=1)

        note = Text("drop() returns a new DataFrame by default (inplace=False)",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Rename column (~50s) ─────────────────────
    def rename_column(self):
        title = section_title("df.rename(columns=...)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df = df.rename(columns={\n    "Salary": "Annual_Pay"\n})')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight the Salary header
        self.play(highlight_cells([self.h_cells[3]], color=YELLOW), run_time=0.3)
        self.wait(0.5)

        # Morph header text from "Salary" to "Annual_Pay"
        old_label = self.h_cells[3][1]
        new_label = Text("Annual_Pay", font=CODE_FONT, font_size=14,
                         color=TEAL).move_to(old_label.get_center())
        self.play(Transform(old_label, new_label), run_time=1)

        note = Text("Pass a dict: {old_name: new_name}",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• df["col"] = values → add column',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df["col"] = df["x"] * n → calculated column',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df.drop(columns=[...]) → remove columns',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df.rename(columns={...}) → rename columns',
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Filtering Rows →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
