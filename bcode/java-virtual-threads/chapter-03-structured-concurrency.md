# Chapter 3: Structured Concurrency

[← Chapter 2: Your First Virtual Thread](chapter-02-first-virtual-thread.md) | [Chapter 4: Scoped Values →](chapter-04-scoped-values.md)

---

## The Problem

VaultPay's authorization flow calls three services in parallel: fraud check, balance check, and compliance screening. You rewrote it with virtual threads:

```java
public AuthResult authorize(AuthRequest request) throws Exception {
    ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

    Future<FraudResult> fraud = executor.submit(() -> fraudService.check(request));
    Future<BalanceResult> balance = executor.submit(() -> balanceService.check(request));
    Future<ComplianceResult> compliance = executor.submit(() -> complianceService.screen(request));

    FraudResult fraudResult = fraud.get();       // what if this throws?
    BalanceResult balResult = balance.get();      // this keeps running...
    ComplianceResult compResult = compliance.get(); // so does this

    return combine(fraudResult, balResult, compResult);
}
```

Monday morning. Raj pings you: "The fraud service is down. But I'm seeing thousands of balance checks and compliance screens still running. They complete, return results, and nobody reads them. We're burning API quota for nothing."

The problem: when `fraud.get()` throws, the other two futures are **orphaned**. They keep running. They hold connections. They consume resources. And the results are discarded.

This is **unstructured concurrency** — threads with no parent-child relationship, no automatic cancellation, no lifecycle management.

## Structured Concurrency: The Fix

Java 21 introduces `StructuredTaskScope` (preview). It enforces a rule: **subtasks cannot outlive their parent scope**.

```java
import java.util.concurrent.StructuredTaskScope;
import java.util.concurrent.StructuredTaskScope.Subtask;

public AuthResult authorize(AuthRequest request) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {

        Subtask<FraudResult> fraud = scope.fork(() -> fraudService.check(request));
        Subtask<BalanceResult> balance = scope.fork(() -> balanceService.check(request));
        Subtask<ComplianceResult> compliance = scope.fork(() -> complianceService.screen(request));

        scope.join();            // wait for all subtasks
        scope.throwIfFailed();   // propagate first failure

        // All succeeded — safe to use results
        return combine(fraud.get(), balance.get(), compliance.get());
    }
}
```

If the fraud check throws, `ShutdownOnFailure` **cancels** the balance and compliance tasks immediately. No orphans. No wasted work. No leaked threads.

## ShutdownOnFailure: All Must Succeed

The most common pattern. All subtasks must complete successfully, or the entire scope fails:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<FraudResult> fraud = scope.fork(() -> fraudService.check(request));
    Subtask<BankResult> bank = scope.fork(() -> bankService.authorize(request));

    scope.join();
    scope.throwIfFailed(); // throws if ANY subtask failed

    // Both succeeded
    return new AuthResult(fraud.get(), bank.get());
}
```

Behavior:
- If fraud check fails at 50ms → bank call is cancelled immediately
- If bank call fails at 200ms → fraud result is discarded
- If both succeed → results are available after `join()`

## ShutdownOnSuccess: First Wins

Sometimes you want the first successful result. VaultPay queries multiple payment processors and takes the fastest approval:

```java
try (var scope = new StructuredTaskScope.ShutdownOnSuccess<BankResult>()) {
    scope.fork(() -> processorA.authorize(request));
    scope.fork(() -> processorB.authorize(request));
    scope.fork(() -> processorC.authorize(request));

    scope.join();

    // Returns the first successful result, cancels the rest
    BankResult fastest = scope.result();
    return AuthResult.approved(fastest.getAuthCode());
}
```

Processor A responds in 80ms? The other two are cancelled. No wasted work.

## The Fork/Join Pattern

Every structured concurrency block follows the same shape:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    // 1. FORK — launch subtasks
    Subtask<A> a = scope.fork(() -> computeA());
    Subtask<B> b = scope.fork(() -> computeB());
    Subtask<C> c = scope.fork(() -> computeC());

    // 2. JOIN — wait for completion (or failure)
    scope.join();
    scope.throwIfFailed();

    // 3. USE — results are guaranteed available
    return process(a.get(), b.get(), c.get());
}
// 4. CLOSE — scope ensures all threads are done
```

Rules:
- You can't call `subtask.get()` before `scope.join()` — it throws
- You can't fork after `join()` — the scope is sealed
- When the scope closes, all subtasks are guaranteed terminated

## VaultPay: The Full Authorization

Here's the real authorization flow with structured concurrency:

```java
public AuthResult authorizePayment(AuthRequest request) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {

        // Parallel checks — all must pass
        Subtask<FraudResult> fraud = scope.fork(() -> fraudService.check(request));
        Subtask<BalanceResult> balance = scope.fork(() -> balanceService.verify(request));
        Subtask<ComplianceResult> compliance = scope.fork(() -> complianceService.screen(request));

        scope.join();
        scope.throwIfFailed();

        // All passed — proceed with authorization
        if (fraud.get().isRejected()) {
            return AuthResult.declined("fraud");
        }
        if (!balance.get().isSufficient()) {
            return AuthResult.declined("insufficient_funds");
        }

        // Sequential step: actually charge (must happen after checks)
        BankResult bank = bankService.authorize(request);
        return AuthResult.approved(bank.getAuthCode());
    }
}
```

If the fraud service is down, balance and compliance checks are cancelled within milliseconds. No orphaned threads. No wasted API calls. No partial state.

## Timeout Support

Add a deadline to the entire scope:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<FraudResult> fraud = scope.fork(() -> fraudService.check(request));
    Subtask<BankResult> bank = scope.fork(() -> bankService.authorize(request));

    scope.joinUntil(Instant.now().plusMillis(500)); // 500ms deadline
    scope.throwIfFailed();

    return combine(fraud.get(), bank.get());
}
```

If any subtask takes longer than 500ms, the scope shuts down and all subtasks are cancelled.

## What You Learned

- **Unstructured concurrency** — orphaned threads leak resources when one task fails
- **StructuredTaskScope** — enforces parent-child lifecycle for concurrent tasks
- **ShutdownOnFailure** — all subtasks must succeed; first failure cancels the rest
- **ShutdownOnSuccess** — first successful result wins; others are cancelled
- **fork/join pattern** — fork subtasks, join to wait, then use results
- **Automatic cancellation** — no manual cleanup, no orphaned threads
- **Timeout with joinUntil()** — deadline for the entire concurrent operation

Structured concurrency solves thread leaks. But there's another problem lurking. Each of those 10,000 virtual threads needs context — the request ID, the user's tenant, the trace ID for distributed tracing. With platform threads, you used `ThreadLocal`. With a million virtual threads, that's a million copies of your context object sitting in memory.

---

[← Chapter 2: Your First Virtual Thread](chapter-02-first-virtual-thread.md) | [Chapter 4: Scoped Values →](chapter-04-scoped-values.md)
