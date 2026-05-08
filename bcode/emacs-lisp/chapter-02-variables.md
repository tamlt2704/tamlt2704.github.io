# Chapter 2: Variables and State

[← Chapter 1: Hello Elisp](chapter-01-hello.md) | [Chapter 3: Conditionals →](chapter-03-conditionals.md)

---

## The Wish

"I want to toggle between my coding font (13px monospace) and my presentation font (24px). One keybinding, instant switch."

## The Exploration

You need:
1. A variable to track which font size is active
2. A function that toggles between them
3. A way to actually change the font size

Let's explore. `C-h v` (describe-variable), type `default`:

```
default-frame-alist — Alist of default values for frame parameters.
```

And `C-h f set-face-attribute`:

```
(set-face-attribute FACE FRAME &rest ARGS)
Set attributes of FACE on FRAME from ARGS.
```

## setq: Setting Variables

`setq` sets a variable's value:

```elisp
(setq my-coding-size 13)
(setq my-presentation-size 24)
(setq my-current-mode 'coding)  ; Quote: symbol, not a function call
```

`setq` stands for "set quoted" — it automatically quotes the variable name so you don't have to write `(set 'my-coding-size 13)`.

```elisp
;; Set multiple variables at once
(setq my-coding-size 13
      my-presentation-size 24
      my-current-mode 'coding)
```

## The Toggle Function

```elisp
(setq my-coding-size 13)
(setq my-presentation-size 24)

(defun toggle-font-size ()
  "Toggle between coding and presentation font sizes."
  (interactive)  ; Makes it callable via M-x
  (let ((new-size (if (= (face-attribute 'default :height)
                         (* my-coding-size 10))
                      my-presentation-size
                    my-coding-size)))
    (set-face-attribute 'default nil :height (* new-size 10))
    (message "Font size: %d" new-size)))
```

Note: Emacs measures font height in 1/10 pt, so 13pt = 130.

Evaluate it, then `M-x toggle-font-size`. Your font switches instantly.

## let: Local Variables

`let` creates variables that only exist inside the `let` block:

```elisp
(let ((x 10)
      (y 20))
  (+ x y))  ; → 30
;; x and y don't exist out here
```

Why use `let` instead of `setq`?
- `setq` creates/modifies **global** variables (visible everywhere)
- `let` creates **local** variables (gone when the block ends)

```elisp
;; GLOBAL: pollutes the namespace, persists forever
(setq temp-result (+ 1 2))

;; LOCAL: clean, temporary, no side effects
(let ((temp-result (+ 1 2)))
  (message "Result: %d" temp-result))
;; temp-result doesn't exist here
```

### let vs let*

```elisp
;; let: all bindings happen simultaneously (can't reference each other)
(let ((a 1)
      (b (+ a 1)))  ; ERROR: 'a' not yet bound in this context
  (+ a b))

;; let*: bindings happen sequentially (later ones can use earlier ones)
(let* ((a 1)
       (b (+ a 1)))  ; OK: 'a' is already bound
  (+ a b))  ; → 3
```

Use `let*` when later variables depend on earlier ones.

## defvar and defcustom: Declaring Variables Properly

For variables that other code (or users) might want to customize:

### defvar: Developer-Facing Variable

```elisp
(defvar my-font-coding-size 13
  "Font size for coding mode.")

(defvar my-font-presentation-size 24
  "Font size for presentation mode.")
```

`defvar` only sets the value if the variable is **not already set**. This means users can override it in their init.el before your code loads:

```elisp
;; User's init.el (loaded first):
(setq my-font-coding-size 15)  ; User prefers 15

;; Your code (loaded later):
(defvar my-font-coding-size 13)  ; Does NOT override — already set!
```

### defcustom: User-Facing Variable (Appears in Customize UI)

```elisp
(defcustom my-font-coding-size 13
  "Font size for coding mode."
  :type 'integer
  :group 'my-font-toggle)

(defcustom my-font-presentation-size 24
  "Font size for presentation mode."
  :type 'integer
  :group 'my-font-toggle)
```

`defcustom` variables appear in `M-x customize-group` — Emacs's GUI settings panel. Users can change them without editing Elisp.

## Buffer-Local Variables

Some variables should have different values in different buffers:

```elisp
;; Global: same value everywhere
(setq my-var "global")

;; Buffer-local: different value per buffer
(make-variable-buffer-local 'my-indent-width)
(setq my-indent-width 4)  ; Default for all buffers

;; Or set for just the current buffer:
(setq-local my-indent-width 2)  ; Only this buffer gets 2
```

This is how Emacs handles per-file settings — `tab-width`, `fill-column`, etc. are buffer-local.

## The Complete Font Toggle

```elisp
;;; Font size toggle — add to init.el

(defcustom my-font-sizes '(13 . 24)
  "Cons cell of (coding-size . presentation-size)."
  :type '(cons integer integer))

(defvar my-font--presenting nil
  "Non-nil when in presentation mode.")

(defun my-toggle-font-size ()
  "Toggle between coding and presentation font sizes."
  (interactive)
  (setq my-font--presenting (not my-font--presenting))
  (let ((size (if my-font--presenting
                  (cdr my-font-sizes)
                (car my-font-sizes))))
    (set-face-attribute 'default nil :height (* size 10))
    (message "%s mode (size %d)"
             (if my-font--presenting "Presentation" "Coding")
             size)))

;; Bind to a key
(global-set-key (kbd "C-c f") #'my-toggle-font-size)
```

Now `C-c f` toggles instantly. The variable `my-font--presenting` tracks state. The double dash (`--`) is an Elisp convention meaning "private/internal variable."

## Variable Naming Conventions

| Pattern | Meaning | Example |
|---|---|---|
| `my-package-var` | Public variable | `my-font-sizes` |
| `my-package--var` | Private/internal | `my-font--presenting` |
| `my-package-var-p` | Boolean (predicate) | `my-font-presenting-p` |
| `my-package-var-hook` | Hook variable | `my-font-change-hook` |

## Inspecting Variables

```elisp
;; Check a variable's value
(message "%S" my-font-sizes)  ; %S prints any Lisp object

;; Check if a variable is bound
(boundp 'my-font-sizes)  ; → t (true) or nil (false)

;; Describe a variable (interactive)
;; C-h v my-font-sizes RET
```

## Exercises

1. Create a `my-toggle-theme` function that switches between a light and dark theme. Use `load-theme` and a boolean variable to track state.

2. Create a variable `my-scratch-counter` that increments every time you evaluate something in `*scratch*`. (Hint: use `advice-add` on `eval-last-sexp` — preview of Chapter 7.)

3. Make `my-font-sizes` a list of 3+ sizes instead of a cons cell, and cycle through them on each toggle.

## What You Learned

- **`setq`** — set a global variable
- **`let` / `let*`** — local variables (temporary, scoped)
- **`defvar`** — declare a variable (won't override existing value)
- **`defcustom`** — user-customizable variable (appears in Customize UI)
- **Buffer-local** — `setq-local` for per-buffer values
- **Naming conventions** — `package-name`, `package--private`, `-p` for booleans
- **`interactive`** — makes a function callable via `M-x`

The font toggle works. But you want different behavior for different file types — format on save for Go, but not for Markdown. That requires conditionals.

---

[← Chapter 1: Hello Elisp](chapter-01-hello.md) | [Chapter 3: Conditionals →](chapter-03-conditionals.md)
