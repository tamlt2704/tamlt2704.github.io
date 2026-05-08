# Chapter 9: Text Manipulation

[← Chapter 8: Keymaps](chapter-08-keymaps.md) | [Chapter 10: Regular Expressions →](chapter-10-regex.md)

---

## The Wish

"I want to bulk-rename variables in a region — select some code, run my command, and replace every occurrence of `oldName` with `newName` within just that selection."

## Point, Mark, and Region

```elisp
(point)             ; Current cursor position (integer)
(point-min)         ; Start of buffer (usually 1)
(point-max)         ; End of buffer
(mark)              ; The mark position (other end of selection)
(region-beginning)  ; Start of selected region
(region-end)        ; End of selected region
(region-active-p)   ; Is there an active selection?
```

Point is a position between characters, starting at 1.

## Moving Point

```elisp
(goto-char (point-min))       ; Jump to start of buffer
(goto-char 100)               ; Jump to position 100
(forward-char 5)              ; Move 5 chars forward
(backward-char 3)             ; Move 3 chars back
(forward-line 1)              ; Move to next line
(beginning-of-line)           ; Jump to line start
(end-of-line)                 ; Jump to line end
(forward-word 2)              ; Skip 2 words forward
```

## Reading Text

```elisp
;; Get text from buffer
(buffer-substring BEG END)                ; With text properties (font, face)
(buffer-substring-no-properties BEG END)  ; Plain text only

;; Get current line
(thing-at-point 'line t)      ; Current line as string
(thing-at-point 'word t)      ; Word at point
(thing-at-point 'symbol t)    ; Symbol at point (includes hyphens)
(thing-at-point 'url t)       ; URL at point (or nil)

;; Get bounds of thing at point
(bounds-of-thing-at-point 'word)  ; → (START . END)
```

## Inserting and Deleting

```elisp
;; Insert at point
(insert "hello")
(insert "line 1\n" "line 2\n")  ; Multiple strings

;; Delete text
(delete-char 5)                  ; Delete 5 chars forward
(delete-region BEG END)          ; Delete a range
(erase-buffer)                   ; Clear entire buffer

;; Replace text in a range
(delete-region beg end)
(insert new-text)

;; Or use replace helpers
(save-excursion
  (goto-char (point-min))
  (while (search-forward "old" nil t)
    (replace-match "new")))
```

## String Operations

```elisp
;; String manipulation (non-buffer)
(concat "hello" " " "world")           ; → "hello world"
(substring "hello world" 0 5)          ; → "hello"
(string-trim "  hi  ")                 ; → "hi"
(upcase "hello")                       ; → "HELLO"
(downcase "HELLO")                     ; → "hello"
(capitalize "hello world")             ; → "Hello world"

;; Replace in strings (not buffers)
(replace-regexp-in-string "foo" "bar" "foo is foo")  ; → "bar is bar"

;; Format strings
(format "Name: %s, Age: %d" "Alice" 30)  ; → "Name: Alice, Age: 30"

;; Split and join
(split-string "a,b,c" ",")             ; → ("a" "b" "c")
(string-join '("a" "b" "c") ", ")      ; → "a, b, c"
```

## Practical: Bulk Rename in Region

```elisp
(defun my-rename-in-region (beg end old-name new-name)
  "Replace OLD-NAME with NEW-NAME within the region BEG to END."
  (interactive
   (if (use-region-p)
       (let* ((bounds (list (region-beginning) (region-end)))
              (old (read-string "Old name: " (thing-at-point 'symbol t)))
              (new (read-string (format "Replace '%s' with: " old))))
         (append bounds (list old new)))
     (user-error "No region selected")))
  (save-excursion
    (save-restriction
      (narrow-to-region beg end)
      (goto-char (point-min))
      (let ((count 0))
        (while (search-forward old-name nil t)
          (replace-match new-name t t)
          (setq count (1+ count)))
        (message "Replaced %d occurrence%s" count
                 (if (= count 1) "" "s"))))))
```

## narrow-to-region: Restrict Operations

`narrow-to-region` makes the buffer appear to contain only the selected text. All operations (search, replace, point-min/max) respect the narrowing:

```elisp
(save-restriction                    ; Restore original narrowing after
  (narrow-to-region beg end)         ; Only see this region
  (goto-char (point-min))            ; "Start" is now region start
  (while (search-forward "x" nil t)
    (replace-match "y")))
```

## Practical: Smart Line Operations

```elisp
(defun my-duplicate-line-or-region ()
  "Duplicate the current line, or region if active."
  (interactive)
  (if (use-region-p)
      (let ((text (buffer-substring (region-beginning) (region-end))))
        (goto-char (region-end))
        (insert text))
    (let ((line (thing-at-point 'line t)))
      (end-of-line)
      (insert "\n" (string-trim-right line)))))

(defun my-move-line-up ()
  "Move the current line up one line."
  (interactive)
  (let ((col (current-column)))
    (transpose-lines 1)
    (forward-line -2)
    (move-to-column col)))

(defun my-move-line-down ()
  "Move the current line down one line."
  (interactive)
  (let ((col (current-column)))
    (forward-line 1)
    (transpose-lines 1)
    (forward-line -1)
    (move-to-column col)))
```

## Text Properties

Text in Emacs can carry invisible metadata — faces, read-only flags, custom data:

```elisp
;; Add a face to text
(put-text-property beg end 'face 'bold)

;; Make text read-only
(put-text-property beg end 'read-only t)

;; Add custom property
(put-text-property beg end 'my-data "some value")

;; Read property at point
(get-text-property (point) 'face)
```

## Exercises

1. Write `my-wrap-region` that wraps the selected text in a pair of characters (parens, brackets, quotes) chosen by the user.
2. Create a command that sorts the lines in the current region alphabetically.
3. Write `my-count-words-region` that counts words, lines, and characters in the selection.

## What You Learned

- **Point and mark** — cursor position and selection boundaries
- **`buffer-substring`** — extract text from buffer
- **`thing-at-point`** — get word/symbol/line at cursor
- **`insert` / `delete-region`** — modify buffer content
- **`replace-regexp-in-string`** — transform strings
- **`narrow-to-region`** — restrict operations to a selection
- **`save-restriction`** — restore narrowing after operations
- **Text properties** — invisible metadata on text

You're replacing literal strings, but what about patterns? What if you want to match all `camelCase` variables, or find dates in any format? Time for regular expressions.

---

[← Chapter 8: Keymaps](chapter-08-keymaps.md) | [Chapter 10: Regular Expressions →](chapter-10-regex.md)
