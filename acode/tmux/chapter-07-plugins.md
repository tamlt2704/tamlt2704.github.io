# Chapter 7: Plugins — Power-Ups

[← Chapter 6: Workflows](chapter-06-workflows.md)

---

## The Problem

tmux is powerful out of the box. But there are gaps: sessions don't survive reboots, copying to the system clipboard requires workarounds, and finding things across many sessions is slow.

Dev: "Plugins fill the gaps. Five plugins and tmux goes from great to unstoppable. The best part — they're all managed by one tool: TPM."

## TPM: Tmux Plugin Manager

TPM is the package manager for tmux plugins. Install it once, then adding plugins is a one-liner in your config.

### Installation

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

Add to the bottom of your `~/.tmux.conf`:

```bash
# ─── Plugins ──────────────────────────────────────────
# List of plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'

# Initialize TPM (keep this line at the very bottom)
run '~/.tmux/plugins/tpm/tpm'
```

Reload your config:

```
Ctrl-b  :source-file ~/.tmux.conf
```

### Installing Plugins

After adding a plugin line to your config:

```
Ctrl-b  I       →  install plugins (capital I)
```

TPM clones the repos and loads them. You'll see a message when it's done.

### Updating and Removing

```
Ctrl-b  U       →  update all plugins
Ctrl-b  alt-u   →  remove plugins not in config
```

## Plugin 1: tmux-sensible

Sane defaults that everyone agrees on. Saves you from configuring the obvious stuff:

```bash
set -g @plugin 'tmux-plugins/tmux-sensible'
```

What it sets:
- UTF-8 support
- Increase scrollback to 50000
- Faster key repetition
- Better status bar refresh
- Focus events enabled
- Aggressive resize (useful for grouped sessions)

Dev: "I always include sensible. It's the 'you should have these settings' plugin."

## Plugin 2: tmux-resurrect

The killer plugin. Save your entire tmux environment and restore it after a reboot.

```bash
set -g @plugin 'tmux-plugins/tmux-resurrect'
```

### Usage

```
Ctrl-b  Ctrl-s      →  save environment
Ctrl-b  Ctrl-r      →  restore environment
```

What gets saved:
- All sessions, windows, and panes
- Pane layouts and sizes
- Current working directories
- Running programs (vim, htop, etc. — configurable)

What gets restored:
- The exact layout you had
- Programs restarted in their correct panes
- Working directories preserved

### Restoring Programs

By default, resurrect restores a limited set of programs. Add more:

```bash
set -g @resurrect-processes 'vim nvim htop "npm run dev" "python manage.py runserver"'
```

### Saving Vim Sessions

resurrect can restore vim sessions too:

```bash
set -g @resurrect-strategy-vim 'session'    # requires vim-obsession plugin
set -g @resurrect-strategy-nvim 'session'
```

Dev: "Resurrect changed my life. Reboot for a system update, run `Ctrl-b Ctrl-r`, and everything is back. Every session, every pane, every program. Magic."

## Plugin 3: tmux-continuum

Automatic saving. Pairs with resurrect to save every 15 minutes without thinking:

```bash
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @continuum-save-interval '15'
set -g @continuum-restore 'on'       # auto-restore when tmux starts
```

With continuum + resurrect: your environment auto-saves, and if you reboot, just start tmux — continuum auto-restores your last state.

### Auto-Start tmux

Continuum can start tmux automatically when you open your terminal:

```bash
set -g @continuum-boot 'on'
```

## Plugin 4: tmux-yank

System clipboard integration. Copy in tmux, paste anywhere.

```bash
set -g @plugin 'tmux-plugins/tmux-yank'
```

After installing, copying in copy mode (with `Enter` or `y`) goes to both tmux's buffer AND your system clipboard. Requirements: `pbcopy` (macOS, built-in), `xclip` (Linux), or `clip.exe` (WSL).

In copy mode with vi bindings:
- `y` — copy selection to system clipboard
- `Y` — copy and paste to command line

