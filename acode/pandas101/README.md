# Pandas 101 — Animated Video Series

A series of ~5 minute Manim videos teaching pandas fundamentals. One concept per video. Each video shows the code, then animates what happens inside the DataFrame.

## Setup

```bash
pip install manim pandas
```

Render a video:

```bash
manim -pqh ep01_dataframe.py DataFrameScene
```

## Two Versions

| Version | Style | Folder |
|---|---|---|
| **Reference** | Concept-first, clean examples | [`ep01_dataframe.py`](ep01_dataframe.py), [`ep02_read_write.py`](ep02_read_write.py), ... |
| **Story** | Karen breaks things, you fix them | [`story/`](story/README.md) |

Same concepts, different delivery. Pick whichever style you prefer.

## Episodes

| # | Concept | What You See |
|---|---|---|
| 01 | What is a DataFrame | Dict → columns, List → rows, Series vs DataFrame side by side |
| 02 | Reading & Writing Data | CSV file → `read_csv` → table appears, `head()` highlights top 5 |
| 03 | Selecting Data | `loc`/`iloc` highlight rows/cols, boolean mask filters rows |
| 04 | Adding & Removing Columns | New column slides in, `drop()` column fades out |
| 05 | Filtering Rows | Condition → mask (True/False) → matching rows glow |
| 06 | Sorting | Rows shuffle into sorted order with animation |
| 07 | GroupBy | Rows split into groups, aggregate values appear |
| 08 | Missing Data | NaN cells glow red, `fillna`/`dropna` fix them |
| 09 | Merge & Join | Two tables slide together, matching keys connect |
| 10 | Apply & Lambda | Function box processes each cell, output appears |
| 11 | Pivot Tables | Rows reorganize into pivot layout |
| 12 | Plotting | DataFrame → bar/line chart animation |

## Project Structure

```
acode/pandas101/
├── README.md
├── ep01_dataframe.py
├── ep02_read_write.py
├── ep03_selecting.py
├── ep04_add_remove_cols.py
├── ep05_filtering.py
├── ep06_sorting.py
├── ep07_groupby.py
├── ep08_missing_data.py
├── ep09_merge_join.py
├── ep10_apply.py
├── ep11_pivot.py
├── ep12_plotting.py
└── helpers.py            ← shared table rendering utilities
```

## Style Guide

- Dark background (`#1e1e1e`)
- Monospace font for code (`Courier New`)
- Table cells: dark gray (`#252526`) with white text
- Highlight color: `#4ec9b0` (teal) for selected cells
- Code appears on the left, animated table on the right
- Each video: ~5 minutes, 1920×1080, 30fps
