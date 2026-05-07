"""
Episode 09: Merge & Join
~5 min | Concepts: pd.merge(), how="inner"/"left"/"right"/"outer", pd.concat()

Render: manim -pqh ep09_merge_join.py MergeJoinScene
"""
from manim import *
from helpers import *


class MergeJoinScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.inner_join()
        self.left_join()
        self.concat_section()
        self.outro()

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 9: Merge & Join",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Inner join (~80s) ────────────────────────
    def inner_join(self):
        title = section_title('pd.merge() — inner join')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Left table: employees
        left_headers = ["emp_id", "Name"]
        left_rows = [
            ["1", "Alice"],
            ["2", "Bob"],
            ["3", "Charlie"],
        ]
        left_table, lh, ld = make_table(left_headers, left_rows, col_width=1.5)
        left_table.scale(0.7).move_to(LEFT * 3 + DOWN * 0.3)

        # Right table: salaries
        right_headers = ["emp_id", "Salary"]
        right_rows = [
            ["1", "70000"],
            ["2", "80000"],
            ["4", "90000"],
        ]
        right_table, rh, rd = make_table(right_headers, right_rows, col_width=1.5)
        right_table.scale(0.7).move_to(RIGHT * 3 + DOWN * 0.3)

        # Labels
        left_label = Text("df_employees", font=CODE_FONT, font_size=14, color=DIM)
        left_label.next_to(left_table, UP, buff=0.2)
        right_label = Text("df_salaries", font=CODE_FONT, font_size=14, color=DIM)
        right_label.next_to(right_table, UP, buff=0.2)

        self.play(FadeIn(left_table), FadeIn(left_label),
                  FadeIn(right_table), FadeIn(right_label), run_time=0.5)

        code = make_code_block('pd.merge(df_emp, df_sal, on="emp_id")')
        code.scale(0.6).to_edge(UP, buff=1.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Draw connecting lines between matching keys (emp_id 1 and 2)
        lines = VGroup()
        for row_l, row_r in [(0, 0), (1, 1)]:  # emp_id 1→1, 2→2
            start = ld[row_l][0].get_right()
            end = rd[row_r][0].get_left()
            line = Line(start, end, color=GREEN, stroke_width=2)
            lines.add(line)

        self.play(Create(lines), run_time=0.8)
        self.wait(0.5)

        # Highlight non-matching rows (Charlie=3, emp_id=4)
        no_match_left = [ld[2][c] for c in range(2)]
        no_match_right = [rd[2][c] for c in range(2)]
        self.play(
            highlight_cells(no_match_left, color=RED),
            highlight_cells(no_match_right, color=RED),
            run_time=0.5
        )

        # Slide tables together
        self.play(
            left_table.animate.shift(RIGHT * 1.5),
            left_label.animate.shift(RIGHT * 1.5),
            right_table.animate.shift(LEFT * 1.5),
            right_label.animate.shift(LEFT * 1.5),
            FadeOut(lines),
            run_time=1
        )

        note = Text("inner join: only rows with matching keys in BOTH tables",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)

        # Fade out non-matching rows
        self.play(
            *[FadeOut(c) for c in no_match_left],
            *[FadeOut(c) for c in no_match_right],
            run_time=0.8
        )
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Left join (~60s) ─────────────────────────
    def left_join(self):
        title = section_title('how="left"')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Left table
        left_headers = ["emp_id", "Name"]
        left_rows = [
            ["1", "Alice"],
            ["2", "Bob"],
            ["3", "Charlie"],
        ]
        left_table, lh, ld = make_table(left_headers, left_rows, col_width=1.5)
        left_table.scale(0.7).move_to(LEFT * 3 + DOWN * 0.3)

        # Right table
        right_headers = ["emp_id", "Salary"]
        right_rows = [
            ["1", "70000"],
            ["2", "80000"],
        ]
        right_table, rh, rd = make_table(right_headers, right_rows, col_width=1.5)
        right_table.scale(0.7).move_to(RIGHT * 3 + DOWN * 0.3)

        self.play(FadeIn(left_table), FadeIn(right_table), run_time=0.5)

        code = make_code_block('pd.merge(left, right, on="emp_id",\n         how="left")')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 2)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show result: all left rows kept, unmatched get NaN
        result_headers = ["emp_id", "Name", "Salary"]
        result_rows = [
            ["1", "Alice", "70000"],
            ["2", "Bob", "80000"],
            ["3", "Charlie", "NaN"],
        ]
        result_table, res_h, res_d = make_table(result_headers, result_rows,
                                                 col_width=1.5)
        result_table.scale(0.7).move_to(DOWN * 0.3)

        self.play(
            FadeOut(left_table), FadeOut(right_table),
            FadeIn(result_table, shift=UP * 0.5),
            run_time=1
        )

        # Highlight the NaN cell
        nan_cell = res_d[2][2]
        self.play(highlight_cells([nan_cell], color=RED), run_time=0.5)

        note = Text("Left join: ALL left rows kept, NaN where no right match",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        # Quick comparison of join types
        comparison = VGroup(
            Text("inner → only matching rows", font=CODE_FONT,
                 font_size=14, color=WHITE),
            Text("left  → all left + matching right", font=CODE_FONT,
                 font_size=14, color=WHITE),
            Text("right → all right + matching left", font=CODE_FONT,
                 font_size=14, color=WHITE),
            Text("outer → all rows from both", font=CODE_FONT,
                 font_size=14, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        comparison.to_edge(LEFT, buff=0.3).shift(DOWN * 1)
        self.play(LaggedStart(*[FadeIn(c) for c in comparison],
                              lag_ratio=0.2), run_time=1)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── pd.concat() (~60s) ───────────────────────
    def concat_section(self):
        title = section_title("pd.concat()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Two DataFrames to stack
        headers = ["Name", "Age"]
        rows1 = [["Alice", "25"], ["Bob", "30"]]
        rows2 = [["Charlie", "35"], ["Diana", "28"]]

        table1, h1, d1 = make_table(headers, rows1, col_width=1.8)
        table1.scale(0.7).move_to(UP * 0.5)
        table2, h2, d2 = make_table(headers, rows2, col_width=1.8)
        table2.scale(0.7).move_to(DOWN * 1.5)

        label1 = Text("df1", font=CODE_FONT, font_size=14, color=DIM)
        label1.next_to(table1, LEFT, buff=0.3)
        label2 = Text("df2", font=CODE_FONT, font_size=14, color=DIM)
        label2.next_to(table2, LEFT, buff=0.3)

        self.play(FadeIn(table1), FadeIn(label1), run_time=0.3)
        self.play(FadeIn(table2), FadeIn(label2), run_time=0.3)

        code = make_code_block('pd.concat([df1, df2], ignore_index=True)')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 2.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Animate tables stacking vertically
        self.play(
            table2.animate.next_to(table1, DOWN, buff=0),
            FadeOut(label1), FadeOut(label2),
            FadeOut(h2),  # Remove duplicate header
            run_time=1.5
        )

        note = Text("concat stacks DataFrames vertically (axis=0) or horizontally (axis=1)",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• pd.merge(left, right, on="key") → SQL-style join',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• how="inner"/"left"/"right"/"outer"',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• pd.concat([df1, df2]) → stack DataFrames",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• ignore_index=True → reset row numbers",
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Apply & Lambda →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
