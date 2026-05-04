# Chapter 5: The Deadlock at 3 AM — "PagerDuty Won't Stop"

[← The Million TPS Challenge](04-the-million-tps-challenge.md) | [Next: The Read Replica Strategy →](06-the-read-replica-strategy.md)

---

Production. 3 AM. Deadlock alerts firing every second.

```
ERROR: deadlock detected
Detail: Process 12345 waits for ShareLock on transaction 67890;
        blocked by process 67891.
        Process 67891 waits for ShareLock on transaction 67892;
        blocked by process 12345.
```

## Root Cause

Two concurrent transfers:
- **Thread A**: Transfer from Account 1 → Account 2 (locks 1, then tries to lock 2)
- **Thread B**: Transfer from Account 2 → Account 1 (locks 2, then tries to lock 1)

**This is why [Chapter 2](02-the-dirty-read-incident.md) locks in ID order.**

## The Subtler Deadlock: Mixing Lock Strategies

```java
// ❌ Optimistic + Pessimistic mixing causes chaos
@Transactional
public void riskyTransfer(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepo.findById(fromId).orElseThrow(); // No lock, loads version=5
    Account to = accountRepo.findByIdWithLock(toId);           // Pessimistic lock

    from.setBalance(from.getBalance().subtract(amount));
    // At flush: UPDATE ... WHERE id=? AND version=5
    // Another thread changed version to 6 → OptimisticLockException
    // But 'to' is still pessimistic-locked → other threads waiting → cascade failure
}
```

**Rule**: Pick one locking strategy per operation. For money: pessimistic. For low-contention reads: optimistic.

## Retry Pattern for Optimistic Locking

When you do use optimistic locking (low-contention scenarios), add retries:

```java
@Retryable(
    retryFor = OptimisticLockingFailureException.class,
    maxAttempts = 3,
    backoff = @Backoff(delay = 50, multiplier = 2, random = true)
)
@Transactional
public void optimisticTransfer(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepo.findById(fromId).orElseThrow();
    Account to = accountRepo.findById(toId).orElseThrow();

    if (from.getBalance().compareTo(amount) < 0) {
        throw new InsufficientFundsException();
    }

    from.setBalance(from.getBalance().subtract(amount));
    to.setBalance(to.getBalance().add(amount));
    // If version conflict → Spring retries with fresh data
}
```

Key details:
- `random = true` adds jitter to prevent retry storms
- `@Transactional` must be on the same method — Spring creates a **new** transaction on each retry
- Enable with `@EnableRetry` on your configuration class

---

[← The Million TPS Challenge](04-the-million-tps-challenge.md) | [Next: The Read Replica Strategy →](06-the-read-replica-strategy.md)
