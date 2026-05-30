# Chapter 12: File Processing at Scale

[prev: ETL Pipelines](chapter-11-etl-pipelines.md) | [next: API Integration](chapter-13-api-integration.md)

## File Processing Patterns

Real products deal with: partner data feeds, bank reconciliation files, regulatory reports, bulk imports from customers. Spring Batch excels here.

## Multi-File Processing

### Watching a Directory for New Files

```java
@Bean
@StepScope
public MultiResourceItemReader<Transaction> multiFileReader(
        @Value("#{jobParameters['inputDir']}") String inputDir) {

    Resource[] resources = new PathMatchingResourcePatternResolver()
            .getResources("file:" + inputDir + "/*.csv");

    MultiResourceItemReader<Transaction> reader = new MultiResourceItemReader<>();
    reader.setResources(resources);
    reader.setDelegate(singleFileReader());
    return reader;
}

private FlatFileItemReader<Transaction> singleFileReader() {
    return new FlatFileItemReaderBuilder<Transaction>()
            .name("transactionReader")
            .delimited()
            .names("txId", "accountId", "amount", "currency", "timestamp", "type")
            .targetType(Transaction.class)
            .linesToSkip(1)
            .build();
}
```

### File-Per-Partition Strategy

```java
@Bean
public Partitioner filePartitioner(@Value("${input.dir}") String inputDir) {
    return gridSize -> {
        Resource[] files = new PathMatchingResourcePatternResolver()
                .getResources("file:" + inputDir + "/*.csv");

        Map<String, ExecutionContext> partitions = new HashMap<>();
        for (int i = 0; i < files.length; i++) {
            ExecutionContext ctx = new ExecutionContext();
            ctx.putString("fileName", files[i].getFilename());
            ctx.putString("filePath", files[i].getFile().getAbsolutePath());
            partitions.put("file-" + i, ctx);
        }
        return partitions;
    };
}
```

## Fixed-Width File Parsing

Bank files often use fixed-width format:

```java
@Bean
public FlatFileItemReader<BankStatement> fixedWidthReader() {
    return new FlatFileItemReaderBuilder<BankStatement>()
            .name("bankStatementReader")
            .resource(new ClassPathResource("statements/daily.txt"))
            .fixedLength()
            .columns(new Range[]{
                    new Range(1, 10),    // account number
                    new Range(11, 18),   // date (YYYYMMDD)
                    new Range(19, 30),   // amount (right-aligned, 2 decimals)
                    new Range(31, 31),   // debit/credit flag
                    new Range(32, 71),   // description
                    new Range(72, 83)    // reference
            })
            .names("accountNumber", "date", "amount", "dcFlag", "description", "reference")
            .targetType(BankStatement.class)
            .build();
}
```

## XML File Processing

```java
@Bean
public StaxEventItemReader<Invoice> xmlReader() {
    return new StaxEventItemReaderBuilder<Invoice>()
            .name("invoiceXmlReader")
            .resource(new ClassPathResource("invoices/batch.xml"))
            .addFragmentRootElements("invoice")
            .unmarshaller(invoiceMarshaller())
            .build();
}

@Bean
public Jaxb2Marshaller invoiceMarshaller() {
    Jaxb2Marshaller marshaller = new Jaxb2Marshaller();
    marshaller.setClassesToBeBound(Invoice.class);
    return marshaller;
}
```

## Excel File Processing

```java
@Component
@StepScope
public class ExcelItemReader implements ItemReader<ProductImport> {

    private Iterator<Row> rowIterator;

    @PostConstruct
    public void init(@Value("#{jobParameters['excelFile']}") String filePath) throws Exception {
        Workbook workbook = WorkbookFactory.create(new File(filePath));
        Sheet sheet = workbook.getSheetAt(0);
        rowIterator = sheet.iterator();
        rowIterator.next(); // skip header
    }

    @Override
    public ProductImport read() {
        if (!rowIterator.hasNext()) return null;

        Row row = rowIterator.next();
        ProductImport product = new ProductImport();
        product.setSku(row.getCell(0).getStringCellValue());
        product.setName(row.getCell(1).getStringCellValue());
        product.setPrice(BigDecimal.valueOf(row.getCell(2).getNumericCellValue()));
        product.setCategory(row.getCell(3).getStringCellValue());
        product.setStock((int) row.getCell(4).getNumericCellValue());
        return product;
    }
}
```

## Large File Splitting

For files too large to process in one go:

