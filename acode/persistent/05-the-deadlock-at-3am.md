# Chapter 5: The Deadlock at 3 AM — "PagerDuty Won't Stop"

[← The Million TPS Challenge](04-the-million-tps-challenge.md) | [Next: The Read Replica Strategy →](06-the-read-replica-strategy.md)

---

3:14 AM. Your phone screams. PagerDuty. Then again. And again.

You fumble for your laptop. The #incidents channel is a wall of red:

```
ERROR: deadlock detected
  Detail: Process 12345 waits for ShareLock on transaction 67890;
          blocked by process 67891.
          Process 67891 waits for ShareLock on transaction 67892;
          blocked by process 12345.
  Hint: See server log for query details.
```

Twelve deadlocks in the last minute. Transfer failures cascading. Customers can't move money.

Linus joins the call. He sounds tired but not surprised.

> "Someone bypassed the ordered locking. Check the new bulk transfer endpoint."

---

## The Crime Scene: Bug #1

A new developer — let's call them "past you from a parallel universe" — wrote a bulk transfer endpoint last week. They didn't read [Chapter 2](02-the-dirty-read-incident.md):

```java
// src/main/java/com/payflow/service/BulkTransferService.java
// ⚠️ BUG: Locks accounts in the order they appear in the request.
// Not in ID order. This WILL deadlock.
@Transactional
public void bulkTransfer(List<TransferRequest> requests) {
    for (TransferRequest req : requests) {
        Account from = accountRepo.findByIdWithLock(req.fromId());
        Account to = accountRepo.findByIdWithLock(req.toId());

        from.setBalance(from.getBalance().subtract(req.amount()));
        to.setBalance(to.getBalance().add(req.amount()));
    }
}
```

Here's the deadlock:

```
Thread A: Transfer Account 1 → Account 2
  → Locks Account 1 ✅
  → Tries to lock Account 2... waiting

Thread B: Transfer Account 2 → Account 1
  → Locks Account 2 ✅
  → Tries to lock Account 1... waiting

Both threads wait forever. PostgreSQL detects it after 1 second
and kills one. But the damage is done — cascading failures.
```

---

## Step 1: Write a Test That Reproduces the Deadlock

```java
// src/test/java/com/payflow/service/DeadlockReproTest.java
@SpringBootTest
class DeadlockReproTest {

    @Autowired private BulkTransferService bulkService;
    @Autowired private AccountRepository accountRepo;

    @Test
    void unordered_locking_causes_deadlock() throws Exception {
        accountRepo.save(new Account(1L, "A", new BigDecimal("10000")));
        accountRepo.save(new Account(2L, "B", new BigDecimal("10000")));

        ExecutorService pool = Executors.newFixedThreadPool(2);
        AtomicInteger deadlocks = new AtomicInteger(0);

        // Thread A: 1 → 2, Thread B: 2 → 1
        pool.submit(() -> {
            try {
                bulkService.bulkTransfer(List.of(
                    new TransferRequest(1L, 2L, BigDecimal.TEN)));
            } catch (Exception e) {
                if (e.getMessage().contains("deadlock")) {
                    deadlocks.incrementAndGet();
                }
            }
        });
        pool.submit(() -> {
            try {
                bulkService.bulkTransfer(List.of(
                    new TransferRequest(2L, 1L, BigDecimal.TEN)));
            } catch (Exception e) {
                if (e.getMessage().contains("deadlock")) {
                    deadlocks.incrementAndGet();
                }
            }
        });

        pool.shutdown();
        pool.awaitTermination(10, TimeUnit.SECONDS);
        assertTrue(deadlocks.get() > 0, "Deadlock should occur");
    }
}
```

---

## Step 2: Fix — Ordered Locking (Again)

The fix is the same principle from [Chapter 2](02-the-dirty-read-incident.md), applied to bulk operations:

```java
// src/main/java/com/payflow/service/BulkTransferService.java
@Service
@RequiredArgsConstructor
public class BulkTransferService {

    private final AccountRepository accountRepo;

    @Transactional
    public void bulkTransfer(List<TransferRequest> requests) {
        // Collect ALL account IDs, sort them, lock in order
        List<Long> allIds = requests.stream()
            .flatMap(r -> Stream.of(r.fromId(), r.toId()))
            .distinct()
            .sorted()
            .toList();

        // Lock all accounts in ascending ID order — no deadlock possible
        Map<Long, Account> locked = new LinkedHashMap<>();
        for (Long id : allIds) {
            locked.put(id, accountRepo.findByIdWithLock(id));
        }

        // Now execute transfers — all locks already held
        for (TransferRequest req : requests) {
            Account from = locked.get(req.fromId());
            Account to = locked.get(req.toId());
            from.setBalance(from.getBalance().subtract(req.amount()));
            to.setBalance(to.getBalance().add(req.amount()));
        }
    }
}
```

---

## The Crime Scene: Bug #2 — Mixing Lock Strategies

While investigating, Priya finds a second bug in a different service:

