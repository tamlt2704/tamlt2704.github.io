# Chapter 4: Real-Time Listeners — "Tasks Should Update Live"

[← Chapter 3: Firestore CRUD](chapter-03-firestore-crud.md) | [Chapter 5: Security Rules →](chapter-05-security-rules.md)

---

## The Task

Marco: "I create a task on my phone. Lena has the web app open on her laptop. She should see it appear *instantly* — no refresh, no polling. That's the whole point of a collaborative app."

---

## The Difference: getDoc vs onSnapshot

```typescript
// ONE-TIME READ — fetches data once, done
const snapshot = await getDoc(taskRef);

// REAL-TIME LISTENER — fires every time the data changes
const unsubscribe = onSnapshot(taskRef, (snapshot) => {
  // This callback fires:
  // 1. Immediately with current data
  // 2. Again every time the document changes
  // 3. Until you call unsubscribe()
});
```

`onSnapshot` is the core of Firebase's real-time capability. It opens a persistent connection to Firestore and pushes changes to your client the moment they happen on the server.

---

## Listen to a Single Document

```typescript
import { doc, onSnapshot } from "firebase/firestore";
import { db } from "./firebase";

function listenToTask(teamId: string, taskId: string, callback: (task: any) => void) {
  const taskRef = doc(db, "teams", teamId, "tasks", taskId);

  const unsubscribe = onSnapshot(taskRef, (snapshot) => {
    if (snapshot.exists()) {
      callback({ id: snapshot.id, ...snapshot.data() });
    } else {
      callback(null); // document was deleted
    }
  });

  return unsubscribe; // call this to stop listening
}
```

---

## Listen to a Collection

```typescript
import { collection, query, orderBy, onSnapshot } from "firebase/firestore";

function listenToTasks(teamId: string, callback: (tasks: any[]) => void) {
  const tasksRef = collection(db, "teams", teamId, "tasks");
  const q = query(tasksRef, orderBy("createdAt", "desc"));

  const unsubscribe = onSnapshot(q, (snapshot) => {
    const tasks = snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
    }));
    callback(tasks);
  });

  return unsubscribe;
}
```

Every time any task in the collection is created, updated, or deleted, the callback fires with the complete updated list.

---

## React Hook: useRealtimeTasks

```tsx
// src/hooks/useRealtimeTasks.ts
import { useState, useEffect } from "react";
import { collection, query, orderBy, onSnapshot } from "firebase/firestore";
import { db } from "../firebase";

interface Task {
  id: string;
  title: string;
  status: string;
  priority: string;
  assignee: string | null;
  createdBy: string;
  createdAt: any;
}

export function useRealtimeTasks(teamId: string | null) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!teamId) return;

    const tasksRef = collection(db, "teams", teamId, "tasks");
    const q = query(tasksRef, orderBy("createdAt", "desc"));

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const tasks = snapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as Task[];
        setTasks(tasks);
        setLoading(false);
      },
      (err) => {
        setError(err.message);
        setLoading(false);
      }
    );

    return unsubscribe; // cleanup when component unmounts or teamId changes
  }, [teamId]);

  return { tasks, loading, error };
}
```

Usage:

```tsx
function TaskBoard({ teamId }: { teamId: string }) {
  const { tasks, loading, error } = useRealtimeTasks(teamId);

  if (loading) return <p>Loading tasks...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>
          {task.title} — {task.status}
        </li>
      ))}
    </ul>
  );
}
```

Open two browser tabs. Create a task in one. It appears in the other instantly.

---

## Snapshot Metadata: What Changed?

```typescript
onSnapshot(q, (snapshot) => {
  snapshot.docChanges().forEach((change) => {
    if (change.type === "added") {
      console.log("New task:", change.doc.data());
    }
    if (change.type === "modified") {
      console.log("Updated task:", change.doc.data());
    }
    if (change.type === "removed") {
      console.log("Deleted task:", change.doc.id);
    }
  });
});
```

`docChanges()` tells you exactly what changed since the last snapshot. Useful for animations (fade in new tasks, highlight updated ones).

---

## Local Writes: Optimistic UI

When you write to Firestore, the `onSnapshot` callback fires **twice**:

1. **Immediately** — with the local write (before the server confirms)
2. **Again** — when the server confirms (usually identical)

You can detect this:

```typescript
onSnapshot(q, (snapshot) => {
  snapshot.docs.forEach((doc) => {
    const source = doc.metadata.hasPendingWrites ? "local" : "server";
    console.log(`${doc.id}: ${source}`);
  });
});
```

This means your UI updates instantly when the user creates a task — no waiting for the server round-trip. If the write fails (e.g., security rule denies it), the snapshot reverts.

This is **optimistic UI** for free.

---

## Snapshot Options

