# Chapter 3: Sessions — One Session Per Project

[← Chapter 2: Panes](chapter-02-panes.md) | [Chapter 4: Copy Mode →](chapter-04-copy-mode.md)

---

## The Problem

You're working on the frontend. You get a Slack message: "The API is returning 500s." You need to jump to the backend project — different directory, different tools, different context. You don't want to tear down your frontend layout.

Dev: "One session per project. Frontend session has its windows and panes. Backend session has its own. Switch between them in a second. Each project stays exactly where you left it."

## What Is a Session?

A session is the top-level container in tmux:

```
Session "frontend"
  ├── Window 0: server (npm run dev)
  ├── Window 1: code (vim)
  └── Window 2: test (jest --watch)

Session "backend"
  ├── Window 0: server (python manage.py runserver)
  ├── Window 1: code (vim)
  └── Window 2: db (psql)

Session "devops"
  ├── Window 0: k8s (kubectl)
  └── Window 1: logs (stern)
```

Each session is independent. Its own windows, its own panes, its own working state.

## Creating Named Sessions

Always name your sessions. Unnamed sessions get numbers (0, 1, 2) — useless when you have five of them.

```bash
# From outside tmux:
tmux new -s frontend
tmux new -s backend
tmux new -s devops

# From inside tmux (command mode):
Ctrl-b  :new-session -s monitoring
```

The `-s` flag means "session name." Pick short, descriptive names.

## Detaching from a Session

```
Ctrl-b  d       →  detach from current session
```

Detaching doesn't kill anything. Your processes keep running. Your panes stay split. Your vim buffers stay open. You just disconnect your terminal from the session.

## Listing Sessions

```bash
# From outside tmux:
tmux ls

# Output:
# backend: 3 windows (created Mon Jun  2 09:15:00 2025)
# devops: 2 windows (created Mon Jun  2 09:20:00 2025)
# frontend: 3 windows (created Mon Jun  2 09:10:00 2025)
```

## Attaching to a Session

```bash
# Attach to a specific session:
tmux attach -t backend
tmux a -t backend          # short form

# Attach to the last session you used:
tmux a
```

If you're already inside tmux, you don't need to detach first — just switch.

## Switching Sessions (From Inside tmux)

This is where sessions become powerful. No detach/attach dance needed:

```
Ctrl-b  s       →  session picker (interactive list)
Ctrl-b  (       →  previous session
Ctrl-b  )       →  next session
```

The session picker (`Ctrl-b s`) shows all sessions with their windows. Navigate with arrow keys, press Enter to switch:

```
(0) + backend: 3 windows
(1) + devops: 2 windows
(2) + frontend: 3 windows (attached)
```

Expand a session with the right arrow to see its windows. Select any window directly.

Dev: "I use `Ctrl-b s` dozens of times a day. It's like Alt-Tab but for entire project contexts."

## Renaming Sessions

```
Ctrl-b  $       →  rename current session (type new name, press Enter)
```

Or from command mode:

```bash
Ctrl-b  :rename-session -t old-name new-name
```

## Killing Sessions

When you're done with a project:

```bash
# From outside tmux:
tmux kill-session -t backend

# Kill all sessions except the current one:
tmux kill-session -a

# Kill the tmux server entirely (all sessions):
tmux kill-server
```

From inside tmux:

```
Ctrl-b  :kill-session       →  kills the current session (you'll be moved to another)
```

## The Morning Routine

Dev's workflow every morning:

```bash
# Check what's still running from yesterday:
tmux ls

# If sessions exist, just attach:
tmux a -t frontend

# If starting fresh:
tmux new -s frontend -c ~/projects/frontend
tmux new -s backend -c ~/projects/backend -d    # -d = don't attach yet
tmux new -s devops -c ~/projects/infra -d

# Attach to the one you want to start with:
tmux a -t frontend
```

The `-c` flag sets the starting directory for the session. The `-d` flag creates the session without attaching to it (so you can create multiple sessions in sequence).

## Practical: Project-Based Sessions

Here's how Dev organizes a typical workday:

```bash
# Session: frontend
# Working directory: ~/projects/webapp
# Windows: server, code, test, storybook

# Session: backend
# Working directory: ~/projects/api
# Windows: server, code, test, db

# Session: devops
# Working directory: ~/projects/infra
# Windows: k8s, terraform, monitoring
```

Switching context is instant. `Ctrl-b s` → select "backend" → you're in the API project with all your windows and panes exactly as you left them.

## Nested Sessions (Don't)

If you SSH into a remote server that also runs tmux, you'll have tmux inside tmux. The prefix key gets confusing — which tmux receives it?

Solutions:
1. Use a different prefix on the remote machine (e.g., `Ctrl-a`)
2. Send the prefix to the inner tmux: `Ctrl-b Ctrl-b` sends `Ctrl-b` to the nested session
3. Avoid nesting — detach from local tmux before attaching to remote

Dev: "I remap the remote server's prefix to `Ctrl-a`. Local is `Ctrl-b`, remote is `Ctrl-a`. No confusion."

## Session Groups (Advanced)

Multiple clients can attach to the same session (useful for pair programming). But if you want independent views of the same session:

```bash
# Create a session group — both see the same windows but can view different ones:
tmux new-session -t existing-session -s my-view
```

This creates a new session linked to the existing one. Both share windows, but each can look at a different window independently.

## Session Commands Reference

| Keys / Command | Action |
|---|---|
| `tmux new -s name` | Create named session |
| `tmux a -t name` | Attach to session |
| `tmux ls` | List all sessions |
| `tmux kill-session -t name` | Kill a session |
| `Ctrl-b d` | Detach from session |
| `Ctrl-b s` | Session picker |
| `Ctrl-b (` | Previous session |
| `Ctrl-b )` | Next session |
| `Ctrl-b $` | Rename session |
| `Ctrl-b :new-session -s name` | New session from inside tmux |

## Exercise

1. Create three named sessions (don't attach to the first two):
   ```bash
   tmux new -s frontend -d
   tmux new -s backend -d
   tmux new -s devops
   ```
2. You're now in the "devops" session. Verify with `tmux ls`.
3. Use `Ctrl-b s` to see all three sessions in the picker.
4. Switch to "frontend" using the picker.
5. Create a window named "server" and run `python3 -m http.server 8000`.
6. Switch to "backend" with `Ctrl-b )`.
7. Detach with `Ctrl-b d`.
8. From outside, list sessions: `tmux ls` — all three are still running.
9. Reattach to frontend: `tmux a -t frontend` — your HTTP server is still going.
10. Kill the backend session: `tmux kill-session -t backend`.
11. Verify it's gone: `tmux ls`.

Dev: "Sessions keep your projects isolated. But there's one more thing you'll need constantly — scrolling back through output and copying text. That's copy mode, and it changes everything."

---

[← Chapter 2: Panes](chapter-02-panes.md) | [Chapter 4: Copy Mode →](chapter-04-copy-mode.md)
