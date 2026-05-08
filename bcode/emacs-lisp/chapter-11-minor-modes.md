# Chapter 11: Minor Modes

[← Chapter 10: Regular Expressions](chapter-10-regex.md) | [Chapter 12: Major Modes →](chapter-12-major-modes.md)

---

## The Wish

"I want a toggleable writing mode — when I'm writing prose, I want a clean interface: no line numbers, bigger margins, centered text, soft word wrap. One keybinding to flip it on and off."

## What Is a Minor Mode?

A minor mode is a toggleable feature that can be active in any buffer. Unlike major modes (one per buffer), you can stack multiple minor modes. Examples: `flyspell-mode`, `display-line-numbers-mode`, `visual-line-mode`.

A minor mode provides:
- A toggle command (turn on/off)
- A lighter (text in the mode line)
- An optional keymap (active only when the mode is on)
- Setup/teardown logic

## define-minor-mode

```elisp
(define-minor-mode my-example-mode
  "A minimal example minor mode."
  :lighter " Ex"           ; Shows " Ex" in mode line when active
  :keymap (make-sparse-keymap)
  ;; Body: runs when mode is toggled
  (if my-example-mode
      (message "Example mode ON")
    (message "Example mode OFF")))
```

The body runs every time the mode is toggled. The mode variable (`my-example-mode`) is `t` when on, `nil` when off.

## Anatomy of define-minor-mode

```elisp
(define-minor-mode MODE-NAME
  "DOCSTRING"
  :lighter LIGHTER      ; Mode line indicator
  :keymap KEYMAP        ; Mode-specific bindings
  :global GLOBAL-P      ; nil = buffer-local, t = global
  :group GROUP          ; Customization group
  BODY...)              ; Code that runs on toggle
```

## Practical: Writing Mode

```elisp
(defvar-local my-writing--old-margins nil
  "Stored margins to restore when writing mode is disabled.")

(defvar-local my-writing--old-line-numbers nil
  "Whether line numbers were active before writing mode.")

(define-minor-mode my-writing-mode
  "A distraction-free writing environment.
Hides line numbers, centers text with wide margins, and enables
soft word wrap."
  :lighter " ✍"
  :keymap (let ((map (make-sparse-keymap)))
            (define-key map (kbd "C-c q") #'my-writing-mode)
            map)
  (if my-writing-mode
      (my-writing--enable)
    (my-writing--disable)))

(defun my-writing--enable ()
  "Set up the writing environment."
  ;; Save state to restore later
  (setq my-writing--old-line-numbers display-line-numbers-mode)
  (setq my-writing--old-margins
        (cons left-margin-width right-margin-width))

  ;; Disable distractions
  (display-line-numbers-mode -1)
  (visual-line-mode 1)

  ;; Center text with margins
  (let ((margin (max 0 (/ (- (window-width) 80) 2))))
    (setq left-margin-width margin)
    (setq right-margin-width margin))

  ;; Apply margin changes (requires buffer redisplay)
  (set-window-buffer (selected-window) (current-buffer))
  (message "Writing mode enabled. Focus."))

(defun my-writing--disable ()
  "Tear down the writing environment."
  ;; Restore previous state
  (when my-writing--old-line-numbers
    (display-line-numbers-mode 1))
  (visual-line-mode -1)

  ;; Restore margins
  (setq left-margin-width (car my-writing--old-margins))
  (setq right-margin-width (cdr my-writing--old-margins))
  (set-window-buffer (selected-window) (current-buffer))
  (message "Writing mode disabled."))

;; Bind globally
(global-set-key (kbd "C-c w") #'my-writing-mode)
```

## Global Minor Modes

A global mode affects all buffers:

```elisp
(define-minor-mode my-global-beacon-mode
  "Flash the cursor line after every jump."
  :global t
  :lighter " 💡"
  (if my-global-beacon-mode
      (add-hook 'post-command-hook #'my-beacon--flash)
    (remove-hook 'post-command-hook #'my-beacon--flash)))

(defvar-local my-beacon--last-point nil)

(defun my-beacon--flash ()
  "Flash the current line if point moved significantly."
  (when (and my-beacon--last-point
             (> (abs (- (point) my-beacon--last-point)) 200))
    (pulse-momentary-highlight-one-line (point)))
  (setq my-beacon--last-point (point)))
```

## Mode Hooks

Every minor mode automatically gets a hook:

```elisp
;; my-writing-mode creates my-writing-mode-hook
(add-hook 'my-writing-mode-hook
          (lambda ()
            (when my-writing-mode
              (setq-local cursor-type 'bar))))
```

## Turning Modes On Automatically

```elisp
;; Enable writing mode for org and markdown files
(add-hook 'org-mode-hook #'my-writing-mode)
(add-hook 'markdown-mode-hook #'my-writing-mode)

;; Or use a function that checks conditions
(defun my-maybe-writing-mode ()
  "Enable writing mode for prose files."
  (when (derived-mode-p 'text-mode)
    (my-writing-mode 1)))

(add-hook 'find-file-hook #'my-maybe-writing-mode)
```

## defvar-local: Buffer-Local State

Use `defvar-local` for per-buffer state in your mode:

```elisp
(defvar-local my-mode-active-overlays '()
  "Overlays created by my-mode in this buffer.")

;; Clean up on disable
(define-minor-mode my-highlight-mode
  "Highlight things."
  :lighter " Hi"
  (if my-highlight-mode
      (my-highlight--add-overlays)
    ;; Cleanup
    (mapc #'delete-overlay my-mode-active-overlays)
    (setq my-mode-active-overlays nil)))
```

## Exercises

1. Create a `my-focus-mode` that hides the mode line and makes the buffer read-only (for reading code without accidentally editing).
2. Write a minor mode that auto-saves the buffer every 30 seconds (hint: `run-with-timer`, cancel on disable).
3. Build a `my-pair-mode` that auto-inserts closing brackets/parens/quotes when you type the opening one.

## What You Learned

- **`define-minor-mode`** — create toggleable features
- **`:lighter`** — mode line indicator
- **`:keymap`** — mode-specific keybindings
- **`:global`** — buffer-local vs global modes
- **State management** — save/restore with `defvar-local`
- **Mode hooks** — auto-created hooks for your mode
- **Cleanup** — always tear down what you set up

A minor mode adds behavior. But what if you need a completely new editing experience — with its own syntax highlighting, indentation, and commands? That's a major mode.

---

[← Chapter 10: Regular Expressions](chapter-10-regex.md) | [Chapter 12: Major Modes →](chapter-12-major-modes.md)
