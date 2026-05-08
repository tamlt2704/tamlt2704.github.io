# Chapter 14: Async Processes

[← Chapter 13: Packages](chapter-13-packages.md) | [Back to Overview →](chapter-00-overview.md)

---

## The Wish

"I want to run builds, tests, and linters without freezing Emacs. Kick off a `cargo build`, keep editing, and get notified when it finishes — with errors highlighted if it failed."

## Synchronous vs Asynchronous

```elisp
;; SYNCHRONOUS: Emacs freezes until done
(shell-command "cargo build")           ; Blocks!
(call-process "npm" nil t nil "test")   ; Blocks!

;; ASYNCHRONOUS: Emacs stays responsive
(start-process "build" "*build*" "cargo" "build")  ; Returns immediately
```

Always use async for anything that takes more than a fraction of a second.

## start-process: The Foundation

```elisp
(start-process NAME BUFFER PROGRAM &rest ARGS)
```

```elisp
;; Start a build process, output goes to *build* buffer
(start-process "my-build" "*build*" "cargo" "build")

;; Start without a buffer (discard output)
(start-process "notify" nil "notify-send" "Build started")

;; The process object
(let ((proc (start-process "test" "*test*" "npm" "test")))
  (process-status proc)    ; → run, exit, signal, etc.
  (process-exit-status proc))  ; → exit code (0 = success)
```

## Sentinels: React When a Process Finishes

A sentinel is a callback that runs when a process changes state:

```elisp
(defun my-build-sentinel (process event)
  "Handle build process completion."
  (cond
   ((string-match-p "finished" event)
    (message "✓ Build succeeded!")
    (kill-buffer (process-buffer process)))
   ((string-match-p "exited abnormally" event)
    (message "✗ Build FAILED — check *build* buffer")
    (display-buffer (process-buffer process)))))

(let ((proc (start-process "build" "*build*" "cargo" "build")))
  (set-process-sentinel proc #'my-build-sentinel))
```

## Practical: Async Build Command

```elisp
(defvar my-build-process nil
  "Current build process, if any.")

(defun my-build ()
  "Run the project build asynchronously."
  (interactive)
  ;; Kill previous build if still running
  (when (and my-build-process (process-live-p my-build-process))
    (kill-process my-build-process)
    (message "Killed previous build"))

  (let* ((default-directory (or (project-root (project-current))
                                default-directory))
         (cmd (my-build--detect-command))
         (buf (get-buffer-create "*my-build*")))

    ;; Clear the output buffer
    (with-current-buffer buf (erase-buffer))

    ;; Start the process
    (setq my-build-process
          (start-process-shell-command "my-build" buf cmd))

    (set-process-sentinel my-build-process #'my-build--sentinel)
    (message "Building: %s" cmd)))

(defun my-build--detect-command ()
  "Detect the build command for the current project."
  (cond
   ((file-exists-p "Cargo.toml") "cargo build 2>&1")
   ((file-exists-p "package.json") "npm run build 2>&1")
   ((file-exists-p "Makefile") "make 2>&1")
   ((file-exists-p "go.mod") "go build ./... 2>&1")
   (t (read-string "Build command: "))))

(defun my-build--sentinel (proc event)
  "Handle build completion."
  (let ((status (process-exit-status proc)))
    (if (= status 0)
        (progn
          (message "✓ Build succeeded in %s"
                   (project-root (project-current)))
          ;; Auto-close buffer after success
          (run-at-time 2 nil #'kill-buffer (process-buffer proc)))
      (message "✗ Build failed (exit %d)" status)
      (display-buffer (process-buffer proc)))))

(global-set-key (kbd "<f5>") #'my-build)
```

## Process Filters: Handle Output Line by Line

A filter function receives output as it arrives (not just at the end):

