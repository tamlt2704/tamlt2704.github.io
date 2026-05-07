# Chapter 2: The Dirty Read Incident — "Where Did $50,000 Go?"

[← The Genesis](01-the-genesis.md) | [Next: The N+1 Apocalypse →](03-the-n-plus-1-apocalypse.md)

---

Two weeks in. You're sleeping soundly when your phone buzzes at 2:07 AM.

**Maya (CTO)** in #incidents:

> 🚨 A customer is reporting $50,000 missing from their account. This is not a drill. Who's on call?

You are. You are on call.

---

## The Crime Scene

You pull up the transfer service you wrote last week. It looked so clean. So simple:

```java
// src/main/java/com/payflow/service/TransferService.java
// ⚠️ BUG: No @Transactional. Each save() auto-commits independently.
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepo.findById(fromId).orElseThrow();
    Account to = accountRepo.findById(toId).orElseThrow();

    from.setBalance(from.getBalance().subtract(amount));
    to.setBalance(to.getBalance().add(amount));

    accountRepo.save(from);  // ← Auto-commits. Money leaves.
    // 💥 Server crashed RIGHT HERE at 2:03 AM.
    accountRepo.save(to);    // ← Never executed. Money never arrives.
}
```

The `from` account was debited. The `to` account was never credited. $50,000 — gone.

But that's only **Bug #1**.

---

## Bug #2: The Race Condition

Priya joins the incident call. She's calm. She's seen this before.

> "Check the audit logs. Two transfers hit the same account at the same time."

She's right. Here's what happened:

```
Thread A reads Account 42: balance = $100,000
Thread B reads Account 42: balance = $100,000
Thread A subtracts $50,000 → saves balance = $50,000
Thread B subtracts $50,000 → saves balance = $50,000
                                                  ↑
                              Should be $0, but Thread B overwrote Thread A.
                              Customer got $50,000 for free.
```

No transaction boundary + concurrent access = **manufactured money**.

---

## Step 1: Write a Test That Reproduces the Bug

Before you fix anything, prove the bug exists:

```java
// src/test/java/com/payflow/service/TransferRaceTest.java
@SpringBootTest
class TransferRaceTest {

    @Autowired private TransferService transferService;
    @Autowired private AccountRepository accountRepo;

    @Test
    void concurrent_transfers_lose_money() throws Exception {
        Account a = accountRepo.save(
            new Account(1L, "Alice", new BigDecimal("1000.00")));

        ExecutorService pool = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(1);

        // 10 threads each try to debit $100 simultaneously
        for (int i = 0; i < 10; i++) {
            pool.submit(() -> {
                latch.await();
                transferService.transfer(1L, 2L,
                    new BigDecimal("100.00"));
                return null;
            });
        }
        latch.countDown(); // Fire all at once
        pool.shutdown();
        pool.awaitTermination(10, TimeUnit.SECONDS);

        Account after = accountRepo.findById(1L).orElseThrow();
        // Expected: 1000 - (10 × 100) = 0
        // Actual: some random positive number (money was manufactured)
        assertNotEquals(BigDecimal.ZERO, after.getBalance());
    }
}
```

Test passes. The bug is real. Money is being manufactured out of thin air.

---

## Step 2: Understand Why

Two problems, two fixes needed:

1. **No atomicity** — the two `save()` calls are independent database transactions. A crash between them loses money.
2. **No isolation** — two threads read the same balance, both compute a new value, last writer wins.

---

## Step 3: The Fix — @Transactional + Pessimistic Locking

Linus reviews your fix at 3 AM. He has one demand:

> "Lock in ID order. Always. I don't care if it looks weird. If you lock Account 7 before Account 3, you *will* deadlock. We'll talk about that in [Chapter 5](05-the-deadlock-at-3am.md)."

```java
// src/main/java/com/payflow/service/TransferService.java
@Service
@RequiredArgsConstructor
public class TransferService {

    private final AccountRepository accountRepo;

    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // CRITICAL: Lock in ascending ID order to prevent deadlocks
        Long firstId = Math.min(fromId, toId);
        Long secondId = Math.max(fromId, toId);

        Account first = accountRepo.findByIdWithLock(firstId);
        Account second = accountRepo.findByIdWithLock(secondId);

        Account from = first.getId().equals(fromId) ? first : second;
        Account to = first.getId().equals(fromId) ? second : first;

        if (from.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException();
        }

        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));
        // No explicit save() — dirty checking handles it at commit
    }
}
```

