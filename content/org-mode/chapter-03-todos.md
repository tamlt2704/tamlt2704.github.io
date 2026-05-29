# Chapter 3: TODOs — Task Management

[prev: Markup](chapter-02-markup.md) | [next: Scheduling](chapter-04-scheduling.md)

Org Mode's TODO system turns your outline into a powerful task manager with states, priorities, tags, and metadata.

## Basic TODO Keywords

```org
* TODO Write project proposal
* DONE Send email to client
```

| Keybinding     | Action                  |
| -------------- | ----------------------- |
| `C-c C-t`      | Cycle TODO state        |
| `S-left/right` | Cycle through states    |
| `M-S-RET`      | Insert new TODO heading |

## Custom TODO Sequences

```org
#+TODO: TODO NEXT WAITING | DONE CANCELLED
```

The `|` separates active states from completed states. Letters in parentheses are fast-access keys:

```org
#+TODO: TODO(t) NEXT(n) WAITING(w@/!) | DONE(d!) CANCELLED(c@)
```

- `!` — log timestamp when entering state
- `@` — prompt for a note when entering state

Global configuration:

```org
#+begin_src elisp
(setq org-todo-keywords
      '((sequence "TODO(t)" "NEXT(n)" "WAITING(w@/!)" "|" "DONE(d!)" "CANCELLED(c@)")))
#+end_src
```

## Priorities

```org
* TODO [#A] Critical bug fix
* TODO [#B] Feature request
* TODO [#C] Nice-to-have improvement
```

| Keybinding  | Action         |
| ----------- | -------------- |
| `C-c ,`     | Set priority   |
| `S-up/down` | Cycle priority |

## Tags

Tags appear at the end of headings:

```org
* TODO Call dentist                                   :health:phone:
* TODO Fix login bug                                 :work:urgent:
```

| Keybinding | Action                       |
| ---------- | ---------------------------- |
| `C-c C-q`  | Set tags                     |
| `C-c C-c`  | Set tags (cursor on heading) |

### Tag Inheritance

Children inherit parent tags:

```org
* Work                                               :work:
** TODO Prepare slides
   ;; inherits :work: tag
```

### Predefined Tags

```org
#+TAGS: @office(o) @home(h) @errands(e)
#+TAGS: work(w) personal(p) urgent(u)
```

## Property Drawers

```org
* TODO Redesign homepage
  :PROPERTIES:
  :Effort:   4:00
  :Assignee: Alice
  :Sprint:   3
  :END:
```

| Keybinding  | Action            |
| ----------- | ----------------- |
| `C-c C-x p` | Set a property    |
| `C-c C-x d` | Delete a property |

## Logging State Changes

```org
* DONE Write documentation
  CLOSED: [2024-03-15 Fri 14:30]
  :LOGBOOK:
  - State "DONE" from "NEXT" [2024-03-15 Fri 14:30]
  - State "NEXT" from "TODO" [2024-03-14 Thu 09:00]
  :END:
```

```org
#+begin_src elisp
(setq org-log-done 'time)
(setq org-log-into-drawer t)
#+end_src
```

## Effort Estimates

```org
* TODO Write unit tests
  :PROPERTIES:
  :Effort:   2:30
  :END:
```

| Keybinding  | Action              |
| ----------- | ------------------- |
| `C-c C-x e` | Set effort estimate |

## Exercises

1. Create a file with custom TODO states:

```org
#+TODO: TODO(t) NEXT(n) WAITING(w@/!) | DONE(d!) CANCELLED(c@)

* Project: Learn Org Mode                            :learning:emacs:
** TODO [#A] Complete exercises
   :PROPERTIES:
   :Effort:   0:30
   :END:
** NEXT [#B] Set up capture templates                :config:
** WAITING [#C] Get feedback from colleague
** DONE [#A] Install latest Emacs
   CLOSED: [2024-03-15 Fri 10:00]
```

2. Cycle TODO states with `C-c C-t`
3. Set priorities with `C-c ,`
4. Add tags with `C-c C-q`
5. Set effort with `C-c C-x e`
