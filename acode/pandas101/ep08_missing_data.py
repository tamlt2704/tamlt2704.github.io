"""
Episode 08: Missing Data
~5 min | Concepts: NaN, isna(), fillna(), dropna(), interpolate()

Render: manim -pqh ep08_missing_data.py MissingDataScene
"""
from manim import *
from helpers import *


class MissingDataScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_base_table()
        self.intro()
        self.show_nan()
        self.detect()
        self.fillna_section()
        self.dropna_section()
        self.outro()

    def build_base_table(self):
        """Build a table with missing values."""
        self.headers = ["Name", "Age", "City", "Salary"]
        self.rows = [
            ["Alice", "25", "NYC", "70000"],
            ["Bob", "NaN", "LA", "80000"],
            ["Charlie", "35", "NaN", "NaN"],
            ["Diana", "28", "NYC", "75000"],
            ["Eve", "NaN", "LA", "85000"],
        ]
        # Track which cells are NaN: (row, col) pairs
        self.nan_positions = [(1, 1), (2, 2), (2, 3), (4, 1)]

    def show_table(self, position=RIGHT * 1.5 + DOWN * 0.3, scale=0.75):
        table, h, d = make_table(self.headers, self.rows, col_width=1.5)
        table.scale(scale).move_to(position)
        self.table, self.h_cells, self.d_cells = table, h, d
        return table

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 8: Missing Data",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Show NaN cells (~50s) ────────────────────
    def show_nan(self):
        title = section_title("NaN — Not a Number")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)
        self.wait(0.5)

        # Highlight NaN cells in red
        nan_cells = [self.d_cells[r][c] for r, c in self.nan_positions]
        self.play(highlight_cells(nan_cells, color=RED), run_time=0.8)

        note = Text("NaN = missing or undefined value (like None in Python)",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        # Show how NaN propagates
        code = make_code_block('df["Age"].mean()  # NaN rows are skipped')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)

        calc = Text("(25 + 35 + 28) / 3 = 29.3  (NaN skipped)",
                    font=CODE_FONT, font_size=14, color=YELLOW)
        calc.to_edge(LEFT, buff=0.3).shift(DOWN * 0.5)
        self.play(FadeIn(calc), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Detect missing data (~50s) ───────────────
    def detect(self):
        title = section_title("isna() / notna()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df.isna()')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show boolean heatmap overlay — True for NaN, False otherwise
        for r in range(5):
            for c in range(4):
                is_nan = (r, c) in self.nan_positions
                color = RED if is_nan else GREEN
                indicator = Text("T" if is_nan else "F", font=CODE_FONT,
                                 font_size=10, color=color)
                indicator.move_to(self.d_cells[r][c][0].get_corner(UR) + LEFT * 0.1 + DOWN * 0.1)
                self.add(indicator)

        self.wait(1)

        # Show count
        count_code = make_code_block('df.isna().sum()\n# Age: 2, City: 1, Salary: 1')
        count_code.scale(0.6).to_edge(LEFT, buff=0.3).shift(DOWN * 1)
        self.play(FadeIn(count_code), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── fillna() (~60s) ──────────────────────────
    def fillna_section(self):
        title = section_title("fillna()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        # Highlight NaN cells
        nan_cells = [self.d_cells[r][c] for r, c in self.nan_positions]
        self.play(highlight_cells(nan_cells, color=RED), run_time=0.5)

        code = make_code_block('df["Age"].fillna(df["Age"].mean())')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Animate NaN cells being filled with values
        fill_values = {(1, 1): "29", (4, 1): "29"}  # mean of 25,35,28 ≈ 29
        for (r, c), val in fill_values.items():
            cell = self.d_cells[r][c]
            new_label = Text(val, font=CODE_FONT, font_size=15,
                             color=GREEN).move_to(cell[1].get_center())
            self.play(
                cell[0].animate.set_fill(GREEN, opacity=0.3),
                Transform(cell[1], new_label),
                run_time=0.5
            )

        self.wait(1)

        # Show other fill strategies
        strategies = VGroup(
            Text("• fillna(0) → fill with zero", font=CODE_FONT,
                 font_size=14, color=WHITE),
            Text('• fillna("Unknown") → fill with string', font=CODE_FONT,
                 font_size=14, color=WHITE),
            Text("• fillna(method='ffill') → forward fill", font=CODE_FONT,
                 font_size=14, color=WHITE),
            Text("• interpolate() → linear interpolation", font=CODE_FONT,
                 font_size=14, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        strategies.to_edge(LEFT, buff=0.3).shift(DOWN * 1.5)
        self.play(LaggedStart(*[FadeIn(s) for s in strategies],
                              lag_ratio=0.2), run_time=1)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── dropna() (~50s) ──────────────────────────
    def dropna_section(self):
        title = section_title("dropna()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df.dropna()  # drop rows with ANY NaN')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Rows with NaN: 1 (Age), 2 (City, Salary), 4 (Age)
        nan_rows = [1, 2, 4]
        nan_row_cells = [self.d_cells[r][c] for r in nan_rows for c in range(4)]

        # Highlight rows to be dropped
        self.play(highlight_cells(nan_row_cells, color=RED), run_time=0.5)
        self.wait(0.5)

        # Fade out those rows
        self.play(*[FadeOut(self.d_cells[r][c], shift=LEFT * 0.5)
                    for r in nan_rows for c in range(4)], run_time=1)

        # Show remaining rows
        kept_rows = [0, 3]
        kept_cells = [self.d_cells[r][c] for r in kept_rows for c in range(4)]
        self.play(highlight_cells(kept_cells, color=GREEN), run_time=0.3)

        note = Text("dropna(subset=['col']) → only check specific columns",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text("• NaN represents missing data",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• isna() / notna() → detect missing values",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• fillna(value) → replace NaN with a value",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• dropna() → remove rows/cols with NaN",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• interpolate() → estimate missing values",
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Merge & Join →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
