# Learn Emacs Lisp

[next: Basics](chapter-01-basics.md)

Emacs Lisp (Elisp) is the programming language that powers GNU Emacs. Learning it lets you customize every aspect of your editor, automate workflows, and write full packages that others can use.

## Why Learn Emacs Lisp?

- Customize Emacs beyond what configuration options allow
- Write your own commands and keybindings
- Create minor and major modes
- Build and distribute packages on MELPA
- Understand how Emacs works internally

## Chapters

1. [Basics](chapter-01-basics.md) — S-expressions, atoms, evaluation, types
2. [Functions](chapter-02-functions.md) — defun, lambda, higher-order functions, scoping
3. [Variables](chapter-03-variables.md) — setq, let, buffer-local, defcustom
4. [Control Flow](chapter-04-control-flow.md) — conditionals, loops, pattern matching, error handling
5. [Data Structures](chapter-05-data-structures.md) — lists, strings, hash tables, vectors
6. [Buffers and Text](chapter-06-buffers-text.md) — buffer manipulation, point, text properties
7. [Writing Commands](chapter-07-commands.md) — interactive specs, keybindings, minor modes, hooks
8. [Writing Packages](chapter-08-packages.md) — package structure, autoloads, MELPA, testing
9. [Practical Projects](chapter-09-practical.md) — word counter, pomodoro timer, REST client, advice

## How to Use This Guide

Evaluate code as you read. In Emacs:

- `C-x C-e` — evaluate the expression before point
- `M-:` — evaluate an expression in the minibuffer
- `M-x ielm` — open an interactive Elisp REPL

Open a `*scratch*` buffer (it starts in `lisp-interaction-mode`) and experiment freely.