```java
// src/main/java/com/payflow/service/RiskyTransferService.java
// ⚠️ BUG: Mixing optimistic and pessimistic locking in one transaction
@Transactional
public void riskyTransfer(Long fromId, Long toId, BigDecimal amt) {
    // No lock — loads version=5 via optimistic locking
    Account from = accountRepo.findById(fromId).orElseThrow();
    // Pessimistic lock — SELECT FOR UPDATE
    Account to = accountRepo.findByIdWithLock(toId);

    from.setBalance(from.getBalance().subtract(amt));
    // At flush: UPDATE ... WHERE id=? AND version=5
    // Another thread changed version to 6
    // → OptimisticLockException
    // But 'to' is STILL pessimistic-locked
    // → Other threads waiting on 'to' pile up → cascade failure
}
```

"Pick one strategy per operation," Priya says firmly. "For money: pessimistic. For low-contention reads: optimistic. Never mix them."

---

## Step 3: Fix — Retry Pattern for Optimistic Locking

For scenarios where optimistic locking *is* appropriate (low-contention updates like profile changes), add retries:

```java
// src/main/java/com/payflow/service/ProfileService.java
@Retryable(
    retryFor = OptimisticLockingFailureException.class,
    maxAttempts = 3,
    backoff = @Backoff(delay = 50, multiplier = 2, random = true))
@Transactional
public void updateProfile(Long accountId, String newName) {
    Account account = accountRepo.findById(accountId).orElseThrow();
    account.setOwnerName(newName);
    // If version conflict → Spring retries with fresh data
}
```

Key details:

- `random = true` adds jitter — prevents retry storms when many threads fail simultaneously
- `@Transactional` on the same method means Spring creates a **new** transaction on each retry
- Enable with `@EnableRetry` on your configuration class

```java
// src/main/java/com/payflow/config/RetryConfig.java
@Configuration
@EnableRetry
public class RetryConfig {
    // Spring Retry auto-configures from here
}
```

---

## Step 4: Tests Go Green

Test the ordered locking fix:

```java
// src/test/java/com/payflow/service/DeadlockFixedTest.java
@SpringBootTest
class DeadlockFixedTest {

    @Autowired private BulkTransferService bulkService;
    @Autowired private AccountRepository accountRepo;

    @Test
    void ordered_locking_prevents_deadlock() throws Exception {
        accountRepo.save(new Account(1L, "A", new BigDecimal("10000")));
        accountRepo.save(new Account(2L, "B", new BigDecimal("10000")));

        ExecutorService pool = Executors.newFixedThreadPool(10);
        AtomicInteger failures = new AtomicInteger(0);

        for (int i = 0; i < 100; i++) {
            final long from = (i % 2 == 0) ? 1L : 2L;
            final long to = (i % 2 == 0) ? 2L : 1L;
            pool.submit(() -> {
                try {
                    bulkService.bulkTransfer(List.of(
                        new TransferRequest(from, to, BigDecimal.ONE)));
                } catch (Exception e) { failures.incrementAndGet(); }
            });
        }

        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);
        assertEquals(0, failures.get(),
            "Zero deadlocks with ordered locking");
    }
}
```

Test the retry pattern:

```java
// src/test/java/com/payflow/service/OptimisticRetryTest.java
@SpringBootTest
class OptimisticRetryTest {

    @Autowired private ProfileService profileService;
    @Autowired private AccountRepository accountRepo;

    @Test
    void retry_handles_optimistic_lock_conflict() throws Exception {
        accountRepo.save(new Account(1L, "Alice", new BigDecimal("1000")));

        ExecutorService pool = Executors.newFixedThreadPool(5);
        for (int i = 0; i < 5; i++) {
            final String name = "Name_" + i;
            pool.submit(() -> profileService.updateProfile(1L, name));
        }

        pool.shutdown();
        pool.awaitTermination(10, TimeUnit.SECONDS);

        Account result = accountRepo.findById(1L).orElseThrow();
        assertTrue(result.getOwnerName().startsWith("Name_"),
            "One of the updates should win");
    }
}
```

✅ Both green. You push the fix at 4:22 AM.

---

## The Rules, Carved in Stone

Linus sends this to the engineering channel the next morning:

```
────────────────────────────────────────────────────────────────
LOCKING RULES — VIOLATE THESE AND YOU BUY DONUTS FOR A MONTH
────────────────────────────────────────────────────────────────
1. Always lock accounts in ascending ID order.
2. Never mix optimistic and pessimistic locking in one transaction.
3. Use pessimistic locking for money. Always.
4. Use optimistic locking + @Retryable for low-contention updates.
5. Add jitter to retries (random = true). No retry storms.
────────────────────────────────────────────────────────────────
```

> *The deadlocks are gone. But now Priya notices something else: the dashboard reads are starving the transfer writes. Same database, same connection pool, fighting for the same resources. She has a plan. [Chapter 6](06-the-read-replica-strategy.md).*

---

[← The Million TPS Challenge](04-the-million-tps-challenge.md) | [Next: The Read Replica Strategy →](06-the-read-replica-strategy.md)
