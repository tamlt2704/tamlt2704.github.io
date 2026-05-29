# Chapter 5: Status Bar

[prev: Configuration](chapter-04-config.md) | [next: Plugins](chapter-06-plugins.md)

## Status Bar Anatomy

The status bar has three sections:

```
[left]          [window-list (center)]          [right]
```

## Basic Configuration

```bash
set -g status on
set -g status-position bottom
set -g status-interval 5
set -g status-left-length 40
set -g status-right-length 60
```

## Colors

Colors use the `#[fg=colour,bg=colour]` format:

```bash
set -g status-style fg=white,bg=colour235
setw -g window-status-style fg=colour244,bg=default
setw -g window-status-current-style fg=white,bg=colour39,bold
```

Available color formats:

- Named: `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`, `black`
- 256 palette: `colour0` to `colour255`
- Hex (tmux 3.2+): `#ff5555`

## Variables

| Variable | Value          |
| -------- | -------------- |
| `#S`     | Session name   |
| `#W`     | Window name    |
| `#I`     | Window index   |
| `#P`     | Pane index     |
| `#H`     | Hostname       |
| `#h`     | Short hostname |
| `#T`     | Pane title     |
| `#F`     | Window flags   |

## Left and Right Sections

```bash
set -g status-left "#[fg=green,bold] #S #[default]| "
set -g status-right "#[fg=cyan]%Y-%m-%d #[fg=white]%H:%M "
```

## Date/Time Formatting

```bash
set -g status-right "%H:%M"           # 14:30
set -g status-right "%I:%M %p"        # 02:30 PM
set -g status-right "%a %d %b"        # Fri 29 May
set -g status-right "%Y-%m-%d %H:%M"  # 2026-05-29 14:30
```

## Custom Scripts

Run shell commands with `#()`:

```bash
# Battery percentage
set -g status-right "#(cat /sys/class/power_supply/BAT0/capacity)%% | %H:%M"

# Git branch
set -g status-right "#(cd #{pane_current_path}; git branch --show-current) | %H:%M"

# Custom script
set -g status-right "#(~/.tmux/scripts/status.sh)"
```

## Window Status Format

```bash
setw -g window-status-format " #I:#W "
setw -g window-status-current-format " #I:#W "
setw -g window-status-separator ""
```

## Powerline Style

```bash
set -g status-left "#[fg=black,bg=green,bold] #S #[fg=green,bg=colour235]"
set -g status-right "#[fg=colour39]#[fg=black,bg=colour39] %H:%M #[fg=green]#[fg=black,bg=green] #H "
setw -g window-status-current-format "#[fg=colour235,bg=colour39]#[fg=white,bold] #I:#W #[fg=colour39,bg=colour235]"
```

## Catppuccin Theme

```bash
set -g status-style fg="#cdd6f4",bg="#1e1e2e"
set -g status-left "#[fg=#1e1e2e,bg=#89b4fa,bold] #S #[fg=#89b4fa,bg=#1e1e2e]"
set -g status-right "#[fg=#a6adc8] %Y-%m-%d  %H:%M "
setw -g window-status-format "#[fg=#6c7086] #I:#W "
setw -g window-status-current-format "#[fg=#1e1e2e,bg=#cba6f7,bold] #I:#W #[default]"
```

## Dracula Theme

```bash
set -g status-style fg="#f8f8f2",bg="#282a36"
set -g status-left "#[fg=#282a36,bg=#bd93f9,bold] #S #[default] "
set -g status-right "#[fg=#f8f8f2]%H:%M #[fg=#6272a4]| #[fg=#f8f8f2]#H "
setw -g window-status-format "#[fg=#6272a4] #I:#W "
setw -g window-status-current-format "#[fg=#282a36,bg=#50fa7b,bold] #I:#W #[default]"
set -g pane-border-style fg="#6272a4"
set -g pane-active-border-style fg="#ff79c6"
```

## Cheat Sheet

| Setting                        | Purpose                |
| ------------------------------ | ---------------------- |
| `status-left`                  | Left section content   |
| `status-right`                 | Right section content  |
| `status-style`                 | Default bar colors     |
| `window-status-format`         | Inactive window format |
| `window-status-current-format` | Active window format   |
| `status-interval`              | Refresh rate (seconds) |
| `#S`                           | Session name           |
| `#W`                           | Window name            |
| `#H`                           | Hostname               |
| `#()`                          | Shell command output   |
| `#[fg=,bg=]`                   | Color formatting       |
