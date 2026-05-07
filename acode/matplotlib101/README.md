# Matplotlib 101 — "Karen Needs a Chart"

Captain Deadline has a board meeting every Friday. Karen needs charts. You have data. matplotlib is the only thing standing between you and the weekend.

Each episode: Karen asks for a chart → you build it → she asks for changes → you learn the API.

## Episodes

| # | Karen Says | What You Build | Concepts |
|---|---|---|---|
| 01 | "Just show me the numbers" | Your first line plot | `plt.plot`, `plt.show`, figure/axes, labels, title |
| 02 | "Compare the two products" | Multiple lines + legend | Multiple `plot()`, `legend()`, colors, linestyles |
| 03 | "Make it a bar chart" | Vertical & horizontal bars | `bar()`, `barh()`, colors, width, annotations |
| 04 | "What percentage is each city?" | Pie chart + donut | `pie()`, explode, autopct, donut with `wedgeprops` |
| 05 | "Show me the distribution" | Histogram + KDE | `hist()`, bins, density, twin axes |
| 06 | "Is there a correlation?" | Scatter plot | `scatter()`, size, color, colorbar, alpha |
| 07 | "Put them all on one page" | Subplots grid | `subplots()`, `fig.add_subplot`, gridspec, tight_layout |
| 08 | "Make it look professional" | Styling & themes | `style.use()`, rcParams, custom fonts, spines, grid |
| 09 | "Add error bars and annotations" | Statistical charts | `errorbar()`, `annotate()`, `axhline`, `fill_between` |
| 10 | "Show it over time" | Time series | Date axes, `mdates`, rolling average, shaded regions |
| 11 | "Make it interactive" | Widgets & animation | `FuncAnimation`, sliders, hover tooltips |
| 12 | "Save it for the presentation" | Export & polish | `savefig()`, DPI, transparent, PDF, tight bbox |

## Setup

```bash
pip install matplotlib numpy pandas
```

## Run Any Episode

```bash
python ep01_first_plot.py
```

Each script is self-contained — run it, see the chart, read the code.
