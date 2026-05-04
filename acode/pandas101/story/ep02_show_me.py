"""
Karen's Spreadsheet — Episode 02: "Show Me the First 10"
Karen wants to see the data. You print all 50,000 rows. Your terminal dies.

Render: manim -pqh ep02_show_me.py ShowMeScene
"""
from manim import *
import sys
sys.path.append("..")
from helpers import *


class ShowMeScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.the_request()
        self.the_disaster()
        self.head_to_the_rescue()
        self.tail_and_shape()
        self.info_section()
        self.recap()

    # ── Karen's request (~20s) ───────────────────
    def the_request(self):
        karen = Text('Karen: "Show me the first 10 rows.\n'
                     '        I just want to see what it looks like."',
                     font=CODE_FONT, font_size=20, color=RED, line_spacing=1.3)
        karen.move_to(ORIGIN)
        self.play(Write(karen), run_time=1.5)
        self.wait(1.5)

        you = Text('You: "Sure, I\'ll just print it."', font=CODE_FONT,
                   font_size=18, color=TEAL)
        you.next_to(karen, DOWN, buff=0.5)
        self.play(FadeIn(you), run_time=0.3)
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── The disaster: print(df) (~40s) ───────────
    def the_disaster(self):
        title = Text("The Mistake", font=CODE_FONT, font_size=28, color=RED)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.3)

        code = make_code_block("print(df)  # 50,000 rows...")
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)

        # Terminal with scrolling text
        terminal = Rectangle(width=7, height=4.5, fill_color="#0d0d0d",
                             fill_opacity=1, stroke_color=BORDER)
        terminal.move_to(RIGHT * 1.5 + DOWN * 0.5)
        self.play(FadeIn(terminal), run_time=0.2)

        # Rapid scrolling lines
        scroll_group = VGroup()
        for i in range(20):
            row_text = f"  {i:5d}  Widget_{i:04d}  {19.99 + i:.2f}  NYC  Electronics"
            t = Text(row_text, font=CODE_FONT, font_size=9, color=DIM)
            t.move_to(terminal.get_top() + DOWN * (0.3 + i * 0.2))
            t.align_to(terminal, LEFT).shift(RIGHT * 0.15)
            scroll_group.add(t)

        # Fast scroll animation
        for t in scroll_group:
            self.play(FadeIn(t, shift=UP * 0.1), run_time=0.04)

        # "... 49,980 more rows" in the middle
        more = Text("... 49,980 more rows ...", font=CODE_FONT,
                    font_size=14, color=YELLOW)
        more.move_to(terminal.get_center())
        self.play(FadeIn(more), run_time=0.3)

        # Karen's reaction
        karen_react = Text('Karen: "WHAT IS ALL THAT?!"',
                           font=CODE_FONT, font_size=18, color=RED)
        karen_react.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(karen_react), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── head() saves the day (~60s) ──────────────
    def head_to_the_rescue(self):
        # Old Greg
        greg = Text('Old Greg: "Use .head(), rookie."',
                     font=CODE_FONT, font_size=18, color=DIM)
        greg.to_edge(UP, buff=0.5)
        self.play(FadeIn(greg), run_time=0.3)
        self.wait(0.5)

        title = section_title("df.head(n)")
        title.next_to(greg, DOWN, buff=0.3)
        self.play(Write(title), run_time=0.3)

        # Code
        code = make_code_block("df.head(5)  # first 5 rows (default)")
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)
        self.play(FadeIn(code), run_time=0.3)

        # Full table (but we'll only highlight top 5)
        headers = ["Name", "Price", "City", "Category"]
        rows = [
            ["Widget A", "29.99", "NYC", "Electronics"],
            ["Widget B", "49.99", "LA", "Electronics"],
            ["Gadget C", "19.99", "Chicago", "Home"],
            ["Widget D", "39.99", "NYC", "Home"],
            ["Gadget E", "59.99", "LA", "Electronics"],
            ["Widget F", "24.99", "NYC", "Home"],
            ["Gadget G", "44.99", "Chicago", "Electronics"],
            ["Widget H", "34.99", "LA", "Home"],
        ]
        table, h_cells, d_cells = make_table(headers, rows, col_width=1.5)
        table.scale(0.65).move_to(RIGHT * 2.5 + DOWN * 0.5)
        self.play(FadeIn(table), run_time=0.5)
        self.wait(0.5)

        # Highlight first 5 rows
        top5 = [cell for row in d_cells[:5] for cell in row]
        rest = [cell for row in d_cells[5:] for cell in row]

        self.play(highlight_cells(top5, color=TEAL), run_time=0.5)

        # Dim the rest
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in rest]
        self.play(*dim_anims, run_time=0.5)

        # Bracket showing "these 5"
        brace = Brace(VGroup(*[d_cells[i][0] for i in range(5)]), LEFT,
                       color=TEAL)
        brace_label = Text("5 rows", font=CODE_FONT, font_size=14, color=TEAL)
        brace_label.next_to(brace, LEFT, buff=0.1)
        self.play(GrowFromCenter(brace), FadeIn(brace_label), run_time=0.3)

        note = Text("head(n) shows the first n rows. Default is 5.",
                     font=CODE_FONT, font_size=16, color=DIM)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.stored_table = table
        self.stored_h = h_cells
        self.stored_d = d_cells
        self.play(*[FadeOut(m) for m in [greg, title, code, brace,
                    brace_label, note]])
        # Reset highlights
        self.play(unhighlight_cells(top5),
                  *[cell[0].animate.set_opacity(1) for cell in rest],
                  run_time=0.2)

    # ── tail() and shape (~50s) ──────────────────
    def tail_and_shape(self):
        title = section_title("df.tail(n) and df.shape")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.3)

        # tail(3)
        code_tail = make_code_block("df.tail(3)  # last 3 rows")
        code_tail.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.3)
        self.play(FadeIn(code_tail), run_time=0.3)

        bottom3 = [cell for row in self.stored_d[-3:] for cell in row]
        top_rest = [cell for row in self.stored_d[:-3] for cell in row]

        self.play(highlight_cells(bottom3, color=YELLOW), run_time=0.5)
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in top_rest]
        self.play(*dim_anims, run_time=0.3)

        self.wait(1.5)
        self.play(unhighlight_cells(bottom3),
                  *[cell[0].animate.set_opacity(1) for cell in top_rest],
                  FadeOut(code_tail), run_time=0.3)

        # shape
        code_shape = make_code_block("df.shape  # → (50000, 5)")
        code_shape.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.3)
        self.play(FadeIn(code_shape), run_time=0.3)

        shape_result = VGroup(
            Text("(", font=CODE_FONT, font_size=36, color=WHITE),
            Text("50000", font=CODE_FONT, font_size=36, color=YELLOW),
            Text(",", font=CODE_FONT, font_size=36, color=WHITE),
            Text("5", font=CODE_FONT, font_size=36, color=TEAL),
            Text(")", font=CODE_FONT, font_size=36, color=WHITE),
        ).arrange(RIGHT, buff=0.1)
        shape_result.to_edge(LEFT, buff=0.5).shift(DOWN * 1.5)

        row_label = Text("rows", font=CODE_FONT, font_size=14, color=YELLOW)
        col_label = Text("columns", font=CODE_FONT, font_size=14, color=TEAL)
        row_label.next_to(shape_result[1], DOWN, buff=0.15)
        col_label.next_to(shape_result[3], DOWN, buff=0.15)

        self.play(FadeIn(shape_result), run_time=0.5)
        self.play(FadeIn(row_label), FadeIn(col_label), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── info() (~30s) ────────────────────────────
    def info_section(self):
        title = section_title("df.info()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.3)

        karen_msg = Text('Karen: "Are there any missing values?"',
                         font=CODE_FONT, font_size=18, color=RED)
        karen_msg.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(karen_msg), run_time=0.3)

        code = make_code_block("df.info()")
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(code), run_time=0.3)

        # Simulated info output
        info_lines = [
            "RangeIndex: 50000 entries, 0 to 49999",
            "Data columns (5 columns):",
            " Name      50000 non-null  object",
            " Price     49153 non-null  float64",
            " City      50000 non-null  object",
            " Category  50000 non-null  object",
            " SKU       50000 non-null  object",
        ]
        info_group = VGroup()
        for i, line in enumerate(info_lines):
            color = RED if "49153" in line else WHITE
            t = Text(line, font=CODE_FONT, font_size=13, color=color)
            t.move_to(RIGHT * 2 + DOWN * (i * 0.35 - 0.5))
            info_group.add(t)

        self.play(LaggedStart(*[FadeIn(t) for t in info_group],
                              lag_ratio=0.1), run_time=1)

        # Highlight the problem
        warning = Text("⚠ Price has 847 missing values!",
                       font=CODE_FONT, font_size=18, color=RED)
        warning.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(warning), run_time=0.3)
        self.wait(2)

        karen2 = Text('Karen: "Fix it." (That\'s Episode 08)',
                      font=CODE_FONT, font_size=14, color=DIM)
        karen2.next_to(warning, DOWN, buff=0.2)
        self.play(FadeIn(karen2), run_time=0.3)
        self.wait(1.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (~15s) ─────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=CODE_FONT, font_size=28, color=TEAL),
            Text("• Never print(df) on 50,000 rows",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df.head(n) → first n rows",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df.tail(n) → last n rows",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df.shape → (rows, columns)",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df.info() → column types + missing values",
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text('Next: Karen says "Find all NYC products" →',
                       font=CODE_FONT, font_size=18, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
