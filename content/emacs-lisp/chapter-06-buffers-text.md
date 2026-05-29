# Chapter 6: Buffers and Text

[prev: Data Structures](chapter-05-data-structures.md) | [next: Writing Commands](chapter-07-commands.md)

## Buffers

A buffer is the basic unit of text in Emacs. Every file you edit lives in a buffer, but buffers can also exist without files.

```elisp
(current-buffer)            ;; => #<buffer *scratch*>
(buffer-name)               ;; => "*scratch*"
(buffer-file-name)          ;; => nil (scratch has no file)
(buffer-list)               ;; => list of all buffers
```

### Switching buffers in code

```elisp
;; Temporarily work in another buffer
(with-current-buffer "*Messages*"
  (buffer-size))
;; => size of Messages buffer (current buffer unchanged after)

;; Create or get a buffer
(get-buffer-create "*my-output*")
```

### Buffer content

```elisp
(with-current-buffer "*scratch*"
  (buffer-string))          ;; => entire buffer contents

(buffer-substring 1 10)    ;; => first 9 characters (1-indexed!)
(buffer-substring-no-properties 1 10)  ;; => without text properties
```

## Point — The Cursor Position

`point` is the current cursor position (1-indexed integer):

```elisp
(point)         ;; => current position
(point-min)     ;; => 1 (or start of narrowed region)
(point-max)     ;; => end of buffer
(line-number-at-pos)  ;; => current line number
```

### Moving point

```elisp
(goto-char (point-min))     ;; go to beginning
(goto-char (point-max))     ;; go to end
(forward-char 5)            ;; move forward 5 chars
(forward-line 3)            ;; move forward 3 lines
(beginning-of-line)         ;; go to line start
(end-of-line)               ;; go to line end
```

## Inserting and Deleting Text

```elisp
(insert "hello world")              ;; insert at point
(insert "line1\n" "line2\n")        ;; multiple strings

(delete-char 5)                     ;; delete 5 chars forward
(delete-region 1 10)                ;; delete between positions
(erase-buffer)                      ;; delete everything
```

### Example: insert text into a new buffer

```elisp
(with-current-buffer (get-buffer-create "*demo*")
  (erase-buffer)
  (insert "Line 1\n")
  (insert "Line 2\n")
  (buffer-string))
;; => "Line 1\nLine 2\n"
```

## save-excursion

`save-excursion` saves point and current buffer, restoring them after the body:

```elisp
(save-excursion
  (goto-char (point-min))
  (insert "HEADER\n"))
;; point is back where it was before
```

This is essential when writing functions that move around — you do not want to surprise the user by moving their cursor.

## save-restriction and narrow-to-region

Narrowing restricts the visible portion of a buffer:

```elisp
(save-restriction
  (narrow-to-region 100 200)
  ;; now point-min is 100, point-max is 200
  ;; only that region is visible to search/edit functions
  (buffer-substring (point-min) (point-max)))
;; restriction is restored after
```

### Practical pattern: operate on a region

```elisp
(defun count-words-region (start end)
  "Count words between START and END."
  (interactive "r")
  (save-excursion
    (save-restriction
      (narrow-to-region start end)
      (goto-char (point-min))
      (let ((count 0))
        (while (forward-word)
          (setq count (1+ count)))
        (message "Words: %d" count)))))
```

## Searching in Buffers

```elisp
(save-excursion
  (goto-char (point-min))
  (when (search-forward "TODO" nil t)
    (line-number-at-pos)))
;; => line number of first "TODO", or nil

;; Regex search
(save-excursion
  (goto-char (point-min))
  (when (re-search-forward "def\\w+" nil t)
    (match-string 0)))
;; => first match
```

The third argument `t` means "return nil on failure instead of signaling an error."

## Text Properties

Text in Emacs can carry properties (face, invisible, read-only, etc.):

```elisp
;; Add a face property
(let ((str "hello"))
  (put-text-property 0 5 'face 'bold str)
  str)

;; Propertize (convenient shorthand)
(propertize "warning" 'face 'font-lock-warning-face)

;; Read properties
(get-text-property 0 'face (propertize "hi" 'face 'bold))
;; => bold
```

### In buffers

```elisp
(save-excursion
  (goto-char (point-min))
  (put-text-property (point) (+ (point) 5) 'face 'highlight))
;; highlights first 5 characters
```

## Overlays

Overlays are like text properties but are not part of the text itself. They are attached to buffer positions:

```elisp
(let ((ov (make-overlay 1 10)))
  (overlay-put ov 'face 'highlight)
  (overlay-put ov 'help-echo "This is highlighted")
  ov)

;; Remove an overlay
(remove-overlays (point-min) (point-max) 'face 'highlight)

;; List overlays at point
(overlays-at (point))
```

Overlays are useful for temporary visual feedback without modifying buffer text.

## Exercises

1. Write a function that counts the number of lines in the current buffer.
2. Write a function that inserts a timestamp at point in the format `[2024-01-15 Mon]`.
3. Use `save-excursion` to find and return the first line that starts with `;;` in the current buffer.
4. Write a function that highlights all occurrences of a given word using overlays.
5. Create a function that extracts all URLs (http/https) from the current buffer using `re-search-forward`.
