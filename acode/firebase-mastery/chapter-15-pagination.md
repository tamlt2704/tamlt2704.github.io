# Chapter 15: Pagination — "Paginate 10,000 Tasks"

[← Chapter 14: Transactions](chapter-14-transactions.md) | [Chapter 16: Cold Starts →](chapter-16-cold-starts.md)

---

## The Task

Lena: "We have 10,000 tasks across all teams. The task list tries to load them all. The page freezes. I need pages — 20 tasks at a time, with 'Load More'."

---

## Firestore Pagination: Cursor-Based

Firestore doesn't support offset-based pagination (`SKIP 40 LIMIT 20`). It uses **cursors** — you tell Firestore "start after this document" and it returns the next page.

```typescript
import {
  collection, query, orderBy, limit, startAfter,
  getDocs, QueryDocumentSnapshot,
} from "firebase/firestore";

const PAGE_SIZE = 20;

// First page
async function getFirstPage(teamId: string) {
  const q = query(
    collection(db, "teams", teamId, "tasks"),
    orderBy("createdAt", "desc"),
    limit(PAGE_SIZE)
  );

  const snapshot = await getDocs(q);
  const tasks = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
  const lastDoc = snapshot.docs[snapshot.docs.length - 1];

  return { tasks, lastDoc };
}

// Next page (pass the last document from previous page)
async function getNextPage(teamId: string, lastDoc: QueryDocumentSnapshot) {
  const q = query(
    collection(db, "teams", teamId, "tasks"),
    orderBy("createdAt", "desc"),
    startAfter(lastDoc),
    limit(PAGE_SIZE)
  );

  const snapshot = await getDocs(q);
  const tasks = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
  const newLastDoc = snapshot.docs[snapshot.docs.length - 1];
  const hasMore = snapshot.docs.length === PAGE_SIZE;

  return { tasks, lastDoc: newLastDoc, hasMore };
}
```

---

## React Hook: Paginated Tasks

```tsx
// src/hooks/usePaginatedTasks.ts
import { useState, useCallback } from "react";
import {
  collection, query, orderBy, limit, startAfter,
  getDocs, QueryDocumentSnapshot, QueryConstraint, where,
} from "firebase/firestore";
import { db } from "../firebase";

const PAGE_SIZE = 20;

interface UsePaginatedTasksOptions {
  teamId: string;
  status?: string;
}

export function usePaginatedTasks({ teamId, status }: UsePaginatedTasksOptions) {
  const [tasks, setTasks] = useState<any[]>([]);
  const [lastDoc, setLastDoc] = useState<QueryDocumentSnapshot | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const buildQuery = useCallback(
    (cursor?: QueryDocumentSnapshot) => {
      const constraints: QueryConstraint[] = [];

      if (status) {
        constraints.push(where("status", "==", status));
      }

      constraints.push(orderBy("createdAt", "desc"));

      if (cursor) {
        constraints.push(startAfter(cursor));
      }

      constraints.push(limit(PAGE_SIZE));

      return query(collection(db, "teams", teamId, "tasks"), ...constraints);
    },
    [teamId, status]
  );

  const loadFirst = useCallback(async () => {
    setLoading(true);
    const q = buildQuery();
    const snapshot = await getDocs(q);

    const newTasks = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
    setTasks(newTasks);
    setLastDoc(snapshot.docs[snapshot.docs.length - 1] || null);
    setHasMore(snapshot.docs.length === PAGE_SIZE);
    setLoading(false);
  }, [buildQuery]);

  const loadMore = useCallback(async () => {
    if (!lastDoc || !hasMore || loading) return;

    setLoading(true);
    const q = buildQuery(lastDoc);
    const snapshot = await getDocs(q);

    const newTasks = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
    setTasks((prev) => [...prev, ...newTasks]);
    setLastDoc(snapshot.docs[snapshot.docs.length - 1] || null);
    setHasMore(snapshot.docs.length === PAGE_SIZE);
    setLoading(false);
  }, [lastDoc, hasMore, loading, buildQuery]);

  return { tasks, loading, hasMore, loadFirst, loadMore };
}
```

Usage:

```tsx
function TaskList({ teamId }: { teamId: string }) {
  const { tasks, loading, hasMore, loadFirst, loadMore } = usePaginatedTasks({
    teamId,
    status: "todo",
  });

  useEffect(() => {
    loadFirst();
  }, [loadFirst]);

  return (
    <div>
      <ul>
        {tasks.map((task) => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>

      {loading && <p>Loading...</p>}

      {hasMore && !loading && (
        <button onClick={loadMore}>Load More</button>
      )}

      {!hasMore && <p>No more tasks</p>}
    </div>
  );
}
```

---

## Cursor Functions

