# Chapter 0: Before You Start

[Chapter 1: Hello Elisp →](chapter-01-hello.md)

---

## The Story

You just switched to Emacs. You've learned the keybindings, you can navigate files, you've installed a few packages. But every day, you hit a moment where you think:

"I wish Emacs would just..."

- ...greet me with today's agenda when it starts
- ...toggle between my coding font and my writing font
- ...auto-format on save but only for Go files
- ...have a keybinding that opens my three most-used files
- ...highlight my custom TODO markers in a specific color

In any other editor, you'd file a feature request and wait. In Emacs, you write it yourself. That's the deal: Emacs is a Lisp interpreter that happens to edit text. Every feature — from syntax highlighting to version control — is Elisp code you can read, modify, and extend.

Over 14 chapters, you'll go from "I don't know Lisp" to "I just wrote a minor mode and published it to MELPA." Each chapter starts with a wish — something you want Emacs to do — and ends with working Elisp that makes it happen.

## What Is Emacs Lisp?

Emacs Lisp (Elisp) is a dialect of Lisp designed specifically for extending Emacs. It's:

- **Dynamically typed** — variables can hold any type
- **Interpreted** (mostly) — evaluate code instantly, see results immediately
- **Homoiconic** — code is data (lists), data is code
- **Deeply integrated** — every Emacs feature is an Elisp function you can call

### The Syntax in 30 Seconds

```elisp
;; Everything is a list. The first element is the function.
(+ 1 2)          ; → 3
(message "Hi")   ; → prints "Hi" in the echo area

;; Define a function
(defun greet (name)
  "Say hello to NAME."
  (message "Hello, %s!" name))

;; Call it
(greet "world")  ; → "Hello, world!"

;; Variables
(setq my-name "Emacs User")
(message "I am %s" my-name)
```

If you've never written Lisp, the parentheses look weird for about 30 minutes. Then they become invisible. The structure is always the same: `(function arg1 arg2 ...)`.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Developer | Impatient. Wants Emacs to read your mind. |
| **`*scratch*`** | The scratch buffer | Your Elisp playground. Always there. |
| **`C-h f`** | Help system | Knows every function. Ask it constantly. |
| **init.el** | Your config file | Grows from 5 lines to 500. Lovingly. |

## Prerequisites

### Emacs 29+

```bash
emacs --version
# GNU Emacs 29.x or higher
```

Emacs 29 includes native compilation (for speed), built-in `use-package`, and tree-sitter support. Earlier versions work for most chapters, but 29+ is recommended.

### The *scratch* Buffer

When Emacs starts, it creates a buffer called `*scratch*`. This is your Elisp REPL:

1. Type an expression: `(+ 1 2)`
2. Put your cursor at the end of the expression
3. Press `C-x C-e` (eval-last-sexp)
4. See the result in the echo area: `3`

This is how you'll test every piece of code in this course. Write it in `*scratch*`, evaluate it, see what happens.

### Essential Keybindings

| Key | Command | What it does |
|---|---|---|
| `C-x C-e` | eval-last-sexp | Evaluate expression before cursor |
| `C-M-x` | eval-defun | Evaluate the entire function at point |
| `M-x eval-buffer` | eval-buffer | Evaluate the entire buffer |
| `C-h f` | describe-function | Look up any function |
| `C-h v` | describe-variable | Look up any variable |
| `C-h k` | describe-key | What does this key do? |
| `M-x ielm` | ielm | Interactive Elisp REPL |

### Your init.el

Your Emacs configuration lives in `~/.emacs.d/init.el` (or `~/.config/emacs/init.el`). Every customization you write in this course will eventually live there.

```elisp
;; ~/.emacs.d/init.el
;; Your customizations go here
```

## The Learning Loop

Every chapter:

1. **The wish** — "I want Emacs to do X"
2. **The exploration** — find relevant functions with `C-h f`, read docs
3. **The implementation** — write Elisp in `*scratch*`, test interactively
4. **The integration** — add to init.el, make it permanent

## The Roadmap

| Ch | The Wish | The Elisp |
|---|---|---|
| 1 | Greeting on startup | defun, message, init.el |
| 2 | Toggle font size | setq, let, defvar |
| 3 | Different behavior per file type | if, cond, when |
| 4 | Recent projects list | Lists, cons, car, cdr |
| 5 | Custom M-x commands | interactive, completing-read |
| 6 | Auto-arrange workspace | Buffer and window API |
| 7 | Format on save | Hooks and advice |
| 8 | Custom prefix key | Keymaps |
| 9 | Bulk rename in region | Text manipulation |
| 10 | Custom highlighting | Regex, overlays |
| 11 | Toggleable writing mode | Minor modes |
| 12 | Syntax for my DSL | Major modes |
| 13 | Share with the world | Package creation |
| 14 | Run builds async | Processes and async |

Let's make Emacs say hello.

---

[Chapter 1: Hello Elisp →](chapter-01-hello.md)
