# Chapter 10: Workflows — Putting It All Together

[prev: Export](chapter-09-export.md) | [next: Overview](chapter-00-overview.md)

This chapter shows how to combine Org Mode features into complete productivity systems.

## GTD (Getting Things Done)

### File Structure

```org
;; ~/org/inbox.org    — Capture everything here
;; ~/org/gtd.org      — Active projects and next actions
;; ~/org/someday.org  — Someday/maybe items
;; ~/org/reference.org — Reference material
;; ~/org/archive.org  — Completed items
```

### GTD Setup

```org
#+begin_src elisp
(setq org-todo-keywords
      '((sequence "TODO(t)" "NEXT(n)" "WAITING(w@/!)" "|" "DONE(d!)" "CANCELLED(c@)")))

(setq org-capture-templates
      '(("i" "Inbox" entry (file "~/org/inbox.org")
         "* %?\n  %U\n  %a")
        ("t" "Todo" entry (file+headline "~/org/gtd.org" "Tasks")
         "* TODO %?\n  %U")))

(setq org-refile-targets '(("~/org/gtd.org" :maxlevel . 2)
                           ("~/org/someday.org" :level . 1)
                           ("~/org/reference.org" :level . 1)))

(setq org-agenda-custom-commands
      '(("g" "GTD View"
         ((agenda "" ((org-agenda-span 1)))
          (todo "NEXT" ((org-agenda-overriding-header "Next Actions")))
          (todo "WAITING" ((org-agenda-overriding-header "Waiting")))
          (tags-todo "+inbox" ((org-agenda-overriding-header "Inbox (process me!)")))))))
#+end_src
```

### GTD Workflow

1. **Collect**: `C-c c i` — capture to inbox
2. **Process**: Open inbox, for each item:
   - 2-minute rule: do it now
   - Refile to project (`C-c C-w`)
   - Schedule/deadline it
   - Move to someday
   - Delete
3. **Organize**: Projects have a NEXT action
4. **Review**: Weekly — `C-c a g`
5. **Do**: Work from NEXT actions list

### gtd.org Example

```org
#+TODO: TODO(t) NEXT(n) WAITING(w@/!) | DONE(d!) CANCELLED(c@)

* Projects
** Write blog post series                            :writing:
*** DONE Outline topics
*** NEXT Write first draft
*** TODO Edit and publish
** Home renovation                                   :home:
*** WAITING Get quote from contractor
*** TODO Choose paint colors

* Single Actions
** NEXT Call dentist for appointment                 :health:phone:
** NEXT Review insurance policy                     :finance:
```

## Zettelkasten with org-roam

```org
#+begin_src elisp
(use-package org-roam
  :custom
  (org-roam-directory "~/org/roam/")
  :bind (("C-c n f" . org-roam-node-find)
         ("C-c n i" . org-roam-node-insert)
         ("C-c n l" . org-roam-buffer-toggle))
  :config
  (org-roam-db-autosync-mode))
#+end_src
```

Each note is a single Org file with links to other notes:

```org
:PROPERTIES:
:ID: 20240320T143000
:END:
#+title: Spaced Repetition

Spaced repetition is a learning technique that reviews
material at increasing intervals.

Related: [[id:20240319T100000][Memory and Learning]]

* Key Principles
- Test yourself rather than re-read
- Space reviews over time
- Focus on items you find difficult
```

| Keybinding | Action                      |
| ---------- | --------------------------- |
| `C-c n f`  | Find or create a note       |
| `C-c n i`  | Insert link to another note |
| `C-c n l`  | Show backlinks              |

## Journaling

### org-journal

```org
#+begin_src elisp
(use-package org-journal
  :custom
  (org-journal-dir "~/org/journal/")
  (org-journal-date-format "%A, %d %B %Y")
  (org-journal-file-type 'weekly))
#+end_src
```

### Capture-based journal

```org
#+begin_src elisp
("j" "Journal" entry (file+datetree "~/org/journal.org")
 "* %U %?\n  %i")
#+end_src
```

Produces:

```org
* 2024
** 2024-03 March
*** 2024-03-20 Wednesday
**** [2024-03-20 Wed 14:30] Had a productive meeting
     Discussed project timeline and next steps.
```

## Project Management

```org
* Project: Website Redesign                          :project:web:
  :PROPERTIES:
  :CATEGORY: WebRedesign
  :END:

** Goals
   - Modern responsive design
   - Improve page load time by 50%
   - Accessibility compliance

** NEXT [#A] Create wireframes
   SCHEDULED: <2024-03-20 Wed>
   :PROPERTIES:
   :Effort:   4:00
   :Assignee: Alice
   :END:

** TODO [#B] Set up CI/CD pipeline
   :PROPERTIES:
   :Effort:   2:00
   :Assignee: Bob
   :END:

** WAITING [#B] Get brand assets from design team

** Progress
   - [X] Requirements gathered
   - [X] Tech stack chosen
   - [ ] Wireframes complete
   - [ ] Development sprint 1
   - [ ] Testing
   - [ ] Launch
```

## Meeting Notes

```org
#+begin_src elisp
("m" "Meeting" entry (file+headline "~/org/meetings.org" "Meetings")
 "* %^{Meeting title} :meeting:\n  %U\n  Attendees: %^{Attendees}\n\n** Agenda\n   %?\n\n** Notes\n\n** Action Items\n")
#+end_src
```

```org
* Sprint Planning :meeting:
  [2024-03-20 Wed 10:00]
  Attendees: Alice, Bob, Charlie

** Agenda
   - Review last sprint
   - Plan next sprint
   - Discuss blockers

** Notes
   - Completed 8 of 10 story points
   - New requirement from stakeholder

** Action Items
*** TODO [#A] Alice: Update backlog by Friday
*** TODO [#B] Bob: Fix deployment script
*** TODO Charlie: Schedule stakeholder meeting
```

## Writing a Book

```org
#+TITLE: My Book
#+AUTHOR: Author Name
#+LATEX_CLASS: book

* Part I: Foundations
** Chapter 1: Introduction
*** The Problem
*** Our Approach
** Chapter 2: Background
*** History
*** Current State

* Part II: Implementation
** Chapter 3: Design
** Chapter 4: Building

* Appendix
** Glossary
** Bibliography
```

Tangle code examples, export to PDF, track progress with TODO states on chapters.

## Personal Wiki

Use a directory of Org files with heavy interlinking:

```org
;; ~/wiki/index.org
* Personal Wiki

** Areas
- [[file:programming.org][Programming]]
- [[file:cooking.org][Cooking]]
- [[file:fitness.org][Fitness]]

** Recent
- [[file:emacs-tips.org][Emacs Tips]]
- [[file:book-notes.org][Book Notes]]
```

## Spaced Repetition (org-drill)

```org
#+begin_src elisp
(use-package org-drill)
#+end_src
```

```org
* Vocabulary :drill:

** Word                                              :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: twosided
   :END:

*** Front
    What is the capital of France?

*** Back
    Paris

** Cloze deletion                                    :drill:

   The =org-agenda= is opened with [C-c a].
```

Run `M-x org-drill` to start a review session.

## Exercises

1. Set up a minimal GTD system with inbox, gtd, and someday files
2. Create a weekly review custom agenda command
3. Start a journal using capture templates with datetree
4. Create a project with NEXT actions, deadlines, and effort estimates
5. Build a meeting notes template and use it for your next meeting
