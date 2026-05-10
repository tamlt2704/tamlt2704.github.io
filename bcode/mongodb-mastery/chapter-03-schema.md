# Chapter 3: Schema Design

[← Ch 2](chapter-02-queries.md) | [Ch 4 →](chapter-04-indexes.md)

---

## The Problem

> **Priya:** "We have users, organizations, and documents. A user belongs to one org. An org has many users. A document has many versions. How do we model this without foreign keys?"

MongoDB gives you freedom — embed or reference. The wrong choice means unbounded arrays, slow queries, or duplicated data. Here's the decision framework.

---

## The Decision Framework

| Relationship | Pattern | When |
|---|---|---|
| One-to-One | Embed | Data always accessed together |
| One-to-Few (< 50) | Embed array | Bounded, read together |
| One-to-Many (hundreds+) | Reference | Unbounded, accessed independently |
| Many-to-Many | Array of refs | Both sides need independent access |

**Ask yourself:** Will this array grow without bound? If yes, reference.

---

## One-to-One: Embed

A user has one profile. Always fetched together.

```javascript
db.users.insertOne({
  email: "priya@docuflow.io",
  name: "Priya Sharma",
  role: "tech_lead",
  profile: {
    avatar: "https://cdn.docuflow.io/avatars/priya.jpg",
    timezone: "Asia/Kolkata",
    theme: "dark",
    notifications: { email: true, slack: true }
  },
  createdAt: new Date()
})
```

---

## One-to-Few: Embed Array

A contract has 2-10 clauses. Bounded, always read with the contract.

```javascript
db.contracts.insertOne({
  title: "Enterprise License",
  clauses: [
    { id: 1, text: "Net 30 payment terms", type: "payment" },
    { id: 2, text: "99.9% SLA guarantee", type: "sla" },
    { id: 3, text: "Annual renewal", type: "renewal" }
  ]
})
```

---

## One-to-Many: Reference

An organization has thousands of documents. Store a reference.

```javascript
// Organizations collection
db.organizations.insertOne({
  _id: ObjectId("org001"),
  name: "GlobalBank",
  plan: "enterprise",
  createdAt: new Date()
})

// Documents reference the org
db.documents.insertOne({
  title: "Q4 Financial Report",
  orgId: ObjectId("org001"),
  type: "report",
  createdAt: new Date()
})

// Query: all documents for an org
db.documents.find({ orgId: ObjectId("org001") })
```

---

## Many-to-Many: Array of References

Users can access multiple documents. Documents can have multiple collaborators.

```javascript
db.documents.insertOne({
  title: "Project Proposal",
  orgId: ObjectId("org001"),
  collaborators: [
    ObjectId("user001"),
    ObjectId("user002"),
    ObjectId("user003")
  ],
  permissions: {
    "user001": "owner",
    "user002": "editor",
    "user003": "viewer"
  }
})

// Find all documents a user collaborates on
db.documents.find({ collaborators: ObjectId("user002") })
```

---

## Anti-Pattern: Unbounded Arrays

```javascript
// ❌ BAD — comments array grows forever
db.documents.insertOne({
  title: "Contract Draft",
  comments: [
    // ... could be 10,000+ comments
  ]
})

// ✅ GOOD — separate collection with reference
db.comments.insertOne({
  documentId: ObjectId("doc001"),
  author: ObjectId("user001"),
  text: "Please review clause 3",
  createdAt: new Date()
})
```

> **16MB document limit.** An unbounded array will eventually hit it.

---

## Anti-Pattern: Deep Nesting

```javascript
// ❌ BAD — hard to query and update
{ org: { departments: [{ teams: [{ members: [{ tasks: [...] }] }] }] } }

// ✅ GOOD — flatten with references
db.tasks.insertOne({
  orgId: ObjectId("org001"),
  departmentId: ObjectId("dept001"),
  teamId: ObjectId("team001"),
  assignee: ObjectId("user001"),
  title: "Review contract"
})
```

---

## Schema Validation with JSON Schema

```javascript
db.createCollection("contracts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "client", "status", "createdAt"],
      properties: {
        title: { bsonType: "string", description: "Contract title" },
        client: { bsonType: "string" },
        status: { enum: ["draft", "pending", "active", "signed", "expired"] },
        value: { bsonType: "number", minimum: 0 },
        clauses: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["text", "type"],
            properties: {
              text: { bsonType: "string" },
              type: { bsonType: "string" }
            }
          }
        },
        createdAt: { bsonType: "date" }
      }
    }
  },
  validationLevel: "moderate",
  validationAction: "error"
})
```

Test it:

```javascript
// This fails — missing required "client" field
db.contracts.insertOne({ title: "Bad Contract", status: "draft", createdAt: new Date() })
// MongoServerError: Document failed validation
```

---

## Python Example — Schema Pattern

```python
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client.docuflow

# One-to-many: insert org, then documents referencing it
org_id = db.organizations.insert_one({
    "name": "TechStart",
    "plan": "startup"
}).inserted_id

db.documents.insert_one({
    "title": "Pitch Deck",
    "orgId": org_id,
    "type": "presentation",
    "createdAt": datetime.now()
})

# Query with reference
docs = list(db.documents.find({"orgId": org_id}))
```

---

## What You Learned

- **Embed** when data is bounded and always accessed together
- **Reference** when data grows unbounded or is accessed independently
- Avoid unbounded arrays (16MB limit, slow updates)
- Avoid deep nesting (hard to query with dot notation)
- JSON Schema validation enforces structure without rigid migrations
- `validationLevel: "moderate"` skips validation on existing invalid docs

---

[← Ch 2: Querying](chapter-02-queries.md) | [Ch 4: Indexes →](chapter-04-indexes.md)
