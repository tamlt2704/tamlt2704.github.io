"""Shared Manim helpers for Emacs 101 visuals."""
from manim import *

BG = "#0d0d0d"
EMACS_BG = "#1e1e1e"
MODELINE_BG = "#333333"
CURSOR_COLOR = "#007acc"
REGION_COLOR = "#094771"
MINIBUFFER_BG = "#252526"
KEY_BG = "#333333"
KEY_BORDER = "#555555"
TEAL = "#4ec9b0"
YELLOW = "#e6a700"
RED = "#ff5f57"
GREEN = "#28c840"
DIM = "#888888"
FONT = "Courier New"


def emacs_frame(width=11, height=6.5, title="*scratch*"):
    """Create an Emacs-like frame with modeline and minibuffer."""
    frame = VGroup()

    # Main editing area
    editor = Rectangle(width=width, height=height - 0.8,
                       fill_color=EMACS_BG, fill_opacity=1,
                       stroke_color="#333", stroke_width=1)
    editor.move_to(UP * 0.4)

    # Modeline
    modeline = Rectangle(width=width, height=0.35,
                         fill_color=MODELINE_BG, fill_opacity=1, stroke_width=0)
    modeline.next_to(editor, DOWN, buff=0)
    mode_text = Text(f" -UUU:----F1  {title}    All L1    (Fundamental) ",
                     font=FONT, font_size=11, color=WHITE)
    mode_text.move_to(modeline.get_center())

    # Minibuffer
    mini = Rectangle(width=width, height=0.3,
                     fill_color=MINIBUFFER_BG, fill_opacity=1, stroke_width=0)
    mini.next_to(modeline, DOWN, buff=0)

    frame.add(editor, modeline, mode_text, mini)
    frame.editor = editor
    frame.modeline = modeline
    frame.mini = mini
    return frame


def key_cap(text, width=None):
    """A keyboard key cap visual."""
    label = Text(text, font=FONT, font_size=14, color=WHITE)
    w = width or max(label.width + 0.3, 0.5)
    box = RoundedRectangle(width=w, height=0.4, corner_radius=0.06,
                            fill_color=KEY_BG, fill_opacity=1,
                            stroke_color=KEY_BORDER, stroke_width=1)
    label.move_to(box.get_center())
    return VGroup(box, label)


def key_combo(keys_text):
    """Show a key combination like 'C-x C-f'."""
    parts = keys_text.split(" ")
    group = VGroup()
    for part in parts:
        cap = key_cap(part)
        group.add(cap)
    group.arrange(RIGHT, buff=0.1)
    return group


def cursor_block(char=" ", color=CURSOR_COLOR):
    """A block cursor over a character."""
    rect = Rectangle(width=0.14, height=0.22, fill_color=color,
                     fill_opacity=0.8, stroke_width=0)
    if char.strip():
        label = Text(char, font=FONT, font_size=13, color=WHITE)
        label.move_to(rect.get_center())
        return VGroup(rect, label)
    return rect


def editor_text(lines, start_pos, font_size=13, line_spacing=0.28):
    """Create a group of text lines positioned inside the editor."""
    group = VGroup()
    for i, line in enumerate(lines):
        t = Text(line, font=FONT, font_size=font_size, color=WHITE)
        t.move_to(start_pos + DOWN * i * line_spacing)
        t.align_to(start_pos, LEFT)
        group.add(t)
    return group
