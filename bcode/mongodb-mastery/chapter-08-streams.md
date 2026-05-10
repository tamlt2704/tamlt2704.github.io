# Chapter 8: Change Streams

[← Ch 7](chapter-07-transactions.md) | [Ch 9 →](chapter-09-search.md)

---

## The Problem

> **The Client:** "When a contract gets signed, I need an instant email notification. When a document is updated, the cache must invalidate. I don't want to poll the database every second."

Change streams let you subscribe to real-time data changes. No polling. No cron jobs. The database pushes events to you.

---

## Basic Watch

```javascript
// Watch all changes on a collection
const cursor = db.contracts.watch();

// This blocks and prints each change as it happens
while (cursor.hasNext()) {
  const change = cursor.next();
  printjson(change);
}
```

Change event structure:

```javascript
{
  _id: { _data: "826..." },           // Resume token
  operationType: "insert",             // insert, update, replace, delete
  fullDocument: { title: "...", ... }, // The document (for insert/replace)
  ns: { db: "docuflow", coll: "contracts" },
  documentKey: { _id: ObjectId("...") },
  updateDescription: {                 // Only for updates
    updatedFields: { status: "signed" },
    removedFields: []
  }
}
```

---

## Filtering with Pipeline

Don't process every change — filter at the database level:

```javascript
// Only watch for contracts being signed
const pipeline = [
  { $match: {
    operationType: "update",
    "updateDescription.updatedFields.status": "signed"
  }}
];

const cursor = db.contracts.watch(pipeline);

while (cursor.hasNext()) {
  const change = cursor.next();
  print(`Contract signed: ${change.documentKey._id}`);
}
```

```javascript
// Watch inserts for high-value contracts only
const pipeline = [
  { $match: {
    operationType: "insert",
    "fullDocument.value": { $gte: 100000 }
  }}
];

const cursor = db.contracts.watch(pipeline);
```

---

## fullDocument Option

By default, update events only include changed fields. Use `fullDocument` to get the complete document:

```javascript
// Get the full document after update
const cursor = db.contracts.watch([], {
  fullDocument: "updateLookup"
});

// MongoDB 7+: get document BEFORE the change too
const cursor = db.contracts.watch([], {
  fullDocument: "whenAvailable",
  fullDocumentBeforeChange: "whenAvailable"
});
```

| Option | Behavior |
|---|---|
| `"default"` | No full document on updates |
| `"updateLookup"` | Fetches current document at read time |
| `"whenAvailable"` | Includes if available (pre-images must be enabled) |
| `"required"` | Fails if document unavailable |

---

## Resume Tokens — Surviving Restarts

```javascript
let resumeToken = null;

const cursor = db.contracts.watch([], {
  fullDocument: "updateLookup"
});

while (cursor.hasNext()) {
  const change = cursor.next();
  resumeToken = change._id;  // Save this!

  // Process the change...
  processChange(change);
}

// After restart, resume from where you left off:
const cursor2 = db.contracts.watch([], {
  resumeAfter: resumeToken
});
```

> Store resume tokens in a separate collection or Redis. On restart, read the token and resume.

---

## Watch Entire Database or Cluster

```javascript
// Watch all collections in a database
const cursor = db.watch();

// Watch the entire cluster (all databases)
const cursor = db.getMongo().watch();

// Filter by collection
const cursor = db.watch([
  { $match: { "ns.coll": { $in: ["contracts", "invoices"] } } }
]);
```

---

## Use Case: Audit Log

```javascript
// Automatically log all changes to contracts
const cursor = db.contracts.watch([], {
  fullDocument: "updateLookup"
});

while (cursor.hasNext()) {
  const change = cursor.next();
  db.auditLog.insertOne({
    collection: "contracts",
    operation: change.operationType,
    documentId: change.documentKey._id,
    changes: change.updateDescription || null,
    fullDocument: change.fullDocument || null,
    timestamp: new Date()
  });
}
```

---

## Use Case: Cache Invalidation

```javascript
const pipeline = [
  { $match: { operationType: { $in: ["update", "replace", "delete"] } } }
];

const cursor = db.contracts.watch(pipeline);

while (cursor.hasNext()) {
  const change = cursor.next();
  const cacheKey = `contract:${change.documentKey._id}`;
  // Invalidate cache (pseudo-code)
  // redis.del(cacheKey);
  print(`Cache invalidated: ${cacheKey}`);
}
```

---

## Node.js Example — Event-Driven

```javascript
const { MongoClient } = require('mongodb');

async function watchContracts() {
  const client = new MongoClient('mongodb://localhost:27017/?replicaSet=rs0');
  const db = client.db('docuflow');

  const pipeline = [
    { $match: { operationType: { $in: ['insert', 'update'] } } }
  ];

  const changeStream = db.collection('contracts').watch(pipeline, {
    fullDocument: 'updateLookup'
  });

  changeStream.on('change', (change) => {
    console.log(`[${change.operationType}] ${change.fullDocument?.title}`);

    if (change.updateDescription?.updatedFields?.status === 'signed') {
      sendNotification(change.fullDocument);
    }
  });

  changeStream.on('error', (err) => {
    console.error('Stream error:', err);
    // Reconnect with resume token
  });
}

function sendNotification(contract) {
  console.log(`📧 Notification: "${contract.title}" was signed!`);
}
```

---

## Requirements and Limits

| Requirement | Detail |
|---|---|
| Replica set | Required (even single-node) |
| Oplog | Must have sufficient size for resume |
| Pre/post images | Must enable on collection for `fullDocumentBeforeChange` |
| Max idle time | Cursor closes after 30 min idle (configurable) |

Enable pre-images:

```javascript
db.runCommand({
  collMod: "contracts",
  changeStreamPreAndPostImages: { enabled: true }
})
```

---

## What You Learned

- `watch()` subscribes to real-time collection/database/cluster changes
- Pipeline filters reduce processing to relevant events only
- `fullDocument: "updateLookup"` includes the complete document on updates
- Resume tokens let you restart without missing events
- Use cases: notifications, audit logs, cache invalidation, event sourcing
- Requires a replica set (not standalone)

---

[← Ch 7: Transactions](chapter-07-transactions.md) | [Ch 9: Atlas Search →](chapter-09-search.md)
