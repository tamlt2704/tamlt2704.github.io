# Emacs 101 — Practical Tasks (Chapter by Chapter)

Work through these tasks after each episode. Each task is a real scenario you'd encounter as a developer. Don't skip ahead — the skills compound.

---

## Episode 01–02: Survival

### Task 1: Create a project from scratch

Without using a file manager or terminal outside Emacs:

1. Open Emacs
2. `C-x C-f ~/projects/practice/hello.py RET` (Emacs creates the directory)
3. Type this program:
   ```python
   def greet(name):
       return f"Hello, {name}!"

   names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
   for name in names:
       print(greet(name))
   ```
4. Save with `C-x C-s`
5. Open a second file: `C-x C-f ~/projects/practice/notes.txt RET`
6. Type: "This is my Emacs practice project"
7. Save
8. Switch back to hello.py: `C-x b hel TAB RET`
9. Switch back to notes.txt: `C-x b not TAB RET`
10. Close Emacs: `C-x C-c`

**Success criteria:** You never touched the mouse. You never left Emacs. You created two files in a new directory.

### Task 2: The "I'm stuck" drill

Practice escaping from bad situations:

1. Press `C-x C-f` then realize you don't want to open a file → `C-g` (cancel)
2. Press `M-x` and type gibberish → `C-g` (cancel)
3. Press `C-x` and then forget what comes next → `C-g` (cancel)
4. Accidentally start a search with `C-s` → `C-g` (cancel and return)
5. Open the help with `C-h` accidentally → `q` or `C-g` to close

**Rule:** Whenever you're confused, `C-g` is the answer. Repeat until it's reflex.

---

## Episode 03: Movement

### Task 3: Navigate a long file without arrow keys or mouse

1. Open a file with 100+ lines (download any source file, or use `M-x find-file /etc/hosts`)
2. Go to the very end: `M->`
3. Go to the very beginning: `M-<`
4. Go to line 50: `M-g g 50 RET`
5. Move forward 10 words: `M-f` × 10 (or `C-u 10 M-f`)
6. Move to the beginning of the current line: `C-a`
7. Move to the end of the current line: `C-e`
8. Move down 20 lines: `C-u 20 C-n`
9. Page down: `C-v`. Page up: `M-v`
10. Center the screen on your cursor: `C-l`

**Challenge:** Time yourself. Open a file, navigate to line 73, go to the end of that line, then jump to line 12, beginning of line. Under 5 seconds = mastery.

### Task 4: The word-hop challenge

Open `hello.py` from Task 1. Starting at the top:

1. Jump word-by-word to the word "Charlie" using only `M-f` (forward word)
2. Jump back to "def" using only `M-b` (backward word)
3. Jump to the end of the `greet` function using `C-n` and `C-e`
4. Jump to the opening parenthesis using `C-b` repeatedly (or `C-s (`)

---

## Episode 04: Kill and Yank

### Task 5: Rearrange a list

You have this in a buffer:

```
5. Deploy to production
3. Write tests
1. Design the API
4. Code review
2. Implement the feature
```

Rearrange it into correct order (1-5) using ONLY kill and yank:

1. `C-a` to go to beginning of "1. Design the API"
2. `C-k` to kill the line (or `C-S-k` for whole line including newline)
3. Move to the top
4. `C-y` to yank it
5. Repeat for each line

**No copy-paste from outside. No mouse. Only `C-k`, `C-y`, `M-y`, and movement.**

### Task 6: The kill ring workout

1. Open a new buffer: `C-x b scratch RET`
2. Type five separate lines:
   ```
   First line
   Second line
   Third line
   Fourth line
   Fifth line
   ```
3. Kill each line with `C-k` (5 kills)
4. Now yank back the THIRD line: `C-y` (pastes fifth), `M-y` (fourth), `M-y` (third) — stop
5. Go to a new line, yank the FIRST line: `C-y M-y M-y M-y M-y`

**Goal:** Understand that the kill ring is a stack you can cycle through.

### Task 7: Extract a function

You have:

```python
def process_data(items):
    results = []
    for item in items:
        cleaned = item.strip().lower()
        if cleaned and len(cleaned) > 3:
            results.append(cleaned)
    return results
```

Using kill/yank, extract the inner logic into a new function:

