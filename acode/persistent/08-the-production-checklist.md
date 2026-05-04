# Chapter 8: The Production Checklist — What Separates Senior from Staff

[← The Audit Trail](07-the-audit-trail.md) | [Back to Overview →](00-overview.md)

---

## 8.1 — Second-Level Cache (Use Sparingly for Financial Data)

```yaml
spring:
  jpa:
    properties:
      hibernate:
        cache:
          use_second_level_cache: true
          region.factory_class: org.hibernate.cache.jcache.JCacheRegionFactory
      javax:
        cache:
          provider: org.ehcache.jsr107.EhcacheCachingProvider
```

```java
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_ONLY) // ONLY for reference data
@Table(name = "currencies")
public class Currency {
    @Id
    private String code;
    private String name;
    private int decimalPlaces;
}
```

**Never cache `Account` entities.** Stale balance = lost money. Cache only immutable reference data (currencies, country codes, fee schedules).

## 8.2 — Monitoring Queries in Production

```yaml
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

```java
@Configuration
public class HibernateMetricsConfig {
    @Bean
    public StatisticsExporter hibernateMetrics(
            EntityManagerFactory emf, MeterRegistry registry) {
        new HibernateQueryMetrics(emf, Tags.empty()).bindTo(registry);
        return new StatisticsExporter();
    }
}
```

## 8.3 — The Final Architecture

```
                    ┌─────────────────┐
                    │   Load Balancer  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ PayFlow  │  │ PayFlow  │  │ PayFlow  │
        │ Instance │  │ Instance │  │ Instance │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
             │   ┌──────────┴──────────┐   │
             │   │  HikariCP (20 conn) │   │
             │   └──────────┬──────────┘   │
             │              │              │
        ┌────┴──────────────┴──────────────┴────┐
        │         ReadWriteRoutingDataSource      │
        └────────┬──────────────────┬────────────┘
                 │                  │
          ┌──────▼──────┐   ┌──────▼──────┐
          │  PG Primary │   │ PG Replicas │
          │  (writes)   │──▶│  (reads)    │
          │  Partitioned│   │  Partitioned│
          └─────────────┘   └─────────────┘
```

## 8.4 — The Cheat Sheet

| Problem | Wrong Approach | Right Approach |
|---|---|---|
| Money precision | `double` / `float` | `BigDecimal` + `NUMERIC(19,4)` |
| Concurrent updates | Hope for the best | Pessimistic lock with ordered acquisition |
| N+1 queries | `FetchType.EAGER` | Projections + batch fetch + `JOIN FETCH` |
| Bulk inserts | JPA `saveAll()` | `reWriteBatchedInserts=true` + batch_size + SEQUENCE |
| Hot path writes | JPA entities | `JdbcTemplate.batchUpdate()` |
| Read/write contention | Bigger connection pool | Read replicas + `@Transactional(readOnly=true)` |
| Table growth | Pray | Partition by time range |
| Caching balances | L2 cache on Account | Don't. L2 only for immutable reference data |
| Deadlocks | Random lock order | Always lock by ascending ID |
| ID generation | `GenerationType.IDENTITY` | `SEQUENCE` with `allocationSize=50+` |
| Audit trail | Application logging | Ledger table (event sourcing lite) |

---

The story of PayFlow never ends — next chapters would cover CQRS (separating read/write models entirely), distributed transactions across microservices (Saga pattern), and sharding accounts across multiple PostgreSQL clusters. But the foundation above handles the journey from startup to millions of TPS.

---

[← The Audit Trail](07-the-audit-trail.md) | [Back to Overview →](00-overview.md)
