# Chapter 9: Testing — Fast, Reliable, No Excuses

[← Chapter 8: The Dashboard](chapter-08-monitoring.md)

---

## The Incident

You've built a production-grade batch system. It handles 5 million rows, skips bad data, retries transient failures, restarts from checkpoints, runs in parallel, orchestrates complex flows, and reports metrics.

Then you push a "small refactor" on Friday afternoon. The reconciliation job runs Saturday morning. It silently writes every transaction as MATCHED — including the 3,000 that should be MISMATCHED. Nobody notices until Monday when the auditors ask why the mismatch report is empty.

Director Compliance: "How did this get to production?"

You: "The tests passed."

Director Compliance: "What tests?"

You had one integration test that checked if the job completed. It did. It just produced wrong results. You need better tests.

## The Testing Pyramid for Batch Jobs

```
         ┌─────────────┐
         │  End-to-End  │  ← Few: full job, real DB, real files
         │   (slow)     │
         ├─────────────┤
         │ Integration  │  ← Some: single steps, H2, test files
         │  (medium)    │
         ├─────────────┤
         │    Unit      │  ← Many: processors, validators, mappers
         │   (fast)     │
         └─────────────┘
```

Most of your tests should be unit tests on processors and validators. They're fast, focused, and catch logic bugs like the one that shipped on Friday.

## Unit Testing Processors

Processors are pure functions: input → output. No Spring context needed.

```java
// src/test/java/com/megabank/processor/ReconciliationProcessorTest.java
package com.megabank.processor;

import com.megabank.domain.ReconciliationResult;
import com.megabank.domain.TransactionDto;
import com.megabank.service.LedgerService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class ReconciliationProcessorTest {

    private LedgerService ledgerService;
    private ReconciliationProcessor processor;

    @BeforeEach
    void setUp() {
        ledgerService = mock(LedgerService.class);
        processor = new ReconciliationProcessor(ledgerService);
    }

    @Test
    void shouldReturnMatched_whenAmountsAreEqual() {
        TransactionDto input = createTransaction("TXN-001", "1500.00");
        when(ledgerService.findAmount("TXN-001")).thenReturn(new BigDecimal("1500.00"));

        ReconciliationResult result = processor.process(input);

        assertThat(result.status()).isEqualTo("MATCHED");
        assertThat(result.partnerAmount()).isEqualByComparingTo("1500.00");
        assertThat(result.ledgerAmount()).isEqualByComparingTo("1500.00");
    }

    @Test
    void shouldReturnMismatched_whenAmountsDiffer() {
        TransactionDto input = createTransaction("TXN-002", "1500.00");
        when(ledgerService.findAmount("TXN-002")).thenReturn(new BigDecimal("1499.99"));

        ReconciliationResult result = processor.process(input);

        assertThat(result.status()).isEqualTo("MISMATCHED");
        assertThat(result.partnerAmount()).isEqualByComparingTo("1500.00");
        assertThat(result.ledgerAmount()).isEqualByComparingTo("1499.99");
    }

    @Test
    void shouldReturnMissing_whenTransactionNotInLedger() {
        TransactionDto input = createTransaction("TXN-003", "2000.00");
        when(ledgerService.findAmount("TXN-003")).thenReturn(null);

        ReconciliationResult result = processor.process(input);

        assertThat(result.status()).isEqualTo("MISSING");
        assertThat(result.ledgerAmount()).isNull();
    }

    @ParameterizedTest
    @CsvSource({
        "100.00, 100.00, MATCHED",
        "100.00, 100.01, MISMATCHED",
        "0.01, 0.01, MATCHED",
        "999999.99, 999999.98, MISMATCHED"
    })
    void shouldHandleVariousAmounts(String partner, String ledger, String expected) {
        TransactionDto input = createTransaction("TXN-X", partner);
        when(ledgerService.findAmount("TXN-X")).thenReturn(new BigDecimal(ledger));

        ReconciliationResult result = processor.process(input);

        assertThat(result.status()).isEqualTo(expected);
    }

    private TransactionDto createTransaction(String id, String amount) {
        TransactionDto dto = new TransactionDto();
        dto.setTransactionId(id);
        dto.setAmount(new BigDecimal(amount));
        dto.setCurrency("USD");
        dto.setTimestamp("2024-01-22T09:00:00");
        dto.setCounterparty("PARTNER_A");
        return dto;
    }
}
```

This test would have caught Friday's bug. The processor's logic is tested in isolation — no database, no files, no Spring context. Runs in milliseconds.

## Unit Testing Validators

