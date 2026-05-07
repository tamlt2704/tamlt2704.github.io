# Chapter 7: The Pipeline View — DAG Visualization

[← Chapter 6: Job Actions](chapter-06-actions.md) | [Chapter 8: Authentication →](chapter-08-auth.md)

---

## The Problem

Captain Deadline: "Show me the nightly pipeline. I want to see which step it's on. Like a flowchart, but live."

The backend returns a DAG as nodes and edges (Chapter 5 backend). You need to render it as an interactive directed graph — nodes colored by status, edges showing dependencies, click a node to see the job detail.

## What You'll Build

- **Pipeline page** — `/workflows/:id` route showing the DAG
- **React Flow integration** — render nodes and edges as a directed graph
- **Live status colors** — nodes update in real time via SSE (green = done, blue = running, gray = blocked)
- **Click-to-inspect** — click a node to open the job detail panel
- **Auto-layout** — Dagre algorithm to position nodes without manual coordinates

## Key Concepts

- **React Flow** — declarative graph rendering library
- **Dagre** — automatic graph layout algorithm
- **React Router** — `/workflows/:id` dynamic route with `useParams`
- **Conditional rendering** — different node styles based on job status
- **Side panels** — slide-out detail view without leaving the page

---

[← Chapter 6: Job Actions](chapter-06-actions.md) | [Chapter 8: Authentication →](chapter-08-auth.md)
