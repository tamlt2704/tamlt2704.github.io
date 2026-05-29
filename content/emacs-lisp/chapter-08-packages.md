# Chapter 8: Writing Packages

[prev: Writing Commands](chapter-07-commands.md) | [next: Practical Projects](chapter-09-practical.md)

## Package Structure

A minimal Elisp package is a single `.el` file with specific header conventions:

```elisp
;;; my-package.el --- A short description -*- lexical-binding: t; -*-

;; Author: Your Name <you@example.com>
;; Version: 1.0.0
;; Package-Requires: ((emacs "27.1"))
;; Keywords: convenience
;; URL: https://github.com/you/my-package

;;; Commentary:

;; Longer description of what the package does.
;; Multiple lines are fine.

;;; Code:

(defgroup my-package nil
  "My package customization."
  :group 'convenience)

(defcustom my-package-greeting "Hello"
  "Default greeting."
  :type 'string
  :group 'my-package)

(defun my-package-greet ()
  "Display a greeting."
  (interactive)
  (message "%s from my-package!" my-package-greeting))

(provide 'my-package)
;;; my-package.el ends here
```

## provide and require

`provide` declares what feature a file offers. `require` loads it:

```elisp
;; In my-utils.el
(defun my-utils-double (n) (* n 2))
(provide 'my-utils)

;; In another file
(require 'my-utils)
(my-utils-double 5)  ;; => 10
```

`require` loads the file only once. Use a prefix for all your symbols to avoid conflicts.

## Autoloads

Autoloads let Emacs know about a function without loading the entire file:

```elisp
;;;###autoload
(defun my-package-greet ()
  "Display a greeting."
  (interactive)
  (message "Hello from my-package!"))
```

The `;;;###autoload` cookie tells the package system to make this function available immediately. The full file loads only when the function is first called.

Autoload other forms too:

```elisp
;;;###autoload
(define-minor-mode my-package-mode
  "Toggle my-package-mode."
  :lighter " MP")
```

## Multi-File Packages

For larger packages, use a directory structure:

```
my-package/
  my-package.el          ;; main file with headers
  my-package-utils.el    ;; helper functions
  my-package-pkg.el      ;; package descriptor (alternative to headers)
```

The `-pkg.el` file (optional, for multi-file packages):

```elisp
(define-package "my-package" "1.0.0"
  "A short description."
  '((emacs "27.1")
    (dash "2.19")))
```

## Writing a Minor Mode (Package)

```elisp
;;; word-count-mode.el --- Show word count -*- lexical-binding: t; -*-

;; Package-Requires: ((emacs "26.1"))

;;; Code:

(defvar-local word-count-mode--count 0
  "Current word count.")

(defun word-count-mode--update ()
  "Update the word count."
  (setq word-count-mode--count (count-words (point-min) (point-max))))

;;;###autoload
(define-minor-mode word-count-mode
  "Display word count in mode line."
  :lighter (:eval (format " W:%d" word-count-mode--count))
  (if word-count-mode
      (progn
        (word-count-mode--update)
        (add-hook 'after-change-functions
                  (lambda (&rest _) (word-count-mode--update)) nil t))
    (remove-hook 'after-change-functions
                 (lambda (&rest _) (word-count-mode--update)) t)))

(provide 'word-count-mode)
;;; word-count-mode.el ends here
```

## Writing a Major Mode

```elisp
;;; my-lang-mode.el --- Major mode for MyLang -*- lexical-binding: t; -*-

;;; Code:

(defvar my-lang-mode-syntax-table
  (let ((table (make-syntax-table)))
    (modify-syntax-entry ?# "<" table)   ;; # starts comment
    (modify-syntax-entry ?\n ">" table)  ;; newline ends comment
    (modify-syntax-entry ?\" "\"" table) ;; string delimiter
    table))

(defvar my-lang-mode-font-lock-keywords
  '(("\\b\\(def\\|let\\|if\\|else\\)\\b" . font-lock-keyword-face)
    ("\\b\\(true\\|false\\|nil\\)\\b" . font-lock-constant-face)
    ("def\\s-+\\(\\w+\\)" 1 font-lock-function-name-face)))

;;;###autoload
(define-derived-mode my-lang-mode prog-mode "MyLang"
  "Major mode for editing MyLang files."
  :syntax-table my-lang-mode-syntax-table
  (setq-local comment-start "# ")
  (setq-local font-lock-defaults '(my-lang-mode-font-lock-keywords)))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.mylang\\'" . my-lang-mode))

(provide 'my-lang-mode)
;;; my-lang-mode.el ends here
```

## Distributing on MELPA

1. Host your package on GitHub/GitLab
2. Fork the MELPA repository
3. Add a recipe file in `recipes/`:

```elisp
(my-package :fetcher github :repo "username/my-package")
```

4. Submit a pull request
5. MELPA builds and distributes your package automatically

Requirements:

- Proper file headers (Author, Version, Package-Requires, URL)
- Byte-compilation must succeed without warnings
- Follow naming conventions (prefix all symbols)

## Testing with ERT

ERT (Emacs Lisp Regression Testing) is the built-in test framework:

```elisp
;;; my-package-test.el --- Tests -*- lexical-binding: t; -*-

(require 'ert)
(require 'my-package)

(ert-deftest my-package-test-double ()
  "Test doubling function."
  (should (= (my-package-double 5) 10))
  (should (= (my-package-double 0) 0))
  (should (= (my-package-double -3) -6)))

(ert-deftest my-package-test-greet ()
  "Test greeting contains name."
  (let ((my-package-greeting "Hi"))
    (should (string-match "Hi" (my-package-format-greeting)))))
```

Run tests:

- `M-x ert RET t RET` — run all tests
- `M-x ert RET my-package RET` — run tests matching pattern

### Common assertions

```elisp
(should (= 4 (+ 2 2)))              ;; equality
(should-not (= 4 5))                 ;; negation
(should-error (/ 1 0) :type 'arith-error)  ;; expect error
```

## Exercises

1. Create a minimal single-file package with proper headers, one interactive function, and a `provide` form.
2. Add an autoload cookie and explain what happens when Emacs starts vs when the function is first called.
3. Write a `define-derived-mode` for a simple config file format with comment highlighting.
4. Write three ERT tests for a function you created in a previous chapter.
5. Create a multi-file package structure with a main file that requires a utils file.
