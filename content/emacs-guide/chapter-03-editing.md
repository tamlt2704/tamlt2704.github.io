# Chapter 3: Editing

[prev: Navigation](chapter-02-navigation.md) | [next: Buffers and Windows](chapter-04-buffers-windows.md)

## Kill and Yank (Cut and Paste)

Emacs uses "kill" (cut) and "yank" (paste). Killed text goes to the **kill ring**.

| Key     | Action                         |
| ------- | ------------------------------ |
| `C-k`   | Kill from point to end of line |
| `C-w`   | Kill region (cut selection)    |
| `M-w`   | Copy region (no kill)          |
| `M-d`   | Kill word forward              |
| `M-DEL` | Kill word backward             |
| `C-y`   | Yank (paste) last kill         |
| `M-y`   | Cycle kill ring (after C-y)    |

## Undo

| Key              | Action               |
| ---------------- | -------------------- |
| `C-/`            | Undo                 |
| `C-x u`          | Undo (alternative)   |
| `C-g` then `C-/` | Redo (undo the undo) |

Emacs undo is linear — all changes (including undos) are recorded. To "redo", break the undo sequence with `C-g` then undo again.

## Transpose and Case

| Key       | Action               |
| --------- | -------------------- |
| `C-t`     | Transpose characters |
| `M-t`     | Transpose words      |
| `C-x C-t` | Transpose lines      |
| `M-u`     | Uppercase word       |
| `M-l`     | Lowercase word       |
| `M-c`     | Capitalize word      |

## Query Replace

```
M-%         Interactive search and replace
C-M-%       Regex search and replace
```

During query-replace, respond with:

- `y` — replace this match
- `n` — skip this match
- `!` — replace all remaining
- `q` — quit

### Regex Replace Example

`C-M-%` then:

- Pattern: `\b\([a-z]+\)_\([a-z]+\)`
- Replace: `\1\2`

Emacs regex uses `\(` for groups and `\1` for backreferences.

## Rectangles

Rectangle commands operate on a column-based selection.

1. Set mark at one corner (`C-SPC`)
2. Move point to the opposite corner
3. Use a rectangle command:

| Key       | Action                        |
| --------- | ----------------------------- |
| `C-x r k` | Kill rectangle                |
| `C-x r y` | Yank rectangle                |
| `C-x r o` | Open (insert space) rectangle |
| `C-x r t` | Replace rectangle with string |
| `C-x r d` | Delete rectangle              |
| `C-x r N` | Number lines in rectangle     |

## Keyboard Macros

Record a sequence of keystrokes and replay them:

| Key            | Action                 |
| -------------- | ---------------------- |
| `C-x (`        | Start recording macro  |
| `C-x )`        | Stop recording         |
| `C-x e`        | Execute last macro     |
| `C-u 10 C-x e` | Execute macro 10 times |
| `C-u 0 C-x e`  | Execute until error    |

### Macro Workflow

1. Move to the start of the first item
2. `C-x (` — start recording
3. Perform the edit on one item
4. Move to the start of the next item
5. `C-x )` — stop recording
6. `C-u 0 C-x e` — repeat for all remaining items

To save a macro permanently:

```elisp
;; Name the last macro
M-x kmacro-name-last-macro RET my-macro RET
;; Insert it as elisp
M-x insert-kbd-macro RET my-macro RET
```

## Registers

Registers store text, positions, or window configurations in named slots (single characters).

| Key           | Action                           |
| ------------- | -------------------------------- |
| `C-x r s a`   | Store region in register 'a'     |
| `C-x r i a`   | Insert contents of register 'a'  |
| `C-x r SPC a` | Store point in register 'a'      |
| `C-x r j a`   | Jump to position in register 'a' |

## Bookmarks

Bookmarks are persistent named positions (survive across sessions).

| Key       | Action                |
| --------- | --------------------- |
| `C-x r m` | Set bookmark at point |
| `C-x r b` | Jump to bookmark      |
| `C-x r l` | List all bookmarks    |

## Cheat Sheet

| Key           | Action                   |
| ------------- | ------------------------ |
| `C-k`         | Kill to end of line      |
| `C-w` / `M-w` | Kill / copy region       |
| `C-y` / `M-y` | Yank / cycle kill ring   |
| `C-/`         | Undo                     |
| `M-%`         | Query replace            |
| `C-M-%`       | Regex replace            |
| `C-x r k`     | Kill rectangle           |
| `C-x r t`     | String-replace rectangle |
| `C-x (`       | Start macro              |
| `C-x )`       | End macro                |
| `C-x e`       | Run macro                |
| `C-x r s/i`   | Store/insert register    |
| `C-x r m/b`   | Set/jump bookmark        |
