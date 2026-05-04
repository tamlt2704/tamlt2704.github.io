# Chapter 2: The Dirty Read Incident — "Where Did $50,000 Go?"

[← The Genesis](01-the-genesis.md) | [Next: The N+1 Apocalypse →](03-the-n-plus-1-apocalypse.md)

---

Week two. A customer reports a phantom balance. Your junior dev wrote this:

## The Bug

```java
// ❌ THE BUG
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepo.findById(fromId).orElseThrow();
    Account to = accountRepo.findById(toId).orElseThrow();

    from.setBalance(from.getBalance().subtract(amount));
    to.setBalance(to.getBalance().add(amount));

    accountRepo.save(from);
    // 💥 Server crashes here. 'from' debited, 'to' never credited.
    accountRepo.save(to);
}
```

**Problem 1: No transaction boundary.** Each `save()` auto-commits. Crash between them = lost money.

**Problem 2: Race condition.** Two threads read balance=1000 simultaneously, both subtract 800, both save balance=200. You just manufactured $600.

## The Fix — Pessimistic Locking with Ordered Acquisition

```java
@Service
public class TransferService {

    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // CRITICAL: Always lock in consistent order to prevent deadlocks
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
        // No explicit save needed — dirty checking handles it at commit
    }
}
```

## The Repository Lock Query

```java
public interface AccountRepository extends JpaRepository<Account, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Account findByIdWithLock(@Param("id") Long id);
}
```

This generates `SELECT ... FOR UPDATE` in PostgreSQL — the row is locked until the transaction commits.

## The Isolation Level Deep Dive

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Performance |
|---|---|---|---|---|
| READ UNCOMMITTED | PG promotes to READ COMMITTED | — | — | — |
| **READ COMMITTED** | ✅ Prevented | ⚠️ Possible | ⚠️ Possible | **Best** |
| REPEATABLE READ | ✅ Prevented | ✅ Prevented | ✅ Prevented (in PG!) | Good |
| SERIALIZABLE | ✅ Prevented | ✅ Prevented | ✅ Prevented | Worst |

## Why READ_COMMITTED + Explicit Locking?

**Senior insight**: PostgreSQL's REPEATABLE READ is actually *snapshot isolation* — it prevents phantoms too, unlike the SQL standard. This is a PostgreSQL superpower.

But for money transfers, `READ_COMMITTED` + explicit locking is the right pattern because:

1. You control *exactly* which rows lock
2. You don't pay the cost of snapshot tracking for every query
3. Serialization failures (retries) don't happen

---

[← The Genesis](01-the-genesis.md) | [Next: The N+1 Apocalypse →](03-the-n-plus-1-apocalypse.md)
