# Chapter 6: Job Actions — Forms, Mutations & Confirmation Dialogs

[← Chapter 5: Clean Architecture](chapter-05-architecture.md) | [Chapter 7: The Pipeline View →](chapter-07-dag-visualization.md)

---

## The Problem

Karen can see jobs on the dashboard. She can't *do* anything. To cancel a job, she walks to your desk and asks you to run a curl command. "I want a button that says CANCEL. A big red one."

## What You'll Build

- **Submit Job form** — type selector, payload input, priority picker, submit button
- **Action buttons** — Cancel, Pause, Resume, Resurrect on each job card
- **Confirmation dialog** — "Are you sure you want to cancel 12,000 jobs?" (Yes, Mrs. Jira, we learned)
- **Optimistic UI** — update the badge to CANCELLING immediately, before the server responds
- **Error handling** — show a toast if the action fails, revert the optimistic update
- **Batch actions** — select multiple jobs, cancel/pause all at once

## Key Concepts

- **Forms in React** — controlled inputs, `onChange`, `onSubmit`, `FormData`
- **`POST`/`DELETE` requests** — mutations vs queries
- **Optimistic updates** — update UI before server confirms, rollback on error
- **Toast notifications** — non-blocking feedback for actions
- **`useReducer`** — managing complex form state

---

[← Chapter 5: Clean Architecture](chapter-05-architecture.md) | [Chapter 7: The Pipeline View →](chapter-07-dag-visualization.md)
