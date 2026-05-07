# The Tale of PayFlow: A JPA Survival Story

It's Monday morning. You walk into **PayFlow**, a fintech startup crammed into a WeWork. You're the new intern. Your badge still smells like fresh plastic.

The CTO, **Maya**, shakes your hand and says:

> "We move money. Millions of dollars a day. PostgreSQL, Spring Boot, JPA. Your tech lead is Linus. Don't break production."

You nod. How hard can it be?

You have no idea what's coming.

---

## How to Read This

This isn't a textbook. This is a survival journal.

Every chapter follows the same loop — the loop that will define your career at PayFlow:

```
  😴 Something breaks (Slack at 2 AM)
   │
   ▼
  🔍 Write a test that reproduces the bug
   │
   ▼
  🧠 Understand WHY it broke
   │
   ▼
  🔧 Fix it
   │
   ▼
  ✅ Test goes green
   │
   ▼
  😴 Sleep... until the next incident
```

You will write buggy code. On purpose. You'll deploy it. You'll watch it burn. Then you'll understand *why* it burned, and you'll never make that mistake again.

The characters you'll meet:

- **Linus** — your tech lead. Mass of curly hair. Mass of opinions. Assigns you tasks that sound simple but aren't.
- **Maya** — the CTO. Sends Slack messages at 2 AM when money vanishes. Makes business decisions that reshape your architecture.
- **Priya** — senior dev. Quiet. Notices things nobody else does. Saves your career at least twice.

---

## The Roadmap

```
────┬────────────────────────────────────┬────────────────────────────────────────────────
Part│The Incident                        │What You Learn
────┼────────────────────────────────────┼────────────────────────────────────────────────
 01 │ "Start simple," says Linus         │ Entity design, BigDecimal, @Version, SEQUENCE
────┼────────────────────────────────────┼────────────────────────────────────────────────
 02 │ $50,000 vanishes overnight         │ @Transactional, pessimistic locking, isolation
────┼────────────────────────────────────┼────────────────────────────────────────────────
 03 │ Dashboard takes 30 seconds         │ N+1 queries, projections, batch fetching
────┼────────────────────────────────────┼────────────────────────────────────────────────
 04 │ "We need 1 million TPS"            │ Batch writes, JdbcTemplate, HikariCP, partitions
────┼────────────────────────────────────┼────────────────────────────────────────────────
 05 │ PagerDuty at 3 AM — deadlocks      │ Lock ordering, optimistic vs pessimistic, retry
────┼────────────────────────────────────┼────────────────────────────────────────────────
 06 │ Reads are starving writes          │ Read replicas, routing datasource, readOnly
────┼────────────────────────────────────┼────────────────────────────────────────────────
 07 │ "The regulators are coming"        │ Ledger pattern, reconciliation, JPA auditing
────┼────────────────────────────────────┼────────────────────────────────────────────────
 08 │ Intern → Junior: the final review  │ L2 cache, monitoring, architecture, cheat sheet
────┴────────────────────────────────────┴────────────────────────────────────────────────
```

---

## Prerequisites

Before your first day, make sure you have:

- **Java 17+** — PayFlow runs on LTS releases
- **Spring Boot 3.x** — with `spring-boot-starter-data-jpa`
- **PostgreSQL 15+** — the database that handles our money
- **A healthy fear of `double` for money** — you'll understand why in Chapter 1

Optional but recommended:

- Docker (for local PostgreSQL)
- A Slack account (for the 2 AM messages)
- Coffee. Lots of coffee.

---

[Next: The Genesis →](01-the-genesis.md)
