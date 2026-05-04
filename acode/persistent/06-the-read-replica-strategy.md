# Chapter 6: The Read Replica Strategy — "Reads Are Killing Writes"

[← The Deadlock at 3 AM](05-the-deadlock-at-3am.md) | [Next: The Audit Trail →](07-the-audit-trail.md)

---

Your dashboard queries are competing with transfers for database connections. Solution: **read replicas**.

## Routing DataSource

```java
public class ReadWriteRoutingDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
            ? "replica"
            : "primary";
    }
}
```

This routes queries based on the `@Transactional` annotation's `readOnly` flag.

## Using It in Services

```java
// Dashboard queries automatically route to replica
@Transactional(readOnly = true)
public List<AccountSummary> getDashboard() {
    return accountRepo.findAllProjectedBy();
}
```

## What `readOnly = true` Actually Does

It triggers **three** optimizations:

1. **Routes to read replica** (with the routing datasource above)
2. **Tells Hibernate to skip dirty checking** (performance boost)
3. **Sets PostgreSQL transaction to read-only mode** (allows query optimizations)

Always use it for read-only service methods — even without replicas, you still get benefits #2 and #3.

---

[← The Deadlock at 3 AM](05-the-deadlock-at-3am.md) | [Next: The Audit Trail →](07-the-audit-trail.md)