```elisp
(defun my-test-filter (proc output)
  "Process test output, looking for failures."
  ;; Insert into process buffer
  (when (buffer-live-p (process-buffer proc))
    (with-current-buffer (process-buffer proc)
      (goto-char (point-max))
      (insert output)))

  ;; Check for failures in real-time
  (when (string-match-p "FAIL\\|ERROR" output)
    (message "⚠ Test failure detected!")))

(let ((proc (start-process "test" "*test*" "npm" "test")))
  (set-process-filter proc #'my-test-filter)
  (set-process-sentinel proc #'my-build--sentinel))
```

## make-process: Modern API (Emacs 25+)

`make-process` is a keyword-based alternative to `start-process`:

```elisp
(make-process
 :name "lint"
 :buffer "*lint*"
 :command '("eslint" "--format" "compact" ".")
 :sentinel #'my-build--sentinel
 :filter #'my-test-filter
 :connection-type 'pipe)
```

## Compilation Mode: Built-In Async

For builds with parseable error output, use `compile`:

```elisp
(defun my-smart-compile ()
  "Compile with auto-detected command."
  (interactive)
  (let ((default-directory (or (project-root (project-current))
                               default-directory)))
    (compile (my-build--detect-command))))

;; compilation-mode auto-parses errors and lets you jump to them
;; M-g n (next-error) and M-g p (previous-error) navigate errors
```

## Timers: Scheduled Async Work

```elisp
;; Run once after delay
(run-at-time 5 nil #'my-function)          ; 5 seconds from now

;; Run repeatedly
(run-with-timer 0 60 #'my-auto-save)       ; Every 60 seconds

;; Run when idle
(run-with-idle-timer 2 t #'my-idle-task)   ; After 2s idle, repeat

;; Cancel a timer
(setq my-timer (run-with-timer 0 30 #'my-check))
(cancel-timer my-timer)
```

## Practical: Auto-Run Tests on Save

```elisp
(defvar my-autotest-timer nil
  "Debounce timer for auto-testing.")

(defun my-autotest-on-save ()
  "Run tests after saving, debounced to avoid rapid re-runs."
  (when (and (buffer-file-name)
             (project-current))
    ;; Cancel pending run (debounce)
    (when my-autotest-timer
      (cancel-timer my-autotest-timer))
    ;; Schedule test run in 1 second
    (setq my-autotest-timer
          (run-at-time 1 nil #'my-autotest-run))))

(defun my-autotest-run ()
  "Actually run the tests."
  (let* ((default-directory (project-root (project-current)))
         (cmd (cond
               ((file-exists-p "Cargo.toml") "cargo test 2>&1")
               ((file-exists-p "package.json") "npm test 2>&1")
               (t nil))))
    (when cmd
      (let ((proc (start-process-shell-command
                   "autotest" "*autotest*" cmd)))
        (set-process-sentinel proc
          (lambda (p e)
            (if (= (process-exit-status p) 0)
                (message "✓ Tests pass")
              (message "✗ Tests FAILED"))))))))

(add-hook 'after-save-hook #'my-autotest-on-save)
```

## Exercises

1. Write an async command that runs `git status` and displays the result in a popup buffer.
2. Create a process that watches a file for changes (using `inotifywait` or `fswatch`) and recompiles.
3. Build a command that runs multiple processes in sequence (lint → test → build), stopping on first failure.

## What You Learned

- **`start-process`** — launch external commands without blocking
- **Sentinels** — callbacks for process state changes
- **Filters** — handle output as it streams in
- **`make-process`** — modern keyword-based process creation
- **`compile`** — built-in async with error parsing
- **Timers** — scheduled and idle execution
- **Debouncing** — avoid rapid re-execution

## Course Complete 🎉

You started with "I wish Emacs would..." and now you can make it do anything. You've gone from evaluating `(+ 1 2)` in `*scratch*` to writing async build systems and publishable packages.

The loop never ends: wish → explore → implement → integrate. Your init.el is your workshop. `C-h f` is your mentor. The `*scratch*` buffer is always waiting.

Keep wishing. Keep building.

---

[← Chapter 13: Packages](chapter-13-packages.md) | [Back to Overview →](chapter-00-overview.md)
