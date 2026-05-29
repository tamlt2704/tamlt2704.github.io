# Chapter 4: Scheduling — Time Management

[prev: TODOs](chapter-03-todos.md) | [next: Agenda](chapter-05-agenda.md)

Org Mode integrates timestamps, deadlines, scheduling, and time clocking into your task system.

## Timestamps

### Active Timestamps (appear in agenda)

```org
* Meeting with team
  <2024-03-20 Wed 14:00>
```

### Inactive Timestamps (just records)

```org
* Notes from call
  [2024-03-18 Mon 10:30]
```

| Keybinding     | Action                     |
| -------------- | -------------------------- |
| `C-c .`        | Insert active timestamp    |
| `C-c !`        | Insert inactive timestamp  |
| `S-up/down`    | Adjust date/time component |
| `S-left/right` | Move date by one day       |

Date picker shortcuts: `+3` (3 days), `fri` (next Friday), `+2w` (2 weeks).

## Deadlines and Scheduling

### DEADLINE — must be finished by this date

```org
* TODO Submit tax return
  DEADLINE: <2024-04-15 Mon>
```

| Keybinding    | Action          |
| ------------- | --------------- |
| `C-c C-d`     | Set deadline    |
| `C-u C-c C-d` | Remove deadline |

### SCHEDULED — start working on this date

```org
* TODO Write chapter 5
  SCHEDULED: <2024-03-18 Mon>
```

| Keybinding    | Action                |
| ------------- | --------------------- |
| `C-c C-s`     | Set scheduled date    |
| `C-u C-c C-s` | Remove scheduled date |

### Combined

```org
* TODO Prepare presentation
  SCHEDULED: <2024-03-18 Mon> DEADLINE: <2024-03-22 Fri>
```

## Repeating Tasks

```org
* TODO Weekly review
  SCHEDULED: <2024-03-22 Fri +1w>

* TODO Pay rent
  DEADLINE: <2024-04-01 Mon +1m>
```

### Repeater Types

| Repeater | Meaning                             |
| -------- | ----------------------------------- |
| `+1w`    | Shift from original date            |
| `.+1w`   | Shift from today (when marked done) |
| `++1w`   | Shift to next future occurrence     |

When you mark a repeating task DONE, it resets to TODO and shifts the date.

## Time Ranges

```org
* Meeting
  <2024-03-20 Wed 14:00-15:30>

* Conference
  <2024-06-15 Sat>--<2024-06-17 Mon>
```

## Clocking Time

| Keybinding    | Action               |
| ------------- | -------------------- |
| `C-c C-x C-i` | Clock in             |
| `C-c C-x C-o` | Clock out            |
| `C-c C-x C-q` | Cancel clock         |
| `C-c C-x C-j` | Jump to clocked task |
| `C-c C-x C-d` | Display clocked time |

```org
* TODO Write documentation
  :LOGBOOK:
  CLOCK: [2024-03-18 Mon 09:15]--[2024-03-18 Mon 10:45] =>  1:30
  CLOCK: [2024-03-18 Mon 14:00]--[2024-03-18 Mon 15:30] =>  1:30
  :END:
```

### Clock Reports

```org
#+BEGIN: clocktable :scope subtree :maxlevel 3
| Heading             | Time   |
|---------------------+--------|
| *Total*             | *3:00* |
| Write documentation | 3:00   |
#+END:
```

| Keybinding    | Action                     |
| ------------- | -------------------------- |
| `C-c C-x C-r` | Insert/update clock report |
| `C-c C-c`     | Update dynamic block       |

## Diary-Style Dates

```org
* Third Monday of every month
  <%%(diary-float t 1 3)>

* Alice's Birthday
  <%%(org-anniversary 1990 6 15)> Alice is %d years old

* Weekday standup
  <%%(memq (calendar-day-of-week date) '(1 2 3 4 5))>
```

## Exercises

1. Create tasks with deadlines and scheduled dates
2. Clock in (`C-c C-x C-i`), work, clock out (`C-c C-x C-o`)
3. Insert a clock report with `C-c C-x C-r`
4. Create a repeating task and mark it DONE to see the date shift
5. Try all three repeater types (`+1w`, `.+1w`, `++1w`)
