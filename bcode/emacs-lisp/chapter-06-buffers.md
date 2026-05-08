# Chapter 6: Buffers and Windows

[← Chapter 5: Interactive Commands](chapter-05-interactive.md) | [Chapter 7: Hooks and Advice →](chapter-07-hooks.md)

---

## The Wish

"I want Emacs to auto-arrange my workspace on startup — code on the left, terminal on the bottom-right, notes on the top-right. Every morning, same layout, zero clicks."

## Buffers vs Windows vs Frames

```
Frame (OS window)
├── Window (top-left)     → displays Buffer A
├── Window (top-right)    → displays Buffer B
└── Window (bottom)       → displays Buffer C
```

- **Buffer** — text content (may or may not be visible)
- **Window** — a viewport into a buffer
- **Frame** — an OS-level window containing windows

A buffer exists even when no window shows it. Multiple windows can show the same buffer.

## Buffer Basics

```elisp
;; Get info about buffers
(current-buffer)                ; → #<buffer *scratch*>
(buffer-name)                   ; → "*scratch*"
(buffer-file-name)              ; → nil (or "/path/to/file")
(buffer-list)                   ; → list of all buffers

;; Switch to a buffer (makes it current for Elisp, doesn't display)
(set-buffer "init.el")

;; Create or get a buffer
(get-buffer-create "*my-output*")

;; Kill a buffer
(kill-buffer "*my-output*")
```

## save-excursion: Don't Lose Your Place

`save-excursion` is essential — it restores the current buffer and cursor position after your code runs:

```elisp
(save-excursion
  (set-buffer "*Messages*")
  (goto-char (point-max))
  (insert "Hello from Elisp\n"))
;; After this, you're back where you started
```

## with-current-buffer: Work in Another Buffer

```elisp
;; Cleaner than save-excursion + set-buffer
(with-current-buffer "*Messages*"
  (buffer-substring-no-properties
   (point-min) (min 100 (point-max))))

;; Create and populate a buffer
(with-current-buffer (get-buffer-create "*my-report*")
  (erase-buffer)
  (insert "Report generated: " (current-time-string) "\n")
  (insert "Open buffers: " (number-to-string (length (buffer-list)))))
```

## Window Management

```elisp
;; Split windows
(split-window-right)            ; Split vertically (side by side)
(split-window-below)            ; Split horizontally (top/bottom)

;; Navigate windows
(other-window 1)                ; Move to next window
(select-window (next-window))   ; Same thing, explicit

;; Display a buffer in a window
(switch-to-buffer "init.el")           ; Replace current window's buffer
(switch-to-buffer-other-window "init.el")  ; Show in other window
(display-buffer "*compilation*")       ; Let Emacs decide where

;; Delete windows
(delete-other-windows)          ; Make current window fill frame
(delete-window)                 ; Remove current window
```

## Window Sizing

```elisp
;; Resize windows
(window-width)                  ; Current window width in columns
(window-height)                 ; Current window height in lines

;; Set exact size
(let ((win (selected-window)))
  (window-resize win (- 80 (window-width win)) t))  ; Set width to 80

;; Balance all windows equally
(balance-windows)
```

## Practical: Startup Workspace Layout

```elisp
(defun my-workspace-layout ()
  "Set up my preferred workspace: code left, notes top-right, term bottom-right."
  (interactive)
  ;; Start fresh
  (delete-other-windows)

  ;; Left window: main code (current buffer stays)
  (let ((left-win (selected-window))
        (right-win (split-window-right)))

    ;; Right side: split into top and bottom
    (select-window right-win)
    (let ((top-right (selected-window))
          (bottom-right (split-window-below)))

      ;; Top-right: notes
      (set-window-buffer top-right
                         (find-file-noselect "~/notes/todo.org"))

      ;; Bottom-right: eshell
      (select-window bottom-right)
      (eshell)

      ;; Return focus to left (code) window
      (select-window left-win)))

  ;; Make left window wider (60% of frame)
  (let ((target-width (floor (* 0.6 (frame-width)))))
    (window-resize (selected-window)
                   (- target-width (window-width))
                   t)))

;; Run on startup (after init)
(add-hook 'emacs-startup-hook #'my-workspace-layout)
```

## display-buffer-alist: Control Where Buffers Appear

```elisp
;; Tell Emacs where to show specific buffers
(setq display-buffer-alist
      '(;; Compilation at the bottom, 15 lines tall
        ("\\*compilation\\*"
         (display-buffer-at-bottom)
         (window-height . 15))

        ;; Help on the right side
        ("\\*Help\\*"
         (display-buffer-in-side-window)
         (side . right)
         (window-width . 0.4))

        ;; Shell buffers at the bottom
        ("\\*e?shell\\*"
         (display-buffer-at-bottom)
         (window-height . 0.3))))
```

## Temporary Buffers with with-temp-buffer

```elisp
;; Create a buffer, do work, discard it
(with-temp-buffer
  (insert-file-contents "~/.emacs.d/init.el")
  (count-lines (point-min) (point-max)))
;; → number of lines in init.el (buffer is gone now)
```

## Exercises

1. Write a command that lists all unsaved buffers in a new buffer.
2. Create a `my-focus-mode` that deletes other windows and centers the current buffer.
3. Write a function that saves the current window layout and restores it later (hint: `current-window-configuration` and `set-window-configuration`).

## What You Learned

- **Buffers** — text containers, independent of display
- **`save-excursion`** — preserve position during buffer operations
- **`with-current-buffer`** — operate on another buffer cleanly
- **Window splitting** — `split-window-right`, `split-window-below`
- **`display-buffer-alist`** — rules for where buffers appear
- **`with-temp-buffer`** — disposable scratch space

Your workspace is set up, but you want things to happen automatically — format on save, lint on open, compile on change. That's what hooks are for.

---

[← Chapter 5: Interactive Commands](chapter-05-interactive.md) | [Chapter 7: Hooks and Advice →](chapter-07-hooks.md)
