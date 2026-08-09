# Chapter 74: JPA Deep Dive — Build a Transactional Order System

## What you'll learn

- JPA entity lifecycle (transient, managed, detached, removed)
- Relationships: OneToMany, ManyToOne, ManyToMany (with fetch strategies)
- Transactions: ACID, isolation levels, dirty reads, phantom reads
- Optimistic locking (@Version) vs Pessimistic locking (SELECT FOR UPDATE)
- N+1 problem and how to fix it (JOIN FETCH, EntityGraph, batch fetching)
- Build: a concurrent order system that handles race conditions correctly

---

## PART 1: Entity Lifecycle

## 74.1 The 4 states

```
┌──────────┐     persist()      ┌──────────┐
│TRANSIENT │ ──────────────────► │ MANAGED  │
│(new, no  │                     │(tracked  │
│ DB row)  │                     │ by EM)   │
└──────────┘                     └─────┬────┘
                                       │
      merge()     ┌──────────┐         │ detach() / close() / clear()
  ┌──────────────►│ MANAGED  │◄────────┘
  │               └──────────┘         │
  │                                    ▼
  │               ┌──────────┐    ┌──────────┐
  └───────────────│ DETACHED │    │ DETACHED │
                  │(was managed,   │(session   │
                  │ now disconnected)│ closed)  │
                  └──────────┘    └──────────┘
                                       │
                                       │ merge() → becomes managed again
                                       │ remove() → scheduled for deletion
                                       ▼
                                  ┌──────────┐
                                  │ REMOVED  │
                                  │(will be  │
                                  │ deleted) │
                                  └──────────┘
```

**MANAGED** is the key state:
- JPA tracks ALL changes to managed entities automatically
- When the transaction commits → all changes are flushed to DB (no explicit save needed!)
- This is called **"dirty checking"** — JPA compares current state vs snapshot at load time

```java
@Transactional
public void updatePrice(Long productId, BigDecimal newPrice) {
    Product product = entityManager.find(Product.class, productId); // MANAGED
    product.setPrice(newPrice);  // JPA detects this change automatically
    // NO save() call needed! Flush happens at commit.
}
```

---

## PART 2: Entities & Relationships

## 74.2 Entity design

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private Integer stock;

    @Version  // ← OPTIMISTIC LOCKING (explained in Part 4)
    private Long version;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    @OneToMany(mappedBy = "product", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Review> reviews = new ArrayList<>();

    @CreationTimestamp
    private Instant createdAt;

    @UpdateTimestamp
    private Instant updatedAt;
}

