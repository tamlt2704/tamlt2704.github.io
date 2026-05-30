# Chapter 13: API Integration Batch Jobs

[prev: File Processing](chapter-12-file-processing.md) | [next: Reporting & Aggregation](chapter-14-reporting.md)

## When APIs Meet Batch

Products often need to:

- Sync data from third-party APIs (CRM, payment providers, shipping)
- Push bulk updates to external systems
- Reconcile local data with remote APIs
- Rate-limit API calls while processing millions of records

## Paginated API Reader

```java
@Component
@StepScope
public class PaginatedApiReader implements ItemReader<CustomerDto> {

    private final RestClient restClient;
    private int currentPage = 0;
    private List<CustomerDto> currentBatch = new ArrayList<>();
    private int currentIndex = 0;
    private boolean exhausted = false;

    public PaginatedApiReader(RestClient.Builder builder) {
        this.restClient = builder
                .baseUrl("https://api.crm-provider.com/v2")
                .defaultHeader("Authorization", "Bearer " + apiKey)
                .build();
    }

    @Override
    public synchronized CustomerDto read() {
        if (exhausted) return null;

        if (currentIndex >= currentBatch.size()) {
            currentBatch = fetchPage(currentPage++);
            currentIndex = 0;
            if (currentBatch.isEmpty()) {
                exhausted = true;
                return null;
            }
        }
        return currentBatch.get(currentIndex++);
    }

    private List<CustomerDto> fetchPage(int page) {
        ApiResponse<CustomerDto> response = restClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/customers")
                        .queryParam("page", page)
                        .queryParam("size", 100)
                        .queryParam("updatedSince", LocalDate.now().minusDays(1))
                        .build())
                .retrieve()
                .body(new ParameterizedTypeReference<>() {});

        return response != null ? response.getData() : List.of();
    }
}
```

## Rate-Limited API Writer

```java
@Component
public class RateLimitedApiWriter implements ItemWriter<OrderUpdate> {

    private final RestClient restClient;
    private final RateLimiter rateLimiter; // Resilience4j

    public RateLimitedApiWriter(RestClient.Builder builder) {
        this.restClient = builder.baseUrl("https://api.shipping.com/v1").build();
        this.rateLimiter = RateLimiter.of("shippingApi",
                RateLimiterConfig.custom()
                        .limitForPeriod(50)           // 50 requests
                        .limitRefreshPeriod(Duration.ofSeconds(1)) // per second
                        .timeoutDuration(Duration.ofSeconds(30))
                        .build());
    }

    @Override
    public void write(Chunk<? extends OrderUpdate> items) throws Exception {
        for (OrderUpdate update : items) {
            rateLimiter.acquirePermission();

            restClient.put()
                    .uri("/shipments/{id}/status", update.getShipmentId())
                    .body(update)
                    .retrieve()
                    .toBodilessEntity();
        }
    }
}
```

## Retry with Exponential Backoff

```java
@Bean
public Step apiSyncStep(JobRepository jobRepository,
                        PlatformTransactionManager txManager,
                        ItemReader<CustomerDto> apiReader,
                        ItemProcessor<CustomerDto, Customer> processor,
                        ItemWriter<Customer> dbWriter) {
    return new StepBuilder("apiSync", jobRepository)
            .<CustomerDto, Customer>chunk(50, txManager)
            .reader(apiReader)
            .processor(processor)
            .writer(dbWriter)
            .faultTolerant()
            .retry(HttpServerErrorException.class)
            .retry(ResourceAccessException.class)
            .retryLimit(3)
            .backOffPolicy(exponentialBackOff())
            .skip(HttpClientErrorException.NotFound.class)
            .skipLimit(100)
            .listener(new ApiRetryListener())
            .build();
}

private BackOffPolicy exponentialBackOff() {
    ExponentialBackOffPolicy policy = new ExponentialBackOffPolicy();
    policy.setInitialInterval(1000);
    policy.setMultiplier(2.0);
    policy.setMaxInterval(30000);
    return policy;
}
```

## Bulk API Operations

Some APIs support batch endpoints:

```java
@Component
public class BulkApiWriter implements ItemWriter<ProductUpdate> {

    private final RestClient restClient;

    @Override
    public void write(Chunk<? extends ProductUpdate> items) throws Exception {
        // Send as bulk request
        BulkRequest request = new BulkRequest(items.getItems());

        BulkResponse response = restClient.post()
                .uri("/products/bulk-update")
                .body(request)
                .retrieve()
                .body(BulkResponse.class);

        // Handle partial failures
        if (response.hasErrors()) {
            List<BulkError> errors = response.getErrors();
            log.warn("Bulk update had {} errors out of {} items", errors.size(), items.size());

            for (BulkError error : errors) {
                if (error.isRetryable()) {
                    throw new RetryableApiException(error.getMessage());
                }
                log.error("Non-retryable error for item {}: {}", error.getItemId(), error.getMessage());
            }
        }
    }
}
```

