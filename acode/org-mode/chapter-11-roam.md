# Chapter 11: Build a Second Brain — Org-Roam and Networked Notes

[← Ch 10](chapter-10-agenda-advanced.md) | [Ch 12 →](chapter-12-workflows.md)

---

## The Problem

You've been taking notes for months. They're organized in files and headings. But knowledge doesn't fit neatly into hierarchies. That insight from a book connects to a project idea which connects to a conversation you had last week. Your notes are trees, but your thinking is a *graph*.

You read an article about event-driven architecture. Six months later, you're designing a notification system and can't remember where you wrote about it. It's in your notes *somewhere* — but which file? Which heading?

---

## The Naive Attempt

You try to organize notes by topic. But topics overlap:
- Does "Redis pub/sub" go under "Redis" or "Event-driven architecture" or "Notification system"?
- Does a meeting note about database design go under "Meetings" or "Database" or the project name?

You end up duplicating notes or putting them in one place and never finding them from the other context.

---

## Nadia's Way: Notes That Link to Each Other

> "Org-roam gives you networked notes — like a personal Wikipedia. Every note is a node. You link between them freely. When you open a note, you see what *links to it* — backlinks. Over time, clusters of connected ideas emerge. You don't organize top-down; the structure emerges bottom-up from connections."

---

## What Is Org-Roam?

Org-roam is a package that adds:
- **One note per file** (or per heading) — each is a "node"
- **Backlinks** — see what other notes reference this one
- **A graph** — visualize connections between notes
- **Fast search** — find any note by title instantly

It implements the Zettelkasten method (slip-box) in org-mode.

---

## Setup

Install org-roam (via use-package or straight.el):

```elisp
(use-package org-roam
  :ensure t
  :custom
  (org-roam-directory (file-truename "~/org/roam/"))
  :bind (("C-c n l" . org-roam-buffer-toggle)
         ("C-c n f" . org-roam-node-find)
         ("C-c n i" . org-roam-node-insert)
         ("C-c n c" . org-roam-capture)
         ("C-c n g" . org-roam-graph)
         :map org-mode-map
         ("C-M-i" . completion-at-point))
  :config
  (org-roam-db-autosync-mode))
```

Create the directory:

```bash
mkdir -p ~/org/roam
```

---

## Creating Notes

Press `C-c n f` (find node). Type a title. If it doesn't exist, org-roam creates it:

```org
:PROPERTIES:
:ID: 20260115T093000
:END:
#+title: Event-Driven Architecture

Event-driven architecture (EDA) is a design pattern where components
communicate through events rather than direct calls.

* Key Concepts
- Events are immutable facts about something that happened
- Producers emit events without knowing who consumes them
- Consumers subscribe to event types they care about

* Patterns
- Pub/Sub (see [[id:20260115T094500][Redis Pub/Sub]])
- Event Sourcing
- CQRS (see [[id:20260115T095000][CQRS Pattern]])

* When to Use
- Decoupling services
- Async processing
- Audit trails
- Real-time notifications (see [[id:20260115T100000][Notification System Design]])
```

Each `[[id:...][Title]]` is a link to another roam note.

---

## Linking Notes

While writing, press `C-c n i` (insert node). Search for an existing note or create a new one. A link is inserted:

```org
The notification system uses [[id:20260115T093000][Event-Driven Architecture]]
to decouple the sending logic from the trigger.
```

This creates a bidirectional connection. When you open "Event-Driven Architecture," you'll see "Notification System Design" in the backlinks.

---

## Backlinks: The Magic

Open any note and press `C-c n l` to toggle the backlinks buffer:

```
╔══════════════════════════════════════════════╗
║ Backlinks for: Event-Driven Architecture     ║
╠══════════════════════════════════════════════╣
║                                              ║
║ ── Notification System Design ──             ║
║ The notification system uses                 ║
║ [[Event-Driven Architecture]] to decouple... ║
║                                              ║
║ ── Sprint 14 Spike Notes ──                  ║
║ Researched [[Event-Driven Architecture]]     ║
║ options for the real-time features...        ║
║                                              ║
║ ── Meeting: Architecture Review ──           ║
║ Decided to adopt [[Event-Driven             ║
║ Architecture]] for the messaging layer...    ║
║                                              ║
╚══════════════════════════════════════════════╝
```

You didn't organize this. You just linked naturally while writing. The connections emerged.

---

## Daily Notes / Journal

Org-roam has built-in daily notes:

```elisp
(setq org-roam-dailies-directory "daily/")
(setq org-roam-dailies-capture-templates
      '(("d" "default" entry
         "* %<%H:%M> %?"
         :target (file+head "%<%Y-%m-%d>.org"
                            "#+title: %<%Y-%m-%d %A>\n"))))
```

| Binding | Action |
|---|---|
| `C-c n d` | Today's daily note |
| `C-c n D` | Pick a date |

Your daily note becomes a journal entry that links to whatever you worked on:

