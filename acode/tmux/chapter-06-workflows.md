# Chapter 6: Workflows — Real Developer Workflows

[← Chapter 5: Configuration](chapter-05-config.md) | [Chapter 7: Plugins →](chapter-07-plugins.md)

---

## The Problem

You know the commands. You can split panes, create sessions, copy text. But every morning you spend 5 minutes recreating the same layout — split here, resize there, cd into this directory, start that server. It's tedious.

Dev: "Script it. I open my laptop, type one command, and my entire dev environment appears — 3 sessions, 8 windows, 12 panes, all in the right directories with the right commands running. Takes 2 seconds."

## The Morning Routine

Dev's daily startup:

```bash
# Check if sessions from yesterday are still alive:
tmux ls

# If they are (laptop was sleeping, not rebooted):
tmux a    # Done. Everything is where you left it.

# If starting fresh:
./dev-start.sh    # Script creates everything.
```

tmux sessions survive terminal closes, SSH disconnects, and sleep/wake cycles. They only die on reboot (unless you use tmux-resurrect — Chapter 7).

## Layout Scripts

A shell script that creates your perfect environment:

```bash
#!/bin/bash
# dev-start.sh — Create my development environment
SESSION="work"

tmux kill-session -t $SESSION 2>/dev/null
tmux new-session -d -s $SESSION -n editor -c ~/projects/webapp
tmux split-window -h -t $SESSION:editor -c ~/projects/webapp
tmux resize-pane -t $SESSION:editor.2 -x 60

tmux new-window -t $SESSION -n server -c ~/projects/webapp
tmux send-keys -t $SESSION:server 'npm run dev' Enter

tmux new-window -t $SESSION -n test -c ~/projects/webapp
tmux send-keys -t $SESSION:test 'npm test -- --watch' Enter

tmux new-window -t $SESSION -n git -c ~/projects/webapp
tmux send-keys -t $SESSION:git 'git status' Enter

tmux select-window -t $SESSION:editor
tmux attach -t $SESSION
```

Save it, `chmod +x dev-start.sh`, run it. Two seconds later: 4 windows, server running, tests watching.

## The `send-keys` Command

The magic behind layout scripts:

```bash
tmux send-keys -t session:window.pane 'command here' Enter
```

The `Enter` at the end simulates pressing Enter. Without it, the command is typed but not executed.

## Workflow 1: Full-Stack Development

Frontend + backend + database + logs, all visible:

```bash
#!/bin/bash
# fullstack.sh

# Frontend session
tmux new-session -d -s frontend -n server -c ~/projects/frontend
tmux send-keys -t frontend:server 'npm run dev' Enter
tmux new-window -t frontend -n code -c ~/projects/frontend
tmux new-window -t frontend -n test -c ~/projects/frontend
tmux send-keys -t frontend:test 'npm test -- --watch' Enter

# Backend session
tmux new-session -d -s backend -n server -c ~/projects/api
tmux send-keys -t backend:server 'python manage.py runserver' Enter
tmux new-window -t backend -n code -c ~/projects/api
tmux new-window -t backend -n test -c ~/projects/api
tmux send-keys -t backend:test 'pytest --watch' Enter
tmux new-window -t backend -n db -c ~/projects/api
tmux send-keys -t backend:db 'pgcli mydb' Enter

# Monitoring session
tmux new-session -d -s monitor -n logs -c ~/projects
tmux split-window -h -t monitor:logs
tmux send-keys -t monitor:logs.1 'tail -f ~/projects/frontend/.next/server.log' Enter
tmux send-keys -t monitor:logs.2 'tail -f ~/projects/api/debug.log' Enter

# Attach to frontend
tmux attach -t frontend
```

Switch between projects with `Ctrl-b s`. Each has its own context, its own state.

## Workflow 2: Remote Server Management

SSH + tmux = indestructible remote sessions:

```bash
# On your local machine:
ssh production-server

# On the remote server, start or reattach:
tmux a || tmux new -s admin
```

If your SSH connection drops (WiFi, VPN, laptop sleep), the remote tmux session keeps running. Reconnect and reattach — nothing lost.

