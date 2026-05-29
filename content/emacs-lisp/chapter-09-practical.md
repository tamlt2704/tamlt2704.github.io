# Chapter 9: Practical Projects

[prev: Writing Packages](chapter-08-packages.md) | [next: Overview](chapter-00-overview.md)

## Project 1: Word Counter Mode

A minor mode that displays the word count in the mode line and updates as you type:

```elisp
;;; -*- lexical-binding: t; -*-

(defvar-local wc-mode--count 0)

(defun wc-mode--update (&rest _)
  "Recount words in buffer."
  (setq wc-mode--count (count-words (point-min) (point-max)))
  (force-mode-line-update))

(define-minor-mode wc-mode
  "Display word count in mode line."
  :lighter (:eval (format " [%dW]" wc-mode--count))
  (if wc-mode
      (progn
        (wc-mode--update)
        (add-hook 'after-change-functions #'wc-mode--update nil t))
    (remove-hook 'after-change-functions #'wc-mode--update t)))
```

Usage: `M-x wc-mode` to toggle. The mode line shows `[42W]`.

## Project 2: Pomodoro Timer

A simple 25-minute timer with notification:

```elisp
;;; -*- lexical-binding: t; -*-

(defvar pomodoro--timer nil)
(defvar pomodoro--end-time nil)

(defun pomodoro--format-remaining ()
  "Format remaining time as MM:SS."
  (let ((remaining (- (float-time pomodoro--end-time) (float-time))))
    (if (> remaining 0)
        (format " [P:%s]" (format-seconds "%m:%s" remaining))
      " [P:done]")))

(defun pomodoro--tick ()
  "Check if timer is done."
  (if (time-less-p pomodoro--end-time (current-time))
      (progn
        (cancel-timer pomodoro--timer)
        (setq pomodoro--timer nil)
        (message "Pomodoro complete! Take a break.")
        (ding))
    (force-mode-line-update t)))

(defun pomodoro-start (minutes)
  "Start a pomodoro timer for MINUTES (default 25)."
  (interactive "nMinutes: ")
  (when pomodoro--timer
    (cancel-timer pomodoro--timer))
  (setq pomodoro--end-time (time-add (current-time) (* minutes 60))
        pomodoro--timer (run-at-time 1 1 #'pomodoro--tick))
  (message "Pomodoro started: %d minutes" minutes))

(defun pomodoro-stop ()
  "Cancel the current pomodoro."
  (interactive)
  (when pomodoro--timer
    (cancel-timer pomodoro--timer)
    (setq pomodoro--timer nil)
    (message "Pomodoro cancelled.")))
```

## Project 3: Custom Org-Capture Template Function

A function that creates a capture template with dynamic content:

```elisp
;;; -*- lexical-binding: t; -*-

(defun my-capture-meeting-template ()
  "Generate an org-capture template for meetings."
  (let ((attendees (read-string "Attendees: "))
        (date (format-time-string "%Y-%m-%d %a")))
    (concat "* Meeting: %^{Topic}\n"
            ":PROPERTIES:\n"
            ":DATE: " date "\n"
            ":ATTENDEES: " attendees "\n"
            ":END:\n\n"
            "** Agenda\n%?\n\n"
            "** Action Items\n- [ ] \n\n"
            "** Notes\n")))

;; Add to org-capture-templates:
;; (add-to-list 'org-capture-templates
;;              '("m" "Meeting" entry
;;                (file "~/org/meetings.org")
;;                (function my-capture-meeting-template)))
```

## Project 4: Mode-Line Segment

A custom mode-line segment showing git branch:

