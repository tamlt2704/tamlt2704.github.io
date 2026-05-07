"""
Episode 11: Pivot Tables
~5 min | Concepts: pivot_table(), pd.melt(), stack(), unstack()

Render: manim -pqh ep11_pivot.py PivotScene
"""
from manim import *
from helpers import *


class PivotScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.basic_pivot()
        self.melt_section()
        self.stack_unstack()
        self.outro()

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 11: Pivot Tables",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Basic pivot_table() (~80s) ───────────────
    def basic_pivot(self):
        title = section_title("pivot_table()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Source data: sales by person and product
        headers = ["Name", "Product", "Revenue"]
        rows = [
            ["Alice", "Widget", "100"],
            ["Alice", "Gadget", "150"],
            ["Bob", "Widget", "200"],
            ["Bob", "Gadget", "120"],
            ["Charlie", "Widget", "180"],
            ["Charlie", "Gadget", "90"],
        ]
        table, h, d = make_table(headers, rows, col_width=1.5)
        table.scale(0.65).move_to(LEFT * 3 + DOWN * 0.3)

        source_label = Text("Source (long format)", font=CODE_FONT,
                            font_size=12, color=DIM)
        source_label.next_to(table, UP, buff=0.2)
        self.play(FadeIn(table), FadeIn(source_label), run_time=0.5)

        code = make_code_block('df.pivot_table(\n    values="Revenue",\n    index="Name",\n    columns="Product",\n    aggfunc="mean"\n)')
        code.scale(0.55).to_edge(LEFT, buff=0.3).shift(UP * 2.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(1)

        # Show pivot result
        pivot_headers = ["Name", "Gadget", "Widget"]
        pivot_rows = [
            ["Alice", "150", "100"],
            ["Bob", "120", "200"],
            ["Charlie", "90", "180"],
        ]
        pivot_table, ph, pd_cells = make_table(pivot_headers, pivot_rows,
                                                col_width=1.5)
        pivot_table.scale(0.7).move_to(RIGHT * 2.5 + DOWN * 0.3)

        result_label = Text("Pivot result (wide format)", font=CODE_FONT,
                            font_size=12, color=DIM)
        result_label.next_to(pivot_table, UP, buff=0.2)

        # Animate transformation
        arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color=TEAL, stroke_width=3)
        arrow.move_to(ORIGIN + DOWN * 0.3)
        self.play(GrowArrow(arrow), run_time=0.3)
        self.play(FadeIn(pivot_table), FadeIn(result_label), run_time=1)

        # Highlight how rows became columns
        self.play(highlight_cells([ph[1], ph[2]], color=YELLOW), run_time=0.5)

        note = Text("Product values became column headers!",
                    font=CODE_FONT, font_size=15, color=YELLOW)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── pd.melt() — wide to long (~70s) ─────────
    def melt_section(self):
        title = section_title("pd.melt() — Wide → Long")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Wide format table
        wide_headers = ["Name", "Math", "Science"]
        wide_rows = [
            ["Alice", "90", "85"],
            ["Bob", "78", "92"],
        ]
        wide_table, wh, wd = make_table(wide_headers, wide_rows, col_width=1.5)
        wide_table.scale(0.7).move_to(LEFT * 3 + UP * 0.5)

        wide_label = Text("Wide format", font=CODE_FONT, font_size=12, color=DIM)
        wide_label.next_to(wide_table, UP, buff=0.2)
        self.play(FadeIn(wide_table), FadeIn(wide_label), run_time=0.5)

        code = make_code_block('pd.melt(df, id_vars=["Name"],\n        value_vars=["Math", "Science"],\n        var_name="Subject",\n        value_name="Score")')
        code.scale(0.55).to_edge(LEFT, buff=0.3).shift(DOWN * 1.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show melted result
        long_headers = ["Name", "Subject", "Score"]
        long_rows = [
            ["Alice", "Math", "90"],
            ["Bob", "Math", "78"],
            ["Alice", "Science", "85"],
            ["Bob", "Science", "92"],
        ]
        long_table, lh, ld = make_table(long_headers, long_rows, col_width=1.5)
        long_table.scale(0.65).move_to(RIGHT * 2.5 + DOWN * 0.3)

        long_label = Text("Long format", font=CODE_FONT, font_size=12, color=DIM)
        long_label.next_to(long_table, UP, buff=0.2)

        arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color=TEAL, stroke_width=3)
        arrow.move_to(ORIGIN + UP * 0.5)
        self.play(GrowArrow(arrow), run_time=0.3)
        self.play(FadeIn(long_table), FadeIn(long_label), run_time=1)

        # Highlight how columns became rows
        self.play(highlight_cells([wh[1], wh[2]], color=YELLOW), run_time=0.3)

        note = Text("melt() is the inverse of pivot — columns become row values",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── stack() / unstack() (~50s) ───────────────
    def stack_unstack(self):
        title = section_title("stack() / unstack()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Visual explanation
        explanation = VGroup(
            Text("stack()   → columns → row index (wide → long)",
                 font=CODE_FONT, font_size=16, color=WHITE),
            Text("unstack() → row index → columns (long → wide)",
                 font=CODE_FONT, font_size=16, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        explanation.move_to(UP * 0.5)
        self.play(FadeIn(explanation), run_time=0.5)
        self.wait(1)

        code = make_code_block('# MultiIndex example\ndf.set_index(["City", "Year"]).unstack()')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(DOWN * 1)
        self.play(FadeIn(code), run_time=0.3)

        # Show before/after
        before_headers = ["City", "Year", "Pop"]
        before_rows = [
            ["NYC", "2020", "8.3M"],
            ["NYC", "2021", "8.1M"],
            ["LA", "2020", "3.9M"],
            ["LA", "2021", "3.8M"],
        ]
        before_table, bh, bd = make_table(before_headers, before_rows, col_width=1.2)
        before_table.scale(0.6).move_to(LEFT * 3 + DOWN * 1)

        after_headers = ["City", "2020", "2021"]
        after_rows = [
            ["NYC", "8.3M", "8.1M"],
            ["LA", "3.9M", "3.8M"],
        ]
        after_table, ah, ad = make_table(after_headers, after_rows, col_width=1.2)
        after_table.scale(0.6).move_to(RIGHT * 3 + DOWN * 1)

        arrow = Arrow(LEFT * 0.3, RIGHT * 0.3, color=TEAL, stroke_width=3)
        arrow.move_to(ORIGIN + DOWN * 1)

        self.play(FadeIn(before_table), run_time=0.3)
        self.play(GrowArrow(arrow), run_time=0.2)
        self.play(FadeIn(after_table), run_time=0.3)

        note = Text("unstack() pivots an index level into columns",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text("• pivot_table() → reshape long → wide",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• pd.melt() → reshape wide → long",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• stack() → columns → MultiIndex rows",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• unstack() → MultiIndex rows → columns",
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Plotting →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
