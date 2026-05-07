# Chapter 1: Organize Your Thoughts — Outlines That Move

[← Ch 0](chapter-00-overview.md) | [Ch 2 →](chapter-02-todo.md)

---

## The Problem

You're planning a new feature. You open a blank document and start writing. Twenty minutes later you have a wall of text — requirements mixed with implementation ideas mixed with questions mixed with "oh wait, what about..." tangents.

You try to reorganize. Copy-paste paragraphs around. Lose track of what goes where. End up with a document that's somehow *less* organized than when you started.

---

## The Naive Attempt

Markdown with manual numbering:

```markdown
# Feature: User Dashboard

## 1. Requirements
### 1.1 Must show recent activity
### 1.2 Must show upcoming deadlines

## 2. Design
### 2.1 Layout options
### 2.2 Component structure

## 3. Implementation
### 3.1 API endpoints needed
### 3.2 Frontend components
```

This works until you need to:
- Move section 2.1 under section 3 (copy-paste, fix numbering)
- Add a section between 1.1 and 1.2 (renumber everything)
- Collapse sections you're not working on (you can't)
- See just the outline without the body text (you can't)

---

## Nadia's Way: Structural Editing

> "In org-mode, headings aren't just formatting — they're *objects* you can grab and move. Promote, demote, reorder. The document is a tree, and you manipulate the tree."

---

## Headings: The Building Blocks

```org
* Top-level heading (one star)
** Second-level heading (two stars)
*** Third-level heading (three stars)
**** Fourth-level (you get the idea)

* Another top-level heading
  Body text goes here. It belongs to the heading above it.
  As much text as you want.

** A child of "Another top-level heading"
   This text belongs to this sub-heading.
```

Rules:
- Stars must start at column 0 (beginning of line)
- A space must follow the last star
- Everything between two headings is the "body" of the first heading
- Nesting depth is unlimited (but 3-4 levels is practical)

---

## Visibility Cycling: See Only What You Need

The killer feature. Your cursor is on a heading:

| Press | Result |
|---|---|
| `Tab` | Cycle: folded → children → subtree |
| `S-Tab` | Cycle ALL headings globally |

The three states of a heading:

```
FOLDED:     * Project Alpha...          (body hidden, children hidden)
CHILDREN:   * Project Alpha             (body shown, children shown as folded)
              ** Planning...
              ** Implementation...
SUBTREE:    * Project Alpha             (everything visible)
              ** Planning
                 All the planning text...
              ** Implementation
                 All the implementation text...
```

`S-Tab` cycles the entire buffer:
1. **Overview** — only top-level headings
2. **Contents** — all headings, no body text
3. **Show all** — everything visible

---

## Moving Headings: Restructure Instantly

This is where org-mode leaves Markdown in the dust.

| Binding | Action |
|---|---|
| `M-up` | Move heading UP (swap with previous sibling) |
| `M-down` | Move heading DOWN (swap with next sibling) |
| `M-left` | Promote heading (remove a star, move left in tree) |
| `M-right` | Demote heading (add a star, move right in tree) |
| `M-S-left` | Promote subtree (heading + all children) |
| `M-S-right` | Demote subtree (heading + all children) |

Example — you have:

```org
* Project
** Design
** Implementation
** Testing
** Requirements
```

Oops, Requirements should be first. Put cursor on `** Requirements`, hit `M-up` three times:

```org
* Project
** Requirements
** Design
** Implementation
** Testing
```

Want to make Testing a child of Implementation? Cursor on `** Testing`, hit `M-right`:

```org
* Project
** Requirements
** Design
** Implementation
*** Testing
```

Changed your mind? `M-left` promotes it back. No copy-paste. No renumbering. No broken formatting.

---

## Creating New Headings

| Binding | Action |
|---|---|
| `M-RET` | New heading at same level |
| `C-RET` | New heading after current subtree |
| `M-S-RET` | New TODO heading at same level |

`M-RET` is context-aware:
- At end of a heading line → new sibling heading below
- In the middle of body text → splits the text, new heading from remainder

`C-RET` is safer for brainstorming — it always creates the new heading *after* the entire current subtree, so you don't accidentally split content.

---

## Practical: Planning a Sprint

Let's build a real sprint plan. Create `~/org/sprint.org`:

```org
#+TITLE: Sprint 14 — User Dashboard

* Goals
** Ship dashboard MVP to staging
** Fix 3 critical bugs from last sprint
** Spike on notification system

* Stories
** Dashboard: Recent Activity Feed
   Show last 10 actions by team members.
   - API: GET /activity?limit=10
   - Component: ActivityFeed.tsx
   - Estimate: 3 points

** Dashboard: Deadline Widget
   Show upcoming deadlines from all projects.
   - API: GET /deadlines?upcoming=7d
   - Component: DeadlineWidget.tsx
   - Estimate: 2 points

** Bug: Login redirect loop on Safari
   Reported by 3 users. Reproduce steps in ticket #421.
   - Estimate: 1 point

** Bug: Notification count doesn't reset
   Badge shows stale count after reading notifications.
   - Estimate: 1 point

** Bug: File upload fails over 5MB
   Timeout on large files. Need chunked upload.
   - Estimate: 3 points

** Spike: Push notification architecture
   Research options: FCM, WebSockets, SSE.
   - Timebox: 4 hours
   - Deliverable: decision document

* Retrospective
** What went well
** What didn't
** Action items
```

Now practice:
1. `S-Tab` to collapse everything — see just the top-level structure
2. `Tab` on `* Stories` — see all story titles without details
3. `M-up`/`M-down` to reorder stories by priority
4. `M-right` on a bug to nest it under a "Bugs" heading you create

---

## Narrowing: Focus on One Section

When you're deep in one section and don't want distractions:

| Binding | Action |
|---|---|
| `C-x n s` | Narrow to current subtree (hide everything else) |
| `C-x n w` | Widen (show everything again) |

Cursor on `** Dashboard: Recent Activity Feed`, then `C-x n s` — the buffer shows *only* that subtree. Everything else disappears. You focus. When done, `C-x n w` brings it all back.

---

## Sparse Trees: Find Without Scrolling

Need to find something in a large file without losing your place?

| Binding | Action |
|---|---|
| `C-c /` | Sparse tree (search headings) |
| `C-c / r` | Regex sparse tree |

`C-c /` prompts for a search string, then folds everything *except* matching headings and their context. You see a filtered view of your document.

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `Tab` | Cycle visibility (current heading) |
| `S-Tab` | Cycle visibility (global) |
| `M-RET` | New heading (same level) |
| `C-RET` | New heading (after subtree) |
| `M-up` | Move heading up |
| `M-down` | Move heading down |
| `M-left` | Promote (fewer stars) |
| `M-right` | Demote (more stars) |
| `M-S-left` | Promote subtree |
| `M-S-right` | Demote subtree |
| `C-x n s` | Narrow to subtree |
| `C-x n w` | Widen |
| `C-c /` | Sparse tree search |

---

## Exercise: Restructure a Messy Document

1. Create `~/org/messy.org` with this deliberately disorganized content:

```org
#+TITLE: Project Brain Dump

* API endpoints
* Database schema
* The login page needs work
* Maybe use Redis for caching
* Frontend components
* Need to ask Sarah about the deadline
* Testing strategy
* Deploy to staging Friday
* Research GraphQL vs REST
* Bug: memory leak in worker process
```

2. Reorganize it into a proper structure using ONLY keyboard commands:
   - Create parent headings: `Planning`, `Implementation`, `Operations`
   - Move items under the right parents (M-up/down, then M-right to demote)
   - Reorder items within each section by priority

3. Your result should look something like:

```org
#+TITLE: Project Brain Dump

* Planning
** Research GraphQL vs REST
** Need to ask Sarah about the deadline

* Implementation
** Frontend
*** The login page needs work
*** Frontend components
** Backend
*** API endpoints
*** Database schema
*** Maybe use Redis for caching

* Operations
** Testing strategy
** Deploy to staging Friday
** Bug: memory leak in worker process
```

4. Practice collapsing to just top-level, then expanding one section at a time.

> **Nadia's tip:** "I restructure my files constantly. That's the point — org-mode makes reorganizing so cheap that you never have to get the structure right on the first try. Brain dump first, organize second. The keybindings become muscle memory within a week."

---

[← Ch 0](chapter-00-overview.md) | [Ch 2: Track What Needs Doing →](chapter-02-todo.md)