Dev: "Before tmux-yank, I had this hacky pipe-to-pbcopy thing. Now it just works. Copy in tmux, Cmd-V in Chrome."

## Plugin 5: tmux-fzf

Fuzzy-find everything in tmux — sessions, windows, panes, commands:

```bash
set -g @plugin 'sainnhe/tmux-fzf'
```

Requires [fzf](https://github.com/junegunn/fzf) installed (`brew install fzf` or `sudo apt install fzf`).

### Usage

```
Ctrl-b  F       →  open tmux-fzf menu (capital F)
```

The menu lets you fuzzy-search sessions, windows, panes, commands, key bindings, and clipboard history.

Dev: "When you have 5 sessions with 4 windows each, `Ctrl-b s` gets crowded. tmux-fzf lets me type 'back' and instantly jump to my backend session."

## Bonus Plugins

A few more worth knowing:

- **tmux-fingers** — highlight and copy text patterns (URLs, paths, IPs) with a keystroke
- **tmux-open** — open highlighted URLs or file paths directly from copy mode
- **tmux-pain-control** — better pane navigation with prefix + h/j/k/l

## The Complete Power-User Config

Here's Dev's full `.tmux.conf` with plugins:

```bash
# ─── Prefix ───────────────────────────────────────────
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

# ─── Reload ───────────────────────────────────────────
bind r source-file ~/.tmux.conf \; display-message "Config reloaded!"

# ─── Status Bar ───────────────────────────────────────
set -g status-position top
set -g status-style 'bg=#1e1e2e fg=#cdd6f4'
set -g status-left '#[fg=#89b4fa,bold] #S '
set -g status-right '#[fg=#a6adc8] %H:%M '

# ─── Plugins ──────────────────────────────────────────
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @plugin 'tmux-plugins/tmux-yank'
set -g @plugin 'sainnhe/tmux-fzf'

set -g @resurrect-processes 'vim nvim htop "~npm run dev"'
set -g @continuum-save-interval '15'
set -g @continuum-restore 'on'

# Initialize TPM (must be last)
run '~/.tmux/plugins/tpm/tpm'
```

## Plugin Management Reference

| Keys / Command | Action |
|---|---|
| `Ctrl-b I` | Install new plugins |
| `Ctrl-b U` | Update plugins |
| `Ctrl-b alt-u` | Remove unlisted plugins |
| `Ctrl-b Ctrl-s` | Save environment (resurrect) |
| `Ctrl-b Ctrl-r` | Restore environment (resurrect) |
| `Ctrl-b F` | Open tmux-fzf |
| `y` (in copy mode) | Copy to system clipboard (yank) |

## Exercise

1. Install TPM:
   ```bash
   git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
   ```

2. Add the plugin block to your `~/.tmux.conf` (at minimum: tpm, resurrect, continuum)

3. Reload your config: `Ctrl-b :source-file ~/.tmux.conf`

4. Install plugins: `Ctrl-b I` — wait for the "Done" message

5. Create a layout with 2 sessions, each with 2-3 windows and some split panes

6. Save with resurrect: `Ctrl-b Ctrl-s` — you'll see "Tmux environment saved!"

7. Kill the tmux server completely:
   ```bash
   tmux kill-server
   ```

8. Start tmux fresh:
   ```bash
   tmux
   ```

9. Restore: `Ctrl-b Ctrl-r` — watch your entire environment reappear

10. Verify: all sessions, windows, panes, and working directories are back

Dev: "That's the full toolkit. tmux with a good config and these plugins is the most productive terminal setup I've ever used. You'll never go back to plain terminals. The investment pays off every single day."

---

## What's Next?

You now have the full toolkit: panes, windows, sessions, copy mode, a custom config, scripted workflows, and plugins. The only thing left is practice. Use tmux for everything — in a week it'll be muscle memory.

---

[← Chapter 6: Workflows](chapter-06-workflows.md)
