# Chapter 2: Navigation

[prev: Getting Started](chapter-01-basics.md) | [next: Editing](chapter-03-editing.md)

## Basic Movement

All movement commands can be prefixed with `C-u N` to repeat N times (e.g., `C-u 10 C-n` moves down 10 lines).

| Key     | Movement                   |
| ------- | -------------------------- |
| `C-f`   | Forward one character      |
| `C-b`   | Backward one character     |
| `C-n`   | Next line (down)           |
| `C-p`   | Previous line (up)         |
| `M-f`   | Forward one word           |
| `M-b`   | Backward one word          |
| `C-a`   | Beginning of line          |
| `C-e`   | End of line                |
| `M-a`   | Beginning of sentence      |
| `M-e`   | End of sentence            |
| `C-v`   | Scroll down (page forward) |
| `M-v`   | Scroll up (page backward)  |
| `M-<`   | Beginning of buffer        |
| `M->`   | End of buffer              |
| `M-g g` | Go to line number          |
| `C-l`   | Center screen on point     |

The mnemonic: `C-` moves by small units (char/line), `M-` moves by larger units (word/sentence/buffer).

## Search

### Incremental Search (isearch)

| Key       | Action                         |
| --------- | ------------------------------ |
| `C-s`     | Search forward (incremental)   |
| `C-r`     | Search backward (incremental)  |
| `C-s C-s` | Repeat last search forward     |
| `C-r C-r` | Repeat last search backward    |
| `RET`     | Stop search at current match   |
| `C-g`     | Cancel search, return to start |

While in isearch:

- Type characters to narrow the search
- `C-s` again jumps to next match
- `C-r` jumps to previous match
- `M-e` edits the search string
- `C-w` adds word at point to search

### Occur

```
M-x occur RET pattern RET
```

Shows all lines matching a pattern in a separate buffer. Click any line to jump to it.

## Go to Line

```
M-g g    (or M-g M-g)
```

Prompts for a line number and jumps to it.

## Mark and Region

The **mark** is a saved position. The text between mark and point is the **region** (selection).

| Key       | Action                              |
| --------- | ----------------------------------- |
| `C-SPC`   | Set mark at point                   |
| `C-x C-x` | Exchange point and mark             |
| `C-w`     | Kill (cut) region                   |
| `M-w`     | Copy region (save to kill ring)     |
| `C-y`     | Yank (paste) most recent kill       |
| `M-y`     | Cycle through kill ring (after C-y) |
| `C-x h`   | Select entire buffer                |

### Workflow Example

To copy a word:

1. `M-b` — move to beginning of word
2. `C-SPC` — set mark
3. `M-f` — move to end of word
4. `M-w` — copy
5. Move to destination
6. `C-y` — paste

## Kill Ring

The kill ring stores your last ~60 kills. After yanking with `C-y`, press `M-y` repeatedly to cycle through older kills.

## Cheat Sheet

| Key           | Action                          |
| ------------- | ------------------------------- |
| `C-f` / `C-b` | Char forward / backward         |
| `M-f` / `M-b` | Word forward / backward         |
| `C-n` / `C-p` | Line down / up                  |
| `C-a` / `C-e` | Line start / end                |
| `M-a` / `M-e` | Sentence start / end            |
| `C-v` / `M-v` | Page down / up                  |
| `M-<` / `M->` | Buffer start / end              |
| `M-g g`       | Go to line                      |
| `C-s` / `C-r` | Search forward / backward       |
| `C-SPC`       | Set mark                        |
| `C-w`         | Kill (cut) region               |
| `M-w`         | Copy region                     |
| `C-y`         | Yank (paste)                    |
| `M-y`         | Yank previous (cycle kill ring) |
| `C-g`         | Cancel                          |