@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private OrderStatus status = OrderStatus.PENDING;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal total = BigDecimal.ZERO;

    @Version
    private Long version;

    @CreationTimestamp
    private Instant createdAt;

    // Business method
    public void addItem(Product product, int quantity) {
        OrderItem item = new OrderItem(this, product, quantity, product.getPrice());
        items.add(item);
        recalculateTotal();
    }

    private void recalculateTotal() {
        this.total = items.stream()
            .map(i -> i.getUnitPrice().multiply(BigDecimal.valueOf(i.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}

@Entity
@Table(name = "order_items")
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal unitPrice;  // price at time of purchase (snapshot)
}
```

## 74.3 Fetch strategies (LAZY vs EAGER)

```java
// LAZY (default for collections — load only when accessed):
@OneToMany(fetch = FetchType.LAZY)
private List<OrderItem> items;
// items NOT loaded from DB until you call order.getItems()

// EAGER (load immediately with parent):
@ManyToOne(fetch = FetchType.EAGER)
private User user;
// user IS loaded with every Order query (even if you don't need it)

// RULE:
// @ManyToOne  → default is EAGER  (change to LAZY!)
// @OneToMany  → default is LAZY   (good — keep it)
// @ManyToMany → default is LAZY   (good — keep it)

// ALWAYS USE LAZY. Fetch eagerly only when you KNOW you need it.
// Use JOIN FETCH in queries when you actually need the data (see Part 5).
```

---

## PART 3: Transactions & Isolation Levels

## 74.4 Transaction problems (what goes wrong without proper isolation)

```
PROBLEM 1: DIRTY READ
  Transaction A writes data (uncommitted)
  Transaction B reads that uncommitted data
  Transaction A ROLLS BACK
  → Transaction B used data that NEVER EXISTED

  Timeline:
    T1: UPDATE product SET stock = 0       (not committed yet)
    T2: SELECT stock FROM product → 0      (reads uncommitted change!)
    T1: ROLLBACK                            (stock is actually still 10)
    T2: "Sorry, out of stock!" (WRONG — stock is 10!)

PROBLEM 2: NON-REPEATABLE READ
  Transaction reads a row
  Another transaction updates that row and commits
  First transaction reads again → DIFFERENT value!

  Timeline:
    T1: SELECT price → $10.00
    T2: UPDATE price = $15.00; COMMIT
    T1: SELECT price → $15.00  (different from first read!)
    T1: "Wait, the price changed mid-transaction?!"

PROBLEM 3: PHANTOM READ
  Transaction reads rows matching a condition
  Another transaction inserts new rows matching that condition
  First transaction reads again → MORE rows appear!

  Timeline:
    T1: SELECT * WHERE status = 'ACTIVE' → 5 rows
    T2: INSERT new row WHERE status = 'ACTIVE'; COMMIT
    T1: SELECT * WHERE status = 'ACTIVE' → 6 rows (phantom!)
```

## 74.5 Isolation levels

| Level | Dirty Read | Non-Repeatable | Phantom | Performance |
|-------|-----------|----------------|---------|-------------|
| READ_UNCOMMITTED | ❌ Possible | ❌ Possible | ❌ Possible | Fastest |
| **READ_COMMITTED** | ✅ Prevented | ❌ Possible | ❌ Possible | **Default (PostgreSQL)** |
| REPEATABLE_READ | ✅ Prevented | ✅ Prevented | ❌ Possible | Slower |
| SERIALIZABLE | ✅ Prevented | ✅ Prevented | ✅ Prevented | Slowest |

```java
// Spring: set isolation per transaction
@Transactional(isolation = Isolation.READ_COMMITTED)  // default
public void processOrder() { ... }

@Transactional(isolation = Isolation.REPEATABLE_READ)  // for financial
public void transferFunds() { ... }

@Transactional(isolation = Isolation.SERIALIZABLE)     // strictest (rare)
public void auditReconciliation() { ... }
```

**Rule of thumb:**
- `READ_COMMITTED` for 95% of operations (default — good enough)
- `REPEATABLE_READ` for financial transactions (reads must be consistent)
- `SERIALIZABLE` almost never (too slow, causes deadlocks)
- Use **optimistic/pessimistic locking** instead of higher isolation for concurrency control

---

## PART 4: Locking — Handling Concurrent Access

## 74.6 The race condition problem

```
TWO USERS BUY THE LAST ITEM SIMULTANEOUSLY:

  Stock = 1 (only 1 item left)

  User A:                          User B:
  1. Read stock → 1 (available!)   1. Read stock → 1 (available!)
  2. stock = stock - 1 = 0         2. stock = stock - 1 = 0
  3. SAVE (stock = 0)              3. SAVE (stock = 0)
  
  RESULT: Both users "bought" the item. Stock = 0. But TWO orders placed!
  REALITY: Only 1 item existed. Someone doesn't get their order.

  This is called a "lost update" — both read stale data, both overwrite.
```

## 74.7 Optimistic locking (@Version)

**Assumes conflicts are RARE.** Reads freely, checks at WRITE time.

```java
@Entity
public class Product {
    @Id
    private Long id;
    private Integer stock;
    
    @Version  // JPA auto-manages this field
    private Long version;  // starts at 0, incremented on every update
}
```

**How it works:**
```sql
-- When JPA updates, it includes the version in the WHERE clause:
UPDATE products SET stock = 0, version = 6
WHERE id = 42 AND version = 5;

-- If another transaction already changed it (version is now 6, not 5):
-- 0 rows updated → JPA throws OptimisticLockException!
```

```java
@Service
public class OrderService {
    
    @Transactional
    public void purchaseProduct(Long productId, int quantity) {
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new NotFoundException("Product not found"));
        
        if (product.getStock() < quantity) {
            throw new InsufficientStockException("Not enough stock");
        }
        
        product.setStock(product.getStock() - quantity);
        productRepository.save(product);
        // If another transaction modified this product between our read and write:
        // → OptimisticLockException thrown automatically!
    }
}

// Handle the exception (retry or fail gracefully):
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(OptimisticLockException.class)
    public ResponseEntity<?> handleOptimisticLock(OptimisticLockException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
            .body(new ErrorResponse("CONFLICT", "Item was modified by another user. Please retry."));
    }
}

