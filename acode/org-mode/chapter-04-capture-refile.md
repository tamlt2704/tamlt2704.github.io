# Chapter 4: Capture Thoughts Instantly — The Inbox Workflow

[← Ch 3](chapter-03-scheduling.md) | [Ch 5 →](chapter-05-tables.md)

---

## The Problem

You're deep in code. Flow state. Then a thought hits: "Oh, I need to email Sarah about the API change." If you switch to your task manager, you lose flow. If you don't write it down, you'll forget by lunch.

So you do what everyone does — open a new browser tab, type half a note, get distracted, and 20 minutes later you're reading Hacker News. The thought is gone. The flow is gone.

---

## The Naive Attempt

You keep a scratch buffer open. Or a sticky note. Or you text yourself. These "work" but:
- The note has no context (what project? what priority?)
- It never gets processed (the sticky note pile grows)
- It's not in your system (the agenda doesn't know about it)

---

## Nadia's Way: Capture Without Context Switching

> "Org capture is a 2-second interruption. You press `C-c c`, type your thought, press `C-c C-c`, and you're back exactly where you were. The thought goes to your inbox. You process it later. Zero flow disruption."

---

## Setting Up Capture

Add to your Emacs config:

```elisp
;; Global keybinding for capture
(global-set-key (kbd "C-c c") #'org-capture)

;; Capture templates
(setq org-capture-templates
      '(("t" "Todo" entry (file+headline "~/org/inbox.org" "Tasks")
         "* TODO %?\n  %U\n  %a" :empty-lines 1)

        ("n" "Note" entry (file+headline "~/org/inbox.org" "Notes")
         "* %?\n  %U\n  %a" :empty-lines 1)

        ("j" "Journal" entry (file+datetree "~/org/journal.org")
         "* %U %?\n  %i" :empty-lines 1)

        ("m" "Meeting" entry (file+headline "~/org/inbox.org" "Meetings")
         "* %? :meeting:\n  %U\n  Attendees:\n  Notes:\n  Action items:\n" :empty-lines 1)))
```

---

## Using Capture

Press `C-c c` from anywhere in Emacs. A menu appears:

```
Select a capture template:
[t] Todo
[n] Note
[j] Journal
[m] Meeting
```

Press `t`. A capture buffer opens:

```org
* TODO |
  [2026-01-15 Wed 14:32]
  [[file:~/code/project/src/auth.py::42][auth.py:42]]
```

The `|` is your cursor. The timestamp is automatic. The link points back to where you *were* when you captured — so you can find context later.

Type your thought: "Email Sarah about API breaking change"

Press `C-c C-c` to finalize. The entry goes to `~/org/inbox.org` under `* Tasks`. You're back in `auth.py` exactly where you left off.

Press `C-c C-k` to abort (discard the capture).

---

## Template Syntax

The template string uses special `%` escapes:

| Escape | Expands To |
|---|---|
| `%?` | Cursor position after template expands |
| `%U` | Inactive timestamp (now) |
| `%T` | Active timestamp (now) |
| `%a` | Link to where you were when you captured |
| `%i` | Selected text (if any was highlighted) |
| `%^{Prompt}` | Ask for input with "Prompt" |
| `%^g` | Prompt for tags |
| `%^t` | Prompt for a date |

Example — a template that asks for a deadline:

```elisp
("d" "Todo with deadline" entry (file+headline "~/org/inbox.org" "Tasks")
 "* TODO %?\n  DEADLINE: %^t\n  %U\n  %a" :empty-lines 1)
```

---

## Refile: Move Things to the Right Place

Your inbox fills up. That's fine — it's supposed to. The second half of the workflow is *refile*: moving entries from the inbox to their proper home.

Set up refile targets:

```elisp
;; Allow refiling to any heading in these files, up to 3 levels deep
(setq org-refile-targets
      '(("~/org/projects.org" :maxlevel . 3)
        ("~/org/tasks.org" :maxlevel . 2)
        ("~/org/notes.org" :maxlevel . 2)
        ("~/org/someday.org" :maxlevel . 1)))

;; Show full path for refiling
(setq org-refile-use-outline-path t)
(setq org-outline-path-complete-in-steps nil)  ;; show full paths in completion
```

Now put your cursor on any heading and press `C-c C-w`. A completion prompt appears:

```
Refile to: projects.org/Dashboard MVP/Frontend components
```

You can type to fuzzy-match: `dash front` → finds "projects.org/Dashboard MVP/Frontend components". Press `RET` and the heading moves there.