```elisp
;;; -*- lexical-binding: t; -*-

(defvar-local my-modeline--branch nil)

(defun my-modeline--get-branch ()
  "Get current git branch name."
  (let ((branch (string-trim
                 (shell-command-to-string
                  "git rev-parse --abbrev-ref HEAD 2>/dev/null"))))
    (setq my-modeline--branch
          (unless (string-empty-p branch) branch))))

(defun my-modeline-branch-segment ()
  "Return mode-line string for git branch."
  (when my-modeline--branch
    (format " [%s]" my-modeline--branch)))

;; Update on file open
(add-hook 'find-file-hook #'my-modeline--get-branch)

;; Add to mode-line:
;; (setq-default mode-line-format
;;   (append mode-line-format
;;           '((:eval (my-modeline-branch-segment)))))
```

## Project 5: Simple REST Client

Make HTTP requests and display results:

```elisp
;;; -*- lexical-binding: t; -*-

(require 'url)
(require 'json)

(defun rest-get (url)
  "GET URL and return parsed JSON."
  (with-current-buffer (url-retrieve-synchronously url t)
    (goto-char (point-min))
    (re-search-forward "^$")
    (forward-char)
    (let ((json-object-type 'alist))
      (prog1 (json-read)
        (kill-buffer)))))

(defun rest-post (url data)
  "POST DATA (alist) to URL, return parsed JSON."
  (let ((url-request-method "POST")
        (url-request-extra-headers
         '(("Content-Type" . "application/json")))
        (url-request-data (json-encode data)))
    (with-current-buffer (url-retrieve-synchronously url t)
      (goto-char (point-min))
      (re-search-forward "^$")
      (forward-char)
      (let ((json-object-type 'alist))
        (prog1 (json-read)
          (kill-buffer))))))

(defun rest-show (url)
  "Fetch URL and display JSON in a buffer."
  (interactive "sURL: ")
  (let ((result (rest-get url)))
    (with-current-buffer (get-buffer-create "*REST Response*")
      (erase-buffer)
      (insert (pp-to-string result))
      (goto-char (point-min))
      (display-buffer (current-buffer)))))
```

Usage:

```elisp
(rest-get "https://httpbin.org/get")
;; => alist of response data

(rest-post "https://httpbin.org/post" '((name . "Alice") (age . 30)))
;; => alist of response
```

## Project 6: Advice Functions

Advice lets you modify existing functions without changing their source:

### :before — run code before the original

```elisp
(defun my-save-message (&rest _)
  "Log a message before saving."
  (message "Saving %s at %s" (buffer-name) (current-time-string)))

(advice-add 'save-buffer :before #'my-save-message)
```

### :after — run code after the original

```elisp
(defun my-after-find-file (&rest _)
  "Notify after opening a file."
  (message "Opened: %s (%d bytes)"
           (buffer-file-name) (buffer-size)))

(advice-add 'find-file :after #'my-after-find-file)
```

### :around — wrap the original

```elisp
(defun my-timed-advice (orig-fn &rest args)
  "Time how long ORIG-FN takes."
  (let ((start (current-time)))
    (prog1 (apply orig-fn args)
      (message "Took %.3fs"
               (float-time (time-subtract (current-time) start))))))

(advice-add 'some-slow-function :around #'my-timed-advice)
```

### Removing advice

```elisp
(advice-remove 'save-buffer #'my-save-message)
(advice-remove 'find-file #'my-after-find-file)
```

### Practical example: auto-chmod scripts

```elisp
(defun my-make-script-executable (&rest _)
  "Make file executable if it starts with #!."
  (when (and (buffer-file-name)
             (save-excursion
               (goto-char (point-min))
               (looking-at "#!")))
    (set-file-modes (buffer-file-name) #o755)))

(advice-add 'save-buffer :after #'my-make-script-executable)
```

## Exercises

1. Extend the word counter mode to also show character count.
2. Add a "break timer" (5 minutes) that starts automatically when a pomodoro finishes.
3. Write an advice that automatically creates parent directories when saving a file to a non-existent path.
4. Extend the REST client to support custom headers passed as an alist.
5. Write a mode-line segment that shows the number of TODO items in the current buffer, updating on changes.
