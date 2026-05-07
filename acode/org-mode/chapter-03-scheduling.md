# Chapter 3: Never Miss a Deadline — Scheduling and the Agenda

[← Ch 2](chapter-02-todo.md) | [Ch 4 →](chapter-04-capture-refile.md)

---

## The Problem

You have tasks (Chapter 2). But *when* are they due? When should you *start* working on them? You're still checking a separate calendar app. Deadlines sneak up because your task list doesn't know about time.

Last week you missed a code review deadline because it was in Google Calendar and your tasks were in org-mode. Two systems. Two places to check. One fell through the cracks.

---

## The Naive Attempt

You add dates manually to headings:

```org
* TODO Submit PR for review (due Friday)
* TODO Prepare sprint demo (Jan 20)
* TODO Renew SSL certificate (before March 1!!)
```

This is just text. Org-mode can't query it. You can't ask "what's due this week?" You're back to scanning the whole file with your eyes.

---

## Nadia's Way: Timestamps Are Queryable

> "Org-mode timestamps aren't decoration — they're structured data. Add a DEADLINE and it shows up in your agenda. Add SCHEDULED and org-mode reminds you when to start. The agenda pulls from ALL your org files and shows you one unified view of your week."

---

## Timestamps

Org-mode has two timestamp formats:

```org
Active:   <2026-01-20 Mon>        (shows in agenda)
Inactive: [2026-01-20 Mon]        (doesn't show in agenda, just a record)
```

Insert a timestamp:

| Binding | Action |
|---|---|
| `C-c .` | Insert/edit active timestamp |
| `C-c !` | Insert/edit inactive timestamp |

When you press `C-c .`, a date picker appears in the minibuffer:

```
Date+time [2026-01-15 Wed]:
```

You can type:
- `2026-01-20` — specific date
- `+3` — three days from today
- `+2w` — two weeks from today
- `fri` — next Friday
- `11:00` — add a time

---

## DEADLINE and SCHEDULED

These are the two planning properties that make the agenda work:

```org
* TODO Submit PR for review
  DEADLINE: <2026-01-20 Mon>

* TODO Start working on dashboard feature
  SCHEDULED: <2026-01-16 Thu>
```

| Property | Meaning |
|---|---|
| `DEADLINE` | Must be done BY this date. Agenda warns you as it approaches. |
| `SCHEDULED` | Plan to START working on this date. Appears in agenda from that day forward. |

Set them with:

| Binding | Action |
|---|---|
| `C-c C-d` | Set DEADLINE |
| `C-c C-s` | Set SCHEDULED |

The difference matters:
- **DEADLINE** = "this is due Friday" (shows warnings: "In 3 days", "In 2 days", "OVERDUE!")
- **SCHEDULED** = "I'll start this on Thursday" (appears in agenda starting Thursday, carries forward if not done)

---

## Timestamps with Times

```org
* TODO Team standup
  <2026-01-16 Thu 09:30>

* TODO Deploy to production
  SCHEDULED: <2026-01-17 Fri 14:00>
  DEADLINE: <2026-01-17 Fri 17:00>
```

Time ranges:

```org
* Meeting with design team
  <2026-01-16 Thu 14:00-15:30>
```

---

## Repeating Tasks

Some tasks recur. Don't create them manually each week:

```org
* TODO Weekly team standup
  SCHEDULED: <2026-01-16 Thu 09:30 +1w>

* TODO Pay rent
  DEADLINE: <2026-02-01 Sat +1m>

* TODO Water plants
  SCHEDULED: <2026-01-15 Wed +3d>
```

| Repeater | Meaning |
|---|---|
| `+1d` | Every day |
| `+1w` | Every week |
| `+2w` | Every two weeks |
| `+1m` | Every month |
| `+1y` | Every year |

When you mark a repeating task DONE, org-mode:
1. Resets it to TODO
2. Shifts the date forward by the repeat interval
3. Logs that you completed it

```org
* TODO Weekly team standup
  SCHEDULED: <2026-01-23 Thu 09:30 +1w>
  :LOGBOOK:
  - State "DONE" from "TODO" [2026-01-16 Thu 09:45]
  :END:
```

### Repeat Variants

| Syntax | Behavior |
|---|---|
| `+1w` | Shift from the original date (may accumulate if you miss one) |
| `++1w` | Shift to at least one week from today |
| `.+1w` | Shift to exactly one week from today (ignores original date) |

Use `.+1w` for "every week from when I last did it" (like watering plants). Use `+1w` for "every Thursday" (like standups).

---

## The Agenda: Your Command Center

