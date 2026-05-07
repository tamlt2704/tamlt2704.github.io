# Chapter 2: Panes — See Everything at Once

[← Chapter 1: Windows](chapter-01-windows.md) | [Chapter 3: Sessions →](chapter-03-sessions.md)

---

## The Problem

You're debugging a failing test. You need to see the test output, the source code, and the server logs — all at the same time. Switching between windows means you lose context every time you flip.

Dev: "Split your window into panes. Editor on the left, tests top-right, logs bottom-right. You see everything. You miss nothing."

## Splitting Panes

Two ways to split:

```
Ctrl-b  %       →  split vertically (left | right)
Ctrl-b  "       →  split horizontally (top / bottom)
```

Think of it this way:
- `%` has a vertical line in it — it creates a vertical divider
- `"` has horizontal lines — it creates a horizontal divider

Start with a full window, then split:

```
┌─────────────────────┐       ┌──────────┬──────────┐
│                     │  %    │          │          │
│      original       │  →    │  left    │  right   │
│                     │       │          │          │
└─────────────────────┘       └──────────┴──────────┘

┌─────────────────────┐       ┌─────────────────────┐
│                     │  "    │        top          │
│      original       │  →    ├─────────────────────┤
│                     │       │       bottom        │
└─────────────────────┘       └─────────────────────┘
```

## Navigating Between Panes

```
Ctrl-b  ←       →  move to the pane on the left
Ctrl-b  →       →  move to the pane on the right
Ctrl-b  ↑       →  move to the pane above
Ctrl-b  ↓       →  move to the pane below
```

The active pane has a highlighted border. You always know where your cursor lives.

Dev: "Arrow keys are fine for 2-3 panes. Once you get comfortable, you can bind keys for faster switching — but don't optimize too early."

## Resizing Panes

Need more space for your editor? Shrink the terminal pane:

```
Ctrl-b  Ctrl-←      →  resize left (1 cell)
Ctrl-b  Ctrl-→      →  resize right (1 cell)
Ctrl-b  Ctrl-↑      →  resize up (1 cell)
Ctrl-b  Ctrl-↓      →  resize down (1 cell)
```

For bigger jumps, use the command prompt:

```
Ctrl-b  :resize-pane -D 5      →  grow down 5 cells
Ctrl-b  :resize-pane -U 5      →  shrink up 5 cells
Ctrl-b  :resize-pane -L 10     →  grow left 10 cells
Ctrl-b  :resize-pane -R 10     →  grow right 10 cells
```

The `-D`, `-U`, `-L`, `-R` flags mean Down, Up, Left, Right — the direction the border moves.

## Zooming a Pane

Sometimes you need one pane fullscreen for a moment — reading a stack trace, editing a long file — then back to the split view.

```
Ctrl-b  z       →  toggle zoom (fullscreen) for current pane
```

When zoomed, the status bar shows a `Z` flag. Press `Ctrl-b z` again to unzoom. Your layout is preserved exactly as it was.

Dev: "Zoom is my most-used pane command. Quick fullscreen to read something, then back to the split. No rearranging needed."

## Closing Panes

```
Ctrl-b  x       →  close current pane (confirms with y/n)
exit            →  close the shell in the pane (pane disappears)
```

When you close the last pane in a window, the window itself closes.

## Rotating and Swapping Panes

Don't like the order? Move panes around:

```
Ctrl-b  {       →  swap current pane with the previous one
Ctrl-b  }       →  swap current pane with the next one
Ctrl-b  Space   →  cycle through preset layouts
```

The preset layouts cycle through: even-horizontal, even-vertical, main-horizontal, main-vertical, and tiled. Handy when you want a quick rearrangement without manual resizing.

## Preset Layouts

tmux has built-in layouts you can apply instantly:

```bash
# From command mode (Ctrl-b :)
select-layout even-horizontal    # all panes side by side, equal width
select-layout even-vertical      # all panes stacked, equal height
select-layout main-horizontal    # one big pane on top, rest below
select-layout main-vertical      # one big pane on left, rest on right
select-layout tiled              # grid layout
```

Or just keep pressing `Ctrl-b Space` to cycle through them.

## Practical Layout: The Developer Split

Here's the layout Dev uses every day — editor takes 60% of the screen on the left, terminal and tests share the right side:

```
┌────────────────────────┬─────────────────┐
│                        │   terminal      │
│                        │   (shell)       │
│       editor           ├─────────────────┤
│       (vim/code)       │   tests         │
│                        │   (npm test)    │
│                        │                 │
└────────────────────────┴─────────────────┘
```

How to create it:

```bash
# Start in a fresh window
# Step 1: Split vertically (creates left | right)
Ctrl-b  %

# Step 2: Move to the right pane
Ctrl-b  →

# Step 3: Split the right pane horizontally (creates top / bottom)
Ctrl-b  "

# Step 4: Go back to the left pane and resize it bigger
Ctrl-b  ←
Ctrl-b  :resize-pane -R 20

# Step 5: Run your programs
# Left pane: vim .
# Top-right: shell commands
# Bottom-right: npm test --watch
```

Now you edit code on the left, run commands top-right, and watch tests auto-run bottom-right. When a test fails, you see it immediately without switching context.

## Converting Panes to Windows (and Back)

Sometimes a pane deserves its own window:

```
Ctrl-b  !       →  break current pane into a new window
```

To pull a window back into a pane:

```bash
# From command mode:
Ctrl-b  :join-pane -s :2    # join window 2 as a pane in current window
```

## Pane Commands Reference

| Keys | Action |
|---|---|
| `Ctrl-b %` | Split vertically (left/right) |
| `Ctrl-b "` | Split horizontally (top/bottom) |
| `Ctrl-b ←↑→↓` | Navigate between panes |
| `Ctrl-b Ctrl-←↑→↓` | Resize pane (1 cell) |
| `Ctrl-b z` | Zoom/unzoom pane |
| `Ctrl-b x` | Close pane (with confirm) |
| `Ctrl-b {` | Swap pane with previous |
| `Ctrl-b }` | Swap pane with next |
| `Ctrl-b Space` | Cycle preset layouts |
| `Ctrl-b !` | Break pane into new window |
| `Ctrl-b q` | Show pane numbers briefly |

## Exercise

1. Start a fresh tmux session: `tmux new -s panes-practice`
2. Split the window vertically with `Ctrl-b %`
3. In the right pane, split horizontally with `Ctrl-b "`
4. You now have 3 panes. Navigate between them with arrow keys.
5. In the left pane, run `top`
6. In the top-right pane, run `ls -la /`
7. In the bottom-right pane, run `watch date`
8. Resize the left pane to be wider: `Ctrl-b :resize-pane -R 15`
9. Zoom into the left pane with `Ctrl-b z` — notice `top` goes fullscreen
10. Unzoom with `Ctrl-b z` — your 3-pane layout is back
11. Close the bottom-right pane with `Ctrl-b x`

Dev: "Panes let you see everything at once. But what happens when you have multiple projects? You don't want your frontend panes mixed with your backend panes. That's where sessions come in."

---

[← Chapter 1: Windows](chapter-01-windows.md) | [Chapter 3: Sessions →](chapter-03-sessions.md)
