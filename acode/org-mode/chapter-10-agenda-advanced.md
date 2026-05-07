# Chapter 10: The Command Center — Advanced Agenda and GTD

[← Ch 9](chapter-09-clocking.md) | [Ch 11 →](chapter-11-roam.md)

---

## The Problem

You have tasks scattered across 10 org files. The basic agenda (Chapter 3) shows your week. But you need more: "Show me all high-priority backend tasks." "What's stuck — started but not progressing?" "What did I complete this week?" The default agenda is a calendar. You need a *dashboard*.

---

## The Naive Attempt

You open each org file and scan for relevant tasks. Or you use `grep` across your org directory. It works, but it's slow, manual, and you can't sort or filter the results interactively.

---

## Nadia's Way: Custom Agenda Views

> "The agenda isn't just a calendar — it's a query engine for your entire org system. I have custom views: my daily driver shows today's schedule + overdue + high-priority. My weekly review shows completed items + stuck projects. My sprint view shows only work-tagged items by status. All one keystroke away."

---

## Custom Agenda Commands

Add to your config:

```elisp
(setq org-agenda-custom-commands
      '(("d" "Daily Driver"
         ((agenda "" ((org-agenda-span 'day)))
          (tags-todo "+PRIORITY=\"A\""
                     ((org-agenda-overriding-header "High Priority")))
          (tags-todo "+PRIORITY=\"B\"+TODO=\"IN-PROGRESS\""
                     ((org-agenda-overriding-header "In Progress")))
          (tags-todo "+TODO=\"WAITING\""
                     ((org-agenda-overriding-header "Waiting On")))
          ))

        ("w" "Weekly Review"
         ((agenda "" ((org-agenda-span 'week)))
          (tags "+TODO=\"DONE\"+CLOSED>=\"<-7d>\""
                ((org-agenda-overriding-header "Completed This Week")))
          (stuck ""
                 ((org-agenda-overriding-header "Stuck Projects")))
          ))

        ("p" "Projects"
         ((tags-todo "+project"
                     ((org-agenda-overriding-header "Active Projects")))))

        ("b" "Backend Tasks"
         ((tags-todo "+backend"
                     ((org-agenda-overriding-header "Backend")))))))
```

Now `C-c a d` shows your daily driver. `C-c a w` shows your weekly review.

---

## Agenda View Types

Each entry in a custom command can be:

| Type | What It Shows |
|---|---|
| `agenda` | Calendar view (scheduled/deadline items) |
| `todo` | All items with a specific TODO state |
| `tags` | Items matching a tag/property query |
| `tags-todo` | TODO items matching a tag query |
| `stuck` | Projects with no next action |
| `search` | Full-text search results |

---

## Tag and Property Queries

The query language is powerful:

| Query | Matches |
|---|---|
| `+backend` | Has tag `:backend:` |
| `+backend+urgent` | Has BOTH tags |
| `+backend-frontend` | Has `:backend:` but NOT `:frontend:` |
| `+PRIORITY="A"` | Priority A |
| `+TODO="IN-PROGRESS"` | In-progress state |
| `+Effort<"2:00"` | Effort under 2 hours |
| `+SCHEDULED<"<today>"` | Scheduled before today (overdue) |

Combine them:

```
+backend+PRIORITY="A"+TODO="TODO"
```

= Backend tasks, high priority, not yet started.

---

## Filtering in the Agenda

Once you're in an agenda view, filter interactively:

| Binding | Action |
|---|---|
| `/` | Filter by tag |
| `\` | Filter by tag (narrow) |
| `<` | Filter by category (file) |
| `=` | Filter by regex |
| `|` | Remove all filters |
| `t` | Cycle TODO state of item |
| `I` | Clock in |
| `O` | Clock out |
| `r` | Refresh |

Example: You're in the weekly agenda. Press `/` then type `backend` — only backend-tagged items remain visible.

---

## Stuck Projects

A "stuck project" is a heading with sub-tasks where none of the sub-tasks have a "next action" state. Configure what counts:

```elisp
(setq org-stuck-projects
      '("+project/-DONE-CANCELLED"  ;; identify projects by tag, exclude done
        ("TODO" "IN-PROGRESS")       ;; these states count as "next actions"
        nil                          ;; no tags required
        ""))                         ;; no regex required
```

Now `C-c a #` (or your custom view with `stuck`) shows projects that have no active next step — they're stalled and need attention.

---

## The GTD Workflow in Org

