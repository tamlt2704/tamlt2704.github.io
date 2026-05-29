# Chapter 3: Variables

[prev: Functions](chapter-02-functions.md) | [next: Control Flow](chapter-04-control-flow.md)

## setq — Setting Variables

`setq` assigns a value to a symbol:

```elisp
(setq my-name "Alice")
my-name  ;; => "Alice"

;; setq can set multiple variables at once
(setq x 1
      y 2
      z 3)
x  ;; => 1
```

## let and let\* — Local Variables

`let` creates local bindings. Variables are scoped to the let body:

```elisp
(let ((x 10)
      (y 20))
  (+ x y))
;; => 30
;; x and y are not accessible outside
```

`let*` allows later bindings to reference earlier ones:

```elisp
(let* ((x 10)
       (y (* x 2)))
  (+ x y))
;; => 30
```

With plain `let`, this would error because `x` is not yet bound when `y` is defined.

## defvar — Declaring Special Variables

`defvar` declares a variable with a default value. It only sets the value if the variable is not already bound:

```elisp
(defvar my-counter 0
  "A counter for demonstration.")

(setq my-counter 5)
(defvar my-counter 0)  ;; does NOT reset to 0
my-counter  ;; => 5
```

`defvar` also marks the variable as "special" (dynamically scoped), which matters with lexical binding enabled.

## defcustom — User-Configurable Variables

`defcustom` creates variables that appear in `M-x customize`:

```elisp
(defcustom my-greeting "Hello"
  "The greeting to use."
  :type 'string
  :group 'my-package)

(defcustom my-repeat-count 3
  "How many times to repeat."
  :type 'integer
  :group 'my-package)
```

Common `:type` values:

```elisp
:type 'string
:type 'integer
:type 'boolean
:type '(choice (const "option1") (const "option2"))
:type '(repeat string)
```

## defconst — Constants

`defconst` always sets the value (unlike `defvar`) and signals intent that it should not change:

```elisp
(defconst my-pi 3.14159
  "An approximation of pi.")
```

Note: Elisp does not enforce immutability. You can still `setq` a `defconst`, but you should not.

## Buffer-Local Variables

A buffer-local variable has a separate value in each buffer:

```elisp
;; Make a variable buffer-local in the current buffer
(setq-local my-buffer-var "only here")

;; Or explicitly:
(make-local-variable 'my-var)
(setq my-var "local value")
```

To make a variable automatically buffer-local in all buffers:

```elisp
(defvar-local my-mode-active nil
  "Whether my-mode is active in this buffer.")
```

This is equivalent to:

```elisp
(defvar my-mode-active nil)
(make-variable-buffer-local 'my-mode-active)
```

### Checking buffer-local status

```elisp
(local-variable-p 'major-mode)  ;; => t
(buffer-local-value 'major-mode (current-buffer))  ;; => emacs-lisp-mode
```

## Special Variables and Scoping

With `lexical-binding: t`, variables declared with `defvar` or `defcustom` remain dynamically scoped (special). All other variables are lexically scoped:

```elisp
;;; -*- lexical-binding: t; -*-

(defvar my-dynamic-var 10)

(defun read-dynamic ()
  my-dynamic-var)

(let ((my-dynamic-var 99))
  (read-dynamic))
;; => 99 (dynamic: let binding is visible to called functions)

(let ((local-var 42))
  ;; local-var is lexical, only visible in this scope
  local-var)
;; => 42
```

## Practical Example

```elisp
(defcustom greeting-name "World"
  "Name to greet."
  :type 'string
  :group 'greeting)

(defvar greeting-count 0
  "Number of times greeting was called.")

(defun greet ()
  "Greet the configured name."
  (interactive)
  (setq greeting-count (1+ greeting-count))
  (message "Hello, %s! (called %d times)"
           greeting-name greeting-count))
```

## Exercises

1. Use `let` to bind `a` to 5 and `b` to 10, then compute their product.
2. Write a `defcustom` for a variable that holds a list of strings. Use the correct `:type`.
3. Create a counter using `setq` that increments each time you call a function. Make the function interactive.
4. Open two buffers. Set a buffer-local variable in one and verify it is not visible in the other.
5. Explain why `defvar` does not overwrite an existing value. When is this useful?
