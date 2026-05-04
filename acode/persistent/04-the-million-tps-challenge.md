# Chapter 4: The Million TPS Challenge — "We Got Acquired by a Bank"

[← The N+1 Apocalypse](03-the-n-plus-1-apocalypse.md) | [Next: The Deadlock at 3 AM →](05-the-deadlock-at-3am.md)

---

PayFlow gets acquired. The new requirement: **1,000,000 transactions per second**. Your current setup does 2,000. Time to architect.

## 4.1 — Batch Writes: The Single Biggest Win

```yaml
# application.yml
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
    url: jdbc:postgresql://localhost:5432/payflow?reWriteBatchedInserts=true
```

**`reWriteBatchedInserts=true`** is the most impactful one-line change in PostgreSQL + JPA performance tuning. It transforms:

```sql
-- Without (50 round trips)
INSERT INTO transactions (id, amount, ...) VALUES (1, 100, ...);
INSERT INTO transactions (id, amount, ...) VALUES (2, 200, ...);

-- With reWriteBatchedInserts=true (1 round trip)
INSERT INTO transactions (id, amount, ...)
VALUES (1, 100, ...), (2, 200, ...), ... ;
```

## 4.2 — Bypass JPA for Hot Paths

At million TPS, JPA's dirty checking becomes overhead. For the critical transfer path, use `JdbcTemplate`:

```java
@Repository
@RequiredArgsConstructor
public class BulkTransferRepository {

    private final JdbcTemplate jdbc;

    @Transactional
    public int[] executeBatch(List<TransferCommand> commands) {
        return jdbc.batchUpdate(
            """
            UPDATE accounts SET balance = balance - ?, version = version + 1
            WHERE id = ? AND balance >= ?
            """,
            new BatchPreparedStatementSetter() {
                public void setValues(PreparedStatement ps, int i) throws SQLException {
                    ps.setBigDecimal(1, commands.get(i).amount());
                    ps.setLong(2, commands.get(i).fromId());
                    ps.setBigDecimal(3, commands.get(i).amount());
                }
                public int getBatchSize() { return commands.size(); }
            }
        );
        // Check update counts — 0 means insufficient funds
    }
}
```

**Architectural pattern**: Use JPA for CRUD, reads, and moderate-throughput writes. Use `JdbcTemplate` for hot paths. They coexist in the same `@Transactional` boundary.

## 4.3 — Connection Pool Tuning

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20    # NOT 100. See below.
      minimum-idle: 20
      connection-timeout: 3000
      leak-detection-threshold: 30000
```

**Why 20, not 200?** The PostgreSQL formula:

> `connections = (core_count * 2) + effective_spindle_count`

A 8-core server with SSD: `(8 * 2) + 1 = 17`, round to 20. More connections = more context switching = *slower*. This is counterintuitive and almost everyone gets it wrong.

## 4.4 — Partitioning: When One Table Isn't Enough

At 1M TPS, your `transactions` table grows by 86 billion rows/day. You need partitioning:

```sql
CREATE TABLE transactions (
    id              BIGINT NOT NULL,
    from_account_id BIGINT NOT NULL,
    to_account_id   BIGINT NOT NULL,
    amount          NUMERIC(19,4) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE transactions_2026_05 PARTITION OF transactions
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

CREATE TABLE transactions_2026_06 PARTITION OF transactions
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

JPA doesn't know about partitions — it just sees `transactions`. But your queries **must** include `created_at` in the WHERE clause or PostgreSQL scans every partition:

```java
// ✅ Partition-aware — scans only 1 partition
@Query("SELECT t FROM Transaction t WHERE t.fromAccountId = :id AND t.createdAt BETWEEN :start AND :end")
List<Transaction> findByAccountAndDateRange(Long id, Instant start, Instant end);

// ❌ Full table scan across ALL partitions
@Query("SELECT t FROM Transaction t WHERE t.fromAccountId = :id")
List<Transaction> findByAccount(Long id);
```

---

[← The N+1 Apocalypse](03-the-n-plus-1-apocalypse.md) | [Next: The Deadlock at 3 AM →](05-the-deadlock-at-3am.md)
