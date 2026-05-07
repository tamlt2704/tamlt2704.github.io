# Chapter 13: Aggregation — "Counting Tasks Is Expensive"

[← Chapter 12: Offline Mode](chapter-12-offline.md) | [Chapter 14: Transactions →](chapter-14-transactions.md)

---

## The Task

Lena: "The dashboard shows 'Total tasks: 847'. But to get that number, we're reading all 847 documents. That's 847 reads just to display a number."

---

## The Problem

Firestore doesn't have `SELECT COUNT(*)`. Historically, the only way to count documents was to read them all:

```typescript
// ❌ Reads ALL documents just to count them
const snapshot = await getDocs(collection(db, "teams", teamId, "tasks"));
const count = snapshot.size; // 847 reads billed!
```

At scale, this is expensive and slow.

---

## Solution 1: Count Queries (Built-in)

Firestore now supports server-side count queries:

```typescript
import { collection, query, where, getCountFromServer } from "firebase/firestore";

// Count all tasks in a team
const tasksRef = collection(db, "teams", teamId, "tasks");
const snapshot = await getCountFromServer(query(tasksRef));
console.log(snapshot.data().count); // 847

// Count with filters
const todoCount = await getCountFromServer(
  query(tasksRef, where("status", "==", "todo"))
);
console.log(todoCount.data().count); // 142
```

`getCountFromServer` counts documents without downloading them. It's billed as 1 read per 1,000 documents counted (much cheaper than reading all documents).

---

## Solution 2: Distributed Counters

For high-write scenarios (thousands of increments per second), a single counter document becomes a bottleneck. Use distributed counters:

```typescript
// Create counter shards
const NUM_SHARDS = 10;

async function initializeCounter(counterRef: DocumentReference) {
  for (let i = 0; i < NUM_SHARDS; i++) {
    await setDoc(doc(collection(counterRef, "shards"), `${i}`), { count: 0 });
  }
}

// Increment a random shard
async function incrementCounter(counterRef: DocumentReference) {
  const shardId = Math.floor(Math.random() * NUM_SHARDS);
  const shardRef = doc(collection(counterRef, "shards"), `${shardId}`);
  await updateDoc(shardRef, { count: increment(1) });
}

// Read total count (sum all shards)
async function getCount(counterRef: DocumentReference): Promise<number> {
  const shardsSnapshot = await getDocs(collection(counterRef, "shards"));
  let total = 0;
  shardsSnapshot.forEach((doc) => {
    total += doc.data().count;
  });
  return total;
}
```

Each shard can handle ~1 write/second. 10 shards = 10 writes/second without contention.

For SnapTask, this is overkill. A single counter field with `increment()` handles the load fine. Distributed counters are for viral apps with thousands of concurrent writes.

---

## Solution 3: Maintain Counters with Cloud Functions

The most common pattern: update a counter whenever a document is created or deleted.

```typescript
// functions/src/counters.ts
import { onDocumentCreated, onDocumentDeleted } from "firebase-functions/v2/firestore";
import { getFirestore, FieldValue } from "firebase-admin/firestore";

const db = getFirestore();

export const incrementTaskCount = onDocumentCreated(
  "teams/{teamId}/tasks/{taskId}",
  async (event) => {
    const teamId = event.params.teamId;
    const status = event.data?.data()?.status || "todo";

    await db.doc(`teams/${teamId}`).update({
      [`taskCounts.${status}`]: FieldValue.increment(1),
      "taskCounts.total": FieldValue.increment(1),
    });
  }
);

export const decrementTaskCount = onDocumentDeleted(
  "teams/{teamId}/tasks/{taskId}",
  async (event) => {
    const teamId = event.params.teamId;
    const status = event.data?.data()?.status || "todo";

    await db.doc(`teams/${teamId}`).update({
      [`taskCounts.${status}`]: FieldValue.increment(-1),
      "taskCounts.total": FieldValue.increment(-1),
    });
  }
);

export const updateTaskStatusCount = onDocumentUpdated(
  "teams/{teamId}/tasks/{taskId}",
  async (event) => {
    const before = event.data?.before.data();
    const after = event.data?.after.data();

    if (!before || !after || before.status === after.status) return;

    const teamId = event.params.teamId;

    await db.doc(`teams/${teamId}`).update({
      [`taskCounts.${before.status}`]: FieldValue.increment(-1),
      [`taskCounts.${after.status}`]: FieldValue.increment(1),
    });
  }
);
```

