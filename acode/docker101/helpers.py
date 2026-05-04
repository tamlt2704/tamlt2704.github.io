"""Shared Manim helpers for Docker 101 visuals."""
from manim import *

BG = "#0d0d0d"
DOCKER_BLUE = "#2496ed"
CONTAINER_GREEN = "#28c840"
CONTAINER_YELLOW = "#e6a700"
CONTAINER_RED = "#ff5f57"
IMAGE_PURPLE = "#c678dd"
VOLUME_ORANGE = "#d19a66"
NETWORK_TEAL = "#4ec9b0"
GREY_DIM = "#888888"
DARK_CELL = "#252526"
BORDER = "#3c3c3c"
FONT = "Courier New"


def docker_logo(scale=1):
    """Simple Docker whale made of rectangles."""
    whale = VGroup()
    # Body
    body = RoundedRectangle(width=1.8, height=0.9, corner_radius=0.15,
                             fill_color=DOCKER_BLUE, fill_opacity=1, stroke_width=0)
    # Containers on top (the cargo)
    for r in range(2):
        for c in range(4):
            box = Rectangle(width=0.3, height=0.2, fill_color="#1a7bc4",
                            fill_opacity=1, stroke_color=DOCKER_BLUE, stroke_width=0.5)
            box.move_to(body.get_top() + UP * (0.12 + r * 0.22) + RIGHT * (c * 0.35 - 0.52))
            whale.add(box)
    whale.add(body)
    # Tail
    tail = Triangle(fill_color=DOCKER_BLUE, fill_opacity=1, stroke_width=0)
    tail.scale(0.3).rotate(-PI / 2).next_to(body, LEFT, buff=-0.05)
    whale.add(tail)
    return whale.scale(scale)


def container_box(label="app", color=CONTAINER_GREEN, width=2, height=1.2):
    """A container visual — rounded rect with label."""
    box = RoundedRectangle(width=width, height=height, corner_radius=0.1,
                            fill_color=DARK_CELL, fill_opacity=1,
                            stroke_color=color, stroke_width=2)
    lbl = Text(label, font=FONT, font_size=16, color=color)
    lbl.move_to(box.get_center())
    return VGroup(box, lbl)


def image_layers(labels, width=3, layer_height=0.35):
    """Stack of image layers (like a cake)."""
    group = VGroup()
    colors = [IMAGE_PURPLE, "#a855f7", "#9333ea", "#7c3aed", "#6d28d9",
              "#5b21b6", "#4c1d95"]
    for i, label in enumerate(labels):
        rect = Rectangle(width=width, height=layer_height,
                         fill_color=colors[i % len(colors)], fill_opacity=0.8,
                         stroke_color=colors[i % len(colors)], stroke_width=1)
        rect.move_to([0, i * layer_height, 0])
        lbl = Text(label, font=FONT, font_size=11, color=WHITE)
        lbl.move_to(rect.get_center())
        group.add(VGroup(rect, lbl))
    group.move_to(ORIGIN)
    return group


def cmd_text(text, font_size=20):
    """Terminal command text."""
    return Text(f"$ {text}", font=FONT, font_size=font_size, color=CONTAINER_GREEN)


def section_title(text, color=DOCKER_BLUE):
    return Text(text, font=FONT, font_size=28, color=color)
