"""
Episode 06: Sorting
~5 min | Concepts: sort_values(), ascending, nlargest(), nsmallest()

Render: manim -pqh ep06_sorting.py SortingScene
"""
from manim import *
from helpers import *


class SortingScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_base_table()
        self.intro()
        self.sort_single()
        self.sort_multiple()
        self.nlargest()
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
        subtitle = Text("Episode 6: Sorting",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Sort by single column (~70s) ─────────────
    def sort_single(self):
        title = section_title("sort_values()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df.sort_values("Age")')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight Age column
        age_cells = [self.h_cells[1]] + [self.d_cells[r][1] for r in range(5)]
        self.play(highlight_cells(age_cells, color=TEAL), run_time=0.5)
        self.wait(0.5)

        # Animate rows shuffling into sorted order by Age
        # Original order: Alice(25), Bob(30), Charlie(35), Diana(28), Eve(32)
        # Sorted order:   Alice(25), Diana(28), Bob(30), Eve(32), Charlie(35)
        sorted_indices = [0, 3, 1, 4, 2]  # original row index in sorted order
        target_positions = [self.d_cells[i][0].get_center() for i in range(5)]

        row_groups = []
        for r in range(5):
            row_vg = VGroup(*[self.d_cells[r][c] for c in range(4)])
            row_groups.append(row_vg)

        # Animate each row moving to its sorted position
        anims = []
        for new_pos, orig_idx in enumerate(sorted_indices):
            target_y = target_positions[new_pos][1]
            current_y = row_groups[orig_idx].get_center()[1]
            shift_amount = target_y - current_y
            anims.append(row_groups[orig_idx].animate.shift(UP * shift_amount))

        self.play(*anims, run_time=1.5)

        note = Text("ascending=True by default (smallest first)",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        # Show descending
        code2 = make_code_block('df.sort_values("Age", ascending=False)')
        code2.scale(0.6).to_edge(LEFT, buff=0.3).shift(DOWN * 1)
        self.play(FadeIn(code2), run_time=0.3)

        desc_note = Text("ascending=False → largest first",
                         font=CODE_FONT, font_size=15, color=YELLOW)
        desc_note.next_to(code2, DOWN, buff=0.3)
        self.play(FadeIn(desc_note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Sort by multiple columns (~60s) ──────────
    def sort_multiple(self):
        title = section_title("Multi-column Sort")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Use a table where multi-sort makes sense
        headers = ["Name", "City", "Age"]
        rows = [
            ["Alice", "NYC", "25"],
            ["Bob", "LA", "30"],
            ["Charlie", "NYC", "35"],
            ["Diana", "LA", "28"],
            ["Eve", "NYC", "32"],
        ]
        table, h, d = make_table(headers, rows, col_width=1.5)
        table.scale(0.75).move_to(RIGHT * 1.5 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df.sort_values(["City", "Age"])')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Step 1: Highlight City column (primary sort)
        city_cells = [h[1]] + [d[r][1] for r in range(5)]
        self.play(highlight_cells(city_cells, color=TEAL), run_time=0.5)

        step1 = Text("① Sort by City first", font=CODE_FONT,
                     font_size=14, color=TEAL)
        step1.to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(step1), run_time=0.3)
        self.wait(1)

        # Step 2: Highlight Age column (secondary sort)
        age_cells = [h[2]] + [d[r][2] for r in range(5)]
        self.play(highlight_cells(age_cells, color=YELLOW), run_time=0.5)

        step2 = Text("② Then by Age within each City", font=CODE_FONT,
                     font_size=14, color=YELLOW)
        step2.next_to(step1, DOWN, buff=0.2)
        self.play(FadeIn(step2), run_time=0.3)

        # Show sorted result
        result_text = Text(
            "Result: LA(28,30), NYC(25,32,35)",
            font=CODE_FONT, font_size=14, color=DIM
        )
        result_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(result_text), run_time=0.3)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── nlargest / nsmallest (~50s) ──────────────
    def nlargest(self):
        title = section_title("nlargest() / nsmallest()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        table = self.show_table()
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df.nlargest(3, "Salary")')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight salary column
        sal_cells = [self.d_cells[r][3] for r in range(5)]
        self.play(highlight_cells(sal_cells, color=TEAL), run_time=0.3)
        self.wait(0.5)

        # Top 3 salaries: Charlie(90k), Eve(85k), Bob(80k) → rows 2, 4, 1
        top_rows = [2, 4, 1]
        top_cells = [self.d_cells[r][c] for r in top_rows for c in range(4)]
        self.play(highlight_cells(top_cells, color=GREEN), run_time=0.5)

        # Dim the rest
        bottom_rows = [0, 3]
        dim_cells = [self.d_cells[r][c] for r in bottom_rows for c in range(4)]
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in dim_cells]
        self.play(*dim_anims, run_time=0.5)

        note = Text("nlargest/nsmallest: faster than sort + head for large DataFrames",
                    font=CODE_FONT, font_size=14, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• sort_values("col") → sort by column',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• ascending=False → descending order',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• sort_values(["a","b"]) → multi-level sort',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• nlargest(n, "col") → top N rows',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• nsmallest(n, "col") → bottom N rows',
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: GroupBy →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