```org
#+title: 2026-01-15 Wednesday

* 09:00 Morning planning
  Working on [[id:20260115T100000][Notification System Design]] today.
  Need to finish the [[id:20260114T140000][Redis Pub/Sub]] spike.

* 11:30 Architecture discussion
  Met with Sarah. Decided to use [[id:20260115T093000][Event-Driven Architecture]]
  with [[id:20260115T094500][Redis Pub/Sub]] for the MVP.
  Full event sourcing deferred to Q2.

* 14:00 Implementation
  Started the consumer service. Ran into issues with
  [[id:20260110T160000][Connection Pooling]] — need to share the pool
  across workers.

* 16:30 End of day
  Completed the basic pub/sub flow. Tomorrow: error handling
  and dead letter queue.
```

Every daily note links to concept notes. Every concept note accumulates backlinks from daily notes. You can trace when you worked on what.

---

## The Zettelkasten Principles

1. **Atomic notes** — One idea per note. "Redis Pub/Sub" is separate from "Event-Driven Architecture."
2. **Link liberally** — Every time you reference a concept, link to it.
3. **Write in your own words** — Don't copy-paste. Rephrase to understand.
4. **Let structure emerge** — Don't pre-organize. Let clusters form from links.

---

## Practical: Developer Knowledge Base

Build notes for concepts you encounter:

```
~/org/roam/
├── daily/
│   ├── 2026-01-13.org
│   ├── 2026-01-14.org
│   └── 2026-01-15.org
├── event-driven-architecture.org
├── redis-pub-sub.org
├── cqrs-pattern.org
├── notification-system-design.org
├── connection-pooling.org
├── jwt-authentication.org
├── react-query.org
├── docker-multi-stage-builds.org
└── meeting-architecture-review-2026-01-15.org
```

Each file is a node. Links connect them. The graph grows organically.

---

## Visualizing the Graph

Press `C-c n g` to generate a graph visualization. Org-roam creates an HTML file with an interactive graph showing all your notes and their connections.

Clusters of densely-connected notes reveal your areas of expertise. Isolated notes might need more connections — or might be ideas that haven't found their place yet.

---

## Tags in Org-Roam

Add tags to notes for broad categorization:

```org
#+title: Redis Pub/Sub
#+filetags: :redis:architecture:backend:
```

Search by tag: `C-c n f` then filter by tag. Tags are coarse categories; links are fine-grained connections.

---

## Meeting Notes in Roam

```org
:PROPERTIES:
:ID: 20260115T110000
:END:
#+title: Meeting: Architecture Review 2026-01-15
#+filetags: :meeting:

* Attendees
  - You, Sarah, Marcus, Nadia

* Decisions
  - Use [[id:20260115T093000][Event-Driven Architecture]] for messaging
  - [[id:20260115T094500][Redis Pub/Sub]] for MVP (not Kafka)
  - Defer [[id:20260115T095000][CQRS Pattern]] to Q2

* Action Items
  - [ ] You: Implement basic pub/sub consumer by Friday
  - [ ] Sarah: Update [[id:20260110T090000][System Architecture Diagram]]
  - [ ] Marcus: Frontend WebSocket integration spike

* Notes
  Sarah raised concerns about message ordering. For MVP,
  we accept eventual consistency. If ordering becomes critical,
  we'll add sequence numbers per-channel.
```

This meeting note links to concepts, decisions, and other notes. Six months later, you can trace *why* you chose Redis over Kafka — follow the link.

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c n f` | Find/create node |
| `C-c n i` | Insert link to node |
| `C-c n l` | Toggle backlinks buffer |
| `C-c n c` | Capture to roam |
| `C-c n g` | View graph |
| `C-c n d` | Today's daily note |
| `C-c n D` | Daily note for a date |

---

## Exercise: Start Your Knowledge Graph

1. Install org-roam and set up `~/org/roam/`.
2. Create 5 concept notes about things you're working on or learning:
   - A technology (e.g., "WebSockets", "Docker Compose")
   - A pattern (e.g., "Repository Pattern", "Circuit Breaker")
   - A project (e.g., "Dashboard Redesign")
   - A tool (e.g., "PostgreSQL", "React Query")
   - A decision (e.g., "Why We Chose TypeScript")

3. Link between them. Each note should link to at least 2 others.
4. Create a daily note for today. Reference at least 2 of your concept notes.
5. Open one of your concept notes and check the backlinks buffer (`C-c n l`).
6. Create a meeting note that links to relevant concept notes.

> **Nadia's tip:** "Org-roam changed how I learn. Before, I'd read something, take notes, and forget. Now every new concept gets a note that links to what I already know. When I revisit a topic, the backlinks show me everything I've connected to it — meetings, daily notes, other concepts. It's like having a conversation with my past self. Start small: 5 notes. The network effect kicks in around 50."

---

[← Ch 10](chapter-10-agenda-advanced.md) | [Ch 12: Putting It All Together →](chapter-12-workflows.md)
