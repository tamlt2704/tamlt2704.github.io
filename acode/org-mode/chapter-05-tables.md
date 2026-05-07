# Chapter 5: Spreadsheets in Plain Text — Tables and Formulas

[← Ch 4](chapter-04-capture-refile.md) | [Ch 6 →](chapter-06-links-attachments.md)

---

## The Problem

You need a quick comparison table. Or you're tracking sprint velocity. Or logging expenses for a client invoice. You open Google Sheets, wait for it to load, fight with formatting, realize you can't version-control it, and end up with a link that'll be dead in 2 years.

---

## The Naive Attempt

Markdown tables:

```markdown
| Task | Estimate | Actual |
|------|----------|--------|
| Auth | 3 | 5 |
| API  | 5 | 4 |
| UI   | 8 | 10 |
| Total | 16 | 19 |
```

You manually calculate the total. When you add a row, you recalculate. When you need the average, you pull out a calculator. It's a table that can't *do* anything.

---

## Nadia's Way: Tables That Calculate

> "Org tables auto-align, auto-resize, and can run spreadsheet formulas. I track sprint velocity, client billing, and expense reports — all in plain text, all version-controlled, all greppable."

---

## Creating Tables

Type a row with pipes and press `Tab`:

```org
| Name | Role | Team |
```

Press `Tab` — org-mode creates the separator and aligns:

```org
| Name | Role | Team |
|------+------+------|
|      |      |      |
```

Keep typing and pressing `Tab` to move between cells:

```org
| Name    | Role     | Team     |
|---------+----------+----------|
| Alice   | Backend  | Platform |
| Bob     | Frontend | Product  |
| Charlie | DevOps   | Platform |
```

Org-mode auto-aligns columns as you type. No manual spacing.

---

## Table Navigation

| Binding | Action |
|---|---|
| `Tab` | Next cell (creates new row at end) |
| `S-Tab` | Previous cell |
| `RET` | Next row (same column) |
| `M-left` / `M-right` | Move column left/right |
| `M-up` / `M-down` | Move row up/down |
| `M-S-left` | Delete column |
| `M-S-right` | Insert column |
| `M-S-up` | Delete row |
| `M-S-down` | Insert row |

---

## Horizontal Rules and Groups

```org
| Category | Q1   | Q2   | Q3   | Q4   |
|----------+------+------+------+------|
| Revenue  | 100k | 120k | 115k | 140k |
| Costs    | 80k  | 85k  | 82k  | 90k  |
|----------+------+------+------+------|
| Profit   | 20k  | 35k  | 33k  | 50k  |
```

A line starting with `|-` is a horizontal rule. Use it to visually separate header, body, and footer rows.

---

## Formulas: The Spreadsheet Part

Here's where org tables become powerful. Add a formula line below the table:

```org
| Task   | Estimate | Actual | Diff |
|--------+----------+--------+------|
| Auth   |        3 |      5 |   -2 |
| API    |        5 |      4 |    1 |
| UI     |        8 |     10 |   -2 |
| Tests  |        3 |      3 |    0 |
|--------+----------+--------+------|
| Total  |       19 |     22 |   -3 |
#+TBLFM: $4=$2-$3::@6$2=vsum(@2..@5)::@6$3=vsum(@2..@5)::@6$4=vsum(@2..@5)
```

The `#+TBLFM:` line defines formulas:
- `$4=$2-$3` — Column 4 = Column 2 minus Column 3 (for all rows)
- `@6$2=vsum(@2..@5)` — Row 6, Column 2 = sum of rows 2-5
- `::` separates multiple formulas

Apply formulas with `C-c C-c` on the `#+TBLFM` line. Or `C-u C-c C-c` to recalculate the whole table.

---

## Cell References

| Reference | Meaning |
|---|---|
| `$3` | Column 3 (current row) |
| `@2` | Row 2 (current column) |
| `@2$3` | Row 2, Column 3 (absolute) |
| `@2..@5` | Range: rows 2 through 5 |
| `$2..$4` | Range: columns 2 through 4 |
| `@>` | Last row |
| `$>` | Last column |
| `@<` | First data row (after header) |

---

## Common Formulas

```org
#+TBLFM: $4=$2-$3                          ;; difference
#+TBLFM: @>$2=vsum(@2..@-1)                ;; sum of column (last row)
#+TBLFM: @>$2=vmean(@2..@-1)               ;; average
#+TBLFM: $4=$2*$3;%.2f                     ;; multiply, 2 decimal places
#+TBLFM: $5=if($4 > 0, "over", "under")   ;; conditional
```

