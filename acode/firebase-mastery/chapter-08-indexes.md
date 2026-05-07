# Chapter 8: Indexes — "The Query Fails with an Index Error"

[← Chapter 7: Queries](chapter-07-queries.md) | [Chapter 9: Cloud Functions →](chapter-09-cloud-functions.md)

---

## The Task

Lena tests the new filter feature in production. She filters tasks by status and sorts by due date. The app crashes:

```
FirebaseError: The query requires an index.
You can create it here: https://console.firebase.google.com/v1/r/project/snaptask-dev/firestore/indexes?create_composite=...
```

"It worked in development! Why is it broken now?"

---

## Why Indexes Exist

Firestore guarantees that query performance scales with the result set size, not the collection size. Whether you have 100 documents or 100 million, a query that returns 10 results takes the same time.

This guarantee requires indexes. Every query must be fully satisfiable by an index — Firestore never scans documents.

---

## Single-Field Indexes (Automatic)

Firestore automatically creates a single-field index for every field in every document. These cover:

```typescript
// All of these work without manual indexes:
where("status", "==", "todo")
where("assignee", "==", userId)
orderBy("createdAt", "desc")
where("priority", "in", ["high", "urgent"])
```

Any query that filters or sorts on a single field works out of the box.

---

## Composite Indexes (Manual)

When you combine filters on different fields, or filter on one field and sort by another, Firestore needs a **composite index**:

```typescript
// ❌ Needs composite index: filter on status + sort by dueDate
query(tasksRef,
  where("status", "==", "todo"),
  orderBy("dueDate", "asc")
);

// ❌ Needs composite index: filter on two fields
query(tasksRef,
  where("status", "==", "in_progress"),
  where("assignee", "==", userId)
);

// ❌ Needs composite index: filter + sort on different fields
query(tasksRef,
  where("assignee", "==", userId),
  orderBy("createdAt", "desc")
);
```

---

## Creating Indexes

### Method 1: Click the Error Link

When a query fails, the error message includes a direct link to create the required index. Click it → Firebase console opens → Click "Create" → Wait 2-5 minutes.

This is the most common method during development.

### Method 2: Firebase Console

Firebase console → Firestore → Indexes → Composite → Add Index

Specify:
- Collection (or collection group)
- Fields and their sort direction (Ascending/Descending)

### Method 3: firestore.indexes.json (Recommended for Production)

```json
{
  "indexes": [
    {
      "collectionGroup": "tasks",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "dueDate", "order": "ASCENDING" }
      ]
    },
    {
      "collectionGroup": "tasks",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "assignee", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "tasks",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "priority", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "tasks",
      "queryScope": "COLLECTION_GROUP",
      "fields": [
        { "fieldPath": "assignee", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    }
  ],
  "fieldOverrides": []
}
```

Deploy:

```bash
firebase deploy --only firestore:indexes
```

Indexes take 2-10 minutes to build. During that time, queries using them will fail.

---

## How to Know What Indexes You Need

Think about every query your app makes:

| Query | Index Needed |
|-------|-------------|
| `where("status", "==", X)` | No (single-field, automatic) |
| `where("status", "==", X), orderBy("dueDate")` | Yes: `status ASC, dueDate ASC` |
| `where("assignee", "==", X), orderBy("createdAt", "desc")` | Yes: `assignee ASC, createdAt DESC` |
| `where("status", "==", X), where("priority", "==", Y)` | Yes: `status ASC, priority ASC` |
| `where("status", "==", X), where("priority", "==", Y), orderBy("createdAt", "desc")` | Yes: `status ASC, priority ASC, createdAt DESC` |

---

## Index Limits

- Max 200 composite indexes per database
- Max fields per composite index: varies (typically up to 100, but keep it under 10)
- Index build time: 2-10 minutes (can be longer for large collections)
- Each index consumes storage (billed)

---

## The Index Explosion Problem

Every unique combination of filters needs its own index. If your filter UI has:
- 3 status options
- 5 priority levels
- Sort by date or priority

You might think you need an index for every combination. You don't — Firestore is smarter than that. An index on `(status, priority, createdAt)` covers:
- `where(status) + orderBy(createdAt)`
- `where(status) + where(priority) + orderBy(createdAt)`

But it does NOT cover:
- `where(priority) + orderBy(createdAt)` (different prefix)
- `where(status) + orderBy(priority)` (different sort)

---

## Strategies to Minimize Indexes

### 1. Composite Fields

Instead of indexing `status` + `priority` separately:

```typescript
// Store a composite field
await addDoc(tasksRef, {
  title: "Design landing page",
  status: "todo",
  priority: "high",
  status_priority: "todo_high", // composite field
  createdAt: serverTimestamp(),
});

// Query on the composite field (single-field index, automatic!)
query(tasksRef, where("status_priority", "==", "todo_high"));
```

Tradeoff: you maintain the composite field manually on every write.

### 2. Limit Filter Combinations

Don't let users filter on everything simultaneously. Design the UI to support the queries you've indexed.

### 3. Use `in` Instead of Multiple Queries

```typescript
// Instead of separate queries for each status:
query(tasksRef, where("status", "in", ["todo", "in_progress"]));
// One query, one index
```

---

## Exemptions (Field Overrides)

Sometimes you want to disable automatic indexing for a field:

```json
{
  "fieldOverrides": [
    {
      "collectionGroup": "tasks",
      "fieldPath": "description",
      "indexes": []
    }
  ]
}
```

Exempt fields you never query on (like `description` or `body`). This saves storage costs and write latency.

---

## Debugging Index Issues

### The Error Message

```
FirebaseError: The query requires an index.
You can create it here: https://console.firebase.google.com/...
```

Click the link. It pre-fills the exact index you need.

### Index Status

Firebase console → Firestore → Indexes shows:
- **Building** — index is being created (queries will fail)
- **Enabled** — index is ready
- **Error** — something went wrong (usually a field type mismatch)

### The Emulator Doesn't Require Indexes

This is why Lena's query worked in development but failed in production. The emulator ignores index requirements. Always test against production (or deploy indexes before deploying code).

---

## Common Mistakes

### 1. Not deploying indexes before deploying code

If your new feature uses a new query, deploy the index first. Wait for it to build. Then deploy the code. Otherwise, users hit the error.

```bash
# Deploy indexes first
firebase deploy --only firestore:indexes
# Wait 5 minutes for indexes to build
# Then deploy the app
firebase deploy --only hosting
```

### 2. Relying on the emulator for index testing

The emulator doesn't enforce indexes. Your queries will work locally and fail in production. Keep `firestore.indexes.json` up to date.

### 3. Creating too many indexes

Each index adds write latency (the index must be updated on every write) and storage cost. Only create indexes for queries your app actually makes.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Concept                                 │ Details
────────────────────────────────────────┼──────────────────────────────────────
Single-field index                      │ Automatic for every field
Composite index                         │ Manual — needed for multi-field queries
firestore.indexes.json                  │ Define indexes in code
firebase deploy --only firestore:indexes│ Deploy indexes
Index build time                        │ 2-10 minutes
Max composite indexes                   │ 200 per database
Collection group index                  │ For collectionGroup() queries
Field exemption                         │ Disable indexing for a field
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "When someone assigns a task to me, I want a notification. Not just in the app — an actual push notification on my phone."

That requires server-side logic. Client code can't send notifications to other users. Time for Cloud Functions.

---

[← Chapter 7: Queries](chapter-07-queries.md) | [Chapter 9: Cloud Functions →](chapter-09-cloud-functions.md)