The agenda is where it all comes together. It queries ALL your org files and shows a unified view.

First, tell org-mode which files to scan:

```elisp
;; In ~/.emacs.d/init.el
(setq org-agenda-files '("~/org/"))
```

This scans every `.org` file in `~/org/`. Now press:

```
C-c a
```

You see the agenda dispatcher:

```
Press key for an agenda command:
a   Agenda for the current week
t   List of all TODO entries
m   Match a TAGS/PROP/TODO query
s   Search for keywords
```

Press `a` for the weekly agenda:

```
Week-agenda (W03):
Monday     13 January 2026
  tasks:      DEADLINE: In 2 d.: TODO Submit PR for review
Tuesday    14 January 2026
Wednesday  15 January 2026
  tasks:      Scheduled: TODO Start working on dashboard feature
Thursday   16 January 2026
  tasks:      09:30 Scheduled: TODO Weekly team standup
Friday     17 January 2026
  tasks:      DEADLINE: TODO Submit PR for review
  tasks:      14:00 Scheduled: TODO Deploy to production
```

From the agenda view:
- `RET` on an item → jump to it in the org file
- `t` on an item → cycle its TODO state
- `f` / `b` → forward/backward one week
- `d` → day view
- `w` → week view

---

## Deadline Warnings

By default, org-mode warns you about deadlines 14 days in advance. The agenda shows:

```
  tasks:      In 5 d.: DEADLINE: TODO Renew SSL certificate
```

Customize the warning period per task:

```org
* TODO Renew SSL certificate
  DEADLINE: <2026-03-01 Sun -30d>
```

The `-30d` means "warn me 30 days before." For critical deadlines, set longer warnings.

---

## Practical: Your Week in Org

Create `~/org/schedule.org`:

```org
#+TITLE: Schedule

* Recurring
** TODO Weekly standup
   SCHEDULED: <2026-01-16 Thu 09:30 +1w>
** TODO Sprint retrospective
   SCHEDULED: <2026-01-17 Fri 16:00 +2w>
** TODO Review dependabot PRs
   SCHEDULED: <2026-01-15 Wed +1w>

* This Sprint
** TODO [#A] Dashboard MVP
   SCHEDULED: <2026-01-14 Tue>
   DEADLINE: <2026-01-20 Mon>
** TODO [#B] API documentation
   SCHEDULED: <2026-01-16 Thu>
   DEADLINE: <2026-01-24 Fri>
** TODO [#A] Fix Safari login bug
   DEADLINE: <2026-01-15 Wed>

* Upcoming
** TODO Prepare Q1 roadmap presentation
   DEADLINE: <2026-02-01 Sat -7d>
** TODO Renew AWS reserved instances
   DEADLINE: <2026-02-15 Sat -14d>
```

Now `C-c a a` shows your week. Everything in one view. No app switching.

---

## Agenda Navigation

| Binding | Action (in agenda buffer) |
|---|---|
| `f` | Forward one period (day/week) |
| `b` | Backward one period |
| `d` | Day view |
| `w` | Week view |
| `RET` | Go to item in org file |
| `t` | Cycle TODO state |
| `S-right` | Move timestamp forward one day |
| `S-left` | Move timestamp backward one day |
| `.` | Go to today |
| `r` | Refresh agenda |
| `q` | Quit agenda |

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c .` | Insert active timestamp |
| `C-c !` | Insert inactive timestamp |
| `C-c C-d` | Set DEADLINE |
| `C-c C-s` | Set SCHEDULED |
| `C-c a` | Open agenda dispatcher |
| `S-left` / `S-right` | Shift date by one day |
| `S-up` / `S-down` | Shift date component (year/month/day) |
| `C-c C-y` | Compute time range duration |

---

## Exercise: Schedule Your Real Week

1. Add `DEADLINE` or `SCHEDULED` to at least 5 tasks in your org files.
2. Set up `org-agenda-files` in your config:

```elisp
(setq org-agenda-files '("~/org/"))
```

3. Open the agenda with `C-c a a`.
4. Create one repeating task (weekly standup, daily review, whatever fits).
5. Mark the repeating task DONE and verify it shifts to next week.
6. Navigate the agenda: go forward a week, back a week, switch to day view.

> **Nadia's tip:** "The agenda is the reason I never go back to other systems. I have 15 org files — projects, personal, work, reading list. The agenda queries ALL of them and shows me one unified view. 'What's due this week?' One keystroke. That's the power of structured plain text."

---

[← Ch 2](chapter-02-todo.md) | [Ch 4: Capture Thoughts Instantly →](chapter-04-capture-refile.md)
