# Chapter 2: Track What Needs Doing — TODO States and Priorities

[← Ch 1](chapter-01-outlines.md) | [Ch 3 →](chapter-03-scheduling.md)

---

## The Problem

You have a project plan from Chapter 1. Beautiful outline. But which items are *done*? Which are *in progress*? Which are blocked? You're back to grepping for `- [ ]` or maintaining a separate task tracker.

Your Todoist has 147 items. Your Jira board has 53 tickets. Your sticky notes have... you can't read your own handwriting. Nothing is in one place.

---

## The Naive Attempt

You try prefixing headings manually:

```markdown
## [DONE] Set up database
## [IN PROGRESS] Build API endpoints
## [BLOCKED] Deploy to staging (waiting on DevOps)
## [TODO] Write tests
```

This "works" but:
- No keyboard shortcut to cycle states
- No way to query "show me all in-progress items"
- No progress tracking
- No priority system
- You forget to update them

---

## Nadia's Way: TODO as a First-Class Concept

> "In org-mode, TODO isn't a prefix you type — it's a *state* that the heading carries. You cycle it with one keystroke. Org-mode tracks it, queries it, and reports on it."

---

## Basic TODO States

Any heading can become a task by adding a TODO keyword:

```org
* TODO Write the API documentation
* DONE Set up the database
* TODO Review pull request from Marcus
```

The magic: put your cursor on a TODO heading and press `C-c C-t`.

| Press | State Change |
|---|---|
| `C-c C-t` | → TODO |
| `C-c C-t` | TODO → DONE |
| `C-c C-t` | DONE → (none) |

It cycles: unmarked → TODO → DONE → unmarked.

When you mark something DONE, org-mode adds a timestamp:

```org
* DONE Set up the database
  CLOSED: [2026-01-15 Wed 14:32]
```

---

## Custom TODO States

Two states aren't enough for real work. Add this to the top of your file:

```org
#+TODO: TODO IN-PROGRESS REVIEW | DONE CANCELLED
```

The `|` separates "active" states (left) from "completed" states (right). Now `C-c C-t` cycles through all of them:

```
(none) → TODO → IN-PROGRESS → REVIEW → DONE → CANCELLED → (none)
```

Or set it globally in your Emacs config (`~/.emacs.d/init.el`):

```elisp
(setq org-todo-keywords
      '((sequence "TODO(t)" "IN-PROGRESS(i)" "REVIEW(r)" "|" "DONE(d)" "CANCELLED(c)")))
```

The letters in parentheses are fast-select keys. With this config, `C-c C-t` shows a menu:

```
Select keyword: [t] TODO  [i] IN-PROGRESS  [r] REVIEW  [d] DONE  [c] CANCELLED
```

Press `i` to jump straight to IN-PROGRESS without cycling.

---

## TODO Faces (Colors)

Org-mode colors TODO states by default:
- **TODO** — red (needs attention)
- **DONE** — green (completed)
- Custom states get default colors, or you configure them:

```elisp
(setq org-todo-keyword-faces
      '(("IN-PROGRESS" . (:foreground "orange" :weight bold))
        ("REVIEW" . (:foreground "purple" :weight bold))
        ("CANCELLED" . (:foreground "gray" :strike-through t))))
```

---

## Priorities

Not all tasks are equal. Org-mode has three priority levels:

```org
* TODO [#A] Fix production crash
* TODO [#B] Implement new feature
* TODO [#C] Update README typo
```

| Priority | Meaning |
|---|---|
| `[#A]` | High — do this first |
| `[#B]` | Medium — default |
| `[#C]` | Low — when you get to it |

Set priority with:

| Binding | Action |
|---|---|
| `C-c ,` | Set priority (prompts for A/B/C) |
| `S-up` | Increase priority |
| `S-down` | Decrease priority |

Priorities affect sorting in the agenda (Chapter 10) — `[#A]` items float to the top.

---

## Checkboxes: Subtask Tracking

For tasks with multiple steps that don't need their own heading:

```org
* TODO Implement user authentication
  - [X] Research JWT libraries
  - [X] Set up auth middleware
  - [ ] Implement login endpoint
  - [ ] Implement registration endpoint
  - [ ] Add password reset flow
  - [ ] Write integration tests
```

| Binding | Action |
|---|---|
| `C-c C-c` | Toggle checkbox under cursor |
| `M-S-RET` | New checkbox item |

`[X]` = done, `[ ]` = not done. Toggle with `C-c C-c` on the line.

---

## Progress Indicators

Add a cookie to the parent heading to see progress:

```org
* TODO Implement user authentication [2/6]
  - [X] Research JWT libraries
  - [X] Set up auth middleware
  - [ ] Implement login endpoint
  - [ ] Implement registration endpoint
  - [ ] Add password reset flow
  - [ ] Write integration tests
```

