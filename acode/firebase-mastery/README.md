# Firebase Mastery: A Serverless Survival Story

Three co-founders. No backend engineer. No DevOps budget. Six weeks to demo day. Build a real-time collaborative app with Firebase — fast, but without the horror stories.

## The Story

You're building **SnapTask** — a real-time collaborative task manager. No servers, no Docker, no Kubernetes. Just Firebase services, security rules, and a React frontend. Ship the MVP in weeks, not months — but avoid the traps that lead to $30K bills and security holes.

## Chapters

### Part 1: Ship the MVP

| # | The Feature | What You Learn |
|---|------------|----------------|
| 01 | Project setup, first deploy | Firebase console, SDK, Hosting |
| 02 | Users need to sign in | Auth — email/password, Google, session |
| 03 | Store tasks in a database | Firestore — documents, collections, CRUD |
| 04 | Tasks update in real-time | onSnapshot, real-time listeners, optimistic UI |
| 05 | Anyone can read anyone's tasks 😱 | Security Rules (most critical chapter) |

### Part 2: Make It Useful

| # | The Feature | What You Learn |
|---|------------|----------------|
| 06 | Attach files to tasks | Storage — upload, download, rules |
| 07 | Filter by status, assignee | Queries — where, orderBy, compound |
| 08 | Query fails with index error | Composite indexes, query limitations |
| 09 | Notify when task assigned | Cloud Functions — triggers, events |
| 10 | Push notifications to mobile | FCM, topics, tokens |

### Part 3: Make It Scale

| # | The Problem | What You Learn |
|---|------------|----------------|
| 11 | Loading team loads ALL tasks | NoSQL modeling, denormalization, subcollections |
| 12 | Offline mode (subway users) | Offline persistence, conflict resolution |
| 13 | Counting tasks is expensive | Aggregation, distributed counters |
| 14 | Batch operations | Batched writes, transactions, atomicity |
| 15 | Paginate 10,000 tasks | Cursors, startAfter, query limits |

### Part 4: Survive Demo Day

| # | The Problem | What You Learn |
|---|------------|----------------|
| 16 | Cloud Function cold starts | Optimization, min instances, scheduled |
| 17 | $200 bill with 50 users | Cost optimization, billing alerts |
| 18 | Need an API for integrations | Callable functions, REST endpoints |
| 19 | Testing without hitting prod | Firebase Emulator Suite |
| 20 | Demo day investor questions | Security audit, scaling limits, the pitch |

## The Trap

Firebase is easy to start. That's the trap. The easy path leads to:
- Security rules that let anyone read everything
- Data models that can't be queried
- Unindexed queries that fail in production
- Reading entire collections ($$$)

This series teaches you to ship fast AND ship correctly.

## Prerequisites

```bash
npm install -g firebase-tools
firebase login
firebase init  # Select: Firestore, Functions, Hosting, Storage, Emulators
firebase emulators:start  # Everything runs locally
```
