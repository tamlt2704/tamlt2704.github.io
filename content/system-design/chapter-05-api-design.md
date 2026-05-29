# Chapter 5: API Design

[← Chapter 4: Message Queues](/blog/system-design/chapter-04-message-queues) | [Chapter 6: Load Balancing →](/blog/system-design/chapter-06-load-balancing)

---

## REST API Design Principles

REST is not a protocol — it's a set of constraints. Most "REST" APIs are actually HTTP APIs. True REST requires HATEOAS, which almost nobody implements.

### Resource Naming

```
GOOD (nouns, plural):
GET    /api/users              → list users
GET    /api/users/123          → get user 123
POST   /api/users              → create user
PUT    /api/users/123          → replace user 123
PATCH  /api/users/123          → partial update user 123
DELETE /api/users/123          → delete user 123

BAD (verbs, actions):
GET    /api/getUsers
POST   /api/createUser
POST   /api/deleteUser/123
```

**Nested resources for relationships:**

```
GET /api/users/123/orders          → orders for user 123
GET /api/users/123/orders/456      → order 456 of user 123
POST /api/users/123/orders         → create order for user 123
```

**When nesting gets too deep, flatten:**

```
BAD:  GET /api/users/123/orders/456/items/789/reviews
GOOD: GET /api/reviews?order_item_id=789
```

---

## HTTP Status Codes That Matter

| Code | Meaning               | When to Use                                           |
| ---- | --------------------- | ----------------------------------------------------- |
| 200  | OK                    | Successful GET, PUT, PATCH                            |
| 201  | Created               | Successful POST (return Location header)              |
| 204  | No Content            | Successful DELETE                                     |
| 400  | Bad Request           | Validation error, malformed input                     |
| 401  | Unauthorized          | Missing or invalid auth token                         |
| 403  | Forbidden             | Valid auth but insufficient permissions               |
| 404  | Not Found             | Resource doesn't exist                                |
| 409  | Conflict              | Duplicate resource, version conflict                  |
| 422  | Unprocessable Entity  | Semantically invalid (valid JSON, bad business logic) |
| 429  | Too Many Requests     | Rate limited                                          |
| 500  | Internal Server Error | Unhandled exception                                   |
| 503  | Service Unavailable   | Overloaded, maintenance                               |

---

## Pagination

Never return unbounded lists. Three approaches:

### Offset-based (simple, common)

```
GET /api/posts?page=2&size=20

Response:
{
  "data": [...],
  "page": 2,
  "size": 20,
  "totalPages": 50,
  "totalElements": 1000
}
```

**Problem:** Slow for large offsets. `OFFSET 100000` still scans 100K rows.

### Cursor-based (scalable)

```
GET /api/posts?cursor=eyJpZCI6MTAwfQ&size=20

Response:
{
  "data": [...],
  "nextCursor": "eyJpZCI6MTIwfQ",
  "hasMore": true
}
```

The cursor encodes the last seen ID. Query becomes `WHERE id > last_id LIMIT 20` — always fast regardless of position.

**When to use which:**

- Offset: Admin panels, small datasets, need "jump to page 50"
- Cursor: Infinite scroll, feeds, large datasets, real-time data

### Keyset Pagination (cursor variant)

```sql
-- Instead of: SELECT * FROM posts ORDER BY created_at OFFSET 1000
-- Use:        SELECT * FROM posts WHERE created_at < '2024-01-15' ORDER BY created_at DESC LIMIT 20
```

---

## Filtering, Sorting, and Field Selection

```
# Filtering
GET /api/products?category=electronics&price_min=100&price_max=500&in_stock=true

# Sorting
GET /api/products?sort=price:asc,rating:desc

# Field selection (reduce payload)
GET /api/users/123?fields=id,name,email

# Search
GET /api/products?q=wireless+headphones
```

---

## API Versioning

| Strategy    | Example                                      | Pros                 | Cons                   |
| ----------- | -------------------------------------------- | -------------------- | ---------------------- |
| URL path    | `/api/v1/users`                              | Clear, easy to route | URL pollution          |
| Header      | `Accept: application/vnd.api+json;version=2` | Clean URLs           | Hidden, harder to test |
| Query param | `/api/users?version=2`                       | Easy to test         | Clutters params        |

**Recommendation:** URL path versioning (`/v1/`, `/v2/`). It's the most explicit and debuggable.

