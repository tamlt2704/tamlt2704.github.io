# Chapter 4: Copy Mode — Scroll and Copy Without a Mouse

[← Chapter 3: Sessions](chapter-03-sessions.md) | [Chapter 5: Configuration →](chapter-05-config.md)

---

## The Problem

A stack trace just flew past your terminal. You need to read it. You reach for the mouse to scroll up — but wait, you're in tmux. The mouse scrolls your outer terminal, not the tmux pane. The error is gone.

Dev: "Copy mode. Press `Ctrl-b [` and you can scroll, search, and copy anything from your terminal history. No mouse needed. It's like having a text editor for your terminal output."

## Entering Copy Mode

```
Ctrl-b  [       →  enter copy mode
```

Your pane freezes. The status bar shows `[0/500]` (your position in the scrollback buffer). Now you can navigate freely through everything that's been printed to this pane.

To exit copy mode without copying:

```
q               →  quit copy mode (vi mode)
Escape          →  quit copy mode (vi mode)
Ctrl-c          →  quit copy mode (emacs mode)
```

## Navigating in Copy Mode

Once in copy mode, you can move around:

### Basic Navigation (Works in Both Modes)

```
↑ ↓ ← →        →  move by character/line
Page Up         →  scroll up one page
Page Down       →  scroll down one page
```

### Vi Mode Navigation (if configured — see Chapter 5)

```
h j k l         →  left, down, up, right
Ctrl-u          →  half page up
Ctrl-d          →  half page down
g               →  go to top of buffer
G               →  go to bottom of buffer
0               →  beginning of line
$               →  end of line
w               →  next word
b               →  previous word
```

### Emacs Mode Navigation (default)

```
Ctrl-p          →  up
Ctrl-n          →  down
Ctrl-b          →  left (careful — this is also the prefix!)
Ctrl-f          →  forward
Meta-v          →  page up
Ctrl-v          →  page down
Meta-<          →  top of buffer
Meta->          →  bottom of buffer
```

Dev: "Set vi mode. Seriously. The emacs bindings conflict with the prefix key and it's a mess. One line in your config fixes it: `setw -g mode-keys vi`"

## Searching in Copy Mode

Find that error message buried 200 lines up:

### Vi Mode Search

```
/pattern        →  search forward (press Enter to execute)
?pattern        →  search backward
n               →  next match
N               →  previous match
```

### Emacs Mode Search

```
Ctrl-s          →  search forward
Ctrl-r          →  search backward
```

Example: You know the error contained "TypeError". Enter copy mode, type `/TypeError`, press Enter. tmux jumps to the first match. Press `n` to find the next one.

## Copying Text

This is the full workflow — enter copy mode, navigate to what you want, select it, copy it, then paste it.

### Vi Mode (Recommended)

```
1. Ctrl-b [              →  enter copy mode
2. Navigate to start of text you want
3. Space                 →  start selection
4. Move to end of text   →  selection highlights
5. Enter                 →  copy selection and exit copy mode
6. Ctrl-b ]              →  paste
```

### Emacs Mode

```
1. Ctrl-b [              →  enter copy mode
2. Navigate to start of text you want
3. Ctrl-Space            →  start selection
4. Move to end of text   →  selection highlights
5. Meta-w               →  copy selection and exit copy mode
6. Ctrl-b ]              →  paste
```

The copied text goes into tmux's paste buffer — it's separate from your system clipboard (we'll fix that in Chapter 7 with tmux-yank).

## The Paste Buffer

tmux maintains its own clipboard (paste buffer). You can have multiple items:

```bash
# List paste buffers (from command mode):
Ctrl-b  :list-buffers

# Paste the most recent buffer:
Ctrl-b  ]

# Choose which buffer to paste:
Ctrl-b  =       →  interactive buffer picker
```

Each time you copy something in copy mode, it's added to the buffer stack. The most recent copy is always what `Ctrl-b ]` pastes.

## Scrollback Buffer Size

By default, tmux keeps 2000 lines of history per pane. If you're tailing logs or running verbose builds, that fills up fast.

Increase it in your `.tmux.conf`:

```bash
set -g history-limit 10000    # 10,000 lines per pane
```

Dev: "I use 50000. Disk is cheap, and I never want to lose output. But don't go crazy — each pane uses memory for its buffer."

## Practical: Copying an Error Message

Real scenario — your build fails and you need to search for the error:

```bash
# 1. The build just failed. Error scrolled past.
# 2. Enter copy mode:
Ctrl-b  [

# 3. Search backward for the error:
?Error

# 4. Found it! Now select the full error message:
#    Move to the start of the line: 0
#    Start selection: Space
#    Move to end of the relevant text: $ (or multiple j's for multi-line)
#    Copy: Enter

# 5. Now paste it somewhere useful:
#    Switch to another pane, open a browser, whatever
Ctrl-b  ]
```

## Practical: Copying a File Path from Output

```bash
# ls output shows a file you need:
# drwxr-xr-x  5 dev  staff  160 Jun  2 10:30 src/components/Header.tsx

# 1. Enter copy mode: Ctrl-b [
# 2. Navigate to the filename
# 3. Press Space to start selection
# 4. Select just "src/components/Header.tsx"
# 5. Press Enter to copy
# 6. In another pane: vim Ctrl-b ]
#    This pastes the path directly into your command
```

## Mouse Mode (Alternative)

If you enable mouse support (Chapter 5), you can:
- Scroll with the mouse wheel (auto-enters copy mode)
- Click and drag to select text
- Right-click to paste

But Dev recommends learning the keyboard way first: "Mouse mode is a crutch. Learn copy mode properly and you'll be faster."

## Copy Mode Commands Reference

| Keys (Vi Mode) | Action |
|---|---|
| `Ctrl-b [` | Enter copy mode |
| `q` or `Escape` | Exit copy mode |
| `h j k l` | Navigate (vi-style) |
| `/pattern` | Search forward |
| `?pattern` | Search backward |
| `n` / `N` | Next / previous match |
| `Space` | Start selection |
| `Enter` | Copy selection & exit |
| `Ctrl-b ]` | Paste buffer |
| `Ctrl-b =` | Choose buffer to paste |
| `g` / `G` | Top / bottom of buffer |
| `Ctrl-u` / `Ctrl-d` | Half page up / down |

## Exercise

1. Open a tmux session and run: `seq 1 500` (prints 500 lines of numbers)
2. Enter copy mode: `Ctrl-b [`
3. Scroll up to find the number "42" — use `/42` to search
4. Press `n` to cycle through matches until you find the line with just "42"
5. Select the line: press `0` (start of line), `Space` (start selection), `$` (end of line), `Enter` (copy)
6. Exit copy mode (it exits automatically after copying)
7. Paste with `Ctrl-b ]` — you should see "42" appear at your prompt
8. Now run: `echo "This is a long error message with important details about the failure"`
9. Enter copy mode, search for "important", select from "important" to "failure", copy it
10. Paste it into a new command: `echo "Ctrl-b ]"` — verify the text appears

Dev: "Copy mode is essential. But right now you're using tmux's defaults — and some of them are awkward. Let's fix that. Time to write your own config."

---

[← Chapter 3: Sessions](chapter-03-sessions.md) | [Chapter 5: Configuration →](chapter-05-config.md)
