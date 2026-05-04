# Chapter 1: The Genesis — "We Just Need a Simple Payment Service"

[← Overview](00-overview.md) | [Next: The Dirty Read Incident →](02-the-dirty-read-incident.md)

---

You start simple. Two entities: accounts and transactions.

## The Account Entity

```java
@Entity
@Table(name = "accounts")
public class Account {
    @Id
    private Long id;
    private String ownerName;
    private BigDecimal balance;

    @Version // Optimistic locking — remember this. It saves your life later.
    private Long version;
}
```

**Architectural decision**: `BigDecimal`, never `double`. You lose $0.000001 per transaction with floating point. At a million TPS, that's **$86/day** vanishing into the void.

## The Transaction Entity

```java
@Entity
@Table(name = "transactions")
public class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "txn_seq")
    @SequenceGenerator(name = "txn_seq", sequenceName = "txn_id_seq", allocationSize = 50)
    private Long id;

    private Long fromAccountId;
    private Long toAccountId;
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    private TxnStatus status; // PENDING, COMPLETED, FAILED

    private Instant createdAt;
}
```

**Architectural decision**: `allocationSize = 50`. JPA fetches 50 sequence values at once from PostgreSQL. At millions of inserts, you *cannot* afford a round-trip per ID.

## Why These Choices Matter

| Decision | Wrong Choice | Right Choice | Why |
|---|---|---|---|
| Money type | `double` / `float` | `BigDecimal` + `NUMERIC(19,4)` | Floating point loses precision |
| ID strategy | `GenerationType.IDENTITY` | `SEQUENCE` with `allocationSize=50+` | IDENTITY disables batch inserts |
| Concurrency | No `@Version` | `@Version` field | Detects concurrent modifications |

---

[← Overview](00-overview.md) | [Next: The Dirty Read Incident →](02-the-dirty-read-incident.md)