```java
// src/test/java/com/megabank/processor/ValidatingProcessorTest.java
package com.megabank.processor;

import com.megabank.domain.TransactionDto;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.batch.item.validator.ValidationException;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.assertThatNoException;

class ValidatingProcessorTest {

    private final ValidatingProcessor processor = new ValidatingProcessor(null);

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {"  ", "\t"})
    void shouldRejectBlankTransactionId(String id) {
        TransactionDto dto = validTransaction();
        dto.setTransactionId(id);

        assertThatThrownBy(() -> processor.process(dto))
            .isInstanceOf(ValidationException.class)
            .hasMessageContaining("transaction ID");
    }

    @Test
    void shouldRejectNegativeAmount() {
        TransactionDto dto = validTransaction();
        dto.setAmount(new BigDecimal("-100.00"));

        assertThatThrownBy(() -> processor.process(dto))
            .isInstanceOf(ValidationException.class)
            .hasMessageContaining("Negative amount");
    }

    @ParameterizedTest
    @ValueSource(strings = {"US", "USDD", "12", ""})
    void shouldRejectInvalidCurrency(String currency) {
        TransactionDto dto = validTransaction();
        dto.setCurrency(currency);

        assertThatThrownBy(() -> processor.process(dto))
            .isInstanceOf(ValidationException.class)
            .hasMessageContaining("currency");
    }

    @Test
    void shouldAcceptValidTransaction() {
        TransactionDto dto = validTransaction();

        assertThatNoException().isThrownBy(() -> processor.process(dto));
    }

    private TransactionDto validTransaction() {
        TransactionDto dto = new TransactionDto();
        dto.setTransactionId("TXN-001");
        dto.setAmount(new BigDecimal("1500.00"));
        dto.setCurrency("USD");
        dto.setTimestamp("2024-01-22T09:00:00");
        dto.setCounterparty("PARTNER_A");
        return dto;
    }
}
```

## Integration Testing: JobLauncherTestUtils

Spring Batch provides `JobLauncherTestUtils` for testing jobs and individual steps:

```java
// src/test/java/com/megabank/integration/ReconciliationJobIntegrationTest.java
package com.megabank.integration;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.batch.core.*;
import org.springframework.batch.test.JobLauncherTestUtils;
import org.springframework.batch.test.context.SpringBatchTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBatchTest
@SpringBootTest
class ReconciliationJobIntegrationTest {

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @TempDir
    Path tempDir;

    @DynamicPropertySource
    static void configureTestDb(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1");
        registry.add("spring.datasource.driver-class-name", () -> "org.h2.Driver");
        registry.add("spring.batch.jdbc.initialize-schema", () -> "always");
    }

    @BeforeEach
    void setUp() {
        jdbcTemplate.execute("DELETE FROM reconciliation_results");
    }

    @Test
    void fullJob_shouldReconcileAllTransactions() throws Exception {
        Path inputFile = createTestFile("""
            transaction_id,amount,currency,timestamp,counterparty
            TXN-001,1500.00,USD,2024-01-22T09:00:00,PARTNER_A
            TXN-002,2300.50,EUR,2024-01-22T10:00:00,PARTNER_B
            TXN-003,4000.00,USD,2024-01-22T11:00:00,PARTNER_A
            """);

        JobParameters params = new JobParametersBuilder()
            .addString("inputFile", inputFile.toString())
            .addString("date", "2024-01-22")
            .toJobParameters();

        JobExecution execution = jobLauncherTestUtils.launchJob(params);

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

        // Verify actual output data
        List<Map<String, Object>> results = jdbcTemplate.queryForList(
            "SELECT * FROM reconciliation_results ORDER BY transaction_id");
        assertThat(results).hasSize(3);
        assertThat(results.get(0).get("transaction_id")).isEqualTo("TXN-001");
    }

    @Test
    void singleStep_canBeTestedInIsolation() throws Exception {
        Path inputFile = createTestFile("""
            transaction_id,amount,currency,timestamp,counterparty
            TXN-001,1500.00,USD,2024-01-22T09:00:00,PARTNER_A
            """);

        JobExecution execution = jobLauncherTestUtils.launchStep("reconcileChunkStep",
            new JobParametersBuilder()
                .addString("inputFile", inputFile.toString())
                .toJobParameters());

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
        StepExecution step = execution.getStepExecutions().iterator().next();
        assertThat(step.getReadCount()).isEqualTo(1);
        assertThat(step.getWriteCount()).isEqualTo(1);
    }

    private Path createTestFile(String content) throws IOException {
        Path file = tempDir.resolve("test_transactions.csv");
        Files.writeString(file, content);
        return file;
    }
}
```

### Key Testing Utilities

