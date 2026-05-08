# Chapter 3: Conditionals and Logic

[← Chapter 2: Variables](chapter-02-variables.md) | [Chapter 4: Lists →](chapter-04-lists.md)

---

## The Wish

"I want different behavior for different file types. Format on save for Go and Rust, but not for Markdown or org files. Show line numbers in code files but not in prose files."

## if: The Basic Branch

```elisp
(if CONDITION
    THEN-FORM      ; Executed if condition is non-nil
  ELSE-FORMS...)   ; Executed if condition is nil (optional)
```

```elisp
(defun my-maybe-format ()
  "Format buffer on save, but only for code files."
  (if (derived-mode-p 'prog-mode)
      (format-buffer)       ; Then: format code files
    (message "Skipping format for %s" major-mode)))  ; Else: skip
```

In Elisp, **nil** is false. **Everything else** is true (including 0, empty string, and the symbol `t`).

```elisp
(if nil "yes" "no")     ; → "no"
(if t "yes" "no")       ; → "yes"
(if 0 "yes" "no")       ; → "yes" (0 is NOT nil!)
(if "" "yes" "no")      ; → "yes" (empty string is NOT nil!)
(if '() "yes" "no")     ; → "no" ('() is nil)
```

## when and unless: One-Branch Conditionals

When you only need the "then" or only the "else":

```elisp
;; when = if without else (do something only if true)
(when (derived-mode-p 'go-mode)
  (setq-local tab-width 4)
  (gofmt-before-save))  ; Can have multiple body forms

;; unless = if-not (do something only if false)
(unless (derived-mode-p 'org-mode)
  (display-line-numbers-mode 1))
```

`when` and `unless` are cleaner than `if` when you don't need both branches. They also allow multiple body forms without `progn`.

## cond: Multi-Branch (Switch/Case)

```elisp
(defun my-setup-mode ()
  "Configure settings based on current major mode."
  (cond
   ((derived-mode-p 'go-mode)
    (setq-local tab-width 4)
    (add-hook 'before-save-hook #'gofmt-before-save nil t))

   ((derived-mode-p 'rust-mode)
    (setq-local tab-width 4)
    (add-hook 'before-save-hook #'rust-format-buffer nil t))

   ((derived-mode-p 'python-mode)
    (setq-local tab-width 4)
    (setq-local python-indent-offset 4))

   ((derived-mode-p 'markdown-mode)
    (visual-line-mode 1)
    (setq-local fill-column 80))

   (t  ; Default case (always true)
    (message "No special config for %s" major-mode))))
```

`cond` evaluates each condition in order. The first true one wins. `t` at the end is the default (always true).

## Logical Operators: and, or, not

```elisp
;; and: returns last value if all true, nil if any false
(and t t t)        ; → t
(and t nil t)      ; → nil (short-circuits at nil)
(and 1 2 3)       ; → 3 (last value)

;; or: returns first non-nil value
(or nil nil 42)   ; → 42
(or nil nil nil)  ; → nil
(or "first" "second")  ; → "first" (short-circuits)

;; not: inverts truthiness
(not nil)          ; → t
(not t)            ; → nil
(not 42)           ; → nil (42 is truthy)
```

### Short-Circuit Evaluation

`and` and `or` short-circuit — they stop evaluating as soon as the result is determined:

```elisp
;; Safe: won't call buffer-file-name if buffer is nil
(and buffer
     (buffer-file-name buffer)
     (string-match "\\.go$" (buffer-file-name buffer)))

;; Default value pattern:
(or user-specified-value
    (getenv "MY_VAR")
    "fallback-default")
```

## Practical: Format on Save (Per Mode)