---

## The Inbox Workflow

This is the GTD (Getting Things Done) capture-process-refile loop:

```
  Throughout the day:
  ┌─────────────────────────────────────┐
  │  Thought → C-c c → inbox.org        │  (2 seconds, no context switch)
  └─────────────────────────────────────┘

  Once or twice a day (processing time):
  ┌─────────────────────────────────────┐
  │  Open inbox.org                      │
  │  For each item:                      │
  │    - Add context (priority, tags)    │
  │    - Refile to proper location       │
  │    - Or do it now if < 2 minutes     │
  │    - Or delete if not actionable     │
  └─────────────────────────────────────┘
```

Your inbox should be EMPTY after processing. It's a temporary holding area, not a permanent list.

---

## Practical: Developer Capture Templates

Here's a real-world set of templates for developers:

```elisp
(setq org-capture-templates
      '(("t" "Task" entry (file+headline "~/org/inbox.org" "Tasks")
         "* TODO [#B] %?\n  %U\n  %a" :empty-lines 1)

        ("b" "Bug" entry (file+headline "~/org/inbox.org" "Bugs")
         "* TODO [#A] BUG: %?\n  %U\n  %a\n  Steps to reproduce:\n  Expected:\n  Actual:" :empty-lines 1)

        ("n" "Note" entry (file+headline "~/org/notes.org" "Inbox")
         "* %?\n  %U\n  %a" :empty-lines 1)

        ("j" "Journal" entry (file+datetree "~/org/journal.org")
         "* %U %?\n  %i" :empty-lines 1)

        ("m" "Meeting notes" entry (file+headline "~/org/inbox.org" "Meetings")
         "* %^{Meeting title} :meeting:\n  %U\n  Attendees: %^{Attendees}\n  \n** Notes\n   %?\n\n** Action Items\n" :empty-lines 1)

        ("s" "Code snippet" entry (file+headline "~/org/notes.org" "Snippets")
         "* %^{Description}\n  %U\n  #+BEGIN_SRC %^{Language}\n  %i%?\n  #+END_SRC" :empty-lines 1)

        ("l" "Link/Article" entry (file+headline "~/org/reading.org" "To Read")
         "* TODO %^{Title}\n  %U\n  %^{URL}\n  %?" :empty-lines 1)))
```

---

## Capture from Anywhere (OS-level)

Want to capture without even having Emacs focused? Use `emacsclient`:

```bash
# In your shell config (.bashrc, .zshrc)
alias capture="emacsclient -e '(org-capture)'"
```

Or bind it to a global hotkey in your OS. Nadia uses `Super+c` (Windows key + c) to pop up a capture frame from anywhere.

```elisp
;; For emacsclient capture frame
(defun my/org-capture-frame ()
  "Create a new frame for org-capture."
  (interactive)
  (make-frame '((name . "capture")
                (width . 80)
                (height . 20)))
  (select-frame-by-name "capture")
  (org-capture))
```

---

## Refile Tips

| Binding | Action |
|---|---|
| `C-c C-w` | Refile heading to another location |
| `C-u C-c C-w` | Jump to last refile location |
| `C-u C-u C-c C-w` | Refile as a copy (original stays) |

Pro moves:
- Refile from the agenda view: cursor on item, press `r`
- Bulk refile: mark multiple items in agenda with `m`, then `B r`

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c c` | Start capture (global, after setup) |
| `C-c C-c` | Finalize capture |
| `C-c C-k` | Abort capture |
| `C-c C-w` | Refile heading |
| `C-u C-c C-w` | Go to last refile target |

---

## Exercise: Build Your Capture Workflow

1. Add the capture templates from this chapter to your Emacs config.
2. Create `~/org/inbox.org`:

```org
#+TITLE: Inbox

* Tasks

* Notes

* Meetings
```

3. Practice capturing from different contexts:
   - Open a source file, capture a TODO related to it
   - Capture a meeting note
   - Capture a journal entry
4. Process your inbox: add priorities, tags, then refile each item to its proper home.
5. Verify your inbox is empty after processing.

> **Nadia's tip:** "The capture habit changes everything. Before org-mode, I'd think 'I should remember to...' and then forget. Now it's muscle memory: thought → C-c c t → type → C-c C-c → back to work. My inbox catches everything. I process it twice a day — morning and end of day. Nothing falls through the cracks."

---

[← Ch 3](chapter-03-scheduling.md) | [Ch 5: Spreadsheets in Plain Text →](chapter-05-tables.md)
