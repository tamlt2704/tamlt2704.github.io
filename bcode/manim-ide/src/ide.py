"""
IDE Component for Manim — VSCode-like code editor with highlighting.
Each function is ≤10 lines. Compose them to build teaching scenes.
"""

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService


class IDE(VGroup):
    """A VSCode-like code panel with title bar, line numbers, and syntax highlighting."""

    def __init__(self, code="", language="python", title="main.py", **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.language = language
        self.code_str = code
        self._build()

    def _build(self):
        """Assemble the IDE: background + title bar + code block."""
        self.bg = self._make_bg()
        self.title_bar = self._make_title_bar()
        self.code_block = self._make_code(self.code_str)
        self.add(self.bg, self.title_bar, self.code_block)

    def _make_bg(self):
        """Dark rounded rectangle as the editor background."""
        bg = RoundedRectangle(
            corner_radius=0.15, width=7, height=5,
            fill_color="#1e1e1e", fill_opacity=1, stroke_color="#3c3c3c"
        )
        return bg

    def _make_title_bar(self):
        """Top bar with filename and traffic light dots."""
        bar = Rectangle(width=7, height=0.4, fill_color="#2d2d2d", fill_opacity=1, stroke_width=0)
        bar.move_to(self.bg.get_top() - DOWN * 0.2)
        dots = self._traffic_dots().move_to(bar.get_left() + RIGHT * 0.5)
        label = Text(self.title_text, font_size=16, color=WHITE).move_to(bar)
        return VGroup(bar, dots, label)

    def _traffic_dots(self):
        """Red/yellow/green dots like macOS window controls."""
        colors = ["#ff5f57", "#febc2e", "#28c840"]
        dots = VGroup(*[Dot(radius=0.06, color=c) for c in colors])
        dots.arrange(RIGHT, buff=0.12)
        return dots

    def _make_code(self, code_str):
        """Syntax-highlighted code block positioned inside the editor."""
        code = Code(
            code=code_str, language=self.language, font_size=14,
            background="rectangle", insert_line_no=True,
            style="monokai", background_stroke_width=0,
        )
        code.background_mobject.set_opacity(0)
        code.move_to(self.bg.get_center() + DOWN * 0.15)
        code.scale_to_fit_width(self.bg.width - 0.6)
        return code

    def highlight_lines(self, scene, start, end, color=YELLOW):
        """Add a highlight rectangle over specific lines."""
        lines = self.code_block.code[start - 1:end]
        box = SurroundingRectangle(
            lines, color=color, fill_opacity=0.15, buff=0.05
        )
        scene.play(Create(box), run_time=0.5)
        return box

    def change_code(self, scene, new_code):
        """Animate swapping the code content."""
        new_block = self._make_code(new_code)
        scene.play(FadeOut(self.code_block), run_time=0.3)
        self.code_block = new_block
        self.add(new_block)
        scene.play(FadeIn(new_block), run_time=0.3)

    def type_line(self, scene, line_text, position=-1):
        """Animate typing a new line at the given position."""
        typed = Text(line_text, font="Monospace", font_size=14, color=GREEN)
        typed.next_to(self.code_block, DOWN, buff=0.1).align_to(self.code_block, LEFT)
        scene.play(AddTextLetterByLetter(typed, time_per_char=0.05))
        return typed


class OutputPanel(VGroup):
    """Right-side output panel showing results, visualizations, or terminal output."""

    def __init__(self, title="Output", **kwargs):
        super().__init__(**kwargs)
        self.bg = RoundedRectangle(
            corner_radius=0.15, width=5.5, height=5,
            fill_color="#0d1117", fill_opacity=1, stroke_color="#30363d"
        )
        label = Text(title, font_size=16, color=GRAY).move_to(self.bg.get_top() + DOWN * 0.25)
        self.add(self.bg, label)

    def show_text(self, scene, text, color=GREEN):
        """Display text output in the panel."""
        output = Text(text, font_size=18, color=color)
        output.move_to(self.bg.get_center())
        scene.play(Write(output), run_time=0.5)
        return output

    def show_array(self, scene, values, color=BLUE):
        """Display an array visualization."""
        boxes = VGroup(*[
            VGroup(
                Square(side_length=0.5, color=color),
                Text(str(v), font_size=16, color=WHITE)
            ) for v in values
        ]).arrange(RIGHT, buff=0.05)
        boxes.move_to(self.bg.get_center())
        scene.play(Create(boxes), run_time=0.8)
        return boxes


# --- Demo Scene ---

class IDEDemo(VoiceoverScene):
    """Example scene: Two Sum LeetCode problem."""

    def construct(self):
        self.set_speech_service(GTTSService())

        code = '''def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i'''

        # Layout: IDE left, Output right
        ide = IDE(code=code, title="two_sum.py")
        output = OutputPanel(title="Visualization")
        ide.shift(LEFT * 3.5)
        output.shift(RIGHT * 3.5)

        with self.voiceover("Let's solve Two Sum with a hash map approach."):
            self.play(FadeIn(ide), FadeIn(output))

        with self.voiceover("We use a dictionary to store numbers we've seen."):
            box = ide.highlight_lines(self, 2, 2)

        with self.voiceover("For each number, we check if the complement exists."):
            self.play(FadeOut(box))
            ide.highlight_lines(self, 4, 6, color=BLUE)

        # Show array on the right
        with self.voiceover("Given nums equals 2, 7, 11, 15 and target 9:"):
            output.show_array(self, [2, 7, 11, 15])

        with self.voiceover("The answer is indices 0 and 1."):
            output.show_text(self, "→ [0, 1]", color=GREEN)

        self.wait(2)
