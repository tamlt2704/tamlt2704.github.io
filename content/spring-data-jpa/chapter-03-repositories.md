# Chapter 3: Repositories

[prev: Entities](chapter-02-entities.md) | [next: Relationships](chapter-04-relationships.md)

## Repository Hierarchy

```
Repository (marker)
  └── CrudRepository (CRUD operations)
       └── ListCrudRepository (returns List instead of Iterable)
            └── JpaRepository (JPA-specific: flush, batch, example queries)
```

```java
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
}
```

This gives you: `save`, `findById`, `findAll`, `deleteById`, `count`, `existsById`, `flush`, `saveAll`, and more — with zero implementation.

## Derived Query Methods

Spring Data generates queries from method names:

```java
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);

    List<User> findByNameAndActive(String name, boolean active);

    List<User> findByNameContaining(String fragment);

    List<User> findByAgeGreaterThan(int age);

    List<User> findByStatusIn(List<OrderStatus> statuses);

    List<User> findByEmailIsNotNull();

    List<User> findByActiveOrderByNameAsc(boolean active);

    List<User> findTop5ByOrderByCreatedAtDesc();

    Optional<User> findFirstByOrderByIdDesc();

    List<User> findDistinctByDepartment(Department dept);

    long countByActive(boolean active);

    boolean existsByEmail(String email);

    void deleteByEmail(String email);
}
```

### Keyword Reference

| Keyword          | Example                   | SQL                       |
| ---------------- | ------------------------- | ------------------------- |
| And              | findByNameAndAge          | WHERE name=? AND age=?    |
| Or               | findByNameOrAge           | WHERE name=? OR age=?     |
| Between          | findByAgeBetween          | WHERE age BETWEEN ? AND ? |
| LessThan         | findByAgeLessThan         | WHERE age < ?             |
| GreaterThanEqual | findByAgeGreaterThanEqual | WHERE age >= ?            |
| Like             | findByNameLike            | WHERE name LIKE ?         |
| Containing       | findByNameContaining      | WHERE name LIKE %?%       |
| StartingWith     | findByNameStartingWith    | WHERE name LIKE ?%        |
| IsNull           | findByEmailIsNull         | WHERE email IS NULL       |
| In               | findByStatusIn            | WHERE status IN (?)       |
| True/False       | findByActiveTrue          | WHERE active = true       |

## @Query — JPQL and Native SQL

```java
public interface OrderRepository extends JpaRepository<Order, Long> {

    // JPQL (entity-based, portable)
    @Query("SELECT o FROM Order o WHERE o.status = :status AND o.total > :minTotal")
    List<Order> findExpensiveByStatus(@Param("status") OrderStatus status,
                                     @Param("minTotal") BigDecimal minTotal);

    // Native SQL (database-specific)
    @Query(value = "SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '7 days'",
           nativeQuery = true)
    List<Order> findRecentOrders();

    // Projection to DTO
    @Query("SELECT new com.example.dto.OrderSummary(o.id, o.status, o.total) " +
           "FROM Order o WHERE o.customer.id = :customerId")
    List<OrderSummary> findSummariesByCustomer(@Param("customerId") Long customerId);
}
```

## @Modifying — Update and Delete Queries

```java
public interface UserRepository extends JpaRepository<User, Long> {

    @Modifying
    @Query("UPDATE User u SET u.active = false WHERE u.lastLoginAt < :cutoff")
    int deactivateInactiveUsers(@Param("cutoff") LocalDateTime cutoff);

    @Modifying
    @Query("DELETE FROM User u WHERE u.active = false AND u.createdAt < :cutoff")
    int deleteOldInactiveUsers(@Param("cutoff") LocalDateTime cutoff);
}
```

`@Modifying` queries must be called within a `@Transactional` context. They return the number of affected rows. Add `clearAutomatically = true` if you need the persistence context refreshed after the update.

## Pagination and Sorting

```java
public interface ProductRepository extends JpaRepository<Product, Long> {

    Page<Product> findByCategory(Category category, Pageable pageable);

    List<Product> findByActive(boolean active, Sort sort);
}
```

```java
@Service
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public Page<Product> getProducts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("name").ascending());
        return productRepository.findByCategory(Category.ELECTRONICS, pageable);
    }

    public List<Product> getSorted() {
        Sort sort = Sort.by(Sort.Order.desc("price"), Sort.Order.asc("name"));
        return productRepository.findByActive(true, sort);
    }
}
```

### Page vs Slice

|                      | Page                 | Slice           |
| -------------------- | -------------------- | --------------- |
| Total count query    | Yes (extra query)    | No              |
| `getTotalElements()` | Available            | Not available   |
| `getTotalPages()`    | Available            | Not available   |
| `hasNext()`          | Available            | Available       |
| Performance          | Slower (count query) | Faster          |
| Use case             | UI with page numbers | Infinite scroll |

```java
// Slice — no count query, fetches size+1 to check hasNext
Slice<Product> findByCategory(Category category, Pageable pageable);
```

## Exercises

1. Create a `ProductRepository` with derived methods: findByCategory, findByPriceLessThan, findByNameContainingIgnoreCase
2. Add a `@Query` method that finds products with price above average
3. Implement pagination: return page 0 with 10 items sorted by price descending
4. Write a `@Modifying` query that increases all product prices by 10%
5. Compare `Page` vs `Slice` — call both and observe the SQL logs (enable `show-sql: true`)
