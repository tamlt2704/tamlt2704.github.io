# Chapter 2: Windows and Panes

[prev: Basics](chapter-01-basics.md) | [next: Copy Mode](chapter-03-copy-mode.md)

## Windows

Windows are like tabs within a session. Each window occupies the full terminal screen.

### Window Keybindings

| Key       | Action                         |
| --------- | ------------------------------ |
| `C-b c`   | Create new window              |
| `C-b n`   | Next window                    |
| `C-b p`   | Previous window                |
| `C-b 0-9` | Switch to window by number     |
| `C-b ,`   | Rename current window          |
| `C-b &`   | Close current window (confirm) |
| `C-b w`   | List all windows (interactive) |
| `C-b l`   | Toggle to last active window   |
| `C-b .`   | Move window to another index   |

```bash
# Create window from command line
tmux new-window -n editor

# Rename window
tmux rename-window logs
```

## Panes

Panes split a window into multiple terminal areas.

### Splitting

| Key     | Action                          |
| ------- | ------------------------------- |
| `C-b "` | Split horizontally (top/bottom) |
| `C-b %` | Split vertically (left/right)   |

### Navigating Panes

| Key              | Action                                   |
| ---------------- | ---------------------------------------- |
| `C-b arrow keys` | Move to pane in direction                |
| `C-b o`          | Cycle to next pane                       |
| `C-b ;`          | Toggle to last active pane               |
| `C-b q`          | Show pane numbers (press number to jump) |

### Resizing Panes

| Key           | Action                 |
| ------------- | ---------------------- |
| `C-b C-Left`  | Resize left            |
| `C-b C-Right` | Resize right           |
| `C-b C-Up`    | Resize up              |
| `C-b C-Down`  | Resize down            |
| `C-b M-1`     | Even horizontal layout |
| `C-b M-2`     | Even vertical layout   |
| `C-b Space`   | Cycle through layouts  |

### Zoom and Close

| Key     | Action                         |
| ------- | ------------------------------ |
| `C-b z` | Zoom pane (toggle fullscreen)  |
| `C-b x` | Close current pane (confirm)   |
| `C-b !` | Break pane into its own window |

## Pane Commands

```bash
# Split from command line
tmux split-window -h    # vertical split
tmux split-window -v    # horizontal split

# Resize from command line
tmux resize-pane -L 5   # left 5 cells
tmux resize-pane -R 5   # right 5 cells
tmux resize-pane -U 5   # up 5 cells
tmux resize-pane -D 5   # down 5 cells

# Swap panes
tmux swap-pane -U       # swap with pane above
tmux swap-pane -D       # swap with pane below
```

## Cheat Sheet

| Action               | Key            |
| -------------------- | -------------- |
| New window           | `C-b c`        |
| Next window          | `C-b n`        |
| Previous window      | `C-b p`        |
| Window by number     | `C-b 0-9`      |
| Rename window        | `C-b ,`        |
| Close window         | `C-b &`        |
| Split horizontal     | `C-b "`        |
| Split vertical       | `C-b %`        |
| Navigate panes       | `C-b arrows`   |
| Cycle panes          | `C-b o`        |
| Resize panes         | `C-b C-arrows` |
| Zoom pane            | `C-b z`        |
| Close pane           | `C-b x`        |
| Break pane to window | `C-b !`        |
