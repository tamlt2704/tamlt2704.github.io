# Emacs Lisp — Bending Your Editor to Your Will

A narrative-driven course on Emacs Lisp (Elisp). You're a developer who just switched to Emacs and keeps thinking "I wish it did X." Every chapter, you'll build a real customization — from simple keybindings to full minor modes. By the end, Emacs does exactly what you want.

## Episodes

| # | Title | The Wish | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, *scratch* buffer, eval basics, the cast |
| 01 | [Hello Elisp](chapter-01-hello.md) | "I want a greeting when Emacs starts" | message, defun, init.el, evaluation |
| 02 | [Variables and State](chapter-02-variables.md) | "I want to toggle my preferred font size" | setq, let, defvar, defcustom, buffer-local |
| 03 | [Conditionals and Logic](chapter-03-conditionals.md) | "Different behavior for different file types" | if, cond, when, unless, and/or |
| 04 | [Lists Everywhere](chapter-04-lists.md) | "I want a recent-projects list" | cons, car, cdr, list manipulation, quote |
| 05 | [Interactive Commands](chapter-05-interactive.md) | "I want my own M-x commands" | interactive, prefix args, completing-read |
| 06 | [Buffers and Windows](chapter-06-buffers.md) | "Auto-arrange my workspace on startup" | buffer API, window management, save-excursion |
| 07 | [Hooks and Advice](chapter-07-hooks.md) | "Run my formatter on every save" | add-hook, advice-add, before/after/around |
| 08 | [Keymaps](chapter-08-keymaps.md) | "My own prefix key with custom bindings" | define-key, keymap creation, hydra-style menus |
| 09 | [Text Manipulation](chapter-09-text.md) | "Bulk-rename variables in a region" | point, mark, region, replace-regexp-in-string |
| 10 | [Regular Expressions](chapter-10-regex.md) | "Highlight TODO/FIXME in my own way" | Elisp regex syntax, re-search-forward, overlays |
| 11 | [Minor Modes](chapter-11-minor-modes.md) | "A toggleable writing mode" | define-minor-mode, lighter, keymap, hooks |
| 12 | [Major Modes](chapter-12-major-modes.md) | "Syntax highlighting for my custom DSL" | define-derived-mode, font-lock, syntax tables |
| 13 | [Packages](chapter-13-packages.md) | "Share my mode with the world" | package.el structure, MELPA, autoloads, dependencies |
| 14 | [Async and Processes](chapter-14-async.md) | "Run builds without freezing Emacs" | start-process, sentinels, async.el, comint |

## Prerequisites

- Emacs 29+ (for built-in features used in examples)
- Willingness to live in `C-h f` and `C-h v`

## Philosophy

Every Elisp concept is introduced because you want Emacs to do something it doesn't do yet. You'll feel the friction first, then write the code that removes it. The annoyance comes first. The customization follows.
