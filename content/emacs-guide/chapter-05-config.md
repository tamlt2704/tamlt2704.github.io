# Chapter 5: Configuration

[prev: Buffers and Windows](chapter-04-buffers-windows.md) | [next: Essential Packages](chapter-06-essential-packages.md)

## Config File Locations

| File                       | Purpose                                  |
| -------------------------- | ---------------------------------------- |
| `~/.emacs.d/init.el`       | Main configuration file                  |
| `~/.emacs.d/early-init.el` | Runs before GUI/package init (Emacs 27+) |
| `~/.config/emacs/init.el`  | XDG alternative location                 |

## Emacs Lisp Basics

### Setting Variables

```elisp
(setq inhibit-startup-screen t)
(setq
 ring-bell-function 'ignore
 use-short-answers t
 make-backup-files nil)
```

### Hooks

```elisp
(add-hook 'prog-mode-hook 'display-line-numbers-mode)
(add-hook 'before-save-hook 'delete-trailing-whitespace)
```

### Keybindings

```elisp
(global-set-key (kbd "C-c l") 'org-store-link)
(define-key emacs-lisp-mode-map (kbd "C-c e") 'eval-buffer)
```

## Package Management with MELPA

```elisp
(require 'package)
(setq package-archives
      '(("melpa" . "https://melpa.org/packages/")
        ("gnu" . "https://elpa.gnu.org/packages/")
        ("nongnu" . "https://elpa.nongnu.org/nongnu/")))
(package-initialize)

(unless package-archive-contents
  (package-refresh-contents))
```

## use-package

`use-package` is the standard way to configure packages (built-in since Emacs 29):

```elisp
(use-package magit
  :ensure t
  :bind ("C-x g" . magit-status)
  :config
  (setq magit-display-buffer-function
        #'magit-display-buffer-same-window-except-diff-v1))
```

### use-package Keywords

| Keyword     | Purpose                                  |
| ----------- | ---------------------------------------- |
| `:ensure t` | Auto-install from package archive        |
| `:init`     | Code run before package loads            |
| `:config`   | Code run after package loads             |
| `:bind`     | Define keybindings (also defers loading) |
| `:hook`     | Add to hooks (defers loading)            |
| `:defer t`  | Lazy-load (don't load until needed)      |
| `:commands` | Autoload specific commands               |
| `:custom`   | Set customization variables              |
| `:after`    | Load after another package               |

### Deferred Loading

```elisp
(use-package flycheck
  :ensure t
  :hook (prog-mode . flycheck-mode))  ; Loads on prog-mode activation
```

## Starter Config

```elisp
;; early-init.el
(setq package-enable-at-startup nil)
(setq inhibit-startup-screen t)
(menu-bar-mode -1)
(tool-bar-mode -1)
(scroll-bar-mode -1)
```

```elisp
;; init.el
(require 'package)
(setq package-archives
      '(("melpa" . "https://melpa.org/packages/")
        ("gnu" . "https://elpa.gnu.org/packages/")))
(package-initialize)

(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))
(require 'use-package)
(setq use-package-always-ensure t)

;; Basic settings
(setq
 make-backup-files nil
 auto-save-default nil
 create-lockfiles nil
 use-short-answers t
 ring-bell-function 'ignore)

;; UI
(global-display-line-numbers-mode 1)
(column-number-mode 1)
(show-paren-mode 1)
(recentf-mode 1)
(savehist-mode 1)
(winner-mode 1)

(set-face-attribute 'default nil :height 140)
```

## Organizing Your Config

As your config grows, split it into files:

```elisp
(load (expand-file-name "ui.el" user-emacs-directory))
(load (expand-file-name "keybindings.el" user-emacs-directory))
(load (expand-file-name "languages.el" user-emacs-directory))
```
