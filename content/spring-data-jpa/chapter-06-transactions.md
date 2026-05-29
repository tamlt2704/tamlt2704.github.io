# Chapter 6: Transactions

[prev: N+1 Problem](chapter-05-n-plus-one.md) | [next: Specifications](chapter-07-specifications.md)

## @Transactional Basics

```java
@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;

    public OrderService(OrderRepository orderRepository, InventoryService inventoryService) {
        this.orderRepository = orderRepository;
        this.inventoryService = inventoryService;
    }

    @Transactional
    public Order placeOrder(CreateOrderRequest request) {
        Order order = new Order();
        order.setStatus(OrderStatus.PENDING);
        order.setCustomerId(request.customerId());

        Order saved = orderRepository.save(order);
        inventoryService.reserve(request.items()); // if this throws, order is rolled back

        return saved;
    }
}
```

`@Transactional` wraps the method in a database transaction. If any unchecked exception is thrown, the entire transaction rolls back.

## Propagation

| Propagation          | Behavior                                        |
| -------------------- | ----------------------------------------------- |
| `REQUIRED` (default) | Join existing tx, or create new one             |
| `REQUIRES_NEW`       | Always create a new tx (suspends current)       |
| `MANDATORY`          | Must run within existing tx (throws if none)    |
| `SUPPORTS`           | Join tx if exists, otherwise run without        |
| `NOT_SUPPORTED`      | Run without tx (suspends current)               |
| `NEVER`              | Must NOT run within a tx (throws if one exists) |
| `NESTED`             | Nested tx with savepoint (JDBC only)            |

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void sendNotification(Long orderId) {
    // runs in its own transaction — failure here won't roll back the caller
}
```

## Isolation Levels

| Level            | Dirty Read | Non-Repeatable Read | Phantom Read |
| ---------------- | ---------- | ------------------- | ------------ |
| READ_UNCOMMITTED | Yes        | Yes                 | Yes          |
| READ_COMMITTED   | No         | Yes                 | Yes          |
| REPEATABLE_READ  | No         | No                  | Yes          |
| SERIALIZABLE     | No         | No                  | No           |

```java
@Transactional(isolation = Isolation.REPEATABLE_READ)
public void transferFunds(Long fromId, Long toId, BigDecimal amount) {
    // prevents non-repeatable reads during the transfer
}
```

PostgreSQL default is `READ_COMMITTED`. Only change isolation when you have a specific concurrency requirement.

## readOnly

```java
@Transactional(readOnly = true)
public List<Order> getOrderHistory(Long customerId) {
    return orderRepository.findByCustomerId(customerId);
}
```

Benefits of `readOnly = true`:

- Hibernate skips dirty checking (faster flush)
- Some databases route to read replicas
- Prevents accidental writes

**Use `readOnly = true` on all read-only service methods.**

## rollbackFor

```java
@Transactional(rollbackFor = Exception.class)
public void importData(InputStream data) throws IOException {
    // By default, only RuntimeException triggers rollback
    // This ensures checked exceptions also trigger rollback
}
```

Default behavior:

- `RuntimeException` / `Error` → rollback
- Checked `Exception` → commit (usually not what you want)

## Programmatic Transactions

When you need fine-grained control:

```java
@Service
public class BatchService {

    private final TransactionTemplate transactionTemplate;
    private final ItemRepository itemRepository;

    public BatchService(PlatformTransactionManager txManager, ItemRepository itemRepository) {
        this.transactionTemplate = new TransactionTemplate(txManager);
        this.itemRepository = itemRepository;
    }

    public void processBatch(List<Item> items) {
        for (List<Item> chunk : partition(items, 100)) {
            transactionTemplate.execute(status -> {
                itemRepository.saveAll(chunk);
                return null;
            });
        }
    }
}
```

## Optimistic Locking (@Version)

Detects concurrent modifications without database locks:

```java
@Entity
@Table(name = "products")
@Getter @Setter @NoArgsConstructor
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Version
    private Integer version;
}
```

```java
@Service
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    @Transactional
    public Product updatePrice(Long id, BigDecimal newPrice) {
        Product product = productRepository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Product not found: " + id));
        product.setPrice(newPrice);
        return productRepository.save(product);
        // If another transaction modified this row, throws OptimisticLockException
    }
}
```

Hibernate adds `WHERE version = ?` to the UPDATE. If the version changed, zero rows are updated and `OptimisticLockException` is thrown.

**Use optimistic locking when**: conflicts are rare, you want high throughput, and you can retry on conflict.

## Pessimistic Locking (@Lock)

Acquires a database lock — other transactions wait:

```java
public interface AccountRepository extends JpaRepository<Account, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Optional<Account> findByIdForUpdate(@Param("id") Long id);
}
```

```java
@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    // Lock both accounts — order by ID to prevent deadlocks
    Long firstId = Math.min(fromId, toId);
    Long secondId = Math.max(fromId, toId);

    Account first = accountRepository.findByIdForUpdate(firstId)
        .orElseThrow();
    Account second = accountRepository.findByIdForUpdate(secondId)
        .orElseThrow();

    Account from = fromId.equals(firstId) ? first : second;
    Account to = toId.equals(firstId) ? first : second;

    from.debit(amount);
    to.credit(amount);
}
```

**Use pessimistic locking when**: conflicts are frequent, operations cannot be retried, or you need guaranteed consistency (e.g., financial transfers).

## Deadlock Prevention

1. **Always acquire locks in a consistent order** (e.g., by ID ascending)
2. **Keep transactions short** — less time holding locks
3. **Set lock timeouts**:

```yaml
spring:
  jpa:
    properties:
      jakarta.persistence.lock.timeout: 5000 # 5 seconds
```

4. **Avoid mixing pessimistic and optimistic locking** on the same entity

## Common Pitfalls

**Self-invocation bypass**: `@Transactional` uses proxies — calling a transactional method from within the same class bypasses the proxy:

```java
@Service
public class OrderService {

    @Transactional
    public void processOrder(Long id) {
        // ...
        this.sendEmail(id); // BUG: @Transactional on sendEmail is ignored
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void sendEmail(Long id) {
        // This won't get its own transaction when called from processOrder
    }
}
```

Fix: inject the service into itself, or extract to a separate class.

## Exercises

1. Create a service with `@Transactional` that saves two entities — throw an exception after the first save and verify both are rolled back
2. Add `@Version` to an entity, load it in two transactions, modify both, and observe `OptimisticLockException`
3. Implement a money transfer with `PESSIMISTIC_WRITE` locks, ordered by account ID
4. Test `readOnly = true` — try to save an entity in a read-only transaction and observe the behavior
5. Demonstrate the self-invocation problem and fix it by extracting to a separate service