1. Select the 3 inner lines (from `cleaned = ...` to `results.append(...)`) with `C-SPC` then move
2. `C-w` to kill the region
3. Move above the function
4. Type the new function signature: `def clean_item(item):`
5. `C-y` to yank the killed lines inside it
6. Fix indentation and add a return statement
7. Replace the original lines with a call to `clean_item(item)`

---

## Episode 05: Undo

### Task 8: The undo confidence drill

1. Open a new file
2. Type "AAA" → undo (`C-/`) → it's gone
3. Type "BBB" → type "CCC" → undo once → "CCC" gone, "BBB" remains
4. Undo again → "BBB" gone
5. Now type "DDD" → the undo history now includes the undos themselves
6. Undo → "DDD" gone
7. Undo → "BBB" reappears (undoing the undo!)
8. Undo → "CCC" reappears

**Goal:** Trust that Emacs never loses anything. Every state is reachable through undo.

---

## Episode 06: Buffers and Windows

### Task 9: The multi-file workflow

Simulate a real coding session:

1. Open 4 files (create them if needed):
   - `C-x C-f ~/projects/practice/app.py`
   - `C-x C-f ~/projects/practice/test_app.py`
   - `C-x C-f ~/projects/practice/config.py`
   - `C-x C-f ~/projects/practice/README.md`
2. Split into 2 windows: `C-x 3` (vertical split)
3. Left window: `app.py`. Right window: `test_app.py`
4. Switch to right window: `C-x o`
5. Change right window to `config.py`: `C-x b config RET`
6. Go back to one window: `C-x 1`
7. List all buffers: `C-x C-b`
8. Kill the README buffer: `C-x b README RET` then `C-x k RET`
9. Verify it's gone: `C-x C-b`

### Task 10: The "compare two files" drill

1. Open `app.py` in one window
2. `C-x 3` to split vertically
3. `C-x o` to switch to the right window
4. Open `test_app.py` there
5. Write a function in `app.py` (left window)
6. `C-x o` to switch right
7. Write a test for it in `test_app.py`
8. Keep switching with `C-x o` as you develop both files together

---

## Episode 07: M-x

### Task 11: Discover commands

Without looking anything up, use `M-x` to:

1. Count the words in the current buffer: `M-x count-words`
2. Sort lines alphabetically: select a region, `M-x sort-lines`
3. Remove duplicate lines: select a region, `M-x delete-duplicate-lines`
4. Insert today's date: `M-x org-time-stamp` or write a quick function
5. Toggle line wrapping: `M-x visual-line-mode`
6. Check what face/font is at cursor: `M-x describe-char`
7. Open a calculator: `M-x calc`

**Goal:** Build the habit of "I wonder if Emacs can..." → `M-x` → type a guess → Tab complete.

---

## Episode 08: init.el

### Task 12: Build your config from scratch

1. Back up any existing config: `mv ~/.emacs.d ~/.emacs.d.bak`
2. Create `~/.emacs.d/init.el`
3. Add these one at a time, restarting Emacs after each to verify:
   - Disable the toolbar: `(tool-bar-mode -1)`
   - Disable the startup screen: `(setq inhibit-startup-message t)`
   - Show line numbers: `(global-display-line-numbers-mode 1)`
   - Set up MELPA package archive
   - Install `use-package`
   - Install and load a theme (`doom-one` or `modus-vivendi`)
   - Install `which-key`
4. After each addition, verify it works before adding the next

**Goal:** Understand that your config is a living document. You add to it over months, not all at once.

### Task 13: Write your first Elisp function

Add to your `init.el`:

```elisp
(defun my/insert-date ()
  "Insert the current date at point."
  (interactive)
  (insert (format-time-string "%Y-%m-%d")))

(global-set-key (kbd "C-c d") 'my/insert-date)
```

Test it: press `C-c d` in any buffer. Today's date appears.

Now write another one:

```elisp
(defun my/open-init ()
  "Open my init.el file."
  (interactive)
  (find-file "~/.emacs.d/init.el"))

(global-set-key (kbd "C-c i") 'my/open-init)
```

---

## Episode 09: Search and Replace

### Task 14: The search-as-navigation drill

