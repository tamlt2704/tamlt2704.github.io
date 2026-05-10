# Chapter 0: Before You Start

[Chapter 1: First Documents →](chapter-01-crud.md)

---

## The Story

You're a backend engineer at **DocuFlow**, a document management SaaS. Clients upload contracts, invoices, forms, and reports. Each document type has different fields:

- A **contract** has parties, clauses, signatures, effective dates
- An **invoice** has line items, tax rates, payment terms
- A **form** has dynamic fields defined by the user

In a relational database, you'd need: a `documents` table, a `document_fields` table (EAV pattern), a `line_items` table, a `clauses` table, a `signatures` table... and 15 JOINs to reconstruct one document.

Your tech lead, **Priya**, says: "The data IS a document. Store it as a document."

## Documents vs Tables

**Relational (SQL):**
```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  documents  │────→│  line_items  │     │  clauses   │
│  id, title  │     │  doc_id, ... │     │  doc_id,...│
└─────────────┘     └──────────────┘     └────────────┘
       │
       └──→ ┌──────────────┐
            │  signatures  │
            │  doc_id, ... │
            └──────────────┘
```

**MongoDB (Document):**
```json
{
  "_id": "ObjectId(...)",
  "title": "Service Agreement",
  "type": "contract",
  "parties": ["Acme Corp", "Widget Inc"],
  "clauses": [
    { "number": 1, "text": "Payment terms...", "agreed": true },
    { "number": 2, "text": "Termination...", "agreed": false }
  ],
  "signatures": [
    { "name": "Alice", "date": "2024-01-15", "role": "CEO" }
  ],
  "metadata": {
    "created_by": "user_123",
    "version": 3,
    "tags": ["legal", "active"]
  }
}
```

One document. No JOINs. Everything you need in one read.

## When to Use MongoDB

✅ **Good fit:**
- Documents with varying/evolving schemas
- Nested/hierarchical data (JSON-like)
- High write throughput
- Horizontal scaling (sharding)
- Rapid iteration (schema changes without migrations)
- Content management, catalogs, user profiles, IoT, logging

❌ **Bad fit:**
- Heavy cross-document JOINs (use PostgreSQL)
- Complex transactions across many collections (use PostgreSQL)
- Strict relational integrity (foreign keys, cascades)
- Small dataset that fits in one table (overkill)

## Key Concepts

| MongoDB | SQL Equivalent | Notes |
|---|---|---|
| Database | Database | Same concept |
| Collection | Table | Schema-free (no ALTER TABLE) |
| Document | Row | JSON/BSON, can be nested |
| Field | Column | Can vary per document |
| `_id` | Primary Key | Auto-generated ObjectId |
| Embedding | JOIN (denormalized) | Nested documents |
| Reference | Foreign Key | Manual, no enforcement |

## Setup

### Option 1: MongoDB Atlas (Free Cloud — Recommended)

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create free M0 cluster (512MB, free forever)
3. Create a database user
4. Whitelist your IP (or 0.0.0.0/0 for dev)
5. Get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/docuflow`

### Option 2: Local Install

```bash
# macOS
brew install mongodb-community

# Docker (easiest)
docker run -d --name mongo -p 27017:27017 mongo:7

# Verify
mongosh
```

### Option 3: mongosh (Shell)

```bash
# Connect to Atlas
mongosh "mongodb+srv://cluster.mongodb.net/docuflow" --username admin

# Connect to local
mongosh

# You're in! Try:
> show dbs
> use docuflow
> db.test.insertOne({ hello: "world" })
> db.test.find()
```

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Engineer | Recovering SQL developer |
| **Priya** | Tech Lead | "If you're JOINing 5 tables, your schema is wrong" |
| **The Client** | Enterprise users | "We need a new field on invoices. By Friday." |
| **Atlas** | MongoDB Cloud | Free tier, auto-scales, handles backups |

## The Roadmap

| Ch | The Problem | The MongoDB Solution |
|---|---|---|
| 1 | Store a contract with nested data | CRUD operations on documents |
| 2 | Find contracts by any field | Rich query language |
| 3 | Model relationships | Embedding vs referencing |
| 4 | Queries are slow | Indexes |
| 5 | Complex reports | Aggregation pipeline |
| 6 | Update nested arrays | Update operators |
| 7 | Multi-document consistency | Transactions |
| 8 | Real-time updates | Change streams |
| 9 | Full-text search | Atlas Search |
| 10 | Performance at scale | Profiling, sharding |
| 11 | Production readiness | Security, backups, replicas |
| 12 | Connect from code | Drivers (Node, Python, Java) |

## Quick Taste

```javascript
// mongosh — insert a document
use docuflow

db.contracts.insertOne({
  title: "Service Agreement",
  client: "Acme Corp",
  value: 50000,
  status: "active",
  clauses: [
    { id: 1, text: "Net 30 payment terms" },
    { id: 2, text: "12-month term" }
  ],
  signed_at: new Date("2024-06-15"),
  tags: ["enterprise", "recurring"]
})

// Find it
db.contracts.findOne({ client: "Acme Corp" })

// Query nested fields
db.contracts.find({ "clauses.text": /payment/ })

// Update a nested field
db.contracts.updateOne(
  { client: "Acme Corp" },
  { $set: { status: "renewed" }, $push: { tags: "renewed-2025" } }
)
```

That's MongoDB in 15 lines. No schema definition. No migration. No ALTER TABLE. Just store and query JSON.

---

[Chapter 1: First Documents →](chapter-01-crud.md)