| Utility | Purpose |
|---|---|
| `JobLauncherTestUtils.launchJob()` | Run the entire job |
| `JobLauncherTestUtils.launchStep()` | Run a single step in isolation |
| `@SpringBatchTest` | Auto-configures test utilities |
| `@DynamicPropertySource` | Override properties for test (H2 instead of Postgres) |
| `@TempDir` | Temporary directory for test files (auto-cleaned) |

## Testing Skip and Retry Behavior

```java
@Test
void shouldSkipBadRows_andWriteGoodOnes() throws Exception {
    Path inputFile = createTestFile("""
        transaction_id,amount,currency,timestamp,counterparty
        TXN-001,1500.00,USD,2024-01-22T09:00:00,PARTNER_A
        TXN-BAD,NOT_A_NUMBER,USD,2024-01-22T09:01:00,PARTNER_A
        TXN-003,3000.00,USD,2024-01-22T09:02:00,PARTNER_A
        """);

    JobExecution execution = jobLauncherTestUtils.launchJob(
        paramsWithFile(inputFile));

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution step = execution.getStepExecutions().iterator().next();
    assertThat(step.getReadCount()).isEqualTo(2);      // 2 good rows
    assertThat(step.getReadSkipCount()).isEqualTo(1);  // 1 bad row
    assertThat(step.getWriteCount()).isEqualTo(2);

    // Verify only good rows in output
    List<Map<String, Object>> results = jdbcTemplate.queryForList(
        "SELECT * FROM reconciliation_results");
    assertThat(results).hasSize(2);
    assertThat(results).extracting(r -> r.get("transaction_id"))
        .containsExactlyInAnyOrder("TXN-001", "TXN-003");
}

@Test
void shouldRetryTransientFailures_thenSucceed() throws Exception {
    // Mock service that fails twice then succeeds
    when(exchangeRateService.getRate(any(), any()))
        .thenThrow(new RuntimeException("Connection timeout"))
        .thenThrow(new RuntimeException("Connection timeout"))
        .thenReturn(new BigDecimal("1.0"));

    Path inputFile = createTestFile(singleTransaction());

    JobExecution execution = jobLauncherTestUtils.launchJob(
        paramsWithFile(inputFile));

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    verify(exchangeRateService, times(3)).getRate(any(), any()); // 2 retries + 1 success
}
```

## Testing Restartability

```java
@Test
void shouldRestartFromCheckpoint_afterFailure() throws Exception {
    Path inputFile = createTestFile(generateRows(5000)); // 5 chunks of 1000

    JobParameters params = new JobParametersBuilder()
        .addString("inputFile", inputFile.toString())
        .addString("date", "2024-01-22")
        .toJobParameters();

    // First run: inject failure at row 3500
    doThrow(new RuntimeException("DB connection lost"))
        .when(writer).write(argThat(chunk -> chunk.size() > 0
            && getRowCount() > 3000));

    JobExecution run1 = jobLauncherTestUtils.launchJob(params);
    assertThat(run1.getStatus()).isEqualTo(BatchStatus.FAILED);

    long writtenInRun1 = jdbcTemplate.queryForObject(
        "SELECT COUNT(*) FROM reconciliation_results", Long.class);
    assertThat(writtenInRun1).isEqualTo(3000); // 3 chunks committed

    // Second run: no failures
    reset(writer); // remove the mock failure

    JobExecution run2 = jobLauncherTestUtils.launchJob(params);
    assertThat(run2.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    long totalWritten = jdbcTemplate.queryForObject(
        "SELECT COUNT(*) FROM reconciliation_results", Long.class);
    assertThat(totalWritten).isEqualTo(5000); // all rows, no duplicates
}
```

## Testing Conditional Flows

```java
@Test
void monthEndJob_shouldFollowCorrectPath_onSuccess() throws Exception {
    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    List<String> executedSteps = execution.getStepExecutions().stream()
        .map(StepExecution::getStepName)
        .toList();

    assertThat(executedSteps).containsExactly(
        "reconcileStep", "positionStep", "reportStep", "archiveStep", "notifyStep");
}

@Test
void monthEndJob_shouldSkipDownstreamSteps_onReconciliationFailure() throws Exception {
    // Force reconciliation to fail
    forceStepFailure("reconcileStep");

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.FAILED);

    List<String> executedSteps = execution.getStepExecutions().stream()
        .map(StepExecution::getStepName)
        .toList();

    assertThat(executedSteps).containsExactly("reconcileStep");
    assertThat(executedSteps).doesNotContain("positionStep", "reportStep");
}
```

## Testing with Embedded Databases

For fast integration tests, use H2 with Spring Batch schema:

