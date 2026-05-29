# Chapter 5: Agenda — Views and Queries

[prev: Scheduling](chapter-04-scheduling.md) | [next: Capture](chapter-06-capture.md)

The agenda is Org Mode's command center — a dynamic view that pulls tasks, deadlines, and scheduled items from all your Org files into one place.

## Setup: Agenda Files

Tell Org which files to scan:

```org
#+begin_src elisp
(setq org-agenda-files '("~/org/work.org"
                         "~/org/personal.org"
                         "~/org/projects.org"))
#+end_src
```

Or add files interactively with `C-c [` (add current file) and `C-c ]` (remove).

## Opening the Agenda

| Keybinding | Action                 |
| ---------- | ---------------------- |
| `C-c a`    | Open agenda dispatcher |
| `C-c a a`  | Weekly/daily agenda    |
| `C-c a t`  | Global TODO list       |
| `C-c a m`  | Match tags/properties  |
| `C-c a s`  | Search (full text)     |

## Agenda View (Day/Week)

`C-c a a` shows scheduled items, deadlines, and timestamps for the current week.

Navigation inside the agenda:

| Key       | Action                      |
| --------- | --------------------------- |
| `f` / `b` | Forward/backward one period |
| `d`       | Day view                    |
| `w`       | Week view                   |
| `v m`     | Month view                  |
| `.`       | Go to today                 |
| `j`       | Jump to date                |
| `RET`     | Go to item in source file   |
| `TAB`     | Go to item in other window  |

## TODO List

`C-c a t` shows all TODO items across agenda files.

| Key | Action                     |
| --- | -------------------------- |
| `t` | Cycle TODO state           |
| `T` | Show specific TODO keyword |
| `r` | Refresh                    |

## Tag/Property Matching

`C-c a m` prompts for a match expression:

```
work+urgent        — items tagged both :work: and :urgent:
work|personal      — items tagged :work: or :personal:
work-urgent        — items tagged :work: but not :urgent:
Effort<"1:00"      — items with effort less than 1 hour
PRIORITY="A"       — only priority A items
```

## Filtering in Agenda

| Key | Action             |
| --- | ------------------ | ------------------ |
| `/` | Filter by tag      |
| `<` | Filter by category |
| `=` | Filter by regex    |
| `   | `                  | Remove all filters |

## Bulk Actions

Mark multiple items and act on them:

| Key | Action                    |
| --- | ------------------------- |
| `m` | Mark item for bulk action |
| `u` | Unmark item               |
| `U` | Unmark all                |
| `B` | Execute bulk action       |

Bulk actions: reschedule (`B s`), set deadline (`B d`), change state (`B t`), archive (`B a`).

## Custom Agenda Commands

```org
#+begin_src elisp
(setq org-agenda-custom-commands
      '(("w" "Work tasks" tags-todo "+work")
        ("h" "Home tasks" tags-todo "+home")
        ("n" "Next actions" todo "NEXT")
        ("W" "Weekly review"
         ((agenda "" ((org-agenda-span 7)))
          (todo "WAITING")
          (todo "NEXT")
          (stuck "")))))
#+end_src
```

Access with `C-c a w`, `C-c a h`, etc.

## Stuck Projects

A "stuck" project is a heading with subtasks but no NEXT action:

```org
#+begin_src elisp
(setq org-stuck-projects
      '("+LEVEL=2/-DONE" ("NEXT" "WAITING") nil ""))
#+end_src
```

View with `C-c a #`.

## Column View

See properties in a table-like format:

```org
#+COLUMNS: %40ITEM %TODO %3PRIORITY %Effort{:} %TAGS
```

| Keybinding    | Action            |
| ------------- | ----------------- |
| `C-c C-x C-c` | Enter column view |
| `q`           | Exit column view  |
| `e`           | Edit value        |

## Category

Set category for agenda display:

```org
#+CATEGORY: Work

* TODO Fix bug
  ;; Shows as "Work" in agenda
```

Or per-heading:

```org
* Projects
  :PROPERTIES:
  :CATEGORY: Projects
  :END:
```

## Exercises

1. Set up `org-agenda-files` with at least 2 files
2. Open weekly agenda with `C-c a a`, navigate with `f`, `b`, `d`, `w`
3. View all TODOs with `C-c a t`
4. Filter by tag with `C-c a m` using `work+urgent`
5. Create a custom agenda command and access it
