# Chapter 10: Production Patterns

[prev: Performance](chapter-09-performance.md) | [Overview](chapter-00-overview.md)

## Soft Delete

Never physically delete rows — mark them as deleted instead.

```java
@Entity
@Table(name = "customers")
@SQLDelete(sql = "UPDATE customers SET deleted = true WHERE id = ?")
@Where(clause = "deleted = false")
@Getter @Setter @NoArgsConstructor
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String email;

    @Column(nullable = false)
    private boolean deleted = false;

    private LocalDateTime deletedAt;
}
```

Now `customerRepository.delete(customer)` executes UPDATE instead of DELETE, and all queries automatically exclude deleted rows.

### Querying Deleted Records

```java
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    // This respects @Where — only returns non-deleted
    List<Customer> findByName(String name);

    // Native query bypasses @Where
    @Query(value = "SELECT * FROM customers WHERE id = :id", nativeQuery = true)
    Optional<Customer> findByIdIncludingDeleted(@Param("id") Long id);
}
```

## Multi-Tenancy

### Schema-per-tenant

```java
public class TenantIdentifierResolver implements CurrentTenantIdentifierResolver<String> {

    @Override
    public String resolveCurrentTenantIdentifier() {
        return TenantContext.getCurrentTenant(); // from ThreadLocal or request header
    }

    @Override
    public boolean validateExistingCurrentSessions() {
        return true;
    }
}

public class SchemaMultiTenantConnectionProvider implements MultiTenantConnectionProvider<String> {

    private final DataSource dataSource;

    public SchemaMultiTenantConnectionProvider(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public Connection getAnyConnection() throws SQLException {
        return dataSource.getConnection();
    }

    @Override
    public Connection getConnection(String tenantId) throws SQLException {
        Connection conn = dataSource.getConnection();
        conn.setSchema(tenantId);
        return conn;
    }

    @Override
    public void releaseAnyConnection(Connection connection) throws SQLException {
        connection.close();
    }

    @Override
    public void releaseConnection(String tenantId, Connection connection) throws SQLException {
        connection.setSchema("public");
        connection.close();
    }
}
```

### Discriminator Column (shared table)

```java
@Entity
@Table(name = "documents")
@Getter @Setter @NoArgsConstructor
public class Document {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String tenantId;

    private String title;
    private String content;
}
```

```java
@Aspect
@Component
public class TenantFilter {

    @PersistenceContext
    private EntityManager em;

    @Before("execution(* com.example.repository.*.*(..))")
    public void enableTenantFilter() {
        Session session = em.unwrap(Session.class);
        session.enableFilter("tenantFilter")
            .setParameter("tenantId", TenantContext.getCurrentTenant());
    }
}
```

## DTO Projections

### Interface-Based Projection

```java
public interface OrderSummary {
    Long getId();
    OrderStatus getStatus();
    BigDecimal getTotal();
    String getCustomerName();
}

public interface OrderRepository extends JpaRepository<Order, Long> {

    @Query("SELECT o.id as id, o.status as status, o.total as total, " +
           "c.name as customerName FROM Order o JOIN o.customer c WHERE c.id = :customerId")
    List<OrderSummary> findSummariesByCustomer(@Param("customerId") Long customerId);
}
```

Spring Data creates a proxy implementing the interface. Only selected columns are fetched.

### Class-Based Projection (Record)

```java
public record OrderDetail(Long id, OrderStatus status, BigDecimal total, String customerName) {}

public interface OrderRepository extends JpaRepository<Order, Long> {

    @Query("SELECT new com.example.dto.OrderDetail(o.id, o.status, o.total, c.name) " +
           "FROM Order o JOIN o.customer c WHERE o.id = :id")
    Optional<OrderDetail> findDetailById(@Param("id") Long id);
}
```

### When to Use

| Approach                | Use Case                                          |
| ----------------------- | ------------------------------------------------- |
| Entity                  | Need to modify data, navigate relationships       |
| Interface projection    | Read-only views, subset of columns                |
| Record/class projection | Read-only, need constructor validation, immutable |

## Custom Repository Implementation

When Spring Data methods are not enough:

```java
// 1. Define custom interface
public interface OrderRepositoryCustom {
    List<Order> findWithComplexLogic(OrderFilter filter);
}

// 2. Implement it
public class OrderRepositoryCustomImpl implements OrderRepositoryCustom {

    @PersistenceContext
    private EntityManager em;

    @Override
    public List<Order> findWithComplexLogic(OrderFilter filter) {
        CriteriaBuilder cb = em.getCriteriaBuilder();
        CriteriaQuery<Order> cq = cb.createQuery(Order.class);
        Root<Order> root = cq.from(Order.class);

        List<Predicate> predicates = new ArrayList<>();
        // build complex query...

        cq.where(predicates.toArray(new Predicate[0]));
        return em.createQuery(cq).getResultList();
    }
}

// 3. Extend in main repository
public interface OrderRepository extends JpaRepository<Order, Long>, OrderRepositoryCustom {
}
```

The implementation class **must** be named `{RepositoryInterface}Impl` (convention over configuration).

## Testing with @DataJpaTest + Testcontainers

Test against a real PostgreSQL database:

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("org.testcontainers:junit-jupiter")
    testImplementation("org.testcontainers:postgresql")
    testImplementation("org.springframework.boot:spring-boot-testcontainers")
}
```

```java
@DataJpaTest
@Testcontainers
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class OrderRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void shouldFindOrdersByStatus() {
        Order order = new Order();
        order.setStatus(OrderStatus.PENDING);
        order.setTotal(new BigDecimal("99.99"));
        orderRepository.save(order);

        List<Order> pending = orderRepository.findByStatus(OrderStatus.PENDING);

        assertThat(pending).hasSize(1);
        assertThat(pending.get(0).getTotal()).isEqualByComparingTo("99.99");
    }
}
```

### Reusable Container with Spring Boot 3.1+

```java
@TestConfiguration(proxyBeanMethods = false)
public class TestcontainersConfig {

    @Bean
    @ServiceConnection
    public PostgreSQLContainer<?> postgres() {
        return new PostgreSQLContainer<>("postgres:16");
    }
}
```

```java
@DataJpaTest
@Import(TestcontainersConfig.class)
class ProductRepositoryTest {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void shouldSaveAndRetrieve() {
        Product product = new Product();
        product.setName("Widget");
        product.setPrice(new BigDecimal("19.99"));

        Product saved = productRepository.save(product);

        assertThat(saved.getId()).isNotNull();
        assertThat(productRepository.findById(saved.getId()))
            .isPresent()
            .get()
            .extracting(Product::getName)
            .isEqualTo("Widget");
    }
}
```

## Exercises

1. Implement soft delete on a `Post` entity with `@SQLDelete` and `@Where`, verify `findAll()` excludes deleted posts
2. Create an interface-based projection for a `UserSummary` (id, name, email only) and verify only those columns are selected
3. Implement a custom repository method using `EntityManager` and Criteria API
4. Set up Testcontainers with PostgreSQL and write a test that verifies a Flyway migration runs correctly
5. Create a record-based DTO projection and compare the SQL output with loading the full entity