// Retry pattern:
@Retryable(value = OptimisticLockException.class, maxAttempts = 3, backoff = @Backoff(100))
@Transactional
public void purchaseWithRetry(Long productId, int quantity) {
    // Same logic — retries automatically on conflict
}
```

**When to use:** Most situations. Low contention (conflicts are rare). Better throughput than pessimistic.

## 74.8 Pessimistic locking (SELECT FOR UPDATE)

**Assumes conflicts are LIKELY.** Locks the row IMMEDIATELY on read.

```java
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    // Lock the row when reading — other transactions WAIT until this one commits
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdWithLock(@Param("id") Long id);
}

@Service
public class OrderService {
    
    @Transactional
    public void purchaseProduct(Long productId, int quantity) {
        // This SELECT locks the row — other transactions block here until we commit
        Product product = productRepository.findByIdWithLock(productId)
            .orElseThrow(() -> new NotFoundException("Product not found"));
        
        if (product.getStock() < quantity) {
            throw new InsufficientStockException("Not enough stock");
        }
        
        product.setStock(product.getStock() - quantity);
        // Lock released when transaction commits — other transactions can now proceed
    }
}
```

**Generated SQL:**
```sql
SELECT * FROM products WHERE id = 42 FOR UPDATE;
-- Other transactions trying to read this row with FOR UPDATE will WAIT
```

**When to use:** High contention (many concurrent writes to same row). Financial systems. Inventory decrement.

## 74.9 Comparison

| | Optimistic (@Version) | Pessimistic (FOR UPDATE) |
|---|---|---|
| Assumption | Conflicts are rare | Conflicts are common |
| Lock timing | At write time (check version) | At read time (lock row) |
| Conflict handling | Exception → retry | Block → wait |
| Throughput | Higher (no blocking) | Lower (threads wait) |
| Deadlock risk | None | Possible (if locking multiple rows in different order) |
| Use when | Most CRUD, read-heavy, low contention | Inventory decrement, seat booking, financial transfers |

---

## PART 5: N+1 Problem

## 74.10 What it is

```java
// Loading 10 orders, each with a user:
List<Order> orders = orderRepository.findAll();  // 1 query: SELECT * FROM orders

for (Order order : orders) {
    System.out.println(order.getUser().getName());
    // LAZY loading triggers 1 query PER order: SELECT * FROM users WHERE id = ?
}

// TOTAL: 1 + 10 = 11 queries! (N+1 where N = number of orders)
// With 1000 orders: 1001 queries! Catastrophically slow.
```

## 74.11 Fix: JOIN FETCH

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    
    // JOIN FETCH: load orders AND users in ONE query
    @Query("SELECT o FROM Order o JOIN FETCH o.user")
    List<Order> findAllWithUser();
    
    // Multiple JOIN FETCHes
    @Query("SELECT o FROM Order o JOIN FETCH o.user JOIN FETCH o.items i JOIN FETCH i.product")
    List<Order> findAllWithDetails();
}

// Result: 1 query instead of N+1!
// SELECT o.*, u.* FROM orders o JOIN users u ON o.user_id = u.id
```

## 74.12 Fix: @EntityGraph

```java
@Entity
@NamedEntityGraph(name = "Order.withUserAndItems",
    attributeNodes = {
        @NamedAttributeNode("user"),
        @NamedAttributeNode(value = "items", subgraph = "items.product"),
    },
    subgraphs = @NamedSubgraph(name = "items.product", attributeNodes = @NamedAttributeNode("product"))
)
public class Order { ... }

// Use in repository:
@EntityGraph(value = "Order.withUserAndItems")
List<Order> findByStatus(OrderStatus status);
```

