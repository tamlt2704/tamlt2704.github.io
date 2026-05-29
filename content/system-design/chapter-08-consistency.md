# Chapter 8: Consistency & Distributed Systems

[← Chapter 7: Microservices](/blog/system-design/chapter-07-microservices) | [Chapter 9: Real-World Designs →](/blog/system-design/chapter-09-real-world)

---

## The CAP Theorem

In a distributed system, you can only guarantee **two out of three**:

```
         Consistency
            /\
           /  \
          /    \
         / CP   \
        /________\
       /\   CA   /\
      /  \      /  \
     / AP \    /    \
    /______\  /______\
Availability    Partition Tolerance
```

| Property                | Meaning                                             |
| ----------------------- | --------------------------------------------------- |
| **Consistency**         | Every read returns the most recent write            |
| **Availability**        | Every request gets a response (even if stale)       |
| **Partition Tolerance** | System works despite network failures between nodes |

**The reality:** Network partitions WILL happen. So you're really choosing between:

- **CP** — Consistent + Partition-tolerant (sacrifice availability during partition). Examples: ZooKeeper, HBase, MongoDB (default)
- **AP** — Available + Partition-tolerant (sacrifice consistency during partition). Examples: Cassandra, DynamoDB, CouchDB

**CA doesn't exist in distributed systems** — if you have no partitions, you have a single node (not distributed).

---

## Consistency Models

From strongest to weakest:

| Model                      | Guarantee                                       | Performance | Example                   |
| -------------------------- | ----------------------------------------------- | ----------- | ------------------------- |
| **Linearizability**        | Reads always see latest write, globally ordered | Slowest     | Single-node DB, ZooKeeper |
| **Sequential consistency** | All nodes see operations in same order          | Slow        | Distributed locks         |
| **Causal consistency**     | Causally related operations are ordered         | Medium      | Social media comments     |
| **Eventual consistency**   | All replicas converge eventually                | Fastest     | DNS, CDN, Cassandra       |

### Strong Consistency

Every read sees the latest write. Requires coordination (consensus).

```
Client writes X=5 to Primary
Primary replicates to ALL replicas before acknowledging
Client reads from ANY node → guaranteed to see X=5

Cost: High latency (wait for all replicas)
```

### Eventual Consistency

Write is acknowledged immediately. Replicas converge over time.

```
Client writes X=5 to Node A
Node A acknowledges immediately
Node A replicates to B, C in background (milliseconds to seconds)

Client reads from Node B → might see X=3 (old value)
Wait a moment...
Client reads from Node B → sees X=5 (converged)
```

**When eventual consistency is fine:**

- Social media feeds (seeing a post 2 seconds late is OK)
- Product view counts
- Recommendation engines
- Search indexes

**When you need strong consistency:**

- Bank account balances
- Inventory counts (prevent overselling)
- Distributed locks
- Leader election

---

## Consensus Algorithms

How do distributed nodes agree on a value?

### Raft (Understandable Consensus)

```
Nodes: [Leader] [Follower] [Follower] [Follower] [Follower]

Write flow:
1. Client sends write to Leader
2. Leader appends to its log
3. Leader replicates to Followers
4. Majority (3/5) acknowledge → committed
5. Leader responds to client

Leader election:
- Leader sends heartbeats every 150ms
- If Follower doesn't hear heartbeat for 300ms → starts election
- Candidate requests votes from all nodes
- Majority votes → new Leader
```

**Used by:** etcd, Consul, CockroachDB, TiKV

### Paxos

Older, more complex. Same goal as Raft but harder to understand and implement.

**Used by:** Google Spanner, Chubby

---

## Distributed Locks

When multiple services need exclusive access to a resource:

### Redis-based (Redlock)

```java
// Acquire lock
String lockKey = "lock:order:" + orderId;
String lockValue = UUID.randomUUID().toString();
boolean acquired = redis.set(lockKey, lockValue, "NX", "EX", 30);
// NX = only if not exists, EX = expire in 30 seconds

if (acquired) {
    try {
        // Critical section — only one instance executes this
        processOrder(orderId);
    } finally {
        // Release lock (only if we still own it)
        String script = "if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end";
        redis.eval(script, List.of(lockKey), List.of(lockValue));
    }
}
```

**Problems with Redis locks:**

- Redis is AP, not CP — during failover, lock can be lost
- Clock skew can cause premature expiry
- For critical systems, use ZooKeeper or etcd instead

### ZooKeeper-based (Stronger)

```
/locks/order-123
  ├── _lock_0000000001 (Service A) ← lowest sequence = lock holder
  ├── _lock_0000000002 (Service B) ← watches previous node
  └── _lock_0000000003 (Service C) ← watches previous node
```

Each service creates an ephemeral sequential node. Lowest sequence number holds the lock. Others watch the node before them.

---

## Vector Clocks & Conflict Resolution