Open any source file with 200+ lines. Use ONLY `C-s` (incremental search) to navigate:

1. Jump to the word "function" (or "def" in Python): `C-s function`
2. Jump to the next occurrence: `C-s` again
3. Jump to a specific variable name: `C-s myVariable`
4. Go back to where you started: `C-g` (cancels search and returns to origin)
5. Search backward for "import": `C-r import`

**Key insight:** `C-s` isn't just for "finding" — it's the fastest way to move to any known text.

### Task 15: Bulk rename with query-replace

Create a file with this content:

```javascript
function getUserName(userId) {
  const userName = fetchUser(userId).name;
  console.log("userName:", userName);
  return userName;
}

function setUserName(userId, userName) {
  updateUser(userId, { name: userName });
  console.log("Updated userName for", userId);
}
```

Rename `userName` to `displayName` using query-replace:

1. `M-<` to go to the top
2. `M-%` → type `userName` → RET → type `displayName` → RET
3. For each match: `y` (replace), `n` (skip), `!` (replace all remaining)
4. Skip the ones inside `getUserName` and `setUserName` (function names) — press `n`
5. Replace the variable usages — press `y`

### Task 16: Regex replace

You have a CSV-like list:

```
Alice, 25, Engineer
Bob, 30, Designer
Charlie, 28, Manager
```

Convert to JSON objects using regex replace:

1. `C-M-%` (query-replace-regexp)
2. Regex: `\(.+\), \([0-9]+\), \(.+\)`
3. Replace: `{"name": "\1", "age": \2, "role": "\3"}`
4. Press `!` to replace all

---

## Episode 10: Dired

### Task 17: Organize a messy downloads folder

1. `C-x d ~/Downloads RET` (or any messy directory)
2. Sort by date: `s` (toggle sort)
3. Mark old files for deletion: move to each, press `d`
4. Create a new subdirectory: `+` → type "archive"
5. Mark files to move: `m` on each file
6. Move them: `R` → type the destination path
7. Execute deletions: `x`
8. Refresh: `g`

### Task 18: Bulk rename with wdired

Create 5 files named `photo_001.jpg` through `photo_005.jpg` (use `touch` in shell or create them in dired with `!`).

1. Open the directory in dired: `C-x d`
2. Enter wdired mode: `C-x C-q`
3. Use `M-%` (query-replace) to change `photo_` to `vacation_` in all filenames
4. Apply: `C-c C-c`
5. Verify: all files are now `vacation_001.jpg` through `vacation_005.jpg`

---

## Episode 11: Magit

### Task 19: The full git workflow

1. Create a new project:
   ```
   M-x shell RET
   mkdir ~/projects/emacs-practice && cd ~/projects/emacs-practice && git init
   ```
2. Create a file: `C-x C-f ~/projects/emacs-practice/main.py`
3. Write some code, save
4. `C-x g` → magit status
5. Stage the file: move to it, press `s`
6. Commit: `c c` → type "Initial commit" → `C-c C-c`
7. Make a change to main.py
8. `C-x g` → see the diff (press `Tab` on the file)
9. Stage only ONE hunk (not the whole file): expand the diff, move to a hunk, press `s`
10. Commit just that hunk: `c c` → message → `C-c C-c`

### Task 20: Branch and merge

1. Create a branch: `b c` → type "feature/add-tests" → RET
2. Create `test_main.py`, write a test, save
3. Stage and commit
4. Switch back to main: `b b` → select "main"
5. Merge: `m m` → select "feature/add-tests"
6. Check the log: `l l` — see both commits

---

## Episode 12: Org Mode

### Task 21: Plan a project

Create `~/org/project.org`:

```org
#+TITLE: My Side Project

* TODO Design the database schema
  DEADLINE: <2026-05-10 Sun>
* TODO Set up the API
  - [ ] Install dependencies
  - [ ] Create routes
  - [ ] Add authentication
* TODO Build the frontend
* TODO Write documentation
* TODO Deploy
```

Practice:
1. Fold/unfold headings: `Tab`
2. Move a heading up: `M-↑`
3. Mark "Design the database schema" as DONE: `C-c C-t`
4. Add a deadline to "Set up the API": `C-c C-d`
5. Toggle checkboxes: move to `[ ]`, press `C-c C-c`
6. Add a new heading: `M-RET`
7. Export to HTML: `C-c C-e h h`