## OAuth2 Token Management

```java
@Component
public class OAuth2TokenManager {

    private final RestClient tokenClient;
    private String accessToken;
    private Instant tokenExpiry = Instant.EPOCH;

    public synchronized String getToken() {
        if (Instant.now().isAfter(tokenExpiry.minusSeconds(60))) {
            refreshToken();
        }
        return accessToken;
    }

    private void refreshToken() {
        TokenResponse response = tokenClient.post()
                .uri("/oauth/token")
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body("grant_type=client_credentials&client_id={id}&client_secret={secret}")
                .retrieve()
                .body(TokenResponse.class);

        this.accessToken = response.getAccessToken();
        this.tokenExpiry = Instant.now().plusSeconds(response.getExpiresIn());
    }
}
```

## API Reconciliation Job

Compare local data with remote API and sync differences:

```java
@Configuration
public class ReconciliationJobConfig {

    @Bean
    public Job reconciliationJob(JobRepository jobRepository,
                                  Step fetchRemoteStep,
                                  Step compareStep,
                                  Step syncDifferencesStep) {
        return new JobBuilder("reconciliationJob", jobRepository)
                .start(fetchRemoteStep)
                .next(compareStep)
                .next(syncDifferencesStep)
                .build();
    }

    @Bean
    public Step compareStep(JobRepository jobRepository,
                            PlatformTransactionManager txManager) {
        return new StepBuilder("compare", jobRepository)
                .tasklet((contribution, chunkContext) -> {
                    // Load remote snapshot into temp table
                    // Compare with local data
                    jdbc.execute("""
                        INSERT INTO reconciliation_diff (entity_id, diff_type, local_value, remote_value)
                        SELECT
                            COALESCE(l.id, r.id) as entity_id,
                            CASE
                                WHEN l.id IS NULL THEN 'MISSING_LOCAL'
                                WHEN r.id IS NULL THEN 'MISSING_REMOTE'
                                ELSE 'MISMATCH'
                            END as diff_type,
                            l.data as local_value,
                            r.data as remote_value
                        FROM local_entities l
                        FULL OUTER JOIN remote_snapshot r ON l.id = r.id
                        WHERE l.data IS DISTINCT FROM r.data
                    """);
                    return RepeatStatus.FINISHED;
                }, txManager)
                .build();
    }
}
```

## Webhook-Triggered Batch Jobs

```java
@RestController
@RequestMapping("/api/batch")
public class BatchTriggerController {

    private final JobLauncher asyncJobLauncher;
    private final Job syncJob;

    @PostMapping("/trigger/sync")
    public ResponseEntity<Map<String, Object>> triggerSync(
            @RequestBody WebhookPayload payload) throws Exception {

        JobParameters params = new JobParametersBuilder()
                .addString("triggeredBy", payload.getSource())
                .addString("entityType", payload.getEntityType())
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters();

        JobExecution execution = asyncJobLauncher.run(syncJob, params);

        return ResponseEntity.accepted().body(Map.of(
                "jobId", execution.getJobId(),
                "status", execution.getStatus().toString()
        ));
    }

    @GetMapping("/status/{jobId}")
    public ResponseEntity<Map<String, Object>> getStatus(@PathVariable Long jobId) {
        JobExecution execution = jobExplorer.getJobExecution(jobId);
        return ResponseEntity.ok(Map.of(
                "status", execution.getStatus(),
                "startTime", execution.getStartTime(),
                "endTime", execution.getEndTime(),
                "readCount", execution.getStepExecutions().stream()
                        .mapToLong(StepExecution::getReadCount).sum()
        ));
    }
}
```

## Circuit Breaker Pattern

```java
@Component
public class CircuitBreakerApiReader implements ItemReader<PaymentDto> {

    private final CircuitBreaker circuitBreaker;
    private final PaginatedApiReader delegate;

    public CircuitBreakerApiReader(PaginatedApiReader delegate) {
        this.delegate = delegate;
        this.circuitBreaker = CircuitBreaker.of("paymentApi",
                CircuitBreakerConfig.custom()
                        .failureRateThreshold(50)
                        .waitDurationInOpenState(Duration.ofMinutes(2))
                        .slidingWindowSize(10)
                        .build());
    }

    @Override
    public PaymentDto read() throws Exception {
        return circuitBreaker.executeSupplier(() -> {
            try {
                return delegate.read();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
    }
}
```

## Key Takeaways

- Implement pagination in readers to handle large API result sets
- Use rate limiters to respect API quotas (Resilience4j integrates cleanly)
- Configure retry with exponential backoff for transient API failures
- Prefer bulk API endpoints when available to reduce round trips
- Circuit breakers prevent cascading failures when APIs are down
- Webhook triggers enable event-driven batch processing
- OAuth2 token refresh should be thread-safe and proactive
