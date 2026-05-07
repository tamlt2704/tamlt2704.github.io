# Chapter 20: Priya's Board Meeting

[← Chapter 19: Audit & CDC](chapter-19-audit-cdc.md)

---

## Friday Morning

Priya walks to your desk at 8:45 AM. The board meeting is at 10:00.

"Three things. The dashboard needs to load in under 2 seconds. The revenue numbers need to be correct. And I need to show the board we won't lose data again."

You've spent 19 chapters building toward this moment. Let's prove it works.

---

## The Dashboard: Fast and Correct

### The Revenue Query (Final Version)

```sql
-- Materialized view, refreshed hourly
CREATE MATERIALIZED VIEW mv_board_metrics AS
WITH monthly AS (
    SELECT
        date_trunc('month', order_date) AS month,
        count(*) AS orders,
        count(DISTINCT customer_id) AS customers,
        sum(total_cents) / 100.0 AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY date_trunc('month', order_date)
),
with_growth AS (
    SELECT
        month,
        orders,
        customers,
        revenue,
        sum(revenue) OVER (ORDER BY month) AS cumulative_revenue,
        lag(revenue) OVER (ORDER BY month) AS prev_revenue,
        round(avg(revenue) OVER (
            ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2) AS moving_avg_3m
    FROM monthly
)
SELECT
    to_char(month, 'Mon YYYY') AS period,
    orders,
    customers,
    revenue,
    cumulative_revenue,
    CASE
        WHEN prev_revenue IS NULL OR prev_revenue = 0 THEN NULL
        ELSE round((revenue - prev_revenue) / prev_revenue * 100, 1)
    END AS growth_pct,
    moving_avg_3m
FROM with_growth
ORDER BY month;

CREATE UNIQUE INDEX ON mv_board_metrics (period);
```

Query time: 3ms. Refreshed every hour. Always consistent.

### Customer Health Dashboard

```sql
CREATE MATERIALIZED VIEW mv_customer_health AS
SELECT
    c.name,
    c.plan,
    c.country,
    COALESCE(rev.total_spent, 0) AS lifetime_value,
    rev.last_order,
    COALESCE(tix.open_tickets, 0) AS open_tickets,
    CASE
        WHEN tix.has_critical THEN 'At Risk'
        WHEN rev.last_order < CURRENT_DATE - interval '90 days' THEN 'Inactive'
        WHEN rev.total_spent > 30000 THEN 'Healthy'
        WHEN rev.total_spent > 10000 THEN 'Okay'
        ELSE 'New'
    END AS health
FROM customers c
LEFT JOIN (
    SELECT
        customer_id,
        sum(total_cents) / 100.0 AS total_spent,
        max(order_date) AS last_order
    FROM orders WHERE status = 'completed'
    GROUP BY customer_id
) rev ON rev.customer_id = c.id
LEFT JOIN (
    SELECT
        customer_id,
        count(*) AS open_tickets,
        bool_or(priority IN ('high', 'critical')) AS has_critical
    FROM tickets WHERE status IN ('open', 'in_progress')
    GROUP BY customer_id
) tix ON tix.customer_id = c.id;

CREATE UNIQUE INDEX ON mv_customer_health (name);
```

---

## The Architecture: What You Built