Now the team document always has accurate counts:

```typescript
// 1 read instead of 847
const teamDoc = await getDoc(doc(db, "teams", teamId));
const counts = teamDoc.data().taskCounts;
// { total: 847, todo: 142, in_progress: 89, done: 616 }
```

---

## Solution 4: Aggregation Queries (Sum, Average)

Firestore also supports sum and average:

```typescript
import { collection, query, where, getAggregateFromServer, sum, average } from "firebase/firestore";

// Sum of estimated hours
const result = await getAggregateFromServer(
  query(collection(db, "teams", teamId, "tasks")),
  { totalHours: sum("estimatedHours") }
);
console.log(result.data().totalHours); // 234.5

// Average priority score
const avgResult = await getAggregateFromServer(
  query(collection(db, "teams", teamId, "tasks"), where("status", "==", "todo")),
  { avgPriority: average("priorityScore") }
);
console.log(avgResult.data().avgPriority); // 3.2
```

---

## Choosing the Right Approach

| Scenario | Best Approach |
|----------|--------------|
| Display count on a dashboard | Maintained counter (Cloud Function) |
| One-off analytics query | `getCountFromServer` |
| High-write counter (likes, views) | Distributed counters |
| Sum/average for reports | `getAggregateFromServer` |
| Real-time count updates | Maintained counter + `onSnapshot` |

---

## Real-Time Counters

Since the counter is stored as a field on the team document, you get real-time updates for free:

```typescript
// Real-time task counts
onSnapshot(doc(db, "teams", teamId), (snapshot) => {
  const counts = snapshot.data()?.taskCounts;
  setTaskCounts(counts); // UI updates instantly when counts change
});
```

---

## Common Mistakes

### 1. Counting client-side

```typescript
// ❌ Downloads all documents to count them
const snap = await getDocs(tasksRef);
const count = snap.size; // expensive!

// ✅ Use server-side count
const snap = await getCountFromServer(query(tasksRef));
const count = snap.data().count; // cheap!
```

### 2. Counter drift

If a Cloud Function fails or is retried, counters can drift. Periodically reconcile:

```typescript
// Scheduled function to fix counter drift
export const reconcileCounts = onSchedule("every 24 hours", async () => {
  const teamsSnapshot = await db.collection("teams").get();

  for (const teamDoc of teamsSnapshot.docs) {
    const tasksRef = db.collection(`teams/${teamDoc.id}/tasks`);
    const todoCount = (await tasksRef.where("status", "==", "todo").count().get()).data().count;
    const inProgressCount = (await tasksRef.where("status", "==", "in_progress").count().get()).data().count;
    const doneCount = (await tasksRef.where("status", "==", "done").count().get()).data().count;

    await teamDoc.ref.update({
      taskCounts: {
        total: todoCount + inProgressCount + doneCount,
        todo: todoCount,
        in_progress: inProgressCount,
        done: doneCount,
      },
    });
  }
});
```

### 3. Not handling negative counts

If a delete trigger fires but the create trigger failed, you get negative counts. Guard against it:

```typescript
// In your UI
const displayCount = Math.max(0, counts.todo);
```

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Method                                  │ Cost / Use Case
────────────────────────────────────────┼──────────────────────────────────────
getCountFromServer(query)               │ 1 read per 1K docs counted
getAggregateFromServer(query, { sum })  │ 1 read per 1K docs
Maintained counter (Cloud Function)     │ 1 read to display, 1 write per change
Distributed counters                    │ High-write scenarios (1K+ writes/sec)
getDocs(query).size                     │ ❌ Reads all docs (expensive)
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "When a user joins a team, I need to add them to the team AND update their user profile. If one fails, we're in an inconsistent state."

Transactions and batched writes. Atomic operations in Firestore.

---

[← Chapter 12: Offline Mode](chapter-12-offline.md) | [Chapter 14: Transactions →](chapter-14-transactions.md)
