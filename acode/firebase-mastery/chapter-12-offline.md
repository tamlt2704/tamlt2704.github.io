# Chapter 12: Offline Mode — "Subway Users"

[← Chapter 11: Data Modeling](chapter-11-data-modeling.md) | [Chapter 13: Aggregation →](chapter-13-aggregation.md)

---

## The Task

Marco: "Half our users are on the subway during their commute. No internet. The app shows a spinner and they can't do anything. They switch to a competitor that works offline."

---

## Firestore Offline Persistence

Firestore has built-in offline support. When enabled, it:

1. Caches every document the client reads
2. Serves reads from cache when offline
3. Queues writes locally when offline
4. Syncs everything when connectivity returns

On mobile (iOS/Android), offline persistence is enabled by default. On web, you must opt in.

---

## Enable Offline Persistence (Web)

```typescript
// src/firebase.ts
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager } from "firebase/firestore";

const app = initializeApp(firebaseConfig);

// Enable offline persistence with multi-tab support
const db = initializeFirestore(app, {
  localCache: persistentLocalCache({
    tabManager: persistentMultipleTabManager(),
  }),
});

export { db };
```

That's it. Now:
- Every document read is cached in IndexedDB
- Queries return cached results when offline
- Writes are queued and synced when back online

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Online                                                      │
│                                                              │
│  Client ──read──▶ Server ──response──▶ Client + Cache       │
│  Client ──write─▶ Server ──confirm──▶ Client + Cache        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Offline                                                     │
│                                                              │
│  Client ──read──▶ Cache (instant, from IndexedDB)           │
│  Client ──write─▶ Local Queue (pending)                     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Back Online                                                 │
│                                                              │
│  Local Queue ──sync──▶ Server                               │
│  Server ──updates──▶ Cache + Listeners                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Offline Reads

With persistence enabled, `onSnapshot` listeners work offline:

```typescript
// This works offline — returns cached data
const unsubscribe = onSnapshot(
  query(tasksRef, where("status", "==", "todo")),
  (snapshot) => {
    // snapshot.docs contains cached documents
    // snapshot.metadata.fromCache === true when offline
    const tasks = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
    setTasks(tasks);
  }
);
```

`getDoc` and `getDocs` also work offline — they return cached data.

---

## Detecting Offline State

```typescript
onSnapshot(q, { includeMetadataChanges: true }, (snapshot) => {
  if (snapshot.metadata.fromCache) {
    // Data is from local cache — user might be offline
    showOfflineIndicator();
  } else {
    // Data is fresh from server
    hideOfflineIndicator();
  }
});
```

Or listen to Firestore's network state:

```typescript
import { enableNetwork, disableNetwork } from "firebase/firestore";

// Manually go offline (useful for testing)
await disableNetwork(db);

// Manually go back online
await enableNetwork(db);
```

---

## Offline Writes

Writes work offline too. They're queued locally and synced when connectivity returns:

```typescript
// This succeeds immediately, even offline
await addDoc(collection(db, "teams", teamId, "tasks"), {
  title: "New task from subway",
  status: "todo",
  createdBy: user.uid,
  createdAt: serverTimestamp(), // resolved when synced
});
```

The `onSnapshot` listener fires immediately with the local write (`hasPendingWrites: true`). When the write syncs to the server, the listener fires again with the confirmed data.

---

## Pending Writes Indicator

Show users which changes haven't synced yet:

```tsx
function TaskItem({ task, snapshot }: { task: Task; snapshot: DocumentSnapshot }) {
  const isPending = snapshot.metadata.hasPendingWrites;

  return (
    <li className={isPending ? "pending" : ""}>
      {task.title}
      {isPending && <span className="sync-icon">⏳ Syncing...</span>}
    </li>
  );
}
```

---

## Conflict Resolution

What happens if two users edit the same task offline?

Firestore uses **last-write-wins**. When both devices come back online, the last write to reach the server overwrites the other. There's no automatic merge.

For SnapTask, this is usually fine — task updates are small (status change, title edit). But for collaborative text editing, you'd need a different approach (CRDTs, operational transforms).

Strategies to minimize conflicts:

```typescript
// 1. Use field-level updates (not full document overwrites)
await updateDoc(taskRef, { status: "done" }); // only touches status
// Another user updating "title" won't conflict

// 2. Use atomic operations
await updateDoc(taskRef, { commentCount: increment(1) });
// Two increments both apply correctly

// 3. Use arrayUnion for lists
await updateDoc(taskRef, { tags: arrayUnion("urgent") });
// Two different tags both get added
```

---

