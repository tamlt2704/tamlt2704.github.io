# Chapter 7: The Audit Trail — "The Regulators Are Coming"

[← The Read Replica Strategy](06-the-read-replica-strategy.md) | [Next: The Production Checklist →](08-the-production-checklist.md)

---

Financial regulations require a complete audit trail. Every balance change must be traceable.

## The Ledger Entity

```java
@Entity
@Table(name = "account_ledger")
public class LedgerEntry {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "ledger_seq")
    @SequenceGenerator(name = "ledger_seq", sequenceName = "ledger_id_seq", allocationSize = 100)
    private Long id;

    private Long accountId;
    private Long transactionId;
    private BigDecimal amount;       // Signed: positive = credit, negative = debit
    private BigDecimal balanceAfter; // Denormalized for fast lookups
    private Instant createdAt;
}
```

**Architectural pattern**: Event sourcing lite. The `accounts.balance` is a *materialized view* of the ledger. If they ever disagree, the ledger is the source of truth.

## Reconstructing Balances from the Ledger

```sql
SELECT account_id, SUM(amount) as reconstructed_balance
FROM account_ledger
GROUP BY account_id;
```

Run this as a nightly reconciliation job. Any mismatch triggers an alert.

## JPA Auditing for Entity Metadata

```java
@Entity
@Table(name = "accounts")
@EntityListeners(AuditingEntityListener.class)
public class Account {
    // ... existing fields ...

    @CreatedDate
    private Instant createdAt;
    @LastModifiedDate
    private Instant updatedAt;
    @CreatedBy
    private String createdBy;
    @LastModifiedBy
    private String updatedBy;
}
```

Enable with `@EnableJpaAuditing` on your configuration class and provide an `AuditorAware<String>` bean that returns the current user.

---

[← The Read Replica Strategy](06-the-read-replica-strategy.md) | [Next: The Production Checklist →](08-the-production-checklist.md)
