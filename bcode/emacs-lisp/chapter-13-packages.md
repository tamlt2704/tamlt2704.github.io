# Chapter 13: Packages

[← Chapter 12: Major Modes](chapter-12-major-modes.md) | [Chapter 14: Async Processes →](chapter-14-async.md)

---

## The Wish

"I want to share my task-mode with the world — publish it so anyone can `M-x package-install` it. A proper Emacs package on MELPA."

## Package Structure

An Emacs package is just an `.el` file (or directory) with specific header comments:

```
my-task-mode/
├── my-task-mode.el        ; Main file
├── README.md              ; Documentation
├── LICENSE                ; Required for MELPA
└── .github/
    └── workflows/
        └── test.yml       ; CI (optional but recommended)
```

## The Package Header

Every package needs a header that `package.el` can parse:

```elisp
;;; my-task-mode.el --- Major mode for task DSL files -*- lexical-binding: t; -*-

;; Copyright (C) 2024 Your Name

;; Author: Your Name <you@example.com>
;; Version: 0.1.0
;; Package-Requires: ((emacs "29.1"))
;; Keywords: languages, tools
;; URL: https://github.com/you/my-task-mode

;; This file is not part of GNU Emacs.

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;;; Commentary:

;; A major mode for editing .task files using the Task DSL.
;; Features:
;; - Syntax highlighting for tasks, directives, and properties
;; - Indentation support
;; - Imenu integration
;; - Commands for creating and managing tasks

;;; Code:
```

### Required Headers

| Header | Purpose |
|---|---|
| `;;; file.el ---` | First line: file, description, lexical-binding |
| `Author:` | Who wrote it |
| `Version:` | Semantic version |
| `Package-Requires:` | Dependencies as alist |
| `Keywords:` | Searchable categories |
| `URL:` | Repository link |
| `;;; Commentary:` | User-facing documentation |
| `;;; Code:` | Start of actual code |

## The Package Footer

Every package file must end with:

```elisp
(provide 'my-task-mode)
;;; my-task-mode.el ends here
```

`provide` registers the feature so `require` can find it.

## Autoloads

Autoloads let Emacs know about your commands without loading the entire file:

```elisp
;;;###autoload
(defun my-task-new-file ()
  "Create a new task file."
  (interactive)
  ...)

;;;###autoload
(define-derived-mode my-task-mode prog-mode "Tasks"
  ...)

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.task\\'" . my-task-mode))
```

The `;;;###autoload` cookie tells the package system to make these available immediately, loading the full file only when actually called.

## Dependencies

Declare dependencies in `Package-Requires`:

```elisp
;; Package-Requires: ((emacs "29.1") (seq "2.20"))
```

Only list packages your code actually `require`s. Emacs built-in libraries (like `seq` in Emacs 25+) don't need listing unless you need a minimum version.

```elisp
;;; Code:

(require 'seq)       ; Needed at runtime
(require 'cl-lib)    ; Common Lisp compatibility

;; eval-when-compile: only needed during byte-compilation
(eval-when-compile
  (require 'subr-x))  ; string-trim, etc.
```

## Full Package Example

```elisp
;;; my-task-mode.el --- Major mode for task DSL files -*- lexical-binding: t; -*-

;; Author: Your Name <you@example.com>
;; Version: 0.1.0
;; Package-Requires: ((emacs "29.1"))
;; Keywords: languages, tools
;; URL: https://github.com/you/my-task-mode

;;; Commentary:

;; Edit .task files with syntax highlighting, indentation, and task commands.
;; See README.md for the DSL specification.

;;; Code:

(defgroup my-task nil
  "Settings for my-task-mode."
  :group 'languages
  :prefix "my-task-")

(defcustom my-task-default-priority "medium"
  "Default priority for new tasks."
  :type '(choice (const "high") (const "medium") (const "low"))
  :group 'my-task)

(defvar my-task-font-lock-keywords
  '(("^#.*$" . font-lock-comment-face)
    ("^@\\(\\w+\\)" (1 font-lock-keyword-face))
    ("^\\(task\\|subtask\\|depends\\)\\b" (1 font-lock-function-name-face))
    ("\"[^\"]*\"" . font-lock-string-face)
    (":\\(\\w+\\)" (1 font-lock-type-face)))
  "Font-lock keywords for `my-task-mode'.")

(defvar my-task-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-n") #'my-task-new)
    map)
  "Keymap for `my-task-mode'.")

;;;###autoload
(define-derived-mode my-task-mode prog-mode "Tasks"
  "Major mode for editing task DSL files."
  (setq font-lock-defaults '(my-task-font-lock-keywords))
  (setq-local comment-start "# ")
  (setq-local comment-end ""))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.task\\'" . my-task-mode))

(defun my-task-new ()
  "Insert a new task."
  (interactive)
  (insert (format "\ntask \"\" :priority %s :assignee "
                  my-task-default-priority))
  (search-backward "\"\"")
  (forward-char 1))

(provide 'my-task-mode)
;;; my-task-mode.el ends here
```

## Publishing to MELPA

1. **Push to GitHub** — public repo with LICENSE file

2. **Create a MELPA recipe** — fork [melpa/melpa](https://github.com/melpa/melpa), add:

```elisp
;; recipes/my-task-mode
(my-task-mode :fetcher github :repo "you/my-task-mode")
```

3. **Submit a PR** — MELPA maintainers review your package

4. **Users install it:**

```elisp
;; In their init.el
(use-package my-task-mode
  :ensure t
  :mode "\\.task\\'")
```

## Testing Your Package Locally

```elisp
;; Install from local directory (no MELPA needed)
(use-package my-task-mode
  :load-path "~/code/my-task-mode")

;; Or add to load-path manually
(add-to-list 'load-path "~/code/my-task-mode")
(require 'my-task-mode)
```

## Byte Compilation

Byte-compile to catch warnings and improve speed:

```bash
emacs --batch -f batch-byte-compile my-task-mode.el
```

Fix all warnings before publishing — MELPA runs this check.

## Exercises

1. Add a `defcustom` for configurable faces (let users pick their own highlight colors).
2. Write a multi-file package: split font-lock rules into `my-task-faces.el`.
3. Add an `;;;###autoload` for a command that creates a new `.task` file from a template.

## What You Learned

- **Package headers** — required metadata for `package.el`
- **`provide`** — register your feature
- **`;;;###autoload`** — lazy-load entry points
- **`defgroup` / `defcustom`** — user-configurable settings
- **MELPA submission** — recipe format and process
- **Byte compilation** — catch errors, improve performance

Your package is published. But one thing still bothers you: running builds, linters, and tests freezes Emacs while they execute. Let's fix that with async processes.

---

[← Chapter 12: Major Modes](chapter-12-major-modes.md) | [Chapter 14: Async Processes →](chapter-14-async.md)
