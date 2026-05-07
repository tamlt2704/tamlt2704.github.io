"""
Episode 03: Selecting Data
~5 min | Concepts: column selection, loc, iloc, boolean indexing

Render: manim -pqh ep03_selecting.py SelectingScene
"""
from manim import *
from helpers import *


class SelectingScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_base_table()
        self.intro()
        self.select_column()
        self.select_multiple_columns()
        self.loc_section()
        self.iloc_section()
        self.boolean_indexing()
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

    def show_table(self, position=ORIGIN, scale=0.75):
        table, h, d = make_table(self.headers, self.rows, col_width=1.5)
        table.scale(scale).move_to(position)
        self.table, self.h_cells, self.d_cells = table, h, d
        return table

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 3: Selecting Data",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Select single column (~50s) ──────────────
    def select_column(self):
        title = section_title('df["column"]')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table(RIGHT * 1.5 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df["Name"]')
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight the Name column (header + all data cells in col 0)
        col_cells = [self.h_cells[0]] + [self.d_cells[r][0] for r in range(5)]
        self.play(highlight_cells(col_cells, color=TEAL), run_time=0.5)

        # Show result as a Series
        result_label = Text("→ Returns a Series:", font=CODE_FONT,
                            font_size=14, color=DIM)
        result_label.to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(result_label), run_time=0.3)

        result_vals = VGroup()
        for i, name in enumerate(["Alice", "Bob", "Charlie", "Diana", "Eve"]):
            t = Text(name, font=CODE_FONT, font_size=16, color=WHITE)
            t.move_to(LEFT * 4 + DOWN * (1 + i * 0.35))
            result_vals.add(t)
        self.play(LaggedStart(*[FadeIn(t) for t in result_vals],
                              lag_ratio=0.1), run_time=0.5)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Select multiple columns (~40s) ───────────
    def select_multiple_columns(self):
        title = section_title('df[["col1", "col2"]]')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table(RIGHT * 1.5 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df[["Name", "Salary"]]')
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight Name (col 0) and Salary (col 3)
        selected = ([self.h_cells[0], self.h_cells[3]] +
                    [self.d_cells[r][0] for r in range(5)] +
                    [self.d_cells[r][3] for r in range(5)])
        self.play(highlight_cells(selected, color=TEAL), run_time=0.5)

        # Dim unselected columns
        unselected = ([self.h_cells[1], self.h_cells[2]] +
                      [self.d_cells[r][1] for r in range(5)] +
                      [self.d_cells[r][2] for r in range(5)])
        dim_anims = [cell[0].animate.set_opacity(0.2) for cell in unselected]
        self.play(*dim_anims, run_time=0.5)

        note = Text("Double brackets → returns a DataFrame (subset of columns)",
                     font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── loc (label-based) (~60s) ─────────────────
    def loc_section(self):
        title = section_title("df.loc[row, col]  (label-based)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table(RIGHT * 1 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        # Example 1: single cell
        code1 = make_code_block('df.loc[1, "City"]  # → "LA"')
        code1.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code1), run_time=0.3)
        self.wait(0.5)

        # Highlight row 1, col "City" (index 2)
        target = self.d_cells[1][2]
        self.play(highlight_cells([target], color=GREEN), run_time=0.5)
        self.wait(1.5)
        self.play(unhighlight_cells([target]), FadeOut(code1), run_time=0.3)

        # Example 2: row slice
        code2 = make_code_block('df.loc[1:3, "Name":"City"]')
        code2.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code2), run_time=0.3)
        self.wait(0.5)

        # Highlight rows 1-3, cols Name-City (0-2) — loc is INCLUSIVE
        slice_cells = [self.d_cells[r][c] for r in range(1, 4) for c in range(3)]
        self.play(highlight_cells(slice_cells, color=BLUE), run_time=0.5)

        note = Text("loc uses labels — slices are INCLUSIVE on both ends",
                     font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── iloc (integer-based) (~50s) ──────────────
    def iloc_section(self):
        title = section_title("df.iloc[row, col]  (integer-based)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table(RIGHT * 1 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        # Example: iloc[0:2, 0:3] — EXCLUSIVE end
        code = make_code_block('df.iloc[0:2, 0:3]  # rows 0,1 cols 0,1,2')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight rows 0-1, cols 0-2 (exclusive end)
        slice_cells = [self.d_cells[r][c] for r in range(2) for c in range(3)]
        self.play(highlight_cells(slice_cells, color=YELLOW), run_time=0.5)

        note = Text("iloc uses integers — slices are EXCLUSIVE on the end (like Python)",
                     font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        # Comparison box
        comp = VGroup(
            Text("loc[1:3]  → rows 1, 2, 3  (inclusive)", font=CODE_FONT,
                 font_size=16, color=BLUE),
            Text("iloc[1:3] → rows 1, 2     (exclusive)", font=CODE_FONT,
                 font_size=16, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        comp.to_edge(LEFT, buff=0.5).shift(DOWN * 1.5)
        self.play(FadeIn(comp), run_time=0.5)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Boolean indexing (~60s) ──────────────────
    def boolean_indexing(self):
        title = section_title("Boolean Indexing (Filtering)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table(RIGHT * 1 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df[df["Age"] > 30]')
        code.scale(0.7).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Step 1: Show the boolean mask
        ages = [25, 30, 35, 28, 32]
        mask_texts = VGroup()
        for i, age in enumerate(ages):
            result = age > 30
            color = GREEN if result else RED
            t = Text(str(result), font=CODE_FONT, font_size=14, color=color)
            # Position next to each row
            t.next_to(self.d_cells[i][-1], RIGHT, buff=0.3)
            mask_texts.add(t)

        mask_label = Text("mask:", font=CODE_FONT, font_size=12, color=DIM)
        mask_label.next_to(mask_texts, UP, buff=0.2)
        self.play(FadeIn(mask_label),
                  LaggedStart(*[FadeIn(t) for t in mask_texts], lag_ratio=0.1),
                  run_time=0.8)
        self.wait(1)

        # Step 2: Highlight True rows (Charlie=35, Eve=32)
        true_rows = [2, 4]  # indices where age > 30
        true_cells = [self.d_cells[r][c] for r in true_rows for c in range(4)]
        self.play(highlight_cells(true_cells, color=GREEN), run_time=0.5)

        # Step 3: Dim False rows
        false_rows = [0, 1, 3]
        false_cells = [self.d_cells[r][c] for r in false_rows for c in range(4)]
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in false_cells]
        self.play(*dim_anims, run_time=0.5)

        note = Text("Only rows where the condition is True are kept",
                     font=CODE_FONT, font_size=16, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• df["col"] → select one column (Series)',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df[["a","b"]] → select columns (DataFrame)',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df.loc[row, col] → label-based (inclusive)",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df.iloc[row, col] → integer-based (exclusive)",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df[df["col"] > val] → boolean filter',
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Adding & Removing Columns →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
