# Chapter 14: Reporting & Aggregation

[prev: API Integration](chapter-13-api-integration.md) | [next: Event-Driven Batch](chapter-15-event-driven.md)

## Batch Reporting Patterns

Products need scheduled reports: daily summaries, monthly invoices, compliance reports, analytics aggregations. Spring Batch handles the heavy lifting.

## Aggregation with ItemProcessor

```java
@Component
@StepScope
public class DailyAggregationProcessor implements ItemProcessor<Transaction, DailySummary> {

    private final Map<String, DailySummary> aggregations = new ConcurrentHashMap<>();

    @Override
    public DailySummary process(Transaction tx) {
        String key = tx.getAccountId() + "|" + tx.getDate();

        aggregations.compute(key, (k, existing) -> {
            DailySummary summary = existing != null ? existing : new DailySummary(tx.getAccountId(), tx.getDate());
            if ("DEBIT".equals(tx.getType())) {
                summary.addDebit(tx.getAmount());
            } else {
                summary.addCredit(tx.getAmount());
            }
            summary.incrementCount();
            return summary;
        });

        return null; // Don't pass through — flush in completion callback
    }

    public Collection<DailySummary> getAggregations() {
        return aggregations.values();
    }
}
```

## Group-By Aggregation with Custom Step

```java
@Bean
public Step aggregationStep(JobRepository jobRepository,
                            PlatformTransactionManager txManager) {
    return new StepBuilder("aggregate", jobRepository)
            .<Transaction, MonthlySummary>chunk(5000, txManager)
            .reader(transactionReader())
            .processor(new ItemProcessor<>() {
                private final Map<String, MonthlySummary> buffer = new HashMap<>();

                @Override
                public MonthlySummary process(Transaction tx) {
                    String key = tx.getAccountId();
                    buffer.merge(key, MonthlySummary.from(tx), MonthlySummary::merge);
                    return null;
                }
            })
            .writer(items -> {}) // no-op, real write happens in listener
            .listener(new StepExecutionListener() {
                @Override
                public ExitStatus afterStep(StepExecution stepExecution) {
                    // Flush aggregations
                    summaryWriter.write(new Chunk<>(new ArrayList<>(buffer.values())));
                    return ExitStatus.COMPLETED;
                }
            })
            .build();
}
```

## SQL-Based Aggregation (Tasklet)

For simpler cases, let the database do the work:

```java
@Bean
public Step sqlAggregationStep(JobRepository jobRepository,
                               PlatformTransactionManager txManager) {
    return new StepBuilder("sqlAggregate", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                String reportDate = chunkContext.getStepContext()
                        .getJobParameters().get("reportDate").toString();

                jdbc.execute("""
                    INSERT INTO daily_account_summary (account_id, report_date, total_debits,
                        total_credits, transaction_count, net_amount)
                    SELECT
                        account_id,
                        ?::date as report_date,
                        SUM(CASE WHEN type = 'DEBIT' THEN amount ELSE 0 END) as total_debits,
                        SUM(CASE WHEN type = 'CREDIT' THEN amount ELSE 0 END) as total_credits,
                        COUNT(*) as transaction_count,
                        SUM(CASE WHEN type = 'CREDIT' THEN amount ELSE -amount END) as net_amount
                    FROM transactions
                    WHERE transaction_date = ?::date
                    GROUP BY account_id
                    ON CONFLICT (account_id, report_date) DO UPDATE SET
                        total_debits = EXCLUDED.total_debits,
                        total_credits = EXCLUDED.total_credits,
                        transaction_count = EXCLUDED.transaction_count,
                        net_amount = EXCLUDED.net_amount
                """);

                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## PDF Report Generation

```java
@Component
public class PdfReportWriter implements ItemWriter<AccountSummary> {

