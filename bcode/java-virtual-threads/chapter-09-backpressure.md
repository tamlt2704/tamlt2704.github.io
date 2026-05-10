# Chapter 9: Backpressure

[← Chapter 8: HTTP Servers](chapter-08-http-servers.md) | [Chapter 10: Debugging & Profiling →](chapter-10-debugging.md)

---

## The Problem

Wednesday, 2 AM. PagerDuty fires. VaultPay's fraud detection service is returning 503s. The service handles 1,000 requests/second normally. Tonight it's receiving 40,000 requests/second.

What happened: the payment authorization service now runs on virtual threads. It handles 10,000 concurrent requests. Each request calls the fraud service. The fraud service hasn't been upgraded — it's still on a 200-thread Tomcat pool.

You removed the bottleneck in your service. You moved it to the next service in the chain. Virtual threads make it trivially easy to generate unbounded concurrency. Without backpressure, you'll DDoS your own infrastructure.

Nadia, at the post-mortem: "Virtual threads don't have a built-in throttle. The thread pool *was* the throttle. We removed it. Now we need to build our own."

## The Semaphore Pattern

A `Semaphore` limits how many virtual threads can perform an operation concurrently:

```java
@Service
public class FraudClient {

    private final HttpClient httpClient = HttpClient.newHttpClient();
    private final Semaphore permits = new Semaphore(100); // max 100 concurrent calls

    public FraudResult check(AuthRequest request) throws Exception {
        permits.acquire(); // virtual thread parks here if no permits available
        try {
            HttpRequest httpReq = HttpRequest.newBuilder()
                .uri(URI.create("https://fraud.internal/check"))
                .POST(HttpRequest.BodyPublishers.ofString(toJson(request)))
                .build();

            HttpResponse<String> response = httpClient.send(httpReq,
                HttpResponse.BodyHandlers.ofString());

            return parseResponse(response.body());
        } finally {
            permits.release();
        }
    }
}
```

10,000 virtual threads call `check()`. Only 100 proceed to the HTTP call. The other 9,900 park on `permits.acquire()` — cheaply, without holding any resources. When a call completes and releases a permit, the next parked virtual thread wakes up.

## Timed Permits: Fail Fast

Don't let virtual threads wait forever for a permit:

```java
public FraudResult check(AuthRequest request) throws Exception {
    boolean acquired = permits.tryAcquire(2, TimeUnit.SECONDS);
    if (!acquired) {
        // Shed load — return a degraded response instead of waiting
        return FraudResult.allowWithWarning("fraud_service_overloaded");
    }
    try {
        return callFraudApi(request);
    } finally {
        permits.release();
    }
}
```

After 2 seconds of waiting, the request gets a degraded response instead of timing out. This is **load shedding** — better to serve a partial answer than to queue indefinitely.

## The Bulkhead Pattern

Different downstream services have different capacities. Use separate semaphores for each:

```java
@Service
public class PaymentService {

    // Each downstream gets its own concurrency limit
    private final Semaphore fraudPermits = new Semaphore(100);
    private final Semaphore bankPermits = new Semaphore(50);
    private final Semaphore ledgerPermits = new Semaphore(200);

    public AuthResult authorize(AuthRequest request) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {

            Subtask<FraudResult> fraud = scope.fork(() -> {
                fraudPermits.acquire();
                try { return fraudService.check(request); }
                finally { fraudPermits.release(); }
            });

            Subtask<BankResult> bank = scope.fork(() -> {
                bankPermits.acquire();
                try { return bankService.authorize(request); }
                finally { bankPermits.release(); }
            });

            scope.join();
            scope.throwIfFailed();

            // Record in ledger
            ledgerPermits.acquire();
            try { ledgerService.record(request, bank.get().getAuthCode()); }
            finally { ledgerPermits.release(); }

            return AuthResult.approved(bank.get().getAuthCode());
        }
    }
}
```

If the bank API is slow, only 50 virtual threads are stuck waiting for it. The fraud service and ledger continue operating normally. One slow dependency doesn't cascade to everything else.

## Rate Limiting with Virtual Threads

