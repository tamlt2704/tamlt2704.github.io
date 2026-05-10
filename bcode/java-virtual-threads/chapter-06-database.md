# Chapter 6: Database Access

[← Chapter 5: I/O Bound Workloads](chapter-05-io-bound.md) | [Chapter 7: Pinning →](chapter-07-pinning.md)

---

## The Problem

You deployed virtual threads. VaultPay now handles 10,000 concurrent requests. Each request queries the database — balance check, transaction insert, ledger update. The connection pool is HikariCP with 20 connections.

10,000 virtual threads. 20 database connections.

Monday morning, Raj pages you: "P99 latency spiked to 30 seconds. Thread dumps show 9,980 virtual threads parked on `HikariPool.getConnection()`. The database is fine — 5% CPU. The pool is the bottleneck."

With platform threads, you had 200 threads and 20 connections. Threads waited briefly. With virtual threads, you have 10,000 threads and 20 connections. The queue is 500x longer.

Virtual threads removed the thread pool bottleneck. The connection pool is the new wall.

## Why Connection Pools Exist

Databases limit concurrent connections. PostgreSQL defaults to 100. Each connection holds memory on the server, maintains transaction state, and consumes a file descriptor. You can't have 10,000 connections.

```java
// HikariCP configuration
@Bean
public DataSource dataSource() {
    HikariConfig config = new HikariConfig();
    config.setJdbcUrl("jdbc:postgresql://localhost:5432/vaultpay");
    config.setMaximumPoolSize(20);          // only 20 connections
    config.setConnectionTimeout(30000);      // wait up to 30s for a connection
    return new HikariDataSource(config);
}
```

With 200 platform threads, the ratio was 200:20 (10:1). Acceptable.
With 10,000 virtual threads, the ratio is 10,000:20 (500:1). Disaster.

## The Queuing Math

Average query time: 5ms. Pool size: 20 connections.

Maximum throughput: 20 connections × (1000ms / 5ms) = **4,000 queries/second**.

With 10,000 concurrent requests each needing 3 queries:
- Queries needed: 30,000/second
- Pool capacity: 4,000/second
- Queue depth: grows unbounded
- Wait time: seconds, then timeout

```
Timeline with 10K virtual threads and 20 connections:

VT-1:    [wait.....][query][wait........][query][wait..][query]
VT-2:    [wait........][query][wait.....][query][wait......][query]
...
VT-9980: [wait.................................................][timeout!]
```

## The Fix: Right-Size the Pool

The connection pool formula for virtual threads:

```
pool_size = expected_concurrent_db_operations × avg_query_time / target_latency
```

But there's a hard ceiling: the database itself. PostgreSQL with 100 max connections, minus connections for admin/monitoring, gives you ~80 usable connections.

```java
@Bean
public DataSource dataSource() {
    HikariConfig config = new HikariConfig();
    config.setJdbcUrl("jdbc:postgresql://localhost:5432/vaultpay");
    config.setMaximumPoolSize(50);           // increased, but bounded by DB
    config.setMinimumIdle(10);               // keep some warm
    config.setConnectionTimeout(5000);       // fail fast — don't wait 30s
    config.setMaxLifetime(1800000);          // 30 min
    return new HikariDataSource(config);
}
```

## JDBC with Virtual Threads

JDBC is blocking by design. Every `executeQuery()` blocks the calling thread. With virtual threads, this is fine — the virtual thread unmounts while waiting for the database response:

```java
@Repository
public class TransactionRepository {

    @Autowired private DataSource dataSource;

    public Transaction findById(String txnId) throws SQLException {
        // Virtual thread unmounts here while waiting for:
        // 1. A connection from the pool
        // 2. The query result from the database
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "SELECT * FROM transactions WHERE id = ?")) {

            stmt.setString(1, txnId);

            try (ResultSet rs = stmt.executeQuery()) {  // unmounts during I/O
                if (rs.next()) {
                    return mapRow(rs);
                }
                return null;
            }
        }
    }
}
```

