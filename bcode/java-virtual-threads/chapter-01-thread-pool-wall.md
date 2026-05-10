# Chapter 1: The Thread Pool Wall

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Your First Virtual Thread →](chapter-02-first-virtual-thread.md)

---

## The Problem

VaultPay's payment authorization endpoint:

```java
@RestController
public class AuthorizationController {

    @Autowired private FraudService fraudService;
    @Autowired private BankService bankService;
    @Autowired private LedgerService ledgerService;

    @PostMapping("/authorize")
    public ResponseEntity<AuthResult> authorize(@RequestBody AuthRequest request) {
        // Step 1: Check fraud (calls external API, ~100ms)
        FraudCheck fraud = fraudService.check(request);
        if (fraud.isRejected()) {
            return ResponseEntity.ok(AuthResult.declined("fraud"));
        }

        // Step 2: Authorize with bank (calls bank API, ~200ms)
        BankResponse bank = bankService.authorize(request);
        if (!bank.isApproved()) {
            return ResponseEntity.ok(AuthResult.declined("bank"));
        }

        // Step 3: Update ledger (database write, ~20ms)
        ledgerService.record(request, bank.getAuthCode());

        return ResponseEntity.ok(AuthResult.approved(bank.getAuthCode()));
    }
}
```

Each request takes ~320ms (100 + 200 + 20). During that time, the thread is **blocked** — waiting for network responses. It's not computing anything. It's just... waiting.

Tomcat's default thread pool: 200 threads.

Maximum throughput: 200 threads / 0.32 seconds = **625 requests/second**.

VaultPay needs 3,000 requests/second on Black Friday.

## Measuring the Wall

Let's prove it with a load test:

```javascript
// load-test.js (k6)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 100 },   // Ramp to 100 users
        { duration: '30s', target: 500 },   // Ramp to 500 users
        { duration: '30s', target: 1000 },  // Ramp to 1000 users
        { duration: '30s', target: 2000 },  // Ramp to 2000 users
    ],
};

export default function () {
    const payload = JSON.stringify({
        cardNumber: '4111111111111111',
        amount: 42.00,
        merchantId: 'merchant-123',
    });

    const res = http.post('http://localhost:8080/authorize', payload, {
        headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
        'status is 200': (r) => r.status === 200,
        'response time < 1s': (r) => r.timings.duration < 1000,
    });
}
```

Results at 200 concurrent users:
```
✓ status is 200: 100%
✓ response time < 1s: 99.8%
avg response time: 340ms
p95 response time: 380ms
```

Results at 1000 concurrent users:
```
✓ status is 200: 100%
✗ response time < 1s: 34%
avg response time: 2,400ms
p95 response time: 8,100ms
```

At 1000 users, requests queue behind the 200-thread pool. They wait seconds just to get a thread. The actual work still takes 320ms — but the queuing adds 2–8 seconds.

## Why Not Just Add More Threads?

Nadia's first question: "Can't we just set `server.tomcat.threads.max=2000`?"

Let's try:

```yaml
# application.yml
server:
  tomcat:
    threads:
      max: 2000
```

Results at 1000 concurrent users with 2000 threads:
```
✓ response time < 1s: 99.5%
avg response time: 350ms
```

It works! Problem solved?

Check the JVM metrics:

```
Heap used: 512MB
Thread stacks: 2,000 × 1MB = 2,000MB
Total memory: ~2.5GB
GC pause time: 45ms (was 12ms)
```

2GB just for thread stacks. And we're only at 1000 concurrent requests. At 10,000:

```yaml
server:
  tomcat:
    threads:
      max: 10000
```

```
java.lang.OutOfMemoryError: unable to create native thread
```

The OS refuses. On Linux, the default thread limit is typically 4,096–32,768 per process. Even if the OS allows it, 10,000 threads × 1MB = 10GB of stack space. Your 8GB heap is gone.

## The Math of Platform Threads

| Concurrent Requests | Threads Needed | Stack Memory | Feasible? |
|---|---|---|---|
| 200 | 200 | 200MB | ✓ |
| 1,000 | 1,000 | 1GB | Marginal |
| 5,000 | 5,000 | 5GB | Painful |
| 10,000 | 10,000 | 10GB | No |
| 100,000 | 100,000 | 100GB | Impossible |

The thread-per-request model has a hard ceiling. You can't scale it with hardware — you hit OS limits before you hit CPU limits.

## What the Thread Is Actually Doing

Here's the timeline of a single request on a platform thread:

