# Chapter 7: Tables — Spreadsheets in Plain Text

[prev: Capture](chapter-06-capture.md) | [next: Babel](chapter-08-babel.md)

Org tables are surprisingly powerful — from simple data alignment to full spreadsheet calculations.

## Creating Tables

Type `|` followed by column content and press `TAB`:

```org
| Name    | Age | City     |
|---------+-----+----------|
| Alice   |  30 | London   |
| Bob     |  25 | Paris    |
| Charlie |  35 | Berlin   |
```

| Keybinding     | Action                                    |
| -------------- | ----------------------------------------- |
| `TAB`          | Move to next cell (creates row if at end) |
| `S-TAB`        | Move to previous cell                     |
| `RET`          | Move to next row                          |
| `M-left/right` | Move column left/right                    |
| `M-up/down`    | Move row up/down                          |
| `M-S-left`     | Delete column                             |
| `M-S-right`    | Insert column                             |
| `M-S-up`       | Delete row                                |
| `M-S-down`     | Insert row                                |
| `C-c -`        | Insert horizontal separator               |
| `C-c RET`      | Insert separator and move below           |
| `C-c ^`        | Sort table by column                      |

## Quick Table Creation

```org
|---+---+---|
```

Press `TAB` and it expands to a formatted table. Or use `C-c |` to convert region/create table.

## Formulas

### Column Formulas (Calc syntax)

```org
| Item   | Price | Qty | Total |
|--------+-------+-----+-------|
| Apples |  1.50 |   4 |  6.00 |
| Bread  |  2.00 |   2 |  4.00 |
| Milk   |  1.20 |   3 |  3.60 |
|--------+-------+-----+-------|
| Total  |       |     | 13.60 |
#+TBLFM: $4=$2*$3::@5$4=vsum(@2$4..@4$4)
```

- `$2` — column 2
- `@5$4` — row 5, column 4
- `vsum(@2$4..@4$4)` — sum of column 4, rows 2-4

### Lisp Formulas

Prefix with single quote:

```org
| Name  | Score | Grade |
|-------+-------+-------|
| Alice |    92 | A     |
| Bob   |    78 | B     |
#+TBLFM: $3='(if (> $2 90) "A" (if (> $2 70) "B" "C"))
```

| Keybinding    | Action                                |
| ------------- | ------------------------------------- |
| `C-c C-c`     | Recalculate row                       |
| `C-u C-c C-c` | Recalculate entire table              |
| `C-c =`       | Install formula for current cell      |
| `C-c '`       | Edit all formulas in dedicated buffer |
| `C-c ?`       | Show row/column info for current cell |

## Column References

```
$1, $2, $3...     — column by number
$N                 — last column
@2, @3...          — row by number
@<, @>             — first/last row
@I, @II            — first/second hline
$name              — named column (via header)
```

## Importing CSV

Select a region of CSV text and run `C-c |`:

```org
Name,Age,City
Alice,30,London
Bob,25,Paris
```

Becomes a formatted table.

## Exporting Tables

Tables export naturally to HTML, LaTeX, and other formats. Add attributes:

```org
#+CAPTION: Employee Data
#+ATTR_HTML: :border 2 :rules all
| Name  | Department |
|-------+------------|
| Alice | Engineering |
| Bob   | Marketing   |
```

## table.el for Complex Tables

For merged cells and complex layouts, use `table.el`:

```org
+----------+----------+
| Merged across       |
+----------+----------+
| Cell 1   | Cell 2   |
+----------+----------+
```

Activate with `M-x table-insert`.

## Exercises

1. Create a budget table with formulas:

```org
| Category  | Budget | Spent | Remaining |
|-----------+--------+-------+-----------|
| Food      |    500 |   420 |        80 |
| Transport |    200 |   180 |        20 |
| Utilities |    150 |   145 |         5 |
|-----------+--------+-------+-----------|
| Total     |    850 |   745 |       105 |
#+TBLFM: $4=$2-$3::@5$2=vsum(@2$2..@4$2)::@5$3=vsum(@2$3..@4$3)::@5$4=vsum(@2$4..@4$4)
```

2. Navigate with `TAB` and `S-TAB`
3. Sort by a column with `C-c ^`
4. Add/remove rows and columns with `M-S-` keys
5. Edit formulas with `C-c '`
