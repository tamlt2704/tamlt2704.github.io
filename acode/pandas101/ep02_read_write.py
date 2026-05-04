"""
Episode 02: Reading & Writing Data
~5 min | Concepts: read_csv, to_csv, head, tail, shape, info

Render: manim -pqh ep02_read_write.py ReadWriteScene
"""
from manim import *
from helpers import *


class ReadWriteScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.read_csv_section()
        self.head_tail_section()
        self.shape_section()
        self.to_csv_section()
        self.outro()

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 2: Reading & Writing Data",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── read_csv (~80s) ──────────────────────────
    def read_csv_section(self):
        title = section_title("pd.read_csv()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show a CSV file (raw text)
        csv_text = Text(
            "Name,Age,City,Salary\n"
            "Alice,25,NYC,70000\n"
            "Bob,30,LA,80000\n"
            "Charlie,35,Chicago,90000\n"
            "Diana,28,NYC,75000\n"
            "Eve,32,LA,85000",
            font=CODE_FONT, font_size=16, color=DIM
        )
        csv_box = SurroundingRectangle(csv_text, color=BORDER, buff=0.3,
                                        fill_color="#0d0d0d", fill_opacity=1)
        csv_label = Text("employees.csv", font=CODE_FONT, font_size=14, color=YELLOW)
        csv_group = VGroup(csv_box, csv_text)
        csv_label.next_to(csv_box, UP, buff=0.1)
        csv_group.add(csv_label)
        csv_group.to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)

        self.play(FadeIn(csv_group), run_time=0.5)
        self.wait(1)

        # Show code
        code = make_code_block('df = pd.read_csv("employees.csv")')
        code.scale(0.7).move_to(UP * 0.5 + RIGHT * 3)
        self.play(FadeIn(code), run_time=0.5)
        self.wait(0.5)

        # Arrow from CSV to table
        arrow = Arrow(start=csv_group.get_right(), end=RIGHT * 1.5,
                      color=TEAL, buff=0.2)
        self.play(GrowArrow(arrow), run_time=0.5)

        # Build the DataFrame table
        headers = ["Name", "Age", "City", "Salary"]
        rows = [
            ["Alice", "25", "NYC", "70000"],
            ["Bob", "30", "LA", "80000"],
            ["Charlie", "35", "Chicago", "90000"],
            ["Diana", "28", "NYC", "75000"],
            ["Eve", "32", "LA", "85000"],
        ]
        table, h_cells, d_cells = make_table(headers, rows, col_width=1.5)
        table.scale(0.75).move_to(RIGHT * 3 + DOWN * 1.2)

        # Animate table appearing
        self.play(LaggedStart(*[FadeIn(c) for c in h_cells], lag_ratio=0.08),
                  run_time=0.4)
        for row in d_cells:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in row],
                                  lag_ratio=0.05), run_time=0.3)

        note = Text("CSV → DataFrame: each row becomes a row, headers become columns",
                     font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        # Store for reuse
        self.table = table
        self.h_cells = h_cells
        self.d_cells = d_cells
        self.play(*[FadeOut(m) for m in [csv_group, code, arrow, note, title]])

    # ── head() and tail() (~60s) ─────────────────
    def head_tail_section(self):
        title = section_title("head() and tail()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Reposition table
        self.table.move_to(RIGHT * 1 + DOWN * 0.3)

        # head(3) — highlight first 3 rows
        code_head = make_code_block("df.head(3)")
        code_head.scale(0.7).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.play(FadeIn(code_head), run_time=0.3)
        self.wait(0.5)

        # Highlight top 3 rows
        top3 = [cell for row in self.d_cells[:3] for cell in row]
        self.play(highlight_cells(top3, color=TEAL), run_time=0.5)

        note = Text("head(n) → first n rows (default 5)",
                     font=CODE_FONT, font_size=16, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(unhighlight_cells(top3), FadeOut(note), FadeOut(code_head),
                  run_time=0.3)

        # tail(2) — highlight last 2 rows
        code_tail = make_code_block("df.tail(2)")
        code_tail.scale(0.7).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.play(FadeIn(code_tail), run_time=0.3)
        self.wait(0.5)

        bottom2 = [cell for row in self.d_cells[-2:] for cell in row]
        self.play(highlight_cells(bottom2, color=YELLOW), run_time=0.5)

        note2 = Text("tail(n) → last n rows (default 5)",
                      font=CODE_FONT, font_size=16, color=DIM)
        note2.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note2), run_time=0.3)
        self.wait(2)

        self.play(unhighlight_cells(bottom2, color=CELL_BG),
                  FadeOut(note2), FadeOut(code_tail), run_time=0.3)
        self.play(FadeOut(title))

    # ── shape (~40s) ─────────────────────────────
    def shape_section(self):
        title = section_title("shape")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block("df.shape  # → (5, 4)")
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Highlight all rows with count
        row_count = Text("5 rows", font=CODE_FONT, font_size=20, color=YELLOW)
        col_count = Text("4 columns", font=CODE_FONT, font_size=20, color=TEAL)

        # Count rows: flash each row
        for i, row in enumerate(self.d_cells):
            self.play(highlight_cells(row, color="#094771"), run_time=0.15)
        row_count.move_to(LEFT * 4 + DOWN * 1)
        self.play(FadeIn(row_count), run_time=0.3)

        # Reset
        all_cells = [c for row in self.d_cells for c in row]
        self.play(unhighlight_cells(all_cells), run_time=0.2)

        # Count columns: flash each column
        for j in range(4):
            col_cells = [self.d_cells[i][j] for i in range(5)]
            self.play(highlight_cells(col_cells, color="#094771"), run_time=0.15)
        col_count.move_to(LEFT * 4 + DOWN * 1.6)
        self.play(FadeIn(col_count), run_time=0.3)

        # Reset
        self.play(unhighlight_cells(all_cells), run_time=0.2)

        # Show result
        result = Text("(5, 4)", font=CODE_FONT, font_size=36, color=GREEN)
        result.move_to(LEFT * 4 + DOWN * 2.5)
        self.play(FadeIn(result), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in [title, code, row_count, col_count, result]])

    # ── to_csv (~40s) ────────────────────────────
    def to_csv_section(self):
        title = section_title("to_csv()")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block('df.to_csv("output.csv", index=False)')
        code.scale(0.7).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Arrow from table to file
        arrow = Arrow(start=self.table.get_left() + LEFT * 0.2,
                      end=LEFT * 3.5 + DOWN * 1.5, color=TEAL, buff=0.2)
        self.play(GrowArrow(arrow), run_time=0.5)

        # Show output file
        file_box = Rectangle(width=3, height=1.5, fill_color="#0d0d0d",
                             fill_opacity=1, stroke_color=BORDER)
        file_box.move_to(LEFT * 3.5 + DOWN * 2.5)
        file_label = Text("output.csv", font=CODE_FONT, font_size=16, color=GREEN)
        file_label.move_to(file_box.get_center())
        self.play(FadeIn(file_box), Write(file_label), run_time=0.5)

        note = Text("DataFrame → CSV file (index=False skips row numbers)",
                     font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text("• pd.read_csv() → load CSV into DataFrame",
                 font=CODE_FONT, font_size=18, color=WHITE),
            Text("• df.head(n) → first n rows",
                 font=CODE_FONT, font_size=18, color=WHITE),
            Text("• df.tail(n) → last n rows",
                 font=CODE_FONT, font_size=18, color=WHITE),
            Text("• df.shape → (rows, columns)",
                 font=CODE_FONT, font_size=18, color=WHITE),
            Text("• df.to_csv() → save to CSV file",
                 font=CODE_FONT, font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Next: Selecting Data →",
                       font=CODE_FONT, font_size=20, color=DIM)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
