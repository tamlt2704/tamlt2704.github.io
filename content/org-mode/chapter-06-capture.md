# Chapter 6: Capture and Refile — Collecting Information

[prev: Agenda](chapter-05-agenda.md) | [next: Tables](chapter-07-tables.md)

Capture lets you quickly jot down tasks and notes without leaving your current work. Refile moves them to the right place later.

## Capture Setup

```org
#+begin_src elisp
(global-set-key (kbd "C-c c") #'org-capture)

(setq org-capture-templates
      '(("t" "Todo" entry (file+headline "~/org/inbox.org" "Tasks")
         "* TODO %?\n  %U\n  %a")
        ("n" "Note" entry (file+headline "~/org/inbox.org" "Notes")
         "* %? :note:\n  %U")
        ("j" "Journal" entry (file+datetree "~/org/journal.org")
         "* %U %?\n  %i")
        ("m" "Meeting" entry (file+headline "~/org/inbox.org" "Meetings")
         "* MEETING %? :meeting:\n  %U\n  %a")))
#+end_src
```

## Using Capture

| Keybinding | Action                               |
| ---------- | ------------------------------------ |
| `C-c c`    | Start capture (shows template menu)  |
| `C-c C-c`  | Finalize capture (save and close)    |
| `C-c C-w`  | Refile capture to different location |
| `C-c C-k`  | Abort capture                        |

Workflow: press `C-c c`, pick template, type content, `C-c C-c`. Done.

## Template Syntax

Key elements in templates:

| Symbol       | Expands to                            |
| ------------ | ------------------------------------- |
| `%?`         | Cursor position after expansion       |
| `%U`         | Inactive timestamp                    |
| `%T`         | Active timestamp                      |
| `%a`         | Link to where you were when capturing |
| `%i`         | Active region (selected text)         |
| `%^{Prompt}` | Prompt user for input                 |
| `%^g`        | Prompt for tags                       |
| `%^t`        | Prompt for date                       |

### Example Templates

```org
#+begin_src elisp
;; Bug report with prompts
("b" "Bug" entry (file "~/org/bugs.org")
 "* BUG %^{Title}\n  :PROPERTIES:\n  :Severity: %^{Severity|Low|Medium|High|Critical}\n  :END:\n  %U\n  %?")

;; Quick TODO with deadline prompt
("d" "Deadline task" entry (file+headline "~/org/inbox.org" "Tasks")
 "* TODO %?\n  DEADLINE: %^t")

;; Bookmark
("B" "Bookmark" entry (file+headline "~/org/bookmarks.org" "New")
 "* [[%^{URL}][%^{Title}]] :bookmark:\n  %U\n  %?")
#+end_src
```

## Refile

Move headings to the correct location after capture:

| Keybinding        | Action                     |
| ----------------- | -------------------------- |
| `C-c C-w`         | Refile current heading     |
| `C-u C-c C-w`     | Jump to refile target      |
| `C-u C-u C-c C-w` | Refile to last used target |

### Refile Targets

```org
#+begin_src elisp
(setq org-refile-targets '((org-agenda-files :maxlevel . 3)))
(setq org-refile-use-outline-path 'file)
(setq org-outline-path-complete-in-steps nil)  ; show full path in completion
(setq org-refile-allow-creating-parent-nodes 'confirm)
#+end_src
```

## Archive

Move completed tasks out of active files:

| Keybinding    | Action                            |
| ------------- | --------------------------------- |
| `C-c C-x C-a` | Archive subtree (to archive file) |
| `C-c C-x a`   | Toggle ARCHIVE tag                |

Default archive location: `filename.org_archive`. Customize:

```org
#+ARCHIVE: ~/org/archive.org::* From %s
```

## GTD Inbox Workflow

1. **Capture** everything into inbox (`C-c c t`)
2. **Process** inbox regularly — for each item decide:
   - Do it now (under 2 minutes)
   - Refile to a project (`C-c C-w`)
   - Schedule/deadline it
   - Someday/maybe
   - Delete it
3. **Review** weekly

```org
;; Inbox file structure
* Tasks
* Notes
* Meetings

;; Refile targets
~/org/work.org       - Work projects
~/org/personal.org   - Personal projects
~/org/someday.org    - Someday/maybe
~/org/reference.org  - Reference material
```

## Exercises

1. Set up capture templates for TODO, note, and journal
2. Capture 5 items with `C-c c`
3. Refile them to appropriate locations with `C-c C-w`
4. Archive a completed task with `C-c C-x C-a`
5. Build a daily habit: capture immediately, refile during review
