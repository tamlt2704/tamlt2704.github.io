# Chapter 12: Putting It All Together — The Developer's Daily Workflow

[← Ch 11](chapter-11-roam.md)

---

## The Problem

You've learned the pieces: outlines, TODOs, scheduling, capture, tables, links, export, Babel, clocking, agenda, and roam. But how do they fit together in a real day? What does it actually look like to run your developer life in org-mode?

---

## The Naive Attempt

You set up org-mode, use it for a week, then drift back to old habits. The system is too complex. You don't have a routine. The tools are powerful but you're not sure *when* to use *which*.

---

## Nadia's Way: A System, Not a Collection of Features

> "Org-mode isn't about features — it's about a workflow. I have a morning routine, a during-work flow, and an end-of-day ritual. Each takes 5-10 minutes. The rest of the day, I just capture and clock. The system runs itself once you build the habit."

---

## The File Structure

A complete developer org setup:

```
~/org/
├── inbox.org           ← capture target (temporary holding)
├── work.org            ← work tasks and projects
├── personal.org        ← personal tasks
├── projects.org        ← active project plans (detailed)
├── notes.org           ← reference material
├── journal.org         ← daily log (datetree)
├── someday.org         ← ideas for later
├── reading.org         ← articles/books to read
├── meetings.org        ← meeting notes
├── roam/               ← knowledge base (org-roam)
│   ├── daily/          ← daily notes
│   └── *.org           ← concept notes
└── archive/            ← completed projects (out of agenda)
```

---

## Morning Routine (5 minutes)

```
  1. Open agenda: C-c a d (daily driver view)
  2. Review today's schedule
  3. Check overdue items — reschedule or do
  4. Pick 1-3 items to focus on today
  5. Clock into the first task: C-c C-x C-i
```

Your daily driver agenda (from Chapter 10):

```elisp
("d" "Daily Driver"
 ((agenda "" ((org-agenda-span 'day)
              (org-agenda-overriding-header "Today")))
  (tags-todo "+PRIORITY=\"A\"+TODO=\"TODO\""
             ((org-agenda-overriding-header "High Priority — Not Started")))
  (tags-todo "+TODO=\"IN-PROGRESS\""
             ((org-agenda-overriding-header "In Progress")))
  (tags-todo "+TODO=\"WAITING\""
             ((org-agenda-overriding-header "Waiting For")))
  (tags "+inbox+TODO=\"TODO\""
        ((org-agenda-overriding-header "Inbox (process me!)")))))
```

---

## During Work: The Flow

### Starting a task
```
C-c C-x C-i          → clock in
C-c C-t → i          → set state to IN-PROGRESS
```

### Having a thought (without losing flow)
```
C-c c t              → capture a TODO
Type the thought
C-c C-c              → saved to inbox, back to work
```

### Finishing a task
```
C-c C-t → d          → set state to DONE (auto clocks out)
C-c C-x C-i          → clock into next task
```

### Quick note about current work
```
C-c c n              → capture a note (links back to current file)
```

### Switching tasks
```
C-c C-x C-o          → clock out of current
Navigate to new task
C-c C-x C-i          → clock into new task
```

---

## Meeting Workflow

### Before the meeting
```org
* TODO Prepare for architecture review                    :meeting:
  SCHEDULED: <2026-01-15 Wed 14:00>
  - [ ] Review Sarah's proposal
  - [ ] Prepare questions about scaling
  - [ ] Check current metrics
```

### During the meeting
```
C-c c m              → capture meeting note
```

Or clock into the meeting heading and take notes directly:

```org
* Meeting: Architecture Review [2026-01-15]               :meeting:
  :LOGBOOK:
  CLOCK: [2026-01-15 Wed 14:00]--[2026-01-15 Wed 15:15] =>  1:15
  :END:

** Attendees
   You, Sarah, Marcus, Nadia

** Decisions
   - Use Redis pub/sub for MVP notifications
   - Defer Kafka evaluation to Q2

** Action Items
   - [ ] You: Implement consumer service by Friday
   - [ ] Sarah: Update architecture diagram
   - [ ] Marcus: WebSocket spike

** Notes
   Sarah concerned about message ordering.
   Accepted eventual consistency for MVP.
```

### After the meeting
Refile action items to appropriate projects with `C-c C-w`.

---

## End of Day Ritual (10 minutes)

```
  1. Clock out: C-c C-x C-o
  2. Process inbox: open inbox.org
     - For each item: add context, refile, or delete
     - Goal: empty inbox
  3. Quick journal entry: C-c c j
     - What did I accomplish?
     - What's blocking me?
     - What's the plan for tomorrow?
  4. Check tomorrow's agenda: C-c a d, then f (forward one day)
  5. Git commit your org files:
     cd ~/org && git add -A && git commit -m "$(date +%Y-%m-%d)"
```

---

## Weekly Review (Friday, 15 minutes)

Open your weekly review view: `C-c a r`

```
  1. Review completed items — celebrate progress
  2. Check stuck projects — what needs unblocking?
  3. Review WAITING items — follow up?
  4. Process someday.org — anything ready to activate?
  5. Plan next week — set SCHEDULED dates for key tasks
  6. Generate time report: C-c C-x C-r (clock table for the week)
```

