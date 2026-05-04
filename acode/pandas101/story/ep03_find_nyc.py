"""
Karen's Spreadsheet — Episode 03: "Find All NYC Products"
Karen wants NYC products. You select the wrong column. Then learn loc, iloc, and boolean indexing.

Render: manim -pqh ep03_find_nyc.py FindNYCScene
"""
from manim import *
import sys
sys.path.append("..")
from helpers import *


class FindNYCScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.headers = ["Name", "Price", "City", "Category"]
        self.rows = [
            ["Widget A", "29.99", "NYC", "Electronics"],
            ["Widget B", "49.99", "LA", "Electronics"],
            ["Gadget C", "19.99", "Chicago", "Home"],
            ["Widget D", "39.99", "NYC", "Home"],
            ["Gadget E", "59.99", "LA", "Electronics"],
            ["Widget F", "24.99", "NYC", "Home"],
        ]
        self.the_request()
        self.the_wrong_way()
        self.select_column()
        self.boolean_mask()
        self.loc_and_iloc()
        self.recap()

    # ── Karen's request (~15s) ───────────────────
    def the_request(self):
        karen = Text('Karen: "Give me all the NYC products.\n'
                     '        Just NYC. Nothing else."',
                     font=CODE_FONT, font_size=20, color=RED, line_spacing=1.3)
        karen.move_to(ORIGIN)
        self.play(Write(karen), run_time=1.5)
        self.wait(1.5)
        self.play(FadeOut(karen))

    # ── The wrong way (~30s) ─────────────────────
    def the_wrong_way(self):
        title = Text("Your First Attempt", font=CODE_FONT, font_size=24, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.3)

        bad_code = make_code_block(
            '# You try this:\n'
            'for i in range(len(df)):\n'
            '    if df["City"][i] == "NYC":\n'
            '        print(df.iloc[i])'
        )
        bad_code.scale(0.65).move_to(ORIGIN)
        self.play(FadeIn(bad_code), run_time=0.5)
        self.wait(1)

        greg = Text('Old Greg: "A for loop? In pandas? Delete that."',
                     font=CODE_FONT, font_size=18, color=DIM)
        greg.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(greg), run_time=0.3)
        self.wait(1.5)

        # Cross it out
        cross = Line(bad_code.get_corner(UL), bad_code.get_corner(DR),
                     color=RED, stroke_width=4)
        self.play(Create(cross), run_time=0.3)
        self.wait(1)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Select a column (~40s) ───────────────────
    def select_column(self):
        title = section_title('Step 1: df["City"]')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.3)

        table, h_cells, d_cells = make_table(self.headers, self.rows, col_width=1.6)
        table.scale(0.75).move_to(RIGHT * 1.5 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('df["City"]')
        code.scale(0.7).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight City column
        city_col = [h_cells[2]] + [d_cells[r][2] for r in range(6)]
        other_cols = ([h_cells[i] for i in [0,1,3]] +
                      [d_cells[r][c] for r in range(6) for c in [0,1,3]])

        self.play(highlight_cells(city_col, color=TEAL), run_time=0.5)
        dim_anims = [cell[0].animate.set_opacity(0.15) for cell in other_cols]
        self.play(*dim_anims, run_time=0.3)

        # Show the extracted series
        series_vals = VGroup()
        cities = ["NYC", "LA", "Chicago", "NYC", "LA", "NYC"]
        for i, city in enumerate(cities):
            t = Text(city, font=CODE_FONT, font_size=16, color=WHITE)
            t.move_to(LEFT * 4 + DOWN * (0.8 + i * 0.35))
            series_vals.add(t)

        series_label = Text("→ Series:", font=CODE_FONT, font_size=14, color=DIM)
        series_label.move_to(LEFT * 4 + DOWN * 0.4)
        self.play(FadeIn(series_label),
                  LaggedStart(*[FadeIn(t) for t in series_vals], lag_ratio=0.08),
                  run_time=0.6)
        self.wait(1.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Boolean mask (~70s) ──────────────────────
    def boolean_mask(self):
        title = section_title('Step 2: df["City"] == "NYC"')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.3)

        table, h_cells, d_cells = make_table(self.headers, self.rows, col_width=1.6)
        table.scale(0.75).move_to(RIGHT * 1 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.5)

        code = make_code_block('mask = df["City"] == "NYC"')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show mask values appearing next to each row
        cities = ["NYC", "LA", "Chicago", "NYC", "LA", "NYC"]
        mask_group = VGroup()
        for i, city in enumerate(cities):
            is_nyc = city == "NYC"
            color = GREEN if is_nyc else RED
            val = "True" if is_nyc else "False"
            t = Text(val, font=CODE_FONT, font_size=14, color=color)
            t.next_to(d_cells[i][-1], RIGHT, buff=0.3)
            mask_group.add(t)

        mask_label = Text("mask", font=CODE_FONT, font_size=12, color=DIM)
        mask_label.next_to(mask_group, UP, buff=0.15)

        self.play(FadeIn(mask_label))
        for t in mask_group:
            self.play(FadeIn(t), run_time=0.15)
        self.wait(1)

        # Step 3: Apply the mask
        code2 = make_code_block('nyc = df[mask]  # or df[df["City"] == "NYC"]')
        code2.scale(0.6).to_edge(LEFT, buff=0.3).shift(DOWN * 0.5)
        self.play(FadeIn(code2), run_time=0.3)
        self.wait(0.5)

        # Highlight True rows (0, 3, 5)
        true_rows = [0, 3, 5]
        false_rows = [1, 2, 4]

        true_cells = [d_cells[r][c] for r in true_rows for c in range(4)]
        false_cells = [d_cells[r][c] for r in false_rows for c in range(4)]

        self.play(highlight_cells(true_cells, color=GREEN), run_time=0.5)

        # False rows fade out
        fade_anims = []
        for r in false_rows:
            for c in range(4):
                fade_anims.append(d_cells[r][c].animate.set_opacity(0.1))
            fade_anims.append(mask_group[r].animate.set_opacity(0.1))
        self.play(*fade_anims, run_time=0.5)

        # Result count
        result = Text("→ 3 rows match", font=CODE_FONT, font_size=20, color=GREEN)
        result.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(result), run_time=0.3)
        self.wait(2)

        # Karen is happy
        karen = Text('Karen: "Perfect. Now sort them by price."',
                     font=CODE_FONT, font_size=16, color=RED)
        karen.next_to(result, DOWN, buff=0.2)
        self.play(FadeIn(karen), run_time=0.3)
        self.wait(1)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── loc vs iloc (~60s) ───────────────────────
    def loc_and_iloc(self):
        title = section_title("Bonus: loc vs iloc")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.3)

        table, h_cells, d_cells = make_table(self.headers, self.rows, col_width=1.6)
        table.scale(0.7).move_to(RIGHT * 1.5 + DOWN * 0.5)
        self.play(FadeIn(table), run_time=0.4)

        # loc example
        code_loc = make_code_block('df.loc[0, "City"]  # → "NYC"')
        code_loc.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 0.3)
        self.play(FadeIn(code_loc), run_time=0.3)

        target = d_cells[0][2]
        self.play(highlight_cells([target], color=TEAL), run_time=0.3)

        loc_note = Text("loc → by label (row 0, column 'City')",
                        font=CODE_FONT, font_size=14, color=TEAL)
        loc_note.to_edge(LEFT, buff=0.3).shift(DOWN * 0.5)
        self.play(FadeIn(loc_note), run_time=0.3)
        self.wait(1.5)

        self.play(unhighlight_cells([target]), FadeOut(code_loc),
                  FadeOut(loc_note), run_time=0.2)

        # iloc example
        code_iloc = make_code_block("df.iloc[0, 2]     # → same thing")
        code_iloc.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 0.3)
        self.play(FadeIn(code_iloc), run_time=0.3)

        self.play(highlight_cells([target], color=YELLOW), run_time=0.3)

        iloc_note = Text("iloc → by integer position (row 0, col 2)",
                         font=CODE_FONT, font_size=14, color=YELLOW)
        iloc_note.to_edge(LEFT, buff=0.3).shift(DOWN * 0.5)
        self.play(FadeIn(iloc_note), run_time=0.3)
        self.wait(1.5)

        # Comparison
        self.play(unhighlight_cells([target]), FadeOut(code_iloc),
                  FadeOut(iloc_note), run_time=0.2)

        comp = VGroup(
            Text("loc  → labels:   loc[0, 'City']", font=CODE_FONT,
                 font_size=18, color=TEAL),
            Text("iloc → integers: iloc[0, 2]", font=CODE_FONT,
                 font_size=18, color=YELLOW),
            Text("Both get the same cell — different addressing",
                 font=CODE_FONT, font_size=14, color=DIM),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        comp.to_edge(LEFT, buff=0.3).shift(DOWN * 1.5)
        self.play(FadeIn(comp), run_time=0.5)
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (~15s) ─────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• df["col"] selects a column (Series)',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df["col"] == "val" creates a boolean mask',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• df[mask] filters rows where mask is True",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• loc = label-based, iloc = integer-based",
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• Never use a for loop to filter pandas data",
                 font=CODE_FONT, font_size=17, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text('Next: Karen says "Add a tax column" →',
                       font=CODE_FONT, font_size=18, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
