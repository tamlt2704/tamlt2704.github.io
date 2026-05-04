# Karen's Spreadsheet — A Pandas Story

Karen from Sales has a messy CSV with 50,000 rows of product data. Every episode, she asks you to do something with it. Each request sounds simple. The data fights back.

This is the story-driven version of the [Pandas 101 series](../README.md). Same concepts, but every episode starts with Karen breaking something.

## The Cast

| Character | Role |
|---|---|
| **You** | The intern who "knows Python" |
| **Karen** | "I just need a quick thing with the spreadsheet" |
| **Old Greg** | "Why are you using a for loop?" |
| **Captain Deadline** | "The board meeting is in 2 hours" |

## Episodes

| # | Karen Says | What Breaks | What You Learn |
|---|---|---|---|
| 01 | "Here's my spreadsheet" | It's a CSV, not Excel. 50,000 rows. | Series, DataFrame, read_csv |
| 02 | "Show me the first 10" | Terminal explodes with 50,000 rows | head, tail, shape, info |
| 03 | "Find all NYC products" | Wrong column, garbage output | loc, iloc, boolean indexing |
| 04 | "Add a tax column" | Overwrites the price column | Adding/removing columns |
| 05 | "Remove the duplicates" | 3,000 duplicate SKUs | drop_duplicates, filtering |
| 06 | "Sort by price" | Strings sort wrong ("9" > "80000") | sort_values, dtypes, astype |
| 07 | "Total sales per city" | You write a for loop. Old Greg sighs. | groupby, agg |
| 08 | "Why are there blanks?" | 847 NaN values, averages are wrong | fillna, dropna, isna |
| 09 | "Merge with inventory" | Keys don't match, 2,000 rows vanish | merge, join, concat |
| 10 | "15% discount for NYC only" | Discount applied to everything | apply, lambda, where |
| 11 | "Pivot for the board" | Captain Deadline wants rows as columns | pivot_table |
| 12 | "Make me a chart" | 50,000 data points, unreadable | plot, groupby + plot |

## Render

```bash
manim -pqh ep01_karens_spreadsheet.py KarensSpreadsheet
```
