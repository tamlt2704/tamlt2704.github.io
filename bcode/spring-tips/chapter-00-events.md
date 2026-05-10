# Chapter 0: Event Publisher — Decoupling with Domain Events

[Chapter 1: Available Beans →](chapter-01-beans.md)

---

## Why Events?

You have an `OrderService` that, after placing an order, needs to:
1. Send a confirmation email
2. Update inventory
3. Notify the warehouse
4. Log an audit trail

The naive approach:

```java
@Service
public class OrderService {
    private final EmailService emailService;
    private final InventoryService inventoryService;
    private final WarehouseService warehouseService;
    private final AuditService auditService;

    @Transactional
    public Order placeOrder(OrderRequest request) {
        Order order = orderRepository.save(createOrder(request));
        emailService.sendConfirmation(order);      // Coupled!
        inventoryService.decrementStock(order);    // Coupled!
        warehouseService.notify(order);            // Coupled!
        auditService.log("ORDER_PLACED", order);   // Coupled!
        return order;
    }
}
```

Problems: OrderService knows about email, inventory, warehouse, and audit. Adding a new side-effect means editing OrderService. Testing requires mocking 4 dependencies.

**Events fix this.** OrderService publishes "order placed." Listeners react independently.

## Basic Event Publishing

### 1. Define the Event

```java
// A simple POJO — no special interface needed (Spring 4.2+)
public record OrderPlacedEvent(
    String orderId,
    String customerId,
    BigDecimal total,
    List<String> itemIds,
    Instant timestamp
) {
    public OrderPlacedEvent(Order order) {
        this(order.getId(), order.getCustomerId(), order.getTotal(),
             order.getItemIds(), Instant.now());
    }
}
```

### 2. Publish the Event

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public Order placeOrder(OrderRequest request) {
        Order order = orderRepository.save(createOrder(request));

        // Publish — OrderService doesn't know who's listening
        eventPublisher.publishEvent(new OrderPlacedEvent(order));

        return order;
    }
}
```

### 3. Listen to the Event

```java
@Component
@RequiredArgsConstructor
public class OrderEmailListener {
    private final EmailService emailService;

    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        emailService.sendConfirmation(event.orderId(), event.customerId());
    }
}

@Component
@RequiredArgsConstructor
public class InventoryListener {
    private final InventoryService inventoryService;

    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        inventoryService.decrementStock(event.itemIds());
    }
}

@Component
public class AuditListener {
    private static final Logger log = LoggerFactory.getLogger(AuditListener.class);

    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        log.info("Order placed: {} by customer {} for ${}",
                 event.orderId(), event.customerId(), event.total());
    }
}
```

Now OrderService has ONE dependency (the publisher). Adding a new reaction = adding a new listener class. No changes to OrderService.

## Async Events

By default, events are synchronous — the publisher waits for all listeners to finish. For slow operations (email, HTTP calls), make them async:

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean
    public TaskExecutor applicationEventExecutor() {
        var executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(8);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("event-");
        executor.initialize();
        return executor;
    }
}

@Component
public class OrderEmailListener {

    @Async  // Runs on a separate thread — doesn't block the publisher
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        // Slow email sending doesn't block order placement
        emailService.sendConfirmation(event.orderId(), event.customerId());
    }
}
```

**Warning:** `@Async` listeners run outside the original transaction. If the transaction rolls back, the email is already sent. Use `@TransactionalEventListener` for safety.

## Transactional Events (The Right Way)

```java
@Component
public class InventoryListener {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onOrderPlaced(OrderPlacedEvent event) {
        // Only runs if the transaction COMMITTED successfully
        // If order save fails → this never fires
        inventoryService.decrementStock(event.itemIds());
    }
}

@Component
public class NotificationListener {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void onOrderFailed(OrderPlacedEvent event) {
        // Only runs if the transaction ROLLED BACK
        alertService.notifyFailure(event.orderId());
    }
}
```