### Task 22: Time tracking with org

Add to your project.org:

```org
* TODO Write the API
  :LOGBOOK:
  :END:
```

1. Start the clock: `C-c C-x C-i` (clock in)
2. Work on the task for a few minutes
3. Stop the clock: `C-c C-x C-o` (clock out)
4. View the time report: `C-c C-x C-r` (clock report)

---

## Episode 13: Multiple Cursors

### Task 23: Add console.log to every function

You have:

```javascript
function handleClick() {
  // ...
}

function handleSubmit() {
  // ...
}

function handleChange() {
  // ...
}

function handleBlur() {
  // ...
}
```

Add `console.log("entering <name>")` to each function:

1. Select "function" on the first line
2. `C-c C-<` → mark all occurrences of "function"
3. `C-e` → all cursors go to end of their lines
4. `RET` → new line on each
5. Type: `  console.log("entering");`
6. Now go back and fill in the names (or use a macro)

### Task 24: Convert object keys

You have:

```javascript
const config = {
  user_name: "alice",
  first_name: "Alice",
  last_name: "Smith",
  email_address: "alice@example.com",
  phone_number: "555-1234",
};
```

Convert all snake_case keys to camelCase:

1. Select the first `_` followed by a letter
2. Use `C->` to mark each similar pattern
3. Delete the underscore, capitalize the next letter

(This is tricky — macros might be easier here. Try both approaches!)

---

## Episode 14: Completion

### Task 25: Speed-coding with company-mode

1. Open a Python file
2. Type `imp` → company should suggest `import`
3. Type `def` → Tab → snippet expands (if yasnippet is installed)
4. Inside a function, type `self.` → see attribute completions (if LSP is running)
5. Type a long variable name once, then later type the first 3 letters → company completes it

**Goal:** Never type a full word twice. Let completion do the work.

---

## Episode 15: LSP

### Task 26: Navigate a codebase with LSP

1. Open a project with LSP configured (Python, JS, Rust, etc.)
2. `M-x eglot` (or it auto-starts)
3. Place cursor on a function call → `M-.` (go to definition)
4. `M-,` to jump back
5. Place cursor on a function definition → `M-?` (find all references)
6. Rename a symbol: `C-c C-r` → type new name → all references update
7. Hover on a function → see documentation (if `lsp-ui` is installed)
8. See diagnostics (errors/warnings) in the buffer

### Task 27: Fix all lint errors

1. Open a file with intentional errors (unused imports, wrong types)
2. `M-x flymake-show-diagnostics-buffer` (or `lsp-ui` inline errors)
3. Jump to next error: `M-g n` (next-error)
4. Fix it
5. Jump to next: `M-g n`
6. Repeat until clean

---

## Episode 16: Terminal

### Task 28: The "never leave Emacs" challenge

Do an entire development cycle without leaving Emacs:

1. `M-x vterm` → open terminal
2. `cd` to your project
3. Run tests: `python -m pytest` (or equivalent)
4. See a failure → `C-x o` to switch to code window
5. Fix the code
6. `C-x o` back to terminal
7. Up arrow → re-run tests
8. All green → `C-x g` → stage → commit → push

Alternative with `compile`:
1. `M-x compile` → type `python -m pytest`
2. Errors are clickable → click to jump to file:line
3. Fix → `M-x recompile` (or `g` in the compilation buffer)

---

## Episode 17: Macros

### Task 29: Generate test data

You have a list of names:

```
Alice Johnson
Bob Smith
Charlie Brown
Diana Prince
Eve Wilson
Frank Castle
Grace Hopper
Henry Ford
Iris West
Jack Ryan
```

Convert each to a Python dictionary using a macro:

**Target:**
```python
{"first": "Alice", "last": "Johnson"},
```

1. Go to first line
2. `C-x (` — start recording
3. `C-a` — beginning of line
4. Type `{"first": "`
5. `M-f` — forward one word (past "Alice")
6. Type `", "last": "`
7. `C-e` — end of line
8. Type `"},`
9. `C-n C-a` — next line, beginning
10. `C-x )` — stop recording
11. `C-u 9 C-x e` — replay 9 times

