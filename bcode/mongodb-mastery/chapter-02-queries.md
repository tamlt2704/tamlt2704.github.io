# Chapter 2: Querying

[← Ch 1](chapter-01-crud.md) | [Ch 3 →](chapter-03-schema.md)

---

## The Problem

> **The Client:** "I need to find all contracts over $50k that are either active OR pending, signed by someone in the legal department, and I only want the title and value back — sorted by value descending."

Simple `find()` won't cut it. You need comparison operators, logical combinators, array queries, projections, and sorting.

---

## Comparison Operators

```javascript
// Exact match
db.contracts.find({ status: "active" })

// Greater than / less than
db.contracts.find({ value: { $gt: 50000 } })
db.contracts.find({ value: { $lt: 10000 } })
db.contracts.find({ value: { $gte: 50000, $lte: 100000 } })

// Not equal
db.contracts.find({ status: { $ne: "expired" } })

// In a set of values
db.contracts.find({ status: { $in: ["active", "pending"] } })

// Not in a set
db.contracts.find({ status: { $nin: ["expired", "cancelled"] } })
```

---

## Logical Operators

```javascript
// AND (implicit — multiple fields)
db.contracts.find({ status: "active", value: { $gt: 50000 } })

// AND (explicit — same field, multiple conditions)
db.contracts.find({ $and: [
  { value: { $gt: 50000 } },
  { value: { $lt: 200000 } }
]})

// OR
db.contracts.find({ $or: [
  { status: "active" },
  { status: "pending" }
]})

// NOT
db.contracts.find({ value: { $not: { $lt: 10000 } } })

// NOR (none of these)
db.contracts.find({ $nor: [
  { status: "expired" },
  { status: "cancelled" }
]})
```

---

## Element Operators

```javascript
// Field exists
db.contracts.find({ "metadata.region": { $exists: true } })

// Field is a specific BSON type
db.contracts.find({ value: { $type: "number" } })
db.contracts.find({ createdAt: { $type: "date" } })
```

---

## Array Operators

```javascript
// Match any element in array
db.contracts.find({ "clauses.type": "sla" })

// $elemMatch — element must satisfy ALL conditions
db.contracts.find({
  clauses: { $elemMatch: { type: "payment", text: /30 days/ } }
})

// $size — exact array length
db.contracts.find({ clauses: { $size: 3 } })

// $all — array contains ALL specified values
db.contracts.find({ "clauses.type": { $all: ["sla", "compliance"] } })
```

---

## Regex

```javascript
// Case-insensitive search
db.contracts.find({ title: { $regex: /agreement/i } })

// Starts with
db.contracts.find({ title: { $regex: /^NDA/ } })

// Contains "bank" (case-insensitive)
db.contracts.find({ client: { $regex: "bank", $options: "i" } })
```

> **Warning:** Unanchored regex (`/keyword/`) can't use indexes. Prefer `$text` or Atlas Search for full-text.

---

## Projection — Choose Your Fields

```javascript
// Include only title and value (plus _id by default)
db.contracts.find({ status: "active" }, { title: 1, value: 1 })

// Exclude _id
db.contracts.find({ status: "active" }, { title: 1, value: 1, _id: 0 })

// Exclude large fields
db.contracts.find({}, { clauses: 0, signatures: 0 })

// Array slice — first 2 clauses only
db.contracts.find({}, { clauses: { $slice: 2 } })
```

> You can't mix inclusion and exclusion (except `_id: 0`).

---

## Sort, Limit, Skip

```javascript
// Sort by value descending, then by title ascending
db.contracts.find().sort({ value: -1, title: 1 })

// Pagination: page 2, 10 per page
db.contracts.find().sort({ createdAt: -1 }).skip(10).limit(10)

// Top 5 highest-value contracts
db.contracts.find({}, { title: 1, value: 1, _id: 0 })
  .sort({ value: -1 })
  .limit(5)
```

---

## Putting It All Together

The client's original request as a single query:

```javascript
db.contracts.find(
  {
    value: { $gt: 50000 },
    $or: [{ status: "active" }, { status: "pending" }],
    "metadata.department": "legal"
  },
  { title: 1, value: 1, _id: 0 }
).sort({ value: -1 })
```

---

## Node.js Equivalent

```javascript
const { MongoClient } = require('mongodb');

async function findHighValueContracts() {
  const client = new MongoClient('mongodb://localhost:27017');
  const db = client.db('docuflow');

  const results = await db.collection('contracts')
    .find({
      value: { $gt: 50000 },
      $or: [{ status: 'active' }, { status: 'pending' }]
    })
    .project({ title: 1, value: 1, _id: 0 })
    .sort({ value: -1 })
    .limit(10)
    .toArray();

  console.log(results);
  await client.close();
}
```

---

## What You Learned

- Comparison: `$eq`, `$gt`, `$lt`, `$gte`, `$lte`, `$in`, `$ne`, `$nin`
- Logical: `$and`, `$or`, `$not`, `$nor`
- Element: `$exists`, `$type`
- Array: `$elemMatch`, `$size`, `$all`
- Regex for pattern matching (use sparingly — prefer text indexes)
- Projection to limit returned fields and reduce network payload
- `sort()`, `limit()`, `skip()` for ordering and pagination

---

[← Ch 1: CRUD](chapter-01-crud.md) | [Ch 3: Schema Design →](chapter-03-schema.md)
