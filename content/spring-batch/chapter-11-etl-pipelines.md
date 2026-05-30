# Chapter 11: ETL Pipelines

[prev: Data Migration](chapter-10-data-migration.md) | [next: File Processing](chapter-12-file-processing.md)

## ETL with Spring Batch

Extract-Transform-Load is the bread and butter of batch processing. Spring Batch maps perfectly:

- **Extract** → ItemReader (pull from source systems)
- **Transform** → ItemProcessor (clean, enrich, reshape)
- **Load** → ItemWriter (push to data warehouse/lake)

## Multi-Source ETL Job

```java
@Configuration
public class SalesEtlConfig {

    @Bean
    public Job salesEtlJob(JobRepository jobRepository,
                           Step extractOrdersStep,
                           Step extractInventoryStep,
                           Step transformStep,
                           Step loadWarehouseStep) {
        Flow extractFlow = new FlowBuilder<SimpleFlow>("extractFlow")
                .split(new SimpleAsyncTaskExecutor())
                .add(
                        new FlowBuilder<SimpleFlow>("orders").start(extractOrdersStep).build(),
                        new FlowBuilder<SimpleFlow>("inventory").start(extractInventoryStep).build()
                )
                .build();

        return new JobBuilder("salesEtlJob", jobRepository)
                .start(extractFlow)
                .next(transformStep)
                .next(loadWarehouseStep)
                .end()
                .build();
    }
}
```

## Extract: Reading from Multiple Sources

### From REST API

```java
@Component
@StepScope
public class ApiItemReader implements ItemReader<OrderDto> {

    private final RestClient restClient;
    private int page = 0;
    private List<OrderDto> buffer = new ArrayList<>();
    private int bufferIndex = 0;

    @Override
    public OrderDto read() {
        if (bufferIndex >= buffer.size()) {
            buffer = fetchNextPage();
            bufferIndex = 0;
            if (buffer.isEmpty()) return null;
        }
        return buffer.get(bufferIndex++);
    }

    private List<OrderDto> fetchNextPage() {
        OrderPageResponse response = restClient.get()
                .uri("/api/orders?page={page}&size=100&since={date}", page, LocalDate.now().minusDays(1))
                .retrieve()
                .body(OrderPageResponse.class);
        page++;
        return response != null ? response.getContent() : List.of();
    }
}
```

### From Kafka Topic (Batch Consume)

```java
@Component
@StepScope
public class KafkaBatchReader implements ItemReader<SalesEvent> {

    private final KafkaConsumer<String, SalesEvent> consumer;
    private Iterator<ConsumerRecord<String, SalesEvent>> iterator;

    @Override
    public SalesEvent read() {
        if (iterator == null || !iterator.hasNext()) {
            ConsumerRecords<String, SalesEvent> records = consumer.poll(Duration.ofSeconds(5));
            if (records.isEmpty()) return null;
            iterator = records.iterator();
        }
        return iterator.hasNext() ? iterator.next().value() : null;
    }
}
```

### From S3 Files

```java
@Bean
@StepScope
public FlatFileItemReader<RawSalesRecord> s3FileReader(
        @Value("#{jobParameters['s3Key']}") String s3Key) {

    Resource s3Resource = new S3Resource(s3Client, "data-bucket", s3Key);

    return new FlatFileItemReaderBuilder<RawSalesRecord>()
            .name("s3SalesReader")
            .resource(s3Resource)
            .delimited()
            .delimiter(",")
            .names("orderId", "product", "quantity", "price", "timestamp")
            .targetType(RawSalesRecord.class)
            .linesToSkip(1) // header
            .build();
}
```

## Transform: Data Cleaning and Enrichment

