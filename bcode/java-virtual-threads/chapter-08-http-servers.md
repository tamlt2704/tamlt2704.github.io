# Chapter 8: HTTP Servers

[← Chapter 7: Pinning](chapter-07-pinning.md) | [Chapter 9: Backpressure →](chapter-09-backpressure.md)

---

## The Problem

VaultPay's internal services use virtual threads for business logic. But the front door — Tomcat's HTTP connector — still uses a platform thread pool. Every incoming request gets a platform thread from Tomcat's pool (default: 200). That platform thread then creates virtual threads for parallel work.

The bottleneck moved but didn't disappear. At 5,000 concurrent connections, requests queue at Tomcat's thread pool before they even reach your virtual-thread-powered code.

Nadia: "We're using virtual threads inside the handler but platform threads to receive the request. That's like putting a Ferrari engine in a car with bicycle wheels."

## Spring Boot 3.2: One Property

Spring Boot 3.2+ supports virtual threads as the request executor. One property:

```yaml
# application.yml
spring:
  threads:
    virtual:
      enabled: true
```

That's it. Tomcat now dispatches each request to a virtual thread instead of pulling from a platform thread pool. No pool. No queue. No 200-thread ceiling.

## What Changes Under the Hood

### Before (Platform Thread Pool)

```
Request → Tomcat Acceptor → Thread Pool (200 threads) → Handler
                                    ↑
                            Queue when full (9,800 waiting)
```

```java
// Tomcat's default: FixedThreadPool
server:
  tomcat:
    threads:
      max: 200      # hard ceiling
      min-spare: 10
    accept-count: 100  # queue size before rejecting
```

### After (Virtual Thread Per Request)

```
Request → Tomcat Acceptor → New Virtual Thread → Handler
                                    ↑
                            No pool. No queue. Instant dispatch.
```

Each request gets its own virtual thread immediately. The virtual thread handles the entire request lifecycle — reading the body, calling services, writing the response.

## Benchmark: Before and After

Load test with k6, 10,000 concurrent users, each request does 200ms of I/O:

### Platform Threads (200 pool)

```yaml
server:
  tomcat:
    threads:
      max: 200
```

```
✓ status is 200: 100%
✗ response time < 500ms: 12%
avg response time: 4,200ms
p95 response time: 9,800ms
p99 response time: 14,200ms
throughput: 620 req/s
```

### Virtual Threads

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

```
✓ status is 200: 100%
✓ response time < 500ms: 99.7%
avg response time: 210ms
p95 response time: 240ms
p99 response time: 280ms
throughput: 9,400 req/s
```

15x throughput. 20x latency reduction. Same application code.

## Tomcat Configuration with Virtual Threads

When using virtual threads, some Tomcat settings become irrelevant:

```yaml
server:
  tomcat:
    # These no longer matter with virtual threads:
    # threads.max: 200        ← no thread pool
    # threads.min-spare: 10   ← no thread pool
    # accept-count: 100       ← no queuing

    # These still matter:
    max-connections: 10000     # TCP connection limit
    connection-timeout: 20000  # idle connection timeout
```

`max-connections` is now your primary concurrency control. It limits TCP connections at the socket level, independent of threads.

## Programmatic Configuration

If you need more control:

```java
@Configuration
public class VirtualThreadConfig {

    @Bean
    public TomcatProtocolHandlerCustomizer<?> protocolHandlerCustomizer() {
        return protocolHandler -> {
            protocolHandler.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        };
    }
}
```

Or with a custom thread factory for naming:

```java
@Bean
public TomcatProtocolHandlerCustomizer<?> protocolHandlerCustomizer() {
    return protocolHandler -> {
        protocolHandler.setExecutor(
            Executors.newThreadPerTaskExecutor(
                Thread.ofVirtual().name("vaultpay-request-", 0).factory()
            )
        );
    };
}
```

Now thread dumps show meaningful names: `vaultpay-request-0`, `vaultpay-request-1`, etc.

## Spring MVC: No Code Changes

Your controllers don't change at all:

```java
@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    @Autowired private PaymentService paymentService;

    @PostMapping("/authorize")
    public ResponseEntity<AuthResult> authorize(@RequestBody AuthRequest request) {
        // This entire method now runs on a virtual thread
        // All blocking calls inside unmount cleanly
        AuthResult result = paymentService.authorize(request);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Payment> getPayment(@PathVariable String id) {
        // Database query blocks → virtual thread unmounts → carrier is free
        Payment payment = paymentService.findById(id);
        return ResponseEntity.ok(payment);
    }
}
```

Every `@GetMapping`, `@PostMapping`, every filter, every interceptor — all run on virtual threads. Blocking calls in services, repositories, HTTP clients — all unmount cleanly.

## Async Endpoints: Still Useful?

With virtual threads, do you still need `@Async` or `CompletableFuture` return types?

```java
// BEFORE: needed async to avoid blocking the thread pool
@GetMapping("/report")
public CompletableFuture<Report> generateReport() {
    return CompletableFuture.supplyAsync(() -> reportService.generate());
}

// AFTER: just block — the virtual thread handles it
@GetMapping("/report")
public Report generateReport() {
    return reportService.generate(); // blocks, but it's a virtual thread — fine
}
```

Async endpoints add complexity without benefit when running on virtual threads. The blocking call unmounts the virtual thread just as efficiently as an async dispatch would.

## Verifying Virtual Threads Are Active

Add a diagnostic endpoint:

```java
@GetMapping("/debug/thread-info")
public Map<String, Object> threadInfo() {
    Thread current = Thread.currentThread();
    return Map.of(
        "threadName", current.getName(),
        "isVirtual", current.isVirtual(),
        "threadClass", current.getClass().getSimpleName()
    );
}
```

Response:
```json
{
  "threadName": "vaultpay-request-42",
  "isVirtual": true,
  "threadClass": "VirtualThread"
}
```

## What You Learned

- **spring.threads.virtual.enabled=true** — one property to switch Tomcat to virtual threads
- **No thread pool** — each request gets a new virtual thread immediately
- **15x throughput** — for I/O-bound handlers with no code changes
- **Tomcat tuning** — `max-connections` replaces `threads.max` as the concurrency knob
- **Programmatic config** — `TomcatProtocolHandlerCustomizer` for custom executors
- **Async is optional** — blocking code is efficient on virtual threads, no need for `CompletableFuture`
- **Zero code changes** — controllers, services, repositories all work unchanged

The HTTP server is unshackled. VaultPay can accept 10,000 concurrent requests without queuing. But there's a dangerous side effect: if every request spawns virtual threads for parallel work, and those virtual threads call downstream services... you can accidentally send 50,000 concurrent requests to a service that can handle 1,000. Virtual threads make it too easy to overwhelm everything downstream.

---

[← Chapter 7: Pinning](chapter-07-pinning.md) | [Chapter 9: Backpressure →](chapter-09-backpressure.md)
