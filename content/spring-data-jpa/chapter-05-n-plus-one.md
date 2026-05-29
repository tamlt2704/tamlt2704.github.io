# Chapter 5: The N+1 Problem

[prev: Relationships](chapter-04-relationships.md) | [next: Transactions](chapter-06-transactions.md)

## What Is the N+1 Problem?

When you load N entities and each triggers a separate query to fetch a related association:

```java
// 1 query: SELECT * FROM customers
List<Customer> customers = customerRepository.findAll();

// N queries: SELECT * FROM orders WHERE customer_id = ? (one per customer)
for (Customer c : customers) {
    System.out.println(c.getOrders().size());
}
```

With 100 customers, this executes **101 queries** instead of 1 or 2.

## How to Detect

### Enable Hibernate SQL Logging

```yaml
# application.yml
spring:
  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true
logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.orm.jdbc.bind: TRACE
```

### Using p6spy (detailed logging with parameters)

```kotlin
// build.gradle.kts
implementation("com.github.gavlyukovskiy:p6spy-spring-boot-starter:1.9.1")
```

```properties
# src/main/resources/spy.properties
appender=com.p6spy.engine.spy.appender.Slf4JLogger
logMessageFormat=com.p6spy.engine.spy.appender.MultiLineFormat
```

p6spy shows the actual SQL with bound parameter values, making N+1 issues obvious.

## Solution 1: JOIN FETCH (JPQL)

```java
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    @Query("SELECT c FROM Customer c JOIN FETCH c.orders WHERE c.active = true")
    List<Customer> findActiveWithOrders();
}
```

One query with a JOIN. Best when you always need the association.

**Limitation**: Cannot use JOIN FETCH with `Pageable` (Hibernate fetches all results in memory then paginates). Use `@EntityGraph` or a two-query approach instead.

## Solution 2: @EntityGraph

```java
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    @EntityGraph(attributePaths = {"orders"})
    List<Customer> findByActiveTrue();

    @EntityGraph(attributePaths = {"orders", "orders.items"})
    Optional<Customer> findWithOrdersById(Long id);
}
```

Overrides the fetch type for a specific query without writing JPQL. Works with derived query methods and pagination.

### Named Entity Graph (on the entity)

```java
@Entity
@NamedEntityGraph(
    name = "Customer.withOrders",
    attributeNodes = @NamedAttributeNode("orders")
)
public class Customer {
    // ...
}
```

```java
@EntityGraph("Customer.withOrders")
List<Customer> findAll();
```

## Solution 3: @BatchSize

```java
@Entity
public class Customer {

    @OneToMany(mappedBy = "customer")
    @BatchSize(size = 25)
    private List<Order> orders = new ArrayList<>();
}
```

When Hibernate loads orders for one customer, it loads orders for up to 25 customers in a single `WHERE customer_id IN (?, ?, ...)` query. Turns N+1 into N/25+1.

Global setting:

```yaml
spring:
  jpa:
    properties:
      hibernate:
        default_batch_fetch_size: 25
```

**Best for**: cases where you sometimes access the collection but not always. Low-effort fix.

## Solution 4: DTO Projections

Avoid loading entities entirely — fetch only the data you need:

```java
public record CustomerOrderCount(Long customerId, String name, long orderCount) {}

public interface CustomerRepository extends JpaRepository<Customer, Long> {

    @Query("SELECT new com.example.dto.CustomerOrderCount(c.id, c.name, COUNT(o)) " +
           "FROM Customer c LEFT JOIN c.orders o GROUP BY c.id, c.name")
    List<CustomerOrderCount> findCustomerOrderCounts();
}
```

No N+1 possible — single query, no entity management overhead.

## When to Use Each

| Solution       | Best For                                   | Trade-off                                     |
| -------------- | ------------------------------------------ | --------------------------------------------- |
| JOIN FETCH     | Always need the association, no pagination | Cartesian product with multiple collections   |
| @EntityGraph   | Selective eager loading per query          | Same as JOIN FETCH                            |
| @BatchSize     | Sometimes access collection, many parents  | Still multiple queries (but fewer)            |
| DTO Projection | Read-only views, reports                   | No entity features (dirty checking, lazy nav) |

### Multiple Collections

Never JOIN FETCH two collections simultaneously — it creates a Cartesian product:

```java
// BAD: Cartesian product
@Query("SELECT c FROM Customer c JOIN FETCH c.orders JOIN FETCH c.addresses")

// GOOD: Two separate queries
@EntityGraph(attributePaths = {"orders"})
List<Customer> findAllWithOrders();

@EntityGraph(attributePaths = {"addresses"})
List<Customer> findAllWithAddresses();
```

Or use `@BatchSize` on both collections.

## Exercises

1. Create Customer with OneToMany orders. Load all customers and access orders — count the SQL queries
2. Fix it with `JOIN FETCH` and verify only 1 query executes
3. Apply `@BatchSize(size = 10)` instead and observe the batched IN queries
4. Create a DTO projection that returns customer name + order count in a single query
5. Try `@EntityGraph` with pagination and verify it works (unlike JOIN FETCH)