## 74.13 Fix: Batch fetching (global)

```yaml
# application.yml — fetch lazy collections in batches (not one by one)
spring:
  jpa:
    properties:
      hibernate:
        default_batch_fetch_size: 20
```

With batch size 20: instead of N individual queries, Hibernate fetches 20 at a time using `WHERE id IN (?, ?, ..., ?)`. 1000 orders → 50 queries instead of 1000.

---

## PART 6: The Complete Order Service

## 74.14 Putting it all together

```java
@Service
@Transactional(readOnly = true)
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final UserRepository userRepository;

    @Transactional  // read-write
    public OrderResponse createOrder(Long userId, List<OrderItemRequest> items) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new NotFoundException("User", userId));

        Order order = new Order();
        order.setUser(user);

        for (OrderItemRequest itemReq : items) {
            // PESSIMISTIC LOCK: prevent overselling
            Product product = productRepository.findByIdWithLock(itemReq.productId())
                .orElseThrow(() -> new NotFoundException("Product", itemReq.productId()));

            if (product.getStock() < itemReq.quantity()) {
                throw new InsufficientStockException(
                    "Product '%s' has only %d in stock (requested: %d)"
                    .formatted(product.getName(), product.getStock(), itemReq.quantity())
                );
            }

            // Decrement stock (safe — we hold the lock)
            product.setStock(product.getStock() - itemReq.quantity());

            // Add item to order (snapshots current price)
            order.addItem(product, itemReq.quantity());
        }

        Order saved = orderRepository.save(order);
        return OrderResponse.from(saved);
    }

    @Transactional
    @Retryable(value = OptimisticLockException.class, maxAttempts = 3)
    public OrderResponse cancelOrder(Long orderId) {
        Order order = orderRepository.findByIdWithItems(orderId)
            .orElseThrow(() -> new NotFoundException("Order", orderId));

        if (order.getStatus() != OrderStatus.PENDING) {
            throw new IllegalStateException("Only pending orders can be cancelled");
        }

        // Restore stock
        for (OrderItem item : order.getItems()) {
            Product product = item.getProduct();
            product.setStock(product.getStock() + item.getQuantity());
        }

        order.setStatus(OrderStatus.CANCELLED);
        // @Version on Order ensures no concurrent modification
        return OrderResponse.from(order);
    }

    // Read-only: no locking needed
    public Page<OrderResponse> getUserOrders(Long userId, Pageable pageable) {
        return orderRepository.findByUserIdWithDetails(userId, pageable)
            .map(OrderResponse::from);
    }
}
```

---

## Summary

✅ Entity lifecycle: transient → managed (dirty-checked) → detached → removed
✅ Fetch strategies: ALWAYS use LAZY, fetch eagerly with JOIN FETCH when needed
✅ Transaction problems: dirty read, non-repeatable read, phantom read
✅ Isolation levels: READ_COMMITTED (default, 95% of cases), REPEATABLE_READ (financial)
✅ Optimistic locking: @Version field, conflict → exception → retry (best for low contention)
✅ Pessimistic locking: SELECT FOR UPDATE, blocks other transactions (best for high contention/inventory)
✅ N+1 problem: JOIN FETCH, @EntityGraph, or batch_fetch_size (ALWAYS fix this!)
✅ Complete order system with concurrent stock management

## Key takeaways

**Optimistic locking is your default choice.** @Version with retry handles 90% of concurrency. Only use pessimistic locking when you KNOW there's high contention on specific rows (inventory, seat booking, financial balances).

**LAZY loading + JOIN FETCH = best performance.** Set everything to LAZY (no surprise queries). When you need related data, explicitly JOIN FETCH in your query. This gives you full control over what's loaded and when.

**The N+1 problem is the #1 JPA performance issue.** If your app is slow, check your SQL logs. See 100 individual SELECTs? That's N+1. Fix with JOIN FETCH or batch_fetch_size. Always.

---

→ [Back to Chapter 73: Python One-Liners](./73-PYTHON-ONELINERS.md)
