"""
Karen's Spreadsheet — Episode 01: "Here's My Spreadsheet"
Karen emails you a CSV. You don't know what a DataFrame is. Yet.

Render: manim -pqh ep01_karens_spreadsheet.py KarensSpreadsheet
"""
from manim import *
import sys
sys.path.append("..")
from helpers import *


class KarensSpreadsheet(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.the_email()
        self.the_mistake()
        self.what_is_dataframe()
        self.the_fix()
        self.series_vs_dataframe()
        self.the_dict_way()
        self.recap()

    # ── Act 1: The Email (~40s) ──────────────────
    def the_email(self):
        # Slack message from Karen
        karen = Text("Karen from Sales", font=CODE_FONT, font_size=16, color=RED)
        karen.to_edge(UP, buff=0.8).to_edge(LEFT, buff=1)

        msg = Text(
            '"Hey, I attached the product spreadsheet.\n'
            ' Can you do some analysis? Thanks!!"',
            font=CODE_FONT, font_size=18, color=WHITE, line_spacing=1.3
        )
        msg.next_to(karen, DOWN, aligned_edge=LEFT, buff=0.3)

        attachment = VGroup(
            Rectangle(width=3, height=0.6, fill_color="#333333",
                      fill_opacity=1, stroke_color=BORDER),
            Text("📎 products.csv  (2.4 MB)", font=CODE_FONT,
                 font_size=14, color=DIM),
        )
        attachment[1].move_to(attachment[0])
        attachment.next_to(msg, DOWN, aligned_edge=LEFT, buff=0.3)

        self.play(FadeIn(karen), run_time=0.3)
        self.play(Write(msg), run_time=1.5)
        self.play(FadeIn(attachment), run_time=0.3)
        self.wait(1.5)

        # Your thought
        thought = Text("How hard can it be?", font=CODE_FONT,
                       font_size=20, color=DIM)
        thought.to_edge(DOWN, buff=1)
        self.play(FadeIn(thought), run_time=0.3)
        self.wait(1)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Act 2: The Mistake (~40s) ────────────────
    def the_mistake(self):
        title = Text("You try to open it...", font=CODE_FONT,
                     font_size=24, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Wrong way: open() and read lines
        bad_code = make_code_block(
            '# Your first attempt\n'
            'with open("products.csv") as f:\n'
            '    for line in f:\n'
            '        print(line)'
        )
        bad_code.scale(0.7).move_to(LEFT * 3 + DOWN * 0.3)
        self.play(FadeIn(bad_code), run_time=0.5)
        self.wait(1)

        # Terminal output: wall of text
        terminal = Rectangle(width=6, height=4, fill_color="#0d0d0d",
                             fill_opacity=1, stroke_color=BORDER)
        terminal.move_to(RIGHT * 2.5 + DOWN * 0.3)

        lines = VGroup()
        raw = [
            "Name,Price,City,Category,SKU",
            "Widget A,29.99,NYC,Electronics,SKU001",
            "Widget B,49.99,LA,Electronics,SKU002",
            "Gadget C,19.99,Chicago,Home,SKU003",
            "... (49,997 more lines)",
            "Widget Z,99.99,NYC,Electronics,SKU50000",
        ]
        for i, line in enumerate(raw):
            t = Text(line, font=CODE_FONT, font_size=11,
                     color=DIM if i == 4 else WHITE)
            t.move_to(terminal.get_top() + DOWN * (0.4 + i * 0.35) + LEFT * 0.1)
            t.align_to(terminal, LEFT).shift(RIGHT * 0.2)
            lines.add(t)

        self.play(FadeIn(terminal), run_time=0.3)
        for line in lines:
            self.play(FadeIn(line, shift=UP * 0.1), run_time=0.15)

        # Red warning
        warning = Text("50,000 lines of raw text. No structure. No types.",
                       font=CODE_FONT, font_size=16, color=RED)
        warning.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(warning), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Act 3: What is a DataFrame? (~50s) ───────
    def what_is_dataframe(self):
        # Old Greg appears
        greg = Text("Old Greg:", font=CODE_FONT, font_size=16, color=DIM)
        greg.to_edge(UP, buff=0.5).to_edge(LEFT, buff=1)
        advice = Text('"Use pandas. Read the CSV into a DataFrame."',
                      font=CODE_FONT, font_size=18, color=WHITE)
        advice.next_to(greg, DOWN, aligned_edge=LEFT, buff=0.2)

        self.play(FadeIn(greg), Write(advice), run_time=1)
        self.wait(1)

        you = Text('You: "What\'s a DataFrame?"', font=CODE_FONT,
                   font_size=16, color=TEAL)
        you.next_to(advice, DOWN, aligned_edge=LEFT, buff=0.4)
        self.play(FadeIn(you), run_time=0.3)
        self.wait(0.5)

        greg2 = Text("Old Greg: *sighs* \"It's a table. Rows and columns. Like Excel.\"",
                      font=CODE_FONT, font_size=16, color=DIM)
        greg2.next_to(you, DOWN, aligned_edge=LEFT, buff=0.3)
        self.play(FadeIn(greg2), run_time=0.5)
        self.wait(1.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

        # Show the concept
        title = section_title("DataFrame = Rows × Columns")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        headers = ["Name", "Price", "City", "Category"]
        rows = [
            ["Widget A", "29.99", "NYC", "Electronics"],
            ["Widget B", "49.99", "LA", "Electronics"],
            ["Gadget C", "19.99", "Chicago", "Home"],
            ["Widget D", "39.99", "NYC", "Home"],
        ]
        table, h_cells, d_cells = make_table(headers, rows, col_width=1.8)
        table.scale(0.85).shift(DOWN * 0.5)

        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in h_cells],
                              lag_ratio=0.1), run_time=0.5)
        for row in d_cells:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in row],
                                  lag_ratio=0.06), run_time=0.35)

        # Label rows and columns
        row_brace = Brace(VGroup(*[d_cells[i][0] for i in range(4)]), LEFT, color=YELLOW)
        row_label = Text("rows\n(products)", font=CODE_FONT, font_size=14, color=YELLOW)
        row_label.next_to(row_brace, LEFT, buff=0.1)

        col_brace = Brace(VGroup(*h_cells), UP, color=TEAL)
        col_label = Text("columns (attributes)", font=CODE_FONT, font_size=14, color=TEAL)
        col_label.next_to(col_brace, UP, buff=0.1)

        self.play(GrowFromCenter(row_brace), FadeIn(row_label), run_time=0.5)
        self.play(GrowFromCenter(col_brace), FadeIn(col_label), run_time=0.5)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Act 4: The Fix (~50s) ────────────────────
    def the_fix(self):
        title = section_title("The Right Way")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show the correct code
        code = make_code_block(
            'import pandas as pd\n\n'
            'df = pd.read_csv("products.csv")\n'
            'print(df.shape)   # (50000, 5)\n'
            'print(df.head())  # first 5 rows'
        )
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)
        self.play(FadeIn(code), run_time=0.5)
        self.wait(1)

        # Animate: CSV file → arrow → table
        csv_icon = VGroup(
            Rectangle(width=1.5, height=1, fill_color="#0d0d0d",
                      fill_opacity=1, stroke_color=BORDER),
            Text("CSV", font=CODE_FONT, font_size=16, color=DIM),
        )
        csv_icon[1].move_to(csv_icon[0])
        csv_icon.move_to(RIGHT * 1 + UP * 0.5)

        arrow = Arrow(start=RIGHT * 2, end=RIGHT * 3.2, color=TEAL)
        pd_label = Text("pd.read_csv()", font=CODE_FONT, font_size=12, color=TEAL)
        pd_label.next_to(arrow, UP, buff=0.1)

        self.play(FadeIn(csv_icon), run_time=0.3)
        self.play(GrowArrow(arrow), FadeIn(pd_label), run_time=0.5)

        # Small table appears
        headers = ["Name", "Price", "City"]
        rows = [["Widget A", "29.99", "NYC"],
                ["Widget B", "49.99", "LA"],
                ["...", "...", "..."]]
        table, h_cells, d_cells = make_table(headers, rows, col_width=1.4)
        table.scale(0.7).move_to(RIGHT * 5 + UP * 0.3)

        self.play(FadeIn(table), run_time=0.5)

        # Shape result
        shape_result = Text("df.shape → (50000, 5)", font=CODE_FONT,
                            font_size=20, color=GREEN)
        shape_result.move_to(RIGHT * 3 + DOWN * 1.5)
        self.play(FadeIn(shape_result), run_time=0.3)

        note = Text("One line of code. 50,000 rows loaded. Structured.",
                     font=CODE_FONT, font_size=16, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Act 5: Series vs DataFrame (~40s) ────────
    def series_vs_dataframe(self):
        title = section_title("Series vs DataFrame")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Karen: "Just give me the prices"
        karen_msg = Text('Karen: "Just give me the prices"',
                         font=CODE_FONT, font_size=18, color=RED)
        karen_msg.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(karen_msg), run_time=0.3)

        code = make_code_block('prices = df["Price"]\ntype(prices)  # → pd.Series')
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(code), run_time=0.3)

        # Series: single column
        s_cells = VGroup()
        for i, v in enumerate(["29.99", "49.99", "19.99", "39.99", "..."]):
            cell = make_cell(v, width=1.5)
            cell.move_to(RIGHT * 3 + DOWN * (i * 0.5 - 0.5))
            s_cells.add(cell)

        s_label = Text("Series\n(one column)", font=CODE_FONT,
                       font_size=14, color=TEAL)
        s_label.next_to(s_cells, RIGHT, buff=0.3)

        self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in s_cells],
                              lag_ratio=0.1), run_time=0.6)
        self.play(FadeIn(s_label), run_time=0.3)

        note = Text("One column = Series. Multiple columns = DataFrame.",
                     font=CODE_FONT, font_size=16, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Act 6: Creating from a Dict (~40s) ───────
    def the_dict_way(self):
        title = section_title("Creating a DataFrame from Scratch")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        you_msg = Text('You: "What if I don\'t have a CSV?"',
                       font=CODE_FONT, font_size=16, color=TEAL)
        you_msg.next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(you_msg), run_time=0.3)

        code = make_code_block(
            'data = {\n'
            '    "Name":  ["Alice", "Bob"],\n'
            '    "Price": [29.99, 49.99],\n'
            '}\n'
            'df = pd.DataFrame(data)'
        )
        code.scale(0.65).to_edge(LEFT, buff=0.5).shift(DOWN * 0.8)
        self.play(FadeIn(code), run_time=0.5)
        self.wait(1)

        # Keys fly up to become headers
        key_name = Text('"Name"', font=CODE_FONT, font_size=18, color=TEAL)
        key_price = Text('"Price"', font=CODE_FONT, font_size=18, color=TEAL)
        key_name.move_to(RIGHT * 2.5 + UP * 0.5)
        key_price.move_to(RIGHT * 4.5 + UP * 0.5)

        self.play(FadeIn(key_name, shift=UP * 0.3),
                  FadeIn(key_price, shift=UP * 0.3), run_time=0.5)

        # Arrow
        arrow_text = Text("keys → columns", font=CODE_FONT,
                          font_size=12, color=DIM)
        arrow_text.move_to(RIGHT * 3.5 + DOWN * 0.1)
        self.play(FadeIn(arrow_text), run_time=0.2)

        # Table
        headers = ["Name", "Price"]
        rows = [["Alice", "29.99"], ["Bob", "49.99"]]
        table, h_cells, d_cells = make_table(headers, rows, col_width=1.8)
        table.scale(0.85).move_to(RIGHT * 3.5 + DOWN * 1.5)

        self.play(
            Transform(key_name, h_cells[0]),
            Transform(key_price, h_cells[1]),
            FadeOut(arrow_text),
            run_time=0.8
        )
        for row in d_cells:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in row],
                                  lag_ratio=0.08), run_time=0.3)

        note = Text("Dict keys → column names. Values → column data.",
                     font=CODE_FONT, font_size=16, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (~20s) ─────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=CODE_FONT, font_size=28, color=TEAL),
            Text("• Don't read CSVs with open() — use pd.read_csv()",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• DataFrame = table (rows × columns)",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• Series = one column of a DataFrame",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• Create from dict: keys become column names",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df.shape tells you (rows, columns)",
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.2), run_time=1.5)
        self.wait(3)

        next_ep = Text('Next: Karen says "Show me the first 10 rows" →',
                       font=CODE_FONT, font_size=18, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
