# Chapter 2: Functions

[prev: Basics](chapter-01-basics.md) | [next: Variables](chapter-03-variables.md)

## Defining Functions with defun

```elisp
(defun greet (name)
  "Return a greeting for NAME."
  (concat "Hello, " name "!"))

(greet "Emacs")  ;; => "Hello, Emacs!"
```

The structure is: `(defun NAME ARGLIST DOCSTRING BODY...)`.

## Docstrings

The first string after the argument list is the docstring. It appears in `C-h f`:

```elisp
(defun square (n)
  "Return N multiplied by itself."
  (* n n))

(square 5)  ;; => 25
```

## Lambda (Anonymous Functions)

```elisp
(lambda (x) (* x x))  ;; => a function object

(funcall (lambda (x) (* x x)) 4)  ;; => 16
```

## Interactive Functions (Commands)

Adding `(interactive)` makes a function callable via `M-x`:

```elisp
(defun say-hello ()
  "Display a greeting in the echo area."
  (interactive)
  (message "Hello from Elisp!"))
```

Now `M-x say-hello` works.

## Arguments

### Required arguments

```elisp
(defun add (a b)
  (+ a b))

(add 3 4)  ;; => 7
```

### Optional arguments

```elisp
(defun greet (name &optional greeting)
  "Greet NAME with optional GREETING."
  (concat (or greeting "Hello") ", " name "!"))

(greet "World")          ;; => "Hello, World!"
(greet "World" "Hi")     ;; => "Hi, World!"
```

### Rest arguments

```elisp
(defun sum (&rest numbers)
  "Sum all NUMBERS."
  (apply #'+ numbers))

(sum 1 2 3 4)  ;; => 10
```

### Keyword arguments (with cl-lib)

```elisp
(require 'cl-lib)

(cl-defun make-person (&key name age)
  (list :name name :age age))

(make-person :name "Alice" :age 30)
;; => (:name "Alice" :age 30)
```

## Calling Functions: funcall and apply

`funcall` calls a function with individual arguments. `apply` spreads a list as arguments:

```elisp
(funcall #'+ 1 2 3)       ;; => 6
(apply #'+ '(1 2 3))      ;; => 6
(apply #'+ 1 2 '(3 4))    ;; => 10
```

The `#'` (sharp-quote) is shorthand for `(function ...)`, which refers to a function by name:

```elisp
#'car    ;; => the function object for car
```

## Higher-Order Functions

### mapcar — apply function to each element

```elisp
(mapcar #'1+ '(1 2 3 4))          ;; => (2 3 4 5)
(mapcar #'upcase '("hi" "there")) ;; => ("HI" "THERE")
(mapcar (lambda (x) (* x x)) '(1 2 3))  ;; => (1 4 9)
```

### seq-filter — keep elements matching predicate

```elisp
(require 'seq)

(seq-filter #'cl-evenp '(1 2 3 4 5 6))  ;; => (2 4 6)
(seq-filter (lambda (s) (> (length s) 3))
            '("hi" "hello" "hey" "world"))
;; => ("hello" "world")
```

### seq-reduce — fold/accumulate

```elisp
(seq-reduce #'+ '(1 2 3 4) 0)      ;; => 10
(seq-reduce (lambda (acc x) (concat acc " " x))
            '("world" "from" "elisp")
            "hello")
;; => "hello world from elisp"
```

## Lexical vs Dynamic Binding

Emacs Lisp historically uses dynamic binding. Modern Elisp files should enable lexical binding:

```elisp
;;; -*- lexical-binding: t; -*-
```

### Dynamic binding (default in old code)

The variable is looked up in the call stack:

```elisp
(defvar x 10)

(defun show-x ()
  x)

(defun dynamic-example ()
  (let ((x 99))
    (show-x)))

(dynamic-example)  ;; => 99 (dynamic: show-x sees caller's x)
```

### Lexical binding

The variable is looked up where the function was defined:

```elisp
;; With lexical-binding: t

(defun make-adder (n)
  (lambda (x) (+ x n)))

(funcall (make-adder 5) 3)  ;; => 8 (n is captured as 5)
```

With dynamic binding, closures like `make-adder` would not work correctly.

Always add `;;; -*- lexical-binding: t; -*-` as the first line of your Elisp files.

## Exercises

1. Write a function `factorial` that computes n! recursively.
2. Write a function `my-filter` that takes a predicate and a list, returning elements where the predicate returns non-nil. Do not use `seq-filter`.
3. Use `mapcar` with a lambda to double every number in a list.
4. Write a `make-multiplier` function that returns a closure. `(funcall (make-multiplier 3) 7)` should return 21.
5. Make `factorial` interactive so that `M-x factorial` prompts for a number and displays the result with `message`.
