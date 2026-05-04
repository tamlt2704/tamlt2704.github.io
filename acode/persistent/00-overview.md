# The Tale of PayFlow: Building a Million-TPS Payment Engine with Spring JPA & PostgreSQL

You join **PayFlow**, a fintech startup. Day one, the CTO says:

> "We process payments. PostgreSQL, Spring Boot, JPA. Ship it."

This is the story of how you go from a naive `save()` call to handling **millions of money transactions per second** — and every disaster you hit along the way.

---

## Table of Contents

| Chapter | Title | Key Concepts |
|---|---|---|
| [01](01-the-genesis.md) | The Genesis | Entity design, `BigDecimal`, sequence strategy |
| [02](02-the-dirty-read-incident.md) | The Dirty Read Incident | Transactions, pessimistic locking, isolation levels |
| [03](03-the-n-plus-1-apocalypse.md) | The N+1 Apocalypse | Query performance, projections, batch fetching |
| [04](04-the-million-tps-challenge.md) | The Million TPS Challenge | Batch writes, JDBC, connection pooling, partitioning |
| [05](05-the-deadlock-at-3am.md) | The Deadlock at 3 AM | Deadlock prevention, optimistic vs pessimistic, retry |
| [06](06-the-read-replica-strategy.md) | The Read Replica Strategy | Read/write splitting, routing datasource |
| [07](07-the-audit-trail.md) | The Audit Trail | Ledger pattern, event sourcing lite, JPA auditing |
| [08](08-the-production-checklist.md) | The Production Checklist | L2 cache, monitoring, architecture, cheat sheet |
