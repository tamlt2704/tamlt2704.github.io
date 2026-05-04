# Chapter 8: The Production Checklist — From Intern to Junior

[← The Audit Trail](07-the-audit-trail.md) | [Back to Overview →](00-overview.md)

---

Three months have passed. You've survived the $50k incident, the N+1 apocalypse, the deadlocks at 3 AM, and the regulator audit. Maya calls you into her office.

> "We're promoting you to Junior Engineer. Linus says you've earned it."

But before the title change goes through, Linus has one final task:

> "Architecture review. Walk me through the whole system. Show me you understand what we built and why."

You open your laptop. Deep breath. Let's go.

---

## 8.1 — Second-Level Cache: The Trap

Linus starts with a trick question: "Should we cache Account entities in Hibernate's L2 cache?"

You know this one. "Absolutely not."

"Why?"

"Stale balance = lost money. If the cache serves a balance of $10,000 but the database says $5,000, a transfer could overdraw the account. L2 cache is for **immutable reference data only**."

```yaml
# src/main/resources/application.yml
spring:
  jpa:
    properties:
      hibernate:
        cache:
          use_second_level_cache: true
          region.factory_class: >-
            org.hibernate.cache.jcache.JCacheRegionFactory
      javax:
        cache:
          provider: org.ehcache.jsr107.EhcacheCachingProvider
```

```java
// src/main/java/com/payflow/entity/Currency.java
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_ONLY)
@Table(name = "currencies")
public class Currency {
    @Id
    private String code;   // "USD", "EUR", "GBP"
    private String name;
    private int decimalPlaces;
}
```

Linus nods. "What's safe to cache?"

```
────────────────────────┬──────────────┬──────────────────────────
Entity                  │ Cache?       │ Why
────────────────────────┼──────────────┼──────────────────────────
Currency                │ ✅ Yes       │ Immutable reference data
Country codes           │ ✅ Yes       │ Immutable reference data
Fee schedules           │ ✅ Yes       │ Changes rarely, versioned
Account                 │ ❌ NEVER     │ Stale balance = lost money
Transaction             │ ❌ NEVER     │ High write volume, no reuse
LedgerEntry             │ ❌ NEVER     │ Append-only, no reuse
────────────────────────┴──────────────┴──────────────────────────
```

---

## 8.2 — Monitoring: Seeing Inside Hibernate

"How do you know if a query is slow in production?" Linus asks.

```yaml
# src/main/resources/application.yml
spring:
  jpa:
    properties:
      hibernate:
        session:
          events:
            log:
              LOG_QUERIES_SLOWER_THAN_MS: 100
        generate_statistics: true
```

This logs any query taking longer than 100ms. But logs aren't enough — you need metrics in Grafana:

```java
// src/main/java/com/payflow/config/HibernateMetricsConfig.java
@Configuration
public class HibernateMetricsConfig {

    @Bean
    public HibernateQueryMetrics hibernateMetrics(
            EntityManagerFactory emf, MeterRegistry registry) {
        HibernateQueryMetrics metrics =
            new HibernateQueryMetrics(emf, Tags.empty());
        metrics.bindTo(registry);
        return metrics;
    }
}
```

"What metrics do you watch?" Linus presses.

```
────────────────────────────────┬──────────────────────────────────
Metric                          │ Alert Threshold
────────────────────────────────┼──────────────────────────────────
hibernate.query.execution.max   │ > 500ms
hikaricp.connections.pending    │ > 5 for 30 seconds
hikaricp.connections.timeout    │ any occurrence
hibernate.sessions.open         │ > pool size (connection leak)
hibernate.cache.miss.count      │ > 90% miss rate (cache useless)
────────────────────────────────┴──────────────────────────────────
```

---

## 8.3 — The Final Architecture

Linus asks you to draw the architecture on the whiteboard. You draw:

