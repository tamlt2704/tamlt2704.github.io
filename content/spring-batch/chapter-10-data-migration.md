# Chapter 10: Data Migration

[prev: Production](chapter-09-production.md) | [next: ETL Pipelines](chapter-11-etl-pipelines.md)

## Why Spring Batch for Migrations

Database migrations at scale (millions of rows, schema transformations, cross-system moves) need:

- Restartability — resume from where it failed
- Auditing — know exactly what was migrated
- Validation — ensure data integrity post-migration
- Throttling — don't overwhelm source/target systems

## Migration Job Architecture

```
Source DB ──► ItemReader ──► Transformer ──► Validator ──► Target DB
                                                              │
                                                              ▼
                                                        Audit Log
```

## Full Migration Example: Legacy to New Schema

```java
@Configuration
public class CustomerMigrationConfig {

    @Bean
    public Job customerMigrationJob(JobRepository jobRepository,
                                     Step extractStep,
                                     Step validateStep,
                                     Step reportStep) {
        return new JobBuilder("customerMigrationJob", jobRepository)
                .start(extractStep)
                .next(validateStep)
                .next(reportStep)
                .listener(new MigrationJobListener())
                .build();
    }

    @Bean
    public Step extractStep(JobRepository jobRepository,
                            PlatformTransactionManager txManager,
                            ItemReader<LegacyCustomer> reader,
                            ItemProcessor<LegacyCustomer, Customer> processor,
                            ItemWriter<Customer> writer) {
        return new StepBuilder("extractStep", jobRepository)
                .<LegacyCustomer, Customer>chunk(500, txManager)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .faultTolerant()
                .skip(DataIntegrityViolationException.class)
                .skipLimit(100)
                .listener(new MigrationSkipListener())
                .build();
    }
}
```

## Reading from Legacy Database

```java
@Bean
@StepScope
public JdbcPagingItemReader<LegacyCustomer> legacyReader(
        @Qualifier("legacyDataSource") DataSource legacyDs) {

    Map<String, Order> sortKeys = Map.of("customer_id", Order.ASCENDING);

    return new JdbcPagingItemReaderBuilder<LegacyCustomer>()
            .name("legacyCustomerReader")
            .dataSource(legacyDs)
            .selectClause("SELECT customer_id, first_name, last_name, email, phone, created_date")
            .fromClause("FROM legacy_customers")
            .whereClause("WHERE migrated = false")
            .sortKeys(sortKeys)
            .pageSize(500)
            .rowMapper(new LegacyCustomerRowMapper())
            .build();
}
```

## Schema Transformation Processor

```java
@Component
public class CustomerTransformProcessor
        implements ItemProcessor<LegacyCustomer, Customer> {

    private final PhoneNormalizer phoneNormalizer;
    private final AddressLookupService addressService;

    @Override
    public Customer process(LegacyCustomer legacy) {
        Customer customer = new Customer();
        customer.setId(UUID.randomUUID());
        customer.setFullName(legacy.getFirstName() + " " + legacy.getLastName());
        customer.setEmail(legacy.getEmail().toLowerCase().trim());
        customer.setPhone(phoneNormalizer.normalize(legacy.getPhone()));
        customer.setCreatedAt(legacy.getCreatedDate().atStartOfDay(ZoneOffset.UTC).toInstant());
        customer.setSource("LEGACY_MIGRATION");
        customer.setLegacyId(legacy.getCustomerId());

        // Enrich with external data
        addressService.findByLegacyId(legacy.getCustomerId())
                .ifPresent(customer::setAddress);

        return customer;
    }
}
```

## Multi-DataSource Configuration

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.legacy")
    public DataSource legacyDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.target")
    public DataSource targetDataSource() {
        return DataSourceBuilder.create().build();
    }
}
```

```yaml
spring:
  datasource:
    legacy:
      url: jdbc:postgresql://legacy-host:5432/legacy_db
      username: readonly_user
      password: ${LEGACY_DB_PASSWORD}
    target:
      url: jdbc:postgresql://new-host:5432/new_db
      username: migration_user
      password: ${TARGET_DB_PASSWORD}
