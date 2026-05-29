# Chapter 4: Buffers and Windows

[prev: Editing](chapter-03-editing.md) | [next: Configuration](chapter-05-config.md)

## Buffers

A buffer is a region of memory holding text. Every file you open gets a buffer, but buffers can also exist without files (e.g., `*scratch*`, `*Messages*`).

| Key       | Action                    |
| --------- | ------------------------- |
| `C-x C-f` | Find (open) file          |
| `C-x C-s` | Save current buffer       |
| `C-x s`   | Save all modified buffers |
| `C-x b`   | Switch buffer (by name)   |
| `C-x C-b` | List all buffers          |
| `C-x k`   | Kill (close) buffer       |

### ibuffer

`M-x ibuffer` opens an advanced buffer list with filtering, sorting, and bulk operations:

- `d` — mark for deletion
- `x` — execute marked operations
- `/ m` — filter by major mode
- `/ n` — filter by name

```elisp
(global-set-key (kbd "C-x C-b") 'ibuffer)
```

## Windows

Windows are views into buffers. One frame can have multiple windows.

| Key       | Action                                  |
| --------- | --------------------------------------- |
| `C-x 2`   | Split window horizontally (top/bottom)  |
| `C-x 3`   | Split window vertically (left/right)    |
| `C-x 1`   | Delete all other windows (keep current) |
| `C-x 0`   | Delete current window                   |
| `C-x o`   | Switch to other window                  |
| `C-x 4 f` | Find file in other window               |
| `C-x 4 b` | Switch buffer in other window           |

### Resizing Windows

| Key     | Action                       |
| ------- | ---------------------------- |
| `C-x ^` | Enlarge window vertically    |
| `C-x }` | Enlarge window horizontally  |
| `C-x {` | Shrink window horizontally   |
| `C-x +` | Balance windows (equal size) |

### Winner Mode

Undo/redo window layout changes:

```elisp
(winner-mode 1)
;; C-c <left>   undo window change
;; C-c <right>  redo window change
```

## Frames

Frames are OS-level windows. Most people work in one frame with multiple windows.

| Key       | Action                |
| --------- | --------------------- |
| `C-x 5 2` | Create new frame      |
| `C-x 5 0` | Delete current frame  |
| `C-x 5 o` | Switch to other frame |

## Dired (Directory Editor)

Dired is Emacs's built-in file manager. Open with `C-x d` or by opening a directory with `C-x C-f`.

| Key   | Action                    |
| ----- | ------------------------- |
| `RET` | Open file/directory       |
| `^`   | Go up to parent directory |
| `d`   | Mark for deletion         |
| `x`   | Execute deletions         |
| `R`   | Rename/move file          |
| `C`   | Copy file                 |
| `+`   | Create directory          |
| `g`   | Refresh listing           |
| `m`   | Mark file                 |
| `u`   | Unmark file               |
| `% m` | Mark by regex             |

### Wdired (Writable Dired)

Press `C-x C-q` in Dired to make filenames editable. Rename files by editing text, then `C-c C-c` to apply or `C-c C-k` to cancel. Powerful for bulk renames.

## Practical Layout

```
C-x 3       Split vertically (code left, code right)
C-x o       Move to right window
C-x C-f     Open another file
C-x 2       Split right window horizontally
```

Result: code on the left, code top-right, shell bottom-right.