```
Time:  0ms        100ms       300ms    320ms
       |-----------|-----------|--------|
       [fraud API] [bank API ] [ledger]
       ← waiting → ← waiting → ←wait→

CPU work: ~1ms total (serialization, logic)
Waiting:  ~319ms total (network I/O)
Thread utilization: 0.3%
```

The thread is **99.7% idle**. It exists only to hold a stack frame while waiting for network responses. That's 1MB of memory to remember "I'm waiting for the bank API to respond."

This is the fundamental problem. Platform threads are expensive containers for cheap state.

## The Traditional Solutions (And Why They're Painful)

### Option 1: Reactive/Async (WebFlux)

```java
@GetMapping("/authorize")
public Mono<AuthResult> authorize(@RequestBody AuthRequest request) {
    return fraudService.checkReactive(request)
        .flatMap(fraud -> {
            if (fraud.isRejected()) {
                return Mono.just(AuthResult.declined("fraud"));
            }
            return bankService.authorizeReactive(request)
                .flatMap(bank -> {
                    if (!bank.isApproved()) {
                        return Mono.just(AuthResult.declined("bank"));
                    }
                    return ledgerService.recordReactive(request, bank.getAuthCode())
                        .map(v -> AuthResult.approved(bank.getAuthCode()));
                });
        });
}
```

This works — it uses a small thread pool and never blocks. But:
- The code is unreadable (callback hell with types)
- Stack traces are useless (no sequential call stack)
- Debugging is a nightmare
- Every library must be reactive (JDBC isn't)
- The entire team needs retraining

Nadia: "We have 200K lines of blocking code. We're not rewriting it in reactive."

### Option 2: Async with CompletableFuture

```java
public CompletableFuture<AuthResult> authorize(AuthRequest request) {
    return fraudService.checkAsync(request)
        .thenCompose(fraud -> {
            if (fraud.isRejected()) {
                return CompletableFuture.completedFuture(AuthResult.declined("fraud"));
            }
            return bankService.authorizeAsync(request);
        })
        .thenCompose(bank -> {
            // ... more nesting
        });
}
```

Same problems. Different syntax. Still not sequential code.

### Option 3: Virtual Threads

```java
@PostMapping("/authorize")
public ResponseEntity<AuthResult> authorize(@RequestBody AuthRequest request) {
    // SAME CODE AS BEFORE — no changes!
    FraudCheck fraud = fraudService.check(request);
    if (fraud.isRejected()) {
        return ResponseEntity.ok(AuthResult.declined("fraud"));
    }

    BankResponse bank = bankService.authorize(request);
    if (!bank.isApproved()) {
        return ResponseEntity.ok(AuthResult.declined("bank"));
    }

    ledgerService.record(request, bank.getAuthCode());
    return ResponseEntity.ok(AuthResult.approved(bank.getAuthCode()));
}
```

Same blocking code. Same sequential logic. Same readability. But now each request runs on a virtual thread that costs ~1KB instead of 1MB. When it blocks on the fraud API, it unmounts — the carrier thread picks up another virtual thread.

10,000 concurrent requests × 1KB = 10MB. Not 10GB.

## The One-Line Fix (Preview)

```yaml
# application.yml (Spring Boot 3.2+)
spring:
  threads:
    virtual:
      enabled: true
```

That's it. Tomcat now uses virtual threads instead of a platform thread pool. Every request gets its own virtual thread. No pool. No queue. No ceiling.

Results at 10,000 concurrent users:
```
✓ status is 200: 100%
✓ response time < 1s: 99.9%
avg response time: 330ms
p95 response time: 360ms
Thread stacks: ~10MB (was 10GB)
```

Same code. Same logic. 50x more concurrency. 1000x less memory for threads.

Nadia: "That's suspiciously easy. What's the catch?"

There are catches. Several of them. That's Chapters 3–12.

## What You Learned

- **Platform threads** — 1:1 with OS threads, ~1MB each, limited to thousands
- **Thread-per-request** — simple model, hard ceiling on concurrency
- **The wall** — when requests exceed thread pool size, latency explodes
- **Thread utilization** — I/O-bound threads are 99%+ idle
- **Traditional solutions** — reactive/async works but destroys readability
- **Virtual threads** — same blocking code, 1000x cheaper threads
- **The one-line fix** — Spring Boot 3.2+ virtual thread executor

The thread pool wall is gone. But we've traded one set of problems for another. Virtual threads are cheap — so cheap that you can accidentally create a million of them. And a million threads all hitting your database at once is a different kind of disaster.

Let's understand how virtual threads actually work.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Your First Virtual Thread →](chapter-02-first-virtual-thread.md)