Transaction phases:
- `AFTER_COMMIT` — most common, safe for side-effects
- `AFTER_ROLLBACK` — cleanup/alerting on failure
- `AFTER_COMPLETION` — runs regardless of outcome
- `BEFORE_COMMIT` — runs inside the transaction (can cause rollback)

## Conditional Listening

```java
@Component
public class HighValueOrderListener {

    // Only fires for orders over $1000
    @EventListener(condition = "#event.total.compareTo(new java.math.BigDecimal('1000')) > 0")
    public void onHighValueOrder(OrderPlacedEvent event) {
        slackService.notify("#sales", "🎉 High-value order: $" + event.total());
    }
}
```

## Returning Events (Event Chains)

A listener can return another event, creating a chain:

```java
@Component
public class PaymentListener {

    @EventListener
    public PaymentProcessedEvent onOrderPlaced(OrderPlacedEvent event) {
        Payment payment = paymentService.charge(event.customerId(), event.total());
        return new PaymentProcessedEvent(payment.getId(), event.orderId());
    }
}

// Another listener picks up the returned event
@Component
public class ReceiptListener {

    @EventListener
    public void onPaymentProcessed(PaymentProcessedEvent event) {
        receiptService.generate(event.paymentId(), event.orderId());
    }
}
```

## Generic Events with Generics

```java
// Generic event wrapper
public record EntityCreatedEvent<T>(T entity, String createdBy, Instant at) {}

// Listener for specific type
@EventListener
public void onUserCreated(EntityCreatedEvent<User> event) {
    welcomeService.sendWelcome(event.entity());
}
```

**Note:** Due to type erasure, this only works if Spring can resolve the generic at compile time. For runtime generics, use `ResolvableType` or separate event classes.

## Testing Events

```java
@SpringBootTest
class OrderServiceTest {

    @Autowired OrderService orderService;
    @Autowired ApplicationEventPublisher publisher;

    @MockBean EmailService emailService;  // Mock the slow dependency

    @Test
    void placeOrder_publishesEvent() {
        // Use ApplicationEvents to capture published events
        // (Spring Boot 3.1+)
    }
}

// Or test listeners in isolation:
@Test
void listener_sendsEmail_onOrderPlaced() {
    var listener = new OrderEmailListener(mockEmailService);
    var event = new OrderPlacedEvent("ord-1", "cust-1", BigDecimal.TEN, List.of(), Instant.now());

    listener.onOrderPlaced(event);

    verify(mockEmailService).sendConfirmation("ord-1", "cust-1");
}
```

## When to Use Events vs Direct Calls

| Use Events When | Use Direct Calls When |
|---|---|
| Multiple independent reactions | One clear dependency |
| Reactions might change/grow | Logic is core to the operation |
| Async processing is acceptable | Synchronous consistency required |
| You want loose coupling | You want explicit flow |
| Cross-module communication | Same-module internal logic |

## Spring's Built-in Events

Spring publishes these automatically:

| Event | When |
|---|---|
| `ContextRefreshedEvent` | ApplicationContext initialized/refreshed |
| `ContextStartedEvent` | Context started |
| `ContextStoppedEvent` | Context stopped |
| `ContextClosedEvent` | Context closed (shutdown) |
| `ApplicationReadyEvent` | App fully started, ready to serve |
| `ApplicationFailedEvent` | Startup failed |

```java
@Component
public class StartupListener {

    @EventListener(ApplicationReadyEvent.class)
    public void onStartup() {
        log.info("Application is ready! Running post-startup tasks...");
        cacheWarmer.warmAll();
    }
}
```

## What You Learned

- **ApplicationEventPublisher** — publish domain events to decouple services
- **@EventListener** — react to events without coupling to the publisher
- **@Async + @EventListener** — non-blocking event processing
- **@TransactionalEventListener** — only fire after commit (safe for side-effects)
- **Conditional listeners** — filter events with SpEL expressions
- **Event chains** — listeners can return new events
- **Testing** — listeners are simple to unit test in isolation

Events are the backbone of clean Spring architecture. Next: how to see what beans are actually in your application context.

---

[Chapter 1: Available Beans →](chapter-01-beans.md)
