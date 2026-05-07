# Chapter 11: Data Modeling — "Loading a Team Loads ALL Tasks"

[← Chapter 10: Push Notifications](chapter-10-push-notifications.md) | [Chapter 12: Offline Mode →](chapter-12-offline.md)

---

## The Task

Lena: "I open the team page and it takes 3 seconds. We only have 500 tasks. What happens when we have 5,000?"

You check the code. The team page loads the team document AND all tasks in one shot. 500 document reads just to show the team name and member list.

---

## The Problem with Your First Data Model

Your current model:

```
teams/{teamId}
  ├── name, members, createdAt
  └── tasks/ (subcollection)
      └── {taskId}
          ├── title, status, assignee, priority
          └── comments/ (subcollection)
```

The team page component does:

```typescript
// Loads team info (1 read) + ALL tasks (500 reads) = 501 reads
const team = await getDoc(doc(db, "teams", teamId));
const tasks = await getDocs(collection(db, "teams", teamId, "tasks"));
```

Every page load costs 501 reads. At $0.06 per 100K reads, that's not terrible yet — but it will be.

The real problem: **latency**. Downloading 500 documents takes time, especially on mobile.

---

## NoSQL Rule #1: Model for Your Queries

In SQL, you normalize data and join at query time. In NoSQL, you **denormalize** — duplicate data so each query reads exactly what it needs.

Ask: "What does each screen need to display?"

| Screen | Data Needed |
|--------|-------------|
| Team overview | Team name, member count, recent activity |
| Task board | Tasks filtered by status (todo/in_progress/done) |
| My tasks | Tasks assigned to me, across all teams |
| Task detail | One task + its comments |

Each screen should require minimal reads.

---

## Strategy 1: Denormalize Summary Data

Store summary info on the team document so the overview page needs only 1 read:

```typescript
// teams/{teamId}
{
  name: "Acme Startup",
  members: ["uid1", "uid2", "uid3"],
  memberCount: 3,
  taskCounts: {
    todo: 12,
    in_progress: 8,
    done: 45,
  },
  recentTasks: [
    { id: "task-1", title: "Design landing page", status: "in_progress" },
    { id: "task-2", title: "Fix login bug", status: "done" },
    { id: "task-3", title: "Write API docs", status: "todo" },
  ],
  updatedAt: timestamp,
}
```

The team overview page now needs **1 read** instead of 501.

Tradeoff: you must update `taskCounts` and `recentTasks` every time a task changes. Use a Cloud Function:

```typescript
export const updateTeamSummary = onDocumentWritten(
  "teams/{teamId}/tasks/{taskId}",
  async (event) => {
    const teamId = event.params.teamId;
    const tasksRef = db.collection(`teams/${teamId}/tasks`);

    // Count by status
    const todoCount = (await tasksRef.where("status", "==", "todo").count().get()).data().count;
    const inProgressCount = (await tasksRef.where("status", "==", "in_progress").count().get()).data().count;
    const doneCount = (await tasksRef.where("status", "==", "done").count().get()).data().count;

    // Get 3 most recent tasks
    const recentSnap = await tasksRef.orderBy("updatedAt", "desc").limit(3).get();
    const recentTasks = recentSnap.docs.map((d) => ({
      id: d.id,
      title: d.data().title,
      status: d.data().status,
    }));

    await db.doc(`teams/${teamId}`).update({
      taskCounts: { todo: todoCount, in_progress: inProgressCount, done: doneCount },
      recentTasks,
      updatedAt: new Date(),
    });
  }
);
```

---

## Strategy 2: Flatten for Cross-Team Queries

Problem: "Show me all MY tasks across all teams."

With subcollections, you'd need to query every team's tasks subcollection. Instead, maintain a flat collection:

```
// Flat collection for cross-team queries
userTasks/{docId}
  ├── userId: "uid1"
  ├── teamId: "team-abc"
  ├── taskId: "task-123"
  ├── title: "Design landing page"
  ├── status: "in_progress"
  ├── priority: "high"
  ├── dueDate: timestamp
  └── updatedAt: timestamp
```

Now "my tasks" is a single query:

```typescript
const myTasks = query(
  collection(db, "userTasks"),
  where("userId", "==", currentUser.uid),
  where("status", "!=", "done"),
  orderBy("dueDate")
);
```

Keep this in sync with a Cloud Function that writes to `userTasks` whenever a task is created, updated, or deleted.

---

## Strategy 3: Subcollections vs Root Collections