Or use percentages:

```org
* TODO Implement user authentication [33%]
  - [X] Research JWT libraries
  - [X] Set up auth middleware
  - [ ] Implement login endpoint
  - [ ] Implement registration endpoint
  - [ ] Add password reset flow
  - [ ] Write integration tests
```

Type `[/]` or `[%]` in the heading — org-mode auto-updates the count when you toggle checkboxes. The counter updates every time you press `C-c C-c` on a checkbox.

---

## Practical: Sprint Board in Org

Create `~/org/sprint-board.org`:

```org
#+TITLE: Sprint 14 Board
#+TODO: TODO IN-PROGRESS REVIEW | DONE CANCELLED

* Sprint 14 [1/6]

** DONE [#A] Fix login redirect loop on Safari
   CLOSED: [2026-01-13 Mon 10:15]
   Reported by 3 users. Was a cookie SameSite issue.

** IN-PROGRESS [#A] Dashboard: Recent Activity Feed
   - [X] Design API response shape
   - [X] Implement GET /activity endpoint
   - [ ] Build ActivityFeed component
   - [ ] Add loading skeleton
   - [ ] Write tests

** TODO [#A] Dashboard: Deadline Widget
   - [ ] Query upcoming deadlines across projects
   - [ ] Build DeadlineWidget component
   - [ ] Handle empty state

** REVIEW [#B] Notification count fix
   PR #892 — waiting on Marcus to review.

** TODO [#B] File upload chunking
   Need to support files > 5MB.
   - [ ] Research tus.io protocol
   - [ ] Implement chunked upload endpoint
   - [ ] Update frontend upload component

** CANCELLED [#C] Spike: Push notifications
   Moved to Sprint 15 — not enough capacity.
```

Now you can:
- `S-Tab` to see just the task titles and their states
- `C-c C-t` to move tasks through your workflow
- `C-c C-c` on checkboxes to track subtask progress
- See `[1/6]` update as you complete tasks

---

## Logging State Changes

Want to know *when* things changed state? Add this:

```org
#+TODO: TODO(t!) IN-PROGRESS(i!) REVIEW(r!) | DONE(d!) CANCELLED(c!)
```

The `!` means "log a timestamp when entering this state." Now when you cycle:

```org
** IN-PROGRESS [#A] Dashboard: Recent Activity Feed
   :LOGBOOK:
   - State "IN-PROGRESS" from "TODO"       [2026-01-14 Tue 09:00]
   - State "TODO"         from ""           [2026-01-13 Mon 14:00]
   :END:
```

You get a full history of state transitions. Useful for retrospectives.

---

## Tags

Add tags to headings for categorization:

```org
* TODO Fix login bug                                        :backend:urgent:
* TODO Update dashboard styles                              :frontend:
* TODO Write API documentation                              :docs:backend:
```

Tags go at the end of the heading line, surrounded by colons. Set them with `C-c C-q` (or `C-c C-c` on the heading).

Tags are searchable in the agenda (Chapter 10) — "show me all `:backend:` tasks."

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c C-t` | Cycle TODO state |
| `C-c ,` | Set priority |
| `S-up` / `S-down` | Increase/decrease priority |
| `C-c C-c` | Toggle checkbox |
| `M-S-RET` | New TODO heading / checkbox item |
| `C-c C-q` | Set tags |
| `C-c / t` | Sparse tree: show all TODOs |

---

## Exercise: Convert Your Real Task List

1. Open whatever task manager you currently use (Todoist, Jira, sticky notes, your brain).
2. Create `~/org/tasks.org` and dump everything in:

```org
#+TITLE: My Tasks
#+TODO: TODO NEXT IN-PROGRESS WAITING | DONE CANCELLED

* Work [/]
** TODO [#A] <your most urgent task>
** TODO [#B] <next task>
** TODO [#C] <that thing you keep putting off>

* Personal [/]
** TODO <something you need to do>
** TODO <something else>

* Someday/Maybe
** <ideas that aren't actionable yet>
```

3. Add checkboxes to at least one task with 3+ subtasks.
4. Practice cycling states with `C-c C-t`.
5. Set priorities on your top 3 items.
6. Mark one thing DONE and watch the `[/]` counter update.

> **Nadia's tip:** "The power isn't in the syntax — it's in having ONE place for all tasks. When everything is in org files, you can query across all of them. 'Show me every [#A] TODO tagged :backend:' — one keystroke. Try that with Todoist + Jira + sticky notes."

---

[← Ch 1](chapter-01-outlines.md) | [Ch 3: Never Miss a Deadline →](chapter-03-scheduling.md)
