# Chapter 1: Getting Started

[prev: Overview](chapter-00-overview.md) | [next: Navigation](chapter-02-navigation.md)

## Installation

**Linux (Debian/Ubuntu):**

```bash
sudo apt install emacs
```

**Linux (Fedora):**

```bash
sudo dnf install emacs
```

**macOS:**

```bash
brew install emacs-plus@29 --with-native-comp
```

**Windows:**

Download from https://ftp.gnu.org/gnu/emacs/windows/ or use:

```bash
winget install GNU.Emacs
```

## Launching Emacs

```bash
emacs           # GUI mode
emacs -nw       # Terminal mode (no window)
emacs file.txt  # Open a specific file
```

## The Built-in Tutorial

The very first thing you should do:

```
C-h t
```

This opens the interactive tutorial. Spend 30 minutes with it.

## Terminology

| Term           | Meaning                                                         |
| -------------- | --------------------------------------------------------------- |
| **Buffer**     | An area of text in memory (may or may not correspond to a file) |
| **Window**     | A visible area displaying a buffer (not an OS window)           |
| **Frame**      | What other programs call a "window" — the OS-level container    |
| **Minibuffer** | The single-line area at the bottom for commands and input       |
| **Mode line**  | The status bar above the minibuffer showing buffer info         |
| **Point**      | The cursor position                                             |
| **Mark**       | A saved position; together with point defines the region        |
| **Region**     | The text between point and mark (like a selection)              |
| **Major mode** | Defines the primary behavior of a buffer (e.g., python-mode)    |
| **Minor mode** | Optional add-on behavior (e.g., line numbers, spell check)      |

## Keybinding Notation

- `C-` means hold Ctrl
- `M-` means hold Alt (Meta)
- `S-` means hold Shift
- `C-x C-f` means Ctrl+x, then Ctrl+f
- `M-x` means Alt+x (opens command prompt)

## Quitting Emacs

```
C-x C-c    Quit Emacs (prompts to save unsaved buffers)
C-g        Cancel current command / get out of trouble
```

`C-g` is your escape hatch. Press it whenever you are stuck.

## Getting Help

Emacs has an extraordinary built-in help system:

| Key     | Command            | Description                |
| ------- | ------------------ | -------------------------- |
| `C-h t` | help-with-tutorial | Open the tutorial          |
| `C-h k` | describe-key       | Describe what a key does   |
| `C-h f` | describe-function  | Describe a function        |
| `C-h v` | describe-variable  | Describe a variable        |
| `C-h m` | describe-mode      | Describe current modes     |
| `C-h a` | apropos-command    | Search commands by keyword |
| `C-h i` | info               | Open the Info manual       |

Try `C-h k` then press any key combination to learn what it does.

## Your First Session

1. Open Emacs
2. Press `C-h t` to start the tutorial
3. When done, press `C-x C-c` to quit
4. Come back tomorrow and do it again — repetition builds muscle memory
