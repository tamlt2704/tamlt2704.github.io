"""Helper functions for common teaching patterns. Each ≤10 lines."""

from manim import *


def make_split_layout(left, right):
    """Position two panels side by side (IDE left, output right)."""
    left.shift(LEFT * 3.5)
    right.shift(RIGHT * 3.5)
    return VGroup(left, right)


def fade_highlight(scene, box):
    """Fade out a highlight box."""
    scene.play(FadeOut(box), run_time=0.3)


def arrow_to_line(scene, ide, line_num, label=""):
    """Point an arrow at a specific line in the IDE."""
    target = ide.code_block.code[line_num - 1]
    arrow = Arrow(start=RIGHT * 2, end=ORIGIN, color=YELLOW).next_to(target, LEFT)
    txt = Text(label, font_size=14, color=YELLOW).next_to(arrow, LEFT)
    scene.play(Create(arrow), Write(txt), run_time=0.5)
    return VGroup(arrow, txt)


def step_through(scene, ide, lines, voiceovers):
    """Step through lines one by one with voiceover."""
    boxes = []
    for line, voice in zip(lines, voiceovers):
        for b in boxes:
            fade_highlight(scene, b)
        boxes.clear()
        with scene.voiceover(voice):
            box = ide.highlight_lines(scene, line, line)
            boxes.append(box)
