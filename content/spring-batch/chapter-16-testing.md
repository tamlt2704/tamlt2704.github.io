# Chapter 16: Testing Strategies

[prev: Event-Driven Batch](chapter-15-event-driven.md) | [next: Building a Batch Platform](chapter-17-batch-platform.md)

## Testing Pyramid for Batch Jobs

```
         /  E2E Tests  \        ← Full job execution, real DB
        / Integration    \      ← Step-level, Spring context
       / Unit Tests        \    ← Processors, validators, mappers
      ──────────────────────
```

## Unit Testing Processors

```java
class CustomerTransformProcessorTest {

    private CustomerTransformProcessor processor;

    @BeforeEach
    void setUp() {
        processor = new CustomerTransformProcessor(
                new PhoneNormalizer(),
                mock(AddressLookupService.class)
        );
    }

    @Test
    void transformsLegacyCustomerToNewFormat() {
        LegacyCustomer legacy = new LegacyCustomer();
        legacy.setCustomerId(123L);
        legacy.setFirstName("John");
        legacy.setLastName("Doe");
        legacy.setEmail("  JOHN@EXAMPLE.COM  ");
        legacy.setPhone("(555) 123-4567");
        legacy.setCreatedDate(LocalDate.of(2020, 1, 15));

        Customer result = processor.process(legacy);

        assertThat(result.getFullName()).isEqualTo("John Doe");
        assertThat(result.getEmail()).isEqualTo("john@example.com");
        assertThat(result.getPhone()).isEqualTo("+15551234567");
        assertThat(result.getLegacyId()).isEqualTo(123L);
        assertThat(result.getSource()).isEqualTo("LEGACY_MIGRATION");
    }

    @Test
    void returnsNullForInvalidEmail() {
        LegacyCustomer legacy = new LegacyCustomer();
        legacy.setEmail("not-an-email");

        Customer result = processor.process(legacy);

        assertThat(result).isNull(); // Filtered out
    }
}
```

## Unit Testing Validators

```java
class TransactionValidatorTest {

    private final TransactionValidator validator = new TransactionValidator();

    @ParameterizedTest
    @CsvSource({
            "100.00, USD, DEBIT, true",
            "-50.00, USD, DEBIT, false",
            "0.00, USD, CREDIT, false",
            "100.00, '', DEBIT, false",
            "100.00, USD, INVALID, false"
    })
    void validatesTransactions(BigDecimal amount, String currency, String type, boolean expected) {
        Transaction tx = new Transaction(amount, currency, type);
        assertThat(validator.isValid(tx)).isEqualTo(expected);
    }
}
```

## Integration Testing Steps

```java
@SpringBatchTest
@SpringBootTest
@ActiveProfiles("test")
class ImportStepIntegrationTest {

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @BeforeEach
    void cleanDb() {
        jdbcTemplate.execute("DELETE FROM customers");
    }

    @Test
    void importStepReadsAndWritesCorrectly() {
        JobExecution execution = jobLauncherTestUtils.launchStep("importStep",
                new JobParametersBuilder()
                        .addString("inputFile", "classpath:test-data/customers.csv")
                        .toJobParameters());

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

        StepExecution step = execution.getStepExecutions().iterator().next();
        assertThat(step.getReadCount()).isEqualTo(5);
        assertThat(step.getWriteCount()).isEqualTo(5);
        assertThat(step.getSkipCount()).isEqualTo(0);

        Long count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM customers", Long.class);
        assertThat(count).isEqualTo(5);
    }

    @Test
    void importStepSkipsInvalidRecords() {
        JobExecution execution = jobLauncherTestUtils.launchStep("importStep",
                new JobParametersBuilder()
                        .addString("inputFile", "classpath:test-data/customers-with-errors.csv")
                        .toJobParameters());

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

        StepExecution step = execution.getStepExecutions().iterator().next();
        assertThat(step.getReadCount()).isEqualTo(10);
        assertThat(step.getWriteCount()).isEqualTo(8);
        assertThat(step.getSkipCount()).isEqualTo(2);
    }
}
```

## Full Job Integration Test

```java
@SpringBatchTest
@SpringBootTest
@ActiveProfiles("test")
class MigrationJobIntegrationTest {

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @Autowired
    @Qualifier("legacyJdbcTemplate")
    private JdbcTemplate legacyJdbc;

    @Autowired
    @Qualifier("targetJdbcTemplate")
    private JdbcTemplate targetJdbc;

    @Test
    void fullMigrationJobCompletesSuccessfully() {
        // Setup: insert test data in legacy DB
        legacyJdbc.execute("""
            INSERT INTO legacy_customers (customer_id, first_name, last_name, email, migrated)
            VALUES (1, 'Alice', 'Smith', 'alice@test.com', false),
                   (2, 'Bob', 'Jones', 'bob@test.com', false)
        """);

        JobExecution execution = jobLauncherTestUtils.launchJob(
                new JobParametersBuilder()
                        .addLong("timestamp", System.currentTimeMillis())
                        .toJobParameters());

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

        // Verify target has records
        Long targetCount = targetJdbc.queryForObject(
                "SELECT COUNT(*) FROM customers WHERE source = 'LEGACY_MIGRATION'", Long.class);
        assertThat(targetCount).isEqualTo(2);

        // Verify source marked as migrated
        Long migratedCount = legacyJdbc.queryForObject(
                "SELECT COUNT(*) FROM legacy_customers WHERE migrated = true", Long.class);
        assertThat(migratedCount).isEqualTo(2);
    }
}
```

