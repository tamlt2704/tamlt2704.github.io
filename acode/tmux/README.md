# tmux — Terminal Multiplexer Mastery

One terminal. Infinite workspaces. Never lose a session again.

## The Story

You SSH into a server. You start a long-running process. Your WiFi drops. The process dies. You scream.

Your colleague **Dev** never has this problem. He reconnects and everything is exactly where he left it — 6 panes, 4 windows, a build running, logs streaming, vim open. "tmux," he says. "Learn it once, use it forever."

## What tmux Gives You

| Problem | tmux Solution |
|---|---|
| SSH drops, process dies | Sessions persist — reconnect and resume |
| One terminal, one task | Split into panes — see everything at once |
| Context switching between projects | Windows — one per project, instant switch |
| "What was I doing yesterday?" | Detach at night, reattach in the morning |
| Pair programming | Share a session — both see the same terminal |

## Chapters

| Ch | Title | What You Learn |
|---|---|---|
| 0 | [Install & First Session](chapter-00-basics.md) | Install, start, prefix key, detach/attach |
| 1 | [Windows](chapter-01-windows.md) | Create, switch, rename, close windows |
| 2 | [Panes](chapter-02-panes.md) | Split, resize, navigate, zoom panes |
| 3 | [Sessions](chapter-03-sessions.md) | Multiple sessions, naming, switching |
| 4 | [Copy Mode](chapter-04-copy-mode.md) | Scroll, search, copy text without mouse |
| 5 | [Configuration](chapter-05-config.md) | .tmux.conf, remap prefix, vi keys, theme |
| 6 | [Workflows](chapter-06-workflows.md) | Dev layouts, project sessions, scripted setups |
| 7 | [Plugins & Advanced](chapter-07-plugins.md) | TPM, resurrect, continuum, fzf integration |

## The Prefix Key

Every tmux command starts with the **prefix** (default: `Ctrl-b`). You press the prefix, release it, then press the command key.

```
Ctrl-b  then  c     →  create new window
Ctrl-b  then  %     →  split pane vertically
Ctrl-b  then  "     →  split pane horizontally
Ctrl-b  then  d     →  detach from session
```

Throughout this course: `<prefix>` means `Ctrl-b` (or whatever you remap it to).

## Prerequisites

```bash
# Install
brew install tmux        # macOS
sudo apt install tmux    # Ubuntu/Debian
sudo pacman -S tmux      # Arch

# Verify
tmux -V
# tmux 3.x
```

Start with [Chapter 0: Install & First Session →](chapter-00-basics.md)
