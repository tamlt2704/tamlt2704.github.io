# Chapter 1: Hello Elisp

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Variables and State →](chapter-02-variables.md)

---

## The Wish

"I want Emacs to greet me when it starts. Something like 'Good morning, here are your 3 open projects.' A small thing, but it makes Emacs feel like *mine*."

## The Exploration

First question: how do you display a message in Emacs?

Press `C-h f` (describe-function), type `message`:

```
message is a built-in function in 'C source code'.

(message FORMAT-STRING &rest ARGS)

Display a message at the bottom of the screen (the echo area).
The message also goes into the *Messages* buffer.
```

Let's try it. In the `*scratch*` buffer:

```elisp
(message "Hello, Emacs!")
```

Put your cursor after the closing paren. Press `C-x C-e`. The echo area shows: `"Hello, Emacs!"`

That's it. You just wrote and executed Elisp.

## Defining a Function

A greeting that just says "Hello" is boring. Let's make it useful:

```elisp
(defun my-greeting ()
  "Display a greeting with the current time."
  (let ((hour (string-to-number (format-time-string "%H"))))
    (cond
     ((< hour 12) (message "Good morning! Time to code."))
     ((< hour 17) (message "Good afternoon! Keep shipping."))
     (t           (message "Good evening! One more commit?")))))
```

### Breaking It Down

```elisp
(defun my-greeting ()          ; Define a function named my-greeting, no arguments
  "Display a greeting..."      ; Docstring (optional but good practice)
  (let ((hour ...))            ; Local variable binding
    (cond                      ; Multi-branch conditional
     ((< hour 12) ...)         ; If hour < 12
     ((< hour 17) ...)         ; Else if hour < 17
     (t ...))))                ; Else (t = true = default)
```

Evaluate it with `C-x C-e`, then call it:

```elisp
(my-greeting)
```

`C-x C-e` → `"Good afternoon! Keep shipping."` (or whatever time it is).

## Making It Run on Startup

Emacs reads `~/.emacs.d/init.el` (or `~/.config/emacs/init.el`) every time it starts. Add your function there:

```elisp
;; ~/.emacs.d/init.el

(defun my-greeting ()
  "Display a greeting with the current time."
  (let ((hour (string-to-number (format-time-string "%H"))))
    (cond
     ((< hour 12) (message "Good morning! Time to code."))
     ((< hour 17) (message "Good afternoon! Keep shipping."))
     (t           (message "Good evening! One more commit?")))))

;; Run it when Emacs finishes loading
(add-hook 'emacs-startup-hook #'my-greeting)
```

`add-hook` attaches your function to an event. `emacs-startup-hook` fires after init.el finishes loading. Now every time Emacs starts, you get a greeting.

## Format Strings

`message` supports printf-style formatting:

```elisp
(message "Hello, %s!" "world")           ; → "Hello, world!"
(message "You have %d buffers" 42)       ; → "You have 42 buffers"
(message "%s has %d items" "list" 5)     ; → "list has 5 items"
```

| Format | Type |
|---|---|
| `%s` | String |
| `%d` | Integer |
| `%f` | Float |
| `%S` | Any Lisp object (printed representation) |

## A Better Greeting: With Context

Let's make the greeting actually useful — show how many buffers are open:

```elisp
(defun my-greeting ()
  "Greet with time and buffer count."
  (let ((hour (string-to-number (format-time-string "%H")))
        (buf-count (length (buffer-list)))
        (greeting (cond
                   ((< hour 12) "Good morning")
                   ((< hour 17) "Good afternoon")
                   (t "Good evening"))))
    (message "%s! You have %d buffers open." greeting buf-count)))
```

## The Evaluation Model

Understanding how Elisp evaluates expressions:

```elisp
(+ 1 2)
; 1. See a list → it's a function call
; 2. First element: + (the function)
; 3. Remaining elements: 1, 2 (the arguments)
; 4. Call (+ 1 2) → 3

(message "Hi %s" (user-login-name))
; 1. See a list → function call
; 2. First element: message
; 3. Arguments: "Hi %s" and (user-login-name)
; 4. Evaluate (user-login-name) first → "yourname"
; 5. Call (message "Hi %s" "yourname") → "Hi yourname"
```

Everything is a list. The first element is always the function. Arguments are evaluated before the function is called (most of the time — special forms like `if` and `let` are exceptions).

## Useful Functions to Know

```elisp
;; Current user
(user-login-name)        ; → "alice"
(user-full-name)         ; → "Alice Smith"

;; Time
(current-time-string)    ; → "Thu May  7 14:30:00 2026"
(format-time-string "%Y-%m-%d")  ; → "2026-05-07"

;; Buffers
(buffer-list)            ; → list of all buffers
(length (buffer-list))   ; → number of buffers
(buffer-name)            ; → name of current buffer

;; System
(emacs-version)          ; → "GNU Emacs 29.1..."
(system-name)            ; → your hostname
```

## The Complete Startup Greeting

```elisp
(defun my-startup-greeting ()
  "Show a useful greeting on Emacs startup."
  (let* ((hour (string-to-number (format-time-string "%H")))
         (name (user-login-name))
         (bufs (length (buffer-list)))
         (time-greeting (cond
                         ((< hour 6)  "Burning the midnight oil")
                         ((< hour 12) "Good morning")
                         ((< hour 17) "Good afternoon")
                         ((< hour 21) "Good evening")
                         (t           "Late night coding"))))
    (message "%s, %s! Emacs ready with %d buffers." time-greeting name bufs)))

(add-hook 'emacs-startup-hook #'my-startup-greeting)
```

`let*` (with asterisk) lets later bindings reference earlier ones. Regular `let` evaluates all bindings in parallel.

## Exercises

1. Modify the greeting to include today's day of the week. (Hint: `(format-time-string "%A")` returns "Monday", "Tuesday", etc.)

2. Write a function `my-buffer-summary` that prints how many `.el` files, `.py` files, and other files you have open. (Hint: `buffer-file-name` returns the file path of a buffer, or nil.)

3. Add a random motivational quote to your greeting. (Hint: use `nth` and `random` with a list of strings.)

## What You Learned

- **`(message ...)`** — display text in the echo area
- **`(defun name (args) "doc" body)`** — define a function
- **`C-x C-e`** — evaluate the expression before cursor
- **`let` / `let*`** — local variable bindings
- **`cond`** — multi-branch conditional
- **`add-hook`** — attach a function to an event
- **init.el** — runs on every Emacs startup

You've written your first Elisp function and made it run automatically. But the greeting always uses the same font size. What if you want to toggle between a coding font (small) and a presentation font (large)? That requires variables and state.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Variables and State →](chapter-02-variables.md)
