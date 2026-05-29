# Chapter 6: Plugins (TPM)

[prev: Status Bar](chapter-05-status-bar.md) | [next: Workflows](chapter-07-workflows.md)

## tmux Plugin Manager (TPM)

TPM manages tmux plugins — install, update, and remove with keybindings.

### Install TPM

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

### Configure TPM

```bash
# Add to .tmux.conf
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'

# Initialize TPM (keep at the very bottom)
run '~/.tmux/plugins/tpm/tpm'
```

### TPM Keybindings

| Key                | Action                     |
| ------------------ | -------------------------- |
| `prefix + I`       | Install plugins            |
| `prefix + U`       | Update plugins             |
| `prefix + alt + u` | Remove plugins not in list |

## Essential Plugins

### tmux-sensible

Sane defaults everyone can agree on.

```bash
set -g @plugin 'tmux-plugins/tmux-sensible'
```

### tmux-resurrect

Save and restore tmux sessions (survives restarts).

```bash
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @resurrect-strategy-nvim 'session'
set -g @resurrect-capture-pane-contents 'on'
```

| Key            | Action          |
| -------------- | --------------- |
| `prefix + C-s` | Save session    |
| `prefix + C-r` | Restore session |

### tmux-continuum

Automatic session saving (works with resurrect).

```bash
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @continuum-save-interval '15'
set -g @continuum-restore 'on'
```

### tmux-yank

Copy to system clipboard from copy mode.

```bash
set -g @plugin 'tmux-plugins/tmux-yank'
```

| Key                | Action                         |
| ------------------ | ------------------------------ |
| `prefix + y`       | Copy command line to clipboard |
| `y` (in copy mode) | Copy selection to clipboard    |
| `Y` (in copy mode) | Copy and paste selection       |

### tmux-fzf

Fuzzy finder for sessions, windows, panes, and commands.

```bash
set -g @plugin 'sainnhe/tmux-fzf'
```

| Key          | Action          |
| ------------ | --------------- |
| `prefix + F` | Launch tmux-fzf |

### tmux-sessionizer

Quick project session switching.

```bash
set -g @plugin 'joshmedeski/tmux-sessionizer'
set -g @sessionizer-paths '~/projects,~/work'
```

| Key          | Action           |
| ------------ | ---------------- |
| `prefix + o` | Open sessionizer |

## Full Plugin Config Example

```bash
# Plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @plugin 'tmux-plugins/tmux-yank'
set -g @plugin 'sainnhe/tmux-fzf'

# Plugin settings
set -g @resurrect-capture-pane-contents 'on'
set -g @continuum-restore 'on'
set -g @continuum-save-interval '10'

# Initialize TPM (must be last)
run '~/.tmux/plugins/tpm/tpm'
```

After adding plugins, press `prefix + I` inside tmux to install them.

## Cheat Sheet

| Plugin      | Purpose               | Key                    |
| ----------- | --------------------- | ---------------------- |
| tpm         | Plugin manager        | `prefix + I` (install) |
| resurrect   | Save/restore sessions | `prefix + C-s` / `C-r` |
| continuum   | Auto-save sessions    | (automatic)            |
| sensible    | Sane defaults         | (automatic)            |
| yank        | System clipboard      | `y` in copy mode       |
| fzf         | Fuzzy finder          | `prefix + F`           |
| sessionizer | Project switcher      | `prefix + o`           |
