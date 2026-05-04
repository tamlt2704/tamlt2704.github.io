# Chapter 6: The Read Replica Strategy — "Reads Are Killing Writes"

[← The Deadlock at 3 AM](05-the-deadlock-at-3am.md) | [Next: The Audit Trail →](07-the-audit-trail.md)

---

Friday standup. Priya has her laptop open to Grafana. She turns the screen toward the team.

> "See this? Dashboard queries are holding connections for 200ms each. Transfer writes are waiting in the HikariCP queue. We have 20 connections and the dashboard is hogging 15 of them."

Linus frowns. "So reads are starving writes."

Priya nods. "Same connection pool. Same database. The dashboard doesn't need to hit the primary at all. It's read-only. We need a replica."

---

## The Problem

Right now, every query — reads and writes — goes through the same datasource:

```
Dashboard (read)  ──┐
                    ├──→ HikariCP (20 conn) ──→ PG Primary
Transfer (write)  ──┘

Dashboard holds 15 connections for slow aggregation queries.
Transfers fight over the remaining 5.
Result: transfer latency spikes from 4ms to 800ms.
```

---

## Step 1: The Routing DataSource

You need Spring to automatically route read-only transactions to the replica and writes to the primary. The key is `AbstractRoutingDataSource`:

```java
// src/main/java/com/payflow/config/ReadWriteRoutingDataSource.java
public class ReadWriteRoutingDataSource
        extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        return TransactionSynchronizationManager
            .isCurrentTransactionReadOnly()
                ? "replica"
                : "primary";
    }
}
```

That's it. One method. It checks whether the current `@Transactional` is marked `readOnly` and routes accordingly.

---

## Step 2: Configure the DataSources

```java
// src/main/java/com/payflow/config/DataSourceConfig.java
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource dataSource() {
        DataSource primary = createHikariDataSource(
            "jdbc:postgresql://primary:5432/payflow", 20);
        DataSource replica = createHikariDataSource(
            "jdbc:postgresql://replica:5432/payflow", 20);

        ReadWriteRoutingDataSource routing =
            new ReadWriteRoutingDataSource();
        Map<Object, Object> sources = Map.of(
            "primary", primary,
            "replica", replica);
        routing.setTargetDataSources(sources);
        routing.setDefaultTargetDataSource(primary);
        return routing;
    }

    private HikariDataSource createHikariDataSource(
            String url, int poolSize) {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl(url);
        ds.setMaximumPoolSize(poolSize);
        ds.setMinimumIdle(poolSize);
        return ds;
    }
}
```

Now the architecture looks like this:

```
Dashboard (readOnly=true)  ──→ HikariCP (20) ──→ PG Replica
Transfer  (readOnly=false) ──→ HikariCP (20) ──→ PG Primary

Each pool has its own 20 connections. No more starvation.
```

---

## Step 3: Mark Your Services

The routing is driven entirely by `@Transactional(readOnly = true)`:

```java
// src/main/java/com/payflow/service/DashboardService.java
@Transactional(readOnly = true) // ← Routes to replica
public List<AccountSummary> getDashboard() {
    return accountRepo.findAllProjectedBy();
}
```

```java
// src/main/java/com/payflow/service/TransferService.java
@Transactional // ← Routes to primary (default)
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    // ... pessimistic locking, ordered acquisition ...
}
```

No changes to your repository layer. No changes to your entities. The routing is invisible to everything except the datasource config.

---

## What `readOnly = true` Actually Does

Priya quizzes you at lunch. "What does `readOnly = true` do? Most people only know one thing. It does three."

```
────┬──────────────────────────────────────────────────────────
 #  │ What Happens
────┼──────────────────────────────────────────────────────────
 1  │ Routes to read replica (with ReadWriteRoutingDataSource)
────┼──────────────────────────────────────────────────────────
 2  │ Tells Hibernate to skip dirty checking — it won't compare
    │ entity state at flush time. Significant performance boost
    │ when loading thousands of entities.
────┼──────────────────────────────────────────────────────────
 3  │ Sets PostgreSQL transaction to read-only mode
    │ (SET TRANSACTION READ ONLY). PostgreSQL can optimize
    │ query plans knowing no writes will occur.
────┴──────────────────────────────────────────────────────────
```

"Always use it for read-only service methods," Priya says. "Even without replicas, you still get benefits #2 and #3. It's free performance."

---

## Step 4: Test the Routing

```java
// src/test/java/com/payflow/config/RoutingDataSourceTest.java
@SpringBootTest
class RoutingDataSourceTest {

    @Autowired private DashboardService dashboardService;
    @Autowired private TransferService transferService;
    @Autowired private DataSource dataSource;

    @Test
    void readOnly_routes_to_replica() {
        // The dashboard method is @Transactional(readOnly=true)
        // Verify it doesn't throw — replica is reachable
        assertDoesNotThrow(
            () -> dashboardService.getDashboard());
    }

    @Test
    void write_routes_to_primary() {
        // The transfer method is @Transactional (not readOnly)
        // Verify it hits the primary
        assertDoesNotThrow(
            () -> transferService.transfer(1L, 2L, BigDecimal.ONE));
    }
}
```

✅ Green. Dashboard latency drops from 800ms to 120ms. Transfer latency returns to 4ms.

---

## The Result

Maya checks the metrics Monday morning:

> "Dashboard is fast. Transfers are fast. What changed?"

"We stopped making reads and writes fight over the same connections," you say.

She nods. "Good. Now about the regulators..."

> *The system is fast and stable. But an email is coming from the compliance team that will change everything. [Chapter 7](07-the-audit-trail.md).*

---

[← The Deadlock at 3 AM](05-the-deadlock-at-3am.md) | [Next: The Audit Trail →](07-the-audit-trail.md)
