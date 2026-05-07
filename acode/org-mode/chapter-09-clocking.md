# Chapter 9: Where Does My Time Go? — Clocking and Time Reports

[← Ch 8](chapter-08-babel.md) | [Ch 10 →](chapter-10-agenda-advanced.md)

---

## The Problem

Friday afternoon. Your manager asks: "How much time did you spend on the dashboard this week?" You stare at the ceiling. "Uh... a lot?" You have no idea. You *think* you spent Monday and Tuesday on it, but there were meetings, and that production bug on Wednesday, and code reviews...

Or: you're freelancing. The client wants an itemized invoice. You open Toggl and realize you forgot to start the timer for half your sessions. The other half have entries like "working" with no description.

---

## The Naive Attempt

You try manual time tracking:
- Start a timer in Toggl/Clockify when you begin a task
- Forget to stop it when you switch tasks
- End up with a 6-hour entry that was actually 3 tasks
- Reconstruct your week from memory on Friday

Or you just don't track time and guess on invoices. Neither feels good.

---

## Nadia's Way: Clock In, Clock Out, Report

> "I clock in when I start a task. I clock out when I stop. Org-mode logs it all in the task itself. At the end of the week, I generate a report — total hours per project, per task, per day. It takes 10 seconds. My invoices are accurate to the minute."

---

## Basic Clocking

Put your cursor on any heading and:

| Binding | Action |
|---|---|
| `C-c C-x C-i` | Clock IN to this task |
| `C-c C-x C-o` | Clock OUT of current task |
| `C-c C-x C-q` | Cancel current clock |
| `C-c C-x C-j` | Jump to currently clocked task |
| `C-c C-x C-d` | Display time for each heading in buffer |

When you clock in:

```org
* IN-PROGRESS Dashboard: Activity Feed
  :LOGBOOK:
  CLOCK: [2026-01-15 Wed 09:15]
  :END:
```

When you clock out:

```org
* IN-PROGRESS Dashboard: Activity Feed
  :LOGBOOK:
  CLOCK: [2026-01-15 Wed 09:15]--[2026-01-15 Wed 11:42] =>  2:27
  :END:
```

The duration is calculated automatically. Multiple clock entries accumulate:

```org
* IN-PROGRESS Dashboard: Activity Feed
  :LOGBOOK:
  CLOCK: [2026-01-15 Wed 14:00]--[2026-01-15 Wed 16:30] =>  2:30
  CLOCK: [2026-01-15 Wed 09:15]--[2026-01-15 Wed 11:42] =>  2:27
  :END:
```

---

## The Mode Line

When you're clocked in, the Emacs mode line shows:

```
[Dashboard: Activity Feed 1:23]
```

You always know what you're clocked into and how long you've been at it.

---

## Clock Table Reports

The real power. Generate a time report with `C-c C-x C-r`:

```org
#+BEGIN: clocktable :scope file :maxlevel 3
#+CAPTION: Clock summary at [2026-01-17 Fri 17:00]
| Heading                        | Time   |      |      |
|--------------------------------+--------+------+------|
| *Total time*                   | *19:45*|      |      |
|--------------------------------+--------+------+------|
| Sprint 14                      | 19:45  |      |      |
| \_  Dashboard: Activity Feed   |        | 8:30 |      |
| \_    Frontend component       |        |      | 4:15 |
| \_    API endpoint             |        |      | 4:15 |
| \_  Dashboard: Deadline Widget |        | 5:00 |      |
| \_  Bug: Safari login          |        | 2:15 |      |
| \_  Code reviews               |        | 2:30 |      |
| \_  Meetings                   |        | 1:30 |      |
#+END:
```

Update the report by putting cursor on the `#+BEGIN:` line and pressing `C-c C-c`.

---

## Clock Table Parameters

Customize your reports:

```org
#+BEGIN: clocktable :scope file :maxlevel 2 :block thisweek
#+END:
```

| Parameter | Effect |
|---|---|
| `:scope file` | Report on current file |
| `:scope agenda` | Report on all agenda files |
| `:scope ("file1.org" "file2.org")` | Specific files |
| `:maxlevel 2` | Show headings up to level 2 |
| `:block thisweek` | Only this week's entries |
| `:block lastweek` | Last week |
| `:block 2026-01` | January 2026 |
| `:block today` | Today only |
| `:tstart "<2026-01-13>"` | Custom start date |
| `:tend "<2026-01-17>"` | Custom end date |
| `:step week` | Break down by week |
| `:step day` | Break down by day |
| `:tags t` | Show tags |
| `:compact t` | Compact format |

---

## Weekly Time Report

```org
#+BEGIN: clocktable :scope agenda :maxlevel 2 :block thisweek :step day :stepskip0 t
#+END:
```

This generates a day-by-day breakdown across ALL your org files:

