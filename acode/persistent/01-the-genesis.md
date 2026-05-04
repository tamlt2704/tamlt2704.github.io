# Chapter 1: The Genesis — "We Just Need a Simple Payment Service"

[← Overview](00-overview.md) | [Next: The Dirty Read Incident →](02-the-dirty-read-incident.md)

---

Your first day. You've barely found the coffee machine when Linus walks over, drops into the chair next to you, and says:

> "We need a payment service. Accounts, transactions. Start simple. You know JPA, right?"

You nod. You took a database course in college. How hard can it be?

Linus grins. "Ship it by end of day."

---

## Your First Entity: Account

You open IntelliJ, crack your knuckles, and write:

```java
// src/main/java/com/payflow/entity/Account.java
@Entity
@Table(name = "accounts")
public class Account {
    @Id
    private Long id;

    private String ownerName;
    private BigDecimal balance;

    @Version // ⚠️ BUG: You add this because Stack Overflow said to.
    private Long version; // You don't fully understand what it does yet.
    // No @Transactional anywhere. This will matter. A lot.
}
```

Linus glances at your screen. "BigDecimal. Good. Never use `double` for money."

You ask why. He pulls up a REPL:

```java
// src/test/java/com/payflow/WhyNotDoubleTest.java
@Test
void doubles_lose_money() {
    double balance = 0.0;
    for (int i = 0; i < 1_000_000; i++) {
        balance += 0.01;
    }
    // Expected: 10000.00
    // Actual:   9999.999999999831
    assertNotEquals(10_000.00, balance);
}
```

At a million transactions per day, that's **$86 vanishing into floating-point hell**. Every. Single. Day.

---

## Your Second Entity: Transaction

```java
// src/main/java/com/payflow/entity/Transaction.java
@Entity
@Table(name = "transactions")
public class Transaction {
    @Id
    @GeneratedValue(
        strategy = GenerationType.SEQUENCE,
        generator = "txn_seq")
    @SequenceGenerator(
        name = "txn_seq",
        sequenceName = "txn_id_seq",
        allocationSize = 50)
    private Long id;

    private Long fromAccountId;
    private Long toAccountId;
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    private TxnStatus status; // PENDING, COMPLETED, FAILED

    private Instant createdAt;
}
```

Linus nods at `allocationSize = 50`. "Good instinct. JPA grabs 50 IDs at once from PostgreSQL. At high volume, you can't afford a database round-trip per insert."

You ask: "What about `GenerationType.IDENTITY`?"

He shakes his head. "IDENTITY disables batch inserts entirely. Hibernate needs the ID back immediately after each INSERT. You'll understand why that matters in Chapter 4."

---

## The Smoke Test

You write a quick test to make sure everything compiles and persists:

```java
// src/test/java/com/payflow/entity/AccountSmokeTest.java
@SpringBootTest
@Transactional // ⚠️ This @Transactional is on the TEST, not the service.
class AccountSmokeTest {

    @Autowired
    private AccountRepository accountRepo;

    @Test
    void can_create_and_find_account() {
        Account a = new Account();
        a.setId(1L);
        a.setOwnerName("Alice");
        a.setBalance(new BigDecimal("1000.00"));

        accountRepo.save(a);

        Account found = accountRepo.findById(1L).orElseThrow();
        assertEquals("Alice", found.getOwnerName());
    }
}
```

Green. You push to `main`. Linus approves the PR in four minutes.

---

## The Decision Table

You feel good. You made smart choices. Here's what you got right:

```
────────────────┬──────────────────────┬──────────────────────────────
Decision        │ Wrong Choice         │ Your Choice
────────────────┼──────────────────────┼──────────────────────────────
Money type      │ double / float       │ BigDecimal + NUMERIC(19,4)
────────────────┼──────────────────────┼──────────────────────────────
ID strategy     │ GenerationType.      │ SEQUENCE with
                │ IDENTITY             │ allocationSize=50
────────────────┼──────────────────────┼──────────────────────────────
Concurrency     │ No @Version          │ @Version field
────────────────┴──────────────────────┴──────────────────────────────
```

---

## The Foreshadow

You go home feeling like a real engineer. Your entities compile. Your tests pass. Your PR is merged.

But here's what you don't know yet:

Your service code has **no `@Transactional` boundaries**. Each `save()` call auto-commits independently. Right now, with one user running smoke tests, that's fine.

But in two weeks, when PayFlow has 10,000 concurrent users and someone transfers $50,000 between two accounts — and the server crashes *between* the two `save()` calls...

That money will vanish. And Maya will Slack you at 2 AM.

> *This code has bugs. We'll discover them in [Chapter 2](02-the-dirty-read-incident.md).*

---

[← Overview](00-overview.md) | [Next: The Dirty Read Incident →](02-the-dirty-read-incident.md)