```
                       ┌─────────────────────┐
                       │    Load Balancer     │
                       └──────────┬──────────┘
                                  │
               ┌──────────────────┼──────────────────┐
               ▼                  ▼                  ▼
         ┌──────────┐      ┌──────────┐      ┌──────────┐
         │ PayFlow  │      │ PayFlow  │      │ PayFlow  │
         │ App  #1  │      │ App  #2  │      │ App  #3  │
         └────┬─────┘      └────┬─────┘      └────┬─────┘
              │                 │                  │
              └────────┬────────┴────────┬─────────┘
                       │                 │
                       ▼                 ▼
              ┌────────────────┐ ┌────────────────┐
              │  HikariCP (20) │ │  HikariCP (20) │
              │  Write Pool    │ │  Read Pool     │
              └───────┬────────┘ └───────┬────────┘
                      │                  │
                      ▼                  ▼
              ┌──────────────┐   ┌──────────────┐
              │  PG Primary  │──▶│  PG Replica   │
              │  (writes)    │   │  (reads)      │
              │  Partitioned │   │  Partitioned  │
              └──────────────┘   └──────────────┘
```

"Walk me through a transfer," Linus says.

1. Request hits load balancer → routed to any app instance
2. `@Transactional` → HikariCP write pool → PG Primary
3. Pessimistic lock in ascending ID order → no deadlocks
4. Balance update + ledger entries in one atomic transaction
5. Dirty checking flushes changes at commit
6. Batch inserts for ledger entries (`reWriteBatchedInserts=true`)

"And a dashboard read?"

1. `@Transactional(readOnly = true)` → HikariCP read pool → PG Replica
2. Interface projections → only needed columns
3. Batch fetch → 2 queries instead of N+1
4. No dirty checking overhead

Linus smiles. "You pass."

---

## 8.4 — The Cheat Sheet

You tape this to the wall above your monitor:

```
──────────────────────┬──────────────────────────┬──────────────────────────────────
Problem               │ Wrong Approach           │ Right Approach
──────────────────────┼──────────────────────────┼──────────────────────────────────
Money precision       │ double / float           │ BigDecimal + NUMERIC(19,4)
──────────────────────┼──────────────────────────┼──────────────────────────────────
Concurrent updates    │ Hope for the best        │ Pessimistic lock + ordered
                      │                          │ acquisition
──────────────────────┼──────────────────────────┼──────────────────────────────────
N+1 queries           │ FetchType.EAGER          │ Projections + batch fetch
──────────────────────┼──────────────────────────┼──────────────────────────────────
Bulk inserts          │ JPA saveAll() default    │ reWriteBatchedInserts=true
                      │                          │ + batch_size + SEQUENCE
──────────────────────┼──────────────────────────┼──────────────────────────────────
Hot path writes       │ JPA entities             │ JdbcTemplate.batchUpdate()
──────────────────────┼──────────────────────────┼──────────────────────────────────
Read/write contention │ Bigger connection pool   │ Read replicas +
                      │                          │ @Transactional(readOnly=true)
──────────────────────┼──────────────────────────┼──────────────────────────────────
Table growth          │ Pray                     │ Partition by time range
──────────────────────┼──────────────────────────┼──────────────────────────────────
Caching balances      │ L2 cache on Account      │ Don't. L2 only for immutable
                      │                          │ reference data
──────────────────────┼──────────────────────────┼──────────────────────────────────
Deadlocks             │ Random lock order        │ Always lock by ascending ID
──────────────────────┼──────────────────────────┼──────────────────────────────────
ID generation         │ GenerationType.IDENTITY  │ SEQUENCE with allocationSize=50+
──────────────────────┼──────────────────────────┼──────────────────────────────────
Audit trail           │ Application logging      │ Ledger table (event sourcing lite)
──────────────────────┴──────────────────────────┴──────────────────────────────────
```

---

## What's Next

The story of PayFlow never ends. The next chapters — if you stick around — would cover:

- **CQRS** — separating read and write models entirely
- **Saga pattern** — distributed transactions across microservices
- **Sharding** — splitting accounts across multiple PostgreSQL clusters

But the foundation you built — from a naive `save()` call to a million-TPS payment engine — is solid. Every decision was forged in a production incident. Every fix was proven by a test.

Linus shakes your hand on your last day as an intern.

> "You came in thinking JPA was just `save()` and `findById()`. Now you know it's a tool — powerful when you understand it, dangerous when you don't. Welcome to the team, Junior."

---

[← The Audit Trail](07-the-audit-trail.md) | [Back to Overview →](00-overview.md)