```bash
#!/bin/bash
# remote-admin.sh — run ON the remote server
tmux new-session -d -s admin -n logs
tmux send-keys -t admin:logs 'journalctl -f' Enter
tmux split-window -v -t admin:logs
tmux send-keys -t admin:logs.2 'tail -f /var/log/nginx/error.log' Enter
tmux new-window -t admin -n htop
tmux send-keys -t admin:htop 'htop' Enter
tmux new-window -t admin -n deploy
tmux select-window -t admin:logs
tmux attach -t admin
```

## Workflow 3: Pair Programming

Two developers, one tmux session:

```bash
# Developer 1 creates the session:
tmux new -s pairing

# Developer 2 attaches to the same session:
tmux attach -t pairing
```

Both see the same windows and panes. When one types, the other sees it. For independent views (same session, different active windows):

```bash
tmux new-session -t pairing -s dev2-view
```

## Workflow 4: Monitoring Dashboard

A dedicated monitoring session — 4 panes showing system health:

```bash
#!/bin/bash
# monitor.sh
tmux new-session -d -s monitor -n dashboard
tmux send-keys -t monitor:dashboard 'htop' Enter
tmux split-window -h -t monitor:dashboard
tmux send-keys 'watch -n 2 "ss -tuln"' Enter
tmux split-window -v -t monitor:dashboard.1
tmux send-keys 'tail -f /var/log/app/production.log' Enter
tmux split-window -v -t monitor:dashboard.2
tmux send-keys 'watch -n 30 "df -h"' Enter
tmux select-layout -t monitor:dashboard tiled
tmux attach -t monitor
```

## tmuxinator: Declarative Session Configs

Tired of bash scripts? tmuxinator uses YAML to define layouts:

```bash
# Install:
gem install tmuxinator

# Create a project:
tmuxinator new webapp
```

This opens a YAML file:

```yaml
# ~/.tmuxinator/webapp.yml
name: webapp
root: ~/projects/webapp

windows:
  - editor:
      layout: main-vertical
      panes:
        - vim .
        - # empty shell
  - server:
      panes:
        - npm run dev
  - test:
      panes:
        - npm test -- --watch
  - git:
      panes:
        - git status
```

Start it:

```bash
tmuxinator start webapp
# or shorter:
mux webapp
```

Stop it:

```bash
tmuxinator stop webapp
```

## tmuxp: Python Alternative

Same idea, Python instead of Ruby: `pip install tmuxp`. Define sessions in YAML, load with `tmuxp load webapp`. The format is nearly identical to tmuxinator.

## Tips for Layout Scripts

1. Always use `-d` (detached) when creating sessions — attach at the end
2. Use `-c` for directories — each pane starts in the right place
3. Add `2>/dev/null` to kill commands — suppress "not found" errors
4. Name everything — sessions, windows. Future you will thank present you.

## Workflow Commands Reference

| Command | What It Does |
|---|---|
| `tmux new-session -d -s name -n win` | Create detached session with named window |
| `tmux new-window -t sess -n name -c dir` | Add window to session |
| `tmux split-window -h -t sess:win` | Split pane in specific window |
| `tmux send-keys -t sess:win.pane 'cmd' Enter` | Type command in pane |
| `tmux select-window -t sess:win` | Switch to window |
| `tmux resize-pane -t sess:win.pane -x 80` | Resize pane width |
| `tmux select-layout -t sess:win tiled` | Apply layout |
| `tmuxinator start project` | Start tmuxinator project |
| `tmuxp load project` | Start tmuxp project |

## Exercise

Write a shell script that creates your ideal development layout:

1. Create `my-dev-layout.sh`
2. It should create a named session with at least 3 windows
3. At least one window should have split panes
4. Use `send-keys` to start at least one command automatically
5. Make it idempotent (kill existing session first)

Template:

```bash
#!/bin/bash
SESSION="myproject"
PROJECT_DIR="$HOME/projects/myproject"

tmux kill-session -t $SESSION 2>/dev/null
tmux new-session -d -s $SESSION -n editor -c $PROJECT_DIR
# Add your windows and panes here...
tmux attach -t $SESSION
```

Bonus: Convert your script to a tmuxinator YAML config and compare.

Dev: "I have a layout script for every project. Some people use tmuxinator, some use plain bash. Doesn't matter — the point is: one command, perfect environment, every time. Now let's add superpowers with plugins."

---

[← Chapter 5: Configuration](chapter-05-config.md) | [Chapter 7: Plugins →](chapter-07-plugins.md)
