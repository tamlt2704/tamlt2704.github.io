# Chapter 6: Updates & Operators

[← Ch 5](chapter-05-aggregation.md) | [Ch 7 →](chapter-07-transactions.md)

---

## The Problem

> **Priya:** "A client wants to add a new clause to an existing contract, increment the version number, rename a field, and update a specific signer's timestamp — all without replacing the whole document. In SQL, that's 4 separate UPDATE statements across 3 tables."

MongoDB's update operators modify documents surgically. No read-modify-write cycle needed.

---

## Field Operators

### $set — Set Field Values

```javascript
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $set: {
    status: "active",
    "metadata.reviewedBy": "Priya",
    "metadata.reviewedAt": new Date()
  }}
)
```

### $unset — Remove Fields

```javascript
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $unset: { "metadata.priority": "", temporaryFlag: "" } }
)
```

### $rename — Rename a Field

```javascript
db.contracts.updateMany(
  {},
  { $rename: { "clientName": "client" } }
)
```

### $inc — Increment / Decrement

```javascript
// Increment version
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $inc: { version: 1 } }
)

// Decrement credits
db.accounts.updateOne(
  { userId: ObjectId("user001") },
  { $inc: { credits: -10 } }
)
```

### $mul — Multiply

```javascript
// Apply 10% price increase to all contracts
db.contracts.updateMany(
  { status: "pending" },
  { $mul: { value: 1.10 } }
)
```

### $min / $max — Conditional Update

```javascript
// Only update if new value is lower (track lowest bid)
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $min: { lowestBid: 45000 } }
)

// Only update if new value is higher (track high water mark)
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $max: { highestOffer: 120000 } }
)
```

---

## Array Operators

### $push — Add to Array

```javascript
// Add a clause
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $push: { clauses: { id: 4, text: "GDPR compliance required", type: "compliance" } } }
)
```

### $push with $each, $position, $slice

```javascript
// Add multiple clauses at position 1, keep only last 10
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $push: {
    clauses: {
      $each: [
        { id: 5, text: "Arbitration in NYC", type: "legal" },
        { id: 6, text: "Force majeure", type: "legal" }
      ],
      $position: 1,
      $slice: -10
    }
  }}
)
```

### $addToSet — Add Only If Unique

```javascript
// Add tag only if not already present
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $addToSet: { tags: "enterprise" } }
)

// Add multiple unique tags
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $addToSet: { tags: { $each: ["enterprise", "priority", "eu"] } } }
)
```

### $pull — Remove Matching Elements

```javascript
// Remove a clause by type
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $pull: { clauses: { type: "renewal" } } }
)

// Remove multiple tags
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $pull: { tags: { $in: ["deprecated", "old"] } } }
)
```

### $pop — Remove First or Last

```javascript
// Remove last element
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $pop: { clauses: 1 } }   // 1 = last, -1 = first
)
```

---

## arrayFilters — Update Specific Array Elements

The killer feature. Update elements that match a condition without knowing their position.

```javascript
// Mark a specific signer as signed
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $set: { "signatures.$[signer].signedAt": new Date() } },
  { arrayFilters: [{ "signer.name": "Jane Doe" }] }
)

// Update all clauses of type "payment"
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $set: { "clauses.$[c].reviewed": true } },
  { arrayFilters: [{ "c.type": "payment" }] }
)

// Nested: update a specific item in a nested array
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  { $set: { "clauses.$[c].amendments.$[a].approved": true } },
  { arrayFilters: [{ "c.id": 2 }, { "a.version": 3 }] }
)
```

---

## Positional Operator $ — First Match

```javascript
// Update the first clause that matches the query
db.contracts.updateOne(
  { _id: ObjectId("contract001"), "clauses.type": "sla" },
  { $set: { "clauses.$.text": "99.95% uptime SLA" } }
)
```

> `$` updates only the **first** matching element. Use `arrayFilters` for multiple.

---

## Upsert — Insert If Not Found

```javascript
// Create or update a user's settings
db.settings.updateOne(
  { userId: ObjectId("user001") },
  { $set: { theme: "dark", language: "en" }, $setOnInsert: { createdAt: new Date() } },
  { upsert: true }
)
```

`$setOnInsert` only applies when the upsert creates a new document.

---

## Node.js Example

```javascript
const { MongoClient, ObjectId } = require('mongodb');

async function signContract(contractId, signerName) {
  const client = new MongoClient('mongodb://localhost:27017');
  const db = client.db('docuflow');

  const result = await db.collection('contracts').updateOne(
    { _id: new ObjectId(contractId) },
    {
      $set: { "signatures.$[s].signedAt": new Date() },
      $inc: { version: 1 }
    },
    { arrayFilters: [{ "s.name": signerName }] }
  );

  console.log(`Modified: ${result.modifiedCount}`);
  await client.close();
}
```

---

## What You Learned

- Field operators: `$set`, `$unset`, `$rename`, `$inc`, `$mul`, `$min`, `$max`
- Array operators: `$push`, `$pull`, `$addToSet`, `$pop`
- `$each`, `$position`, `$slice` for advanced array pushes
- `arrayFilters` to target specific array elements by condition
- Positional `$` for first-match updates
- `upsert: true` with `$setOnInsert` for create-or-update patterns

---

[← Ch 5: Aggregation](chapter-05-aggregation.md) | [Ch 7: Transactions →](chapter-07-transactions.md)