### Weekly Review Template

Create a recurring task:

```org
* TODO Weekly Review
  SCHEDULED: <2026-01-17 Fri 16:00 +1w>
  
  - [ ] Review agenda view for completed items
  - [ ] Check stuck projects
  - [ ] Follow up on WAITING items
  - [ ] Process someday.org
  - [ ] Plan next week's priorities
  - [ ] Generate clock table report
  - [ ] Archive completed projects
  - [ ] Git push org files
```

---

## The Complete Config

Here's a full developer org-mode configuration:

```elisp
;; === Org Mode Configuration ===

;; Basic setup
(setq org-directory "~/org/")
(setq org-default-notes-file (concat org-directory "inbox.org"))

;; Agenda
(setq org-agenda-files '("~/org/inbox.org"
                          "~/org/work.org"
                          "~/org/personal.org"
                          "~/org/projects.org"
                          "~/org/meetings.org"))

;; TODO states
(setq org-todo-keywords
      '((sequence "TODO(t)" "NEXT(n)" "IN-PROGRESS(i!)" "WAITING(w@)" "REVIEW(r)"
                  "|" "DONE(d!)" "CANCELLED(c@)")))

(setq org-todo-keyword-faces
      '(("NEXT" . (:foreground "DeepSkyBlue" :weight bold))
        ("IN-PROGRESS" . (:foreground "orange" :weight bold))
        ("WAITING" . (:foreground "yellow" :weight bold))
        ("REVIEW" . (:foreground "purple" :weight bold))
        ("CANCELLED" . (:foreground "gray" :strike-through t))))

;; Log state changes
(setq org-log-done 'time)
(setq org-log-into-drawer t)

;; Capture templates
(global-set-key (kbd "C-c c") #'org-capture)
(global-set-key (kbd "C-c a") #'org-agenda)
(global-set-key (kbd "C-c l") #'org-store-link)

(setq org-capture-templates
      '(("t" "Task" entry (file+headline "~/org/inbox.org" "Tasks")
         "* TODO [#B] %?\n  %U\n  %a" :empty-lines 1)
        ("n" "Note" entry (file+headline "~/org/inbox.org" "Notes")
         "* %?\n  %U\n  %a" :empty-lines 1)
        ("j" "Journal" entry (file+datetree "~/org/journal.org")
         "* %U %?\n  %i" :empty-lines 1)
        ("m" "Meeting" entry (file+headline "~/org/meetings.org" "Meetings")
         "* %^{Title} :meeting:\n  %U\n  Attendees: %^{Attendees}\n** Notes\n   %?\n** Action Items\n"
         :empty-lines 1)
        ("b" "Bug" entry (file+headline "~/org/inbox.org" "Bugs")
         "* TODO [#A] BUG: %?\n  %U\n  %a\n  Reproduce:\n  Expected:\n  Actual:"
         :empty-lines 1)))

;; Refile
(setq org-refile-targets '((org-agenda-files :maxlevel . 3)))
(setq org-refile-use-outline-path t)
(setq org-outline-path-complete-in-steps nil)

;; Clocking
(setq org-clock-out-when-done t)
(setq org-clock-persist t)
(setq org-clock-idle-time 15)
(org-clock-persistence-inuse)

;; Custom agenda views
(setq org-agenda-custom-commands
      '(("d" "Daily"
         ((agenda "" ((org-agenda-span 'day)))
          (tags-todo "+PRIORITY=\"A\""
                     ((org-agenda-overriding-header "High Priority")))
          (tags-todo "+TODO=\"IN-PROGRESS\""
                     ((org-agenda-overriding-header "In Progress")))
          (tags-todo "+TODO=\"WAITING\""
                     ((org-agenda-overriding-header "Waiting")))
          (tags-todo "+inbox"
                     ((org-agenda-overriding-header "Inbox")))))
        ("r" "Review"
         ((agenda "" ((org-agenda-span 'week)))
          (stuck "" ((org-agenda-overriding-header "Stuck")))
          (tags-todo "+TODO=\"WAITING\""
                     ((org-agenda-overriding-header "Waiting")))))))

;; Stuck projects
(setq org-stuck-projects
      '("+project/-DONE-CANCELLED" ("TODO" "NEXT" "IN-PROGRESS") nil ""))

;; Babel languages
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (shell . t)
   (js . t)
   (emacs-lisp . t)))

;; Org-roam (if installed)
(use-package org-roam
  :ensure t
  :custom
  (org-roam-directory (file-truename "~/org/roam/"))
  :bind (("C-c n f" . org-roam-node-find)
         ("C-c n i" . org-roam-node-insert)
         ("C-c n l" . org-roam-buffer-toggle)
         ("C-c n d" . org-roam-dailies-goto-today))
  :config
  (org-roam-db-autosync-mode))
```

---

## Sprint Workflow Example

### Monday: Sprint Planning

