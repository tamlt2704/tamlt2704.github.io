"""
Episode 12: Plotting
~5 min | Concepts: df.plot(), kind="bar"/"line"/"hist"/"scatter", subplots

Render: manim -pqh ep12_plotting.py PlottingScene
"""
from manim import *
from helpers import *


class PlottingScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.bar_plot()
        self.line_plot()
        self.hist_plot()
        self.scatter_plot()
        self.subplots_section()
        self.outro()

    # ── Intro (~15s) ─────────────────────────────
    def intro(self):
        title = Text("Pandas 101", font=CODE_FONT, font_size=48, color=TEAL)
        subtitle = Text("Episode 12: Plotting",
                        font=CODE_FONT, font_size=24, color=DIM)
        subtitle.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ── Bar plot (~60s) ──────────────────────────
    def bar_plot(self):
        title = section_title('df.plot(kind="bar")')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show source data
        headers = ["Name", "Sales"]
        rows = [["Alice", "120"], ["Bob", "85"], ["Charlie", "150"],
                ["Diana", "95"], ["Eve", "130"]]
        table, h, d = make_table(headers, rows, col_width=1.5)
        table.scale(0.6).move_to(LEFT * 3.5 + DOWN * 0.3)
        self.play(FadeIn(table), run_time=0.3)

        code = make_code_block('df.plot(kind="bar", x="Name", y="Sales")')
        code.scale(0.6).to_edge(UP, buff=1.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Create bar chart on the right
        values = [120, 85, 150, 95, 130]
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        max_val = max(values)
        bar_height_scale = 2.5 / max_val

        bars = VGroup()
        labels = VGroup()
        for i, (name, val) in enumerate(zip(names, values)):
            bar = Rectangle(
                width=0.5, height=val * bar_height_scale,
                fill_color=TEAL, fill_opacity=0.8, stroke_width=1,
                stroke_color=BORDER
            )
            bar.move_to(RIGHT * (0.5 + i * 0.7) + DOWN * 1.5)
            bar.align_to(DOWN * 2.8, DOWN)
            bars.add(bar)

            label = Text(name[0], font=CODE_FONT, font_size=12, color=DIM)
            label.next_to(bar, DOWN, buff=0.1)
            labels.add(label)

        # Animate bars growing from bottom
        self.play(LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars],
                              lag_ratio=0.15), run_time=1.5)
        self.play(FadeIn(labels), run_time=0.3)

        # Add axis
        x_axis = Line(LEFT * 0.1 + DOWN * 2.8, RIGHT * 4 + DOWN * 2.8,
                      color=DIM, stroke_width=1)
        y_axis = Line(LEFT * 0.1 + DOWN * 2.8, LEFT * 0.1 + UP * 0.2,
                      color=DIM, stroke_width=1)
        self.play(Create(x_axis), Create(y_axis), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Line plot (~50s) ─────────────────────────
    def line_plot(self):
        title = section_title('df.plot(kind="line")')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block('df.plot(kind="line", x="Month", y="Revenue")')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 1)
        self.play(FadeIn(code), run_time=0.3)

        # Create line chart
        points_data = [(0, 1.0), (1, 1.5), (2, 1.3), (3, 2.0),
                       (4, 2.2), (5, 1.8)]
        scale_x = 0.8
        scale_y = 1.2
        offset = RIGHT * 1 + DOWN * 1

        dots = VGroup()
        for x, y in points_data:
            dot = Dot(point=[x * scale_x + offset[0],
                             y * scale_y + offset[1], 0],
                      radius=0.06, color=TEAL)
            dots.add(dot)

        # Create line connecting dots
        line_points = [dot.get_center() for dot in dots]
        line = VMobject(color=TEAL, stroke_width=2)
        line.set_points_smoothly(line_points)

        # Axes
        ax_origin = [offset[0] - 0.2, offset[1] - 0.2, 0]
        x_ax = Line(ax_origin, [ax_origin[0] + 5 * scale_x, ax_origin[1], 0],
                    color=DIM, stroke_width=1)
        y_ax = Line(ax_origin, [ax_origin[0], ax_origin[1] + 3 * scale_y, 0],
                    color=DIM, stroke_width=1)

        self.play(Create(x_ax), Create(y_ax), run_time=0.3)
        self.play(Create(line), run_time=1)
        self.play(FadeIn(dots), run_time=0.3)

        note = Text("Line plots are great for time series data",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Histogram (~50s) ─────────────────────────
    def hist_plot(self):
        title = section_title('df.plot(kind="hist")')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block('df["Age"].plot(kind="hist", bins=5)')
        code.scale(0.65).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Create histogram bars (frequency distribution)
        bin_heights = [2, 5, 8, 4, 1]  # frequencies for age bins
        bin_labels = ["20-25", "25-30", "30-35", "35-40", "40-45"]
        max_h = max(bin_heights)
        h_scale = 2.0 / max_h

        hist_bars = VGroup()
        for i, height in enumerate(bin_heights):
            bar = Rectangle(
                width=0.8, height=height * h_scale,
                fill_color=BLUE, fill_opacity=0.7,
                stroke_color=WHITE, stroke_width=1
            )
            bar.move_to(RIGHT * (1 + i * 0.85) + DOWN * 1)
            bar.align_to(DOWN * 2.5, DOWN)
            hist_bars.add(bar)

        self.play(LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in hist_bars],
                              lag_ratio=0.1), run_time=1)

        # Bin labels
        for i, label in enumerate(bin_labels):
            t = Text(label, font=CODE_FONT, font_size=10, color=DIM)
            t.next_to(hist_bars[i], DOWN, buff=0.1)
            self.add(t)

        note = Text("Histograms show the distribution of a single variable",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Scatter plot (~50s) ──────────────────────
    def scatter_plot(self):
        title = section_title('df.plot(kind="scatter")')
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block('df.plot(kind="scatter", x="Age", y="Salary")')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 1)
        self.play(FadeIn(code), run_time=0.3)

        # Create scatter points
        scatter_data = [(25, 70), (30, 80), (35, 90), (28, 75), (32, 85),
                        (27, 72), (33, 88), (29, 77), (31, 82), (36, 95)]
        offset = RIGHT * 0.5 + DOWN * 2

        dots = VGroup()
        for x, y in scatter_data:
            dot = Dot(point=[(x - 25) * 0.15 + offset[0],
                             (y - 65) * 0.03 + offset[1], 0],
                      radius=0.08, color=TEAL, fill_opacity=0.8)
            dots.add(dot)

        ax_x = Line(offset + LEFT * 0.3, offset + RIGHT * 2, color=DIM, stroke_width=1)
        ax_y = Line(offset + DOWN * 0.3, offset + UP * 2.5, color=DIM, stroke_width=1)
        self.play(Create(ax_x), Create(ax_y), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(dot, scale=0.5) for dot in dots],
                              lag_ratio=0.08), run_time=1)

        note = Text("Scatter plots reveal relationships between two variables",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Subplots (~40s) ──────────────────────────
    def subplots_section(self):
        title = section_title("Subplots")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        code = make_code_block('df.plot(subplots=True, layout=(2, 2),\n        figsize=(10, 8))')
        code.scale(0.6).to_edge(LEFT, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(code), run_time=0.3)
        self.wait(0.5)

        # Show 2x2 grid of mini plots
        positions = [LEFT * 1.5 + UP * 0.5, RIGHT * 1.5 + UP * 0.5,
                     LEFT * 1.5 + DOWN * 1.5, RIGHT * 1.5 + DOWN * 1.5]
        labels = ["Sales", "Revenue", "Costs", "Profit"]
        colors = [TEAL, YELLOW, RED, GREEN]

        subplots = VGroup()
        for pos, label, color in zip(positions, labels, colors):
            frame = Rectangle(width=2.2, height=1.5, stroke_color=BORDER,
                              stroke_width=1, fill_opacity=0).move_to(pos)
            mini_bars = VGroup(*[
                Rectangle(width=0.3, height=0.3 + j * 0.2, fill_color=color,
                          fill_opacity=0.7, stroke_width=0
                ).move_to(pos + LEFT * 0.6 + RIGHT * j * 0.4).align_to(
                    pos + DOWN * 0.6, DOWN)
                for j in range(4)
            ])
            plot_title = Text(label, font=CODE_FONT, font_size=11, color=DIM)
            plot_title.next_to(frame, UP, buff=0.05)
            subplots.add(VGroup(frame, mini_bars, plot_title))

        self.play(LaggedStart(*[FadeIn(sp) for sp in subplots],
                              lag_ratio=0.2), run_time=1.5)

        note = Text("subplots=True creates one plot per column",
                    font=CODE_FONT, font_size=15, color=DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Outro (~15s) ─────────────────────────────
    def outro(self):
        recap = VGroup(
            Text("Recap:", font=CODE_FONT, font_size=28, color=TEAL),
            Text('• df.plot(kind="bar") → bar chart',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df.plot(kind="line") → line chart',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df.plot(kind="hist") → histogram',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text('• df.plot(kind="scatter") → scatter plot',
                 font=CODE_FONT, font_size=17, color=WHITE),
            Text("• subplots=True → one plot per column",
                 font=CODE_FONT, font_size=17, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.3)
                                for line in recap], lag_ratio=0.15), run_time=1.5)
        self.wait(3)

        next_ep = Text("Series complete! 🎉",
                       font=CODE_FONT, font_size=20, color=TEAL)
        next_ep.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(next_ep), run_time=0.3)
        self.wait(2)
