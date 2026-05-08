# Chapter 5: Interactive Commands

[← Chapter 4: Lists](chapter-04-lists.md) | [Chapter 6: Buffers and Windows →](chapter-06-buffers.md)

---

## The Wish

"I want my own M-x commands — real commands I can bind to keys, that prompt me for input, and show up in the command palette."

## What Makes a Command?

A regular function can only be called from Elisp. A **command** can be called interactively — via `M-x`, a keybinding, or a menu. The difference is one word: `interactive`.

```elisp
;; This is just a function — can't M-x it
(defun my-greet (name)
  (message "Hello, %s!" name))

;; This is a command — shows up in M-x
(defun my-greet (name)
  "Greet NAME in the echo area."
  (interactive "sYour name: ")
  (message "Hello, %s!" name))
```

The `interactive` spec tells Emacs how to get arguments when called interactively.

## Interactive Codes

The string after `interactive` contains codes that specify argument types:

```elisp
;; Common interactive codes:
;; "s" — prompt for a string
;; "n" — prompt for a number
;; "f" — prompt for a file (with completion)
;; "b" — prompt for a buffer name
;; "r" — pass region start and end (two args)
;; "P" — raw prefix argument (C-u)
;; "p" — prefix argument as number (default 1)
```

```elisp
(defun my-insert-divider (char count)
  "Insert COUNT copies of CHAR as a divider line."
  (interactive "cDivider character: \nnHow many: ")
  (insert (make-string count char) "\n"))
```

Multiple arguments are separated by `\n` in the interactive string.

## completing-read: The Power Prompt

`completing-read` gives users a searchable list of choices:

```elisp
(defun my-pick-color ()
  "Choose a color and insert it."
  (interactive)
  (let ((color (completing-read
                "Color: "
                '("red" "green" "blue" "orange" "purple"))))
    (insert color)))
```

With any completion framework (vertico, ivy, helm), this becomes a fuzzy-searchable menu.

```elisp
;; completing-read with alist for display vs value
(defun my-open-bookmark ()
  "Open a bookmarked file."
  (interactive)
  (let* ((bookmarks '(("Init file" . "~/.emacs.d/init.el")
                      ("Notes"     . "~/notes/index.org")
                      ("Scratch"   . "~/scratch.md")))
         (choice (completing-read "Bookmark: " bookmarks))
         (path (cdr (assoc choice bookmarks))))
    (find-file path)))
```

## Prefix Arguments: C-u

Every command receives an optional prefix argument via `C-u`:

```elisp
(defun my-insert-timestamp (universal)
  "Insert date. With C-u, include time."
  (interactive "P")
  (insert (format-time-string
           (if universal "%Y-%m-%d %H:%M:%S" "%Y-%m-%d"))))
```

- `M-x my-insert-timestamp` → `2024-01-15`
- `C-u M-x my-insert-timestamp` → `2024-01-15 14:30:22`

Numeric prefix with `"p"`:

```elisp
(defun my-insert-lines (n)
  "Insert N blank lines."
  (interactive "p")
  (dotimes (_ n)
    (insert "\n")))
;; C-u 5 M-x my-insert-lines → inserts 5 blank lines
```

## interactive with a List Form

For complex argument logic, use a list instead of a string:

```elisp
(defun my-rename-file (old-name new-name)
  "Rename OLD-NAME to NEW-NAME with smart defaults."
  (interactive
   (let* ((current (buffer-file-name))
          (dir (file-name-directory current))
          (old (file-name-nondirectory current))
          (new (read-string "New name: " old)))
     (list current (expand-file-name new dir))))
  (rename-file old-name new-name)
  (set-visited-file-name new-name t t))
```

The list form lets you compute arguments with arbitrary Elisp before passing them to the function body.

## Practical: Project Switcher Command

Building on Chapter 4's project list:

```elisp
(defvar my-projects
  '(("blog"    . "~/code/blog")
    ("api"     . "~/code/api")
    ("dotfiles" . "~/dotfiles")
    ("notes"   . "~/notes"))
  "Alist of project names to directories.")

(defun my-switch-project (name)
  "Switch to project NAME. With C-u, open in dired."
  (interactive
   (list (completing-read "Project: "
                          (mapcar #'car my-projects))))
  (let ((dir (cdr (assoc name my-projects))))
    (if current-prefix-arg
        (dired dir)
      (project-switch-project dir))))

(defun my-add-project (dir)
  "Add DIR to the projects list."
  (interactive "DProject directory: ")
  (let ((name (read-string "Project name: "
                           (file-name-nondirectory
                            (directory-file-name dir)))))
    (add-to-list 'my-projects (cons name dir))
    (message "Added project: %s → %s" name dir)))
```

## read-* Family: Other Input Functions

```elisp
(read-string "Name: ")              ; Free text input
(read-number "Count: " 5)           ; Number with default
(read-directory-name "Dir: ")       ; Directory with completion
(read-file-name "File: ")           ; File with completion
(yes-or-no-p "Are you sure? ")     ; Yes/no (full word)
(y-or-n-p "Continue? ")            ; y/n (single key)
```

## Exercises

1. Write a command `my-insert-boilerplate` that uses `completing-read` to pick from a list of code templates, then inserts the chosen template.

2. Create a command that takes a numeric prefix arg and inserts that many copies of the current line.

3. Write `my-find-in-project` that prompts for a project (completing-read), then prompts for a file within that project.

## What You Learned

- **`interactive`** — turns a function into an M-x command
- **Interactive codes** — `"s"`, `"n"`, `"f"`, `"b"`, `"r"`, `"P"`, `"p"`
- **`completing-read`** — searchable selection from a list
- **Prefix arguments** — `C-u` for toggling behavior, `C-u N` for counts
- **List form** — compute arguments dynamically with `(interactive (list ...))`
- **`read-*` functions** — various input prompts

Your commands work, but they operate on the current buffer. What if you want to manipulate multiple buffers and windows? Time to learn the buffer API.

---

[← Chapter 4: Lists](chapter-04-lists.md) | [Chapter 6: Buffers and Windows →](chapter-06-buffers.md)
