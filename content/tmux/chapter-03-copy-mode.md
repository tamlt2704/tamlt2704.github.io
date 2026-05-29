# Chapter 3: Copy Mode

[prev: Windows & Panes](chapter-02-windows-panes.md) | [next: Configuration](chapter-04-config.md)

## Entering Copy Mode

| Key     | Action                 |
| ------- | ---------------------- |
| `C-b [` | Enter copy mode        |
| `C-b ]` | Paste from tmux buffer |
| `q`     | Exit copy mode         |

In copy mode you can scroll through the scrollback buffer, search text, and copy selections.

## Navigation (vi mode)

Enable vi mode in your config:

```bash
setw -g mode-keys vi
```

| Key       | Action                  |
| --------- | ----------------------- |
| `h j k l` | Move left/down/up/right |
| `w`       | Next word               |
| `b`       | Previous word           |
| `C-u`     | Page up                 |
| `C-d`     | Page down               |
| `g`       | Top of buffer           |
| `G`       | Bottom of buffer        |
| `0`       | Start of line           |

## Navigation (emacs mode, default)

| Key         | Action               |
| ----------- | -------------------- |
| `C-p / C-n` | Up / Down            |
| `C-b / C-f` | Left / Right         |
| `M-b / M-f` | Previous / Next word |
| `C-a / C-e` | Start / End of line  |

## Searching

| Key   | Action                       |
| ----- | ---------------------------- |
| `/`   | Search forward (vi mode)     |
| `?`   | Search backward (vi mode)    |
| `n`   | Next match                   |
| `N`   | Previous match               |
| `C-s` | Search forward (emacs mode)  |
| `C-r` | Search backward (emacs mode) |

## Selecting and Copying (vi mode)

| Key     | Action                                 |
| ------- | -------------------------------------- |
| `Space` | Start selection                        |
| `Enter` | Copy selection and exit                |
| `v`     | Start selection (with custom bindings) |
| `y`     | Yank/copy (with custom bindings)       |

## Enhanced vi-copy Bindings

```bash
bind-key -T copy-mode-vi v send-keys -X begin-selection
bind-key -T copy-mode-vi y send-keys -X copy-selection-and-cancel
bind-key -T copy-mode-vi r send-keys -X rectangle-toggle
```

## Scrollback Buffer

```bash
# Set scrollback buffer size (default 2000 lines)
set -g history-limit 50000
```

## Copy to System Clipboard

### Linux (xclip)

```bash
bind-key -T copy-mode-vi y send-keys -X copy-pipe-and-cancel "xclip -selection clipboard"
```

### macOS (pbcopy)

```bash
bind-key -T copy-mode-vi y send-keys -X copy-pipe-and-cancel "pbcopy"
```

### WSL

```bash
bind-key -T copy-mode-vi y send-keys -X copy-pipe-and-cancel "clip.exe"
```

## Mouse Mode

```bash
set -g mouse on
```

With mouse mode on:

- Scroll wheel enters copy mode and scrolls
- Click and drag to select text
- Right-click to paste (depending on terminal)

## Cheat Sheet

| Action               | Key     |
| -------------------- | ------- |
| Enter copy mode      | `C-b [` |
| Paste buffer         | `C-b ]` |
| Exit copy mode       | `q`     |
| Start selection (vi) | `Space` |
| Copy selection (vi)  | `Enter` |
| Search forward       | `/`     |
| Search backward      | `?`     |
| Next match           | `n`     |
| Page up              | `C-u`   |
| Page down            | `C-d`   |