    @Override
    public void write(Chunk<? extends AccountSummary> items) throws Exception {
        Document document = new Document(PageSize.A4);
        String outputPath = "reports/monthly-%s.pdf".formatted(YearMonth.now().minusMonths(1));
        PdfWriter.getInstance(document, new FileOutputStream(outputPath));
        document.open();

        // Header
        document.add(new Paragraph("Monthly Account Summary", FontFactory.getFont(FontFactory.HELVETICA_BOLD, 18)));
        document.add(new Paragraph("Period: " + YearMonth.now().minusMonths(1)));
        document.add(Chunk.NEWLINE);

        // Table
        PdfPTable table = new PdfPTable(5);
        table.setWidthPercentage(100);
        Stream.of("Account", "Debits", "Credits", "Net", "Tx Count")
                .forEach(h -> table.addCell(new PdfPCell(new Phrase(h, FontFactory.getFont(FontFactory.HELVETICA_BOLD)))));

        for (AccountSummary summary : items) {
            table.addCell(summary.getAccountId());
            table.addCell(summary.getTotalDebits().toString());
            table.addCell(summary.getTotalCredits().toString());
            table.addCell(summary.getNetAmount().toString());
            table.addCell(String.valueOf(summary.getTransactionCount()));
        }

        document.add(table);
        document.close();
    }
}
```

## Email Report Delivery

```java
@Bean
public Step emailReportStep(JobRepository jobRepository,
                            PlatformTransactionManager txManager) {
    return new StepBuilder("emailReport", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                String reportPath = chunkContext.getStepContext()
                        .getStepExecution().getJobExecution()
                        .getExecutionContext().getString("reportPath");

                MimeMessage message = mailSender.createMimeMessage();
                MimeMessageHelper helper = new MimeMessageHelper(message, true);
                helper.setTo("finance@company.com");
                helper.setSubject("Daily Transaction Report - " + LocalDate.now());
                helper.setText("Please find attached the daily transaction report.");
                helper.addAttachment("daily-report.pdf", new File(reportPath));

                mailSender.send(message);
                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## Multi-Format Report Generation

```java
@Bean
public Job reportingJob(JobRepository jobRepository,
                        Step aggregateStep,
                        Step generateCsvStep,
                        Step generatePdfStep,
                        Step generateExcelStep,
                        Step distributeStep) {

    // Generate all formats in parallel
    Flow reportFormats = new FlowBuilder<SimpleFlow>("reportFormats")
            .split(new SimpleAsyncTaskExecutor())
            .add(
                    new FlowBuilder<SimpleFlow>("csv").start(generateCsvStep).build(),
                    new FlowBuilder<SimpleFlow>("pdf").start(generatePdfStep).build(),
                    new FlowBuilder<SimpleFlow>("excel").start(generateExcelStep).build()
            )
            .build();

    return new JobBuilder("reportingJob", jobRepository)
            .start(aggregateStep)
            .next(reportFormats)
            .next(distributeStep)
            .end()
            .build();
}
```

## Rolling Window Aggregations

```java
@Bean
public Step rollingAverageStep(JobRepository jobRepository,
                               PlatformTransactionManager txManager) {
    return new StepBuilder("rollingAverage", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                jdbc.execute("""
                    INSERT INTO metrics_7day_rolling (metric_date, account_id, avg_daily_volume, avg_transaction_size)
                    SELECT
                        CURRENT_DATE as metric_date,
                        account_id,
                        AVG(daily_volume) as avg_daily_volume,
                        AVG(avg_tx_size) as avg_transaction_size
                    FROM (
                        SELECT
                            account_id,
                            transaction_date,
                            COUNT(*) as daily_volume,
                            AVG(amount) as avg_tx_size
                        FROM transactions
                        WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days'
                        GROUP BY account_id, transaction_date
                    ) daily_stats
                    GROUP BY account_id
                """);
                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## Scheduled Report Pipeline

```java
@Component
public class ReportScheduler {

    private final JobLauncher jobLauncher;
    private final Job reportingJob;

    // Daily at 6 AM
    @Scheduled(cron = "0 0 6 * * *")
    public void dailyReport() throws Exception {
        jobLauncher.run(reportingJob, new JobParametersBuilder()
                .addString("reportType", "daily")
                .addString("reportDate", LocalDate.now().minusDays(1).toString())
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters());
    }

    // Monthly on 1st at 7 AM
    @Scheduled(cron = "0 0 7 1 * *")
    public void monthlyReport() throws Exception {
        jobLauncher.run(reportingJob, new JobParametersBuilder()
                .addString("reportType", "monthly")
                .addString("reportMonth", YearMonth.now().minusMonths(1).toString())
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters());
    }
}
```

## Key Takeaways

- Use SQL aggregation for simple group-by operations — let the database optimize
- In-memory aggregation via processors works for complex business logic
- Generate reports in parallel (CSV, PDF, Excel) using split flows
- Rolling window aggregations are ideal for dashboards and alerting
- Always make report generation idempotent (use ON CONFLICT / MERGE)
- Separate aggregation from formatting — aggregate once, render many formats
