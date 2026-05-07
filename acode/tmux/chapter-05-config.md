# Chapter 5: Configuration — Make tmux Yours

[← Chapter 4: Copy Mode](chapter-04-copy-mode.md) | [Chapter 6: Workflows →](chapter-06-workflows.md)

---

## The Problem

The defaults work, but they're not great. The prefix key requires a hand stretch. Splitting panes with `%` and `"` makes no visual sense. Copy mode uses emacs bindings. The status bar is ugly.

Dev: "The first thing I do on any new machine: drop my `.tmux.conf` in place. Five minutes of config saves years of friction."

## The Config File

tmux reads `~/.tmux.conf` on startup. Every setting, keybinding, and visual tweak lives here.

```bash
# Create it:
touch ~/.tmux.conf

# Edit it:
vim ~/.tmux.conf    # or your editor of choice
```

After making changes, reload without restarting tmux:

```
Ctrl-b  :source-file ~/.tmux.conf
```

Or add a reload binding to your config (we will below).

## Remap the Prefix Key

The most common customization. `Ctrl-b` requires stretching your left hand. `Ctrl-a` is one key over and much more natural (it's what GNU Screen used).

```bash
# Change prefix from Ctrl-b to Ctrl-a
unbind C-b
set -g prefix C-a
bind C-a send-prefix
```

The third line lets you send a literal `Ctrl-a` to programs (like going to the beginning of a line in bash) by pressing `Ctrl-a Ctrl-a`.

Dev: "I've used `Ctrl-a` for 10 years. But some people prefer `Ctrl-Space` or even backtick. Pick what feels natural and commit to it."

> **Note:** The rest of this course uses `Ctrl-b` as the prefix since it's the default. If you remap to `Ctrl-a`, mentally substitute.

## Better Split Bindings

`%` and `"` are hard to remember. Let's use `|` for vertical and `-` for horizontal — they look like what they do:

```bash
# Intuitive split bindings
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
unbind '"'
unbind %
```

The `-c "#{pane_current_path}"` part is crucial — it opens the new pane in the same directory as the current one. Without it, new panes always start in your home directory.

## Enable Mouse Support

Mouse support lets you click to select panes, drag to resize, and scroll with the wheel:

```bash
# Enable mouse mode
set -g mouse on
```

One line. Now you can:
- Click a pane to focus it
- Drag pane borders to resize
- Scroll with the mouse wheel (enters copy mode automatically)
- Click and drag to select text in copy mode

Dev: "I enable mouse mode but still use keyboard shortcuts for everything. The mouse is there for when someone else uses my terminal, or for quick scrolling."

## Vi Mode for Copy

Switch copy mode from emacs to vi bindings:

```bash
# Vi mode in copy mode
setw -g mode-keys vi

# Vi-style copy bindings
bind -T copy-mode-vi v send-keys -X begin-selection
bind -T copy-mode-vi y send-keys -X copy-selection-and-cancel
bind -T copy-mode-vi r send-keys -X rectangle-toggle
```

Now in copy mode: `v` starts selection (like vim visual mode), `y` yanks (copies), and `r` toggles rectangle/block selection.

## Increase Scrollback Buffer

The default 2000 lines isn't enough for real work:

```bash
# Keep 50,000 lines of history per pane
set -g history-limit 50000
```

## Faster Escape Time

By default, tmux waits 500ms after Escape to see if it's part of a key sequence. This makes vim feel sluggish:

```bash
# No delay for escape key
set -sg escape-time 0
```

## Start Window Numbering at 1

Windows start at 0 by default. But your keyboard has 1 on the left, not 0:

```bash
# Start windows and panes at 1, not 0
set -g base-index 1
setw -g pane-base-index 1

# Renumber windows when one is closed
set -g renumber-windows on
```

## Reload Config Binding

Add a shortcut to reload your config without typing the full command:

```bash
# Reload config with prefix + r
bind r source-file ~/.tmux.conf \; display-message "Config reloaded!"
```

Now `Ctrl-b r` reloads your config and shows a confirmation message.

## Pane Navigation with Alt+Arrow

Skip the prefix for pane switching — use Alt+arrow directly:

```bash
# Switch panes with Alt+arrow (no prefix needed)
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up select-pane -U
bind -n M-Down select-pane -D
```

The `-n` flag means "no prefix required." These bindings work instantly.

## Status Bar Customization

The status bar is your dashboard. Customize it:

```bash
# Status bar position
set -g status-position top

# Update interval (seconds)
set -g status-interval 5

# Colors
set -g status-style 'bg=#1e1e2e fg=#cdd6f4'

# Left side: session name
set -g status-left '#[fg=#89b4fa,bold] #S '
set -g status-left-length 30

# Right side: date and time
set -g status-right '#[fg=#a6adc8] %Y-%m-%d  %H:%M '
set -g status-right-length 50

# Window tabs
set -g window-status-format '#[fg=#6c7086] #I:#W '
set -g window-status-current-format '#[fg=#89b4fa,bold] #I:#W* '
```

Variables you can use:
- `#S` — session name
- `#I` — window index
- `#W` — window name
- `#P` — pane index
- `#H` — hostname

## The Complete Starter Config

Here's Dev's recommended starter `.tmux.conf`:

```bash
# ─── Prefix ───────────────────────────────────────────
# Remap prefix to Ctrl-a
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# ─── General ──────────────────────────────────────────
set -g mouse on
set -g history-limit 50000
set -sg escape-time 0
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on

# ─── Splits ───────────────────────────────────────────
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
unbind '"'
unbind %

# ─── Navigation ───────────────────────────────────────
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up select-pane -U
bind -n M-Down select-pane -D

# ─── Copy Mode ────────────────────────────────────────
setw -g mode-keys vi
bind -T copy-mode-vi v send-keys -X begin-selection
bind -T copy-mode-vi y send-keys -X copy-selection-and-cancel
bind -T copy-mode-vi r send-keys -X rectangle-toggle

# ─── Reload ───────────────────────────────────────────
bind r source-file ~/.tmux.conf \; display-message "Config reloaded!"

# ─── Status Bar ───────────────────────────────────────
set -g status-position top
set -g status-interval 5
set -g status-style 'bg=#1e1e2e fg=#cdd6f4'
set -g status-left '#[fg=#89b4fa,bold] #S '
set -g status-left-length 30
set -g status-right '#[fg=#a6adc8] %Y-%m-%d  %H:%M '
set -g status-right-length 50
set -g window-status-format '#[fg=#6c7086] #I:#W '
set -g window-status-current-format '#[fg=#89b4fa,bold] #I:#W* '
```

## Configuration Commands Reference

| Setting | What It Does |
|---|---|
| `set -g prefix C-a` | Change prefix key |
| `set -g mouse on` | Enable mouse support |
| `setw -g mode-keys vi` | Vi keys in copy mode |
| `set -g history-limit 50000` | Scrollback buffer size |
| `set -sg escape-time 0` | No escape delay |
| `set -g base-index 1` | Windows start at 1 |
| `bind key command` | Create a keybinding |
| `bind -n key command` | Keybinding without prefix |
| `unbind key` | Remove a keybinding |

## Exercise

1. Create `~/.tmux.conf` (or a test file if you don't want to change your real config)
2. Add at least 5 customizations from this chapter:
   - Remap prefix to `Ctrl-a`
   - Enable mouse mode
   - Set vi copy mode
   - Better split bindings (`|` and `-`)
   - Increase scrollback to 50000
3. Add the reload binding (`prefix + r`)
4. Reload your config: `Ctrl-b :source-file ~/.tmux.conf`
5. Test your new split bindings — do new panes open in the current directory?
6. Enter copy mode and verify vi keys work (hjkl navigation)
7. Customize the status bar — change at least the colors or add the date
8. Bonus: add `bind -n M-Left select-pane -L` (and the other directions) for prefix-free pane switching

Dev: "Your config will grow over time. Every time something annoys you, fix it in the config. That's how you build a setup that fits like a glove. Now let's put it all together into real workflows."

---

[← Chapter 4: Copy Mode](chapter-04-copy-mode.md) | [Chapter 6: Workflows →](chapter-06-workflows.md)