Getting Things Done (David Allen's method) maps perfectly to org-mode:

```
┌─────────────────────────────────────────────────────────┐
│ GTD Concept          │ Org-mode Implementation           │
├──────────────────────┼───────────────────────────────────┤
│ Inbox                │ ~/org/inbox.org (capture target)   │
│ Next Actions         │ TODO state "NEXT"                  │
│ Projects             │ Headings tagged :project:          │
│ Waiting For          │ TODO state "WAITING"               │
│ Someday/Maybe        │ ~/org/someday.org                  │
│ Reference            │ ~/org/notes.org                    │
│ Calendar             │ SCHEDULED/DEADLINE timestamps      │
│ Weekly Review        │ Custom agenda view                 │
└──────────────────────┴───────────────────────────────────┘
```

GTD-oriented TODO states:

```elisp
(setq org-todo-keywords
      '((sequence "TODO(t)" "NEXT(n)" "IN-PROGRESS(i)" "WAITING(w@)" "|" "DONE(d)" "CANCELLED(c@)")))
```

The `@` means "prompt for a note when entering this state" — useful for WAITING ("waiting on whom?") and CANCELLED ("why?").

---

## Practical: The Developer's GTD Setup

```elisp
;; Files
(setq org-agenda-files '("~/org/inbox.org"
                          "~/org/work.org"
                          "~/org/personal.org"
                          "~/org/projects.org"))

;; Custom agenda views
(setq org-agenda-custom-commands
      '(("g" "GTD View"
         ((agenda "" ((org-agenda-span 'day)
                      (org-agenda-overriding-header "Today")))
          (tags-todo "+TODO=\"NEXT\""
                     ((org-agenda-overriding-header "Next Actions")))
          (tags-todo "+TODO=\"WAITING\""
                     ((org-agenda-overriding-header "Waiting For")))
          (tags-todo "+TODO=\"IN-PROGRESS\""
                     ((org-agenda-overriding-header "In Progress")))
          (stuck ""
                 ((org-agenda-overriding-header "Stuck Projects")))
          (tags "+inbox"
                ((org-agenda-overriding-header "Inbox (process me!)")))))

        ("r" "Weekly Review"
         ((agenda "" ((org-agenda-span 'week)
                      (org-agenda-start-on-weekday 1)))
          (tags "+TODO=\"DONE\"+CLOSED>=\"<-7d>\""
                ((org-agenda-overriding-header "Done This Week")))
          (tags-todo "+TODO=\"TODO\"+PRIORITY=\"A\""
                     ((org-agenda-overriding-header "High Priority Not Started")))
          (stuck ""
                 ((org-agenda-overriding-header "Stuck Projects")))
          (tags-todo "+TODO=\"WAITING\""
                     ((org-agenda-overriding-header "Still Waiting?")))
          ))

        ("s" "Sprint"
         ((tags-todo "+sprint+TODO=\"IN-PROGRESS\""
                     ((org-agenda-overriding-header "In Progress")))
          (tags-todo "+sprint+TODO=\"NEXT\""
                     ((org-agenda-overriding-header "Up Next")))
          (tags-todo "+sprint+TODO=\"REVIEW\""
                     ((org-agenda-overriding-header "In Review")))
          (tags-todo "+sprint+TODO=\"TODO\""
                     ((org-agenda-overriding-header "Backlog")))))))
```

---

## Agenda Bulk Actions

Select multiple items and act on them at once:

| Binding | Action |
|---|---|
| `m` | Mark item for bulk action |
| `u` | Unmark item |
| `U` | Unmark all |
| `B t` | Bulk change TODO state |
| `B s` | Bulk schedule |
| `B d` | Bulk set deadline |
| `B r` | Bulk refile |
| `B $` | Bulk archive |

Example: End of sprint, mark all completed items with `m`, then `B $` to archive them all.

---

## Category and File Organization

The "category" in the agenda comes from the filename by default. Customize:

```org
#+CATEGORY: Dashboard
```

Now items from this file show as "Dashboard:" in the agenda instead of the filename.

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c a` | Agenda dispatcher |
| `C-c a d` | Custom: daily driver (after setup) |
| `C-c a t` | Global TODO list |
| `C-c a m` | Match tags/properties |
| `C-c a #` | Stuck projects |
| `/` | Filter by tag (in agenda) |
| `<` | Filter by category (in agenda) |
| `m` | Mark for bulk action |
| `B t` | Bulk TODO state change |
| `q` | Quit agenda |

---

## Exercise: Build Your Command Center

1. Set up at least 2 custom agenda commands in your config:
   - A "daily driver" that shows today + high priority + in-progress
   - A "weekly review" that shows the week + completed items

2. Tag at least 5 tasks across your org files with relevant tags (`:backend:`, `:frontend:`, `:urgent:`, etc.).

3. Open your custom agenda with `C-c a` + your key.

4. Practice filtering: press `/` and filter by a tag. Press `|` to clear.

5. Try bulk actions: mark 2-3 items with `m`, then `B t` to change their state.

6. Set up stuck projects:
   - Create a heading tagged `:project:` with sub-tasks
   - Remove all "next action" states from sub-tasks
   - Verify it shows in the stuck projects view

> **Nadia's tip:** "My daily ritual: open Emacs, `C-c a d` for my daily view. I see today's schedule, overdue items, and what's in progress. Takes 10 seconds to know exactly what needs my attention. The weekly review (`C-c a r`) on Friday shows what I accomplished and what's stuck. It's the closest thing to a productivity superpower I've found."

---

[← Ch 9](chapter-09-clocking.md) | [Ch 11: Build a Second Brain →](chapter-11-roam.md)