```typescript
onSnapshot(
  q,
  { includeMetadataChanges: true }, // fire on metadata changes too
  (snapshot) => {
    // Now fires when hasPendingWrites changes
    // Useful for showing "saving..." indicators
  }
);
```

---

## Unsubscribing: Why It Matters

Every `onSnapshot` opens a WebSocket connection. If you don't unsubscribe:
- Memory leaks
- Unnecessary reads (billed!)
- Stale callbacks updating unmounted components

Always clean up:

```tsx
useEffect(() => {
  const unsubscribe = onSnapshot(q, callback);
  return unsubscribe; // React calls this on unmount
}, []);
```

---

## Multiple Listeners

A real app has several listeners running simultaneously:

```tsx
function App() {
  const { tasks } = useRealtimeTasks(teamId);       // listener 1
  const { team } = useRealtimeTeam(teamId);         // listener 2
  const { members } = useRealtimeMembers(teamId);   // listener 3

  // All three update independently in real-time
}
```

Each listener is independent. A change to a task doesn't re-fire the team listener.

---

## The Real-Time Architecture

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Browser A   │         │  Firestore   │         │  Browser B   │
│  (Marco)     │         │  (server)    │         │  (Lena)      │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  addDoc(task)          │                        │
       │───────────────────────▶│                        │
       │                        │                        │
       │  onSnapshot fires      │  onSnapshot fires     │
       │◀───────────────────────│───────────────────────▶│
       │  (local, immediate)    │  (server push)        │
       │                        │                        │
```

Marco creates a task. His UI updates instantly (local write). Firestore persists it and pushes the change to Lena's listener. Both see the same state within milliseconds.

---

## Performance: Listener Scope

Listen to what you need, not everything:

```typescript
// ❌ BAD — listens to ALL tasks across ALL teams
onSnapshot(collection(db, "tasks"), callback);

// ✅ GOOD — listens to one team's tasks
onSnapshot(collection(db, "teams", teamId, "tasks"), callback);

// ✅ BETTER — listens to only active tasks
const q = query(
  collection(db, "teams", teamId, "tasks"),
  where("status", "!=", "archived"),
  orderBy("createdAt", "desc"),
  limit(50)
);
onSnapshot(q, callback);
```

Narrower queries = fewer documents transferred = lower cost and better performance.

---

## Error Handling

```typescript
const unsubscribe = onSnapshot(
  q,
  (snapshot) => {
    // success
  },
  (error) => {
    // Listener failed — usually a permission error
    console.error("Listener error:", error.code, error.message);

    // Common errors:
    // "permission-denied" — security rules blocked the read
    // "unavailable" — network issue (will auto-retry)
  }
);
```

If the error is `permission-denied`, the listener stops permanently. You need to fix your security rules or the user's auth state.

If the error is `unavailable`, Firestore automatically retries. The listener resumes when connectivity returns.

---

## Common Mistakes

### 1. Listening without unsubscribing

```tsx
// ❌ Memory leak — new listener on every render
function TaskList({ teamId }) {
  onSnapshot(collection(db, "teams", teamId, "tasks"), (snap) => {
    // This creates a NEW listener every render!
  });
}

// ✅ Use useEffect with cleanup
function TaskList({ teamId }) {
  useEffect(() => {
    const unsub = onSnapshot(/*...*/);
    return unsub;
  }, [teamId]);
}
```

### 2. Fetching inside a listener callback

```typescript
// ❌ Don't fetch related data inside onSnapshot
onSnapshot(tasksQuery, async (snapshot) => {
  for (const doc of snapshot.docs) {
    const user = await getDoc(doc(db, "users", doc.data().assignee)); // N+1 reads!
  }
});

// ✅ Denormalize: store assigneeName on the task document
// Or use a separate listener for users
```

### 3. Not limiting collection listeners

Listening to a collection with 10,000 documents means downloading all 10,000 on first load, then receiving every change. Use `limit()` and pagination (Chapter 15).

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Pattern                                 │ What It Does
────────────────────────────────────────┼──────────────────────────────────────
onSnapshot(docRef, cb)                  │ Listen to one document
onSnapshot(query, cb)                   │ Listen to a query/collection
onSnapshot(q, successCb, errorCb)       │ Listen with error handling
snapshot.docChanges()                   │ Get added/modified/removed docs
doc.metadata.hasPendingWrites           │ True if local write not yet confirmed
{ includeMetadataChanges: true }        │ Fire on metadata changes too
unsubscribe()                           │ Stop listening (cleanup)
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "Wait. I just opened the app in an incognito window — no login — and I can see ALL the tasks. For EVERY team. That's... bad."

You: "Yeah. We haven't written any security rules yet."

Lena: "FIX IT. NOW."

Security Rules. The most important chapter in this series.

---

[← Chapter 3: Firestore CRUD](chapter-03-firestore-crud.md) | [Chapter 5: Security Rules →](chapter-05-security-rules.md)
