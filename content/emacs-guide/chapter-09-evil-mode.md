# Chapter 9: Evil Mode

[prev: Org Mode](chapter-08-org-mode.md) | [next: Productive Workflows](chapter-10-workflows.md)

## Why Evil Mode

Evil (Extensible Vi Layer) brings Vim's modal editing to Emacs. You get:

- Vim's efficient text editing (motions, operators, text objects)
- Emacs's extensibility, Org Mode, Magit, and package ecosystem
- The best of both worlds

## Setup

```elisp
(use-package evil
  :ensure t
  :init
  (setq evil-want-integration t)
  (setq evil-want-keybinding nil)  ; Required for evil-collection
  :config
  (evil-mode 1))
```

## evil-collection

Provides consistent Evil bindings across Emacs modes (Magit, Dired, Org, etc.):

```elisp
(use-package evil-collection
  :ensure t
  :after evil
  :config
  (evil-collection-init))
```

Without evil-collection, many Emacs modes ignore Evil states and use their own keybindings.

## States (Modes)

| State  | Color  | Purpose                                        |
| ------ | ------ | ---------------------------------------------- |
| Normal | Blue   | Navigation and commands (like Vim normal mode) |
| Insert | Green  | Typing text                                    |
| Visual | Orange | Selection                                      |
| Motion | Purple | Read-only navigation                           |
| Emacs  | Red    | Bypass Evil, use Emacs bindings                |

Switch to Emacs state with `C-z` (toggle).

## Leader Key

A leader key gives you a namespace for custom bindings (like Spacemacs/Doom):

```elisp
(use-package general
  :ensure t
  :config
  (general-create-definer my-leader-def
    :keymaps '(normal insert visual emacs)
    :prefix "SPC"
    :global-prefix "C-SPC")

  (my-leader-def
    "f"  '(:ignore t :which-key "files")
    "ff" '(find-file :which-key "find file")
    "fs" '(save-buffer :which-key "save")
    "b"  '(:ignore t :which-key "buffers")
    "bb" '(consult-buffer :which-key "switch buffer")
    "bk" '(kill-buffer :which-key "kill buffer")
    "g"  '(:ignore t :which-key "git")
    "gs" '(magit-status :which-key "git status")
    "w"  '(:ignore t :which-key "windows")
    "wv" '(split-window-right :which-key "split vertical")
    "ws" '(split-window-below :which-key "split horizontal")
    "wd" '(delete-window :which-key "delete window")))
```

Now `SPC f f` finds a file, `SPC g s` opens Magit, etc.

## Common Workflow

Normal mode editing with Emacs power:

- `SPC g s` — open Magit (leader key)
- `g d` — go to definition (via LSP)
- `K` — show documentation (via LSP)
- `:w` — save (Vim command)
- `C-c C-c` — Emacs-style confirm (in Org, Magit, etc.)

## Useful Evil Packages

```elisp
;; Surround text objects (like vim-surround)
(use-package evil-surround
  :ensure t
  :config (global-evil-surround-mode 1))

;; Comment with gc
(use-package evil-commentary
  :ensure t
  :config (evil-commentary-mode))
```

## Tips

- Use `C-z` to toggle between Evil and Emacs state when needed
- In Emacs state, all standard Emacs bindings work
- evil-collection handles most mode-specific bindings automatically
- Start with Normal/Insert/Visual — learn other states later