**Subcollections** (`teams/{teamId}/tasks/{taskId}`):
- Natural access control (security rules check parent)
- Easy to query within one team
- Hard to query across teams (need collection group query + index)

**Root collections** (`tasks/{taskId}` with a `teamId` field):
- Easy to query across all tasks
- Security rules must check `teamId` field manually
- Simpler for collection group queries

For SnapTask, subcollections make sense because most queries are within a team. The `userTasks` flat collection handles the cross-team case.

---

## Strategy 4: Embed vs Reference

**Embed** (store data directly):
```typescript
// Task document with embedded assignee info
{
  title: "Design landing page",
  assignee: {
    uid: "uid2",
    displayName: "Lena",
    photoURL: "https://..."
  }
}
```

**Reference** (store only the ID):
```typescript
// Task document with reference
{
  title: "Design landing page",
  assignee: "uid2"  // must fetch user doc separately
}
```

| Approach | Pros | Cons |
|----------|------|------|
| Embed | One read gets everything | Stale if user changes name |
| Reference | Always current | Extra read per task |

For SnapTask: embed `displayName` and `photoURL` on the task. If a user changes their name, a Cloud Function updates all their tasks. Name changes are rare; task reads are constant.

---

## Strategy 5: Limit What You Load

Don't load all tasks. Load what the user sees:

```typescript
// Load only the current board column
const todoTasks = query(
  tasksRef,
  where("status", "==", "todo"),
  orderBy("priority"),
  limit(20)
);

const inProgressTasks = query(
  tasksRef,
  where("status", "==", "in_progress"),
  orderBy("priority"),
  limit(20)
);
```

Three queries × 20 docs = 60 reads instead of 500.

---

## The Revised Data Model

```
firestore/
├── teams/{teamId}
│   ├── name, members, memberCount
│   ├── taskCounts: { todo, in_progress, done }
│   ├── recentTasks: [{ id, title, status }]  ← denormalized
│   └── tasks/{taskId}
│       ├── title, status, priority, dueDate
│       ├── assignee: { uid, displayName, photoURL }  ← embedded
│       ├── createdBy: { uid, displayName }
│       ├── createdAt, updatedAt
│       └── comments/{commentId}
│           ├── text, author: { uid, displayName }
│           └── createdAt
│
├── users/{uid}
│   ├── displayName, email, photoURL
│   ├── teams: ["teamId1", "teamId2"]
│   └── fcmToken
│
└── userTasks/{docId}  ← flat collection for "my tasks" view
    ├── userId, teamId, taskId
    ├── title, status, priority, dueDate
    └── updatedAt
```

---

## When to Denormalize

| Situation | Denormalize? |
|-----------|-------------|
| Data is read 100x more than written | Yes |
| Data changes rarely (user names) | Yes |
| Data changes constantly (task status) | Maybe (use Cloud Functions) |
| You need it in a list view | Yes |
| You only need it in a detail view | No (fetch on demand) |

---

## Common Mistakes

### 1. Normalizing like SQL

```
// ❌ SQL thinking — requires a "join" (extra reads)
tasks: { assigneeId: "uid2" }
users: { uid: "uid2", name: "Lena" }
// To show "Lena" on the task, you need 2 reads

// ✅ NoSQL thinking — embed what you display
tasks: { assignee: { uid: "uid2", displayName: "Lena" } }
// One read shows everything
```

### 2. Not keeping denormalized data in sync

If you embed `displayName` on tasks but never update it when the user changes their name, you have stale data. Always pair denormalization with a Cloud Function that propagates changes.

### 3. Over-denormalizing

Don't embed everything everywhere. If a field changes frequently and is embedded in 10,000 documents, every change triggers 10,000 writes. Be strategic.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Pattern                                 │ When to Use
────────────────────────────────────────┼──────────────────────────────────────
Subcollection                           │ Data belongs to a parent, queried within parent
Root collection                         │ Data queried across all instances
Embed (denormalize)                     │ Displayed in lists, changes rarely
Reference (ID only)                     │ Only needed in detail views
Summary document                        │ Dashboard/overview screens
Flat mirror collection                  │ Cross-parent queries (my tasks)
Cloud Function sync                     │ Keep denormalized data consistent
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marco: "Users are on the subway. No internet. The app just shows a spinner. Can we make it work offline?"

Offline persistence. Firestore's killer feature for mobile.

---

[← Chapter 10: Push Notifications](chapter-10-push-notifications.md) | [Chapter 12: Offline Mode →](chapter-12-offline.md)
