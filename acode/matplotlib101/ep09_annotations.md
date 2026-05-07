# Episode 9: "Add Context"

> Run the code: `python ep09_annotations.py`

Karen: "The board wants confidence intervals. And highlight the anomaly in March." Raw data isn't enough — you need to tell a story. Annotations, reference lines, and shaded regions turn a chart into an explanation.

---

## Error Bars

Show uncertainty or confidence intervals around each data point:

```python
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
sales = [12000, 15000, 9000, 18000, 22000, 19000]
errors = [1500, 1200, 3000, 1800, 2000, 1600]

ax.errorbar(months, sales, yerr=errors,
            fmt="o-",            # Line with dots
            color="#007acc",
            ecolor="#007acc",    # Error bar color
            elinewidth=1.5,
            capsize=4,           # Cap width
            capthick=1.5,
            linewidth=2,
            markersize=6)
```

`yerr` can be a single value (same error everywhere), a list (different per point), or a 2D array (asymmetric errors: `[[lower], [upper]]`).

## Annotations with Arrows

Point out something specific and explain it:

```python
ax.annotate(
    "Supply chain\ndisruption",
    xy=("Mar", 9000),              # Point being annotated
    xytext=("Apr", 6000),          # Where the text sits
    fontsize=10, color="#ff5f57",
    arrowprops=dict(arrowstyle="->", color="#ff5f57", lw=1.5),
    bbox=dict(boxstyle="round,pad=0.3",
              facecolor="#2a0a0a", edgecolor="#ff5f57"),
)
```

Key parameters:
- `xy` — the point the arrow points TO
- `xytext` — where the label text is placed
- `arrowprops` — arrow style and color
- `bbox` — background box around the text

### Arrow Styles

| Style | Look |
|-------|------|
| `"->"` | Simple arrow |
| `"fancy"` | Curved fancy arrow |
| `"wedge"` | Wide wedge |
| `"-"` | Line (no arrowhead) |

## Horizontal and Vertical Reference Lines

```python
# Target line
ax.axhline(y=15000, color="#28c840", linestyle="--",
           linewidth=1, alpha=0.7, label="Target: $15,000")

# Vertical event marker
ax.axvline(x="Mar", color="#ff5f57", linestyle=":",
           linewidth=1, alpha=0.5, label="Incident")
```

Reference lines give context: "Here's the target," "Here's when the event happened."

## Shaded Regions

Highlight a range (acceptable zone, confidence band, time period):

```python
# Acceptable range
ax.fill_between(months, 13000, 17000, alpha=0.08, color="#28c840",
                label="Target range")
```

For time-based shading (e.g., "holiday season"):

```python
ax.axvspan("Nov", "Dec", alpha=0.1, color="#e6a700", label="Holiday")
```

## Text Boxes

Place explanatory text anywhere on the chart:

```python
ax.text(0.02, 0.95, "Note: March data\nincludes corrections",
        transform=ax.transAxes,    # Position relative to axes (0-1)
        fontsize=9, color="grey",
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
```

`transform=ax.transAxes` means coordinates are 0-1 relative to the plot area, not data values. `(0, 0)` is bottom-left, `(1, 1)` is top-right.

## Combining Annotations

The real power is layering these together:

```python
# 1. Plot the data
ax.plot(months, sales, color="#007acc", linewidth=2, marker="o")

# 2. Reference line (target)
ax.axhline(y=15000, color="#28c840", linestyle="--", label="Target")

# 3. Shaded acceptable range
ax.fill_between(months, 13000, 17000, alpha=0.08, color="#28c840")

# 4. Annotate the anomaly
ax.annotate("Disruption", xy=("Mar", 9000), xytext=("Apr", 6000),
            arrowprops=dict(arrowstyle="->", color="#ff5f57"))

# 5. Legend ties it together
ax.legend(loc="upper left")
```

---

## Exercise

Create a line chart with full annotations:
1. Plot 6-12 months of data
2. Add a horizontal dashed line for the "target" or "average"
3. Shade a region showing the acceptable range (±10% of target)
4. Annotate the highest point with an arrow and label
5. Annotate the lowest point as a "problem area"
6. Add a text box in the corner with a note

## Quick Reference

| Function | Purpose |
|----------|---------|
| `ax.errorbar(x, y, yerr=)` | Error bars |
| `capsize=4` | Error bar cap width |
| `ax.annotate(text, xy=, xytext=)` | Arrow annotation |
| `arrowprops=dict(arrowstyle="->")` | Arrow style |
| `bbox=dict(boxstyle="round")` | Text background box |
| `ax.axhline(y=)` | Horizontal line |
| `ax.axvline(x=)` | Vertical line |
| `ax.fill_between(x, y1, y2)` | Shaded region |
| `ax.axvspan(x1, x2)` | Vertical shaded band |
| `ax.text(x, y, s, transform=ax.transAxes)` | Positioned text |
