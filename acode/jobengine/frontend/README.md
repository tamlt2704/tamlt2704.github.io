# Job Engine Dashboard — Frontend Learning Series

Captain Deadline has a 65-inch TV running `curl -N` in the office. It works. But Mrs. Jira wants buttons. Karen wants a progress bar. Old Greg wants "something that doesn't look like 1997."

You're building the dashboard for the [Job Engine backend](../backend/chapter-00-prerequisites.md). Every chapter adds a feature to the dashboard by solving a real problem — from "I can't even open VS Code" to "we need auth, GraphQL, and it has to work on mobile."

## The Roadmap

| Ch | The Problem | What You Build | What You Learn |
|---|---|---|---|
| 0 | "I don't have Node installed" | Dev environment setup | VS Code, Node, npm, extensions, linting |
| 1 | "I need a project" | Scaffold + first component | Vite, React, TypeScript, JSX, props |
| 2 | "It looks terrible" | Styled job list | Tailwind CSS, responsive layout, dark mode |
| 3 | "It shows stale data" | Live job list from API | `fetch`, `useEffect`, `useState`, loading/error states |
| 4 | "I have to refresh to see updates" | Real-time updates | SSE, `EventSource`, optimistic UI |
| 5 | "The code is a mess" | Refactored architecture | Custom hooks, context, component patterns |
| 6 | "I can't cancel a job from the UI" | Job actions + forms | Forms, mutations, `POST`/`DELETE`, confirmation dialogs |
| 7 | "Show me the pipeline" | DAG visualization | React Flow, graph rendering, interactive nodes |
| 8 | "Who are you?" | Login + protected routes | JWT auth, React Router, route guards, token storage |
| 9 | "It's slow with 10,000 jobs" | Performance | Virtualized lists, pagination, `useMemo`, `React.memo`, lazy loading |
| 10 | "It doesn't work on my phone" | Mobile responsive | Responsive Tailwind, touch interactions, PWA basics |
| 11 | "REST is chatty" | GraphQL integration | Apollo Client, queries, mutations, subscriptions |
| 12 | "Ship it" | Production build + deploy | Build optimization, Docker, environment config, CI/CD |

## Tech Stack

| Tool | Why |
|---|---|
| React 19 | Component model, hooks, massive ecosystem |
| TypeScript | Catch bugs before runtime |
| Vite | Fast dev server, instant HMR |
| Tailwind CSS 4 | Utility-first, no CSS files to manage |
| React Router 7 | Client-side routing |
| React Flow | DAG visualization |
| Apollo Client | GraphQL (Chapter 11) |
| Vitest | Unit tests, same config as Vite |
| Playwright | E2E tests |

## Prerequisites

The backend should be running (Chapters 1-9). If not, the dashboard has nothing to talk to.

```bash
# Backend should be at:
curl http://localhost:8080/jobs
# → [{"id":"abc-123","status":"COMPLETED",...}]
```

Start with [Chapter 0: Setting Up →](chapter-00-setup.md)
