# Chapter 7: Queries — "Filter Tasks by Status, Assignee"

[← Chapter 6: Storage](chapter-06-storage.md) | [Chapter 8: Indexes →](chapter-08-indexes.md)

---

## The Task

Lena: "We have 200 tasks. I need to see only MY tasks. Only the ones that are 'in progress'. Sorted by priority. The task list is useless without filters."

---

## Basic Queries

Firestore queries use a builder pattern — chain constraints onto a collection reference:

```typescript
import {
  collection,
  query,
  where,
  orderBy,
  limit,
  getDocs,
} from "firebase/firestore";
import { db } from "./firebase";

const tasksRef = collection(db, "teams", teamId, "tasks");

// Filter by status
const todoQuery = query(tasksRef, where("status", "==", "todo"));

// Filter by assignee
const myTasksQuery = query(tasksRef, where("assignee", "==", userId));

// Multiple filters
const myTodoQuery = query(
  tasksRef,
  where("assignee", "==", userId),
  where("status", "==", "todo")
);

// Order by field
const recentQuery = query(tasksRef, orderBy("createdAt", "desc"));

// Limit results
const topFiveQuery = query(tasksRef, orderBy("priority"), limit(5));
```

---

## Comparison Operators

```typescript
where("status", "==", "todo")        // equals
where("priority", "!=", "low")       // not equals
where("dueDate", "<", new Date())    // less than
where("dueDate", "<=", today)        // less than or equal
where("dueDate", ">", yesterday)     // greater than
where("dueDate", ">=", startOfWeek)  // greater than or equal
```

---

## Array Queries

```typescript
// Does the array contain this value?
where("tags", "array-contains", "urgent")

// Does the array contain ANY of these values?
where("tags", "array-contains-any", ["urgent", "blocked"])

// Is the value IN this list?
where("status", "in", ["todo", "in_progress"])

// Is the value NOT IN this list?
where("status", "not-in", ["done", "archived"])
```

---

## Combining Filters

```typescript
// Multiple equality filters — always works
query(tasksRef,
  where("status", "==", "todo"),
  where("assignee", "==", userId)
);

// Equality + range on SAME field — works
query(tasksRef,
  where("priority", ">=", "high"),
  where("priority", "<=", "urgent")
);

// Equality + range on DIFFERENT fields — needs composite index
query(tasksRef,
  where("status", "==", "todo"),
  where("dueDate", "<", new Date()),
  orderBy("dueDate")
);

// Equality + orderBy on different field — needs composite index
query(tasksRef,
  where("assignee", "==", userId),
  orderBy("createdAt", "desc")
);
```

---

## The orderBy Requirement

If you use a range filter (`<`, `<=`, `>`, `>=`, `!=`), you must order by that field first:

```typescript
// ✅ Range filter + orderBy on same field
query(tasksRef,
  where("dueDate", ">", yesterday),
  orderBy("dueDate")
);

// ❌ FAILS — range on dueDate but ordering by createdAt
query(tasksRef,
  where("dueDate", ">", yesterday),
  orderBy("createdAt")
);

// ✅ You can add a secondary orderBy after the range field
query(tasksRef,
  where("dueDate", ">", yesterday),
  orderBy("dueDate"),
  orderBy("createdAt", "desc")
);
```

---

## Real-Time Queries

All queries work with `onSnapshot` too:

```typescript
import { onSnapshot } from "firebase/firestore";

const q = query(
  tasksRef,
  where("assignee", "==", userId),
  where("status", "==", "in_progress"),
  orderBy("updatedAt", "desc")
);

const unsubscribe = onSnapshot(q, (snapshot) => {
  const tasks = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
  setMyActiveTasks(tasks);
});
```

The listener only fires when documents matching the query change. If someone else's task updates, your listener doesn't fire.

---

## Building a Filter UI

