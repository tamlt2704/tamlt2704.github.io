# Chapter 0: Why Org Mode — Plain Text That Does Everything

[Chapter 1 →](chapter-01-outlines.md)

---

## The Problem

It's Monday morning. You open your laptop and try to figure out what you're supposed to be doing.

- TODOs are in Todoist (some of them)
- Meeting notes are in Notion (the ones you remembered to write)
- Project plans are in Jira (buried under 200 tickets)
- Quick thoughts are in Apple Notes (unsearchable chaos)
- Time tracking is in Toggl (when you remember to start it)
- That article you wanted to read is in... a browser tab? Pocket? Slack?

You spend 20 minutes just *finding* what you need to do. Then you start working, have an idea, and... where do you put it? Another app. Another context switch.

---

## The Naive Attempt

You try consolidating. Markdown files in a git repo. It works for notes, but:

- No folding (you scroll through 500-line files)
- No TODO tracking (you grep for `- [ ]` and hope)
- No scheduling (you still need a calendar app)
- No time tracking (back to Toggl)
- No execution (code examples are just text)
- No export (you rewrite everything for each format)

Markdown is a document format. You need a *system*.

---

## Nadia's Intervention

You're complaining about this at lunch. Nadia overhears.

> "I track everything in org-mode. TODOs, calendar, time, notes, code, blog posts. It's all plain text. I `git push` my life every night."

You: "Isn't that just fancy Markdown?"

Nadia: "Markdown is a way to format text. Org-mode is a way to *organize your life*. The file format is simple — stars for headings, brackets for links. But Emacs understands the structure. It can fold it, schedule it, clock it, query it, export it, execute it."

She opens her screen. One `.org` file. She hits `Tab` and sections collapse. She hits `C-c a` and a weekly agenda appears — pulled from timestamps scattered across 20 files. She hits `C-c C-c` on a code block and it runs, output appearing inline.

> "It's been my system for 6 years. I've never lost a note. I've never missed a deadline. And I can `grep` anything I've ever written."

---

## What Is an Org File?

A `.org` file is plain text with a simple structure:

```org
#+TITLE: My Project Plan
#+AUTHOR: You
#+DATE: 2026-01-15

* Project Alpha
** Planning
*** Define requirements
    We need to figure out what we're building.
*** Set timeline
    Q1 delivery target.

** Implementation
*** Backend API
    - REST endpoints
    - Database schema
    - Authentication

*** Frontend
    - Component library
    - State management

** Launch
*** Deploy to production
*** Write announcement blog post

* Personal Notes
** Books to read
   - Designing Data-Intensive Applications
   - The Pragmatic Programmer
```

That's it. Stars (`*`) define headings. More stars = deeper nesting. Everything else is body text.

But in Emacs, this file *comes alive*.

---

## The Magic: Folding

When you open this file in Emacs, you see:

```
* Project Alpha...
* Personal Notes...
```

Just the top-level headings. Everything else is hidden. Hit `Tab` on "Project Alpha":

```
* Project Alpha
** Planning...
** Implementation...
** Launch...
* Personal Notes...
```

Hit `Tab` on "Implementation":

```
* Project Alpha
** Planning...
** Implementation
*** Backend API
*** Frontend
** Launch...
* Personal Notes...
```

You navigate a 500-line file by expanding only what you need. Your brain sees structure, not walls of text.

---

## Key Bindings: Your First Five

| Binding | Action | What It Does |
|---|---|---|
| `Tab` | Cycle visibility | Fold/unfold the heading under cursor |
| `S-Tab` | Global cycle | Fold/unfold ALL headings |
| `M-RET` | New heading | Create a sibling heading |
| `C-x C-s` | Save | Save the file |
| `C-x C-f` | Open file | Open/create a .org file |

(`M` = Alt/Meta key, `S` = Shift, `C` = Ctrl)

---

## Quick Verify: Your First Org File

Let's prove this works. Open Emacs and create a file:

```
C-x C-f ~/org/first.org RET
```

Type this:

```org
#+TITLE: My First Org File

* Inbox
** TODO Learn org-mode basics
** TODO Set up my org directory

* Projects
** Side project: CLI tool
*** Design the interface
*** Implement core logic
*** Write tests

* Notes
** Org-mode is plain text that folds
   This is body text under a heading.
   It disappears when the heading is folded.
```

Save with `C-x C-s`. Now:

1. Put your cursor on `* Projects` and hit `Tab` — it collapses
2. Hit `Tab` again — it expands one level
3. Hit `Tab` again — it expands fully
4. Hit `S-Tab` — everything collapses to top-level
5. Hit `S-Tab` again — one level expands globally

You just organized a document that you can navigate in seconds, no matter how large it grows.

---

## Why Developers Love Org Mode

| Feature | What It Means For You |
|---|---|
| Plain text | `git diff` your notes. Grep your life. |
| Folding | Navigate 1000-line files without scrolling |
| TODO tracking | States, priorities, deadlines — in the same file as your notes |
| Agenda | Query all your .org files for upcoming deadlines |
| Time tracking | Clock in/out on tasks. Generate reports. Bill clients. |
| Code execution | Run code blocks inline. Literate programming. |
| Export | One source → HTML, PDF, Markdown, LaTeX, slides |
| Links | Connect files, headings, URLs, emails — everything |
| Tables | Spreadsheet calculations in plain text |
| Capture | Jot a thought in 2 seconds without leaving your current work |

---

## The Org Directory

Nadia's advice:

> "Create one directory for all your org files. I use `~/org/`. Keep it simple. You'll add files as you need them — inbox.org, projects.org, journal.org. Don't over-organize on day one."

```bash
mkdir -p ~/org
```

A minimal starting structure:

```
~/org/
├── inbox.org       ← quick captures go here
├── projects.org    ← active project plans
├── notes.org       ← reference material
└── journal.org     ← daily log
```

---

## What's Coming

Over the next 12 chapters, you'll build a complete personal productivity system:

- **Chapter 1**: Structure your thoughts with outlines
- **Chapter 2**: Track tasks with TODO states and priorities
- **Chapter 3**: Schedule deadlines and use the agenda
- **Chapter 4**: Capture ideas instantly, refile later
- **Chapter 5**: Tables and calculations
- **Chapter 6**: Link everything together
- **Chapter 7**: Export to any format
- **Chapter 8**: Execute code in your documents
- **Chapter 9**: Track where your time goes
- **Chapter 10**: Build a command center with custom agenda views
- **Chapter 11**: Networked notes with org-roam
- **Chapter 12**: The complete daily workflow

Each chapter solves a real problem. No theory without practice.

---

## Exercise: Set Up Your Org Home

1. Create `~/org/` directory
2. Create `~/org/inbox.org` with this content:

```org
#+TITLE: Inbox

* Tasks
** TODO Set up org-mode workflow
** TODO Read chapter 1 of org-mode course

* Ideas
** Try org-mode for sprint planning
** Use org-mode for meeting notes
```

3. Open it in Emacs. Practice folding with `Tab` and `S-Tab`.
4. Add 3 more headings of your own. Nest them 2-3 levels deep.
5. Verify you can collapse everything to just `* Tasks` and `* Ideas`.

> **Nadia's tip:** "Don't worry about the 'perfect' structure yet. Org-mode's killer feature is that restructuring is trivial — you'll learn to move headings around in Chapter 1. Start messy. Organize later."

---

[Chapter 1: Organize Your Thoughts →](chapter-01-outlines.md)
