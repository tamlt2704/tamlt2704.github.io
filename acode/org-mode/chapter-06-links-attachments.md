# Chapter 6: Connect Everything — Links and Attachments

[← Ch 5](chapter-05-tables.md) | [Ch 7 →](chapter-07-export.md)

---

## The Problem

Your notes reference things: a design doc, a Jira ticket, a Slack thread, a specific function in your codebase, another section in another org file. But the references are just text — "see the design doc" or "related to ticket #421." You can't click them. You can't follow them. Your notes are isolated islands.

---

## The Naive Attempt

You paste full URLs inline:

```markdown
Related: https://jira.company.com/browse/PROJ-421
See also: https://docs.google.com/document/d/1a2b3c4d5e6f/edit
Design: file:///Users/you/projects/dashboard/docs/design.md
```

Ugly. Unreadable. And when the URL changes, you have to find-and-replace across all your files.

---

## Nadia's Way: Everything Is Linkable

> "In org-mode, links are first-class. Link to URLs, files, headings, emails, other org files, specific lines of code — anything. And they're readable because you give them descriptions. One keystroke to follow any link."

---

## Link Syntax

```org
[[target][description]]
```

Or without description:

```org
[[target]]
```

Examples:

```org
[[https://github.com/your/repo][Project Repository]]
[[file:~/org/projects.org][My Projects]]
[[file:~/code/app/src/auth.py::42][auth.py line 42]]
[[*Sprint Planning][Jump to Sprint Planning heading]]
```

The description is what you see. The target is where it goes.

---

## Link Types

| Prefix | Links To | Example |
|---|---|---|
| `https://` | Web URL | `[[https://github.com][GitHub]]` |
| `file:` | Local file | `[[file:~/docs/spec.pdf][Spec]]` |
| `file:` + `::` | File + location | `[[file:app.py::def main][main function]]` |
| `*` | Heading in same file | `[[*Implementation][See Implementation]]` |
| `id:` | Heading by ID | `[[id:abc-123][That specific note]]` |
| (none) | Internal link | `[[My Target]]` matches `<<My Target>>` |

---

## Creating and Following Links

| Binding | Action |
|---|---|
| `C-c C-l` | Insert/edit a link |
| `C-c C-o` | Open link at cursor |
| `C-c &` | Go back after following a link |

When you press `C-c C-l`:
1. Emacs prompts for the link target (with completion)
2. Then prompts for the description
3. Inserts the formatted link

To edit an existing link, put cursor on it and press `C-c C-l` again.

---

## File Links: Your Knowledge Web

Link between org files to build a connected system:

```org
* Project Dashboard
  Requirements: [[file:requirements.org::*Dashboard][Dashboard Requirements]]
  Design doc: [[file:design.org::*Dashboard Layout][Layout Design]]
  Sprint: [[file:sprints.org::*Sprint 14][Current Sprint]]
  Retrospective: [[file:retros.org::*Sprint 13 Retro][Last Retro]]
```

Link to non-org files too:

```org
* Resources
  - [[file:~/Documents/architecture.pdf][Architecture Diagram (PDF)]]
  - [[file:~/code/project/src/main.py][Main entry point]]
  - [[file:~/code/project/README.md][Project README]]
```

---

## Linking to Code

Link to specific locations in source files:

```org
** Authentication Bug
   The issue is in [[file:~/code/app/src/auth.py::def verify_token][verify_token]].
   The token expiry check on [[file:~/code/app/src/auth.py::85][line 85]] uses
   the wrong timezone.
```

The `::` syntax supports:
- `::42` — line number
- `::def verify_token` — search for text
- `::*heading` — org heading (in org files)

---

## Internal Links

Link to headings within the same file:

```org
* Overview
  This project has three phases (see [[*Phase 3]] for the exciting part).

* Phase 1
  Foundation work.

* Phase 2
  Core features.

* Phase 3
  The exciting part! Launch and marketing.
```

`[[*Phase 3]]` links to the heading `* Phase 3` in the same file.

---

## Custom IDs for Stable Links

Headings can move. File links with `*heading` break if you rename the heading. Use IDs for stable references:

```org
* My Important Section
  :PROPERTIES:
  :ID: project-dashboard-design
  :END:
  This section has a stable ID.
```

Link to it from anywhere:

```org
See [[id:project-dashboard-design][the dashboard design]].
```

This link survives heading renames and file moves (as long as the ID stays).

Generate an ID automatically: `M-x org-id-get-create` on any heading.

---

## Attachments