For strict rate limits (e.g., "max 500 requests/second to the bank API"):

```java
@Service
public class RateLimitedBankClient {

    private final Semaphore permits;
    private final ScheduledExecutorService refiller;

    public RateLimitedBankClient() {
        int maxPerSecond = 500;
        this.permits = new Semaphore(maxPerSecond);

        // Refill permits every second
        this.refiller = Executors.newSingleThreadScheduledExecutor();
        this.refiller.scheduleAtFixedRate(
            () -> permits.release(maxPerSecond - permits.availablePermits()),
            1, 1, TimeUnit.SECONDS
        );
    }

    public BankResult authorize(AuthRequest request) throws Exception {
        if (!permits.tryAcquire(5, TimeUnit.SECONDS)) {
            throw new RateLimitExceededException("Bank API rate limit reached");
        }
        return bankApi.call(request);
    }
}
```

## Why Not Just Use a Thread Pool?

You might think: "Just use `Executors.newFixedThreadPool(100)` to limit concurrency."

Don't. That defeats the purpose of virtual threads:

```java
// BAD: pooling virtual threads
ExecutorService pool = Executors.newFixedThreadPool(100);
pool.submit(() -> callFraudApi(request)); // queues in the pool

// GOOD: semaphore + virtual threads
Semaphore permits = new Semaphore(100);
Thread.startVirtualThread(() -> {
    permits.acquire();
    try { callFraudApi(request); }
    finally { permits.release(); }
});
```

The semaphore approach lets virtual threads park cheaply. The thread pool approach wastes platform threads as a concurrency limiter.

## VaultPay: The Complete Backpressure Strategy

```java
@Configuration
public class BackpressureConfig {

    @Bean
    public Semaphore fraudServicePermits() {
        return new Semaphore(100);  // fraud service handles 1K/s, we're one of 10 clients
    }

    @Bean
    public Semaphore bankApiPermits() {
        return new Semaphore(50);   // bank API contract: max 50 concurrent
    }

    @Bean
    public Semaphore databasePermits() {
        return new Semaphore(50);   // matches HikariCP pool size
    }
}
```

```java
@Service
public class ProtectedPaymentService {

    @Autowired private Semaphore fraudServicePermits;
    @Autowired private Semaphore bankApiPermits;

    public AuthResult authorize(AuthRequest request) throws Exception {
        // Fraud check with backpressure
        FraudResult fraud = withPermit(fraudServicePermits, Duration.ofSeconds(2),
            () -> fraudService.check(request));

        if (fraud.isRejected()) return AuthResult.declined("fraud");

        // Bank call with backpressure
        BankResult bank = withPermit(bankApiPermits, Duration.ofSeconds(5),
            () -> bankService.authorize(request));

        return AuthResult.approved(bank.getAuthCode());
    }

    private <T> T withPermit(Semaphore sem, Duration timeout, Callable<T> task)
            throws Exception {
        if (!sem.tryAcquire(timeout.toMillis(), TimeUnit.MILLISECONDS)) {
            throw new ServiceOverloadedException("Downstream at capacity");
        }
        try {
            return task.call();
        } finally {
            sem.release();
        }
    }
}
```

## What You Learned

- **Unbounded concurrency** — virtual threads have no built-in throttle; the thread pool was the throttle
- **Semaphore pattern** — limits concurrent access to a downstream resource
- **Timed permits** — `tryAcquire` with timeout enables load shedding
- **Bulkhead pattern** — separate semaphores per downstream service isolate failures
- **Rate limiting** — semaphore + scheduled refill for requests-per-second limits
- **Don't pool virtual threads** — use semaphores for concurrency control instead
- **Fail fast** — reject or degrade when downstream is at capacity

Backpressure is in place. VaultPay handles 10,000 concurrent requests without overwhelming downstream services. But Raj has a new problem: "I can't see what's happening. My monitoring shows 50,000 active threads. My thread dump is 2GB. My profiler crashed. How do I debug this?"

---

[← Chapter 8: HTTP Servers](chapter-08-http-servers.md) | [Chapter 10: Debugging & Profiling →](chapter-10-debugging.md)
