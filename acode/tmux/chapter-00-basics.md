# Chapter 0: Install & First Session

[Chapter 1: Windows →](chapter-01-windows.md)

---

## The Problem

You open 8 terminal tabs. You lose track of which is which. You accidentally close one — the build process dies. You SSH into a server, start a deploy, your laptop sleeps — deploy dies.

Dev: "tmux solves all of that. One command to start. One command to reconnect. Everything survives."

## Start tmux

```bash
tmux
```

That's it. You're inside a tmux session. It looks almost the same — but notice the green bar at the bottom. That's the tmux status bar. You're now inside a persistent session.

## The Prefix Key

tmux commands use a **prefix** — a key combo that tells tmux "the next key is a command, not terminal input."

Default prefix: **`Ctrl-b`**

You press `Ctrl-b`, release both keys, then press the command key. It's a two-step action.

```
Ctrl-b  then  ?     →  show all keybindings (your cheat sheet)
Ctrl-b  then  d     →  detach (leave session running in background)
Ctrl-b  then  c     →  create new window
Ctrl-b  then  ,     →  rename current window
```

## Detach and Reattach — The Killer Feature

```bash
# Inside tmux, start something long-running:
ping google.com

# Detach (session keeps running in background):
# Press: Ctrl-b  then  d

# You're back in your normal terminal. tmux is still running.

# Reattach:
tmux attach
# or
tmux a

# The ping is still going! Nothing was lost.
```

This is why tmux exists. Your session survives:
- Closing the terminal window
- SSH disconnections
- Laptop sleep (if the server stays up)
- Logging out and back in

## Session Basics

```bash
# Start a new named session
tmux new -s work

# Detach
Ctrl-b  d

# List sessions
tmux ls
# Output: work: 1 windows (created Mon May  5 10:00:00 2026)

# Attach to a specific session
tmux attach -t work
# or
tmux a -t work

# Kill a session (from outside)
tmux kill-session -t work
```

## Your First Workflow

```bash
# 1. Start a session for your project
tmux new -s myproject

# 2. You're in window 0. Start your dev server:
npm run dev

# 3. Create a new window for editing:
Ctrl-b  c

# 4. You're in window 1. Open your editor:
vim src/app.js

# 5. Switch between windows:
Ctrl-b  0    →  go to window 0 (dev server)
Ctrl-b  1    →  go to window 1 (editor)

# 6. Done for the day? Detach:
Ctrl-b  d

# 7. Tomorrow, reattach:
tmux a -t myproject
# Everything is exactly where you left it.
```

## Essential Commands (Day 1)

| Keys | Action |
|---|---|
| `Ctrl-b d` | Detach from session |
| `Ctrl-b c` | Create new window |
| `Ctrl-b 0-9` | Switch to window by number |
| `Ctrl-b ,` | Rename current window |
| `Ctrl-b &` | Close current window |
| `Ctrl-b ?` | Show all keybindings |

Outside tmux:

| Command | Action |
|---|---|
| `tmux` | Start new session |
| `tmux new -s name` | Start named session |
| `tmux a` or `tmux attach` | Reattach to last session |
| `tmux a -t name` | Reattach to named session |
| `tmux ls` | List all sessions |
| `tmux kill-session -t name` | Kill a session |

## Verify

- [ ] `tmux` starts a session (green bar at bottom)
- [ ] `Ctrl-b d` detaches (you're back in normal terminal)
- [ ] `tmux a` reattaches (you're back in the session)
- [ ] `Ctrl-b c` creates a second window
- [ ] `Ctrl-b 0` and `Ctrl-b 1` switch between windows

Dev: "That's the foundation. Windows are like tabs. But tmux can do something tabs can't — split a single window into multiple panes."

---

[Chapter 1: Windows →](chapter-01-windows.md)
