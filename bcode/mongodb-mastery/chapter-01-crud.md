# Chapter 1: First Documents

[← Overview](chapter-00-overview.md) | [Ch 2 →](chapter-02-queries.md)

---

## The Problem

> **Priya:** "The client wants to store contracts. Each contract has nested clauses, multiple signers, and metadata that varies per contract type. In Postgres, that's 5 tables and a JOIN nightmare for every read."

A single contract has clauses (array), signatures (array of objects), and flexible metadata. You need to store it, retrieve it, update it, and delete it — without a migration file in sight.

---

## Connecting

```javascript
// mongosh
use docuflow

// Node.js (MongoDB driver)
const { MongoClient } = require('mongodb');
const client = new MongoClient('mongodb://localhost:27017');
const db = client.db('docuflow');
```

---

## insertOne — Store a Contract

```javascript
db.contracts.insertOne({
  title: "SaaS License Agreement",
  client: "Acme Corp",
  status: "draft",
  value: 48000,
  clauses: [
    { id: 1, text: "Payment due within 30 days", type: "payment" },
    { id: 2, text: "Auto-renews annually", type: "renewal" }
  ],
  signatures: [
    { name: "Jane Doe", role: "client", signedAt: null },
    { name: "Bob Smith", role: "vendor", signedAt: null }
  ],
  createdAt: new Date(),
  metadata: { department: "sales", priority: "high" }
})
```

MongoDB returns `{ acknowledged: true, insertedId: ObjectId("...") }`.

---

## insertMany — Bulk Load

```javascript
db.contracts.insertMany([
  {
    title: "NDA - TechStart",
    client: "TechStart Inc",
    status: "signed",
    value: 0,
    clauses: [{ id: 1, text: "Confidentiality for 2 years", type: "confidentiality" }],
    signatures: [{ name: "Alice Chen", role: "client", signedAt: new Date("2024-01-15") }],
    createdAt: new Date("2024-01-10"),
    metadata: { department: "legal" }
  },
  {
    title: "Service Agreement - GlobalBank",
    client: "GlobalBank",
    status: "active",
    value: 120000,
    clauses: [
      { id: 1, text: "SLA 99.9% uptime", type: "sla" },
      { id: 2, text: "Quarterly reviews", type: "review" },
      { id: 3, text: "Data residency in EU", type: "compliance" }
    ],
    signatures: [
      { name: "Mark Lee", role: "client", signedAt: new Date("2024-02-01") },
      { name: "Priya Sharma", role: "vendor", signedAt: new Date("2024-02-01") }
    ],
    createdAt: new Date("2024-01-28"),
    metadata: { department: "enterprise", region: "EU" }
  }
])
```

> **Tip:** `insertMany` is ordered by default. Add `{ ordered: false }` to continue on errors.

---

## find / findOne — Retrieve Documents

```javascript
// Find one contract by client
db.contracts.findOne({ client: "Acme Corp" })

// Find all active contracts
db.contracts.find({ status: "active" })

// Find contracts worth over 50k
db.contracts.find({ value: { $gt: 50000 } })

// Count documents
db.contracts.countDocuments({ status: "draft" })
```

---

## updateOne / updateMany — Modify Documents

```javascript
// Update one: mark contract as signed
db.contracts.updateOne(
  { title: "SaaS License Agreement" },
  {
    $set: { status: "signed" },
    $currentDate: { updatedAt: true }
  }
)

// Update many: add a flag to all active contracts
db.contracts.updateMany(
  { status: "active" },
  { $set: { requiresReview: true } }
)
```

---

## replaceOne — Swap the Entire Document

```javascript
db.contracts.replaceOne(
  { title: "NDA - TechStart" },
  {
    title: "NDA - TechStart (Revised)",
    client: "TechStart Inc",
    status: "draft",
    value: 0,
    clauses: [{ id: 1, text: "Confidentiality for 5 years", type: "confidentiality" }],
    signatures: [],
    createdAt: new Date(),
    metadata: { department: "legal", version: 2 }
  }
)
```

> `replaceOne` swaps the whole document (except `_id`). Use `updateOne` with `$set` for partial changes.

---

## deleteOne / deleteMany — Remove Documents

```javascript
// Delete one draft
db.contracts.deleteOne({ title: "SaaS License Agreement", status: "draft" })

// Delete all expired contracts
db.contracts.deleteMany({ status: "expired" })
```

---

## Bulk Operations

```javascript
db.contracts.bulkWrite([
  { insertOne: { document: { title: "Quick NDA", client: "StartupX", status: "draft", value: 0, clauses: [], signatures: [], createdAt: new Date() } } },
  { updateOne: { filter: { client: "GlobalBank" }, update: { $set: { status: "renewed" } } } },
  { deleteOne: { filter: { client: "OldClient" } } }
], { ordered: false })
```

---

## Python Equivalent (PyMongo)

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.docuflow

# Insert
result = db.contracts.insert_one({
    "title": "SaaS License Agreement",
    "client": "Acme Corp",
    "status": "draft",
    "value": 48000,
    "clauses": [{"id": 1, "text": "Payment due within 30 days", "type": "payment"}],
    "signatures": [{"name": "Jane Doe", "role": "client", "signedAt": None}],
})
print(result.inserted_id)

# Find
contract = db.contracts.find_one({"client": "Acme Corp"})
```

---

## What You Learned

- `insertOne` / `insertMany` — store documents with nested structures, no schema migration needed
- `find` / `findOne` — retrieve by any field, including nested ones
- `updateOne` / `updateMany` — partial updates with `$set`, full swap with `replaceOne`
- `deleteOne` / `deleteMany` — remove by filter
- `bulkWrite` — batch mixed operations in a single round trip

---

[← Overview](chapter-00-overview.md) | [Ch 2: Querying →](chapter-02-queries.md)
