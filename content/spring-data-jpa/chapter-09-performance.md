# Chapter 9: Performance

[prev: Auditing](chapter-08-auditing.md) | [next: Production Patterns](chapter-10-patterns.md)

## Batch Inserts

By default, Hibernate inserts one row at a time. Enable batching:

```yaml
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 50
        order_inserts: true
        order_updates: true
```

**Important**: `GenerationType.IDENTITY` disables batching because Hibernate needs the generated ID immediately. Use `SEQUENCE` with a high `allocationSize`:

```java
@Entity
@Table(name = "events")
@Getter @Setter @NoArgsConstructor
public class Event {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "event_seq")
    @SequenceGenerator(name = "event_seq", sequenceName = "event_id_seq", allocationSize = 50)
    private Long id;

    private String name;
    private LocalDateTime occurredAt;
}
```

### Batch Insert Service

```java
@Service
public class EventBatchService {

    @PersistenceContext
    private EntityManager em;

    @Transactional
    public void batchInsert(List<Event> events) {
        for (int i = 0; i < events.size(); i++) {
            em.persist(events.get(i));
            if (i % 50 == 0 && i > 0) {
                em.flush();
                em.clear(); // release memory
            }
        }
    }
}
```

## Second-Level Cache

Hibernate's first-level cache is per-session. The second-level (L2) cache is shared across sessions.

### Ehcache Setup

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.hibernate.orm:hibernate-jcache")
    implementation("org.ehcache:ehcache:3.10.8:jakarta")
}
```

```yaml
spring:
  jpa:
    properties:
      hibernate:
        cache:
          use_second_level_cache: true
          region.factory_class: jcache
        javax:
          cache:
            provider: org.ehcache.jsr107.EhcacheCachingProvider
```

```xml
<!-- src/main/resources/ehcache.xml -->
<config xmlns="http://www.ehcache.org/v3">
  <cache alias="com.example.entity.Product">
    <expiry>
      <ttl unit="minutes">60</ttl>
    </expiry>
    <heap unit="entries">1000</heap>
  </cache>
</config>
```

### Cacheable Entity

```java
@Entity
@Table(name = "products")
@Cacheable
@org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
@Getter @Setter @NoArgsConstructor
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private BigDecimal price;
}
```

Cache strategies:

- `READ_ONLY` — immutable data, best performance
- `READ_WRITE` — mutable data, uses soft locks
- `NONSTRICT_READ_WRITE` — eventual consistency, no locks
- `TRANSACTIONAL` — full JTA transaction support

### Query Cache

```java
@QueryHints(@QueryHint(name = "org.hibernate.cacheable", value = "true"))
List<Product> findByCategory(Category category);
```

Only use query cache for queries that run frequently with the same parameters and on data that changes rarely.

## Read Replicas Routing

Route read-only transactions to replicas:

```java
public class RoutingDataSource extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
            ? DataSourceType.REPLICA
            : DataSourceType.PRIMARY;
    }
}

public enum DataSourceType {
    PRIMARY, REPLICA
}
```

```java
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource dataSource(
            @Qualifier("primaryDataSource") DataSource primary,
            @Qualifier("replicaDataSource") DataSource replica) {

        RoutingDataSource routing = new RoutingDataSource();
        Map<Object, Object> targets = Map.of(
            DataSourceType.PRIMARY, primary,
            DataSourceType.REPLICA, replica
        );
        routing.setTargetDataSources(targets);
        routing.setDefaultTargetDataSource(primary);
        return routing;
    }

    @Bean
    @ConfigurationProperties("spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.replica")
    public DataSource replicaDataSource() {
        return DataSourceBuilder.create().build();
    }
}
```

Now `@Transactional(readOnly = true)` automatically routes to the replica.

## HikariCP Tuning

HikariCP is the default connection pool in Spring Boot.

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20 # max connections (default 10)
      minimum-idle: 5 # min idle connections
      idle-timeout: 300000 # 5 min idle before removal
      connection-timeout: 30000 # 30s wait for connection
      max-lifetime: 1800000 # 30 min max connection age
      leak-detection-threshold: 60000 # warn if connection held > 60s
```

**Sizing formula**: `pool_size = (core_count * 2) + effective_spindle_count`. For most apps, 10-20 is sufficient. Too many connections can overwhelm the database.

## Flyway Best Practices

```
src/main/resources/db/migration/
├── V1__initial_schema.sql
├── V2__add_products_table.sql
├── V3__add_index_on_email.sql
└── R__refresh_materialized_views.sql  (repeatable migration)
```

Rules:

1. **Never modify an applied migration** — create a new one
2. **One concern per migration** — easier to debug failures
3. **Use transactions** — PostgreSQL supports transactional DDL
4. **Test migrations** — run against a copy of production data
5. **Version naming** — use timestamps in teams: `V20240101120000__description.sql`

```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true # for existing databases
    validate-on-migrate: true # verify checksums
    out-of-order: false # strict ordering in production
```

## Exercises

1. Enable batch inserts with size 50, insert 1000 entities, and compare SQL count with/without batching
2. Add Ehcache L2 cache to a frequently-read entity, verify with Hibernate statistics that cache hits occur
3. Configure `RoutingDataSource` with two H2 databases and verify read-only transactions go to the replica
4. Tune HikariCP: set `leak-detection-threshold` to 2000ms, hold a connection for 3s, and observe the warning
5. Create a Flyway migration that adds an index concurrently (PostgreSQL: `CREATE INDEX CONCURRENTLY`)
