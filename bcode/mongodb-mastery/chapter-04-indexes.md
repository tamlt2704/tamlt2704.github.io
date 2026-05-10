# Chapter 4: Indexes

[← Ch 3](chapter-03-schema.md) | [Ch 5 →](chapter-05-aggregation.md)

---

## The Problem

> **Priya:** "We just hit 1 million documents. The contracts page takes 4 seconds to load. The query scans every single document. We need indexes — but which ones?"

Without indexes, MongoDB does a **COLLSCAN** (collection scan). With the right index, it does an **IXSCAN** and returns in milliseconds.

---

## Single Field Index

```javascript
// Index on status — speeds up find({ status: "active" })
db.contracts.createIndex({ status: 1 })

// Descending — useful for sort({ createdAt: -1 })
db.contracts.createIndex({ createdAt: -1 })

// Unique index — no duplicate emails
db.users.createIndex({ email: 1 }, { unique: true })
```

---

## Compound Index

Order matters. The **ESR rule**: Equality → Sort → Range.

```javascript
// Query: status = "active", sorted by createdAt, value > 50000
// ESR: Equality(status) → Sort(createdAt) → Range(value)
db.contracts.createIndex({ status: 1, createdAt: -1, value: 1 })

// This index supports:
db.contracts.find({ status: "active" }).sort({ createdAt: -1 })
db.contracts.find({ status: "active", value: { $gt: 50000 } }).sort({ createdAt: -1 })
```

> A compound index supports queries on its **prefixes**. `{ a: 1, b: 1, c: 1 }` supports queries on `a`, `a+b`, and `a+b+c`.

---

## Multikey Index (Arrays)

```javascript
// Index on array field — indexes each element
db.contracts.createIndex({ "clauses.type": 1 })

// Now this is fast:
db.contracts.find({ "clauses.type": "sla" })
```

> MongoDB automatically creates a multikey index when the field is an array. One index entry per array element.

---

## Text Index

```javascript
// Full-text search on title and clause text
db.contracts.createIndex({ title: "text", "clauses.text": "text" })

// Search
db.contracts.find({ $text: { $search: "payment terms" } })

// With relevance score
db.contracts.find(
  { $text: { $search: "SLA uptime guarantee" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })
```

> Only one text index per collection. For advanced search, use Atlas Search (Chapter 9).

---

## TTL Index — Auto-Delete Old Documents

```javascript
// Delete audit logs after 90 days
db.auditLogs.createIndex({ createdAt: 1 }, { expireAfterSeconds: 7776000 })

// Documents with createdAt older than 90 days are automatically removed
db.auditLogs.insertOne({
  action: "contract_viewed",
  userId: ObjectId("user001"),
  createdAt: new Date()
})
```

---

## explain() — Analyze Query Performance

```javascript
// See the query plan
db.contracts.find({ status: "active", value: { $gt: 50000 } })
  .sort({ createdAt: -1 })
  .explain("executionStats")
```

Key fields to check:

| Field | Good Value | Bad Value |
|---|---|---|
| `winningPlan.stage` | IXSCAN | COLLSCAN |
| `totalDocsExamined` | Close to `nReturned` | Much higher than `nReturned` |
| `executionTimeMillis` | < 100ms | > 1000ms |
| `totalKeysExamined` | Close to `nReturned` | Much higher |

```javascript
// Before index: COLLSCAN, 1M docs examined, 3200ms
// After index:  IXSCAN, 847 docs examined, 12ms
```

---

## Covered Queries

A query is "covered" when the index contains ALL requested fields — MongoDB never touches the documents.

```javascript
// Create index that covers the query
db.contracts.createIndex({ status: 1, title: 1, value: 1 })

// This query is fully covered (no document fetch)
db.contracts.find(
  { status: "active" },
  { title: 1, value: 1, _id: 0 }  // Must exclude _id!
).explain("executionStats")
// totalDocsExamined: 0 ← covered!
```

---

## Managing Indexes

```javascript
// List all indexes
db.contracts.getIndexes()

// Drop an index
db.contracts.dropIndex({ status: 1 })

// Drop by name
db.contracts.dropIndex("status_1_createdAt_-1_value_1")

// Hide index (test impact without dropping)
db.contracts.hideIndex("status_1")
db.contracts.unhideIndex("status_1")
```

---

## Node.js Example

```javascript
const { MongoClient } = require('mongodb');

async function optimizeQueries() {
  const client = new MongoClient('mongodb://localhost:27017');
  const db = client.db('docuflow');
  const contracts = db.collection('contracts');

  // Create compound index
  await contracts.createIndex({ status: 1, createdAt: -1, value: 1 });

  // Explain a query
  const plan = await contracts.find({ status: 'active' })
    .sort({ createdAt: -1 })
    .explain('executionStats');

  console.log('Stage:', plan.executionStats.executionStages.stage);
  console.log('Docs examined:', plan.executionStats.totalDocsExamined);

  await client.close();
}
```

---

## What You Learned

- Single field indexes for simple equality/sort queries
- Compound indexes following the **ESR rule** (Equality, Sort, Range)
- Multikey indexes automatically handle array fields
- Text indexes for basic full-text search (one per collection)
- TTL indexes for automatic document expiration
- `explain("executionStats")` to verify IXSCAN vs COLLSCAN
- Covered queries avoid document fetches entirely (exclude `_id`)
- `hideIndex()` to test impact before dropping

---

[← Ch 3: Schema Design](chapter-03-schema.md) | [Ch 5: Aggregation →](chapter-05-aggregation.md)
