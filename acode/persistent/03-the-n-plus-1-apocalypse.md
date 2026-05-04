# Chapter 3: The N+1 Apocalypse — "Why Is the Dashboard Taking 30 Seconds?"

[← The Dirty Read Incident](02-the-dirty-read-incident.md) | [Next: The Million TPS Challenge →](04-the-million-tps-challenge.md)

---

Product wants a dashboard: show all accounts with their last 10 transactions. Your dev writes:

## The Disaster

```java
// ❌ THE DISASTER
List<Account> accounts = accountRepo.findAll(); // 1 query
for (Account a : accounts) {
    List<Transaction> txns = txnRepo
        .findTop10ByFromAccountIdOrderByCreatedAtDesc(a.getId());
    // ↑ 1 query PER account. 100,000 accounts = 100,001 queries.
}
```

**The fix isn't `@ManyToOne(fetch = FetchType.EAGER)`**. That's trading one disaster for another.

## Fix 1: Single Query with Batch Fetch

```java
public interface TransactionRepository extends JpaRepository<Transaction, Long> {

    @Query("""
        SELECT t FROM Transaction t
        WHERE t.fromAccountId IN :accountIds
        AND t.createdAt >= :since
        ORDER BY t.fromAccountId, t.createdAt DESC
        """)
    List<Transaction> findRecentByAccounts(
        @Param("accountIds") List<Long> accountIds,
        @Param("since") Instant since
    );
}
```

## Fix 2: Interface-Based Projections

Don't hydrate full entities when you only need 3 fields:

```java
// ✅ JPA generates SELECT with only these columns
public interface AccountSummary {
    Long getId();
    String getOwnerName();
    BigDecimal getBalance();
}
```

```java
public interface AccountRepository extends JpaRepository<Account, Long> {
    List<AccountSummary> findAllProjectedBy();
}
```

**Senior rule**: If you're not going to *modify* the entity, don't load the entity. Projections skip dirty checking, skip the persistence context cache overhead, and use less memory.

---

[← The Dirty Read Incident](02-the-dirty-read-incident.md) | [Next: The Million TPS Challenge →](04-the-million-tps-challenge.md)