When you have multiple writers (AP systems), conflicts happen. How to detect and resolve them?

### Vector Clocks

Track causality across nodes:

```
Node A: [A:1, B:0, C:0]  → writes X=1
Node B: [A:1, B:1, C:0]  → reads from A, writes X=2
Node C: [A:1, B:0, C:1]  → reads from A, writes X=3 (concurrent with B!)

Conflict detected: B's write and C's write are concurrent
(neither happened-before the other)

Resolution strategies:
- Last-write-wins (LWW): use timestamp, risk losing data
- Application merge: present both to user ("conflict!")
- CRDTs: data structures that auto-merge without conflicts
```

### CRDTs (Conflict-Free Replicated Data Types)

Data structures that can be merged without coordination:

| CRDT         | Type                      | Use Case            |
| ------------ | ------------------------- | ------------------- |
| G-Counter    | Grow-only counter         | View counts, likes  |
| PN-Counter   | Positive-negative counter | Upvotes/downvotes   |
| G-Set        | Grow-only set             | Tags, followers     |
| OR-Set       | Observed-remove set       | Shopping cart items |
| LWW-Register | Last-write-wins value     | User profile fields |

```
G-Counter example (3 nodes):
Node A: [A:5, B:0, C:0]  → A counted 5
Node B: [A:0, B:3, C:0]  → B counted 3
Node C: [A:0, B:0, C:7]  → C counted 7

Merge: max each entry → [A:5, B:3, C:7]
Total = 5 + 3 + 7 = 15

No conflicts possible! Always converges to correct total.
```

---

## Two-Phase Commit (2PC)

Distributed transaction across multiple databases:

```
Phase 1 (Prepare):
Coordinator → DB A: "Can you commit?"  → "Yes"
Coordinator → DB B: "Can you commit?"  → "Yes"

Phase 2 (Commit):
Coordinator → DB A: "Commit!"  → Done
Coordinator → DB B: "Commit!"  → Done
```

**Problems:**

- Blocking: if coordinator crashes after Phase 1, participants are stuck
- Slow: requires multiple round trips
- Single point of failure: coordinator

**In practice:** Avoid 2PC. Use sagas (compensating transactions) or design around it.

---

## Quorum Reads/Writes

In a replicated system with N nodes:

- **W** = number of nodes that must acknowledge a write
- **R** = number of nodes that must respond to a read

**Rule:** If `W + R > N`, you get strong consistency.

```
N=3 nodes:

Strong consistency: W=2, R=2 (W+R=4 > 3)
  Write to 2 nodes, read from 2 nodes → at least 1 overlap

High availability writes: W=1, R=3
  Fast writes, but reads must check all nodes

High availability reads: W=3, R=1
  Slow writes, but any single node has latest data
```

**DynamoDB example:**

- Default: eventually consistent reads (R=1)
- Optional: strongly consistent reads (R=quorum)

---

## Split Brain

When a network partition causes two groups of nodes to each think they're the leader:

```
Network partition:
┌─────────────────┐    ╳    ┌─────────────────┐
│ Node A (leader) │  split  │ Node C (leader) │
│ Node B          │         │ Node D          │
└─────────────────┘         └─────────────────┘

Both sides accept writes → data diverges!
```

**Prevention:**

- **Fencing tokens:** Each leader gets a monotonically increasing token. Storage rejects writes with old tokens.
- **Quorum:** Require majority to elect leader. Only one side of a partition can have majority.
- **STONITH (Shoot The Other Node In The Head):** Force-kill the old leader via hardware (power off).

---

## Practical Consistency Decisions

| System Component    | Consistency Needed            | Why                                    |
| ------------------- | ----------------------------- | -------------------------------------- |
| User authentication | Strong                        | Can't have stale passwords/permissions |
| Account balance     | Strong                        | Money must be accurate                 |
| Shopping cart       | Eventual                      | Temporary inconsistency is tolerable   |
| Social feed         | Eventual                      | Seeing a post 2s late is fine          |
| Inventory count     | Strong (or bounded staleness) | Prevent overselling                    |
| Search index        | Eventual                      | Slight delay in indexing is OK         |
| Leaderboard         | Eventual                      | Real-time accuracy not critical        |
| Distributed config  | Strong (linearizable)         | All nodes must see same config         |

---

## Key Takeaways

1. **CAP is a spectrum**, not a binary choice. Most systems are "mostly available, mostly consistent."
2. **Eventual consistency is the default** in distributed systems. Design for it.
3. **Strong consistency is expensive** — use it only where business logic demands it.
4. **Idempotency is your friend** — makes retries safe in eventually consistent systems.
5. **Consensus (Raft/Paxos) is the foundation** of strongly consistent distributed systems.
6. **CRDTs eliminate conflicts** for specific data types — use them when applicable.

---

[Chapter 9: Real-World System Designs →](/blog/system-design/chapter-09-real-world)