## Test Configuration

```java
@TestConfiguration
public class BatchTestConfig {

    @Bean
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()
                .setType(EmbeddedDatabaseType.H2)
                .addScript("classpath:schema.sql")
                .build();
    }

    @Bean
    public JobLauncherTestUtils jobLauncherTestUtils(
            JobRepository jobRepository, Job job, JobLauncher jobLauncher) {
        JobLauncherTestUtils utils = new JobLauncherTestUtils();
        utils.setJobRepository(jobRepository);
        utils.setJob(job);
        utils.setJobLauncher(jobLauncher);
        return utils;
    }
}
```

## Testing with Testcontainers

```java
@SpringBatchTest
@SpringBootTest
@Testcontainers
class PostgresMigrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
            .withDatabaseName("testdb")
            .withInitScript("schema.sql");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @Test
    void jobWorksWithRealPostgres() {
        JobExecution execution = jobLauncherTestUtils.launchJob();
        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    }
}
```

## Testing Restartability

```java
@Test
void jobRestartsFromFailurePoint() {
    // First run — simulate failure at record 50
    simulateFailureAtRecord(50);

    JobExecution firstRun = jobLauncherTestUtils.launchJob(params);
    assertThat(firstRun.getStatus()).isEqualTo(BatchStatus.FAILED);

    StepExecution step = firstRun.getStepExecutions().iterator().next();
    assertThat(step.getWriteCount()).isEqualTo(49); // Processed up to failure

    // Fix the issue
    clearFailureSimulation();

    // Restart — should continue from record 50
    JobExecution restart = jobLauncherTestUtils.launchJob(params);
    assertThat(restart.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution restartStep = restart.getStepExecutions().iterator().next();
    assertThat(restartStep.getReadCount()).isEqualTo(51); // Remaining records
}
```

## Testing Skip and Retry Behavior

```java
@Test
void skipsInvalidRecordsAndContinues() {
    // Input file has 100 records, 3 are invalid
    JobExecution execution = jobLauncherTestUtils.launchStep("processStep",
            new JobParametersBuilder()
                    .addString("inputFile", "classpath:test-data/mixed-validity.csv")
                    .toJobParameters());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution step = execution.getStepExecutions().iterator().next();
    assertThat(step.getReadCount()).isEqualTo(100);
    assertThat(step.getWriteCount()).isEqualTo(97);
    assertThat(step.getReadSkipCount() + step.getProcessSkipCount()).isEqualTo(3);
}

@Test
void retriesTransientFailuresBeforeSkipping() {
    // Mock external service to fail twice then succeed
    when(externalService.call(any()))
            .thenThrow(new TimeoutException())
            .thenThrow(new TimeoutException())
            .thenReturn(successResponse);

    JobExecution execution = jobLauncherTestUtils.launchStep("apiStep");

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    verify(externalService, times(3)).call(any()); // 2 retries + 1 success
}
```

## Performance Testing

```java
@Test
void processesOneMillionRecordsWithinSLA() {
    // Generate 1M test records
    generateTestData(1_000_000);

    long start = System.currentTimeMillis();

    JobExecution execution = jobLauncherTestUtils.launchJob(
            new JobParametersBuilder()
                    .addString("inputFile", "test-data/1m-records.csv")
                    .addLong("timestamp", System.currentTimeMillis())
                    .toJobParameters());

    long duration = System.currentTimeMillis() - start;

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    assertThat(duration).isLessThan(300_000); // Under 5 minutes

    StepExecution step = execution.getStepExecutions().iterator().next();
    long throughput = step.getWriteCount() * 1000L / duration;
    log.info("Throughput: {} records/second", throughput);
    assertThat(throughput).isGreaterThan(5000); // At least 5K/sec
}
```

## Test Data Builders

```java
public class TestDataBuilder {

    public static LegacyCustomer aLegacyCustomer() {
        return LegacyCustomer.builder()
                .customerId(ThreadLocalRandom.current().nextLong(1, 1_000_000))
                .firstName("Test")
                .lastName("User")
                .email("test%d@example.com".formatted(System.nanoTime()))
                .phone("5551234567")
                .createdDate(LocalDate.now().minusDays(30))
                .build();
    }

    public static String generateCsvFile(int recordCount) throws IOException {
        Path tempFile = Files.createTempFile("test-data-", ".csv");
        try (BufferedWriter writer = Files.newBufferedWriter(tempFile)) {
            writer.write("id,name,email,amount,date");
            writer.newLine();
            for (int i = 0; i < recordCount; i++) {
                writer.write("%d,User%d,user%d@test.com,%.2f,%s".formatted(
                        i, i, i, ThreadLocalRandom.current().nextDouble(1, 10000),
                        LocalDate.now().minusDays(ThreadLocalRandom.current().nextInt(365))));
                writer.newLine();
            }
        }
        return tempFile.toString();
    }
}
```

## Key Takeaways

- Unit test processors and validators in isolation — they're pure functions
- Use `@SpringBatchTest` + `JobLauncherTestUtils` for step/job integration tests
- Testcontainers give you real database behavior without environment dependencies
- Test restartability explicitly — it's a core Spring Batch feature
- Performance tests with SLA assertions catch regressions early
- Test data builders keep tests readable and maintainable
