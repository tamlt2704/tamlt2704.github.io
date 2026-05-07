# Episode 12: "Save It for the Presentation"

> Run the code: `python ep12_save_export.py`

Karen: "Email me the chart. As a PNG. And a PDF. High resolution." The chart looks great on screen — now it needs to survive email, printing, and a projector. This is the final mile.

---

## Basic Save

```python
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(months, sales, color="#007acc", linewidth=2, marker="o")
ax.set_title("Monthly Sales — 2026", fontweight="bold")
plt.tight_layout()

fig.savefig("sales_chart.png")
```

That's it. One line. But the defaults (100 DPI, white background, extra whitespace) rarely match what Karen needs.

## DPI: Resolution Matters

```python
fig.savefig("sales_chart.png", dpi=72)    # Screen (small file)
fig.savefig("sales_chart.png", dpi=150)   # Email/slides
fig.savefig("sales_chart.png", dpi=300)   # Print quality
```

| DPI | Use Case | File Size |
|-----|----------|-----------|
| 72 | Web/screen only | Small |
| 150 | Slides and email | Medium |
| 300 | Print (reports, posters) | Large |

Rule of thumb: 300 DPI for anything that might be printed. 150 for everything else.

## Transparent Background

For dark slides or overlaying on images:

```python
fig.savefig("chart_transparent.png", dpi=300, transparent=True)
```

The white background disappears. The chart floats on whatever's behind it.

## Cropping Whitespace

By default, matplotlib leaves padding around the chart. Remove it:

```python
fig.savefig("chart_tight.png", bbox_inches="tight")
```

`bbox_inches="tight"` crops to the actual content. Add padding back with `pad_inches=0.1` if needed.

## Vector Formats: PDF and SVG

Raster (PNG) gets blurry when zoomed. Vector formats stay crisp at any size:

```python
# PDF — for printing and reports
fig.savefig("chart.pdf", bbox_inches="tight")

# SVG — for web and presentations
fig.savefig("chart.svg", bbox_inches="tight")
```

| Format | Best For | Scalable? |
|--------|----------|-----------|
| PNG | Email, slides, web | No (raster) |
| PDF | Print, reports | Yes (vector) |
| SVG | Web, interactive | Yes (vector) |

## The Complete Save Call

```python
fig.savefig("board_ready.png",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
            transparent=False)
```

- `facecolor="white"` — ensures white background (even with dark themes)
- `edgecolor="none"` — no border around the figure
- `bbox_inches="tight"` — crop whitespace

## Save Before Show

Important gotcha: `plt.show()` clears the figure in some backends. Always save first:

```python
fig.savefig("chart.png", dpi=300)   # Save first
plt.show()                           # Then display
```

Or use `plt.close(fig)` for batch processing (no display at all).

## Saving Multiple Figures

For batch export:

```python
for i, data in enumerate(datasets):
    fig, ax = plt.subplots()
    ax.plot(data)
    fig.savefig(f"chart_{i:02d}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)    # Free memory
```

`plt.close(fig)` is essential in loops — without it, matplotlib holds every figure in memory.

## Karen's Export Checklist

```python
# 1. PNG for email (high-res)
fig.savefig("chart.png", dpi=300, bbox_inches="tight")

# 2. PDF for printing
fig.savefig("chart.pdf", bbox_inches="tight")

# 3. Transparent PNG for dark slides
fig.savefig("chart_dark.png", dpi=300, transparent=True, bbox_inches="tight")

# 4. SVG for the website
fig.savefig("chart.svg", bbox_inches="tight")
```

---

## Exercise

Take any chart from a previous episode and export it in three formats:
1. PNG at 300 DPI with `bbox_inches="tight"` (for email)
2. PDF (for the printed report)
3. PNG with `transparent=True` (for a dark slide deck)

Bonus:
- Create a loop that generates 4 different charts and saves each as both PNG and PDF
- Use `plt.close(fig)` after each save to manage memory
- Add a source footnote at the bottom of the chart before saving

## Quick Reference

| Function | Purpose |
|----------|---------|
| `fig.savefig("file.png")` | Save as PNG |
| `dpi=300` | High resolution |
| `transparent=True` | No background |
| `bbox_inches="tight"` | Crop whitespace |
| `facecolor="white"` | Force white background |
| `fig.savefig("file.pdf")` | Save as PDF (vector) |
| `fig.savefig("file.svg")` | Save as SVG (vector) |
| `plt.close(fig)` | Close without displaying |
| `pad_inches=0.1` | Padding after tight crop |
