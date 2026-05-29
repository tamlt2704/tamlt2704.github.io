# Chapter 4: Control Flow

[prev: Variables](chapter-03-variables.md) | [next: Data Structures](chapter-05-data-structures.md)

## if

`if` takes a condition, a then-form, and optional else-forms:

```elisp
(if (> 5 3)
    "yes"
  "no")
;; => "yes"

(if nil
    "never"
  "else1"
  "else2")
;; => "else2" (multiple else forms allowed, last value returned)
```

Note: `if` only allows one then-form. Use `progn` for multiple:

```elisp
(if t
    (progn
      (message "first")
      (message "second"))
  "else")
```

## when and unless

`when` is `if` without else, allowing multiple body forms:

```elisp
(when (> 5 3)
  (message "five is greater")
  "result")
;; => "result"
```

`unless` is the opposite — executes body when condition is nil:

```elisp
(unless (> 1 10)
  (message "1 is not greater than 10")
  "correct")
;; => "correct"
```

## cond

`cond` is a multi-branch conditional:

```elisp
(defun describe-number (n)
  (cond
   ((< n 0) "negative")
   ((= n 0) "zero")
   ((< n 10) "small positive")
   (t "large positive")))

(describe-number -5)  ;; => "negative"
(describe-number 0)   ;; => "zero"
(describe-number 7)   ;; => "small positive"
(describe-number 42)  ;; => "large positive"
```

## pcase — Pattern Matching

`pcase` is a powerful pattern matcher:

```elisp
(defun describe-value (val)
  (pcase val
    (0 "zero")
    ((pred stringp) "a string")
    ((pred listp) "a list")
    (`(,a ,b) (format "pair: %s and %s" a b))
    (_ "something else")))

(describe-value 0)         ;; => "zero"
(describe-value "hi")      ;; => "a string"
(describe-value '(1 2))    ;; => "pair: 1 and 2"
(describe-value 42)        ;; => "something else"
```

### Backquote patterns

```elisp
(pcase '(error 404 "not found")
  (`(error ,code ,msg)
   (format "Error %d: %s" code msg))
  (`(ok ,result)
   (format "Success: %s" result)))
;; => "Error 404: not found"
```

### pcase-let

```elisp
(pcase-let ((`(,first ,second . ,rest) '(1 2 3 4 5)))
  (list first second rest))
;; => (1 2 (3 4 5))
```

## while

```elisp
(let ((i 0)
      (result '()))
  (while (< i 5)
    (push i result)
    (setq i (1+ i)))
  (nreverse result))
;; => (0 1 2 3 4)
```

## dolist

Iterate over a list:

```elisp
(let ((sum 0))
  (dolist (x '(1 2 3 4 5))
    (setq sum (+ sum x)))
  sum)
;; => 15
```

`dolist` can have a result form:

```elisp
(let (result)
  (dolist (x '(1 2 3) (nreverse result))
    (push (* x x) result)))
;; => (1 4 9)
```

## dotimes

Iterate a fixed number of times:

```elisp
(let (result)
  (dotimes (i 5 (nreverse result))
    (push i result)))
;; => (0 1 2 3 4)
```

## catch/throw — Non-Local Exit

`catch` sets up a tag. `throw` jumps back to it:

```elisp
(catch 'found
  (dolist (x '(1 2 3 4 5))
    (when (= x 3)
      (throw 'found (format "found %d" x))))
  "not found")
;; => "found 3"
```

## condition-case — Error Handling

```elisp
(condition-case err
    (/ 10 0)
  (arith-error
   (format "Math error: %s" (error-message-string err)))
  (error
   (format "Generic error: %s" err)))
;; => "Math error: Arithmetic error"
```

### Signaling errors

```elisp
(defun safe-divide (a b)
  (if (zerop b)
      (error "Division by zero: %d / %d" a b)
    (/ a b)))

(condition-case err
    (safe-divide 10 0)
  (error (error-message-string err)))
;; => "Division by zero: 10 / 0"
```

## unwind-protect

Guarantees cleanup code runs even if an error occurs (like try/finally):

```elisp
(defun safe-file-read (filename)
  (let ((buf (find-file-noselect filename)))
    (unwind-protect
        (with-current-buffer buf
          (buffer-string))
      (kill-buffer buf))))
```

## cl-loop

`cl-loop` provides a rich iteration macro (from `cl-lib`):

```elisp
(require 'cl-lib)

;; Collect squares
(cl-loop for i from 1 to 5
         collect (* i i))
;; => (1 4 9 16 25)

;; Sum with condition
(cl-loop for i from 1 to 10
         when (cl-evenp i)
         sum i)
;; => 30

;; Iterate over list with index
(cl-loop for x in '("a" "b" "c")
         for i from 0
         collect (format "%d:%s" i x))
;; => ("0:a" "1:b" "2:c")

;; While with accumulation
(cl-loop for i from 1
         while (< (* i i) 50)
         collect i)
;; => (1 2 3 4 5 6 7)
```

## Exercises

1. Write a function using `cond` that returns "fizz" for multiples of 3, "buzz" for multiples of 5, "fizzbuzz" for multiples of both, and the number as a string otherwise.
2. Use `pcase` to destructure a list like `(name age city)` and format it as a sentence.
3. Write a `find-first` function using `catch`/`throw` that returns the first element in a list matching a predicate.
4. Write a function that reads a file safely using `unwind-protect`, ensuring the buffer is killed even if an error occurs.
5. Use `cl-loop` to generate the first 10 Fibonacci numbers.