Sometimes you need to associate files (images, PDFs, data files) with a heading:

| Binding | Action |
|---|---|
| `C-c C-a` | Attachment dispatcher |
| `C-c C-a a` | Attach a file (copy to attachment dir) |
| `C-c C-a l` | Attach a file (link, don't copy) |
| `C-c C-a o` | Open an attachment |
| `C-c C-a f` | Open attachment directory |

Attachments are stored in a directory structure based on the heading's ID:

```
~/org/data/ab/cd1234-5678/
├── screenshot.png
├── meeting-notes.pdf
└── data-export.csv
```

```org
* Sprint 14 Planning :ATTACH:
  :PROPERTIES:
  :ID: sprint-14-planning
  :END:
  See the attached wireframe for the dashboard layout.
```

---

## Storing Links from Other Apps

Org-mode can store links from various contexts for later insertion:

| Binding | Action |
|---|---|
| `C-c l` | Store a link to current location (global, needs setup) |
| `C-c C-l` | Insert a stored link |

Set up the global binding:

```elisp
(global-set-key (kbd "C-c l") #'org-store-link)
```

Now you can:
1. Be in a source file → `C-c l` (stores link to that file + line)
2. Switch to your org file → `C-c C-l` (inserts the stored link)

Works from: org headings, source files, dired buffers, info pages, emails (with mu4e/notmuch).

---

## Practical: Project Reference Hub

Create `~/org/project-hub.org`:

```org
#+TITLE: Project Hub — Dashboard Feature

* Quick Links
  - Repo: [[https://github.com/company/dashboard][GitHub]]
  - Board: [[https://linear.app/company/project/dash][Linear Board]]
  - Figma: [[https://figma.com/file/abc123][Design Mockups]]
  - Docs: [[file:~/code/dashboard/docs/][Documentation folder]]

* Architecture
  Entry point: [[file:~/code/dashboard/src/index.ts][src/index.ts]]
  API routes: [[file:~/code/dashboard/src/routes/][routes/]]
  Components: [[file:~/code/dashboard/src/components/][components/]]

* Key Decisions
** Use React Query for data fetching
   Decision date: [2026-01-10 Fri]
   Context: [[file:~/org/meetings.org::*2026-01-10 Architecture Review][Architecture Review meeting]]
   
** REST over GraphQL for MVP
   Decision date: [2026-01-08 Wed]
   Spike results: [[file:~/org/notes.org::*GraphQL vs REST Spike][Spike Notes]]

* Related
  - [[file:~/org/sprints.org::*Sprint 14][Current Sprint]]
  - [[file:~/org/retros.org::*Sprint 13][Last Retrospective]]
  - [[file:~/org/inbox.org][Inbox (unprocessed items)]]
```

One file. Every reference you need. One `C-c C-o` away from any resource.

---

## Link Abbreviations

For frequently used URL patterns:

```org
#+LINK: gh https://github.com/company/%s
#+LINK: jira https://jira.company.com/browse/%s
#+LINK: linear https://linear.app/company/issue/%s
```

Now you can write:

```org
- Fix: [[gh:dashboard/pull/42][PR #42]]
- Ticket: [[jira:DASH-123][DASH-123]]
- Issue: [[linear:DASH-45][Dashboard layout bug]]
```

Short, readable, and the full URL is constructed automatically.

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c C-l` | Insert/edit link |
| `C-c C-o` | Open link at point |
| `C-c &` | Go back after following link |
| `C-c l` | Store link (global, needs setup) |
| `C-c C-a` | Attachment dispatcher |
| `C-c C-a a` | Attach file (copy) |
| `C-c C-a o` | Open attachment |

---

## Exercise: Build Your Link Network

1. Create links between at least 3 of your org files (e.g., tasks.org links to projects.org, projects.org links to notes.org).
2. Add a `* Quick Links` section to your main org file with:
   - 3 web links (repos, docs, tools you use daily)
   - 2 file links (to other org files or source code)
   - 1 internal link (to another heading in the same file)
3. Practice `C-c C-o` to follow links and `C-c &` to jump back.
4. Set up at least one link abbreviation for a URL pattern you use often.
5. Attach a file to a heading using `C-c C-a a`.

> **Nadia's tip:** "Links are what turn a collection of org files into a *system*. My project hub links to sprints, which link to tasks, which link to code, which links to documentation. I can start anywhere and navigate to anything in 2-3 keystrokes. It's like a personal wiki that actually works."

---

[← Ch 5](chapter-05-tables.md) | [Ch 7: Publish Anywhere →](chapter-07-export.md)
