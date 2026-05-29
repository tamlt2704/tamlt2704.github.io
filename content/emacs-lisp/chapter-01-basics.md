# Chapter 1: Basics

[prev: Overview](chapter-00-overview.md) | [next: Functions](chapter-02-functions.md)

## S-Expressions

Everything in Elisp is an S-expression (symbolic expression). An S-expression is either an atom or a list.

```elisp
42              ;; atom: a number
"hello"         ;; atom: a string
foo             ;; atom: a symbol
(+ 1 2)        ;; list: function call
(list 1 2 3)   ;; list: function call that returns a list
```

## Atoms

Atoms are the simplest elements:

```elisp
;; Numbers
42          ;; => 42
3.14        ;; => 3.14
#xFF        ;; => 255 (hexadecimal)

;; Strings
"hello world"       ;; => "hello world"
"line1\nline2"      ;; => "line1\nline2" (with newline)

;; Symbols
buffer-file-name    ;; a symbol (used as variable name)
'my-symbol          ;; a quoted symbol (evaluates to itself)
```

## Evaluation

When Emacs evaluates an S-expression:

- Numbers and strings evaluate to themselves
- Symbols evaluate to their variable value
- Lists evaluate as function calls: first element is the function, rest are arguments

```elisp
(+ 2 3)            ;; => 5
(* 4 5)            ;; => 20
(concat "hi" " " "there")  ;; => "hi there"
```

How to evaluate:

- `C-x C-e` — evaluate expression before cursor, result in echo area
- `M-:` — type an expression in the minibuffer to evaluate
- `C-j` in `*scratch*` — evaluate and insert result below

## Quoting

A quote prevents evaluation. The expression is returned as-is:

```elisp
(+ 1 2)    ;; => 3 (evaluated)
'(+ 1 2)   ;; => (+ 1 2) (not evaluated, returns the list)

'foo       ;; => foo (the symbol itself, not its value)
```

`quote` is the long form:

```elisp
(quote foo)      ;; => foo
(quote (1 2 3))  ;; => (1 2 3)
```

## Comments

```elisp
;; This is a comment (convention: two semicolons for line comments)
;;; This is a section heading (three semicolons)

(+ 1 2) ; inline comment (one semicolon)
```

## Types

Elisp has these fundamental types:

```elisp
;; Integer
42              ;; => 42
most-positive-fixnum  ;; => 2305843009213693951 (on 64-bit)

;; Float
3.14            ;; => 3.14
1e10            ;; => 10000000000.0

;; String
"hello"         ;; => "hello"

;; Symbol
'my-symbol      ;; => my-symbol

;; Cons cell (a pair)
(cons 1 2)      ;; => (1 . 2)

;; List (chain of cons cells ending in nil)
(list 1 2 3)    ;; => (1 2 3)
'(a b c)        ;; => (a b c)

;; Vector (fixed-size array)
[1 2 3]         ;; => [1 2 3]

;; nil and t
nil             ;; => nil (false, empty list)
t               ;; => t (true)
()              ;; => nil (empty list is nil)
```

## Type Checking

```elisp
(integerp 42)       ;; => t
(floatp 3.14)       ;; => t
(stringp "hi")      ;; => t
(symbolp 'foo)      ;; => t
(consp '(1 . 2))    ;; => t
(listp '(1 2))      ;; => t
(vectorp [1 2])     ;; => t
(null nil)          ;; => t
(numberp 3.14)      ;; => t (integer or float)
```

## Truthiness

In Elisp, only `nil` is false. Everything else is true:

```elisp
(if nil "yes" "no")     ;; => "no"
(if 0 "yes" "no")       ;; => "yes" (0 is truthy!)
(if "" "yes" "no")      ;; => "yes" (empty string is truthy!)
(if '() "yes" "no")     ;; => "no" ('() is nil)
```

## Exercises

1. Evaluate `(+ (* 3 4) (- 10 5))` and predict the result before checking.
2. What is the difference between `(list 1 2 3)` and `'(1 2 3)`? (Hint: try `(list (+ 1 1) 3)` vs `'((+ 1 1) 3)`)
3. Write an expression that creates a cons cell with `"hello"` as car and `"world"` as cdr.
4. Use `type-of` to check the types of: `42`, `3.14`, `"hi"`, `'foo`, `nil`, `t`, `[1 2]`.
5. Why does `(if 0 "true" "false")` return `"true"`?
