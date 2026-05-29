# Chapter 7: Productive Workflows

[prev: Plugins](chapter-06-plugins.md) | [next: Overview](chapter-00-overview.md)

## Project Sessions (One Per Project)

Keep each project in its own named session:

```bash
tmux new -s webapp
tmux new -s api
tmux new -s dotfiles
```

Switch between them with `C-b s` (session list) or `C-b )` / `C-b (`.

## Scripted Session Setup

Automate your dev environment with a shell script:

```bash
#!/bin/bash
# ~/.tmux/scripts/webapp.sh

SESSION="webapp"
PROJECT_DIR="~/projects/webapp"

# Create session (detached)
tmux new-session -d -s $SESSION -c $PROJECT_DIR

# Window 1: Editor
tmux rename-window -t $SESSION:1 'editor'
tmux send-keys -t $SESSION:1 'nvim .' Enter

# Window 2: Server
tmux new-window -t $SESSION:2 -n 'server' -c $PROJECT_DIR
tmux send-keys -t $SESSION:2 'npm run dev' Enter

# Window 3: Logs + Git (split)
tmux new-window -t $SESSION:3 -n 'logs' -c $PROJECT_DIR
tmux split-window -h -t $SESSION:3 -c $PROJECT_DIR
tmux send-keys -t $SESSION:3.1 'tail -f logs/dev.log' Enter
tmux send-keys -t $SESSION:3.2 'lazygit' Enter

# Focus on editor
tmux select-window -t $SESSION:1

# Attach
tmux attach -t $SESSION
```

```bash
# Make executable and run
chmod +x ~/.tmux/scripts/webapp.sh
~/.tmux/scripts/webapp.sh
```

## tmuxinator

YAML-based session templates:

```bash
# Install
gem install tmuxinator

# Create a project
tmuxinator new webapp
```

Template file (`~/.config/tmuxinator/webapp.yml`):

```bash
# ~/.config/tmuxinator/webapp.yml
name: webapp
root: ~/projects/webapp

windows:
  - editor:
      panes:
        - nvim .
  - server:
      panes:
        - npm run dev
  - logs:
      layout: even-horizontal
      panes:
        - tail -f logs/dev.log
        - lazygit
```

```bash
# Start the session
tmuxinator start webapp

# Stop
tmuxinator stop webapp

# List templates
tmuxinator list
```

## tmuxp

Python-based alternative (JSON/YAML):

```bash
# Install
pip install tmuxp

# Load a session
tmuxp load ~/.tmuxp/webapp.yaml
```

## Pair Programming (Shared Sessions)

Two users can share the same tmux session:

```bash
# User A creates a session
tmux new -s pair

# User B attaches to the same session
tmux attach -t pair
```

Both see the same output and can type. For independent views of the same session:

```bash
# User B attaches with a separate window group
tmux new -t pair -s pair-b
```

## IDE-like Layout

```bash
#!/bin/bash
# IDE layout: editor top-left, terminal bottom-left, file tree right

SESSION="ide"
tmux new-session -d -s $SESSION

# Main editor pane
tmux send-keys 'nvim .' Enter

# Bottom terminal
tmux split-window -v -p 30
tmux send-keys 'clear' Enter

# Right sidebar (file tree)
tmux select-pane -t 0
tmux split-window -h -p 25
tmux send-keys 'tree -L 2' Enter

# Focus on editor
tmux select-pane -t 0

tmux attach -t $SESSION
```

## Dev Environment (Editor + Server + Logs + Git)

```bash
#!/bin/bash
SESSION="dev"
DIR="$(pwd)"

tmux new-session -d -s $SESSION -c $DIR

# Window 1: Editor (full screen)
tmux rename-window 'edit'
tmux send-keys 'nvim .' Enter

# Window 2: Server + Logs (split)
tmux new-window -n 'run' -c $DIR
tmux send-keys 'npm run dev' Enter
tmux split-window -v -p 40 -c $DIR
tmux send-keys 'npm run logs' Enter

# Window 3: Git
tmux new-window -n 'git' -c $DIR
tmux send-keys 'lazygit' Enter

# Window 4: Shell (spare)
tmux new-window -n 'sh' -c $DIR

# Start on editor
tmux select-window -t $SESSION:1
tmux attach -t $SESSION
```

## Tips

- Name sessions after projects for quick switching
- Use `tmux has-session -t name` in scripts to avoid duplicates
- Combine with tmux-resurrect to persist layouts across reboots
- Use `-c` flag to set working directory for new windows/panes

## Cheat Sheet

| Workflow                | Tool/Command                        |
| ----------------------- | ----------------------------------- |
| One session per project | `tmux new -s projectname`           |
| Switch sessions         | `C-b s` or `C-b )`/`(`              |
| Scripted setup          | Shell script with tmux commands     |
| YAML templates          | tmuxinator or tmuxp                 |
| Pair programming        | Both users `tmux attach -t session` |
| Avoid duplicates        | `tmux has-session -t name`          |
| Set working dir         | `-c ~/path` flag                    |