```java
@Component
public class SalesTransformProcessor implements ItemProcessor<RawSalesRecord, SalesFact> {

    private final ProductCatalog catalog;
    private final ExchangeRateService exchangeRates;
    private final GeoLocationService geoService;

    @Override
    public SalesFact process(RawSalesRecord raw) {
        // Skip invalid records
        if (raw.getQuantity() <= 0 || raw.getPrice() == null) return null;

        SalesFact fact = new SalesFact();
        fact.setOrderId(raw.getOrderId());
        fact.setProductId(raw.getProduct());
        fact.setQuantity(raw.getQuantity());

        // Currency normalization
        BigDecimal usdPrice = exchangeRates.toUsd(raw.getPrice(), raw.getCurrency());
        fact.setAmountUsd(usdPrice.multiply(BigDecimal.valueOf(raw.getQuantity())));

        // Dimension enrichment
        Product product = catalog.findById(raw.getProduct());
        fact.setCategoryId(product.getCategoryId());
        fact.setBrandId(product.getBrandId());

        // Time dimension
        Instant ts = Instant.parse(raw.getTimestamp());
        fact.setDateKey(LocalDate.ofInstant(ts, ZoneOffset.UTC).format(DateTimeFormatter.BASIC_ISO_DATE));
        fact.setHourOfDay(ts.atZone(ZoneOffset.UTC).getHour());

        return fact;
    }
}
```

## Load: Writing to Data Warehouse

### Bulk Insert with Staging Table Pattern

```java
@Component
public class WarehouseWriter implements ItemWriter<SalesFact> {

    private final JdbcTemplate warehouseJdbc;

    @Override
    public void write(Chunk<? extends SalesFact> items) throws Exception {
        // 1. Insert into staging table
        warehouseJdbc.batchUpdate(
                "INSERT INTO staging_sales_fact (order_id, product_id, category_id, brand_id, " +
                "quantity, amount_usd, date_key, hour_of_day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                items.getItems().stream().map(f -> new Object[]{
                        f.getOrderId(), f.getProductId(), f.getCategoryId(), f.getBrandId(),
                        f.getQuantity(), f.getAmountUsd(), f.getDateKey(), f.getHourOfDay()
                }).toList()
        );
    }
}
```

### Post-Load Merge Step

```java
@Bean
public Step mergeToFactTable(JobRepository jobRepository,
                             PlatformTransactionManager txManager) {
    return new StepBuilder("mergeToFactTable", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                warehouseJdbc.execute("""
                    INSERT INTO sales_fact (order_id, product_id, category_id, brand_id,
                                           quantity, amount_usd, date_key, hour_of_day)
                    SELECT order_id, product_id, category_id, brand_id,
                           quantity, amount_usd, date_key, hour_of_day
                    FROM staging_sales_fact s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM sales_fact f WHERE f.order_id = s.order_id
                    )
                """);
                warehouseJdbc.execute("TRUNCATE TABLE staging_sales_fact");
                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## Slowly Changing Dimensions (SCD Type 2)

```java
@Component
public class ScdType2Writer implements ItemWriter<ProductDimension> {

    private final JdbcTemplate jdbc;

