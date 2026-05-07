# Firebase Mastery: A Serverless Survival Story

Three co-founders. No backend engineer. No DevOps budget. Six weeks to demo day. Build a real-time collaborative app with Firebase — fast, but without the horror stories.

## The Story

You're building **SnapTask** — a real-time collaborative task manager. No servers, no Docker, no Kubernetes. Just Firebase services, security rules, and a React frontend. Ship the MVP in weeks, not months — but avoid the traps that lead to $30K bills and security holes.

## Chapters

### Part 1: Ship the MVP

| # | The Feature | What You Learn |
|---|------------|----------------|
| [01](chapter-01-setup-deploy.md) | Project setup, first deploy | Firebase console, SDK, Hosting |
| [02](chapter-02-authentication.md) | Users need to sign in | Auth — email/password, Google, session |
| [03](chapter-03-firestore-crud.md) | Store tasks in a database | Firestore — documents, collections, CRUD |
| [04](chapter-04-realtime.md) | Tasks update in real-time | onSnapshot, real-time listeners, optimistic UI |
| [05](chapter-05-security-rules.md) | Anyone can read anyone's tasks 😱 | Security Rules (most critical chapter) |

### Part 2: Make It Useful

| # | The Feature | What You Learn |
|---|------------|----------------|
| [06](chapter-06-storage.md) | Attach files to tasks | Storage — upload, download, rules |
| [07](chapter-07-queries.md) | Filter by status, assignee | Queries — where, orderBy, compound |
| [08](chapter-08-indexes.md) | Query fails with index error | Composite indexes, query limitations |
| [09](chapter-09-cloud-functions.md) | Notify when task assigned | Cloud Functions — triggers, events |
| [10](chapter-10-push-notifications.md) | Push notifications to mobile | FCM, topics, tokens |

### Part 3: Make It Scale

| # | The Problem | What You Learn |
|---|------------|----------------|
| [11](chapter-11-data-modeling.md) | Loading team loads ALL tasks | NoSQL modeling, denormalization, subcollections |
| [12](chapter-12-offline.md) | Offline mode (subway users) | Offline persistence, conflict resolution |
| [13](chapter-13-aggregation.md) | Counting tasks is expensive | Aggregation, distributed counters |
| [14](chapter-14-transactions.md) | Batch operations | Batched writes, transactions, atomicity |
| [15](chapter-15-pagination.md) | Paginate 10,000 tasks | Cursors, startAfter, query limits |

### Part 4: Survive Demo Day

| # | The Problem | What You Learn |
|---|------------|----------------|
| [16](chapter-16-cold-starts.md) | Cloud Function cold starts | Optimization, min instances, scheduled |
| [17](chapter-17-cost-optimization.md) | $200 bill with 50 users | Cost optimization, billing alerts |
| [18](chapter-18-rest-api.md) | Need an API for integrations | Callable functions, REST endpoints |
| [19](chapter-19-emulator-suite.md) | Testing without hitting prod | Firebase Emulator Suite |
| [20](chapter-20-demo-day.md) | Demo day investor questions | Security audit, scaling limits, the pitch |

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
