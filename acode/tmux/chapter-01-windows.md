# Chapter 1: Windows

[← Chapter 0: Basics](chapter-00-basics.md) | [Chapter 2: Panes →](chapter-02-panes.md)

---

## The Problem

You have one window. Your dev server runs there. But you also need to run tests, check git status, and edit files. You keep creating new windows and losing track of which is which.

Dev: "Name your windows. Think of them as workspaces — one per concern."

## Creating and Switching Windows

```
Ctrl-b  c       →  create new window
Ctrl-b  n       →  next window
Ctrl-b  p       →  previous window
Ctrl-b  0-9     →  jump to window by number
Ctrl-b  w       →  list all windows (interactive picker)
Ctrl-b  l       →  toggle to last active window
```

## Naming Windows

By default, windows are named after the running process (`bash`, `vim`, `node`). That's useless when you have 5 windows. Name them:

```
Ctrl-b  ,       →  rename current window (type a name, press Enter)
```

Good naming convention:

```
0: server     ← dev server running
1: code       ← editor
2: test       ← test runner
3: git        ← git operations
4: db         ← database console
```

The status bar shows all windows with their names. You always know where you are.

## Closing Windows

```
Ctrl-b  &       →  close current window (confirms with y/n)
```

Or just `exit` the shell inside the window — when the last pane in a window closes, the window closes.

## Reordering Windows

```bash
# From inside tmux (command mode):
Ctrl-b  :       →  opens the tmux command prompt

# Then type:
swap-window -t 0        # move current window to position 0
move-window -t 5        # move current window to position 5
```

Or add to `.tmux.conf` for keybindings:

```bash
# Shift+Left/Right to reorder
bind-key -n S-Left swap-window -t -1\; select-window -t -1
bind-key -n S-Right swap-window -t +1\; select-window -t +1
```

## Finding Windows

With many windows open, `Ctrl-b w` shows an interactive list:

```
(0) 0: server   ← highlight and press Enter to switch
(1) 1: code
(2) 2: test
(3) 3: git
```

Or search by name:

```
Ctrl-b  f       →  find window by name (type partial name)
```

## Practical Layout: The Developer Setup

```bash
# Start a session with named windows
tmux new -s project

# Window 0: server
Ctrl-b  ,  →  type "server"  →  Enter
npm run dev

# Window 1: code
Ctrl-b  c
Ctrl-b  ,  →  type "code"  →  Enter
vim .

# Window 2: test
Ctrl-b  c
Ctrl-b  ,  →  type "test"  →  Enter
npm test -- --watch

# Window 3: git
Ctrl-b  c
Ctrl-b  ,  →  type "git"  →  Enter
git status
```

Now your status bar reads: `0:server  1:code*  2:test  3:git`

The `*` marks the active window. Switch instantly with `Ctrl-b 0` through `Ctrl-b 3`.

## Window Commands Reference

| Keys | Action |
|---|---|
| `Ctrl-b c` | Create window |
| `Ctrl-b ,` | Rename window |
| `Ctrl-b &` | Close window |
| `Ctrl-b n` | Next window |
| `Ctrl-b p` | Previous window |
| `Ctrl-b 0-9` | Go to window N |
| `Ctrl-b w` | List/pick window |
| `Ctrl-b l` | Last active window |
| `Ctrl-b f` | Find window by name |

## Exercise

1. Create a session with 4 windows named: server, code, test, shell
2. Run `top` in the server window
3. Run `ls -la` in the shell window
4. Switch between them using number keys
5. Use `Ctrl-b w` to see the list
6. Close the shell window with `Ctrl-b &`
7. Verify only 3 windows remain

Dev: "Windows are great for separate concerns. But sometimes you need to see two things at once — your code AND the test output, side by side. That's panes."

---

[← Chapter 0: Basics](chapter-00-basics.md) | [Chapter 2: Panes →](chapter-02-panes.md)