```org
#+TITLE: Sprint 15
#+CATEGORY: Sprint15
#+TODO: TODO NEXT IN-PROGRESS REVIEW | DONE CANCELLED

* Sprint 15 Goals [0/3]
  - [ ] Ship notification system MVP
  - [ ] Close all P1 bugs
  - [ ] Complete API documentation

* Stories
** TODO [#A] Notification: Consumer Service                :backend:sprint:
   SCHEDULED: <2026-01-20 Mon>
   DEADLINE: <2026-01-24 Fri>
   :PROPERTIES:
   :Effort:   8:00
   :END:
   - [ ] Set up Redis connection
   - [ ] Implement message handler
   - [ ] Add retry logic
   - [ ] Write tests
   - [ ] Deploy to staging

** TODO [#A] Notification: Frontend WebSocket              :frontend:sprint:
   SCHEDULED: <2026-01-22 Wed>
   DEADLINE: <2026-01-24 Fri>
   :PROPERTIES:
   :Effort:   5:00
   :END:

** TODO [#B] API Docs: Authentication endpoints            :docs:sprint:
   :PROPERTIES:
   :Effort:   3:00
   :END:

** TODO [#A] BUG: Memory leak in worker process            :backend:sprint:
   DEADLINE: <2026-01-21 Tue>
   :PROPERTIES:
   :Effort:   4:00
   :END:
```

### During the Sprint

Clock in/out as you work. Cycle states. Check off subtasks. The agenda shows what's due. The clock table shows where time went.

### Friday: Sprint Review

```org
#+BEGIN: clocktable :scope file :maxlevel 2 :block thisweek
#+END:
```

Generate the report. Compare effort estimates to actuals. Feed into next sprint's planning.

---

## What's Next

You've built a complete system. Here's what to explore when you're ready:

| Topic | What It Does |
|---|---|
| **org-publish** | Static site generator from org files |
| **org-present** | Presentations from org headings |
| **org-noter** | Annotate PDFs with org notes |
| **org-ref** | Academic citations and references |
| **org-super-agenda** | Better agenda grouping and formatting |
| **org-ql** | SQL-like queries for org headings |
| **ox-hugo** | Export org to Hugo blog posts |
| **org-habit** | Track daily habits with consistency graphs |
| **org-crypt** | Encrypt sensitive headings |
| **org-contacts** | Contact management in org |

---

## The Transformation

Remember where you started? Five apps. Nothing connected. Scattered notes. Missed deadlines. No idea where your time went.

Now:
- **One system** — plain text, version-controlled, yours forever
- **One inbox** — nothing falls through the cracks
- **One agenda** — your week at a glance
- **One clock** — know exactly where time goes
- **One knowledge base** — notes that connect and compound
- **One source** — write once, export anywhere

All of it searchable. All of it greppable. All of it offline. All of it in files you'll be able to read in 30 years.

---

## Exercise: Build Your Complete System

1. Set up the full config from this chapter in your `~/.emacs.d/init.el`.
2. Create the file structure (`inbox.org`, `work.org`, `personal.org`, `journal.org`).
3. Do a full day using the workflow:
   - Morning: check agenda, pick tasks
   - During: capture thoughts, clock tasks
   - End of day: process inbox, journal entry
4. At end of week: run the weekly review checklist.
5. Generate a clock table for the week.
6. Commit your org directory to git.

> **Nadia's tip:** "Don't try to adopt everything at once. Start with capture + agenda. That alone is life-changing. Add clocking after a week. Add roam after a month. The system grows with you. I've been using org-mode for 6 years and I'm still discovering features. But the core — capture, TODO, agenda, clock — that's been my daily driver since week two. Keep it simple. Let it grow."

---

## Quick Reference Card

| Action | Binding |
|---|---|
| **Navigation** | |
| Fold/unfold heading | `Tab` |
| Global fold/unfold | `S-Tab` |
| New heading | `M-RET` |
| Move heading up/down | `M-up` / `M-down` |
| Promote/demote | `M-left` / `M-right` |
| **Tasks** | |
| Cycle TODO state | `C-c C-t` |
| Set priority | `C-c ,` |
| Toggle checkbox | `C-c C-c` |
| Set tags | `C-c C-q` |
| **Scheduling** | |
| Insert timestamp | `C-c .` |
| Set deadline | `C-c C-d` |
| Set scheduled | `C-c C-s` |
| Open agenda | `C-c a` |
| **Capture & Refile** | |
| Capture | `C-c c` |
| Finalize capture | `C-c C-c` |
| Refile | `C-c C-w` |
| **Links** | |
| Insert link | `C-c C-l` |
| Open link | `C-c C-o` |
| **Export** | |
| Export dispatcher | `C-c C-e` |
| **Code** | |
| Execute block | `C-c C-c` |
| Tangle | `C-c C-v t` |
| Edit in native mode | `C-c '` |
| **Clocking** | |
| Clock in | `C-c C-x C-i` |
| Clock out | `C-c C-x C-o` |
| Clock report | `C-c C-x C-r` |
| **Roam** | |
| Find node | `C-c n f` |
| Insert link | `C-c n i` |
| Backlinks | `C-c n l` |
| Daily note | `C-c n d` |

---

[← Ch 11](chapter-11-roam.md)
