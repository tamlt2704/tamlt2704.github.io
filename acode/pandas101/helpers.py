"""Shared Manim utilities for rendering pandas-style tables."""
from manim import *

# ── Colors ───────────────────────────────────────
BG = "#1e1e1e"
CELL_BG = "#252526"
HEADER_BG = "#333333"
BORDER = "#3c3c3c"
TEAL = "#4ec9b0"
YELLOW = "#e6a700"
RED = "#ff5f57"
GREEN = "#28c840"
BLUE = "#007acc"
DIM = "#888888"
CODE_FONT = "Courier New"


def make_cell(text, width=1.8, height=0.5, bg=CELL_BG, text_color=WHITE, font_size=20):
    """Create a single table cell."""
    rect = Rectangle(width=width, height=height, fill_color=bg,
                     fill_opacity=1, stroke_color=BORDER, stroke_width=1)
    label = Text(str(text), font=CODE_FONT, font_size=font_size, color=text_color)
    label.move_to(rect.get_center())
    return VGroup(rect, label)


def make_table(headers, rows, col_width=1.8, row_height=0.5, header_bg=HEADER_BG):
    """Build a full table from headers and row data.

    Returns (table_group, header_cells, data_cells)
    where data_cells[row][col] is a VGroup(rect, label).
    """
    table = VGroup()
    header_cells = []
    data_cells = []

    # Header row
    for j, h in enumerate(headers):
        cell = make_cell(h, width=col_width, height=row_height,
                         bg=header_bg, text_color=TEAL, font_size=18)
        cell.move_to([j * col_width, 0, 0])
        header_cells.append(cell)
        table.add(cell)

    # Data rows
    for i, row in enumerate(rows):
        row_cells = []
        for j, val in enumerate(row):
            cell = make_cell(val, width=col_width, height=row_height)
            cell.move_to([j * col_width, -(i + 1) * row_height, 0])
            row_cells.append(cell)
            table.add(cell)
        data_cells.append(row_cells)

    # Center the whole table
    table.move_to(ORIGIN)
    return table, header_cells, data_cells


def make_index_col(labels, col_width=0.8, row_height=0.5, start_y=0):
    """Create an index column (row labels on the left)."""
    group = VGroup()
    cells = []
    for i, label in enumerate(labels):
        cell = make_cell(str(label), width=col_width, height=row_height,
                         bg=HEADER_BG, text_color=YELLOW, font_size=16)
        cell.move_to([0, start_y - (i + 1) * row_height, 0])
        cells.append(cell)
        group.add(cell)
    return group, cells


def make_code_block(code_text, font_size=18):
    """Create a code block with monospace font."""
    code = Code(
        code=code_text,
        language="python",
        font_size=font_size,
        background="rectangle",
        background_stroke_color=BORDER,
        insert_line_no=False,
        style="monokai",
    )
    return code


def highlight_cells(cells, color=TEAL, run_time=0.3):
    """Return animations to highlight a list of cells."""
    anims = []
    for cell in cells:
        rect = cell[0]  # the Rectangle
        anims.append(rect.animate.set_fill(color, opacity=0.8))
    return AnimationGroup(*anims, run_time=run_time)


def unhighlight_cells(cells, color=CELL_BG, run_time=0.3):
    """Return animations to remove highlight from cells."""
    anims = []
    for cell in cells:
        rect = cell[0]
        anims.append(rect.animate.set_fill(color, opacity=1))
    return AnimationGroup(*anims, run_time=run_time)


def section_title(text, font_size=36):
    """Create a section title."""
    return Text(text, font=CODE_FONT, font_size=font_size, color=TEAL)