### Task 30: Add error handling to multiple functions

You have:

```python
def fetch_user(id):
    return db.query(f"SELECT * FROM users WHERE id = {id}")

def fetch_order(id):
    return db.query(f"SELECT * FROM orders WHERE id = {id}")

def fetch_product(id):
    return db.query(f"SELECT * FROM products WHERE id = {id}")
```

Wrap each in try/except using a macro:

1. Go to first `def` line
2. `C-x (` — start recording
3. `C-e RET` — end of line, new line
4. Type `    try:`
5. `C-n` — next line (the return statement)
6. `C-a` — beginning
7. Type `    ` (4 extra spaces to indent inside try)
8. `C-n RET` — after the return, new line
9. Type `    except Exception as e:`
10. `RET` — new line
11. Type `        raise DatabaseError(f"Query failed: {e}")`
12. Move to the next `def` line
13. `C-x )` — stop recording
14. `C-x e` — replay for remaining functions

---

## Episode 18: Projectile

### Task 31: The "new project" speed run

Time yourself:

1. `C-c p p` → switch to a project (or create one)
2. `C-c p f` → find `app.py` (type partial name, fuzzy match)
3. `C-c p s g` → grep for "TODO" across the project
4. `C-c p b` → switch between project buffers
5. `C-c p k` → kill all project buffers (clean slate)
6. `C-c p c` → compile the project

**Target:** Under 30 seconds for the full sequence.

---

## Episode 19: Snippets

### Task 32: Create 5 custom snippets

Create snippets for patterns you type daily. Examples for Python:

1. `main` → expands to `if __name__ == "__main__":\n    `
2. `pdb` → expands to `import pdb; pdb.set_trace()`
3. `log` → expands to `logger.info(f"$1: {$2}")`
4. `test` → expands to full test function template
5. `cls` → expands to class with `__init__`

Create each in `~/.emacs.d/snippets/python-mode/`:

```
# -*- mode: snippet -*-
# name: main block
# key: main
# --
if __name__ == "__main__":
    $0
```

Test each one: type the trigger, press `Tab`, verify expansion.

---

## Episode 20: The Full Workflow

### Task 33: The 10-minute challenge

Set a timer for 10 minutes. Complete this entire workflow:

1. Create a new Python project with 3 files (app, test, config)
2. Write a function in app.py
3. Write a test in test_app.py
4. Run the test (compile or terminal)
5. Fix any failure
6. Git init, stage, commit with a good message
7. Create a branch, make a change, commit, merge back to main
8. Export a summary as an org file with today's date

**Scoring:**
- Finished in 10 min without mouse: Master
- Finished in 10 min with occasional mouse: Advanced
- Finished in 15 min: Intermediate
- Didn't finish: Keep practicing — you'll get there

### Task 34: Teach someone else

The ultimate test of mastery: open Emacs on a friend's computer and show them:

1. How to open and save a file
2. How to search
3. How to split windows
4. How to undo
5. The `C-g` panic button

If you can explain it clearly and demonstrate it smoothly, you've internalized it.

---

## Progress Tracker

| Episode | Task(s) | Completed | Date |
|---|---|---|---|
| 01–02 | Tasks 1–2 | ☐ | |
| 03 | Tasks 3–4 | ☐ | |
| 04 | Tasks 5–7 | ☐ | |
| 05 | Task 8 | ☐ | |
| 06 | Tasks 9–10 | ☐ | |
| 07 | Task 11 | ☐ | |
| 08 | Tasks 12–13 | ☐ | |
| 09 | Tasks 14–16 | ☐ | |
| 10 | Tasks 17–18 | ☐ | |
| 11 | Tasks 19–20 | ☐ | |
| 12 | Tasks 21–22 | ☐ | |
| 13 | Tasks 23–24 | ☐ | |
| 14 | Task 25 | ☐ | |
| 15 | Tasks 26–27 | ☐ | |
| 16 | Task 28 | ☐ | |
| 17 | Tasks 29–30 | ☐ | |
| 18 | Task 31 | ☐ | |
| 19 | Task 32 | ☐ | |
| 20 | Tasks 33–34 | ☐ | |

**Rule:** Don't move to the next episode until you can complete the current tasks without looking at the cheat sheet.