```
Daily report: [2026-01-13 Mon]
| Heading              | Time  |
|----------------------+-------|
| Dashboard            | 4:30  |
| Code reviews         | 1:00  |
| Meetings             | 1:30  |
| *Total*              | *7:00*|

Daily report: [2026-01-14 Tue]
| Heading              | Time  |
|----------------------+-------|
| Dashboard            | 5:15  |
| Bug fixes            | 1:45  |
| *Total*              | *7:00*|
...
```

---

## Practical: Freelance Billing

```org
#+TITLE: Client: Acme Corp — January 2026

* Billable Work

** TODO [#A] API Redesign
   :LOGBOOK:
   CLOCK: [2026-01-15 Wed 09:00]--[2026-01-15 Wed 12:30] =>  3:30
   CLOCK: [2026-01-14 Tue 13:00]--[2026-01-14 Tue 17:00] =>  4:00
   CLOCK: [2026-01-13 Mon 09:30]--[2026-01-13 Mon 12:00] =>  2:30
   :END:

** DONE Database Migration
   :LOGBOOK:
   CLOCK: [2026-01-10 Fri 10:00]--[2026-01-10 Fri 15:30] =>  5:30
   CLOCK: [2026-01-09 Thu 14:00]--[2026-01-09 Thu 17:00] =>  3:00
   :END:

** IN-PROGRESS Frontend Integration
   :LOGBOOK:
   CLOCK: [2026-01-15 Wed 14:00]--[2026-01-15 Wed 17:30] =>  3:30
   :END:

* Invoice

#+BEGIN: clocktable :scope file :maxlevel 2 :block 2026-01
#+CAPTION: January 2026 — Acme Corp
| Heading                | Time    |       |
|------------------------+---------+-------|
| *Total*                | *22:00* |       |
| Billable Work          | 22:00   |       |
| \_  API Redesign       |         | 10:00 |
| \_  Database Migration |         |  8:30 |
| \_  Frontend Integration|        |  3:30 |
#+END:

  Rate: $150/hr
  Total hours: 22:00
  Invoice amount: $3,300.00
```

---

## Clocking Workflow Tips

### Auto-clock out on done

```elisp
;; Clock out when marking task DONE
(setq org-clock-out-when-done t)
```

### Clock into last task

```elisp
;; Resume the last clock when Emacs starts
(setq org-clock-persist t)
(org-clock-persistence-inuse)
```

### Idle time handling

If you forget to clock out (went to lunch, got distracted):

```elisp
;; After 15 minutes idle, ask what to do
(setq org-clock-idle-time 15)
```

Emacs will ask: "You've been idle for 15 minutes. Clock out at [time]? Subtract idle time? Keep clocking?"

### Clock in from agenda

In the agenda view, put cursor on a task and press `I` to clock in, `O` to clock out.

---

## Effort Estimates

Add estimated time to tasks for planning:

```org
* TODO Dashboard: Activity Feed
  :PROPERTIES:
  :Effort:   4:00
  :END:
```

Set effort with `C-c C-x e`. Now the agenda can show effort vs. actual:

```elisp
;; Show effort in column view
(setq org-columns-default-format
      "%40ITEM %TODO %3PRIORITY %Effort{:} %CLOCKSUM")
```

Press `C-c C-x C-c` in a file to see column view — a spreadsheet-like view showing effort estimates alongside actual clocked time.

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c C-x C-i` | Clock in |
| `C-c C-x C-o` | Clock out |
| `C-c C-x C-q` | Cancel clock |
| `C-c C-x C-j` | Jump to clocked task |
| `C-c C-x C-d` | Display times in buffer |
| `C-c C-x C-r` | Insert clock table report |
| `C-c C-x e` | Set effort estimate |
| `C-c C-x C-c` | Column view (effort vs actual) |
| `C-c C-c` | Update clock table (cursor on #+BEGIN:) |

---

## Exercise: Track Your Time for a Day

1. Pick 3-4 tasks you'll work on today.
2. Clock in (`C-c C-x C-i`) when you start each one.
3. Clock out (`C-c C-x C-o`) when you switch tasks.
4. At end of day, generate a clock table:

```org
#+BEGIN: clocktable :scope file :maxlevel 2 :block today
#+END:
```

5. Press `C-c C-c` on the clocktable line to generate the report.
6. Add effort estimates to tomorrow's tasks and compare planned vs actual at end of day.

> **Nadia's tip:** "Clocking changed my relationship with time. I used to think I spent 6 hours coding. The clock showed 3.5 — the rest was meetings, Slack, and context switching. Now I know exactly where my time goes. It's uncomfortable at first, but incredibly valuable. And for freelancing? My invoices are bulletproof."

---

[← Ch 8](chapter-08-babel.md) | [Ch 10: The Command Center →](chapter-10-agenda-advanced.md)
