# Chapter 2: Entities

[prev: Setup](chapter-01-setup.md) | [next: Repositories](chapter-03-repositories.md)

## Basic Entity

```java
import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(unique = true)
    private String email;

    // getters and setters
}
```

- `@Entity` marks the class as a JPA entity
- `@Table` customizes the table name (defaults to class name)
- `@Id` marks the primary key
- `@Column` customizes column properties

## ID Generation Strategies

### IDENTITY (auto-increment)

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
```

Database handles auto-increment. Simple but disables JDBC batch inserts (Hibernate needs the ID immediately after insert).

### SEQUENCE (recommended for PostgreSQL)

```java
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "user_seq")
@SequenceGenerator(name = "user_seq", sequenceName = "user_id_seq", allocationSize = 50)
private Long id;
```

Uses database sequences. `allocationSize=50` means Hibernate fetches 50 IDs at once, enabling batch inserts. Best performance for PostgreSQL.

### UUID

```java
@Id
@GeneratedValue(strategy = GenerationType.UUID)
private UUID id;
```

Generates UUIDs without database round-trips. Good for distributed systems but larger index size.

## Column Mapping

```java
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "is_active")
    private boolean active;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Lob
    private byte[] image;
}
```

### Java to SQL Type Mapping

| Java Type        | PostgreSQL Type |
| ---------------- | --------------- |
| String           | VARCHAR(255)    |
| Integer/int      | INTEGER         |
| Long/long        | BIGINT          |
| BigDecimal       | NUMERIC         |
| Boolean/boolean  | BOOLEAN         |
| LocalDate        | DATE            |
| LocalDateTime    | TIMESTAMP       |
| UUID             | UUID            |
| byte[] with @Lob | BYTEA           |

## Enumerations

```java
public enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)  // stores "PENDING", "CONFIRMED", etc.
    @Column(nullable = false)
    private OrderStatus status;
}
```

**Always use `EnumType.STRING`**. `EnumType.ORDINAL` (default) stores the index (0, 1, 2...) which breaks if you reorder or insert enum values.

## Timestamps

### With Hibernate Annotations

```java
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

@Entity
@Table(name = "articles")
public class Article {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
```

`@CreationTimestamp` sets the value on insert. `@UpdateTimestamp` sets it on every update. These are Hibernate-specific (not JPA standard). For the JPA-standard approach, see [Chapter 8: Auditing](chapter-08-auditing.md).

## Lombok with JPA

```java
import lombok.*;
import jakarta.persistence.*;

@Entity
@Table(name = "customers")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString(exclude = "orders")
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @EqualsAndHashCode.Include
    private Long id;

    @Column(nullable = false)
    private String name;

    private String email;
}
```

### Lombok + JPA Rules

1. **Never use `@Data`** — it generates `equals`/`hashCode` using all fields, which breaks with lazy-loaded proxies
2. **Use `@EqualsAndHashCode(onlyExplicitlyIncluded = true)`** and include only the `@Id` field (or a natural key)
3. **Exclude collections from `@ToString`** — prevents accidental lazy-loading
4. **Always include `@NoArgsConstructor`** — JPA requires a no-arg constructor
5. **`@Builder` needs `@AllArgsConstructor`** to work with `@NoArgsConstructor`

## Complete Example: Base Entity

```java
@MappedSuperclass
@Getter
@Setter
@NoArgsConstructor
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
```

```java
@Entity
@Table(name = "employees")
@Getter @Setter @NoArgsConstructor
@EqualsAndHashCode(callSuper = false, onlyExplicitlyIncluded = true)
public class Employee extends BaseEntity {

    @EqualsAndHashCode.Include
    @Column(unique = true, nullable = false)
    private String employeeCode;

    @Column(nullable = false)
    private String firstName;

    @Column(nullable = false)
    private String lastName;

    @Enumerated(EnumType.STRING)
    private Department department;

    @Column(precision = 10, scale = 2)
    private BigDecimal salary;
}

public enum Department {
    ENGINEERING, MARKETING, SALES, HR, FINANCE
}
```

## Exercises

1. Create a `Product` entity with: id (SEQUENCE strategy, allocationSize=50), name, price (BigDecimal), category (enum), description (TEXT), createdAt, updatedAt
2. Create a `BaseEntity` with id and timestamps, then extend it in two entities
3. Write a test that persists an entity and verifies `createdAt` is auto-populated
4. Experiment: change an enum from STRING to ORDINAL, reorder values, and observe what breaks
5. Create an entity with a UUID primary key and verify it works without database sequences
