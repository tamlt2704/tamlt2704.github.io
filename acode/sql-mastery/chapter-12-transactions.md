# Chapter 12: "Two Reports Updated the Same Row"

[← Chapter 11: Performance](chapter-11-performance.md) | [Chapter 13: Functions & Triggers →](chapter-13-functions-triggers.md)

---

## The Incident

Wednesday afternoon. Hank upgrades a customer's plan from "pro" to "enterprise" while Maya's revenue report is running. The report shows the customer as "enterprise" but with "pro" pricing. Half the data is from before the update, half from after.

Maya: "The report is wrong. It mixed old and new data."

You: "How is that possible? I thought databases were... safe?"

Silent Sasha: "Transactions. Isolation. Learn them."

---

## Transactions: All or Nothing

A transaction groups multiple statements into one atomic unit. Either ALL succeed, or NONE do.

```sql
BEGIN;

UPDATE customers SET plan = 'enterprise' WHERE id = 2;
INSERT INTO mrr_events (customer_id, event_type, amount_cents, event_date)
VALUES (2, 'expansion', 20000, CURRENT_DATE);
UPDATE orders SET total_cents = 29900 WHERE customer_id = 2 AND status = 'pending';

COMMIT;
```

If any statement fails (constraint violation, disk full, connection drop), everything rolls back:

```sql
BEGIN;
UPDATE customers SET plan = 'enterprise' WHERE id = 2;
-- Oops, this violates a constraint:
INSERT INTO mrr_events (customer_id, event_type, amount_cents, event_date)
VALUES (99999, 'expansion', 20000, CURRENT_DATE);
-- ERROR: foreign key violation
ROLLBACK;  -- nothing changed, customer is still 'pro'
```

### ACID Properties

| Property | Meaning |
|---|---|
| **Atomicity** | All or nothing — partial changes never persist |
| **Consistency** | Constraints are always satisfied |
| **Isolation** | Concurrent transactions don't interfere |
| **Durability** | Committed data survives crashes |

---

## The Problem: Concurrent Access

Two transactions running at the same time:

```
Transaction A (Maya's report):        Transaction B (Hank's update):
─────────────────────────────         ─────────────────────────────
BEGIN;                                BEGIN;
SELECT plan FROM customers            
  WHERE id = 2;                       
  → 'pro'                            UPDATE customers SET plan = 'enterprise'
                                        WHERE id = 2;
SELECT sum(total_cents)               COMMIT;
  FROM orders WHERE customer_id = 2;
  → uses enterprise pricing (?!)
COMMIT;
```

Transaction A sees "pro" for the plan but "enterprise" pricing for orders — because B committed between A's two queries. This is called a **non-repeatable read**.

---

## Isolation Levels

PostgreSQL offers four isolation levels. Each prevents different anomalies:

```sql
-- Set for current transaction
BEGIN ISOLATION LEVEL READ COMMITTED;
-- or
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- or
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Use When |
|---|---|---|---|---|
| Read Uncommitted* | Possible | Possible | Possible | Never in Postgres |
| **Read Committed** (default) | No | Possible | Possible | Most operations |
| **Repeatable Read** | No | No | No** | Reports, analytics |
| **Serializable** | No | No | No | Financial, critical |

*Postgres treats Read Uncommitted as Read Committed.
**Postgres's Repeatable Read also prevents phantoms (it uses snapshot isolation).

### Read Committed (Default)

Each statement sees the latest committed data at the time that statement starts. Different statements in the same transaction can see different snapshots.

```sql
-- Transaction A
BEGIN;  -- Read Committed (default)
SELECT plan FROM customers WHERE id = 2;  -- sees 'pro'
-- ... B commits an update to 'enterprise' ...
SELECT plan FROM customers WHERE id = 2;  -- sees 'enterprise' (!)
COMMIT;
```

### Repeatable Read

The transaction sees a snapshot from the moment it started. No matter what other transactions commit, you see the same data throughout.

```sql
-- Transaction A
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT plan FROM customers WHERE id = 2;  -- sees 'pro'
-- ... B commits an update to 'enterprise' ...
SELECT plan FROM customers WHERE id = 2;  -- STILL sees 'pro'
COMMIT;
```

Maya's report should use Repeatable Read — it needs a consistent snapshot.

### Serializable

The strictest level. Transactions behave as if they ran one after another, even if they actually ran concurrently. If Postgres detects a conflict, it aborts one transaction:

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- ... do work ...
COMMIT;
-- ERROR: could not serialize access due to concurrent update
-- Your app must retry the transaction
```

Use for financial operations where correctness is more important than performance.

---

## Locking: Explicit Control

### Row-Level Locks

