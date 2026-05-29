# Chapter 7: Microservices Architecture

[← Chapter 6: Load Balancing](/blog/system-design/chapter-06-load-balancing) | [Chapter 8: Consistency →](/blog/system-design/chapter-08-consistency)

---

## Monolith vs Microservices

```
MONOLITH:                          MICROSERVICES:
┌─────────────────────────┐        ┌─────────┐ ┌─────────┐ ┌─────────┐
│  ┌─────┐ ┌─────┐       │        │  User   │ │  Order  │ │ Payment │
│  │User │ │Order│        │        │ Service │ │ Service │ │ Service │
│  └─────┘ └─────┘       │        └────┬────┘ └────┬────┘ └────┬────┘
│  ┌─────┐ ┌─────┐       │             │           │           │
│  │Pay  │ │Notif│        │        ┌────┴────┐ ┌───┴────┐ ┌───┴────┐
│  └─────┘ └─────┘       │        │  UserDB │ │OrderDB │ │ PayDB  │
│         ONE DEPLOY      │        └─────────┘ └────────┘ └────────┘
│         ONE DATABASE    │
└─────────────────────────┘
```

| Aspect     | Monolith                  | Microservices                           |
| ---------- | ------------------------- | --------------------------------------- |
| Deployment | All or nothing            | Independent per service                 |
| Scaling    | Scale everything together | Scale hot services only                 |
| Tech stack | One language/framework    | Polyglot (each service picks best tool) |
| Data       | Shared database           | Database per service                    |
| Complexity | In the code               | In the infrastructure                   |
| Team size  | Works for < 10 devs       | Needed for 50+ devs                     |
| Debugging  | Stack trace               | Distributed tracing                     |
| Latency    | In-process calls (ns)     | Network calls (ms)                      |

**Start with a monolith.** Split into microservices when you have a clear reason:

- Team is too large to work on one codebase
- Different parts need different scaling
- Different parts need different deployment cadences
- Clear domain boundaries exist

---

## Service Boundaries — How to Split

### Domain-Driven Design (DDD)

Split by **bounded context** — each service owns a business domain:

```
E-commerce bounded contexts:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Catalog    │  │   Ordering   │  │   Shipping   │
│              │  │              │  │              │
│ - Products   │  │ - Cart       │  │ - Tracking   │
│ - Categories │  │ - Orders     │  │ - Carriers   │
│ - Search     │  │ - Payments   │  │ - Labels     │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Rules for good boundaries:**

- High cohesion within a service (related things together)
- Low coupling between services (minimal dependencies)
- Each service owns its data (no shared databases)
- A service can be rewritten without affecting others

### Anti-patterns

```
BAD: "Distributed monolith"
- Services share a database
- Changing one service requires changing others
- Services call each other synchronously in chains
- You have all the complexity of microservices with none of the benefits

BAD: "Nano-services"
- Too many tiny services (one per CRUD entity)
- Network overhead dominates
- Impossible to reason about
```

---

## Inter-Service Communication

### Synchronous (Request-Response)

```
┌──────────┐  HTTP/gRPC  ┌──────────┐
│ Service A│────────────▶│ Service B│
│          │◀────────────│          │
└──────────┘  response   └──────────┘
```

**Pros:** Simple, immediate response.
**Cons:** Tight coupling, cascading failures, latency accumulates.

### Asynchronous (Event-Driven)

```
┌──────────┐   event    ┌─────────┐   event    ┌──────────┐
│ Service A│───────────▶│  Kafka  │───────────▶│ Service B│
└──────────┘            └─────────┘            └──────────┘
```

**Pros:** Loose coupling, resilient, services can be offline.
**Cons:** Eventual consistency, harder to debug, complex error handling.

### When to Use Which

| Scenario                                   | Pattern                               |
| ------------------------------------------ | ------------------------------------- |
| Need immediate response (get user profile) | Sync (HTTP/gRPC)                      |
| Fire-and-forget (send notification)        | Async (event)                         |
| Long-running process (generate report)     | Async (command + callback)            |
| Data replication across services           | Async (event sourcing)                |
| Orchestrated workflow (order saga)         | Async (choreography or orchestration) |

---

## Service Discovery

How does Service A find Service B's address?

### Client-Side Discovery

```
┌──────────┐     ┌──────────────┐
│ Service A│────▶│   Registry   │  "Where is Service B?"
└─────┬────┘     │ (Consul/Eureka)│  → "10.0.0.5:8080, 10.0.0.6:8080"
      │          └──────────────┘
      │
      └──────────▶ 10.0.0.5:8080 (Service B)
```

### Server-Side Discovery

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│ Service A│────▶│ Load Balancer│────▶│ Service B│
└──────────┘     │ (knows all   │     └──────────┘
                 │  instances)  │
                 └──────────────┘
```

**In Kubernetes:** Built-in via DNS. `http://order-service:8080` resolves to the service's ClusterIP.

