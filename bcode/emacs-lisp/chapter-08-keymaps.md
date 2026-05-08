# Chapter 8: Keymaps

[← Chapter 7: Hooks and Advice](chapter-07-hooks.md) | [Chapter 9: Text Manipulation →](chapter-09-text.md)

---

## The Wish

"I want my own prefix key — like `C-c m` — with a whole tree of custom bindings underneath it. A personal command menu."

## How Keymaps Work

Emacs keybindings live in keymaps — data structures that map key sequences to commands. When you press a key, Emacs searches keymaps in this order:

1. **Minor mode keymaps** (highest priority)
2. **Local keymap** (major mode)
3. **Global keymap** (fallback)

```elisp
;; Bind a key globally
(global-set-key (kbd "C-c d") #'duplicate-line)

;; Bind in a specific mode
(define-key emacs-lisp-mode-map (kbd "C-c C-r") #'eval-region)

;; Unbind a key
(global-unset-key (kbd "C-z"))  ; No more accidental suspend
```

## The kbd Macro

`kbd` translates human-readable key descriptions to internal format:

```elisp
(kbd "C-c m")       ; Control-c then m
(kbd "C-M-s")       ; Control-Meta-s
(kbd "M-RET")       ; Meta-Return
(kbd "<f5>")        ; F5 key
(kbd "C-c C-c")     ; Control-c twice
(kbd "s-p")         ; Super-p (Cmd on Mac)
```

## Creating Your Own Keymap

```elisp
;; define-prefix-command creates a keymap you can bind as a prefix
(define-prefix-command 'my-leader-map)

;; Bind commands within your prefix map
(define-key my-leader-map (kbd "f") #'find-file)
(define-key my-leader-map (kbd "b") #'switch-to-buffer)
(define-key my-leader-map (kbd "k") #'kill-buffer)
(define-key my-leader-map (kbd "s") #'save-buffer)
(define-key my-leader-map (kbd "r") #'recentf-open-files)

;; Attach the prefix map to a key
(global-set-key (kbd "C-c m") 'my-leader-map)
```

Now `C-c m f` opens find-file, `C-c m b` switches buffers, etc.

## Nested Prefix Keys

```elisp
;; Sub-prefix for project commands
(define-prefix-command 'my-project-map)
(define-key my-project-map (kbd "f") #'project-find-file)
(define-key my-project-map (kbd "s") #'project-search)
(define-key my-project-map (kbd "c") #'project-compile)
(define-key my-project-map (kbd "t") #'project-eshell)

;; Nest it under the leader
(define-key my-leader-map (kbd "p") 'my-project-map)
;; Now C-c m p f → project-find-file
```

## Practical: Full Personal Keymap

```elisp
(define-prefix-command 'my-leader-map)

;; File operations
(define-key my-leader-map (kbd "f f") #'find-file)
(define-key my-leader-map (kbd "f r") #'recentf)
(define-key my-leader-map (kbd "f s") #'save-buffer)

;; Buffer operations
(define-key my-leader-map (kbd "b b") #'switch-to-buffer)
(define-key my-leader-map (kbd "b k") #'kill-current-buffer)
(define-key my-leader-map (kbd "b l") #'ibuffer)

;; Window operations
(define-key my-leader-map (kbd "w v") #'split-window-right)
(define-key my-leader-map (kbd "w s") #'split-window-below)
(define-key my-leader-map (kbd "w d") #'delete-window)
(define-key my-leader-map (kbd "w o") #'delete-other-windows)

;; Toggle operations
(define-key my-leader-map (kbd "t l") #'display-line-numbers-mode)
(define-key my-leader-map (kbd "t w") #'whitespace-mode)
(define-key my-leader-map (kbd "t t") #'load-theme)

;; Bind the leader to C-c m
(global-set-key (kbd "C-c m") 'my-leader-map)
```

## which-key: Discoverability

Emacs 30 includes `which-key-mode` built-in. For Emacs 29, install it:

```elisp
(use-package which-key
  :config
  (which-key-mode 1)
  (setq which-key-idle-delay 0.3))
```

Now pressing `C-c m` and waiting shows all available sub-keys in a popup. Self-documenting keybindings.

## Hydra-Style Menus with repeat-map (Emacs 28+)

Repeat maps let you press a prefix once, then repeat actions with single keys:

```elisp
;; Window resize hydra using repeat-map
(defvar my-window-resize-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "h") #'shrink-window-horizontally)
    (define-key map (kbd "l") #'enlarge-window-horizontally)
    (define-key map (kbd "j") #'enlarge-window)
    (define-key map (kbd "k") #'shrink-window)
    (define-key map (kbd "=") #'balance-windows)
    map)
  "Keymap for repeating window resize commands.")

;; Mark commands as repeatable
(put 'shrink-window-horizontally 'repeat-map 'my-window-resize-map)
(put 'enlarge-window-horizontally 'repeat-map 'my-window-resize-map)
(put 'enlarge-window 'repeat-map 'my-window-resize-map)
(put 'shrink-window 'repeat-map 'my-window-resize-map)
(put 'balance-windows 'repeat-map 'my-window-resize-map)

;; Enable repeat-mode globally
(repeat-mode 1)

;; Trigger with a normal binding
(global-set-key (kbd "C-c w h") #'shrink-window-horizontally)
```

After pressing `C-c w h`, you can keep pressing `h`, `l`, `j`, `k` to resize without the prefix.

## Mode-Specific Bindings

```elisp
;; Use define-key with the mode's map
(with-eval-after-load 'python
  (define-key python-mode-map (kbd "C-c C-f") #'python-black-buffer))

;; Or use the mode hook
(defun my-elisp-keys ()
  "Custom keys for elisp editing."
  (local-set-key (kbd "C-c e") #'eval-buffer)
  (local-set-key (kbd "C-c d") #'edebug-defun))

(add-hook 'emacs-lisp-mode-hook #'my-elisp-keys)
```

## Exercises

1. Create a prefix map under `C-c g` for git commands (magit-status, magit-log, magit-blame).
2. Build a repeat-map for text scaling (`C-x C-=` then keep pressing `=` or `-`).
3. Write a command that displays all your custom keybindings in a help buffer.

## What You Learned

- **Keymaps** — data structures mapping keys to commands
- **`define-key`** — bind a key in a specific keymap
- **`define-prefix-command`** — create your own prefix key tree
- **`kbd`** — human-readable key notation
- **Nested prefixes** — `C-c m p f` style deep bindings
- **`repeat-map`** — hydra-style repeating keys (Emacs 28+)
- **`which-key`** — self-documenting key discovery

You have keys bound to commands. But many commands need to manipulate text — move point, select regions, transform content. Let's learn the text API.

---

[← Chapter 7: Hooks and Advice](chapter-07-hooks.md) | [Chapter 9: Text Manipulation →](chapter-09-text.md)
