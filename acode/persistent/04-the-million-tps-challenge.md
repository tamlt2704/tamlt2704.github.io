# Chapter 4: The Million TPS Challenge — "We Got Acquired by a Bank"

[← The N+1 Apocalypse](03-the-n-plus-1-apocalypse.md) | [Next: The Deadlock at 3 AM →](05-the-deadlock-at-3am.md)

---

All-hands meeting. Maya stands at the front, grinning.

> "We've been acquired by First National Bank. They're bringing their transaction volume to our platform. We need to handle **one million transactions per second**."

You check your metrics dashboard. Current throughput: **2,000 TPS**.

That's a 500x improvement. You look at Linus. He's already typing.

> "We're not rewriting. We're optimizing. One bottleneck at a time."

---

## Incident 1: Batch Writes — The Single Biggest Win

Linus pulls up the Hibernate SQL logs. Every `saveAll()` call generates individual INSERT statements. 50 records = 50 round trips to PostgreSQL.

"One config change," he says. "Watch."

```yaml
# src/main/resources/application.yml
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 50
          batch_versioned_data: true
        order_inserts: true
        order_updates: true
  datasource:
    url: >-
      jdbc:postgresql://localhost:5432/payflow
      ?reWriteBatchedInserts=true
```

The magic is `reWriteBatchedInserts=true`. It transforms this:

```sql
-- Without: 50 round trips
INSERT INTO transactions (...) VALUES (1, 100, ...);
INSERT INTO transactions (...) VALUES (2, 200, ...);
INSERT INTO transactions (...) VALUES (3, 300, ...);
```

Into this:

```sql
-- With reWriteBatchedInserts=true: 1 round trip
INSERT INTO transactions (...)
VALUES (1, 100, ...), (2, 200, ...), (3, 300, ...);
```

You write a benchmark test:

```java
// src/test/java/com/payflow/perf/BatchInsertTest.java
@SpringBootTest
class BatchInsertTest {

    @Autowired private TransactionRepository txnRepo;

    @Test
    void batch_insert_performance() {
        List<Transaction> batch = IntStream.range(0, 10_000)
            .mapToObj(i -> new Transaction(
                null, 1L, 2L,
                new BigDecimal("10.00"),
                TxnStatus.COMPLETED, Instant.now()))
            .toList();

        long start = System.nanoTime();
        txnRepo.saveAll(batch);
        long ms = (System.nanoTime() - start) / 1_000_000;

        System.out.println("10,000 inserts in " + ms + "ms");
        assertTrue(ms < 5000, "Should complete under 5 seconds");
    }
}
```

Before: 10,000 inserts in 12,400ms. After: 10,000 inserts in **890ms**. A 14x improvement from config alone.

---

## Incident 2: Bypass JPA for Hot Paths

Linus profiles the transfer endpoint. Even with batching, Hibernate's dirty checking adds overhead: it compares every field of every entity on flush.

> "For the critical path, we go raw. JdbcTemplate. Same transaction, no entity overhead."

```java
// src/main/java/com/payflow/repository/BulkTransferRepository.java
@Repository
@RequiredArgsConstructor
public class BulkTransferRepository {

    private final JdbcTemplate jdbc;

    @Transactional
    public int[] executeBatch(List<TransferCommand> cmds) {
        return jdbc.batchUpdate(
            """
            UPDATE accounts
            SET balance = balance - ?, version = version + 1
            WHERE id = ? AND balance >= ?
            """,
            new BatchPreparedStatementSetter() {
                public void setValues(PreparedStatement ps, int i)
                        throws SQLException {
                    ps.setBigDecimal(1, cmds.get(i).amount());
                    ps.setLong(2, cmds.get(i).fromId());
                    ps.setBigDecimal(3, cmds.get(i).amount());
                }
                public int getBatchSize() {
                    return cmds.size();
                }
            });
    }
}
```

"Check the update counts," Linus warns. "A `0` means the WHERE clause didn't match — either the account doesn't exist or insufficient funds."

```java
// src/test/java/com/payflow/repository/BulkTransferTest.java
@SpringBootTest
class BulkTransferTest {

    @Autowired private BulkTransferRepository bulkRepo;
    @Autowired private JdbcTemplate jdbc;

    @Test
    void batch_update_returns_zero_for_insufficient_funds() {
        jdbc.update(
            "INSERT INTO accounts (id, owner_name, balance, version) "
            + "VALUES (99, 'Test', 50.00, 0)");

        int[] counts = bulkRepo.executeBatch(List.of(
            new TransferCommand(99L, 2L, new BigDecimal("999.00"))
        ));

        assertEquals(0, counts[0],
            "Should return 0 — balance < amount");
    }
}
```

