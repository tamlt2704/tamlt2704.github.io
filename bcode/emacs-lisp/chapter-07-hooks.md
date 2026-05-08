# Chapter 7: Hooks and Advice

[← Chapter 6: Buffers and Windows](chapter-06-buffers.md) | [Chapter 8: Keymaps →](chapter-08-keymaps.md)

---

## The Wish

"I want my formatter to run on every save — but only for certain modes. And I want to tweak how existing commands behave without rewriting them."

## Hooks: Event Callbacks

A hook is a list of functions that Emacs calls when something happens. They're the primary extension mechanism.

```elisp
;; add-hook: attach your function to an event
(add-hook 'HOOK-NAME #'YOUR-FUNCTION)

;; remove-hook: detach it
(remove-hook 'HOOK-NAME #'YOUR-FUNCTION)
```

### Common Hooks

```elisp
;; Mode hooks — run when a mode activates
'emacs-lisp-mode-hook      ; Entering elisp-mode
'python-mode-hook          ; Entering python-mode
'prog-mode-hook            ; Any programming mode
'text-mode-hook            ; Any text mode

;; File hooks
'find-file-hook            ; After opening a file
'after-save-hook           ; After saving
'before-save-hook          ; Before saving

;; Lifecycle hooks
'emacs-startup-hook        ; After init.el loads
'kill-emacs-hook           ; Before Emacs exits
'kill-buffer-hook          ; Before a buffer is killed
```

## Practical: Format on Save

```elisp
(defun my-format-on-save ()
  "Run the appropriate formatter before saving."
  (cond
   ((derived-mode-p 'go-mode)
    (gofmt))
   ((derived-mode-p 'rust-mode)
    (rust-format-buffer))
   ((derived-mode-p 'python-mode)
    (when (executable-find "black")
      (let ((point-pos (point)))
        (shell-command-on-region (point-min) (point-max)
                                "black -q -" t t)
        (goto-char point-pos))))))

(add-hook 'before-save-hook #'my-format-on-save)
```

### Buffer-Local Hooks

The `LOCAL` argument makes a hook buffer-specific:

```elisp
;; Only format in go-mode buffers (cleaner approach)
(defun my-go-format-setup ()
  "Add gofmt to before-save-hook locally."
  (add-hook 'before-save-hook #'gofmt nil t))  ; t = buffer-local

(add-hook 'go-mode-hook #'my-go-format-setup)
```

## Hook Depth (Ordering)

Emacs 29+ supports hook depth — control execution order:

```elisp
;; depth: negative = run earlier, positive = run later
(add-hook 'before-save-hook #'delete-trailing-whitespace -10)  ; Early
(add-hook 'before-save-hook #'my-format-on-save 0)             ; Normal
(add-hook 'before-save-hook #'my-update-timestamp 90)          ; Late
```

## Advice: Modify Existing Functions

Advice lets you wrap, prepend, or append behavior to any function — even built-in ones:

```elisp
;; advice-add: attach advice to a function
(advice-add 'TARGET-FUNCTION :WHERE #'YOUR-ADVICE)

;; advice-remove: detach it
(advice-remove 'TARGET-FUNCTION #'YOUR-ADVICE)
```

### :before — Run Before the Original

```elisp
(defun my-save-message (&rest _)
  "Log a message before every save."
  (message "Saving %s at %s" (buffer-name) (current-time-string)))

(advice-add 'save-buffer :before #'my-save-message)
```

### :after — Run After the Original

```elisp
(defun my-after-kill-ring (&rest _)
  "Notify when something is added to kill ring."
  (message "Copied %d chars" (length (car kill-ring))))

(advice-add 'kill-ring-save :after #'my-after-kill-ring)
```

### :around — Wrap the Original

The most powerful form. You control if and when the original runs:

```elisp
(defun my-timed-save (orig-fn &rest args)
  "Time how long save-buffer takes."
  (let ((start (current-time)))
    (apply orig-fn args)  ; Call the original
    (message "Save took %.3fs"
             (float-time (time-subtract (current-time) start)))))

(advice-add 'save-buffer :around #'my-timed-save)
```

### :override — Replace Entirely

```elisp
(defun my-quiet-message (orig-fn format-string &rest args)
  "Suppress messages matching 'Wrote'."
  (unless (string-match-p "^Wrote" format-string)
    (apply orig-fn format-string args)))

(advice-add 'message :around #'my-quiet-message)
```

## Practical: Auto-Save Notification with Timestamp

```elisp
(defvar my-last-save-time nil
  "Time of last save, per buffer.")
(make-variable-buffer-local 'my-last-save-time)

(defun my-save-timestamp ()
  "Record save time and show time since last save."
  (let ((elapsed (when my-last-save-time
                   (float-time
                    (time-subtract (current-time) my-last-save-time)))))
    (setq my-last-save-time (current-time))
    (when elapsed
      (message "Saved. (%.0fs since last save)" elapsed))))

(add-hook 'after-save-hook #'my-save-timestamp)
```

## Removing Hooks and Advice

```elisp
;; Remove a hook
(remove-hook 'before-save-hook #'my-format-on-save)

;; Remove advice
(advice-remove 'save-buffer #'my-timed-save)

;; List all advice on a function (for debugging)
(advice-mapc (lambda (fn props)
               (message "Advice: %s %s" fn props))
             'save-buffer)
```

## Exercises

1. Write a hook that auto-inserts a file header (author, date) when creating new `.el` files.
2. Add `:around` advice to `find-file` that measures how long file opening takes.
3. Create a `before-save-hook` function that checks for debugger statements (`console.log`, `print()`, `fmt.Println`) and warns you.

## What You Learned

- **Hooks** — lists of functions called on events
- **`add-hook`** — attach behavior to events
- **Buffer-local hooks** — per-buffer behavior with the `LOCAL` arg
- **Hook depth** — control execution order (Emacs 29+)
- **`advice-add`** — modify existing functions without rewriting them
- **`:before` / `:after` / `:around`** — when your code runs relative to the original

Hooks trigger your code. But you still need to trigger it manually sometimes — with keybindings. Let's build a custom keymap.

---

[← Chapter 6: Buffers and Windows](chapter-06-buffers.md) | [Chapter 8: Keymaps →](chapter-08-keymaps.md)
