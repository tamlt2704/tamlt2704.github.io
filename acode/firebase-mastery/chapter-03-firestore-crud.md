# Chapter 3: Firestore CRUD — "Store Tasks in a Database"

[← Chapter 2: Authentication](chapter-02-authentication.md) | [Chapter 4: Real-Time Listeners →](chapter-04-realtime.md)

---

## The Task

Lena: "Users can sign in. Now they need to create tasks, edit them, mark them done, delete them. Basic CRUD. By end of day."

---

## Firestore Mental Model

Firestore is a document database. Not tables and rows — **collections** and **documents**.

```
firestore/
├── teams/                    ← collection
│   └── team-abc/             ← document (has an ID)
│       ├── name: "Acme"     ← field
│       ├── members: [...]   ← field (array)
│       └── tasks/            ← subcollection
│           └── task-001/     ← document
│               ├── title: "Design landing page"
│               ├── status: "todo"
│               └── assignee: "uid-123"
```

Rules:
- Collections contain documents
- Documents contain fields (key-value pairs)
- Documents can contain subcollections
- Documents have a size limit of 1 MB
- Collection names and document IDs are strings

---

## Create a Task

```typescript
import { collection, addDoc, serverTimestamp } from "firebase/firestore";
import { db, auth } from "./firebase";

export async function createTask(teamId: string, title: string) {
  const user = auth.currentUser;
  if (!user) throw new Error("Not authenticated");

  const tasksRef = collection(db, "teams", teamId, "tasks");

  const docRef = await addDoc(tasksRef, {
    title,
    status: "todo",
    priority: "medium",
    assignee: null,
    createdBy: user.uid,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  });

  return docRef.id; // auto-generated ID like "abc123xyz"
}
```

`addDoc` creates a document with an auto-generated ID. `serverTimestamp()` uses the server's clock — not the client's — so timestamps are consistent across devices.

---

## Read a Single Task

```typescript
import { doc, getDoc } from "firebase/firestore";

export async function getTask(teamId: string, taskId: string) {
  const taskRef = doc(db, "teams", teamId, "tasks", taskId);
  const snapshot = await getDoc(taskRef);

  if (!snapshot.exists()) {
    throw new Error("Task not found");
  }

  return { id: snapshot.id, ...snapshot.data() };
}
```

`doc()` creates a reference to a specific document. `getDoc()` fetches it once. The snapshot has:
- `snapshot.id` — the document ID
- `snapshot.data()` — the fields as an object
- `snapshot.exists()` — whether the document exists

---

## Read All Tasks in a Team

```typescript
import { collection, getDocs, query, orderBy } from "firebase/firestore";

export async function getTeamTasks(teamId: string) {
  const tasksRef = collection(db, "teams", teamId, "tasks");
  const q = query(tasksRef, orderBy("createdAt", "desc"));
  const snapshot = await getDocs(q);

  return snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
  }));
}
```

`getDocs` fetches all documents in a collection (or query) once. Each document in `snapshot.docs` has the same `.id` and `.data()` interface.

---

## Update a Task

```typescript
import { doc, updateDoc, serverTimestamp } from "firebase/firestore";

export async function updateTask(
  teamId: string,
  taskId: string,
  updates: Partial<{ title: string; status: string; priority: string; assignee: string | null }>
) {
  const taskRef = doc(db, "teams", teamId, "tasks", taskId);

  await updateDoc(taskRef, {
    ...updates,
    updatedAt: serverTimestamp(),
  });
}
```

`updateDoc` merges the provided fields into the existing document. Fields you don't include are untouched.

```typescript
// Only updates status — title, priority, assignee unchanged
await updateTask("team-abc", "task-001", { status: "done" });
```

---

## Delete a Task

```typescript
import { doc, deleteDoc } from "firebase/firestore";

export async function deleteTask(teamId: string, taskId: string) {
  const taskRef = doc(db, "teams", teamId, "tasks", taskId);
  await deleteDoc(taskRef);
}
```

Deleting a document does NOT delete its subcollections. If `task-001` has a `comments` subcollection, those comments become orphaned. You'll need to delete them separately (or use a Cloud Function — Chapter 9).

---

## Set vs Add

Two ways to create documents:

```typescript
import { doc, setDoc, collection, addDoc } from "firebase/firestore";

// addDoc: Firebase generates the ID
const ref = await addDoc(collection(db, "teams"), { name: "Acme" });
// ref.id → "auto-generated-id"

// setDoc: YOU choose the ID
await setDoc(doc(db, "teams", "acme"), { name: "Acme" });
// Document ID is "acme"
```

