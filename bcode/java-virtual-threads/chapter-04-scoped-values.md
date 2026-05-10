# Chapter 4: Scoped Values

[← Chapter 3: Structured Concurrency](chapter-03-structured-concurrency.md) | [Chapter 5: I/O Bound Workloads →](chapter-05-io-bound.md)

---

## The Problem

VaultPay uses `ThreadLocal` everywhere. Every request carries context — the tenant ID, the correlation ID for distributed tracing, the authenticated user:

```java
public class RequestContext {
    private static final ThreadLocal<String> TENANT_ID = new ThreadLocal<>();
    private static final ThreadLocal<String> CORRELATION_ID = new ThreadLocal<>();
    private static final ThreadLocal<User> CURRENT_USER = new ThreadLocal<>();

    public static void set(String tenant, String correlationId, User user) {
        TENANT_ID.set(tenant);
        CORRELATION_ID.set(correlationId);
        CURRENT_USER.set(user);
    }

    public static String getTenantId() { return TENANT_ID.get(); }
    public static String getCorrelationId() { return CORRELATION_ID.get(); }
    public static User getCurrentUser() { return CURRENT_USER.get(); }

    public static void clear() {
        TENANT_ID.remove();
        CORRELATION_ID.remove();
        CURRENT_USER.remove();
    }
}
```

With 200 platform threads, this works fine. 200 threads × 3 ThreadLocal entries = 600 objects. Negligible.

With virtual threads, you have 100,000 concurrent requests. Each gets its own virtual thread. Each virtual thread gets its own `ThreadLocal` copies.

100,000 threads × 3 ThreadLocals × (object overhead + references) = **significant memory pressure**.

But the real problem isn't just memory. It's mutability.

Raj found a bug: a thread sets `TENANT_ID` to "acme-corp", calls a library that internally spawns a thread pool task, and that task inherits... nothing. The ThreadLocal is empty in the child thread. Or worse — with `InheritableThreadLocal`, the child gets a *copy* that can be mutated independently, leading to stale context.

ThreadLocal was designed for a world with hundreds of threads. Virtual threads break its assumptions.

## ScopedValue: The Replacement

Java 21 introduces `ScopedValue` (preview) — immutable, bounded, and automatically inherited by child threads in structured concurrency:

```java
public class RequestContext {
    public static final ScopedValue<String> TENANT_ID = ScopedValue.newInstance();
    public static final ScopedValue<String> CORRELATION_ID = ScopedValue.newInstance();
    public static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();
}
```

## The where/run Pattern

You bind a scoped value for a specific block of code:

```java
ScopedValue.where(RequestContext.TENANT_ID, "acme-corp")
    .where(RequestContext.CORRELATION_ID, "txn-abc-123")
    .where(RequestContext.CURRENT_USER, authenticatedUser)
    .run(() -> {
        // Inside here, all three values are bound
        processPayment(request);
    });
```

Inside `processPayment` and everything it calls:

```java
public void processPayment(PaymentRequest request) {
    String tenant = RequestContext.TENANT_ID.get(); // "acme-corp"
    String corrId = RequestContext.CORRELATION_ID.get(); // "txn-abc-123"

    // Pass context to downstream calls without method parameters
    fraudService.check(request);  // can read TENANT_ID inside
    ledgerService.record(request); // can read CORRELATION_ID inside
}
```

## Why ScopedValue Over ThreadLocal?

| Property | ThreadLocal | ScopedValue |
|---|---|---|
| Mutability | Mutable (set/get anytime) | Immutable within scope |
| Lifetime | Until remove() is called | Automatic — ends with scope |
| Inheritance | Copies value (InheritableThreadLocal) | Shared reference (zero-copy) |
| Memory | One copy per thread | One instance, many readers |
| Cleanup | Manual (easy to forget) | Automatic |
| With 1M threads | 1M copies | 1 instance |

The key difference: ScopedValue doesn't copy. All virtual threads within the scope **share** the same reference. Since the value is immutable, this is safe.

## VaultPay: Request Filter with ScopedValue

```java
@Component
public class RequestContextFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpReq = (HttpServletRequest) req;
        String tenant = httpReq.getHeader("X-Tenant-ID");
        String correlationId = httpReq.getHeader("X-Correlation-ID");
        User user = authenticate(httpReq);

        ScopedValue.where(RequestContext.TENANT_ID, tenant)
            .where(RequestContext.CORRELATION_ID, correlationId)
            .where(RequestContext.CURRENT_USER, user)
            .run(() -> {
                try {
                    chain.doFilter(req, res);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });
    }
}
```

Every controller, service, and repository called within this filter can access the scoped values. When the request completes, the bindings vanish. No cleanup needed. No memory leak possible.

## ScopedValue + Structured Concurrency

Scoped values are automatically inherited by `StructuredTaskScope` subtasks:

```java
ScopedValue.where(RequestContext.CORRELATION_ID, "txn-abc-123").run(() -> {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {

        scope.fork(() -> {
            // This subtask can read the correlation ID
            String id = RequestContext.CORRELATION_ID.get(); // "txn-abc-123"
            return fraudService.checkWithTracing(id, request);
        });

        scope.fork(() -> {
            // So can this one — same value, zero copies
            String id = RequestContext.CORRELATION_ID.get(); // "txn-abc-123"
            return balanceService.checkWithTracing(id, request);
        });

        scope.join();
        scope.throwIfFailed();
    }
});
```

No `InheritableThreadLocal` gymnastics. No manual propagation. The scoped value is visible to all child threads within the structured scope.

## The Memory Math

With ThreadLocal and 100K virtual threads:
```
100,000 threads × InheritableThreadLocal copy of RequestContext
= 100,000 RequestContext objects
= 100,000 × (tenant String + correlationId String + User object)
≈ 50MB of duplicated context
```

With ScopedValue and 100K virtual threads:
```
1 RequestContext binding per request scope
Child threads share the reference (no copy)
≈ 0.5MB total
```

100x less memory for context propagation.

## Rebinding in Nested Scopes

You can rebind a scoped value for a narrower scope:

```java
ScopedValue.where(RequestContext.TENANT_ID, "acme-corp").run(() -> {
    System.out.println(RequestContext.TENANT_ID.get()); // "acme-corp"

    // Nested scope with different binding
    ScopedValue.where(RequestContext.TENANT_ID, "beta-inc").run(() -> {
        System.out.println(RequestContext.TENANT_ID.get()); // "beta-inc"
    });

    // Back to original
    System.out.println(RequestContext.TENANT_ID.get()); // "acme-corp"
});
```

The outer binding is restored automatically. No stack of values to manage.

## What You Learned

- **ThreadLocal at scale** — 1M virtual threads = 1M copies = memory explosion
- **ScopedValue** — immutable, scoped, automatically inherited
- **where/run pattern** — bind values for a block, automatic cleanup
- **Zero-copy inheritance** — child threads share the reference, no duplication
- **Structured concurrency integration** — forked subtasks see parent's scoped values
- **Rebinding** — nested scopes can override values without affecting the parent
- **No cleanup needed** — values are bound to scope lifetime, not thread lifetime

Context propagation is solved. But we've been simulating I/O with `Thread.sleep()`. Time to understand what actually happens when a virtual thread hits a real blocking call — an HTTP request, a database query, a file read. How does the JVM keep 8 carrier threads busy with 10,000 blocked virtual threads?

---

[← Chapter 3: Structured Concurrency](chapter-03-structured-concurrency.md) | [Chapter 5: I/O Bound Workloads →](chapter-05-io-bound.md)