The repository query that makes it work:

```java
// src/main/java/com/payflow/repository/AccountRepository.java
public interface AccountRepository extends JpaRepository<Account, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Account findByIdWithLock(@Param("id") Long id);
}
```

This generates `SELECT ... FOR UPDATE` in PostgreSQL. The row is locked until the transaction commits. No other thread can read-and-modify it simultaneously.

---

## Step 4: Test Goes Green

```java
// src/test/java/com/payflow/service/TransferFixedTest.java
@SpringBootTest
class TransferFixedTest {

    @Autowired private TransferService transferService;
    @Autowired private AccountRepository accountRepo;

    @Test
    void concurrent_transfers_are_now_safe() throws Exception {
        accountRepo.save(new Account(1L, "Alice", new BigDecimal("1000.00")));
        accountRepo.save(new Account(2L, "Bob", new BigDecimal("0.00")));

        ExecutorService pool = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(1);

        for (int i = 0; i < 10; i++) {
            pool.submit(() -> {
                latch.await();
                transferService.transfer(1L, 2L,
                    new BigDecimal("100.00"));
                return null;
            });
        }
        latch.countDown();
        pool.shutdown();
        pool.awaitTermination(10, TimeUnit.SECONDS);

        Account alice = accountRepo.findById(1L).orElseThrow();
        Account bob = accountRepo.findById(2L).orElseThrow();

        // Exactly $1000 moved. No money created. No money lost.
        assertEquals(new BigDecimal("0.00"), alice.getBalance());
        assertEquals(new BigDecimal("1000.00"), bob.getBalance());
    }
}
```

✅ Green. You push the fix at 3:47 AM. Maya responds with a single emoji: 👍

---

## The Isolation Level Deep Dive

Priya pulls you aside the next morning. "You should understand what you just chose and why."

```
──────────────────────┬─────────────┬────────────────────┬──────────────┬─────────────
Isolation Level       │ Dirty Read  │ Non-Repeatable Read│ Phantom Read │ Performance
──────────────────────┼─────────────┼────────────────────┼──────────────┼─────────────
READ UNCOMMITTED      │ PG promotes │ to READ COMMITTED  │ automatically│ —
──────────────────────┼─────────────┼────────────────────┼──────────────┼─────────────
READ COMMITTED        │ ✅ Prevented│ ⚠️ Possible        │ ⚠️ Possible  │ Best
──────────────────────┼─────────────┼────────────────────┼──────────────┼─────────────
REPEATABLE READ       │ ✅ Prevented│ ✅ Prevented       │ ✅ Prevented │ Good
                      │             │                    │ (in PG!)     │
──────────────────────┼─────────────┼────────────────────┼──────────────┼─────────────
SERIALIZABLE          │ ✅ Prevented│ ✅ Prevented       │ ✅ Prevented │ Worst
──────────────────────┴─────────────┴────────────────────┴──────────────┴─────────────
```

"PostgreSQL's REPEATABLE READ is actually *snapshot isolation*," Priya explains. "It prevents phantoms too, unlike the SQL standard. That's a PostgreSQL superpower."

"So why didn't we use it?"

"Because for money transfers, READ_COMMITTED + explicit locking is better. Three reasons:"

1. **You control exactly which rows lock** — no surprises
2. **No snapshot tracking overhead** for every query in the transaction
3. **No serialization failures** — you never need to retry the whole transaction due to snapshot conflicts

"Explicit locking is more work to write," she says. "But it's predictable. And in fintech, predictable beats clever."

---

## What You Learned

You came in thinking `save()` was safe. Now you know:

- **`@Transactional` is not optional** — without it, each `save()` is its own transaction
- **Pessimistic locking** (`SELECT ... FOR UPDATE`) prevents concurrent modification
- **Lock ordering** (ascending ID) prevents deadlocks — more on this in [Chapter 5](05-the-deadlock-at-3am.md)
- **Dirty checking** means you don't need explicit `save()` inside a transaction

You also learned that 2 AM Slack messages are a way of life in fintech.

---

[← The Genesis](01-the-genesis.md) | [Next: The N+1 Apocalypse →](03-the-n-plus-1-apocalypse.md)
