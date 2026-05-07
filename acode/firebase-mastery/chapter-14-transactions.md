# Chapter 14: Transactions & Batched Writes — "Atomic Operations"

[← Chapter 13: Aggregation](chapter-13-aggregation.md) | [Chapter 15: Pagination →](chapter-15-pagination.md)

---

## The Task

Lena: "When a user joins a team, we need to add them to the team's `members` array AND add the team to the user's `teams` array. If one write fails and the other succeeds, we have inconsistent data."

---

## The Consistency Problem

```typescript
// ❌ Two independent writes — if the second fails, data is inconsistent
await updateDoc(doc(db, "teams", teamId), {
  members: arrayUnion(userId),
});
// What if the app crashes here? User is in team but team isn't in user's list.
await updateDoc(doc(db, "users", userId), {
  teams: arrayUnion(teamId),
});
```

You need atomicity: either both writes succeed, or neither does.

---

## Batched Writes

A batch groups multiple writes into a single atomic operation. All writes succeed or all fail.

```typescript
import { writeBatch, doc, arrayUnion, serverTimestamp } from "firebase/firestore";
import { db } from "./firebase";

export async function joinTeam(userId: string, teamId: string) {
  const batch = writeBatch(db);

  // Write 1: Add user to team
  const teamRef = doc(db, "teams", teamId);
  batch.update(teamRef, {
    members: arrayUnion(userId),
  });

  // Write 2: Add team to user
  const userRef = doc(db, "users", userId);
  batch.update(userRef, {
    teams: arrayUnion(teamId),
  });

  // Write 3: Log the join event
  const eventRef = doc(db, "teams", teamId, "events", `join_${userId}`);
  batch.set(eventRef, {
    type: "member_joined",
    userId,
    timestamp: serverTimestamp(),
  });

  // All three writes happen atomically
  await batch.commit();
}
```

Batch rules:
- Max 500 operations per batch
- All operations must be writes (no reads)
- All documents must be in the same database
- Atomic: all succeed or all fail

---

## Transactions

When you need to **read** data before deciding what to write, use a transaction:

```typescript
import { runTransaction, doc } from "firebase/firestore";

export async function assignTask(teamId: string, taskId: string, assigneeId: string) {
  await runTransaction(db, async (transaction) => {
    // Read the task first
    const taskRef = doc(db, "teams", teamId, "tasks", taskId);
    const taskDoc = await transaction.get(taskRef);

    if (!taskDoc.exists()) {
      throw new Error("Task not found");
    }

    const task = taskDoc.data();

    // Check if already assigned to someone else
    if (task.assignee && task.assignee !== assigneeId) {
      // Unassign from previous user's task list
      const prevAssigneeRef = doc(db, "userTasks", `${task.assignee}_${taskId}`);
      transaction.delete(prevAssigneeRef);
    }

    // Assign to new user
    transaction.update(taskRef, {
      assignee: assigneeId,
      updatedAt: serverTimestamp(),
    });

    // Add to new assignee's task list
    const userTaskRef = doc(db, "userTasks", `${assigneeId}_${taskId}`);
    transaction.set(userTaskRef, {
      userId: assigneeId,
      teamId,
      taskId,
      title: task.title,
      status: task.status,
      assignedAt: serverTimestamp(),
    });
  });
}
```

Transaction rules:
- Reads must come before writes
- If any read document changes before the transaction commits, it retries (up to 5 times)
- Max 500 operations
- Transactions fail if offline (they require server communication)

---

## Transaction vs Batch: When to Use Which

| Scenario | Use |
|----------|-----|
| Multiple writes, no reads needed | Batch |
| Need to read before writing | Transaction |
| Conditional write (check-then-set) | Transaction |
| Bulk import/update | Batch |
| Counter increment based on current value | Transaction |
| Simple multi-document update | Batch |

---

## Transaction Retry Behavior

```typescript
await runTransaction(db, async (transaction) => {
  const taskDoc = await transaction.get(taskRef);
  const currentCount = taskDoc.data().commentCount;

  // If another client modifies this document between our read and write,
  // the transaction retries automatically (up to 5 times)
  transaction.update(taskRef, { commentCount: currentCount + 1 });
});
```

If two users assign the same task simultaneously:
1. User A reads the task (assignee: null)
2. User B reads the task (assignee: null)
3. User A writes (assignee: "userA") — succeeds
4. User B tries to write — document changed since read → **retry**
5. User B reads again (assignee: "userA") — now sees A's assignment
6. User B writes (assignee: "userB") — succeeds, overwriting A

This is optimistic concurrency control.

---

