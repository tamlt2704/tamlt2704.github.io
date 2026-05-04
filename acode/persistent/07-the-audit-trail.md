# Chapter 7: The Audit Trail — "The Regulators Are Coming"

[← The Read Replica Strategy](06-the-read-replica-strategy.md) | [Next: The Production Checklist →](08-the-production-checklist.md)

---

Monday morning. An email from the compliance team lands in the engineering channel. Linus reads it out loud:

> "Financial regulators are conducting an audit next quarter. Every balance change must be traceable to a specific transaction, user, and timestamp. Non-compliance means we lose our banking license."

The room goes quiet.

Maya looks at Linus. "How long?"

Linus looks at you. "Two weeks. We need a ledger."

---

## The Problem

Right now, your `accounts` table has a `balance` field. When a transfer happens, you update it in place. The old value is gone. If a regulator asks "why did this account go from $10,000 to $9,500 at 3:47 PM on March 12th?" — you can't answer.

You have the `transactions` table, but it records *transfers*, not *balance changes*. A single transfer creates two balance changes (one debit, one credit). You need to track each one independently.

---

## Step 1: The Ledger Entity

Linus sketches it on the whiteboard:

> "Every balance change gets a row. The account balance is just the sum of all ledger entries. If they ever disagree, the ledger is the source of truth."

```java
// src/main/java/com/payflow/entity/LedgerEntry.java
@Entity
@Table(name = "account_ledger")
public class LedgerEntry {
    @Id
    @GeneratedValue(
        strategy = GenerationType.SEQUENCE,
        generator = "ledger_seq")
    @SequenceGenerator(
        name = "ledger_seq",
        sequenceName = "ledger_id_seq",
        allocationSize = 100)
    private Long id;

    private Long accountId;
    private Long transactionId;
    private BigDecimal amount;       // Signed: + credit, - debit
    private BigDecimal balanceAfter; // Denormalized for fast lookups
    private Instant createdAt;
}
```

`allocationSize = 100` because every transfer creates two ledger entries. At high volume, you need IDs fast.

---

## Step 2: Record Ledger Entries on Every Transfer

Update the transfer service to write ledger entries:

```java
// src/main/java/com/payflow/service/TransferService.java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void transfer(Long fromId, Long toId, BigDecimal amount) {
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

    Transaction txn = txnRepo.save(new Transaction(
        null, fromId, toId, amount,
        TxnStatus.COMPLETED, Instant.now()));

    ledgerRepo.save(new LedgerEntry(null, fromId, txn.getId(),
        amount.negate(), from.getBalance(), Instant.now()));
    ledgerRepo.save(new LedgerEntry(null, toId, txn.getId(),
        amount, to.getBalance(), Instant.now()));
}
```

Everything — the balance update, the transaction record, and both ledger entries — happens in one `@Transactional` boundary. All or nothing.

---

## Step 3: The Reconciliation Query

Priya insists on a nightly reconciliation job. "Trust but verify. If the account balance ever disagrees with the ledger sum, we have a bug."

```sql
-- src/main/resources/db/queries/reconciliation.sql
SELECT
    a.id AS account_id,
    a.balance AS current_balance,
    COALESCE(SUM(l.amount), 0) AS ledger_balance,
    a.balance - COALESCE(SUM(l.amount), 0) AS discrepancy
FROM accounts a
LEFT JOIN account_ledger l ON a.id = l.account_id
GROUP BY a.id, a.balance
HAVING a.balance != COALESCE(SUM(l.amount), 0);
```

If this query returns any rows, something is very wrong. Wire it to PagerDuty.

```java
// src/main/java/com/payflow/repository/LedgerRepository.java
public interface LedgerRepository
        extends JpaRepository<LedgerEntry, Long> {

    @Query("""
        SELECT l.accountId AS accountId,
               SUM(l.amount) AS ledgerBalance
        FROM LedgerEntry l
        GROUP BY l.accountId
        """)
    List<LedgerSummary> getBalancesByAccount();
}
```

```java
// src/main/java/com/payflow/projection/LedgerSummary.java
public interface LedgerSummary {
    Long getAccountId();
    BigDecimal getLedgerBalance();
}
```

---

## Step 4: JPA Auditing for Entity Metadata

The regulators also want to know *who* changed *what* and *when*. JPA has built-in support:

```java
// src/main/java/com/payflow/entity/Account.java
@Entity
@Table(name = "accounts")
@EntityListeners(AuditingEntityListener.class)
public class Account {
    @Id
    private Long id;
    private String ownerName;
    private BigDecimal balance;
    @Version
    private Long version;

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

Enable auditing and tell Spring how to get the current user:

```java
// src/main/java/com/payflow/config/AuditConfig.java
@Configuration
@EnableJpaAuditing
public class AuditConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(
            SecurityContextHolder.getContext()
                .getAuthentication())
            .map(Authentication::getName);
    }
}
```

Now every `Account` automatically tracks who created it, who last modified it, and when.

---

## Step 5: Test the Ledger

```java
// src/test/java/com/payflow/service/LedgerTest.java
@SpringBootTest
class LedgerTest {

    @Autowired private TransferService transferService;
    @Autowired private AccountRepository accountRepo;
    @Autowired private LedgerRepository ledgerRepo;

    @Test
    void transfer_creates_matching_ledger_entries() {
        accountRepo.save(new Account(1L, "Alice", new BigDecimal("1000")));
        accountRepo.save(new Account(2L, "Bob", new BigDecimal("500")));

        transferService.transfer(1L, 2L, new BigDecimal("200.00"));

        List<LedgerSummary> summaries = ledgerRepo.getBalancesByAccount();
        Map<Long, BigDecimal> balances = summaries.stream()
            .collect(toMap(
                LedgerSummary::getAccountId,
                LedgerSummary::getLedgerBalance));

        // Ledger sum matches account balance
        Account alice = accountRepo.findById(1L).orElseThrow();
        Account bob = accountRepo.findById(2L).orElseThrow();

        assertEquals(alice.getBalance(), balances.get(1L));
        assertEquals(bob.getBalance(), balances.get(2L));
    }
}
```

✅ Green. The ledger matches the balances. The regulators will be satisfied.

---

## Linus's Summary

He writes on the whiteboard before leaving:

> "The `accounts.balance` is a **materialized view** of the ledger. The ledger is the source of truth. If they disagree, the ledger wins. This is event sourcing lite — and it's how every real bank works."

> *The audit trail is in place. The system is fast, safe, and compliant. But you're not done yet. Linus has one final review before your promotion. [Chapter 8](08-the-production-checklist.md).*

---

[← The Read Replica Strategy](06-the-read-replica-strategy.md) | [Next: The Production Checklist →](08-the-production-checklist.md)
