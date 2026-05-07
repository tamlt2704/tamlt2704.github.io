# Episode 4: "What Percentage Is Each City?"

> Run the code: `python ep04_pie_chart.py`

Karen: "The board thinks in percentages, not dollars." She wants to see the share each city contributes. A pie chart it is — and then she'll want a donut, because "pie charts are so 2010."

---

## Basic Pie Chart

```python
fig, ax = plt.subplots(figsize=(6, 6))

cities = ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
sales = [45000, 38000, 29000, 22000, 18000]
colors = ["#007acc", "#ff5f57", "#28c840", "#e6a700", "#c678dd"]

ax.pie(sales, labels=cities, colors=colors,
       autopct="%1.1f%%",       # Show percentage with 1 decimal
       startangle=90)           # Start from 12 o'clock

ax.set_title("Sales Distribution by City", fontweight="bold")
```

`autopct` is the magic parameter. The format string `"%1.1f%%"` means: one decimal place, followed by a literal `%` sign.

## Exploding a Slice

Highlight the most important slice by pulling it out:

```python
explode = [0.08, 0, 0, 0, 0]   # Pull NYC out 8%

ax.pie(sales, labels=cities, colors=colors,
       autopct="%1.1f%%",
       startangle=90,
       explode=explode,
       shadow=True,
       textprops={"fontsize": 11})
```

The `explode` list matches the data — each value is how far to pull that slice from center. `0.08` is subtle; `0.2` is dramatic.

## Donut Chart

The modern alternative to a pie chart. Same data, less ink:

```python
wedges, texts, autotexts = ax.pie(
    sales, labels=cities, colors=colors,
    autopct="%1.1f%%", startangle=90,
    wedgeprops={"width": 0.4, "edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 10},
)

# Bold the percentages
for t in autotexts:
    t.set_fontweight("bold")

# Add center text
ax.text(0, 0, f"Total\n${sum(sales):,}",
        ha="center", va="center", fontsize=14, fontweight="bold")
```

The secret: `wedgeprops={"width": 0.4}`. This makes each wedge only 40% of the radius, leaving a hole in the middle. The center text fills that hole with useful info.

## When to Use Pie/Donut

Pie charts work when:
- You have 3-6 categories (more gets unreadable)
- You want to show parts of a whole
- The audience expects percentages

They fail when:
- Categories are similar in size (hard to compare)
- You have more than 7 slices
- Precision matters (use a bar chart instead)

---

## Exercise

Create a donut chart of how you spend your time:
1. Pick 5-6 categories (coding, meetings, email, breaks, learning, etc.)
2. Use `wedgeprops={"width": 0.4}` for the donut hole
3. Add a center label showing total hours
4. Explode one slice (your biggest time sink)
5. Use `autopct` to show percentages
6. Bold the percentage text

## Quick Reference

| Function | Purpose |
|----------|---------|
| `ax.pie(values, labels=)` | Basic pie chart |
| `autopct="%1.1f%%"` | Show percentages |
| `startangle=90` | Start from top |
| `explode=[0.1, 0, ...]` | Pull out a slice |
| `shadow=True` | Drop shadow |
| `wedgeprops={"width": 0.4}` | Donut chart |
| `textprops={"fontsize": 10}` | Label font size |
| `ax.text(0, 0, s)` | Center text (donut) |
