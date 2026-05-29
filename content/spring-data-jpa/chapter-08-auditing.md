# Chapter 8: Auditing

[prev: Specifications](chapter-07-specifications.md) | [next: Performance](chapter-09-performance.md)

## JPA Auditing Setup

```java
@Configuration
@EnableJpaAuditing
public class JpaConfig {
}
```

## Auditable Base Entity

```java
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
@Getter @Setter
public abstract class AuditableEntity {

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(updatable = false)
    private String createdBy;

    @LastModifiedBy
    private String updatedBy;
}
```

```java
@Entity
@Table(name = "articles")
@Getter @Setter @NoArgsConstructor
public class Article extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;
}
```

## AuditorAware Implementation

Tells Spring who the current user is:

```java
@Component
public class SecurityAuditorAware implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        return Optional.ofNullable(SecurityContextHolder.getContext().getAuthentication())
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName);
    }
}
```

For non-Spring-Security apps:

```java
@Component
public class SimpleAuditorAware implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        return Optional.of("system"); // or extract from request context
    }
}
```

## Complete Configuration

```java
@Configuration
@EnableJpaAuditing(auditorAwareRef = "securityAuditorAware")
public class JpaConfig {
}
```

Now every entity extending `AuditableEntity` automatically gets timestamps and user tracking on create/update.

## Envers: History Tables

Hibernate Envers automatically creates audit/history tables tracking every change.

### Setup

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.springframework.data:spring-data-envers")
}
```

```java
@Configuration
@EnableJpaRepositories(repositoryFactoryBeanClass = EnversRevisionRepositoryFactoryBean.class)
@EnableJpaAuditing
public class JpaConfig {
}
```

### Annotate Entities

```java
@Entity
@Table(name = "products")
@Audited
@Getter @Setter @NoArgsConstructor
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @NotAudited  // exclude specific fields from audit
    private String internalNotes;
}
```

Envers creates a `products_aud` table and a `revinfo` table tracking all revisions.

### Querying History

```java
public interface ProductRepository extends JpaRepository<Product, Long>,
                                           RevisionRepository<Product, Long, Integer> {
}
```

```java
@Service
public class ProductAuditService {

    private final ProductRepository productRepository;

    public ProductAuditService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Revision<Integer, Product>> getHistory(Long productId) {
        Revisions<Integer, Product> revisions = productRepository.findRevisions(productId);
        return revisions.getContent();
    }

    public Optional<Product> getVersionAt(Long productId, int revisionNumber) {
        return productRepository.findRevision(productId, revisionNumber)
            .map(Revision::getEntity);
    }

    public Optional<Revision<Integer, Product>> getLastChange(Long productId) {
        return productRepository.findLastChangeRevision(productId);
    }
}
```

### Custom Revision Entity

```java
@Entity
@Table(name = "revinfo")
@RevisionEntity(CustomRevisionListener.class)
@Getter @Setter
public class CustomRevisionEntity extends DefaultRevisionEntity {

    @Column(name = "username")
    private String username;
}

public class CustomRevisionListener implements RevisionListener {

    @Override
    public void newRevision(Object revisionEntity) {
        CustomRevisionEntity rev = (CustomRevisionEntity) revisionEntity;
        rev.setUsername(
            Optional.ofNullable(SecurityContextHolder.getContext().getAuthentication())
                .map(Authentication::getName)
                .orElse("system")
        );
    }
}
```

## Exercises

1. Create `AuditableEntity` with all four audit fields and extend it in a `Document` entity
2. Implement `AuditorAware` that returns a hardcoded username, verify `createdBy` is populated
3. Add `@Audited` to an entity, make several updates, and query the revision history
4. Use `@NotAudited` to exclude a field and verify it does not appear in the audit table
5. Create a REST endpoint that returns the full change history of an entity by ID