```

## Validation Step

```java
@Bean
public Step validateStep(JobRepository jobRepository,
                         PlatformTransactionManager txManager) {
    return new StepBuilder("validateStep", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                long sourceCount = legacyJdbc.queryForObject(
                        "SELECT COUNT(*) FROM legacy_customers WHERE migrated = true", Long.class);
                long targetCount = targetJdbc.queryForObject(
                        "SELECT COUNT(*) FROM customers WHERE source = 'LEGACY_MIGRATION'", Long.class);

                if (sourceCount != targetCount) {
                    throw new MigrationValidationException(
                            "Count mismatch: source=%d, target=%d".formatted(sourceCount, targetCount));
                }

                // Spot-check random records
                List<Long> sampleIds = legacyJdbc.queryForList(
                        "SELECT customer_id FROM legacy_customers ORDER BY RANDOM() LIMIT 100", Long.class);

                for (Long id : sampleIds) {
                    validateRecord(id);
                }

                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## Marking Records as Migrated

```java
@Component
public class MigrationWriter implements ItemWriter<Customer> {

    private final JdbcBatchItemWriter<Customer> targetWriter;
    private final JdbcTemplate legacyJdbc;

    @Override
    public void write(Chunk<? extends Customer> items) throws Exception {
        // Write to target
        targetWriter.write(items);

        // Mark as migrated in source
        List<Long> legacyIds = items.getItems().stream()
                .map(Customer::getLegacyId)
                .toList();

        legacyJdbc.batchUpdate(
                "UPDATE legacy_customers SET migrated = true, migrated_at = NOW() WHERE customer_id = ?",
                legacyIds.stream().map(id -> new Object[]{id}).toList()
        );
    }
}
```

## Incremental Migration with Partitioning

For large datasets, partition by ID range:

```java
@Bean
public Step partitionedMigrationStep(JobRepository jobRepository,
                                      Step workerStep) {
    return new StepBuilder("partitionedMigration", jobRepository)
            .partitioner("worker", new IdRangePartitioner(legacyJdbc))
            .step(workerStep)
            .gridSize(10)
            .taskExecutor(migrationExecutor())
            .build();
}

public class IdRangePartitioner implements Partitioner {
    private final JdbcTemplate jdbc;

    @Override
    public Map<String, ExecutionContext> partition(int gridSize) {
        Long min = jdbc.queryForObject("SELECT MIN(customer_id) FROM legacy_customers WHERE migrated = false", Long.class);
        Long max = jdbc.queryForObject("SELECT MAX(customer_id) FROM legacy_customers WHERE migrated = false", Long.class);

        long range = (max - min) / gridSize + 1;
        Map<String, ExecutionContext> partitions = new HashMap<>();

        for (int i = 0; i < gridSize; i++) {
            ExecutionContext ctx = new ExecutionContext();
            ctx.putLong("minId", min + (i * range));
            ctx.putLong("maxId", min + ((i + 1) * range) - 1);
            partitions.put("partition" + i, ctx);
        }
        return partitions;
    }
}
```

## Dry Run Mode

```java
@Bean
@StepScope
public ItemWriter<Customer> migrationWriter(
        @Value("#{jobParameters['dryRun']}") String dryRun) {

    if ("true".equals(dryRun)) {
        return items -> log.info("DRY RUN: Would write {} records", items.size());
    }

    return new JdbcBatchItemWriterBuilder<Customer>()
            .sql("INSERT INTO customers (id, full_name, email, phone, created_at, source, legacy_id) " +
                 "VALUES (:id, :fullName, :email, :phone, :createdAt, :source, :legacyId)")
            .beanMapped()
            .dataSource(targetDataSource)
            .build();
}
```

## Rollback Strategy

```java
@Bean
public Step rollbackStep(JobRepository jobRepository,
                         PlatformTransactionManager txManager) {
    return new StepBuilder("rollbackStep", jobRepository)
            .<Customer, Long>chunk(1000, txManager)
            .reader(migratedRecordsReader())
            .processor(Customer::getLegacyId)
            .writer(items -> {
                // Delete from target
                targetJdbc.batchUpdate(
                        "DELETE FROM customers WHERE legacy_id = ?",
                        items.getItems().stream().map(id -> new Object[]{id}).toList());
                // Unmark in source
                legacyJdbc.batchUpdate(
                        "UPDATE legacy_customers SET migrated = false WHERE customer_id = ?",
                        items.getItems().stream().map(id -> new Object[]{id}).toList());
            })
            .build();
}
```

## Migration Metrics and Reporting

```java
public class MigrationJobListener implements JobExecutionListener {

    @Override
    public void afterJob(JobExecution jobExecution) {
        StepExecution step = jobExecution.getStepExecutions().stream()
                .filter(s -> s.getStepName().equals("extractStep"))
                .findFirst().orElseThrow();

        log.info("""
                Migration Complete:
                  Status: {}
                  Records Read: {}
                  Records Written: {}
                  Records Skipped: {}
                  Duration: {} seconds
                """,
                jobExecution.getStatus(),
                step.getReadCount(),
                step.getWriteCount(),
                step.getSkipCount(),
                Duration.between(jobExecution.getStartTime(), jobExecution.getEndTime()).getSeconds()
        );
    }
}
```

## Key Takeaways

- Use multi-datasource config to read from legacy and write to target
- Partition large migrations by ID range for parallel processing
- Always include a validation step comparing source and target counts
- Support dry-run mode for testing without side effects
- Mark records as migrated to enable incremental runs and restartability
- Build rollback steps for when things go wrong
