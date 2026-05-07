# Emacs Rocks! — A Bite-Sized Guide

Short episodes. One trick each. Instantly useful. In the spirit of [emacsrocks.com](http://emacsrocks.com/).

---

## Episode 01: "Install It and Don't Panic"

The first time you open Emacs, you'll want to close it. That's normal.

```
# Install
brew install emacs        # macOS
sudo apt install emacs    # Ubuntu

# Open
emacs

# Close (this is the first thing everyone googles)
C-x C-c
```

`C-x` means hold Ctrl, press x. `M-x` means hold Alt (Meta), press x.

That's it. You can now open and close Emacs. You're ahead of 50% of people who tried.

---

## Episode 02: "The Only Keybindings You Need (Day 1)"

Don't memorize 200 keybindings. Start with 10.

| Keys | What It Does | You'll Use It |
|---|---|---|
| `C-x C-f` | Open a file | Every time |
| `C-x C-s` | Save | Every time |
| `C-x C-c` | Quit Emacs | When you give up (you won't) |
| `C-g` | Cancel anything | When you're stuck |
| `C-x b` | Switch buffer | Constantly |
| `C-x 1` | One window (close others) | When confused |
| `C-x 2` | Split horizontal | Compare files |
| `C-x 3` | Split vertical | Side by side |
| `C-s` | Search forward | Finding stuff |
| `M-x` | Run any command by name | The escape hatch |

`C-g` is your panic button. If anything goes wrong, mash `C-g`.

---

## Episode 03: "Moving Around Without a Mouse"

Your hands never leave the keyboard. That's the point.

```
C-f  → forward one char          C-b  → back one char
C-n  → next line                 C-p  → previous line
C-a  → beginning of line         C-e  → end of line
M-f  → forward one word          M-b  → back one word
C-v  → page down                 M-v  → page up
M-<  → beginning of buffer       M->  → end of buffer
M-g g → go to line number
```

**The pattern**: `C-` moves by character/line. `M-` moves by word/paragraph. Once you see the pattern, you never forget it.

---

## Episode 04: "Kill, Yank, and the Kill Ring"

Emacs doesn't have copy/paste. It has something better.

```
C-k     → kill (cut) to end of line
C-w     → kill region (selection)
M-w     → copy region (don't kill)
C-y     → yank (paste)
M-y     → cycle through kill ring (after C-y)
C-SPC   → set mark (start selection)
```

The **kill ring** remembers everything you've killed. `C-y` pastes the last thing. `M-y` cycles through previous kills. It's clipboard history built in.

```
;; Kill 3 lines, then paste the first one back:
C-k C-k C-k    → kill 3 lines
C-y             → paste the 3rd (most recent)
M-y             → nope, I want the 2nd
M-y             → nope, the 1st
```

---

## Episode 05: "Undo, Redo, and the Undo Tree"

Emacs undo is weird. And brilliant.

```
C-/     → undo
C-g C-/ → redo (undo the undo)
```

Emacs doesn't have a separate redo. Instead, undo is a linear history. If you undo 3 times, then type something, the 3 undos become part of the history — you can undo *the undos*.

Install `undo-tree` for a visual tree:

```elisp
(use-package undo-tree
  :config (global-undo-tree-mode))
;; C-x u → visual undo tree
```

---

## Episode 06: "Buffers, Windows, and Frames"

Three concepts. Once you get them, Emacs clicks.

```
Buffer  = an open file (or scratch pad, or shell, or anything)
Window  = a visible rectangle showing a buffer
Frame   = an OS window containing one or more windows
```

```
C-x b       → switch buffer (type name, Tab to complete)
C-x C-b     → list all buffers
C-x k       → kill (close) current buffer
C-x 2       → split window horizontally
C-x 3       → split window vertically
C-x 1       → close all other windows
C-x o       → switch to other window
C-x 0       → close this window
```

You can have 50 buffers open and only show 2 at a time. Buffers are cheap. Windows are views.

---

## Episode 07: "M-x: The Command That Runs All Commands"

`M-x` is the most powerful key in Emacs. It runs any command by name.

```
M-x shell           → open a shell
M-x replace-string  → find and replace
M-x tetris           → yes, really
M-x doctor           → Emacs therapist (also really)
M-x describe-key     → "what does this key do?"
M-x describe-function → "what does this function do?"
```

Don't know the keybinding? `M-x` + type what you want. Tab completes.

Install `which-key` to see available keys after a prefix:

```elisp
(use-package which-key
  :config (which-key-mode))
;; Press C-x, wait 1 second → see all C-x commands
```

---

## Episode 08: "Your First init.el"

Emacs is configured with Elisp. Your config lives in `~/.emacs.d/init.el`.

```elisp
;; ~/.emacs.d/init.el

;; ── Package Manager ─────────────────────────────
(require 'package)
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/"))
(package-initialize)

;; use-package: the sane way to manage packages
(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))
(require 'use-package)
(setq use-package-always-ensure t)

;; ── Basics ──────────────────────────────────────
(setq inhibit-startup-message t)        ; no splash screen
(tool-bar-mode -1)                       ; no toolbar
(menu-bar-mode -1)                       ; no menu bar
(scroll-bar-mode -1)                     ; no scrollbar
(global-display-line-numbers-mode 1)     ; line numbers
(setq-default indent-tabs-mode nil)      ; spaces, not tabs
(setq-default tab-width 4)

;; ── Theme ───────────────────────────────────────
(use-package doom-themes
  :config (load-theme 'doom-one t))

;; ── Which Key ───────────────────────────────────
(use-package which-key
  :config (which-key-mode))
```

Restart Emacs. It looks completely different. You're in control now.

---

## Episode 09: "Search and Replace Like a Pro"

```
C-s         → incremental search (type to search, C-s for next match)
C-r         → search backward
C-s C-w     → search for word at cursor
M-%         → query replace (y/n for each match)
C-M-%       → query replace with regex
```

**Incremental search** is magic: you type, it finds. Each character narrows the results. `C-s` jumps to the next match. `C-g` cancels and goes back to where you started.

```
;; Replace "foo" with "bar" in the whole buffer:
M-%  foo  RET  bar  RET
;; Then: y = replace, n = skip, ! = replace all remaining
```

---

## Episode 10: "Dired — The File Manager"

Dired turns a directory listing into an editable buffer. Yes, you edit filenames like text.

```
C-x d       → open dired (pick a directory)
```

Inside dired:

| Key | Action |
|---|---|
| `RET` | Open file/directory |
| `^` | Go up one directory |
| `d` | Mark for deletion |
| `x` | Execute deletions |
| `R` | Rename/move |
| `C` | Copy |
| `+` | Create directory |
| `g` | Refresh |
| `q` | Quit dired |

**Wdired** (writable dired) — rename files by editing text:

```
C-x C-q     → enter wdired mode (filenames become editable)
;; edit filenames like normal text
C-c C-c     → apply changes
```

Bulk rename 100 files with a keyboard macro? Easy.

---

## Episode 11: "Magit — Git That Doesn't Suck"

Magit is the best Git interface on any platform. Not just Emacs. Any platform.

```elisp
(use-package magit)
;; C-x g → magit status
```

Inside magit status:

| Key | Action |
|---|---|
| `s` | Stage file/hunk |
| `u` | Unstage |
| `c c` | Commit (type message, `C-c C-c` to confirm) |
| `P p` | Push |
| `F p` | Pull |
| `b b` | Switch branch |
| `b c` | Create branch |
| `l l` | Log |
| `d d` | Diff |
| `Tab` | Expand/collapse section |
| `q` | Quit |

You can stage individual *hunks* (parts of a file), not just whole files. Press `Tab` on a file to see the diff, move to a hunk, press `s`. Surgical commits.

---

## Episode 12: "Org Mode — The Killer Feature"

Org mode is why some people use Emacs. It's notes, todos, spreadsheets, literate programming, and a publishing system in one.

```org
* My Project
** TODO Buy groceries
   DEADLINE: <2026-05-05 Mon>
** DONE Write the report
   CLOSED: [2026-05-04 Sun 14:00]
** Notes
   - Org mode is plain text
   - But it renders beautifully
   - And it exports to HTML, PDF, LaTeX

| Item   | Price | Qty | Total |
|--------+-------+-----+-------|
| Apples |  1.50 |   4 |  6.00 |
| Bread  |  3.00 |   1 |  3.00 |
|--------+-------+-----+-------|
| Total  |       |     |  9.00 |
#+TBLFM: $4=$2*$3::@4$4=vsum(@2$4..@3$4)
```

Key bindings in org:

| Key | Action |
|---|---|
| `Tab` | Fold/unfold heading |
| `M-RET` | New heading |
| `M-↑/↓` | Move heading up/down |
| `C-c C-t` | Cycle TODO state |
| `C-c C-d` | Set deadline |
| `C-c C-e` | Export (HTML, PDF, etc.) |
| `C-c \|` | Create table |
| `Tab` (in table) | Next cell + auto-align |

---

## Episode 13: "Multiple Cursors"

Edit 20 lines at once. Like Sublime Text, but in Emacs.

```elisp
(use-package multiple-cursors)
```

| Key | Action |
|---|---|
| `C-S-c C-S-c` | Edit lines (one cursor per line in region) |
| `C->` | Mark next like this |
| `C-<` | Mark previous like this |
| `C-c C-<` | Mark all like this |

```
;; Example: rename a variable in 15 places
;; 1. Select "oldName"
;; 2. C-c C-< (mark all occurrences)
;; 3. Type "newName" — all 15 change simultaneously
```

---

## Episode 14: "Completion — Company & Vertico"

Type less. Let Emacs complete.

```elisp
;; In-buffer completion (code, words)
(use-package company
  :config (global-company-mode))

;; Minibuffer completion (commands, files, buffers)
(use-package vertico
  :config (vertico-mode))

;; Rich annotations in minibuffer
(use-package marginalia
  :config (marginalia-mode))

;; Fuzzy matching
(use-package orderless
  :custom (completion-styles '(orderless basic)))
```

Now:
- Type in code → Company shows completions (Tab to accept)
- `C-x b` → Vertico shows buffers with fuzzy search
- `M-x` → type partial command name, it finds it

---

## Episode 15: "LSP — IDE Features"

Turn Emacs into a full IDE. Language Server Protocol gives you autocomplete, go-to-definition, find references, and diagnostics for any language.

```elisp
(use-package eglot)  ; built into Emacs 29+
;; M-x eglot → start LSP for current project
```

Or the heavier (more features) option:

```elisp
(use-package lsp-mode
  :hook ((python-mode . lsp)
         (js-mode . lsp)
         (rust-mode . lsp))
  :commands lsp)

(use-package lsp-ui)  ; inline diagnostics, peek
```

| Key | Action |
|---|---|
| `M-.` | Go to definition |
| `M-?` | Find references |
| `C-c C-r` | Rename symbol |
| `C-c C-d` | Show documentation |

---

## Episode 16: "Terminal Inside Emacs"

Never leave Emacs. Run your shell inside it.

```
M-x shell       → basic shell
M-x eshell      → Emacs-native shell (Elisp + bash)
M-x term        → full terminal emulator
M-x vterm       → fast terminal (needs vterm package)
```

```elisp
(use-package vterm)
;; M-x vterm → full terminal, inside Emacs
;; C-c C-t → toggle between line mode and char mode
```

Compile and run without leaving:

```
M-x compile     → run a build command
M-x recompile   → run it again (one key)
;; Errors are clickable — jump to the file and line
```

---

## Episode 17: "Keyboard Macros — Automate Anything"

Record a sequence of keystrokes. Replay it 1000 times.

```
C-x (     → start recording
;; ... do stuff ...
C-x )     → stop recording
C-x e     → replay once
C-u 100 C-x e → replay 100 times
```

**Example**: Convert a list of names to SQL inserts.

```
;; You have:
Alice
Bob
Charlie

;; You want:
INSERT INTO users (name) VALUES ('Alice');
INSERT INTO users (name) VALUES ('Bob');
INSERT INTO users (name) VALUES ('Charlie');

;; Record on the first line:
C-x (
C-a                          → go to beginning
INSERT INTO users (name) VALUES ('   → type prefix
C-e                          → go to end
');                           → type suffix
C-n                          → next line
C-x )

;; Replay on remaining lines:
C-u 2 C-x e                 → do it 2 more times
```

---

## Episode 18: "Projectile — Project Management"

Jump between files in a project without thinking about paths.

```elisp
(use-package projectile
  :config (projectile-mode +1)
  :bind-keymap ("C-c p" . projectile-command-map))
```

| Key | Action |
|---|---|
| `C-c p f` | Find file in project |
| `C-c p s g` | Grep in project |
| `C-c p b` | Switch buffer in project |
| `C-c p p` | Switch project |
| `C-c p k` | Kill all project buffers |
| `C-c p c` | Compile project |
| `C-c p t` | Run tests |

---

## Episode 19: "Snippets — Type Less, Code More"

```elisp
(use-package yasnippet
  :config (yas-global-mode 1))
(use-package yasnippet-snippets)  ; community snippets
```

Type a trigger word, press `Tab`, it expands:

```
;; In Python: type "def" + Tab →
def function_name(args):
    """docstring"""
    pass
;; Cursor lands on "function_name", Tab to jump to "args", Tab to "docstring"
```

Create your own in `~/.emacs.d/snippets/python-mode/`:

```
# -*- mode: snippet -*-
# name: for loop
# key: for
# --
for ${1:item} in ${2:iterable}:
    $0
```

---

## Episode 20: "The .emacs.d That Rocks"

The final config. Everything from episodes 01–19, in one file.

```elisp
;; ~/.emacs.d/init.el — The Complete Setup

;; ── Package Manager ─────────────────────────────
(require 'package)
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/"))
(package-initialize)
(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))
(require 'use-package)
(setq use-package-always-ensure t)

;; ── UI ──────────────────────────────────────────
(setq inhibit-startup-message t)
(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
(global-display-line-numbers-mode 1)
(column-number-mode 1)
(setq-default indent-tabs-mode nil tab-width 4)
(global-hl-line-mode 1)
(show-paren-mode 1)

;; ── Theme ───────────────────────────────────────
(use-package doom-themes :config (load-theme 'doom-one t))
(use-package doom-modeline :config (doom-modeline-mode 1))

;; ── Navigation ──────────────────────────────────
(use-package vertico :config (vertico-mode))
(use-package marginalia :config (marginalia-mode))
(use-package orderless :custom (completion-styles '(orderless basic)))
(use-package which-key :config (which-key-mode))
(use-package projectile
  :config (projectile-mode +1)
  :bind-keymap ("C-c p" . projectile-command-map))

;; ── Editing ─────────────────────────────────────
(use-package company :config (global-company-mode))
(use-package multiple-cursors
  :bind (("C->" . mc/mark-next-like-this)
         ("C-<" . mc/mark-previous-like-this)
         ("C-c C-<" . mc/mark-all-like-this)))
(use-package yasnippet :config (yas-global-mode 1))
(use-package yasnippet-snippets)
(use-package undo-tree :config (global-undo-tree-mode))

;; ── Git ─────────────────────────────────────────
(use-package magit :bind ("C-x g" . magit-status))

;; ── LSP ─────────────────────────────────────────
(use-package eglot
  :hook ((python-mode . eglot-ensure)
         (js-mode . eglot-ensure)
         (rust-mode . eglot-ensure)))

;; ── Terminal ────────────────────────────────────
(use-package vterm)

;; ── Org ─────────────────────────────────────────
(setq org-startup-indented t)
(setq org-hide-leading-stars t)
```

Copy this. Restart Emacs. Wait for packages to install. You now have a modern, fast, keyboard-driven editor that does everything an IDE does — and more.

---

## The Cheat Sheet

```
C-g             PANIC BUTTON (cancel anything)
C-x C-f         Open file
C-x C-s         Save
C-x C-c         Quit
C-x b           Switch buffer
C-x 1/2/3       Window management
C-s / C-r       Search forward / backward
M-%             Find and replace
M-x             Run any command
C-x g           Magit (git)
C-c p f         Find file in project
C-x (  ...  C-x )  C-x e    Record and replay macro
C-SPC           Start selection
C-w / M-w       Cut / Copy
C-y / M-y       Paste / Cycle paste history
C-/             Undo
```

That's it. 20 episodes. You now know more Emacs than most people who've used it for years.

---

## Tips for Daily Mastery

### The 30-Day Muscle Memory Plan

Don't try to learn everything at once. Add one new habit per week:

| Week | Focus | Daily Practice |
|---|---|---|
| 1 | Navigation | Never touch the mouse. `C-f/b/n/p` for everything. |
| 2 | Kill/Yank | Use `C-k`, `C-w`, `C-y` instead of backspace. Kill whole lines. |
| 3 | Buffers/Windows | Keep 5+ files open. Switch with `C-x b`. Split with `C-x 2/3`. |
| 4 | Search | Use `C-s` to navigate (not just to "find"). Jump to words by searching. |

After 4 weeks, your hands know the basics without thinking. Then add power tools (macros, magit, org) one at a time.

### The "No Arrow Keys" Challenge

Unbind arrow keys for a week. Force yourself to use `C-f/b/n/p`:

```elisp
;; Add to init.el (remove after the habit sticks)
(global-unset-key (kbd "<left>"))
(global-unset-key (kbd "<right>"))
(global-unset-key (kbd "<up>"))
(global-unset-key (kbd "<down>"))
```

Painful for 2 days. Natural by day 5. Faster than arrows by day 7.

### Speed Tips That Compound

| Tip | Why It Matters |
|---|---|
| `C-u 8 C-n` | Move 8 lines down. Prefix any command with `C-u N` to repeat it. |
| `M-g g 42` | Jump to line 42 instantly. |
| `C-x C-x` | Swap point and mark (jump back to where you started selecting). |
| `C-l` | Center the screen on cursor. Press again: top. Again: bottom. |
| `M-;` | Comment/uncomment region. Works in any language. |
| `C-x z` | Repeat last command. Press `z` again to keep repeating. |
| `M-q` | Reflow paragraph to fill-column width. |
| `C-x r t` | String-rectangle: insert text at the same column across multiple lines. |
| `C-x r k` | Kill rectangle (delete a column of text). |
| `M-^` | Join this line to the previous one. |

### The "Describe" Commands — Learn Emacs From Inside Emacs

| Command | What It Tells You |
|---|---|
| `C-h k` then press a key | What does this key do? |
| `C-h f` then type a function | What does this function do? |
| `C-h v` then type a variable | What's this variable's value? |
| `C-h m` | What modes are active? What keys are available? |
| `C-h b` | Show ALL keybindings for current buffer. |
| `C-h i` | Open the full Emacs manual (Info). |

**The meta-tip:** When you think "I wish Emacs could do X," type `C-h a` (apropos) and search for a keyword. It probably already can.

---

## Practical Scenarios — Become a Master

### Scenario 1: Refactor a Variable Name Across a Project

**Situation:** You need to rename `user_name` to `username` in 47 files.

```
1. C-c p s g          → projectile-grep: search "user_name" across project
2. Review matches in the *grep* buffer
3. M-x wgrep-change-to-wgrep-mode   → make grep results editable
4. C-M-% user_name RET username RET  → regex replace in the buffer
5. C-c C-c            → apply all changes to the actual files
6. C-x s !            → save all modified buffers at once
```

Or with multiple cursors:
```
1. Open a file with occurrences
2. Select "user_name"
3. C-c C-<            → mark all occurrences in this buffer
4. Type "username"    → all change simultaneously
5. Repeat per file (or use projectile-replace)
```

### Scenario 2: Convert 200 Lines of JSON to SQL Inserts

**Situation:** You have a JSON array and need SQL INSERT statements.

```json
{"name": "Alice", "email": "alice@test.com"}
{"name": "Bob", "email": "bob@test.com"}
... (200 more)
```

**Target:**
```sql
INSERT INTO users (name, email) VALUES ('Alice', 'alice@test.com');
```

**Solution — Keyboard Macro:**
```
1. Go to first line
2. C-x (                          → start recording
3. C-a                            → beginning of line
4. C-k                            → kill the whole line
5. Type: INSERT INTO users (name, email) VALUES ('
6. C-y                            → yank back the killed line
7. Now use C-s, C-w, M-% to extract name and email from the JSON
   (or use a regex replace on that line)
8. C-n                            → move to next line
9. C-x )                          → stop recording
10. C-u 199 C-x e                 → replay 199 times
```

**Alternative — regex replace on the whole buffer:**
```
C-M-%  (regex replace)
Regex: {"name": "\(.+?\)", "email": "\(.+?\)"}
Replace: INSERT INTO users (name, email) VALUES ('\1', '\2');
Press !  → replace all
```

### Scenario 3: Debug a Failing Test — Full Workflow

```
1. C-c p t            → run project tests (projectile)
2. Errors appear in *compilation* buffer
3. Click the error (or M-g n) → jump to failing file:line
4. C-x 3              → split vertically, test on left, code on right
5. Fix the code
6. M-x recompile      → re-run tests without leaving
7. Green? C-x g       → magit status
8. s                  → stage the fix
9. c c               → commit, type message, C-c C-c
10. P p              → push
```

Total time: 90 seconds. Never left Emacs.

### Scenario 4: Write Documentation with Org Mode

**Situation:** Write a technical doc with code examples, export to HTML and PDF.

```org
#+TITLE: API Documentation
#+AUTHOR: Your Name
#+OPTIONS: toc:2 num:t

* Authentication
  All requests require a Bearer token.

  #+BEGIN_SRC bash
  curl -H "Authorization: Bearer $TOKEN" https://api.example.com/users
  #+END_SRC

* Endpoints
** GET /users
   Returns a list of users.

   | Field | Type   | Description      |
   |-------+--------+------------------|
   | id    | int    | Unique ID        |
   | name  | string | Display name     |
   | email | string | Email address    |

** POST /users
   Create a new user.

   #+BEGIN_SRC json
   {
     "name": "Alice",
     "email": "alice@example.com"
   }
   #+END_SRC
```

```
C-c C-e h h    → export to HTML (opens in browser)
C-c C-e l p    → export to PDF (via LaTeX)
```

### Scenario 5: Resolve a Merge Conflict with Magit + Ediff

```
1. C-x g              → magit status (shows "unmerged" files)
2. Move to conflicted file, press e → open in ediff
3. Ediff shows 3 panels: yours | theirs | merged
4. n/p                → navigate between conflicts
5. a                  → accept version A (yours)
6. b                  → accept version B (theirs)
7. Or edit the merged buffer directly
8. q                  → quit ediff, save merged result
9. Back in magit: s   → stage the resolved file
10. c c              → commit the merge
```

### Scenario 6: Explore an Unfamiliar Codebase

```
1. C-c p f            → find any file by fuzzy name
2. M-.                → jump to definition (LSP)
3. M-?                → find all references
4. M-,                → jump back to where you were
5. C-c p s g          → grep for a string across the project
6. C-x C-b            → see all open buffers (your "breadcrumb trail")
7. C-x r m            → set a bookmark at an important location
8. C-x r b            → jump back to a bookmark
```

### Scenario 7: Batch-Edit Config Files

**Situation:** Add a new environment variable to 12 Docker Compose files.

```
1. C-c p f            → find first docker-compose.yml
2. Add the line: "  NEW_VAR: value"
3. C-x (              → start macro
4. C-x C-s            → save
5. C-x b              → switch buffer (to next compose file)
6. C-s environment    → search for the environment section
7. C-e RET            → new line after it
8. Type: "  NEW_VAR: value"
9. C-x )              → stop macro
10. Open remaining files, C-x e on each
```

Or use `dired` + `wdired` + `shell-command-on-region` for truly bulk operations.

### Scenario 8: Live-Code a Presentation

```org
;; Use org-present or org-tree-slide
(use-package org-tree-slide)

;; In an org file:
;; M-x org-tree-slide-mode
;; → Each top-level heading becomes a "slide"
;; → Right arrow: next slide
;; → Left arrow: previous slide
;; → Code blocks can be executed live with C-c C-c
```

### Scenario 9: Remote Editing via TRAMP

Edit files on a remote server as if they were local:

```
C-x C-f /ssh:user@server:/path/to/file.py RET
```

That's it. The file opens. You edit. You save (`C-x C-s`). TRAMP handles the SSH transfer transparently. Magit, LSP, compilation — all work over TRAMP.

```
;; Edit as root on local machine:
C-x C-f /sudo::/etc/nginx/nginx.conf

;; Edit on remote as root:
C-x C-f /ssh:user@server|sudo::/etc/nginx/nginx.conf
```

### Scenario 10: Build a Personal Knowledge Base (Org-Roam)

```elisp
(use-package org-roam
  :custom (org-roam-directory "~/notes")
  :config (org-roam-db-autosync-mode))
```

```
C-c n f    → find or create a note (by title)
C-c n i    → insert a link to another note
C-c n l    → toggle backlinks buffer (what links HERE?)
C-c n g    → visualize your note graph
```

Build a Zettelkasten — interconnected notes that grow into a second brain. All plain text. All searchable. All version-controlled with git.

---

## The Mastery Path

```
Week 1-2:   Survive (open, edit, save, close, don't panic)
Week 3-4:   Navigate (buffers, windows, search, movement)
Month 2:    Edit efficiently (kill/yank, macros, multiple cursors)
Month 3:    Customize (init.el, packages, theme, keybindings)
Month 4:    Integrate (magit, LSP, projectile, terminal)
Month 5:    Automate (macros, elisp functions, snippets)
Month 6+:   Transcend (org-mode, TRAMP, custom workflows)
```

The goal isn't to memorize every keybinding. It's to reach the point where Emacs disappears — where you think about your *work*, not your *editor*. The keystrokes become reflexes. The editor becomes an extension of your thought process.

That's mastery. And it starts with `C-x C-f`.
