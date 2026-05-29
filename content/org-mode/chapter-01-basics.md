# Chapter 1: Basics — Document Structure

[prev: Overview](chapter-00-overview.md) | [next: Markup](chapter-02-markup.md)

Org Mode documents are structured with headings, lists, and paragraphs. The genius is in how Emacs lets you fold, navigate, and restructure content with single keystrokes.

## Headings

Headings start with one or more asterisks at the beginning of a line:

```org
* Top-level heading (level 1)
** Second-level heading (level 2)
*** Third-level heading (level 3)
**** Fourth-level (and so on)
```

Everything under a heading (until the next heading of the same or higher level) belongs to that subtree.

## Folding (Visibility Cycling)

| Keybinding        | Action                                                             |
| ----------------- | ------------------------------------------------------------------ |
| `TAB`             | Cycle visibility of current subtree (folded → children → subtree)  |
| `S-TAB`           | Cycle visibility of entire buffer (overview → contents → show all) |
| `C-u C-u C-u TAB` | Show all                                                           |

When you open an Org file, it starts in overview mode — only top-level headings visible.

## Motion Commands

| Keybinding | Action                         |
| ---------- | ------------------------------ |
| `C-c C-n`  | Next heading (any level)       |
| `C-c C-p`  | Previous heading (any level)   |
| `C-c C-f`  | Next heading at same level     |
| `C-c C-b`  | Previous heading at same level |
| `C-c C-u`  | Up one level (parent heading)  |

## Editing Structure

| Keybinding  | Action                               |
| ----------- | ------------------------------------ |
| `M-RET`     | Insert new heading at same level     |
| `M-S-RET`   | Insert new TODO heading              |
| `M-up`      | Move subtree up                      |
| `M-down`    | Move subtree down                    |
| `M-left`    | Promote heading (decrease level)     |
| `M-right`   | Demote heading (increase level)      |
| `M-S-left`  | Promote subtree (heading + children) |
| `M-S-right` | Demote subtree (heading + children)  |

## Plain Lists

```org
Unordered lists:
- Item one
- Item two
  - Nested item (indent 2 spaces)
- Item three

Ordered lists:
1. First step
2. Second step
3. Third step

Description lists:
- Emacs :: A text editor (and more)
- Vim :: Another text editor
```

| Keybinding     | Action                         |
| -------------- | ------------------------------ |
| `M-RET`        | New list item                  |
| `M-up/down`    | Move item up/down              |
| `M-left/right` | Change indentation             |
| `S-left/right` | Cycle bullet type (- → + → 1.) |

## Checkboxes

```org
* Grocery List [2/4]
  - [X] Milk
  - [X] Bread
  - [ ] Eggs
  - [ ] Butter
```

| Keybinding | Action                   |
| ---------- | ------------------------ |
| `C-c C-c`  | Toggle checkbox          |
| `M-S-RET`  | Insert new checkbox item |

The `[2/4]` counter updates automatically. Use `[50%]` for percentage.

## Paragraphs

Body text goes under headings, separated by blank lines:

```org
* My Heading

This is a paragraph. It can span multiple lines.

This is a second paragraph under the same heading.
```

## Exercises

1. Create a file `practice.org` with this structure:

```org
* Work
** Project Alpha
*** TODO Design document
*** TODO Implementation
** Project Beta
* Personal
** Books to Read
- [ ] The Pragmatic Programmer
- [ ] SICP
** Errands
- [ ] Groceries
- [ ] Dentist appointment
```

2. Use `S-TAB` to cycle through overview → contents → show all
3. Move subtrees with `M-up/down`
4. Promote/demote headings with `M-left/right`
5. Toggle checkboxes with `C-c C-c`
