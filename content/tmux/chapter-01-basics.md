# Chapter 1: Getting Started with tmux

[prev: Overview](chapter-00-overview.md) | [next: Windows & Panes](chapter-02-windows-panes.md)

## Installation

```bash
# Debian/Ubuntu
sudo apt install tmux

# macOS
brew install tmux

# Fedora
sudo dnf install tmux

# Arch
sudo pacman -S tmux

# Check version
tmux -V
```

## Why tmux?

- **Persistent sessions** — your terminal survives disconnections
- **SSH survival** — network drops won't kill running processes
- **Split panes** — multiple terminals in one window
- **Window management** — organize work into named windows
- **Scriptable** — automate complex layouts

## The Prefix Key

Every tmux command starts with a **prefix key**, default `C-b` (Ctrl+b). You press the prefix, release, then press the command key.

Example: to detach, press `C-b` then `d`.

## Sessions

Sessions are the top-level container in tmux. Each session has one or more windows.

```bash
# Start a new session
tmux

# Start a named session
tmux new -s myproject

# Detach from session (inside tmux)
# C-b d

# List sessions
tmux ls

# Attach to a session
tmux attach -t myproject

# Attach to last session
tmux attach

# Kill a session
tmux kill-session -t myproject

# Kill all sessions
tmux kill-server
```

## Session Commands Cheat Sheet

| Action           | Command / Key               |
| ---------------- | --------------------------- |
| New session      | `tmux new -s name`          |
| Detach           | `C-b d`                     |
| List sessions    | `tmux ls`                   |
| Attach           | `tmux attach -t name`       |
| Kill session     | `tmux kill-session -t name` |
| Rename session   | `C-b $`                     |
| Switch session   | `C-b s` (interactive list)  |
| Next session     | `C-b )`                     |
| Previous session | `C-b (`                     |

## First Session Workflow

```bash
# 1. Create a named session for your project
tmux new -s webapp

# 2. Do your work (edit files, run servers, etc.)

# 3. Detach when done (C-b d)

# 4. Later, reattach
tmux attach -t webapp

# 5. Everything is exactly as you left it
```

## Inside vs Outside tmux

Commands typed in your shell (outside tmux):

```bash
tmux new -s name      # create session
tmux attach -t name   # attach to session
tmux ls               # list sessions
tmux kill-session -t name
```

Key bindings (inside tmux, after prefix `C-b`):

| Key | Action               |
| --- | -------------------- |
| `d` | Detach               |
| `$` | Rename session       |
| `s` | List/switch sessions |
| `(` | Previous session     |
| `)` | Next session         |
