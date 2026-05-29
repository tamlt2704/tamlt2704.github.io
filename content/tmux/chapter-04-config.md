# Chapter 4: Configuration

[prev: Copy Mode](chapter-03-copy-mode.md) | [next: Status Bar](chapter-05-status-bar.md)

## The Config File

tmux reads `~/.tmux.conf` on startup. Changes require restarting tmux or reloading the config.

## Reload Config

```bash
# From command mode (C-b :)
source-file ~/.tmux.conf

# Bind a key to reload
bind r source-file ~/.tmux.conf \; display "Config reloaded!"
```

Now `C-b r` reloads your config instantly.

## Change Prefix Key

```bash
unbind C-b
set -g prefix C-a
bind C-a send-prefix
```

## Option Scopes: set -g vs set -s vs setw

| Command          | Scope                                    |
| ---------------- | ---------------------------------------- |
| `set -g`         | Global session option (all sessions)     |
| `set -s`         | Server option (affects the whole server) |
| `setw -g`        | Global window option (all windows)       |
| `set` (no flag)  | Session-specific option                  |
| `setw` (no flag) | Window-specific option                   |

## Mouse Support

```bash
set -g mouse on
```

## Vi Mode

```bash
setw -g mode-keys vi
set -g status-keys vi
```

## Better Splits

```bash
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
unbind '"'
unbind %
```

## Pane Navigation (vim-style)

```bash
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R
```

## Pane Resizing

```bash
bind -r H resize-pane -L 5
bind -r J resize-pane -D 5
bind -r K resize-pane -U 5
bind -r L resize-pane -R 5
```

## Colors and Terminal

```bash
set -g default-terminal "tmux-256color"
set -ag terminal-overrides ",xterm-256color:RGB"
```

## Pane Borders

```bash
set -g pane-border-style fg=colour238
set -g pane-active-border-style fg=colour39
```

## Window Settings

```bash
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on
set -g allow-rename off
```

## Misc

```bash
set -s escape-time 0
set -g history-limit 50000
set -g display-time 3000
set -g focus-events on
```

## Full Starter Config

```bash
# ~/.tmux.conf

# Prefix
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Reload
bind r source-file ~/.tmux.conf \; display "Reloaded!"

# Mouse
set -g mouse on

# Vi mode
setw -g mode-keys vi
set -g status-keys vi

# Splits
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

# Pane navigation
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Start at 1
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on

# Terminal
set -g default-terminal "tmux-256color"
set -ag terminal-overrides ",xterm-256color:RGB"
set -s escape-time 0
set -g history-limit 50000
set -g focus-events on
```

## Cheat Sheet

| Setting                           | Purpose            |
| --------------------------------- | ------------------ |
| `set -g prefix C-a`               | Change prefix      |
| `set -g mouse on`                 | Enable mouse       |
| `setw -g mode-keys vi`            | Vi copy mode       |
| `set -g base-index 1`             | Windows start at 1 |
| `set -s escape-time 0`            | No escape delay    |
| `set -g history-limit 50000`      | Scrollback size    |
| `bind r source-file ~/.tmux.conf` | Reload shortcut    |