**When to version:**

- Breaking changes (removing fields, changing types)
- NOT for additive changes (new optional fields are backward-compatible)

---

## REST vs gRPC vs GraphQL

| Aspect          | REST                    | gRPC                                | GraphQL                       |
| --------------- | ----------------------- | ----------------------------------- | ----------------------------- |
| Protocol        | HTTP/1.1 or 2           | HTTP/2 (binary)                     | HTTP                          |
| Format          | JSON                    | Protobuf (binary)                   | JSON                          |
| Schema          | OpenAPI (optional)      | .proto (required)                   | SDL (required)                |
| Streaming       | No (WebSocket separate) | Bidirectional streaming             | Subscriptions                 |
| Performance     | Good                    | Excellent (10x smaller payloads)    | Depends on query              |
| Browser support | Native                  | Needs grpc-web proxy                | Native                        |
| Best for        | Public APIs, CRUD       | Internal microservices, low-latency | Mobile apps, flexible queries |

### gRPC — When to Use

```protobuf
// user.proto
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);  // server streaming
}

message GetUserRequest {
  string id = 1;
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
}
```

**Use gRPC when:**

- Service-to-service communication (not browser-facing)
- Need streaming (real-time data feeds)
- Performance critical (binary serialization is 5-10x faster than JSON)
- Strong typing across languages (proto generates code for Java, Go, Python, etc.)

### GraphQL — When to Use

```graphql
# Client asks for exactly what it needs:
query {
  user(id: "123") {
    name
    email
    orders(last: 5) {
      id
      total
      items {
        name
      }
    }
  }
}
```

**Use GraphQL when:**

- Multiple clients need different data shapes (mobile vs web)
- Over-fetching is a problem (REST returns too much data)
- Deeply nested relationships
- Rapid frontend iteration without backend changes

**Don't use GraphQL when:**

- Simple CRUD (overkill)
- File uploads (awkward in GraphQL)
- Caching is critical (harder to cache than REST)

---

## Error Handling

Consistent error format across all endpoints:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "must be a valid email address"
      },
      {
        "field": "age",
        "message": "must be at least 18"
      }
    ],
    "traceId": "abc-123-def"
  }
}
```

**Rules:**

- Always return a machine-readable error code (not just HTTP status)
- Include a human-readable message
- Include field-level details for validation errors
- Include a trace ID for debugging (correlate with server logs)
- Never expose stack traces or internal details in production

---

## Rate Limiting

Protect your API from abuse and ensure fair usage:

```
Headers to return:
X-RateLimit-Limit: 100        # max requests per window
X-RateLimit-Remaining: 45     # requests left
X-RateLimit-Reset: 1640000000 # when window resets (Unix timestamp)
Retry-After: 30               # seconds to wait (on 429)
```

### Algorithms

| Algorithm          | How                                               | Best For                             |
| ------------------ | ------------------------------------------------- | ------------------------------------ |
| **Fixed window**   | Count requests per minute                         | Simple, but burst at window boundary |
| **Sliding window** | Weighted count across windows                     | Smooth, prevents boundary bursts     |
| **Token bucket**   | Tokens refill at fixed rate, each request costs 1 | Allows bursts up to bucket size      |
| **Leaky bucket**   | Requests queue, processed at fixed rate           | Smooth output rate                   |

---

## Idempotency in APIs

For non-idempotent operations (POST), use an idempotency key:

```
POST /api/payments
Idempotency-Key: "unique-request-id-abc123"

{
  "amount": 100,
  "currency": "USD"
}
```

Server behavior:

1. First request: process payment, store result keyed by idempotency key
2. Retry with same key: return stored result without re-processing

This prevents double-charges on network retries.

---

## API Design Checklist

1. **Consistent naming** — plural nouns, kebab-case or snake_case (pick one)
2. **Proper status codes** — don't return 200 for errors
3. **Pagination** — never return unbounded lists
4. **Versioning** — plan for breaking changes
5. **Rate limiting** — protect against abuse
6. **Idempotency** — safe retries for mutations
7. **Error format** — consistent, machine-readable
8. **Documentation** — OpenAPI/Swagger, always up to date
9. **HATEOAS** — optional, but useful for discoverability
10. **Security** — auth on every endpoint, validate all input

---

[Chapter 6: Load Balancing & Reverse Proxies →](/blog/system-design/chapter-06-load-balancing)
