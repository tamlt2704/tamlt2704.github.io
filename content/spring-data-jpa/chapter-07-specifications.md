# Chapter 7: Specifications and Dynamic Queries

[prev: Transactions](chapter-06-transactions.md) | [next: Auditing](chapter-08-auditing.md)

## The Problem

Search endpoints with many optional filters:

```
GET /products?category=ELECTRONICS&minPrice=100&maxPrice=500&name=phone&inStock=true
```

You cannot create a derived query method for every combination. Specifications let you build queries dynamically.

## JpaSpecificationExecutor

```java
public interface ProductRepository extends JpaRepository<Product, Long>,
                                           JpaSpecificationExecutor<Product> {
}
```

This adds: `findAll(Specification)`, `findAll(Specification, Pageable)`, `count(Specification)`, `exists(Specification)`.

## Writing Specifications

```java
public class ProductSpecs {

    public static Specification<Product> hasCategory(Category category) {
        return (root, query, cb) -> cb.equal(root.get("category"), category);
    }

    public static Specification<Product> priceBetween(BigDecimal min, BigDecimal max) {
        return (root, query, cb) -> cb.between(root.get("price"), min, max);
    }

    public static Specification<Product> nameContains(String name) {
        return (root, query, cb) ->
            cb.like(cb.lower(root.get("name")), "%" + name.toLowerCase() + "%");
    }

    public static Specification<Product> isInStock() {
        return (root, query, cb) -> cb.greaterThan(root.get("stockQuantity"), 0);
    }
}
```

## Combining Specifications

```java
@Service
public class ProductSearchService {

    private final ProductRepository productRepository;

    public ProductSearchService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public Page<Product> search(ProductFilter filter, Pageable pageable) {
        Specification<Product> spec = Specification.where(null);

        if (filter.category() != null) {
            spec = spec.and(ProductSpecs.hasCategory(filter.category()));
        }
        if (filter.minPrice() != null && filter.maxPrice() != null) {
            spec = spec.and(ProductSpecs.priceBetween(filter.minPrice(), filter.maxPrice()));
        }
        if (filter.name() != null) {
            spec = spec.and(ProductSpecs.nameContains(filter.name()));
        }
        if (filter.inStockOnly()) {
            spec = spec.and(ProductSpecs.isInStock());
        }

        return productRepository.findAll(spec, pageable);
    }
}

public record ProductFilter(
    Category category,
    BigDecimal minPrice,
    BigDecimal maxPrice,
    String name,
    boolean inStockOnly
) {}
```

## Reusable Filter Pattern

A generic approach for building specs from filter objects:

```java
public class SpecBuilder<T> {

    private Specification<T> spec = Specification.where(null);

    public SpecBuilder<T> and(boolean condition, Supplier<Specification<T>> specSupplier) {
        if (condition) {
            spec = spec.and(specSupplier.get());
        }
        return this;
    }

    public Specification<T> build() {
        return spec;
    }
}
```

```java
public Page<Product> search(ProductFilter filter, Pageable pageable) {
    Specification<Product> spec = new SpecBuilder<Product>()
        .and(filter.category() != null, () -> ProductSpecs.hasCategory(filter.category()))
        .and(filter.name() != null, () -> ProductSpecs.nameContains(filter.name()))
        .and(filter.inStockOnly(), ProductSpecs::isInStock)
        .build();

    return productRepository.findAll(spec, pageable);
}
```

## Specifications with Joins

```java
public class OrderSpecs {

    public static Specification<Order> customerNameContains(String name) {
        return (root, query, cb) -> {
            Join<Order, Customer> customer = root.join("customer", JoinType.INNER);
            return cb.like(cb.lower(customer.get("name")), "%" + name.toLowerCase() + "%");
        };
    }

    public static Specification<Order> hasItemWithProduct(Long productId) {
        return (root, query, cb) -> {
            Join<Order, OrderItem> items = root.join("items", JoinType.INNER);
            return cb.equal(items.get("product").get("id"), productId);
        };
    }
}
```

## Criteria API (Lower Level)

Specifications are built on the Criteria API. For complex queries you can use it directly:

```java
@Repository
public class ProductSearchDao {

    @PersistenceContext
    private EntityManager em;

    public List<Product> search(ProductFilter filter) {
        CriteriaBuilder cb = em.getCriteriaBuilder();
        CriteriaQuery<Product> cq = cb.createQuery(Product.class);
        Root<Product> root = cq.from(Product.class);

        List<Predicate> predicates = new ArrayList<>();

        if (filter.category() != null) {
            predicates.add(cb.equal(root.get("category"), filter.category()));
        }
        if (filter.minPrice() != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("price"), filter.minPrice()));
        }

        cq.where(predicates.toArray(new Predicate[0]));
        cq.orderBy(cb.asc(root.get("name")));

        return em.createQuery(cq).getResultList();
    }
}
```

## QueryDSL Integration

QueryDSL provides type-safe queries with generated Q-classes.

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.querydsl:querydsl-jpa:5.1.0:jakarta")
    annotationProcessor("com.querydsl:querydsl-apt:5.1.0:jakarta")
    annotationProcessor("jakarta.persistence:jakarta.persistence-api")
}
```

```java
public interface ProductRepository extends JpaRepository<Product, Long>,
                                           QuerydslPredicateExecutor<Product> {
}
```

```java
@Service
public class ProductSearchService {

    private final ProductRepository productRepository;

    public ProductSearchService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public Page<Product> search(ProductFilter filter, Pageable pageable) {
        QProduct product = QProduct.product;
        BooleanBuilder builder = new BooleanBuilder();

        if (filter.category() != null) {
            builder.and(product.category.eq(filter.category()));
        }
        if (filter.minPrice() != null) {
            builder.and(product.price.goe(filter.minPrice()));
        }
        if (filter.name() != null) {
            builder.and(product.name.containsIgnoreCase(filter.name()));
        }

        return productRepository.findAll(builder, pageable);
    }
}
```

QueryDSL advantages: compile-time type safety, IDE autocomplete, readable syntax. Downside: requires annotation processing setup and generated classes.

## Exercises

1. Create `ProductSpecs` with: hasCategory, priceBetween, nameContains, isActive
2. Build a search endpoint that combines specs based on optional query parameters
3. Implement the `SpecBuilder` utility and refactor your search to use it
4. Write a specification with a JOIN to filter orders by customer name
5. (Optional) Set up QueryDSL and rewrite the same search with `BooleanBuilder`
