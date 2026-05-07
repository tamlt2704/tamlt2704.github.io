# Org Mode Mastery: Plain Text That Does Everything

You're a developer with notes in Notion, TODOs in Todoist, time tracking in Toggl, docs in Google Docs, and a journal in... somewhere. Five apps. Nothing talks to each other. You can't grep your life.

Your colleague **Nadia** runs her entire existence from plain text files. Planning sprints, writing documentation, tracking time, publishing blog posts, managing a knowledge base — all from `.org` files in Emacs. Version-controlled. Searchable. Offline. Forever.

This course is about replacing your scattered digital life with one system that's been quietly powering academics, developers, and productivity nerds since 2003.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Developer | "I have 47 browser tabs of half-read articles and no system." |
| **Nadia** | Colleague / Org-mode evangelist | Runs her life in plain text. Tracks everything. Ships on time. |
| **Your Scattered Notes** | The villain | Spread across 5 apps. Unsearchable. Unlinked. |
| **The .org File** | The hero | Plain text that folds, links, schedules, exports, and executes. |

---

## Prerequisites

| Requirement | Why |
|---|---|
| **Emacs 27+** | Org-mode is built in — nothing to install |
| **Basic Emacs navigation** | C-x C-f to open files, C-x C-s to save |
| **A terminal** | For verifying setup |
| **Willingness to learn keybindings** | They become muscle memory fast |

If you've never used Emacs, check out `acode/emacs101` first.

---

## What Is Org Mode?

Plain text files (`.org`) with a simple markup syntax that Emacs understands deeply. Headings fold. TODOs track state. Timestamps schedule. Tables calculate. Code blocks execute. And it all exports to HTML, PDF, Markdown, LaTeX — whatever you need.

```
Plain text → version-controllable
           → greppable
           → works offline
           → works in 20 years
           → no vendor lock-in
           → infinitely extensible
```

---

## The Roadmap

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 00 │ "Why should I care?"                   │ Overview, first .org file, folding
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "My thoughts are a mess"               │ Outlines, headings, structure
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "I forget what needs doing"            │ TODO states, priorities, checkboxes
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "I miss deadlines"                     │ Scheduling, timestamps, agenda
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Ideas vanish before I write them"     │ Capture, refile, inbox workflow
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "I need a quick spreadsheet"           │ Tables, formulas, CSV
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Nothing connects to anything"         │ Links, attachments, cross-references
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "I write once, copy-paste everywhere"  │ Export to HTML, PDF, Markdown
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Docs and code live in different worlds"│ Babel, literate programming, tangling
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Where does my time go?"               │ Clocking, time reports, billing
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "I need a command center"              │ Advanced agenda, custom views, GTD
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "My notes don't link to each other"    │ Org-roam, Zettelkasten, second brain
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "How do I actually use all this daily?"│ Complete developer workflow
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## How to Read This

Every chapter follows the same loop:

```
  😩 You have a real problem (scattered notes, missed deadline, lost time)
   │
   ▼
  🤷 You try solving it the "normal" way (another app, a spreadsheet, sticky notes)
   │
   ▼
  💡 Nadia shows you the org-mode way
   │
   ▼
  ⌨️  You build it — real org syntax, real keybindings
   │
   ▼
  🏋️ Exercise: apply it to your own workflow
```

---

## Quick Setup Verification

```bash
emacs --version   # 27.0+ (org-mode is built in)
```

Open Emacs and check org version:

```
M-x org-version RET
```

You should see something like `Org mode version 9.x`. You're ready.

---

[Start: Chapter 0 — Overview →](chapter-00-overview.md)
