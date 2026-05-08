# Chapter 10: Regular Expressions

[← Chapter 9: Text Manipulation](chapter-09-text.md) | [Chapter 11: Minor Modes →](chapter-11-minor-modes.md)

---

## The Wish

"I want to highlight TODO, FIXME, and HACK comments in my own colors — not the default font-lock way, but my custom overlays that I can toggle on and off."

## Elisp Regex Syntax

Elisp regex is similar to POSIX but with extra backslash escaping (because strings already use `\`):

```elisp
;; In Elisp strings, you double-escape:
"\\b"        ; word boundary (regex \b)
"\\("        ; group start (regex \()
"\\|"        ; alternation (regex \|)
"\\w+"       ; one or more word chars
"[0-9]+"     ; one or more digits (no extra escaping)
".*"         ; any chars (greedy)
```

### Quick Reference

| Pattern | Elisp String | Matches |
|---|---|---|
| Literal dot | `"\\."` | `.` |
| Group | `"\\(foo\\)"` | Captures "foo" |
| Alternation | `"foo\\|bar"` | "foo" or "bar" |
| Word boundary | `"\\b"` | Edge of a word |
| Word char | `"\\w"` | Letter, digit, underscore |
| Non-word | `"\\W"` | Anything else |
| Start of line | `"^"` | Beginning of line |
| End of line | `"$"` | End of line |
| Shy group | `"\\(?:foo\\)"` | Group without capture |

## Searching in Buffers

```elisp
;; search-forward: literal search
(search-forward "TODO" nil t)    ; Move to next "TODO", return point or nil

;; re-search-forward: regex search
(re-search-forward "\\(TODO\\|FIXME\\|HACK\\)" nil t)

;; Arguments: REGEXP BOUND NOERROR
;; BOUND: don't search past this position (nil = end of buffer)
;; NOERROR: t = return nil instead of signaling error

;; After a match, access groups:
(match-string 0)    ; Entire match
(match-string 1)    ; First capture group
(match-beginning 0) ; Start position of match
(match-end 0)       ; End position of match
```

## Replacing with Regex

```elisp
;; Replace all matches in buffer
(save-excursion
  (goto-char (point-min))
  (while (re-search-forward "\\bvar\\b" nil t)
    (replace-match "const")))

;; Replace with backreferences
(save-excursion
  (goto-char (point-min))
  (while (re-search-forward "\\(\\w+\\)_\\(\\w+\\)" nil t)
    ;; snake_case → camelCase
    (replace-match (concat (match-string 1)
                           (capitalize (match-string 2))))))
```

## String Matching

```elisp
;; Check if string matches regex
(string-match "^[0-9]+" "42abc")     ; → 0 (match at position 0)
(string-match "^[0-9]+" "abc42")     ; → nil (no match at start)

;; Extract from string
(when (string-match "v\\([0-9.]+\\)" "emacs v29.1")
  (match-string 1 "emacs v29.1"))    ; → "29.1"

;; replace-regexp-in-string (for strings, not buffers)
(replace-regexp-in-string
 "\\([a-z]\\)\\([A-Z]\\)"           ; camelCase boundary
 "\\1_\\2"                           ; insert underscore
 "myVariableName")                   ; → "my_Variable_Name"
```

## Overlays: Visual Annotations

Overlays attach visual properties to buffer regions without modifying the text:

```elisp
;; Create an overlay
(let ((ov (make-overlay BEG END)))
  (overlay-put ov 'face '(:background "yellow"))
  (overlay-put ov 'my-type 'highlight))  ; Custom property for tracking

;; Remove overlays
(remove-overlays (point-min) (point-max) 'my-type 'highlight)

;; List overlays at point
(overlays-at (point))
```

## Practical: Custom TODO Highlighter

```elisp
(defvar my-todo-keywords
  '(("TODO"  . '(:foreground "orange" :weight bold))
    ("FIXME" . '(:foreground "red" :weight bold))
    ("HACK"  . '(:foreground "purple" :weight bold))
    ("NOTE"  . '(:foreground "green" :weight bold)))
  "Keywords and their faces for highlighting.")

(defun my-highlight-todos ()
  "Add overlays to TODO/FIXME/HACK keywords in current buffer."
  (interactive)
  (my-clear-todo-highlights)
  (save-excursion
    (dolist (entry my-todo-keywords)
      (let ((keyword (car entry))
            (face (cdr entry)))
        (goto-char (point-min))
        (while (re-search-forward (concat "\\b" keyword "\\b") nil t)
          (let ((ov (make-overlay (match-beginning 0) (match-end 0))))
            (overlay-put ov 'face face)
            (overlay-put ov 'my-todo t)))))))

(defun my-clear-todo-highlights ()
  "Remove all TODO highlight overlays."
  (interactive)
  (remove-overlays (point-min) (point-max) 'my-todo t))

(defun my-toggle-todo-highlights ()
  "Toggle TODO highlighting in current buffer."
  (interactive)
  (if (seq-find (lambda (ov) (overlay-get ov 'my-todo))
                (overlays-in (point-min) (point-max)))
      (my-clear-todo-highlights)
    (my-highlight-todos)))
```

## Practical: Jump Between TODOs

```elisp
(defun my-next-todo ()
  "Jump to the next TODO/FIXME/HACK comment."
  (interactive)
  (let ((pattern "\\b\\(TODO\\|FIXME\\|HACK\\)\\b"))
    (if (re-search-forward pattern nil t)
        (goto-char (match-beginning 0))
      (message "No more TODOs found"))))

(defun my-prev-todo ()
  "Jump to the previous TODO/FIXME/HACK comment."
  (interactive)
  (let ((pattern "\\b\\(TODO\\|FIXME\\|HACK\\)\\b"))
    (if (re-search-backward pattern nil t)
        (goto-char (match-beginning 0))
      (message "No previous TODOs found"))))
```

## rx: Readable Regex (Emacs 27+)

The `rx` macro lets you write regex in s-expression form:

```elisp
;; These are equivalent:
"\\b\\(TODO\\|FIXME\\)\\b:\\s-*\\(.+\\)"

(rx word-boundary
    (group (or "TODO" "FIXME"))
    word-boundary
    ":" (zero-or-more space)
    (group (one-or-more anything)))
```

`rx` is easier to read and maintain for complex patterns.

## Exercises

1. Write a function that finds all email addresses in the current buffer and lists them in a new buffer.
2. Create a command that converts `snake_case` identifiers to `camelCase` in the region.
3. Build a regex that matches ISO dates (`2024-01-15`) and highlights them with overlays.

## What You Learned

- **Elisp regex escaping** — double backslashes in strings
- **`re-search-forward`** — find patterns in buffers
- **`match-string`** — extract captured groups after a match
- **`replace-regexp-in-string`** — regex replace in strings
- **Overlays** — visual annotations without changing text
- **`rx`** — s-expression regex syntax for readability

You've got highlighting, navigation, and keybindings. But they're scattered across functions. What if you could bundle them into a toggleable mode? That's a minor mode.

---

[← Chapter 9: Text Manipulation](chapter-09-text.md) | [Chapter 11: Minor Modes →](chapter-11-minor-modes.md)