Use `setDoc` when you have a natural ID (like a user's UID for their profile). Use `addDoc` when you want Firebase to generate a unique ID.

`setDoc` overwrites the entire document by default. To merge:

```typescript
await setDoc(doc(db, "teams", "acme"), { members: ["uid1"] }, { merge: true });
// Only updates 'members', leaves other fields intact
```

---

## Document References vs Collection References

```typescript
// Collection reference — points to a collection
const tasksRef = collection(db, "teams", "team-abc", "tasks");

// Document reference — points to a specific document
const taskRef = doc(db, "teams", "team-abc", "tasks", "task-001");

// You can also get a doc ref from a collection ref
const taskRef2 = doc(tasksRef, "task-001");

// Or a collection ref from a doc ref
const commentsRef = collection(taskRef, "comments");
```

The path alternates: `collection/document/collection/document/...`

---

## Field Types

Firestore supports these field types:

```typescript
await setDoc(doc(db, "example", "types"), {
  // Primitives
  title: "Hello",                    // string
  count: 42,                         // number
  active: true,                      // boolean
  description: null,                 // null

  // Complex
  tags: ["urgent", "frontend"],      // array
  metadata: { source: "web" },       // map (nested object)

  // Special
  createdAt: serverTimestamp(),       // Firestore Timestamp
  location: new GeoPoint(37.7, -122.4), // geographic point
  ref: doc(db, "users", "uid1"),     // document reference
});
```

---

## Array Operations

```typescript
import { arrayUnion, arrayRemove } from "firebase/firestore";

// Add to array (no duplicates)
await updateDoc(taskRef, {
  tags: arrayUnion("urgent"),
});

// Remove from array
await updateDoc(taskRef, {
  tags: arrayRemove("urgent"),
});
```

---

## Increment a Field

```typescript
import { increment } from "firebase/firestore";

await updateDoc(doc(db, "teams", "team-abc"), {
  taskCount: increment(1),  // atomic increment
});

await updateDoc(doc(db, "teams", "team-abc"), {
  taskCount: increment(-1), // atomic decrement
});
```

---

## Delete a Field

```typescript
import { deleteField } from "firebase/firestore";

await updateDoc(taskRef, {
  assignee: deleteField(), // removes the field entirely
});
```

---

## Putting It Together: Task Service

```typescript
// src/services/tasks.ts
import {
  collection,
  doc,
  addDoc,
  getDoc,
  getDocs,
  updateDoc,
  deleteDoc,
  query,
  orderBy,
  serverTimestamp,
} from "firebase/firestore";
import { db, auth } from "../firebase";

const getTasksRef = (teamId: string) =>
  collection(db, "teams", teamId, "tasks");

const getTaskRef = (teamId: string, taskId: string) =>
  doc(db, "teams", teamId, "tasks", taskId);

export const taskService = {
  async create(teamId: string, title: string) {
    const user = auth.currentUser!;
    return addDoc(getTasksRef(teamId), {
      title,
      status: "todo",
      priority: "medium",
      assignee: null,
      createdBy: user.uid,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
  },

  async get(teamId: string, taskId: string) {
    const snap = await getDoc(getTaskRef(teamId, taskId));
    if (!snap.exists()) return null;
    return { id: snap.id, ...snap.data() };
  },

  async list(teamId: string) {
    const q = query(getTasksRef(teamId), orderBy("createdAt", "desc"));
    const snap = await getDocs(q);
    return snap.docs.map((d) => ({ id: d.id, ...d.data() }));
  },

  async update(teamId: string, taskId: string, updates: Record<string, any>) {
    return updateDoc(getTaskRef(teamId, taskId), {
      ...updates,
      updatedAt: serverTimestamp(),
    });
  },

  async remove(teamId: string, taskId: string) {
    return deleteDoc(getTaskRef(teamId, taskId));
  },
};
```

---

## Common Mistakes

### 1. Forgetting that reads cost money

Every `getDoc` and every document in a `getDocs` result is a billed read. Reading a collection of 1,000 documents = 1,000 reads. This matters at scale (Chapter 17).

### 2. Storing derived data

Don't store `taskCount` as a field you manually update. It will drift. Use `increment()` for counters or compute counts with Cloud Functions (Chapter 13).

### 3. Deeply nested subcollections

```
teams/{teamId}/tasks/{taskId}/comments/{commentId}/reactions/{reactionId}
```

This works but makes queries harder. You can't query across subcollections easily. Keep nesting to 2-3 levels max.

### 4. Using `setDoc` when you mean `updateDoc`

`setDoc` without `{ merge: true }` **overwrites the entire document**. If you only want to update `status`, use `updateDoc`.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Operation                       │ Function
────────────────────────────────┼──────────────────────────────────────
Create (auto ID)                │ addDoc(collectionRef, data)
Create (custom ID)              │ setDoc(docRef, data)
Read one                        │ getDoc(docRef)
Read many                       │ getDocs(query)
Update fields                   │ updateDoc(docRef, fields)
Delete document                 │ deleteDoc(docRef)
Merge on set                    │ setDoc(docRef, data, { merge: true })
Server timestamp                │ serverTimestamp()
Atomic increment                │ increment(n)
Array add                       │ arrayUnion(value)
Array remove                    │ arrayRemove(value)
Delete field                    │ deleteField()
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marco: "I created a task on my phone. Lena has the web app open. She doesn't see it until she refreshes. That's not real-time."

Real-time listeners. The feature that makes Firestore different from a regular REST API.

---

[← Chapter 2: Authentication](chapter-02-authentication.md) | [Chapter 4: Real-Time Listeners →](chapter-04-realtime.md)
