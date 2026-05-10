# Chapter 7: Transactions

[← Ch 6](chapter-06-updates.md) | [Ch 8 →](chapter-08-streams.md)

---

## The Problem

> **Priya:** "When a client purchases a contract package, we need to: deduct credits from their account, create the contract, and log the transaction. If any step fails, everything must roll back. Single-document atomicity isn't enough here."

MongoDB guarantees atomicity for single-document operations. For multi-document, multi-collection operations, you need **transactions**.

---

## When You DON'T Need Transactions

Single-document updates are already atomic:

```javascript
// This is atomic — no transaction needed
db.contracts.updateOne(
  { _id: ObjectId("contract001") },
  {
    $set: { status: "signed" },
    $push: { signatures: { name: "Jane", signedAt: new Date() } },
    $inc: { version: 1 }
  }
)
```

> If you can model your data so related changes happen in one document, you avoid transactions entirely. That's the MongoDB way.

---

## When You NEED Transactions

- Transferring credits between accounts
- Creating a contract AND deducting payment
- Moving a document between collections
- Any operation spanning multiple documents that must be all-or-nothing

---

## Basic Transaction Pattern

```javascript
const session = db.getMongo().startSession();
session.startTransaction();

try {
  const accounts = session.getDatabase("docuflow").accounts;
  const contracts = session.getDatabase("docuflow").contracts;
  const ledger = session.getDatabase("docuflow").ledger;

  // Step 1: Deduct credits
  const result = accounts.updateOne(
    { userId: ObjectId("user001"), credits: { $gte: 100 } },
    { $inc: { credits: -100 } },
    { session }
  );

  if (result.modifiedCount === 0) {
    throw new Error("Insufficient credits");
  }

  // Step 2: Create contract
  contracts.insertOne({
    title: "Enterprise License",
    client: "Acme Corp",
    status: "active",
    value: 100,
    createdAt: new Date()
  }, { session });

  // Step 3: Log transaction
  ledger.insertOne({
    type: "purchase",
    userId: ObjectId("user001"),
    amount: -100,
    description: "Enterprise License purchase",
    createdAt: new Date()
  }, { session });

  // All good — commit
  session.commitTransaction();
  print("Transaction committed successfully");

} catch (error) {
  session.abortTransaction();
  print("Transaction aborted: " + error.message);

} finally {
  session.endSession();
}
```

---

## Read Concern and Write Concern

```javascript
session.startTransaction({
  readConcern: { level: "snapshot" },
  writeConcern: { w: "majority" },
  readPreference: "primary"
});
```

| Setting | Meaning |
|---|---|
| `readConcern: "snapshot"` | Consistent point-in-time reads |
| `writeConcern: "majority"` | Wait for majority of replicas |
| `readPreference: "primary"` | Read from primary only |

---

## Retry Logic — Transient Errors

Transactions can fail due to transient issues (network, elections). MongoDB labels these errors so you can retry.

```javascript
async function runTransactionWithRetry(session, txnFunc) {
  while (true) {
    try {
      await txnFunc(session);
      break;
    } catch (error) {
      if (error.hasOwnProperty("errorLabels") &&
          error.errorLabels.includes("TransientTransactionError")) {
        print("Transient error, retrying...");
        continue;
      }
      throw error;
    }
  }
}
```

---

## Credit Transfer Example

```javascript
function transferCredits(fromUserId, toUserId, amount) {
  const session = db.getMongo().startSession();

  try {
    session.startTransaction();

    const accounts = session.getDatabase("docuflow").accounts;

    // Debit sender (with balance check)
    const debit = accounts.updateOne(
      { userId: fromUserId, credits: { $gte: amount } },
      { $inc: { credits: -amount } },
      { session }
    );

    if (debit.modifiedCount === 0) {
      throw new Error("Insufficient balance");
    }

    // Credit receiver
    accounts.updateOne(
      { userId: toUserId },
      { $inc: { credits: amount } },
      { session }
    );

    session.commitTransaction();
    print(`Transferred ${amount} credits`);

  } catch (e) {
    session.abortTransaction();
    print("Transfer failed: " + e.message);
  } finally {
    session.endSession();
  }
}

transferCredits(ObjectId("user001"), ObjectId("user002"), 50);
```

---

## Transaction Limits

| Constraint | Limit |
|---|---|
| Max runtime | 60 seconds (default) |
| Max size | 16MB oplog entry |
| Lock scope | Document-level |
| Requires | Replica set or sharded cluster |

> **Standalone `mongod` does not support transactions.** Use a replica set (even single-node) for development.

---

## Node.js Example with Driver

```javascript
const { MongoClient, ObjectId } = require('mongodb');

async function purchaseContract(userId, contractData) {
  const client = new MongoClient('mongodb://localhost:27017/?replicaSet=rs0');
  const session = client.startSession();

  try {
    await session.withTransaction(async () => {
      const db = client.db('docuflow');

      // Deduct credits
      const { modifiedCount } = await db.collection('accounts').updateOne(
        { userId: new ObjectId(userId), credits: { $gte: contractData.value } },
        { $inc: { credits: -contractData.value } },
        { session }
      );

      if (modifiedCount === 0) throw new Error('Insufficient credits');

      // Create contract
      await db.collection('contracts').insertOne(
        { ...contractData, createdAt: new Date() },
        { session }
      );
    });

    console.log('Purchase complete');
  } finally {
    await session.endSession();
    await client.close();
  }
}
```

> `session.withTransaction()` handles retries for transient errors automatically.

---

## What You Learned

- Single-document operations are already atomic — no transaction needed
- Multi-document transactions use `startSession()` → `startTransaction()` → `commitTransaction()`
- Always `abortTransaction()` on error and `endSession()` in finally
- Use `readConcern: "snapshot"` and `writeConcern: "majority"` for strong consistency
- Retry on `TransientTransactionError` labels
- `session.withTransaction()` (driver) handles retries automatically
- Transactions require a replica set — not available on standalone

---

[← Ch 6: Updates](chapter-06-updates.md) | [Ch 8: Change Streams →](chapter-08-streams.md)
