# Chapter 4: Lists and Cons Cells

[← Chapter 3: Conditionals](chapter-03-conditionals.md) | [Chapter 5: Interactive Commands →](chapter-05-interactive.md)

---

## The Wish

"I want a recent-projects list that I can push to, pop from, and search through. Something like a personal project switcher that remembers where I've been."

## The Cons Cell: Elisp's Building Block

Everything in Elisp is built from cons cells — pairs of two values:

```elisp
(cons 1 2)          ; → (1 . 2)  — a "dotted pair"
(cons 'a 'b)       ; → (a . b)
```

A list is just a chain of cons cells where each cdr points to the next cell, ending in nil:

```elisp
(cons 1 (cons 2 (cons 3 nil)))  ; → (1 2 3)
(list 1 2 3)                     ; → (1 2 3) — shorthand
'(1 2 3)                         ; → (1 2 3) — quoted literal
```

## car and cdr: Accessing Parts

```elisp
(car '(a b c))     ; → a         (first element)
(cdr '(a b c))     ; → (b c)     (rest of the list)
(cadr '(a b c))    ; → b         (car of cdr = second)
(caddr '(a b c))   ; → c         (third)
```

Modern aliases (Emacs 25+):

```elisp
(nth 0 '(a b c))   ; → a
(nth 2 '(a b c))   ; → c
(last '(a b c))    ; → (c)       (last cons cell)
(length '(a b c))  ; → 3
```

## Quote: Preventing Evaluation

Without quote, Elisp tries to call the first element as a function:

```elisp
(1 2 3)            ; ERROR: 1 is not a function
'(1 2 3)           ; → (1 2 3) — data, not code
(quote (1 2 3))    ; → (1 2 3) — same thing
```

Use `list` when elements need evaluation:

```elisp
(setq x 10)
'(x 20 30)        ; → (x 20 30) — symbol x, not its value
(list x 20 30)    ; → (10 20 30) — evaluates x
```

## Building Lists

```elisp
;; push adds to the front (destructive)
(setq my-list '(b c))
(push 'a my-list)       ; my-list → (a b c)

;; append joins lists (non-destructive, returns new list)
(append '(1 2) '(3 4))  ; → (1 2 3 4)

;; add-to-list adds only if not present
(setq my-list '(a b c))
(add-to-list 'my-list 'd)  ; my-list → (d a b c)
(add-to-list 'my-list 'a)  ; my-list → (d a b c) — no duplicate
```

## Searching and Filtering

```elisp
;; member: find element (uses equal)
(member "foo" '("foo" "bar" "baz"))  ; → ("foo" "bar" "baz")
(member "nope" '("foo" "bar"))       ; → nil

;; assoc: lookup in alist (association list)
(setq projects '(("blog" . "~/code/blog")
                 ("api"  . "~/code/api")
                 ("dots" . "~/dotfiles")))
(assoc "api" projects)    ; → ("api" . "~/code/api")
(cdr (assoc "api" projects))  ; → "~/code/api"

;; seq-filter (Emacs 25+): keep matching elements
(seq-filter #'cl-evenp '(1 2 3 4 5 6))  ; → (2 4 6)

;; seq-remove: drop matching elements
(seq-remove #'cl-evenp '(1 2 3 4 5 6))  ; → (1 3 5)
```

## Mapping Over Lists

```elisp
;; mapcar: apply function to each element, collect results
(mapcar #'upcase '("hello" "world"))  ; → ("HELLO" "WORLD")
(mapcar #'1+ '(1 2 3))               ; → (2 3 4)

;; dolist: loop for side effects
(dolist (item '("one" "two" "three"))
  (message "Item: %s" item))

;; seq-map with lambda
(seq-map (lambda (p) (car p)) projects)  ; → ("blog" "api" "dots")
```

## Practical: Recent Projects List

```elisp
(defvar my-recent-projects '()
  "List of recently visited project directories.")

(defvar my-recent-projects-max 10
  "Maximum number of projects to remember.")

(defun my-project-add (dir)
  "Add DIR to the front of recent projects list."
  (setq my-recent-projects
        (delete dir my-recent-projects))  ; Remove if already present
  (push dir my-recent-projects)
  ;; Trim to max length
  (when (> (length my-recent-projects) my-recent-projects-max)
    (setcdr (nthcdr (1- my-recent-projects-max) my-recent-projects) nil)))

(defun my-project-switch ()
  "Switch to a recent project."
  (interactive)
  (let ((project (completing-read "Project: " my-recent-projects)))
    (when project
      (dired project))))

;; Auto-track projects when opening files
(defun my-project-track ()
  "Track the current file's project root."
  (when-let ((root (project-root (project-current))))
    (my-project-add root)))

(add-hook 'find-file-hook #'my-project-track)
```

## Destructuring with pcase-let

```elisp
;; Pull apart a list in one step
(pcase-let ((`(,first ,second . ,rest) '(a b c d e)))
  (message "first=%s second=%s rest=%s" first second rest))
;; → "first=a second=b rest=(c d e)"

;; Useful for alist entries
(pcase-let ((`(,name . ,path) (assoc "blog" projects)))
  (message "Opening %s at %s" name path))
```

## Exercises

1. Write a function `my-rotate-list` that moves the first element to the end.
2. Create an alist mapping file extensions to modes, then write a lookup function.
3. Implement a simple stack (push/pop/peek) using a list variable.

## What You Learned

- **cons cells** — the pair that builds all lists
- **car / cdr** — access first element and rest
- **quote** — prevent evaluation, treat code as data
- **push / append / add-to-list** — build lists
- **assoc / member** — search lists
- **mapcar / dolist / seq-filter** — iterate and transform
- **Alists** — key-value pairs as lists of cons cells

You have a project list, but you can only use it from Elisp. Next: making it a proper M-x command anyone can invoke.

---

[← Chapter 3: Conditionals](chapter-03-conditionals.md) | [Chapter 5: Interactive Commands →](chapter-05-interactive.md)