```
┌─────────────────────────────────────────────────────────────────┐
│                        DataPulse Database                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Tables      │  │  Views      │  │  Materialized Views     │ │
│  │  (6 core)   │  │  (live)     │  │  (cached, fast)         │ │
│  │  partitioned │  │             │  │  refreshed hourly       │ │
│  └──────┬──────┘  └─────────────┘  └─────────────────────────┘ │
│         │                                                         │
│  ┌──────┴──────────────────────────────────────────────────────┐ │
│  │  Indexes: B-tree (FK, filters), GIN (JSONB, FTS, arrays)   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Functions   │  │  Triggers   │  │  Procedures             │ │
│  │  (business   │  │  (audit,    │  │  (nightly maintenance)  │ │
│  │   logic)     │  │   timestamps│  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Roles/RLS  │  │  Constraints│  │  Audit Log              │ │
│  │  (access    │  │  (data      │  │  (who changed what)     │ │
│  │   control)  │  │   integrity)│  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  WAL        │  │  Streaming  │  │  Backups                │ │
│  │  Archiving  │  │  Replica    │  │  (daily base + WAL)     │ │
│  │  (PITR)     │  │  (failover) │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Checklist: Production-Ready PostgreSQL

### Data Integrity ✅

- [ ] All tables have primary keys
- [ ] Foreign keys on every relationship
- [ ] NOT NULL on required columns
- [ ] CHECK constraints on enums and ranges
- [ ] UNIQUE constraints where business requires it
- [ ] No orphaned rows (FK enforcement)

### Performance ✅

- [ ] Indexes on all foreign keys
- [ ] Indexes on frequently filtered columns
- [ ] No sequential scans on large tables in hot paths
- [ ] Materialized views for expensive reports
- [ ] Connection pooling (PgBouncer)
- [ ] Query execution time < 100ms for dashboard queries

### Security ✅

- [ ] No application connects as superuser
- [ ] Role-based access (least privilege)
- [ ] Row-level security for multi-tenant data
- [ ] Column-level grants (hide PII from non-essential roles)
- [ ] Service accounts with connection limits

### Reliability ✅

- [ ] WAL archiving enabled
- [ ] Daily base backups
- [ ] Streaming replica for failover
- [ ] Backup restoration tested monthly
- [ ] Monitoring on replication lag
- [ ] Disk space alerts

### Observability ✅

- [ ] Audit triggers on all important tables
- [ ] Slow query logging enabled
- [ ] `pg_stat_statements` for query analysis
- [ ] Dead tuple monitoring (autovacuum health)
- [ ] Connection count monitoring

---

## War Stories: What You Learned

| Chapter | The Problem | The Lesson |
|---|---|---|
| 1 | "Show me the data" | SELECT is your lens into the database |
| 2 | "How much did we sell?" | Aggregates summarize; GROUP BY categorizes |
| 3 | "Connect the tables" | JOINs reunite normalized data; watch for row multiplication |
| 4 | "Add new products" | INSERT/UPDATE/DELETE; always use WHERE; RETURNING is gold |
| 5 | "Data is garbage" | Constraints enforce rules at the database level |
| 6 | "Running total" | Window functions aggregate without collapsing |
| 7 | "Unreadable query" | CTEs name your logic; recursive CTEs traverse trees |
| 8 | "Reusable report" | Views = saved queries; materialized views = cached results |
| 9 | "Complex logic" | CASE expressions; conditional aggregation; FILTER |
| 10 | "Date math" | generate_series fills gaps; intervals do arithmetic |
| 11 | "Dashboard is slow" | EXPLAIN ANALYZE; indexes; eliminate correlated subqueries |
| 12 | "Concurrent updates" | Transactions isolate; locks prevent conflicts |
| 13 | "Automate cleanup" | Functions encapsulate; triggers react; procedures orchestrate |
| 14 | "200M rows" | Partition by range; detach to archive; vacuum per partition |
| 15 | "Flexible attributes" | JSONB for schema-less; arrays for lists; FTS for search |
| 16 | "Access control" | Roles grant; RLS restricts rows; schemas separate |
| 17 | "Migrate safely" | CONCURRENTLY; NOT VALID + VALIDATE; expand-contract |
| 18 | "3 AM crash" | WAL archiving; PITR; streaming replica; test your backups |
| 19 | "Who did this?" | Audit triggers; logical replication; CDC for real-time |

---

## The Board Meeting

10:00 AM. Priya presents. The dashboard loads in 1.2 seconds. Revenue numbers match the finance team's spreadsheet (finally). The architecture slide shows redundancy, backups, and access control.

The board nods. No questions about the database.

That's the best outcome. When the database works, nobody notices. When it doesn't, everyone does.

---

## What's Next (For You)

You've gone from `SELECT * FROM customers` to partitioned tables with streaming replication and row-level security. Here's where to go deeper:

| Topic | Resource |
|---|---|
| Query optimization | `pg_stat_statements`, `auto_explain` |
| Connection pooling | PgBouncer, pgcat |
| Extensions | PostGIS (geo), TimescaleDB (time-series), Citus (distributed) |
| Monitoring | pg_stat_activity, pgwatch2, Datadog |
| Advanced indexing | BRIN indexes, bloom filters, expression indexes |
| Logical decoding | Build custom CDC consumers |
| Testing | pgTAP (unit tests for SQL) |

---

## One Last Thing

Maya walks by your desk at 5 PM on Friday.

"Good week. One thing though — Derek's back. He wants to know why you dropped `v_dont_touch_ask_derek`."

You smile. "Tell him to check the audit log."

---

[← Chapter 19: Audit & CDC](chapter-19-audit-cdc.md)
