# Chapter 3: The N+1 Apocalypse — "Why Is the Dashboard Taking 30 Seconds?"

[← The Dirty Read Incident](02-the-dirty-read-incident.md) | [Next: The Million TPS Challenge →](04-the-million-tps-challenge.md)

---

Three weeks in. You've survived the $50k incident. You're feeling confident. Then Maya messages the engineering channel:

> The dashboard takes 30 seconds to load. Our biggest client is threatening to leave. Fix it by Friday or we lose the account.

Linus looks at you. "The dashboard code is yours, right?"

It is. You wrote it last Tuesday. It was so clean. So readable.

---

## The Disaster

You pull up the dashboard service:

```java
// src/main/java/com/payflow/service/DashboardService.java
// ⚠️ BUG: This is the N+1 query problem. You just don't know it yet.
public List<AccountDashboardDTO> getDashboard() {
    List<Account> accounts = accountRepo.findAll(); // 1 query
    List<AccountDashboardDTO> result = new ArrayList<>();

    for (Account a : accounts) {
        List<Transaction> txns = txnRepo
            .findTop10ByFromAccountIdOrderByCreatedAtDesc(
                a.getId()); // ⚠️ 1 query PER account
        result.add(new AccountDashboardDTO(a, txns));
    }
    return result;
}
```

One query to load all accounts. Then one query *per account* to load transactions.

PayFlow now has 100,000 accounts.

That's **100,001 queries**. For one page load.

Priya walks over, looks at your screen, and says one word: "N+1."

---

## Step 1: Write a Test That Counts Queries

Before you fix it, prove how bad it is:

```java
// src/test/java/com/payflow/service/DashboardQueryCountTest.java
@SpringBootTest
class DashboardQueryCountTest {

    @Autowired private DashboardService dashboardService;
    @PersistenceContext private EntityManager em;

    @Test
    void dashboard_fires_too_many_queries() {
        // Setup: 100 accounts, 10 txns each
        createTestData(100);

        Statistics stats = em.unwrap(Session.class)
            .getSessionFactory().getStatistics();
        stats.setStatisticsEnabled(true);
        stats.clear();

        dashboardService.getDashboard();

        long queryCount = stats.getQueryExecutionCount();
        // Expected: 2 (one for accounts, one for transactions)
        // Actual: 101 (1 + 100)
        System.out.println("Queries executed: " + queryCount);
        assertTrue(queryCount > 100,
            "N+1 confirmed: " + queryCount + " queries");
    }
}
```

Output: `Queries executed: 101`. For just 100 accounts. In production, that's 100,001.

---

## Step 2: Understand Why

Your instinct might be: "Just add `FetchType.EAGER` to the relationship!"

**Don't.** That's trading one disaster for another. Eager fetching loads transactions for *every* account query in your entire application, even when you don't need them.

The real problem is simpler: you're making one query per account when you could make one query for *all* accounts' transactions.

---

## Step 3: Fix — Batch Fetch Query

Replace the loop with a single query:

```java
// src/main/java/com/payflow/repository/TransactionRepository.java
public interface TransactionRepository
        extends JpaRepository<Transaction, Long> {

    @Query("""
        SELECT t FROM Transaction t
        WHERE t.fromAccountId IN :accountIds
        AND t.createdAt >= :since
        ORDER BY t.fromAccountId, t.createdAt DESC
        """)
    List<Transaction> findRecentByAccounts(
        @Param("accountIds") List<Long> accountIds,
        @Param("since") Instant since);
}
```

---

## Step 4: Fix — Interface Projections

You don't need full `Account` entities for a dashboard. You need three fields. Loading full entities means Hibernate tracks every field for dirty checking — wasted CPU and memory.

```java
// src/main/java/com/payflow/projection/AccountSummary.java
// ✅ JPA generates SELECT with only these columns
public interface AccountSummary {
    Long getId();
    String getOwnerName();
    BigDecimal getBalance();
}
```

```java
// src/main/java/com/payflow/repository/AccountRepository.java
public interface AccountRepository extends JpaRepository<Account, Long> {

    List<AccountSummary> findAllProjectedBy();

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Account findByIdWithLock(@Param("id") Long id);
}
```

---

## Step 5: The Fixed Dashboard Service

```java
// src/main/java/com/payflow/service/DashboardService.java
@Service
@RequiredArgsConstructor
public class DashboardService {

    private final AccountRepository accountRepo;
    private final TransactionRepository txnRepo;

    @Transactional(readOnly = true)
    public List<AccountDashboardDTO> getDashboard() {
        List<AccountSummary> accounts =
            accountRepo.findAllProjectedBy();       // Query 1

        List<Long> ids = accounts.stream()
            .map(AccountSummary::getId).toList();

        List<Transaction> txns =
            txnRepo.findRecentByAccounts(
                ids, Instant.now().minus(30, DAYS)); // Query 2

        Map<Long, List<Transaction>> txnsByAccount =
            txns.stream().collect(
                groupingBy(Transaction::getFromAccountId));

        return accounts.stream()
            .map(a -> new AccountDashboardDTO(
                a, txnsByAccount.getOrDefault(
                    a.getId(), List.of())))
            .toList();
    }
}
```

Two queries. That's it. Down from 100,001.

---

## Step 6: Test Goes Green

```java
// src/test/java/com/payflow/service/DashboardFixedTest.java
@SpringBootTest
class DashboardFixedTest {

    @Autowired private DashboardService dashboardService;
    @PersistenceContext private EntityManager em;

    @Test
    void dashboard_now_uses_only_two_queries() {
        createTestData(100);

        Statistics stats = em.unwrap(Session.class)
            .getSessionFactory().getStatistics();
        stats.setStatisticsEnabled(true);
        stats.clear();

        dashboardService.getDashboard();

        long queryCount = stats.getQueryExecutionCount();
        System.out.println("Queries executed: " + queryCount);
        assertTrue(queryCount <= 2,
            "Fixed! Only " + queryCount + " queries");
    }
}
```

Output: `Queries executed: 2`. ✅

The dashboard loads in 200ms. Maya sends a thumbs up. The client stays.

---

## Priya's Rule

She catches you at the coffee machine:

> "If you're not going to *modify* the entity, don't load the entity. Projections skip dirty checking, skip the persistence context, and use less memory. Make it a habit."

You nod. You write it on a sticky note. You put it on your monitor.

> *The dashboard is fast now. But we're still only doing 2,000 TPS. In [Chapter 4](04-the-million-tps-challenge.md), Maya announces the acquisition — and the number she needs will make you choke on your coffee.*

---

[← The Dirty Read Incident](02-the-dirty-read-incident.md) | [Next: The Million TPS Challenge →](04-the-million-tps-challenge.md)
