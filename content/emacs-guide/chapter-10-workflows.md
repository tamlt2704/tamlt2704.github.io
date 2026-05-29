# Chapter 10: Productive Workflows

[prev: Evil Mode](chapter-09-evil-mode.md) | [next: Overview](chapter-00-overview.md)

## Pre-configured Distributions

### Doom Emacs

Opinionated, fast, Vim-centric configuration framework:

```bash
git clone --depth 1 https://github.com/doomemacs/doomemacs ~/.config/emacs
~/.config/emacs/bin/doom install
```

- Evil mode by default
- SPC as leader key
- Curated package selection
- Fast startup (~1s)

### Spacemacs

Community-driven, discoverable, supports both Vim and Emacs styles:

```bash
git clone https://github.com/syl20bnr/spacemacs ~/.emacs.d
```

- SPC (Vim) or M-m (Emacs) as leader
- "Layers" for feature groups
- Excellent discoverability via which-key

### When to Use a Distribution vs. Custom Config

- **Distribution**: Want to be productive immediately, prefer curated defaults
- **Custom**: Want full understanding and control, enjoy tinkering

## Custom Keybindings Strategy

Principles:

- `C-c <letter>` is reserved for user bindings
- Use a prefix key (like `C-c`) to namespace your bindings
- Group related commands under the same prefix

```elisp
(global-set-key (kbd "C-c f") 'find-file)
(global-set-key (kbd "C-c r") 'consult-recent-file)
(global-set-key (kbd "C-c g") 'magit-status)
(global-set-key (kbd "C-c s") 'consult-ripgrep)
(global-set-key (kbd "C-c c") 'org-capture)
(global-set-key (kbd "C-c a") 'org-agenda)
```

## Daemon Mode (emacsclient)

Run Emacs as a background server for instant startup:

```bash
# Start the daemon
emacs --daemon

# Open files instantly via client
emacsclient -c file.txt        # New frame
emacsclient -nw file.txt       # Terminal
emacsclient -e '(+ 1 2)'      # Eval expression
```

```elisp
;; Start server automatically from init.el
(unless (server-running-p)
  (server-start))
```

Set as your default editor:

```bash
export EDITOR="emacsclient -nw"
export VISUAL="emacsclient -c"
```

## Shell Integration

```elisp
;; vterm for full terminal
(use-package vterm
  :ensure t
  :bind ("C-c v" . vterm))

;; eshell for Emacs-integrated shell
;; M-x eshell — Lisp-aware shell, no external deps
```

## Note-taking

### org-roam (Zettelkasten)

Networked note-taking with backlinks:

```elisp
(use-package org-roam
  :ensure t
  :custom
  (org-roam-directory "~/org/roam/")
  :bind
  (("C-c n f" . org-roam-node-find)
   ("C-c n i" . org-roam-node-insert)
   ("C-c n l" . org-roam-buffer-toggle))
  :config
  (org-roam-db-autosync-mode))
```

### denote (Simple, file-based)

Minimal note-taking with predictable file names:

```elisp
(use-package denote
  :ensure t
  :custom
  (denote-directory "~/notes/")
  :bind
  (("C-c n n" . denote)
   ("C-c n f" . denote-open-or-create)))
```

## Email (mu4e)

Read email in Emacs with mu4e (requires mu and mbsync/offlineimap):

```elisp
(use-package mu4e
  :config
  (setq mu4e-maildir "~/Mail"
        mu4e-get-mail-command "mbsync -a"
        mu4e-update-interval 300))
```

Alternative: **notmuch** for tag-based email management.

## RSS (elfeed)

Read RSS/Atom feeds:

```elisp
(use-package elfeed
  :ensure t
  :bind ("C-c e" . elfeed)
  :config
  (setq elfeed-feeds
        '("https://planet.emacslife.com/atom.xml"
          "https://sachachua.com/blog/feed/"
          "https://protesilaos.com/codelog.xml")))
```

## Writing Prose

```elisp
;; Visual line mode for soft wrapping
(add-hook 'text-mode-hook 'visual-line-mode)

;; Olivetti for centered, distraction-free writing
(use-package olivetti
  :ensure t
  :hook (text-mode . olivetti-mode)
  :custom (olivetti-body-width 80))

;; Spell checking
(add-hook 'text-mode-hook 'flyspell-mode)
```

## Summary

Emacs is not just an editor — it is a platform. The investment in learning it compounds over time as you integrate more of your workflow into a single, consistent, keyboard-driven environment.

Start small. Add one new thing per week. In a few months, you will wonder how you worked without it.