```java
@Bean
public Step splitFileStep(JobRepository jobRepository,
                          PlatformTransactionManager txManager) {
    return new StepBuilder("splitFile", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                String inputFile = chunkContext.getStepContext()
                        .getJobParameters().get("inputFile").toString();

                Path input = Path.of(inputFile);
                long lineCount = Files.lines(input).count();
                int linesPerSplit = 100_000;
                int splitCount = (int) Math.ceil((double) lineCount / linesPerSplit);

                try (BufferedReader reader = Files.newBufferedReader(input)) {
                    String header = reader.readLine();

                    for (int i = 0; i < splitCount; i++) {
                        Path splitFile = Path.of(inputFile + ".part" + i);
                        try (BufferedWriter writer = Files.newBufferedWriter(splitFile)) {
                            writer.write(header);
                            writer.newLine();
                            for (int line = 0; line < linesPerSplit; line++) {
                                String data = reader.readLine();
                                if (data == null) break;
                                writer.write(data);
                                writer.newLine();
                            }
                        }
                    }
                }

                contribution.getStepExecution().getExecutionContext()
                        .putInt("splitCount", splitCount);
                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## File Validation Before Processing

```java
@Bean
public Step fileValidationStep(JobRepository jobRepository,
                               PlatformTransactionManager txManager) {
    return new StepBuilder("validateFile", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                String filePath = chunkContext.getStepContext()
                        .getJobParameters().get("inputFile").toString();
                Path file = Path.of(filePath);

                // Check file exists and is readable
                if (!Files.isReadable(file)) {
                    throw new FileNotFoundException("Cannot read: " + filePath);
                }

                // Check file size
                long size = Files.size(file);
                if (size == 0) throw new EmptyFileException(filePath);
                if (size > 5_000_000_000L) throw new FileTooLargeException(filePath, size);

                // Validate header
                String header = Files.lines(file).findFirst().orElseThrow();
                String expectedHeader = "txId,accountId,amount,currency,timestamp,type";
                if (!header.equals(expectedHeader)) {
                    throw new InvalidFileFormatException("Header mismatch: " + header);
                }

                // Check for BOM and encoding
                byte[] bom = Files.readAllBytes(file);
                if (bom[0] == (byte) 0xEF && bom[1] == (byte) 0xBB && bom[2] == (byte) 0xBF) {
                    log.warn("File has UTF-8 BOM, will handle accordingly");
                    contribution.getStepExecution().getExecutionContext()
                            .putBoolean("hasBom", true);
                }

                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## Writing Output Files

### CSV Output with Header/Footer

```java
@Bean
public FlatFileItemWriter<ReportLine> csvWriter() {
    return new FlatFileItemWriterBuilder<ReportLine>()
            .name("reportWriter")
            .resource(new FileSystemResource("output/daily-report.csv"))
            .delimited()
            .delimiter(",")
            .names("date", "accountId", "totalDebits", "totalCredits", "balance")
            .headerCallback(writer -> writer.write("Date,Account,Total Debits,Total Credits,Balance"))
            .footerCallback(writer -> writer.write("# Generated: " + Instant.now()))
            .build();
}
```

### Classified Output (Route to Different Files)

```java
@Bean
public ClassifierCompositeItemWriter<Transaction> classifiedWriter() {
    ClassifierCompositeItemWriter<Transaction> writer = new ClassifierCompositeItemWriter<>();
    writer.setClassifier(new Classifier<Transaction, ItemWriter<? super Transaction>>() {
        @Override
        public ItemWriter<? super Transaction> classify(Transaction tx) {
            return switch (tx.getType()) {
                case "DEBIT" -> debitFileWriter();
                case "CREDIT" -> creditFileWriter();
                case "TRANSFER" -> transferFileWriter();
                default -> errorFileWriter();
            };
        }
    });
    return writer;
}
```

## S3 Upload After Processing

```java
@Bean
public Step uploadToS3Step(JobRepository jobRepository,
                           PlatformTransactionManager txManager) {
    return new StepBuilder("uploadToS3", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                String outputFile = "output/daily-report.csv";
                String s3Key = "reports/%s/daily-report.csv".formatted(LocalDate.now());

                s3Client.putObject(
                        PutObjectRequest.builder()
                                .bucket("company-reports")
                                .key(s3Key)
                                .contentType("text/csv")
                                .build(),
                        Path.of(outputFile)
                );

                log.info("Uploaded to s3://company-reports/{}", s3Key);
                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## File Archival Pattern

```java
@Bean
public Step archiveStep(JobRepository jobRepository,
                        PlatformTransactionManager txManager) {
    return new StepBuilder("archiveFiles", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                String inputDir = chunkContext.getStepContext()
                        .getJobParameters().get("inputDir").toString();
                Path archiveDir = Path.of(inputDir, "archive", LocalDate.now().toString());
                Files.createDirectories(archiveDir);

                try (DirectoryStream<Path> stream = Files.newDirectoryStream(Path.of(inputDir), "*.csv")) {
                    for (Path file : stream) {
                        Files.move(file, archiveDir.resolve(file.getFileName()),
                                StandardCopyOption.REPLACE_EXISTING);
                    }
                }
                return RepeatStatus.FINISHED;
            }, txManager)
            .build();
}
```

## Complete File Processing Pipeline

```java
@Bean
public Job fileProcessingJob(JobRepository jobRepository,
                             Step validateFile,
                             Step processFile,
                             Step uploadToS3,
                             Step archiveFiles,
                             Step notifyComplete) {
    return new JobBuilder("fileProcessingJob", jobRepository)
            .start(validateFile)
            .on("FAILED").to(notifyFailure)
            .from(validateFile).on("*").to(processFile)
            .next(uploadToS3)
            .next(archiveFiles)
            .next(notifyComplete)
            .end()
            .build();
}
```

## Key Takeaways

- Use MultiResourceItemReader for processing multiple files in one job
- Partition by file for parallel processing of independent files
- Always validate files before processing (format, encoding, size)
- Use classified writers to route records to different output files
- Implement archive patterns to prevent reprocessing
- Split very large files before processing for better restartability