    @Override
    public void write(Chunk<? extends ProductDimension> items) throws Exception {
        for (ProductDimension incoming : items) {
            ProductDimension current = jdbc.queryForObject(
                    "SELECT * FROM dim_product WHERE product_id = ? AND is_current = true",
                    new ProductDimensionRowMapper(), incoming.getProductId());

            if (current == null) {
                // New record
                incoming.setIsCurrent(true);
                incoming.setValidFrom(LocalDate.now());
                incoming.setValidTo(LocalDate.of(9999, 12, 31));
                insertDimension(incoming);
            } else if (!current.equals(incoming)) {
                // Close old record
                jdbc.update("UPDATE dim_product SET is_current = false, valid_to = ? WHERE id = ?",
                        LocalDate.now().minusDays(1), current.getId());
                // Insert new version
                incoming.setIsCurrent(true);
                incoming.setValidFrom(LocalDate.now());
                incoming.setValidTo(LocalDate.of(9999, 12, 31));
                insertDimension(incoming);
            }
            // No change → skip
        }
    }
}
```

## Data Quality Checks

```java
@Bean
public Step dataQualityStep(JobRepository jobRepository,
                            PlatformTransactionManager txManager) {
    return new StepBuilder("dataQuality", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                Map<String, Long> checks = new LinkedHashMap<>();

                checks.put("null_amounts", warehouseJdbc.queryForObject(
                        "SELECT COUNT(*) FROM staging_sales_fact WHERE amount_usd IS NULL", Long.class));
                checks.put("negative_quantities", warehouseJdbc.queryForObject(
                        "SELECT COUNT(*) FROM staging_sales_fact WHERE quantity < 0", Long.class));
                checks.put("future_dates", warehouseJdbc.queryForObject(
                        "SELECT COUNT(*) FROM staging_sales_fact WHERE date_key > ?", Long.class,
                        LocalDate.now().format(DateTimeFormatter.BASIC_ISO_DATE)));

                long totalIssues = checks.values().stream().mapToLong(Long::longValue).sum();

                if (totalIssues > 0) {
                    log.warn("Data quality issues found: {}", checks);
                    contribution.getStepExecution().getExecutionContext()
                            .put("qualityIssues", checks.toString());
                }

                // Fail if issues exceed threshold
                long totalRecords = warehouseJdbc.queryForObject(
                        "SELECT COUNT(*) FROM staging_sales_fact", Long.class);
                double errorRate = (double) totalIssues / totalRecords;

                if (errorRate > 0.05) {
                    throw new DataQualityException("Error rate %.2f%% exceeds 5%% threshold".formatted(errorRate * 100));
                }

                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## Incremental ETL with Watermarks

```java
@Component
@StepScope
public class WatermarkReader implements ItemReader<RawSalesRecord> {

    private final JdbcPagingItemReader<RawSalesRecord> delegate;

    public WatermarkReader(@Qualifier("sourceDataSource") DataSource source,
                           JobRepository jobRepository) {
        // Get last successful watermark
        Instant lastWatermark = getLastWatermark(jobRepository);

        this.delegate = new JdbcPagingItemReaderBuilder<RawSalesRecord>()
                .name("watermarkReader")
                .dataSource(source)
                .selectClause("SELECT *")
                .fromClause("FROM sales_events")
                .whereClause("WHERE event_time > :lastWatermark")
                .sortKeys(Map.of("event_time", Order.ASCENDING))
                .parameterValues(Map.of("lastWatermark", Timestamp.from(lastWatermark)))
                .pageSize(1000)
                .rowMapper(new SalesRecordRowMapper())
                .build();
    }

    private Instant getLastWatermark(JobRepository jobRepository) {
        // Query last successful job execution for watermark
        // Falls back to epoch if no previous run
        return Instant.EPOCH;
    }

    @Override
    public RawSalesRecord read() throws Exception {
        return delegate.read();
    }
}
```

## Scheduling ETL Pipelines

```java
@Component
public class EtlScheduler {

    private final JobLauncher jobLauncher;
    private final Job salesEtlJob;

    // Hourly micro-batch
    @Scheduled(cron = "0 5 * * * *") // 5 minutes past every hour
    public void hourlyEtl() throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addString("runType", "hourly")
                .addString("hour", LocalDateTime.now().minusHours(1).format(DateTimeFormatter.ofPattern("yyyyMMddHH")))
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters();
        jobLauncher.run(salesEtlJob, params);
    }

    // Daily full reconciliation
    @Scheduled(cron = "0 0 4 * * *") // 4 AM daily
    public void dailyReconciliation() throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addString("runType", "daily")
                .addString("date", LocalDate.now().minusDays(1).toString())
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters();
        jobLauncher.run(salesEtlJob, params);
    }
}
```

## Key Takeaways

- Use parallel flows to extract from multiple sources simultaneously
- Staging tables + merge pattern prevents duplicates and enables idempotency
- Data quality checks should run before merging to production tables
- Watermark-based incremental loads avoid reprocessing entire datasets
- SCD Type 2 pattern preserves historical dimension changes
- Schedule micro-batches hourly with daily full reconciliation as safety net