## Practical Example: Move Task Between Columns

```typescript
export async function moveTask(
  teamId: string,
  taskId: string,
  newStatus: string
) {
  const batch = writeBatch(db);

  const taskRef = doc(db, "teams", teamId, "tasks", taskId);

  // Update task status
  batch.update(taskRef, {
    status: newStatus,
    updatedAt: serverTimestamp(),
  });

  // Update team counters (decrement old, increment new)
  // Note: For accurate counters, use a transaction or Cloud Function
  // This simplified version works if you trust the client
  const teamRef = doc(db, "teams", teamId);
  batch.update(teamRef, {
    [`taskCounts.${newStatus}`]: increment(1),
    updatedAt: serverTimestamp(),
  });

  await batch.commit();
}
```

For the counter decrement (old status), you'd need a transaction since you need to read the current status first:

```typescript
export async function moveTask(teamId: string, taskId: string, newStatus: string) {
  await runTransaction(db, async (transaction) => {
    const taskRef = doc(db, "teams", teamId, "tasks", taskId);
    const taskDoc = await transaction.get(taskRef);
    const oldStatus = taskDoc.data()?.status;

    if (oldStatus === newStatus) return; // no change

    const teamRef = doc(db, "teams", teamId);

    transaction.update(taskRef, {
      status: newStatus,
      updatedAt: serverTimestamp(),
    });

    transaction.update(teamRef, {
      [`taskCounts.${oldStatus}`]: increment(-1),
      [`taskCounts.${newStatus}`]: increment(1),
    });
  });
}
```

---

## Bulk Operations

For operations exceeding 500 documents, chunk into multiple batches:

```typescript
export async function archiveCompletedTasks(teamId: string) {
  const tasksRef = collection(db, "teams", teamId, "tasks");
  const q = query(tasksRef, where("status", "==", "done"));
  const snapshot = await getDocs(q);

  // Chunk into batches of 500
  const chunks: DocumentSnapshot[][] = [];
  for (let i = 0; i < snapshot.docs.length; i += 500) {
    chunks.push(snapshot.docs.slice(i, i + 500));
  }

  for (const chunk of chunks) {
    const batch = writeBatch(db);
    for (const docSnap of chunk) {
      batch.update(docSnap.ref, { status: "archived" });
    }
    await batch.commit();
  }
}
```

Note: this is NOT atomic across chunks. If the second batch fails, the first has already committed. For true atomicity across 500+ documents, use Cloud Functions with the Admin SDK.

---

## Common Mistakes

### 1. Reads after writes in a transaction

```typescript
// ❌ FAILS — reads must come before writes
await runTransaction(db, async (transaction) => {
  transaction.update(taskRef, { status: "done" });
  const taskDoc = await transaction.get(taskRef); // Error!
});

// ✅ Read first, then write
await runTransaction(db, async (transaction) => {
  const taskDoc = await transaction.get(taskRef);
  transaction.update(taskRef, { status: "done" });
});
```

### 2. Using transactions offline

Transactions require server communication. They throw immediately when offline. Use batched writes for offline-capable atomic operations (but note: batches don't support read-then-write logic).

### 3. Long-running transactions

Transactions hold locks. If your transaction does expensive async work (API calls, complex computation), it blocks other transactions on the same documents. Keep transactions fast.

### 4. Exceeding 500 operations

```typescript
// ❌ Batch with 1000 operations — fails
const batch = writeBatch(db);
for (let i = 0; i < 1000; i++) {
  batch.set(doc(collection(db, "items")), { index: i });
}
await batch.commit(); // Error: max 500 operations

// ✅ Split into multiple batches
```

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Feature                                 │ Details
────────────────────────────────────────┼──────────────────────────────────────
writeBatch(db)                          │ Create a batch
batch.set(ref, data)                    │ Add a set operation
batch.update(ref, data)                 │ Add an update operation
batch.delete(ref)                       │ Add a delete operation
batch.commit()                          │ Execute all operations atomically
runTransaction(db, async (t) => {})     │ Read-then-write atomically
transaction.get(ref)                    │ Read in transaction
transaction.set/update/delete           │ Write in transaction
Max operations per batch/transaction    │ 500
Transaction retries                     │ Up to 5 times on conflict
Works offline?                          │ Batch: yes, Transaction: no
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "We have 10,000 tasks now. Loading them all is insane. I need pages — show 20 at a time, with a 'Load More' button."

Pagination. Cursors, `startAfter`, and the art of not loading everything.

---

[← Chapter 13: Aggregation](chapter-13-aggregation.md) | [Chapter 15: Pagination →](chapter-15-pagination.md)
