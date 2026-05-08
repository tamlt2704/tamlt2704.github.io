# Chapter 12: Major Modes

[← Chapter 11: Minor Modes](chapter-11-minor-modes.md) | [Chapter 13: Packages →](chapter-13-packages.md)

---

## The Wish

"I have a custom DSL at work — config files with their own syntax. I want proper syntax highlighting, indentation, and comment support. A real major mode."

## What Is a Major Mode?

Every buffer has exactly one major mode that defines:
- Syntax highlighting (font-lock)
- Indentation rules
- Comment style
- Keybindings
- Which minor modes activate

Most modes derive from a parent: `prog-mode` (code), `text-mode` (prose), or `special-mode` (non-editable).

## define-derived-mode

```elisp
(define-derived-mode my-mode PARENT-MODE "ModeName"
  "DOCSTRING"
  BODY...)
```

Minimal example:

```elisp
(define-derived-mode my-conf-mode prog-mode "MyConf"
  "Major mode for editing my config DSL."
  ;; Body runs when mode activates
  (setq-local comment-start "# ")
  (setq-local comment-end ""))
```

## A Real DSL: Task Files

Let's say your DSL looks like this:

```
# Project tasks
@project "website-redesign"
@deadline 2024-03-01

task "Fix header" :priority high :assignee alice
  subtask "Update CSS"
  subtask "Test mobile"

task "Add search" :priority medium :assignee bob
  depends "Fix header"
```

## Font-Lock: Syntax Highlighting

Font-lock rules map regex patterns to faces:

```elisp
(defvar my-task-font-lock-keywords
  `(;; Comments
    ("^#.*$" . font-lock-comment-face)

    ;; Directives: @keyword
    ("^@\\(\\w+\\)" (1 font-lock-keyword-face))

    ;; Task keyword
    ("^\\(task\\|subtask\\|depends\\)\\b" (1 font-lock-function-name-face))

    ;; Strings
    ("\"[^\"]*\"" . font-lock-string-face)

    ;; Properties: :keyword
    (":\\(\\w+\\)" (1 font-lock-type-face))

    ;; Values after properties
    (":\\w+\\s-+\\(\\w+\\)" (1 font-lock-constant-face)))
  "Font-lock keywords for my-task-mode.")
```

## Syntax Tables

The syntax table tells Emacs about character roles — what's a comment delimiter, what's a string quote, what's a word character:

```elisp
(defvar my-task-mode-syntax-table
  (let ((table (make-syntax-table)))
    ;; # starts a comment that ends at newline
    (modify-syntax-entry ?# "<" table)   ; Comment start
    (modify-syntax-entry ?\n ">" table)  ; Comment end
    ;; " is a string delimiter
    (modify-syntax-entry ?\" "\"" table)
    ;; @ is a word constituent (part of keywords)
    (modify-syntax-entry ?@ "w" table)
    ;; : is punctuation
    (modify-syntax-entry ?: "." table)
    table)
  "Syntax table for my-task-mode.")
```

## Indentation

```elisp
(defun my-task-indent-line ()
  "Indent current line for task files."
  (let ((indent 0)
        (current-line (thing-at-point 'line t)))
    (save-excursion
      (beginning-of-line)
      (cond
       ;; subtask/depends lines indent under task
       ((looking-at "\\s-*\\(subtask\\|depends\\)")
        (setq indent 2))
       ;; task and directives at column 0
       ((looking-at "\\s-*\\(task\\|@\\|#\\)")
        (setq indent 0))
       ;; Continuation: match previous line
       (t
        (forward-line -1)
        (setq indent (current-indentation)))))
    (indent-line-to indent)))
```

## Putting It All Together

```elisp
(define-derived-mode my-task-mode prog-mode "Tasks"
  "Major mode for editing task DSL files."
  ;; Syntax highlighting
  (setq font-lock-defaults '(my-task-font-lock-keywords))

  ;; Comments
  (setq-local comment-start "# ")
  (setq-local comment-end "")

  ;; Indentation
  (setq-local indent-line-function #'my-task-indent-line)
  (setq-local tab-width 2)

  ;; Use our syntax table
  (set-syntax-table my-task-mode-syntax-table))

;; Auto-activate for .task files
(add-to-list 'auto-mode-alist '("\\.task\\'" . my-task-mode))
```

## Mode-Specific Commands

```elisp
;; Add commands to the mode's keymap
(define-key my-task-mode-map (kbd "C-c C-n") #'my-task-new)
(define-key my-task-mode-map (kbd "C-c C-d") #'my-task-mark-done)

(defun my-task-new ()
  "Insert a new task template."
  (interactive)
  (end-of-line)
  (insert "\n\ntask \"\" :priority medium :assignee ")
  (search-backward "\"\"")
  (forward-char 1))

(defun my-task-mark-done ()
  "Mark the task at point as done."
  (interactive)
  (save-excursion
    (beginning-of-line)
    (when (looking-at "\\(\\s-*task\\)")
      (end-of-line)
      (insert " :status done")
      (message "Task marked done"))))
```

## Imenu: Code Navigation

Imenu provides a jump-to-definition menu. Add support for your mode:

```elisp
(defvar my-task-imenu-expression
  '(("Tasks" "^task\\s-+\"\\([^\"]+\\)\"" 1)
    ("Directives" "^@\\(\\w+\\)" 1))
  "Imenu patterns for task files.")

;; Add to mode setup
(define-derived-mode my-task-mode prog-mode "Tasks"
  "Major mode for editing task DSL files."
  (setq font-lock-defaults '(my-task-font-lock-keywords))
  (setq-local comment-start "# ")
  (setq-local comment-end "")
  (setq-local indent-line-function #'my-task-indent-line)
  (setq-local imenu-generic-expression my-task-imenu-expression)
  (set-syntax-table my-task-mode-syntax-table))
```

Now `M-x imenu` (or `C-c C-j` in many configs) lets you jump to any task by name.

## Exercises

1. Add a font-lock rule that highlights `@deadline` values in red when the date is in the past.
2. Create a `my-task-list-all` command that collects all tasks into a summary buffer.
3. Add `completion-at-point-functions` support so `:priority` auto-completes to `high`, `medium`, `low`.

## What You Learned

- **`define-derived-mode`** — create a major mode inheriting from a parent
- **Font-lock keywords** — regex-to-face mappings for highlighting
- **Syntax tables** — character classification (comments, strings, words)
- **`indent-line-function`** — custom indentation logic
- **`auto-mode-alist`** — auto-activate mode for file extensions
- **Imenu** — jump-to-definition support

Your mode works locally. But your team wants it too. Time to package it up and share it with the world.

---

[← Chapter 11: Minor Modes](chapter-11-minor-modes.md) | [Chapter 13: Packages →](chapter-13-packages.md)