The `;%.2f` is a format specifier — two decimal places.

---

## Practical: Sprint Velocity Tracker

```org
#+TITLE: Sprint Velocity

| Sprint | Planned | Completed | Velocity | Carry-over |
|--------+---------+-----------+----------+------------|
|     11 |      34 |        30 |       88 |          4 |
|     12 |      32 |        32 |      100 |          0 |
|     13 |      35 |        28 |       80 |          7 |
|     14 |      30 |        27 |       90 |          3 |
|--------+---------+-----------+----------+------------|
|    Avg |   32.75 |     29.25 |    89.50 |       3.50 |
#+TBLFM: $4=($3/$2)*100;%.0f::$5=$2-$3::@>$2=vmean(@2..@-1);%.2f::@>$3=vmean(@2..@-1);%.2f::@>$4=vmean(@2..@-1);%.2f::@>$5=vmean(@2..@-1);%.2f
```

---

## Practical: Client Billing

```org
#+TITLE: Invoice — January 2026

| Date       | Task                    | Hours | Rate | Amount |
|------------+-------------------------+-------+------+--------|
| 2026-01-06 | API endpoint design     |   3.5 |  150 |  525.0 |
| 2026-01-07 | Database schema         |   4.0 |  150 |  600.0 |
| 2026-01-08 | Authentication system   |   6.0 |  150 |  900.0 |
| 2026-01-09 | Code review & fixes     |   2.5 |  150 |  375.0 |
| 2026-01-10 | Deployment & testing    |   3.0 |  150 |  450.0 |
|------------+-------------------------+-------+------+--------|
|            | TOTAL                   |  19.0 |      | 2850.0 |
#+TBLFM: $5=$3*$4;%.1f::@>$3=vsum(@2..@-1);%.1f::@>$5=vsum(@2..@-1);%.1f
```

---

## Importing and Exporting

### Import CSV

You have a CSV file? Paste it into an org buffer and run:

```
M-x org-table-create-or-convert-from-region
```

Or import directly:

```
M-x org-table-import
```

### Export to CSV

Put cursor in table:

```
M-x org-table-export
```

Choose filename and format (csv, tsv, etc.).

---

## Named Columns

For readability, use named references instead of `$1`, `$2`:

```org
| Student | Math | Science | Average |
|---------+------+---------+---------|
| Alice   |   92 |      88 |      90 |
| Bob     |   78 |      85 |    81.5 |
| Charlie |   95 |      91 |      93 |
#+TBLFM: $Average=($Math+$Science)/2;%.1f
```

Name columns by using the header row names with `$` prefix.

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `Tab` | Next cell / align table |
| `S-Tab` | Previous cell |
| `RET` | Next row |
| `M-left` / `M-right` | Move column |
| `M-up` / `M-down` | Move row |
| `M-S-right` | Insert column |
| `M-S-down` | Insert row |
| `M-S-left` | Delete column |
| `M-S-up` | Delete row |
| `C-c C-c` | Re-apply formulas |
| `C-c }` | Toggle column/row references |
| `C-c {` | Toggle formula debugger |
| `C-c ?` | Show reference of current cell |

---

## Exercise: Build a Project Tracker

1. Create a table tracking your current project's tasks:

```org
| Task | Estimate (hrs) | Actual (hrs) | Status | Diff |
|------+----------------+--------------+--------+------|
|      |                |              |        |      |
```

2. Fill in at least 5 tasks with estimates and actuals.
3. Add a formula for the Diff column (`$5=$2-$3`).
4. Add a Total row with `vsum` for Estimate, Actual, and Diff columns.
5. Add an Average row with `vmean`.
6. Apply formulas with `C-c C-c` on the `#+TBLFM` line.

Bonus: Create a monthly expense tracker with categories, amounts, and a total.

> **Nadia's tip:** "I don't use org tables for everything — complex data still goes in a real database. But for quick calculations, tracking, and reports that live alongside my notes? Nothing beats it. It's version-controlled, it's greppable, and I never have to open Google Sheets for a 10-row table again."

---

[← Ch 4](chapter-04-capture-refile.md) | [Ch 6: Connect Everything →](chapter-06-links-attachments.md)