```typescript
// Start after a document snapshot
startAfter(documentSnapshot)

// Start after field values (must match orderBy fields)
startAfter(timestampValue)

// Start at (inclusive)
startAt(documentSnapshot)

// End before / end at
endBefore(documentSnapshot)
endAt(documentSnapshot)
```

---

## Real-Time Pagination

Combining pagination with real-time listeners is tricky. The simplest approach: use real-time for the first page, one-time reads for subsequent pages.

```typescript
// First page: real-time (new tasks appear instantly)
const firstPageQuery = query(tasksRef, orderBy("createdAt", "desc"), limit(PAGE_SIZE));
const unsubscribe = onSnapshot(firstPageQuery, (snapshot) => {
  setFirstPageTasks(snapshot.docs.map(/*...*/));
  setLastDoc(snapshot.docs[snapshot.docs.length - 1]);
});

// Subsequent pages: one-time reads (load more button)
async function loadMore() {
  const nextQuery = query(tasksRef, orderBy("createdAt", "desc"), startAfter(lastDoc), limit(PAGE_SIZE));
  const snapshot = await getDocs(nextQuery);
  setAdditionalTasks((prev) => [...prev, ...snapshot.docs.map(/*...*/)]);
}
```

---

## Infinite Scroll

```tsx
import { useEffect, useRef } from "react";

function InfiniteTaskList({ teamId }: { teamId: string }) {
  const { tasks, loading, hasMore, loadFirst, loadMore } = usePaginatedTasks({ teamId });
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    loadFirst();
  }, [loadFirst]);

  useEffect(() => {
    if (observerRef.current) observerRef.current.disconnect();

    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore && !loading) {
        loadMore();
      }
    });

    if (sentinelRef.current) {
      observerRef.current.observe(sentinelRef.current);
    }

    return () => observerRef.current?.disconnect();
  }, [hasMore, loading, loadMore]);

  return (
    <div>
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
      <div ref={sentinelRef} style={{ height: 1 }} />
      {loading && <Spinner />}
    </div>
  );
}
```

---

## Why No Offset Pagination?

SQL databases support `OFFSET 100 LIMIT 20` — skip 100 rows, return 20. Firestore doesn't because:

1. **Performance**: Offset requires scanning and discarding documents. With 1 million documents, `OFFSET 999980` scans nearly all of them.
2. **Cost**: Skipped documents are still read (and billed in SQL-based systems).
3. **Consistency**: If documents are added/removed between pages, offset-based pagination shows duplicates or skips items.

Cursor-based pagination is O(1) regardless of position — "start after document X" goes directly to X's position in the index.

---

## Page Numbers (If You Really Need Them)

You can't jump to "page 5" directly. Workarounds:

```typescript
// Store page cursors as you paginate forward
const pageCursors: QueryDocumentSnapshot[] = [];

// When user goes to page 3, use pageCursors[2]
// Only works if they've visited pages 1 and 2 first

// Alternative: use a known field value as cursor
// "Show tasks created after 2024-01-15"
const q = query(tasksRef, orderBy("createdAt"), startAfter(new Date("2024-01-15")), limit(20));
```

For most apps, "Load More" or infinite scroll is better UX than page numbers.

---

## Common Mistakes

### 1. Not passing the document snapshot

```typescript
// ❌ Passing a field value without matching orderBy
startAfter("2024-01-15") // only works if orderBy is on a date field

// ✅ Pass the actual document snapshot — works with any orderBy
startAfter(lastDocumentSnapshot)
```

### 2. Changing filters without resetting pagination

```typescript
// ❌ User changes status filter but cursor is from old query
// Results will be wrong or empty

// ✅ Reset when filters change
useEffect(() => {
  setTasks([]);
  setLastDoc(null);
  setHasMore(true);
  loadFirst();
}, [status, assignee]); // reset on filter change
```

### 3. Not handling empty pages

If `snapshot.docs.length === 0`, there are no more results. Set `hasMore = false` and don't try to paginate further.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Function                                │ What It Does
────────────────────────────────────────┼──────────────────────────────────────
limit(n)                                │ Return at most n documents
startAfter(docSnapshot)                 │ Start after this document
startAfter(fieldValue)                  │ Start after this value
startAt(docSnapshot)                    │ Start at this document (inclusive)
endBefore(docSnapshot)                  │ End before this document
endAt(docSnapshot)                      │ End at this document (inclusive)
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Part 3 is done. The data model is solid, offline works, aggregation is efficient, operations are atomic, and pagination keeps things fast.

Now for Part 4: surviving production. First problem — Cloud Functions are slow on the first call.

---

[← Chapter 14: Transactions](chapter-14-transactions.md) | [Chapter 16: Cold Starts →](chapter-16-cold-starts.md)