```sql
-- Lock specific rows (other transactions wait)
SELECT * FROM customers WHERE id = 2 FOR UPDATE;
-- Now no one else can UPDATE or DELETE this row until you COMMIT

-- Lock but skip if already locked (don't wait)
SELECT * FROM customers WHERE id = 2 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row

-- Skip locked rows (useful for job queues)
SELECT * FROM orders WHERE status = 'pending'
ORDER BY created_at LIMIT 1
FOR UPDATE SKIP LOCKED;
```

| Lock Mode | Allows | Blocks |
|---|---|---|
| `FOR UPDATE` | Other SELECTs | Other FOR UPDATE, UPDATE, DELETE |
| `FOR SHARE` | Other FOR SHARE, SELECTs | UPDATE, DELETE |
| `FOR NO KEY UPDATE` | Other FOR SHARE | FOR UPDATE, UPDATE of key columns |

### Advisory Locks

Application-level locks that don't lock any rows:

```sql
-- Acquire a lock (blocks if already held)
SELECT pg_advisory_lock(12345);

-- Try to acquire (returns true/false, doesn't block)
SELECT pg_try_advisory_lock(12345);

-- Release
SELECT pg_advisory_unlock(12345);
```

Useful for: "Only one process should run this report at a time."

---

## Deadlocks

Two transactions each waiting for the other's lock:

```
Transaction A:                    Transaction B:
BEGIN;                            BEGIN;
UPDATE orders SET ... WHERE id=1; UPDATE orders SET ... WHERE id=2;
-- holds lock on order 1          -- holds lock on order 2
UPDATE orders SET ... WHERE id=2; UPDATE orders SET ... WHERE id=1;
-- waits for B's lock on order 2  -- waits for A's lock on order 1
-- DEADLOCK!
```

Postgres detects deadlocks and kills one transaction:

```
ERROR: deadlock detected
DETAIL: Process 1234 waits for ShareLock on transaction 5678;
        blocked by process 5678.
        Process 5678 waits for ShareLock on transaction 1234;
        blocked by process 1234.
```

**Prevention**: Always lock rows in the same order. If you need to update orders 1 and 2, always lock 1 first, then 2.

```sql
-- ✅ Consistent ordering prevents deadlocks
BEGIN;
SELECT * FROM orders WHERE id IN (1, 2) ORDER BY id FOR UPDATE;
-- Now safely update both
UPDATE orders SET status = 'completed' WHERE id IN (1, 2);
COMMIT;
```

---

## Practical: Safe Balance Transfer

Transfer $100 from customer A to customer B:

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;

-- Lock both rows in consistent order (by ID)
SELECT * FROM accounts WHERE id IN (1, 2) ORDER BY id FOR UPDATE;

-- Check sufficient balance
DO $$
BEGIN
    IF (SELECT balance FROM accounts WHERE id = 1) < 10000 THEN
        RAISE EXCEPTION 'Insufficient funds';
    END IF;
END $$;

-- Transfer
UPDATE accounts SET balance = balance - 10000 WHERE id = 1;
UPDATE accounts SET balance = balance + 10000 WHERE id = 2;

COMMIT;
```

Atomic. Isolated. No partial transfers. No double-spending.

---

## Practical: Fixing Maya's Report

```sql
-- Maya's report now uses a consistent snapshot
BEGIN ISOLATION LEVEL REPEATABLE READ;

SELECT
    c.name,
    c.plan,
    sum(o.total_cents) / 100.0 AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'completed'
GROUP BY c.id, c.name, c.plan
ORDER BY revenue DESC;

COMMIT;
```

Even if Hank updates a customer mid-report, Maya sees the data as it was when her transaction started. Consistent. Correct.

---

## SAVEPOINT: Partial Rollback

```sql
BEGIN;
INSERT INTO orders (...) VALUES (...);  -- succeeds

SAVEPOINT before_risky;
INSERT INTO order_items (...) VALUES (...);  -- fails!
ROLLBACK TO before_risky;  -- undo only the failed part

-- Continue with the transaction
INSERT INTO order_items (...) VALUES (...);  -- different values, succeeds
COMMIT;  -- the order AND the second item are saved
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
BEGIN                           │ Start a transaction
COMMIT                          │ Save all changes
ROLLBACK                        │ Undo all changes
SAVEPOINT name                  │ Create a restore point
ROLLBACK TO name                │ Undo to savepoint
────────────────────────────────┼──────────────────────────────────────
BEGIN ISOLATION LEVEL ...       │ Set isolation for this transaction
FOR UPDATE                      │ Lock selected rows
FOR UPDATE NOWAIT               │ Lock or fail immediately
FOR UPDATE SKIP LOCKED          │ Lock or skip (job queues)
pg_advisory_lock(id)            │ Application-level lock
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Maya: "Every night at 2 AM, we need to archive old orders, update MRR calculations, and send a summary. Can the database do this automatically?"

Functions. Procedures. Triggers.

---

[← Chapter 11: Performance](chapter-11-performance.md) | [Chapter 13: Functions & Triggers →](chapter-13-functions-triggers.md)