## Cache Size Management

By default, Firestore caches up to 40 MB. Configure it:

```typescript
import { persistentLocalCache, CACHE_SIZE_UNLIMITED } from "firebase/firestore";

const db = initializeFirestore(app, {
  localCache: persistentLocalCache({
    cacheSizeBytes: 100 * 1024 * 1024, // 100 MB
    // or: CACHE_SIZE_UNLIMITED (not recommended)
  }),
});
```

When the cache exceeds the limit, Firestore garbage-collects the least recently used documents.

---

## Multi-Tab Support

Without multi-tab support, only one tab manages the cache. Other tabs make direct network requests:

```typescript
// Single-tab (default for persistentLocalCache without tabManager)
persistentLocalCache()

// Multi-tab — all tabs share the cache, one tab manages sync
persistentLocalCache({
  tabManager: persistentMultipleTabManager(),
})
```

With multi-tab, if the user has SnapTask open in 3 tabs, only one maintains the WebSocket connection. The others read from the shared cache.

---

## Offline-First UI Patterns

### 1. Optimistic Updates

```typescript
// The UI updates immediately — don't wait for server confirmation
async function markTaskDone(taskId: string) {
  // Update local state immediately
  setTasks((prev) =>
    prev.map((t) => (t.id === taskId ? { ...t, status: "done" } : t))
  );

  // Write to Firestore (queued if offline)
  await updateDoc(doc(db, "teams", teamId, "tasks", taskId), {
    status: "done",
  });
}
```

### 2. Queue Indicator

```tsx
function SyncStatus() {
  const [pendingWrites, setPendingWrites] = useState(0);

  useEffect(() => {
    const unsubscribe = onSnapshot(
      query(tasksRef),
      { includeMetadataChanges: true },
      (snapshot) => {
        const pending = snapshot.docs.filter(
          (d) => d.metadata.hasPendingWrites
        ).length;
        setPendingWrites(pending);
      }
    );
    return unsubscribe;
  }, []);

  if (pendingWrites === 0) return null;

  return (
    <div className="sync-bar">
      {pendingWrites} change{pendingWrites > 1 ? "s" : ""} waiting to sync
    </div>
  );
}
```

### 3. Disable Destructive Actions Offline

```tsx
function DeleteButton({ taskId, isOnline }) {
  return (
    <button
      onClick={() => deleteTask(taskId)}
      disabled={!isOnline}
      title={!isOnline ? "Can't delete while offline" : "Delete task"}
    >
      Delete
    </button>
  );
}
```

---

## Limitations

1. **`serverTimestamp()` resolves to `null` locally** — until the write syncs, timestamp fields are null in the local cache. Handle this:

```typescript
const createdAt = task.createdAt?.toDate() || new Date(); // fallback
```

2. **Security rule failures are delayed** — if a write violates security rules, you won't know until the device is back online. The local write appears to succeed, then reverts.

3. **No offline queries on unread data** — you can only query documents that have been previously read and cached. You can't discover new documents offline.

4. **Transaction failures** — transactions require server communication. They fail immediately when offline.

---

## Common Mistakes

### 1. Not enabling persistence on web

Mobile SDKs have it on by default. Web doesn't. If you forget `persistentLocalCache`, the app shows nothing offline.

### 2. Relying on `serverTimestamp()` for display

```typescript
// ❌ Shows "Invalid Date" offline
<span>{task.createdAt.toDate().toLocaleDateString()}</span>

// ✅ Handle null timestamps
<span>{task.createdAt ? task.createdAt.toDate().toLocaleDateString() : "Just now"}</span>
```

### 3. Not testing offline behavior

Use Chrome DevTools → Network → Offline to simulate. Or use `disableNetwork(db)` in code.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Feature                                 │ Details
────────────────────────────────────────┼──────────────────────────────────────
persistentLocalCache()                  │ Enable offline persistence (web)
persistentMultipleTabManager()          │ Share cache across tabs
snapshot.metadata.fromCache             │ True if data is from cache
snapshot.metadata.hasPendingWrites      │ True if write hasn't synced
disableNetwork(db)                      │ Force offline (testing)
enableNetwork(db)                       │ Force online
serverTimestamp()                       │ Null locally until synced
Last-write-wins                         │ Default conflict resolution
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "The dashboard needs to show 'Total tasks: 847'. But counting all documents means reading all of them. That's expensive."

Aggregation patterns. How to count without reading every document.

---

[← Chapter 11: Data Modeling](chapter-11-data-modeling.md) | [Chapter 13: Aggregation →](chapter-13-aggregation.md)
