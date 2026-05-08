# Chapter 11: Design a Distributed Job Scheduler

[← Distributed Cache](./chapter-10-cache.md) | [Next: Rideshare Matching →](./chapter-12-rideshare.md)

---

## The Question

> "Design a distributed job scheduler — like cron at scale. It should execute millions of scheduled jobs reliably with exactly-once semantics, support priority scheduling, handle worker failures, and scale horizontally. Think of it as the backbone for background tasks across a large platform."

---

## Step 1: Requirements & Scope

**Functional:**
- Schedule jobs: one-time (run at timestamp) and recurring (cron expression)
- Priority levels (critical, high, normal, low)
- Exactly-once execution guarantee
- Job status tracking (scheduled, running, completed, failed)
- Retry with configurable backoff
- Dead letter queue for permanently failed jobs

**Non-functional:**
- 10M jobs scheduled per day
- Execution accuracy within 1 second of scheduled time
- Survive worker and scheduler node failures
- Horizontal scaling (add workers for more throughput)
- Job execution time: seconds to hours

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Jobs/sec | 10M / 86400 | ~115 jobs/sec |
| Peak (10x burst) | 115 × 10 | ~1,150 jobs/sec |
| Concurrent running jobs | avg 5 min runtime × 115/sec | ~35,000 concurrent |
| Job metadata storage | 10M/day × 365 × 1KB | ~3.6 TB/year |
| Workers needed | 35,000 / 50 jobs per worker | ~700 workers |

---

## Step 3: API Design

```
POST /api/v1/jobs
  Body: {
    "name": "send_weekly_report",
    "schedule": "0 9 * * MON",       // cron expression (recurring)
    "execute_at": "2024-01-15T09:00Z", // one-time
    "handler": "reports.weekly",
    "payload": { "user_id": "u_123" },
    "priority": "normal",
    "max_retries": 3,
    "timeout_sec": 300
  }
  Response: { "job_id": "job_001", "status": "scheduled" }

GET /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}

GET /api/v1/jobs/{job_id}/executions
  Response: { "executions": [{ "attempt": 1, "status": "failed", ... }] }
```

---

## Step 4: Data Model

**Jobs (SQL — needs ACID for state transitions):**

| Field | Type |
|-------|------|
| job_id (PK) | UUID |
| name | VARCHAR |
| schedule (cron) | VARCHAR |
| next_run_at | TIMESTAMP (indexed) |
| handler | VARCHAR |
| payload | JSON |
| priority | INT |
| status | ENUM (scheduled, running, completed, failed, dead) |
| max_retries | INT |
| retry_count | INT |
| timeout_sec | INT |
| locked_by | VARCHAR (worker_id) |
| locked_at | TIMESTAMP |

**Execution History (append-only):**

| Field | Type |
|-------|------|
| execution_id (PK) | UUID |
| job_id | UUID |
| attempt | INT |
| status | ENUM |
| started_at | TIMESTAMP |
| finished_at | TIMESTAMP |
| error_message | TEXT |

---

## Step 5: High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Job Submitter  │────▶│   Job Service    │────▶│   Job Store     │
│  (any service)  │     │   (API)          │     │   (Postgres)    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌──────────────────┐
                                                 │   Scheduler      │
                                                 │   (tick every 1s)│
                                                 └────────┬─────────┘
                                                          │
                                                          ▼
                                                 ┌──────────────────┐
                                                 │  Priority Queue  │
                                                 │  (Redis/Kafka)   │
                                                 └────────┬─────────┘
                                                          │
                              ┌────────────────────────────┼────────────────┐
                              ▼                            ▼                ▼
                     ┌──────────────┐           ┌──────────────┐  ┌──────────────┐
                     │  Worker 1    │           │  Worker 2    │  │  Worker N    │
                     └──────────────┘           └──────────────┘  └──────────────┘
                                                          │
                                                          ▼
                                                 ┌──────────────────┐
                                                 │  Dead Letter Q   │
                                                 └──────────────────┘
```

---

## Step 6: Deep Dive

### Exactly-Once Execution

**Problem:** Two scheduler nodes both pick up the same job → executed twice.

**Solution: Pessimistic locking with fencing tokens.**

```sql
-- Atomic claim: only one worker wins
UPDATE jobs
SET status = 'running', locked_by = 'worker_7', locked_at = NOW()
WHERE job_id = 'job_001'
  AND status = 'scheduled'
  AND next_run_at <= NOW();
-- Only succeeds if status is still 'scheduled' (optimistic lock)
```

**Fencing token:** Each lock acquisition gets a monotonically increasing token. Workers include token in completion message. Stale tokens rejected.

### Scheduler Leader Election

Multiple scheduler instances for HA, but only one actively polls:

- Use distributed lock (ZooKeeper, etcd, or Redis RedLock)
- Leader polls job store every 1 second for due jobs
- If leader dies, another instance acquires lock within seconds
- Alternatively: partition jobs by hash, each scheduler owns a partition

### Priority Scheduling

```
Queue structure:
  critical_queue  → processed first, dedicated workers
  high_queue      → processed second
  normal_queue    → bulk of traffic
  low_queue       → processed when others empty
```

**Starvation prevention:** Weighted fair queuing. Even low-priority jobs get some execution slots (e.g., 70/20/8/2 split).

### Failure Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Worker crashes mid-job | Lock timeout (locked_at + timeout_sec < NOW) | Re-queue job |
| Job exceeds timeout | Worker self-monitors | Kill job, mark failed, retry |
| Scheduler dies | Leader election timeout | New leader takes over |
| DB unavailable | Health checks | Queue in memory, flush when DB returns |

**Heartbeat pattern:** Running workers send heartbeat every 30s. If no heartbeat for 2× interval → assume dead, release their locks.

### Dead Letter Queue

After max_retries exhausted:
1. Move job to dead letter queue
2. Alert operations team
3. Store full execution history for debugging
4. Manual retry available via admin API

### Sharding for Scale

Partition jobs across multiple scheduler instances:

```
scheduler_partition = hash(job_id) % num_schedulers
```

Each scheduler only polls its partition. Rebalance on scheduler add/remove (consistent hashing).

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| DB polling overhead | Partition + index on next_run_at |
| Thundering herd at minute boundaries | Jitter: spread jobs ±5 seconds |
| Worker pool exhaustion | Auto-scale workers based on queue depth |
| Long-running jobs blocking slots | Separate pools for short vs long jobs |
| Clock skew across nodes | NTP sync, use DB timestamp as source of truth |

**Jitter:** Many cron jobs scheduled at :00 seconds. Add random jitter (0-5s) to spread load. `actual_run = scheduled_time + random(0, 5000ms)`

---

## Key Talking Points

- Exactly-once via atomic DB claim (UPDATE WHERE status='scheduled')
- Leader election for scheduler HA, or partition jobs across schedulers
- Heartbeat + lock timeout detects dead workers
- Dead letter queue prevents infinite retry loops
- Jitter prevents thundering herd at common cron boundaries

---

## Common Mistakes

- No mechanism for exactly-once (jobs run multiple times)
- Polling all jobs every tick (doesn't scale — use indexed next_run_at)
- Single scheduler with no failover (single point of failure)
- No timeout handling (zombie jobs hold resources forever)
- Ignoring clock skew in distributed environment
- No dead letter queue (failed jobs retry forever, wasting resources)

---

[← Distributed Cache](./chapter-10-cache.md) | [Next: Rideshare Matching →](./chapter-12-rideshare.md)
