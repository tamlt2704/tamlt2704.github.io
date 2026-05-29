# Chapter 7: Programming

[prev: Essential Packages](chapter-06-essential-packages.md) | [next: Org Mode](chapter-08-org-mode.md)

## LSP (Language Server Protocol)

LSP gives you IDE features: completion, diagnostics, go-to-definition, rename, etc.

### eglot (Built-in, Emacs 29+)

```elisp
;; eglot is built-in, just hook it up
(use-package eglot
  :hook
  ((python-mode . eglot-ensure)
   (typescript-mode . eglot-ensure)
   (rust-mode . eglot-ensure)
   (go-mode . eglot-ensure)
   (java-mode . eglot-ensure)))
```

### lsp-mode (Feature-rich alternative)

```elisp
(use-package lsp-mode
  :ensure t
  :commands lsp
  :hook
  ((python-mode . lsp)
   (typescript-mode . lsp)
   (rust-mode . lsp))
  :custom
  (lsp-keymap-prefix "C-c l"))

(use-package lsp-ui
  :ensure t
  :after lsp-mode
  :custom
  (lsp-ui-doc-enable t)
  (lsp-ui-sideline-enable t))
```

## Tree-sitter (Syntax Highlighting)

Emacs 29+ has built-in tree-sitter support for fast, accurate syntax highlighting:

```elisp
;; Emacs 29+ tree-sitter modes are named *-ts-mode
;; Remap old modes to tree-sitter modes
(setq major-mode-remap-alist
      '((python-mode . python-ts-mode)
        (javascript-mode . js-ts-mode)
        (typescript-mode . typescript-ts-mode)
        (rust-mode . rust-ts-mode)
        (go-mode . go-ts-mode)))
```

Install grammars with `M-x treesit-install-language-grammar`.

## Language-Specific Setup

### Python

```elisp
(use-package lsp-pyright
  :ensure t
  :hook (python-mode . (lambda ()
                         (require 'lsp-pyright)
                         (lsp))))
```

### Java

```elisp
(use-package lsp-java
  :ensure t
  :hook (java-mode . lsp))
```

### TypeScript

```elisp
(use-package typescript-mode
  :ensure t
  :hook (typescript-mode . lsp))
```

### Rust

```elisp
(use-package rustic
  :ensure t
  :custom
  (rustic-lsp-client 'eglot))  ; or 'lsp-mode
```

### Go

```elisp
(use-package go-mode
  :ensure t
  :hook
  ((go-mode . lsp)
   (before-save . gofmt-before-save)))
```

## Compilation

```
M-x compile RET make RET
```

| Key               | Action              |
| ----------------- | ------------------- |
| `M-x compile`     | Run compile command |
| `M-x recompile`   | Re-run last compile |
| `C-x backtick`    | Jump to next error  |
| `M-g n` / `M-g p` | Next/previous error |

```elisp
;; Set default compile command per project
(add-hook 'python-mode-hook
  (lambda () (setq-local compile-command "python -m pytest")))
```

## Debugging with dap-mode

```elisp
(use-package dap-mode
  :ensure t
  :after lsp-mode
  :config
  (dap-auto-configure-mode))
```

Use `M-x dap-debug` to start a debug session. Supports breakpoints, stepping, variable inspection.

## Terminal (vterm)

A fast, full-featured terminal emulator inside Emacs:

```elisp
(use-package vterm
  :ensure t
  :bind ("C-c v" . vterm))
```

Requires `cmake` and `libtool` to compile the native module on first use.