```elisp
(defvar my-format-modes '(go-mode rust-mode c-mode)
  "Modes that should auto-format on save.")

(defun my-maybe-format-on-save ()
  "Format the buffer before saving, if in a supported mode."
  (when (memq major-mode my-format-modes)
    (cond
     ((eq major-mode 'go-mode)
      (gofmt))
     ((eq major-mode 'rust-mode)
      (rust-format-buffer))
     ((eq major-mode 'c-mode)
      (clang-format-buffer)))))

(add-hook 'before-save-hook #'my-maybe-format-on-save)
```

## Practical: Line Numbers for Code, Not Prose

```elisp
(defun my-setup-line-numbers ()
  "Show line numbers in code buffers, hide in prose buffers."
  (if (derived-mode-p 'prog-mode)
      (display-line-numbers-mode 1)
    (display-line-numbers-mode -1)))

;; Run when any buffer's mode is set
(add-hook 'after-change-major-mode-hook #'my-setup-line-numbers)
```

## Comparison Functions

```elisp
;; Numeric comparison
(= 5 5)           ; → t
(< 3 5)           ; → t
(> 3 5)           ; → nil
(<= 5 5)          ; → t

;; String comparison
(string= "hello" "hello")   ; → t
(string< "abc" "abd")       ; → t (lexicographic)

;; Symbol/object comparison
(eq 'foo 'foo)              ; → t (same symbol)
(eq "hi" "hi")              ; → nil! (different string objects)
(equal "hi" "hi")           ; → t (same content)

;; Type checking
(numberp 42)       ; → t
(stringp "hi")     ; → t
(listp '(1 2))     ; → t
(null nil)         ; → t
(null '())         ; → t (nil and '() are the same thing)
```

### eq vs equal vs eql

| Function | Compares | Use for |
|---|---|---|
| `eq` | Identity (same object) | Symbols, quick checks |
| `eql` | Identity or same number | Numbers and symbols |
| `equal` | Structural equality | Strings, lists, general comparison |

```elisp
(eq 'hello 'hello)       ; → t (symbols are interned — same object)
(eq "hello" "hello")     ; → nil (different string objects!)
(equal "hello" "hello")  ; → t (same content)
(equal '(1 2 3) '(1 2 3)) ; → t (same structure)
```

Rule of thumb: use `equal` unless you specifically need identity comparison.

## pcase: Pattern Matching (Modern Elisp)

Emacs 25+ has `pcase` — structural pattern matching:

```elisp
(defun my-describe-buffer ()
  "Describe the current buffer based on its properties."
  (pcase major-mode
    ('org-mode (message "Org file: %d headings" (my-count-headings)))
    ('go-mode (message "Go file: %s" (buffer-file-name)))
    ((pred (lambda (m) (derived-mode-p 'prog-mode)))
     (message "Code file in %s" major-mode))
    (_ (message "Other: %s" major-mode))))
```

`pcase` is powerful but has a learning curve. Start with `cond` and graduate to `pcase` when you need pattern matching.

## Exercises

1. Write a function `my-insert-header` that inserts a comment header appropriate for the current mode: `//` for C/Java, `#` for Python/Ruby, `;;` for Elisp, `--` for Haskell.

2. Write a function that sets `fill-column` to 80 for prose modes and 100 for code modes.

3. Create a `my-smart-open` function: if the current file is a test file (contains "test" in the name), open the corresponding source file, and vice versa.

## What You Learned

- **`if`** — basic two-branch conditional
- **`when` / `unless`** — single-branch (cleaner than if with nil else)
- **`cond`** — multi-branch (like switch/case)
- **`and` / `or` / `not`** — logical operators with short-circuit
- **Truthiness** — nil is false, everything else is true
- **`eq` vs `equal`** — identity vs structural equality
- **`derived-mode-p`** — check if current mode inherits from a parent mode

You can now configure Emacs differently per file type. But you keep wanting to work with collections — recent files, project lists, TODO items. That requires understanding Elisp's fundamental data structure: the list.

---

[← Chapter 2: Variables](chapter-02-variables.md) | [Chapter 4: Lists →](chapter-04-lists.md)