The blocking JDBC call doesn't waste a carrier thread. The virtual thread parks, the carrier picks up another virtual thread, and when the database responds, the original virtual thread resumes.

## Strategy: Semaphore as Application-Level Pool

Instead of relying solely on HikariCP's internal queue, add a semaphore to limit how many virtual threads even attempt to get a connection:

```java
@Service
public class DatabaseService {

    private final DataSource dataSource;
    private final Semaphore dbPermits;

    public DatabaseService(DataSource dataSource) {
        this.dataSource = dataSource;
        // Allow at most 50 concurrent DB operations
        this.dbPermits = new Semaphore(50);
    }

    public <T> T executeQuery(ThrowingFunction<Connection, T> operation)
            throws Exception {
        dbPermits.acquire();  // virtual thread parks here if no permits
        try (Connection conn = dataSource.getConnection()) {
            return operation.apply(conn);
        } finally {
            dbPermits.release();
        }
    }
}
```

Now only 50 virtual threads compete for connections at any time. The other 9,950 park on the semaphore — cheaply, without holding any resources.

## Benchmark: Pool Sizing Impact

```java
public class PoolSizingBenchmark {
    public static void main(String[] args) throws Exception {
        int concurrentRequests = 5000;
        Duration queryTime = Duration.ofMillis(5);

        for (int poolSize : new int[]{10, 20, 50, 100}) {
            Semaphore permits = new Semaphore(poolSize);
            long start = System.currentTimeMillis();

            try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                List<Future<?>> futures = new ArrayList<>();
                for (int i = 0; i < concurrentRequests; i++) {
                    futures.add(executor.submit(() -> {
                        permits.acquire();
                        try {
                            Thread.sleep(queryTime); // simulate query
                        } finally {
                            permits.release();
                        }
                        return null;
                    }));
                }
                for (Future<?> f : futures) f.get();
            }

            long elapsed = System.currentTimeMillis() - start;
            System.out.printf("Pool size %3d: %dms (%.0f queries/s)%n",
                poolSize, elapsed, (concurrentRequests * 1000.0) / elapsed);
        }
    }
}
```

Output:
```
Pool size  10: 2510ms (1992 queries/s)
Pool size  20: 1260ms (3968 queries/s)
Pool size  50:  520ms (9615 queries/s)
Pool size 100:  280ms (17857 queries/s)
```

More connections = more throughput. But you're bounded by what the database can handle.

## Production Configuration

VaultPay's final database configuration:

```yaml
# application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 50        # bounded by PostgreSQL max_connections
      minimum-idle: 10
      connection-timeout: 5000     # fail fast, don't queue for 30s
      idle-timeout: 300000
      max-lifetime: 1800000
      pool-name: vaultpay-pool

# PostgreSQL server
# max_connections = 100 (shared across all app instances)
# 2 app instances × 50 connections = 100 total
```

Key decisions:
- **Fail fast** — 5s timeout instead of 30s. Better to reject than queue indefinitely.
- **Size to database** — pool size is bounded by `max_connections / instance_count`.
- **Semaphore guard** — application-level limit prevents pool starvation.

## What You Learned

- **Connection pool is the new bottleneck** — virtual threads remove thread limits, exposing pool limits
- **Queuing math** — 10K threads / 20 connections = unacceptable wait times
- **JDBC + virtual threads** — blocking calls unmount cleanly, no carrier waste
- **Pool sizing** — bounded by database `max_connections`, not by thread count
- **Semaphore pattern** — limit concurrent DB access at the application level
- **Fail fast** — short connection timeout prevents cascading latency
- **Right-size, don't maximize** — more connections isn't always better (DB overhead)

The database connection pool is tamed. But there's a subtler problem hiding in VaultPay's codebase. Some of those JDBC drivers and legacy services use `synchronized` blocks internally. And `synchronized` does something terrible to virtual threads — it **pins** them to their carrier thread, defeating the entire unmounting mechanism.

---

[← Chapter 5: I/O Bound Workloads](chapter-05-io-bound.md) | [Chapter 7: Pinning →](chapter-07-pinning.md)
