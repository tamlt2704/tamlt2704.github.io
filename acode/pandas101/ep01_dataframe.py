"""
Episode 01: What is a DataFrame?
~5 min | Concepts: Series, DataFrame, creating from dict/list

Render: manim -pqh ep01_dataframe.py DataFrameScene
"""
from manim import *
from helpers import *


class DataFrameScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.what_is_series()
        self.what_is_dataframe()
        self.create_from_dict()
        self.create_from_list()
        self.series_vs_dataframe()
        self.outro()

    # ── Intro (~20s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 1: What is a DataFrame?",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(0.3)

    # ── What is a Series? (~50s) ─────────────────
    def what_is_series(self):
        # Title
        title = section_title("What is a Series?")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show code
        code = make_code_block(
            'import pandas as pd\n\ns = pd.Series([10, 20, 30, 40])\nprint(s)'
        )
        code.scale(0.8).to_edge(LEFT, buff=0.8).shift(DOWN * 0.5)
        self.play(FadeIn(code), run_time=0.5)
        self.wait(1)

        # Animate: a single column of data
        header = make_cell("values", bg=HEADER_BG, text_color=TEAL)
        cells = VGroup()
        idx_cells = VGroup()
        values = [10, 20, 30, 40]

        for i, v in enumerate(values):
            idx = make_cell(str(i), width=0.6, bg=HEADER_BG, text_color=YELLOW, font_size=16)
            cell = make_cell(str(v))
            idx.move_to([3.5, -i * 0.5, 0])
            cell.move_to([3.5 + 1.2, -i * 0.5, 0])
            idx_cells.add(idx)
            cells.add(cell)

        series_group = VGroup(idx_cells, cells)
        series_group.move_to(RIGHT * 3 + DOWN * 0.3)

        # Index label
        idx_label = Text("index", font=CODE_FONT, font_size=14, color=YELLOW)
        val_label = Text("values", font=CODE_FONT, font_size=14, color=TEAL)

        self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.3) for c in idx_cells],
                              lag_ratio=0.15), run_time=1)
        self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.3) for c in cells],
                              lag_ratio=0.15), run_time=1)

        idx_label.next_to(idx_cells, UP, buff=0.2)
        val_label.next_to(cells, UP, buff=0.2)
        self.play(FadeIn(idx_label), FadeIn(val_label), run_time=0.3)

        # Explain
        note = Text("A Series is a single column with an index",
                     font=CODE_FONT, font_size=18, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in [title, code, series_group,
                    idx_label, val_label, note]])
        self.wait(0.3)

    # ── What is a DataFrame? (~60s) ──────────────
    def what_is_dataframe(self):
        title = section_title("What is a DataFrame?")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show the table
        headers = ["Name", "Age", "City"]
        rows = [
            ["Alice", "25", "NYC"],
            ["Bob", "30", "LA"],
            ["Charlie", "35", "Chicago"],
            ["Diana", "28", "NYC"],
        ]
        table, h_cells, d_cells = make_table(headers, rows)
        table.scale(0.9).shift(DOWN * 0.5)

        # Animate header first, then rows
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in h_cells],
                              lag_ratio=0.1), run_time=0.5)
        for row in d_cells:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in row],
                                  lag_ratio=0.08), run_time=0.4)

        self.wait(1)

        # Label: rows and columns
        row_arrow = Arrow(start=LEFT * 4.5 + DOWN * 0.5,
                          end=LEFT * 4.5 + DOWN * 2.5, color=YELLOW)
        row_label = Text("rows", font=CODE_FONT, font_size=16, color=YELLOW)
        row_label.next_to(row_arrow, LEFT, buff=0.1)

        col_arrow = Arrow(start=LEFT * 2.5 + UP * 0.8,
                          end=RIGHT * 2.5 + UP * 0.8, color=TEAL)
        col_label = Text("columns", font=CODE_FONT, font_size=16, color=TEAL)
        col_label.next_to(col_arrow, UP, buff=0.1)

        self.play(GrowArrow(row_arrow), FadeIn(row_label), run_time=0.5)
        self.play(GrowArrow(col_arrow), FadeIn(col_label), run_time=0.5)

        note = Text("A DataFrame = rows × columns (like a spreadsheet)",
                     font=CODE_FONT, font_size=18, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.3)

    # ── Create from Dict (~60s) ──────────────────
    def create_from_dict(self):
        title = section_title("Create from Dictionary")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block(
            'data = {\n'
            '    "Name": ["Alice", "Bob"],\n'
            '    "Age":  [25, 30],\n'
            '    "City": ["NYC", "LA"],\n'
            '}\n'
            'df = pd.DataFrame(data)'
        )
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)
        self.play(FadeIn(code), run_time=0.5)
        self.wait(1)

        # Show dict keys becoming column headers
        keys = ["Name", "Age", "City"]
        key_texts = VGroup()
        for i, k in enumerate(keys):
            t = Text(f'"{k}"', font=CODE_FONT, font_size=20, color=TEAL)
            t.move_to(RIGHT * (1.5 + i * 2) + UP * 1)
            key_texts.add(t)

        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.3) for t in key_texts],
                              lag_ratio=0.15), run_time=0.8)

        # Arrow: keys → headers
        arrow_label = Text("keys → column headers", font=CODE_FONT,
                           font_size=14, color=DIM)
        arrow_label.move_to(RIGHT * 3.5 + UP * 0.3)
        self.play(FadeIn(arrow_label), run_time=0.3)

        # Build the table
        headers = ["Name", "Age", "City"]
        rows = [["Alice", "25", "NYC"], ["Bob", "30", "LA"]]
        table, h_cells, d_cells = make_table(headers, rows)
        table.scale(0.85).move_to(RIGHT * 3.5 + DOWN * 1)

        # Transform keys into headers
        self.play(
            *[Transform(key_texts[i], h_cells[i]) for i in range(3)],
            FadeOut(arrow_label),
            run_time=1
        )

        # Rows appear
        for row in d_cells:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in row],
                                  lag_ratio=0.08), run_time=0.4)

        note = Text("Dict keys become columns, values become rows",
                     font=CODE_FONT, font_size=18, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.3)

    # ── Create from List (~50s) ──────────────────
    def create_from_list(self):
        title = section_title("Create from List of Lists")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block(
            'data = [\n'
            '    ["Alice", 25, "NYC"],\n'
            '    ["Bob",   30, "LA"],\n'
            ']\n'
            'df = pd.DataFrame(\n'
            '    data,\n'
            '    columns=["Name", "Age", "City"]\n'
            ')'
        )
        code.scale(0.65).to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)
        self.play(FadeIn(code), run_time=0.5)
        self.wait(1)

        # Show list items becoming rows
        row_texts = VGroup()
        raw_rows = [["Alice", "25", "NYC"], ["Bob", "30", "LA"]]
        for i, row in enumerate(raw_rows):
            t = Text(str(row), font=CODE_FONT, font_size=16, color=YELLOW)
            t.move_to(RIGHT * 3.5 + UP * (0.5 - i * 0.6))
            row_texts.add(t)

        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.3) for t in row_texts],
                              lag_ratio=0.2), run_time=0.6)

        arrow_label = Text("each list → one row", font=CODE_FONT,
                           font_size=14, color=DIM)
        arrow_label.move_to(RIGHT * 3.5 + DOWN * 0.5)
        self.play(FadeIn(arrow_label), run_time=0.3)
        self.wait(1)

        # Build table
        headers = ["Name", "Age", "City"]
        table, h_cells, d_cells = make_table(headers, raw_rows)
        table.scale(0.85).move_to(RIGHT * 3.5 + DOWN * 1.5)

        self.play(FadeOut(row_texts), FadeOut(arrow_label), run_time=0.3)
        self.play(
            LaggedStart(*[FadeIn(c) for c in h_cells], lag_ratio=0.1),
            run_time=0.4
        )
        for row in d_cells:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in row],
                                  lag_ratio=0.08), run_time=0.4)

        note = Text("Each inner list becomes a row; columns provided separately",
                     font=CODE_FONT, font_size=16, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.3)

    # ── Series vs DataFrame (~40s) ───────────────
    def series_vs_dataframe(self):
        title = section_title("Series vs DataFrame")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Series: single column
        s_label = Text("Series", font=CODE_FONT, font_size=22, color=TEAL)
        s_label.move_to(LEFT * 3.5 + UP * 1.5)
        s_desc = Text("1 column", font=CODE_FONT, font_size=16, color=DIM)
        s_desc.next_to(s_label, DOWN, buff=0.2)

        s_cells = VGroup()
        for i, v in enumerate([10, 20, 30]):
            cell = make_cell(str(v), width=1.5)
            cell.move_to(LEFT * 3.5 + DOWN * (i * 0.5 - 0.3))
            s_cells.add(cell)

        # DataFrame: multiple columns
        df_label = Text("DataFrame", font=CODE_FONT, font_size=22, color=TEAL)
        df_label.move_to(RIGHT * 2.5 + UP * 1.5)
        df_desc = Text("N columns", font=CODE_FONT, font_size=16, color=DIM)
        df_desc.next_to(df_label, DOWN, buff=0.2)

        headers = ["A", "B", "C"]
        rows = [["1", "4", "7"], ["2", "5", "8"], ["3", "6", "9"]]
        table, h_cells, d_cells = make_table(headers, rows, col_width=1.2)
        table.scale(0.85).move_to(RIGHT * 2.5 + DOWN * 0.3)

        # Animate side by side
        self.play(FadeIn(s_label), FadeIn(s_desc), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(c) for c in s_cells], lag_ratio=0.1),
                  run_time=0.5)

        self.play(FadeIn(df_label), FadeIn(df_desc), run_time=0.3)
        self.play(FadeIn(table), run_time=0.5)

        # Highlight: Series = 1 col of a DataFrame
        box = SurroundingRectangle(
            VGroup(*[d_cells[r][0] for r in range(3)], h_cells[0]),
            color=YELLOW, buff=0.05
        )
        note = Text("A Series is one column of a DataFrame",
                     font=CODE_FONT, font_size=18, color=YELLOW)
        note.to_edge(DOWN, buff=0.5)
        self.play(Create(box), FadeIn(note), run_time=0.5)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.3)

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text("• Series = 1D labeled array (one column)",
                 font=CODE_FONT, font_size=20, color=WHITE),
            Text("• DataFrame = 2D table (rows × columns)",
                 font=CODE_FONT, font_size=20, color=WHITE),
            Text("• Create from dict: keys → columns",
                 font=CODE_FONT, font_size=20, color=WHITE),
            Text("• Create from list: each list → one row",
                 font=CODE_FONT, font_size=20, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.2), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Reading & Writing Data →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