---

## API Gateway

Single entry point for all external clients:

```
┌──────────┐         ┌─────────────┐
│  Mobile  │────────▶│             │──▶ User Service
│  Client  │         │   API       │──▶ Order Service
└──────────┘         │  Gateway    │──▶ Product Service
┌──────────┐         │             │──▶ Payment Service
│   Web    │────────▶│ (Kong,      │
│  Client  │         │  Zuul,      │
└──────────┘         │  AWS APIGW) │
                     └─────────────┘
```

**Responsibilities:**

- Authentication/authorization
- Rate limiting
- Request routing
- Protocol translation (REST → gRPC)
- Response aggregation (BFF pattern)
- Logging and monitoring

---

## Resilience Patterns

### Circuit Breaker

Prevent cascading failures when a downstream service is down:

```
States:
CLOSED ──(failures > threshold)──▶ OPEN ──(timeout)──▶ HALF-OPEN
  │                                  │                      │
  │ (requests pass through)          │ (requests fail fast) │ (test one request)
  │                                  │                      │
  └──────────────────────────────────┘                      │
                                                            │
  ◀──(test succeeds)── CLOSED ◀─────────────────────────────┘
  ◀──(test fails)───── OPEN ◀──────────────────────────────┘
```

```java
// Using Resilience4j
@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
public PaymentResult processPayment(PaymentRequest request) {
    return paymentClient.charge(request);
}

public PaymentResult paymentFallback(PaymentRequest request, Exception e) {
    // Queue for retry, return pending status
    return PaymentResult.pending("Payment queued for processing");
}
```

### Retry with Exponential Backoff

```java
@Retry(name = "paymentService", fallbackMethod = "paymentFallback")
// Retry config: maxAttempts=3, waitDuration=1s, multiplier=2
// Attempt 1: immediate
// Attempt 2: wait 1s
// Attempt 3: wait 2s
// Then fallback
```

### Bulkhead

Isolate failures — don't let one slow service consume all threads:

```
Thread Pool Bulkhead:
┌─────────────────────────────────────┐
│  Payment threads: [■][■][□][□][□]   │  ← max 5 threads
│  Order threads:   [■][■][■][□][□]   │  ← max 5 threads
│  User threads:    [■][□][□][□][□]   │  ← max 5 threads
└─────────────────────────────────────┘

If Payment service is slow → only payment threads are exhausted
Order and User services continue working normally
```

### Timeout

Always set timeouts. A missing timeout = potential thread leak:

```java
RestClient client = RestClient.builder()
    .connectTimeout(Duration.ofSeconds(2))
    .readTimeout(Duration.ofSeconds(5))
    .build();
```

---

## Distributed Tracing

Follow a request across multiple services:

```
Request: GET /api/orders/123

Trace ID: abc-123
├── Span 1: API Gateway (2ms)
├── Span 2: Order Service (15ms)
│   ├── Span 3: DB query (5ms)
│   └── Span 4: Payment Service call (8ms)
│       └── Span 5: Payment DB query (3ms)
└── Span 6: Response serialization (1ms)

Total: 31ms
```

**Tools:** Jaeger, Zipkin, AWS X-Ray, OpenTelemetry (standard).

**Implementation:** Propagate trace ID in headers:

```
X-Trace-Id: abc-123
X-Span-Id: span-4
X-Parent-Span-Id: span-2
```

---

## Data Management

### Database per Service

Each service owns its data. No direct DB access from other services.

```
Order Service ──owns──▶ orders_db
User Service  ──owns──▶ users_db
Payment Service ──owns──▶ payments_db

Order Service needs user name?
  → Call User Service API (not query users_db directly)
```

### Saga Pattern for Distributed Transactions

No ACID across services. Use compensating transactions:

```
Create Order Saga:
1. Order Service:   CREATE order (status=PENDING)
2. Payment Service: CHARGE card
   ├── Success → 3. Inventory Service: RESERVE stock
   │                ├── Success → Order Service: CONFIRM order
   │                └── Failure → Payment Service: REFUND
   └── Failure → Order Service: CANCEL order
```

**Choreography** (event-driven, no coordinator):

- Each service listens for events and reacts
- Simple but hard to track overall progress

**Orchestration** (central coordinator):

- A saga orchestrator tells each service what to do
- Easier to understand, single point of failure

---

## When NOT to Use Microservices

- Team < 10 people
- Startup finding product-market fit (speed > architecture)
- Simple CRUD application
- No clear domain boundaries
- Can't afford the infrastructure complexity (observability, CI/CD per service)

**The cost of microservices:**

- Distributed tracing, logging, monitoring
- Service mesh / API gateway
- CI/CD pipeline per service
- Network latency between services
- Data consistency challenges
- Operational complexity (deploy 20 services vs 1)

---

[Chapter 8: Consistency & Distributed Systems →](/blog/system-design/chapter-08-consistency)