```tsx
// src/hooks/useFilteredTasks.ts
import { useState, useEffect } from "react";
import {
  collection, query, where, orderBy, onSnapshot,
  QueryConstraint,
} from "firebase/firestore";
import { db } from "../firebase";

interface Filters {
  status?: string;
  assignee?: string;
  priority?: string;
}

export function useFilteredTasks(teamId: string, filters: Filters) {
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    const constraints: QueryConstraint[] = [];

    if (filters.status) {
      constraints.push(where("status", "==", filters.status));
    }
    if (filters.assignee) {
      constraints.push(where("assignee", "==", filters.assignee));
    }
    if (filters.priority) {
      constraints.push(where("priority", "==", filters.priority));
    }

    constraints.push(orderBy("createdAt", "desc"));

    const q = query(
      collection(db, "teams", teamId, "tasks"),
      ...constraints
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      setTasks(snapshot.docs.map((d) => ({ id: d.id, ...d.data() })));
    });

    return unsubscribe;
  }, [teamId, filters.status, filters.assignee, filters.priority]);

  return tasks;
}
```

---

## Query Limitations

Firestore is NOT SQL. These things don't work:

```typescript
// ❌ No full-text search
where("title", "contains", "landing")  // doesn't exist

// ❌ No OR across different fields
where("status", "==", "todo") OR where("priority", "==", "high")
// Use "in" for OR on the same field:
where("status", "in", ["todo", "in_progress"])

// ❌ No joins
// Can't query tasks and include user names in one query

// ❌ No inequality on multiple fields (without composite index)
where("dueDate", ">", today),
where("priority", ">", 3)
// Only one field can have a range filter per query

// ❌ No regex or pattern matching
where("email", "matches", ".*@gmail.com")  // doesn't exist
```

Workarounds:
- Full-text search → Use Algolia, Typesense, or Cloud Functions
- OR across fields → Multiple queries, merge client-side
- Joins → Denormalize (store user name on the task document)
- Multiple range filters → Composite fields or restructure data

---

## Collection Group Queries

Query across ALL subcollections with the same name:

```typescript
import { collectionGroup } from "firebase/firestore";

// Find all tasks assigned to me, across ALL teams
const allMyTasks = query(
  collectionGroup(db, "tasks"),
  where("assignee", "==", userId)
);

const snapshot = await getDocs(allMyTasks);
```

This queries every `tasks` subcollection in the entire database. Requires a collection group index (Firebase console will prompt you).

Security rules for collection group queries:

```
match /{path=**}/tasks/{taskId} {
  allow read: if request.auth != null
    && request.auth.uid == resource.data.assignee;
}
```

---

## Common Mistakes

### 1. Filtering client-side instead of in the query

```typescript
// ❌ Downloads ALL tasks, then filters — expensive!
const all = await getDocs(collection(db, "teams", teamId, "tasks"));
const filtered = all.docs.filter((d) => d.data().status === "todo");

// ✅ Only downloads matching tasks
const q = query(tasksRef, where("status", "==", "todo"));
const filtered = await getDocs(q);
```

### 2. Forgetting that queries need indexes

If you combine `where` on one field with `orderBy` on another, Firestore needs a composite index. Without it, the query throws an error with a link to create the index. (Next chapter covers this in detail.)

### 3. Using `!=` without understanding the cost

`where("status", "!=", "done")` reads every document that isn't "done". If 90% of tasks are "done", this is efficient. If 10% are "done", you're reading 90% of the collection. Consider using `in` with the values you DO want.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Operator                                │ Usage
────────────────────────────────────────┼──────────────────────────────────────
==                                      │ Exact match
!=                                      │ Not equal (needs index)
<, <=, >, >=                            │ Range (one field per query)
in                                      │ Value in list (max 30 values)
not-in                                  │ Value not in list (max 10)
array-contains                          │ Array has value
array-contains-any                      │ Array has any of values (max 30)
orderBy(field, "asc"|"desc")            │ Sort results
limit(n)                                │ Cap results
collectionGroup(db, name)               │ Query across subcollections
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You deploy the filter feature. Lena tests it. She filters by status AND sorts by due date. The app crashes with:

```
FirebaseError: The query requires an index.
You can create it here: https://console.firebase.google.com/...
```

Composite indexes. The thing Firestore needs but doesn't tell you about until production.

---

[← Chapter 6: Storage](chapter-06-storage.md) | [Chapter 8: Indexes →](chapter-08-indexes.md)
