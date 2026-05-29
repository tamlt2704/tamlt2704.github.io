# Chapter 7: Writing Commands

[prev: Buffers and Text](chapter-06-buffers-text.md) | [next: Writing Packages](chapter-08-packages.md)

## Interactive Spec Codes

The `(interactive "...")` string tells Emacs how to get arguments when called via `M-x` or a keybinding:

```elisp
(defun greet-user (name)
  "Greet NAME."
  (interactive "sYour name: ")
  (message "Hello, %s!" name))
```

Common spec codes:

| Code | Meaning                                   |
| ---- | ----------------------------------------- |
| `s`  | String (prompt in minibuffer)             |
| `n`  | Number (prompt in minibuffer)             |
| `r`  | Region (passes start and end as two args) |
| `p`  | Prefix argument as number (C-u 4 = 4)     |
| `f`  | Existing file name                        |
| `b`  | Existing buffer name                      |

### Multiple arguments

Separate specs with `\n`:

```elisp
(defun copy-to-buffer (text buffer-name)
  "Insert TEXT into BUFFER-NAME."
  (interactive "sText: \nbBuffer: ")
  (with-current-buffer buffer-name
    (insert text)))
```

### Using a list form

For complex argument logic, use a list instead of a string:

```elisp
(defun insert-date (prefix)
  "Insert date. With PREFIX arg, include time."
  (interactive (list current-prefix-arg))
  (insert (format-time-string
           (if prefix "%Y-%m-%d %H:%M" "%Y-%m-%d"))))
```

## Prefix Arguments

`C-u` sets the prefix argument. Access it in your commands:

```elisp
(defun repeat-message (n)
  "Print a message N times (default 1)."
  (interactive "p")
  (dotimes (_ n)
    (message "Hello!")))
;; C-u 5 M-x repeat-message => prints 5 times
```

`"p"` gives 1 by default, 4 with bare `C-u`, or the number typed after `C-u`.

`"P"` gives the raw prefix (nil if not provided):

```elisp
(defun maybe-shout (prefix)
  "Shout if PREFIX is given."
  (interactive "P")
  (if prefix
      (message "HELLO!")
    (message "hello")))
```

## Keybindings

### global-set-key

```elisp
(global-set-key (kbd "C-c g") #'greet-user)
(global-set-key (kbd "C-c d") #'insert-date)
```

### define-key with a keymap

```elisp
(define-key emacs-lisp-mode-map (kbd "C-c e") #'eval-buffer)
```

### Creating your own keymap

```elisp
(defvar my-prefix-map (make-sparse-keymap)
  "My personal prefix keymap.")

(define-key my-prefix-map (kbd "w") #'count-words)
(define-key my-prefix-map (kbd "l") #'count-lines-page)

(global-set-key (kbd "C-c m") my-prefix-map)
;; Now C-c m w runs count-words
```

### Key sequences

```elisp
(kbd "C-c C-k")     ;; Control-c Control-k
(kbd "M-s o")       ;; Meta-s then o
(kbd "C-x 4 f")    ;; three-key sequence
(kbd "<f5>")        ;; function key
```

## Minor Modes

A minor mode is a toggleable feature. `define-minor-mode` creates one:

```elisp
(define-minor-mode my-highlight-mode
  "Highlight the current line."
  :lighter " HL"
  :keymap (let ((map (make-sparse-keymap)))
            (define-key map (kbd "C-c h") #'hl-line-mode)
            map)
  (if my-highlight-mode
      (hl-line-mode 1)
    (hl-line-mode -1)))
```

- `:lighter` — text shown in the mode line
- `:keymap` — keys active only when the mode is on
- The body runs when the mode is toggled

### Global minor mode

```elisp
(define-minor-mode my-global-mode
  "A global minor mode example."
  :global t
  :lighter " MG"
  (if my-global-mode
      (message "Global mode ON")
    (message "Global mode OFF")))
```

## Hooks

Hooks are lists of functions called at specific events:

```elisp
;; Run a function when entering emacs-lisp-mode
(add-hook 'emacs-lisp-mode-hook
          (lambda ()
            (setq-local indent-tabs-mode nil)))

;; Named function (preferred for removability)
(defun my-prog-setup ()
  "Setup for programming modes."
  (display-line-numbers-mode 1)
  (hl-line-mode 1))

(add-hook 'prog-mode-hook #'my-prog-setup)

;; Remove a hook
(remove-hook 'prog-mode-hook #'my-prog-setup)
```

Common hooks:

- `after-init-hook` — after Emacs starts
- `before-save-hook` — before saving a file
- `prog-mode-hook` — entering any programming mode
- `text-mode-hook` — entering text mode
- `kill-buffer-hook` — before a buffer is killed

### Buffer-local hooks

```elisp
(add-hook 'before-save-hook #'delete-trailing-whitespace nil t)
;; The final `t` makes it buffer-local
```

## Exercises

1. Write a command that prompts for a file name and inserts its contents at point. Use the `f` interactive code.
2. Create a command that duplicates the current line. With a prefix argument `C-u N`, duplicate it N times.
3. Define a keymap with three bindings and attach it to a prefix key.
4. Write a minor mode that shows word count in the mode line (update on every change using `post-command-hook`).
5. Add a `before-save-hook` that inserts a "Last modified" timestamp at the top of the file.
