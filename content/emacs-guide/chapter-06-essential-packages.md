# Chapter 6: Essential Packages

[prev: Configuration](chapter-05-config.md) | [next: Programming](chapter-07-programming.md)

## which-key (Keybinding Discovery)

Shows available keybindings in a popup after you start a key sequence:

```elisp
(use-package which-key
  :ensure t
  :config
  (which-key-mode)
  (setq which-key-idle-delay 0.5))
```

Press `C-x` and wait — which-key shows all possible continuations.

## Completion Framework: Vertico + Orderless + Marginalia + Consult

The modern completion stack replaces Helm/Ivy with lighter, composable packages:

```elisp
(use-package vertico
  :ensure t
  :init (vertico-mode))

(use-package orderless
  :ensure t
  :custom
  (completion-styles '(orderless basic))
  (completion-category-overrides '((file (styles partial-completion)))))

(use-package marginalia
  :ensure t
  :init (marginalia-mode))

(use-package consult
  :ensure t
  :bind
  (("C-s" . consult-line)
   ("C-x b" . consult-buffer)
   ("M-g g" . consult-goto-line)
   ("M-s r" . consult-ripgrep)))
```

- **Vertico**: Vertical completion UI in the minibuffer
- **Orderless**: Space-separated fuzzy matching (type in any order)
- **Marginalia**: Annotations next to candidates (docstrings, file sizes)
- **Consult**: Enhanced commands (search, buffer switch, grep)

## Magit (Git)

The best Git interface in any editor:

```elisp
(use-package magit
  :ensure t
  :bind ("C-x g" . magit-status))
```

In magit-status buffer:

- `s` — stage file/hunk
- `u` — unstage
- `c c` — commit
- `P p` — push
- `F p` — pull
- `b b` — switch branch
- `l l` — log
- `d d` — diff

## Corfu (Auto-complete)

Modern, minimal completion-at-point UI:

```elisp
(use-package corfu
  :ensure t
  :custom
  (corfu-auto t)
  (corfu-auto-delay 0.2)
  :init (global-corfu-mode))
```

Alternative: `company-mode` is the older, more established option.

## Flycheck (Linting)

On-the-fly syntax checking:

```elisp
(use-package flycheck
  :ensure t
  :hook (prog-mode . flycheck-mode))
```

## Projectile / project.el

Project-aware commands (find file in project, grep, compile):

```elisp
;; Built-in project.el (Emacs 28+)
;; C-x p f  — find file in project
;; C-x p g  — grep in project
;; C-x p c  — compile project

;; Or use projectile for more features:
(use-package projectile
  :ensure t
  :bind-keymap ("C-c p" . projectile-command-map)
  :config (projectile-mode 1))
```

## Treemacs (File Tree)

Sidebar file explorer:

```elisp
(use-package treemacs
  :ensure t
  :bind ("C-c t" . treemacs))
```

## Themes and Icons

```elisp
(use-package doom-themes
  :ensure t
  :config
  (load-theme 'doom-one t))

(use-package all-the-icons
  :ensure t)
;; Run M-x all-the-icons-install-fonts once after install
```

## Helpful (Better Help Buffers)

Richer, more informative help pages:

```elisp
(use-package helpful
  :ensure t
  :bind
  (("C-h f" . helpful-callable)
   ("C-h v" . helpful-variable)
   ("C-h k" . helpful-key)))
```
