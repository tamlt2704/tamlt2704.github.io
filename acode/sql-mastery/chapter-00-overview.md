# SQL Mastery: A PostgreSQL Survival Story

You thought you'd be writing application code. Then **Maya**, the data team lead at **DataPulse** — a mid-size analytics startup that sells dashboards to e-commerce companies — drops a message in your DMs:

> "Our backend dev quit. The database is a mess. Queries are slow, reports are wrong, and the CEO's dashboard shows negative revenue. You start Monday."

You show up. The database has 47 tables, no documentation, and a view called `v_dont_touch_ask_derek`. Derek left six months ago.

Your mission: understand the data, fix the queries, build the reports, and make the database fast. Before the board meeting on Friday.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | The New Backend Dev | "I know SELECT * FROM... that counts, right?" |
| **Maya** | Data Team Lead | Thinks in JOINs. Draws ER diagrams on napkins. |
| **Priya** | CEO | "The dashboard says we made negative $40,000 last Tuesday." |
| **Derek** | The Dev Who Left | His code has no comments. His views have no documentation. |
| **Hank** | Sales VP | "I need a report by 3 PM. No, not that report. The other one." |
| **Silent Sasha** | DBA | Communicates via EXPLAIN ANALYZE output. Fixes prod at 4 AM. |
| **The Slow Query** | That one report | Takes 47 seconds. Runs every 5 minutes. Blocks everything. |

---

## The Stack

Everything runs locally. One tool.

| Tool | What It Does |
|---|---|
| **PostgreSQL 16** | The database. That's it. That's the stack. |
| **psql** | Terminal client for Postgres |
| **Docker** | Runs Postgres without installing anything |

```bash
docker run -d --name datapulse-db -p 5432:5432 \
  -e POSTGRES_DB=datapulse -e POSTGRES_PASSWORD=datapulse \
  postgres:16
```

Connect:

```bash
psql -h localhost -U postgres -d datapulse
```

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Someone needs something from the database
   │
   ▼
  🤔 You learn the SQL concept needed to solve it
   │
   ▼
  ⌨️  You write the query
   │
   ▼
  💥 Something is wrong — duplicates, nulls, performance
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  📋 Next request arrives
```

No concept shows up before you need it. You won't hear about window functions until Hank asks for a running total. You won't touch CTEs until a query becomes unreadable. You won't learn about indexes until The Slow Query blocks the dashboard.

The problems come first. The SQL follows.

---

## The Roadmap

### Part 1: Foundations — "What's in This Database?"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Request                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Show me all the customers"            │ SELECT, FROM, WHERE, ORDER BY, LIMIT
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "How much did we sell last month?"      │ Aggregates: COUNT, SUM, AVG, GROUP BY
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Connect orders to customers"          │ JOINs: INNER, LEFT, RIGHT, FULL, CROSS
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Add a new product line"               │ INSERT, UPDATE, DELETE, UPSERT
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "The data is garbage"                  │ Constraints, data types, NULLs, COALESCE
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Intermediate — "Make It Useful"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Request                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "I need a running total"               │ Window functions: ROW_NUMBER, SUM OVER
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "This query is unreadable"             │ Subqueries, CTEs, WITH RECURSIVE
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Build me a reusable report"           │ Views, materialized views, REFRESH
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Handle this complex logic"            │ CASE, conditional aggregation, FILTER
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Work with dates properly"             │ Date/time functions, intervals, generate_series
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Advanced — "Make It Fast"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Request                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "The dashboard is slow"                │ EXPLAIN ANALYZE, indexes, query plans
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "Two reports updated the same row"     │ Transactions, isolation levels, locking
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "Automate the nightly cleanup"         │ Functions, procedures, triggers
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "The table has 200 million rows"       │ Partitioning, VACUUM, table maintenance
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Store flexible product attributes"    │ JSONB, arrays, full-text search
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Don't Break Prod"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Request                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "We need role-based access"            │ Users, roles, GRANT, row-level security
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Migrate without downtime"             │ Schema migrations, ALTER TABLE safely
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "The database crashed at 3 AM"         │ Backups, replication, pg_dump, WAL
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "Show me everything that happened"     │ Audit trails, logical replication, CDC
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ Priya's board meeting                  │ Query optimization war stories, review
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Database: DataPulse Schema

This is what you inherit on day one. Derek built it. Derek is gone.

```sql
-- Customers
CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    plan        TEXT DEFAULT 'free',  -- free, starter, pro, enterprise
    signed_up   TIMESTAMP DEFAULT now(),
    country     TEXT
);

-- Products (the dashboards DataPulse sells)
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,         -- analytics, reporting, alerts
    price_cents INTEGER NOT NULL,
    active      BOOLEAN DEFAULT true,
    created_at  TIMESTAMP DEFAULT now()
);

-- Orders
CREATE TABLE orders (
    id           SERIAL PRIMARY KEY,
    customer_id  INTEGER REFERENCES customers(id),
    order_date   DATE NOT NULL,
    status       TEXT DEFAULT 'pending',  -- pending, completed, refunded, cancelled
    total_cents  INTEGER NOT NULL
);

-- Order line items
CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER REFERENCES orders(id),
    product_id  INTEGER REFERENCES products(id),
    quantity    INTEGER NOT NULL DEFAULT 1,
    unit_price  INTEGER NOT NULL  -- price at time of purchase, in cents
);

-- Monthly recurring revenue tracking
CREATE TABLE mrr_events (
    id           SERIAL PRIMARY KEY,
    customer_id  INTEGER REFERENCES customers(id),
    event_type   TEXT NOT NULL,  -- new, expansion, contraction, churn, reactivation
    amount_cents INTEGER NOT NULL,
    event_date   DATE NOT NULL
);

-- Support tickets
CREATE TABLE tickets (
    id           SERIAL PRIMARY KEY,
    customer_id  INTEGER REFERENCES customers(id),
    subject      TEXT NOT NULL,
    priority     TEXT DEFAULT 'medium',  -- low, medium, high, critical
    status       TEXT DEFAULT 'open',    -- open, in_progress, resolved, closed
    created_at   TIMESTAMP DEFAULT now(),
    resolved_at  TIMESTAMP
);
```

Six tables. Customers buy products through orders. Revenue is tracked in MRR events. Customers file support tickets. Simple enough — until you start querying it.

---

## Prerequisites

- **Docker** (to run Postgres)
- **A terminal** with `psql` (or any SQL client: DBeaver, pgAdmin, DataGrip)
- **Curiosity** — every chapter builds on the last

---

## Seed Data

Run this after connecting to the database. It gives you enough data to make queries interesting:

```sql
-- We'll build the seed script in Chapter 1
-- For now, just have the empty schema ready
```

---

[Next: Chapter 1 — "Show Me All the Customers" →](chapter-01-select.md)