```java
@TestConfiguration
static class TestConfig {

    @Bean
    public DataSource testDataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .addScript("classpath:org/springframework/batch/core/schema-h2.sql")
            .addScript("classpath:schema-test.sql") // your app tables
            .build();
    }
}
```

Or use Testcontainers for a real PostgreSQL:

```java
@Testcontainers
@SpringBootTest
class PostgresIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    // Tests run against real Postgres
}
```

## Test Data Builders

For complex test scenarios, use builders:

```java
// src/test/java/com/megabank/testutil/TestDataBuilder.java
package com.megabank.testutil;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class TestDataBuilder {

    public static Path createCsv(Path dir, int goodRows, int badRows) throws Exception {
        Path file = dir.resolve("test_transactions.csv");
        List<String> lines = new ArrayList<>();
        lines.add("transaction_id,amount,currency,timestamp,counterparty");

        for (int i = 0; i < goodRows; i++) {
            lines.add(String.format("TXN-%05d,%.2f,USD,2024-01-22T09:00:00,PARTNER_A",
                i, ThreadLocalRandom.current().nextDouble(100, 10000)));
        }

        for (int i = 0; i < badRows; i++) {
            lines.add(String.format("TXN-BAD-%05d,N/A,XXX,invalid,", i));
        }

        // Shuffle so bad rows aren't all at the end
        java.util.Collections.shuffle(lines.subList(1, lines.size()));
        Files.write(file, lines);
        return file;
    }

    public static JobParameters defaultParams(Path inputFile) {
        return new JobParametersBuilder()
            .addString("inputFile", inputFile.toString())
            .addString("date", "2024-01-22")
            .toJobParameters();
    }
}
```

## The Complete Test Suite Structure

```
src/test/java/com/megabank/
├── processor/
│   ├── ReconciliationProcessorTest.java      ← unit (fast)
│   ├── ValidatingProcessorTest.java          ← unit (fast)
│   └── EnrichmentProcessorTest.java          ← unit (fast)
├── integration/
│   ├── ReconciliationJobIntegrationTest.java ← step/job (medium)
│   ├── SkipRetryIntegrationTest.java         ← fault tolerance (medium)
│   ├── RestartabilityTest.java               ← checkpoint/restart (medium)
│   └── MonthEndFlowTest.java                 ← conditional flows (medium)
├── e2e/
│   └── FullPipelineTest.java                 ← real DB, real files (slow)
└── testutil/
    └── TestDataBuilder.java                  ← shared helpers
```

Run them separately:

```bash
# Fast unit tests only (seconds)
./gradlew test --tests "com.megabank.processor.*"

# Integration tests (minutes)
./gradlew test --tests "com.megabank.integration.*"

# Everything
./gradlew test
```

## What You Learned

- **Unit test processors** — pure functions, mock dependencies, fast feedback
- **`JobLauncherTestUtils`** — launch jobs and steps in tests
- **`launchStep()`** — test individual steps in isolation
- **`@SpringBatchTest`** — auto-configures test utilities
- **H2 for tests** — fast, in-memory, no external dependencies
- **Testcontainers** — real database for integration tests
- **Test skip/retry** — verify fault tolerance behavior
- **Test restartability** — verify checkpoint/resume works
- **Test conditional flows** — verify correct step execution paths
- **Test data builders** — generate realistic test data at scale

## The Full Picture

Over 9 chapters, you built a production-grade batch processing system:

| Chapter | Problem | Solution |
|---|---|---|
| 1 | Manual process, no audit trail | Job/Step/Tasklet, JobRepository |
| 2 | OOM on large files | Chunk-oriented processing |
| 3 | Bad data kills the job | Skip logic, SkipPolicy, listeners |
| 4 | Restart means starting over | ExecutionContext, restartable readers |
| 5 | Transient failures kill the job | Retry, backoff, circuit breaker |
| 6 | Single thread too slow | Partitioning, parallel flows |
| 7 | Jobs run in wrong order | Flows, conditions, deciders |
| 8 | No visibility into job status | JobExplorer, Actuator, metrics |
| 9 | Bugs ship to production | Testing pyramid, JobLauncherTestUtils |

Every feature was introduced because something broke. The bugs came first. The theory followed.

Brenda's 5-million-row file processes in 1.5 minutes. Bad rows are skipped and logged. Transient failures retry automatically. If the job crashes, it restarts from the last checkpoint. Director Compliance has his audit trail. Admiral Uptime has his dashboard. The auditors are satisfied.

You're no longer the new person on the batch team. You're the one they call when things break.

---

[← Chapter 8: The Dashboard](chapter-08-monitoring.md)