**The pattern**: Use JPA for CRUD, reads, and moderate writes. Use `JdbcTemplate` for hot paths. They coexist in the same `@Transactional` boundary.

---

## Incident 3: Connection Pool Tuning

You're at 15,000 TPS now. But under load, you see connection timeout errors. Your instinct: increase the pool size.

Priya stops you.

> "More connections means *slower*, not faster. Trust the math."

```yaml
# src/main/resources/application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20     # NOT 100. NOT 200.
      minimum-idle: 20
      connection-timeout: 3000
      leak-detection-threshold: 30000
```

The PostgreSQL formula:

> `connections = (core_count × 2) + effective_spindle_count`

An 8-core server with SSD: `(8 × 2) + 1 = 17`. Round to 20.

"But why?" you ask. "More connections means more parallelism, right?"

"Wrong," Priya says. "Each PostgreSQL connection is a process. More processes = more context switching. More lock contention. More cache thrashing. A pool of 200 on an 8-core box is 200 processes fighting over 8 CPUs."

She shows you the benchmark:

```
────────────────────┬──────────────┬──────────────
Pool Size           │ Throughput   │ Avg Latency
────────────────────┼──────────────┼──────────────
20 connections      │ 18,200 TPS   │ 4.2ms
50 connections      │ 16,800 TPS   │ 6.1ms
200 connections     │ 11,400 TPS   │ 14.8ms
────────────────────┴──────────────┴──────────────
```

More connections. Less throughput. Everyone gets this wrong.

---

## Incident 4: Partitioning — When One Table Isn't Enough

At 1M TPS, your `transactions` table grows by **86 billion rows per day**. Queries slow to a crawl. Indexes bloat. Vacuuming takes hours.

Linus: "Time to partition."

```sql
-- src/main/resources/db/migration/V5__partition_transactions.sql
CREATE TABLE transactions (
    id              BIGINT NOT NULL,
    from_account_id BIGINT NOT NULL,
    to_account_id   BIGINT NOT NULL,
    amount          NUMERIC(19,4) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE transactions_2026_05
    PARTITION OF transactions
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

CREATE TABLE transactions_2026_06
    PARTITION OF transactions
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

JPA doesn't know about partitions. It just sees `transactions`. But your queries **must** include `created_at` in the WHERE clause:

```java
// src/main/java/com/payflow/repository/TransactionRepository.java
// ✅ Partition-aware — scans only 1 partition
@Query("""
    SELECT t FROM Transaction t
    WHERE t.fromAccountId = :id
    AND t.createdAt BETWEEN :start AND :end
    """)
List<Transaction> findByAccountAndDateRange(
    @Param("id") Long id,
    @Param("start") Instant start,
    @Param("end") Instant end);
```

Without the date range:

```java
// ❌ Full scan across ALL partitions — catastrophic at scale
@Query("SELECT t FROM Transaction t WHERE t.fromAccountId = :id")
List<Transaction> findByAccount(@Param("id") Long id);
```

You write a test to verify partition pruning:

```java
// src/test/java/com/payflow/repository/PartitionPruningTest.java
@SpringBootTest
class PartitionPruningTest {

    @Autowired private EntityManager em;

    @Test
    void query_with_date_range_prunes_partitions() {
        String plan = (String) em.createNativeQuery(
            "EXPLAIN SELECT * FROM transactions "
            + "WHERE from_account_id = 1 "
            + "AND created_at BETWEEN '2026-05-01' AND '2026-05-31'"
        ).getSingleResult();

        assertTrue(plan.contains("transactions_2026_05"),
            "Should scan only May partition");
        assertFalse(plan.contains("transactions_2026_06"),
            "Should NOT scan June partition");
    }
}
```

---

## The Scoreboard

```
────────────────────────────┬──────────────
Optimization                │ TPS After
────────────────────────────┼──────────────
Baseline (Chapter 1)        │ 2,000
+ Batch writes              │ 15,000
+ JdbcTemplate hot paths    │ 45,000
+ Connection pool tuning    │ 65,000
+ Partitioning              │ 200,000+
+ Horizontal scaling (3x)   │ 600,000+
+ Read replicas (Chapter 6) │ 1,000,000+
────────────────────────────┴──────────────
```

You're not at a million yet. But the architecture can get there.

> *The system is fast. But speed creates contention. And contention creates deadlocks. Your phone will ring at 3 AM in [Chapter 5](05-the-deadlock-at-3am.md).*

---

[← The N+1 Apocalypse](03-the-n-plus-1-apocalypse.md) | [Next: The Deadlock at 3 AM →](05-the-deadlock-at-3am.md)
