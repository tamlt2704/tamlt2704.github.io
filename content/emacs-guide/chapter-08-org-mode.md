# Chapter 8: Org Mode

[prev: Programming](chapter-07-programming.md) | [next: Evil Mode](chapter-09-evil-mode.md)

Org Mode is Emacs's killer feature — a plain-text system for notes, tasks, planning, authoring, and literate programming.

## Headings

```org
* Top level heading
** Second level
*** Third level
```

| Key            | Action                      |
| -------------- | --------------------------- |
| `TAB`          | Fold/unfold heading         |
| `S-TAB`        | Cycle all headings globally |
| `M-RET`        | Insert new heading          |
| `M-up/down`    | Move heading up/down        |
| `M-left/right` | Promote/demote heading      |

## TODO Items

```org
* TODO Write chapter on Org Mode
* DONE Install Emacs
```

| Key            | Action           |
| -------------- | ---------------- |
| `C-c C-t`      | Cycle TODO state |
| `S-left/right` | Cycle TODO state |
| `C-c C-c`      | Toggle checkbox  |

Custom TODO sequences:

```elisp
(setq org-todo-keywords
      '((sequence "TODO" "IN-PROGRESS" "WAITING" "|" "DONE" "CANCELLED")))
```

## Scheduling and Deadlines

| Key       | Action           |
| --------- | ---------------- |
| `C-c C-s` | Schedule a task  |
| `C-c C-d` | Set deadline     |
| `C-c .`   | Insert timestamp |

## Tags

```org
* TODO Buy groceries :errands:personal:
```

Set tags with `C-c C-q`. Filter by tag in agenda with `/`.

## Tables

Org creates and formats tables automatically:

```org
| Name  | Age | City   |
|-------+-----+--------|
| Alice |  30 | London |
| Bob   |  25 | Paris  |
```

| Key            | Action                     |
| -------------- | -------------------------- |
| `TAB`          | Move to next cell, realign |
| `S-TAB`        | Move to previous cell      |
| `M-left/right` | Move column                |
| `M-up/down`    | Move row                   |

## Code Blocks (Babel)

Execute code inside Org documents:

```org
#+begin_src python :results output
print("Hello from Python!")
#+end_src
```

Press `C-c C-c` inside the block to execute. Results appear below.

Supported languages: Python, Elisp, Shell, R, JavaScript, SQL, and many more.

```elisp
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (shell . t)
   (emacs-lisp . t)))
```

## Export

| Key       | Action                 |
| --------- | ---------------------- |
| `C-c C-e` | Open export dispatcher |

Export targets:

- `h h` — HTML
- `l l` — LaTeX/PDF
- `m` — Markdown
- `t` — Plain text
- Beamer for slides

## Agenda

The agenda aggregates TODOs and scheduled items across all your Org files:

```elisp
(setq org-agenda-files '("~/org/"))
(global-set-key (kbd "C-c a") 'org-agenda)
```

| Key       | Action        |
| --------- | ------------- |
| `C-c a a` | Weekly agenda |
| `C-c a t` | All TODOs     |

## Capture Templates

Quickly capture ideas without leaving your current work:

```elisp
(global-set-key (kbd "C-c c") 'org-capture)
(setq org-capture-templates
      '(("t" "Task" entry (file "~/org/inbox.org")
         "* TODO %?\n  %U")
        ("n" "Note" entry (file "~/org/notes.org")
         "* %?\n  %U\n  %a")))
```

`C-c c t` captures a task, `C-c c n` captures a note. `C-c C-c` saves, `C-c C-k` cancels.

## GTD Workflow

A simple Getting Things Done setup:

1. **Capture** everything to inbox (`C-c c`)
2. **Clarify** — refile items from inbox to projects (`C-c C-w`)
3. **Organize** — tag, schedule, set deadlines
4. **Review** — weekly agenda view (`C-c a a`)
5. **Engage** — work from agenda, mark DONE (`C-c C-t`)

```elisp
(setq org-refile-targets '((org-agenda-files :maxlevel . 3)))
```
