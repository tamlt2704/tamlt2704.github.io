# Chapter 5: ItemWriters

[prev: Processors](chapter-04-processors.md) | [next: Flow Control](chapter-06-flow.md)

## FlatFileItemWriter (CSV Output)

Writes items to a delimited flat file.

```java
@Bean
@StepScope
public FlatFileItemWriter<PersonDto> csvWriter(
        @Value("#{jobParameters['outputFile']}") String outputFile) {
    return new FlatFileItemWriterBuilder<PersonDto>()
            .name("csvWriter")
            .resource(new FileSystemResource(outputFile))
            .delimited()
            .delimiter(",")
            .names("firstName", "lastName", "email", "age")
            .headerCallback(writer -> writer.write("first_name,last_name,email,age"))
            .footerCallback(writer -> writer.write("# End of file"))
            .build();
}
```

### Formatted Output

```java
@Bean
public FlatFileItemWriter<PersonDto> formattedWriter() {
    return new FlatFileItemWriterBuilder<PersonDto>()
            .name("formattedWriter")
            .resource(new FileSystemResource("output/people.txt"))
            .formatted()
            .format("%-20s %-20s %-30s %3d")
            .names("firstName", "lastName", "email", "age")
            .build();
}
```

## JdbcBatchItemWriter

Writes items to a database using JDBC batch operations. Very efficient for bulk inserts.

```java
@Bean
public JdbcBatchItemWriter<PersonDto> jdbcWriter(DataSource dataSource) {
    return new JdbcBatchItemWriterBuilder<PersonDto>()
            .dataSource(dataSource)
            .sql("INSERT INTO person_output (first_name, last_name, email, age) " +
                 "VALUES (:firstName, :lastName, :email, :age)")
            .beanMapped()
            .build();
}
```

With `ItemPreparedStatementSetter` for positional parameters:

```java
@Bean
public JdbcBatchItemWriter<PersonDto> jdbcWriter(DataSource dataSource) {
    return new JdbcBatchItemWriterBuilder<PersonDto>()
            .dataSource(dataSource)
            .sql("INSERT INTO person_output (first_name, last_name, email, age) VALUES (?, ?, ?, ?)")
            .itemPreparedStatementSetter((item, ps) -> {
                ps.setString(1, item.firstName());
                ps.setString(2, item.lastName());
                ps.setString(3, item.email());
                ps.setInt(4, item.age());
            })
            .build();
}
```

## JpaItemWriter

Uses JPA EntityManager to persist entities. Handles both inserts and updates (merge).

```java
@Bean
public JpaItemWriter<PersonEntity> jpaWriter(EntityManagerFactory emf) {
    JpaItemWriter<PersonEntity> writer = new JpaItemWriter<>();
    writer.setEntityManagerFactory(emf);
    return writer;
}
```

With a processor that converts DTO to entity:

```java
@Bean
public ItemProcessor<PersonDto, PersonEntity> toEntityProcessor() {
    return dto -> {
        PersonEntity entity = new PersonEntity();
        entity.setFirstName(dto.firstName());
        entity.setLastName(dto.lastName());
        entity.setEmail(dto.email());
        entity.setAge(dto.age());
        return entity;
    };
}
```

## JsonFileItemWriter

Writes items as a JSON array to a file.

```java
@Bean
@StepScope
public JsonFileItemWriter<PersonDto> jsonWriter(
        @Value("#{jobParameters['outputFile']}") String outputFile) {
    return new JsonFileItemWriterBuilder<PersonDto>()
            .name("jsonWriter")
            .resource(new FileSystemResource(outputFile))
            .jsonObjectMarshaller(new JacksonJsonObjectMarshaller<>())
            .build();
}
```

Output:

```json
[
  { "firstName": "JOHN", "lastName": "DOE", "email": "john@example.com", "age": 30 },
  { "firstName": "JANE", "lastName": "DOE", "email": "jane@example.com", "age": 25 }
]
```

## CompositeItemWriter (Multiple Destinations)

Write the same items to multiple destinations simultaneously.

```java
@Bean
public CompositeItemWriter<PersonDto> compositeWriter(
        JdbcBatchItemWriter<PersonDto> dbWriter,
        FlatFileItemWriter<PersonDto> fileWriter,
        JsonFileItemWriter<PersonDto> jsonWriter) {
    CompositeItemWriter<PersonDto> composite = new CompositeItemWriter<>();
    composite.setDelegates(List.of(dbWriter, fileWriter, jsonWriter));
    return composite;
}
```

Register all delegates as streams for proper open/close lifecycle:

```java
@Bean
public Step multiWriteStep(JobRepository jobRepository,
                           PlatformTransactionManager transactionManager,
                           ItemReader<Person> reader,
                           CompositeItemWriter<PersonDto> compositeWriter,
                           FlatFileItemWriter<PersonDto> fileWriter,
                           JsonFileItemWriter<PersonDto> jsonWriter) {
    return new StepBuilder("multiWriteStep", jobRepository)
            .<Person, PersonDto>chunk(500, transactionManager)
            .reader(reader)
            .writer(compositeWriter)
            .stream(fileWriter)
            .stream(jsonWriter)
            .build();
}
```

## Custom ItemWriter

Implement `ItemWriter<T>` for custom write logic:

```java
@Component
public class ApiItemWriter implements ItemWriter<PersonDto> {

    private final RestClient restClient;

    public ApiItemWriter(RestClient.Builder builder) {
        this.restClient = builder.baseUrl("https://api.example.com").build();
    }

    @Override
    public void write(Chunk<? extends PersonDto> chunk) {
        restClient.post()
                .uri("/people/batch")
                .body(chunk.getItems())
                .retrieve()
                .toBodilessEntity();
    }
}
```

## ClassifierCompositeItemWriter

Routes items to different writers based on a classifier.

```java
@Bean
public ClassifierCompositeItemWriter<Transaction> classifierWriter(
        JdbcBatchItemWriter<Transaction> dbWriter,
        FlatFileItemWriter<Transaction> errorFileWriter) {

    ClassifierCompositeItemWriter<Transaction> writer = new ClassifierCompositeItemWriter<>();
    writer.setClassifier(new Classifier<Transaction, ItemWriter<? super Transaction>>() {
        @Override
        public ItemWriter<? super Transaction> classify(Transaction tx) {
            if (tx.status().equals("ERROR")) {
                return errorFileWriter;
            }
            return dbWriter;
        }
    });
    return writer;
}
```

Register streams for file-based delegates:

```java
@Bean
public Step classifiedWriteStep(JobRepository jobRepository,
                                PlatformTransactionManager transactionManager,
                                ItemReader<Transaction> reader,
                                ClassifierCompositeItemWriter<Transaction> writer,
                                FlatFileItemWriter<Transaction> errorFileWriter) {
    return new StepBuilder("classifiedWriteStep", jobRepository)
            .<Transaction, Transaction>chunk(500, transactionManager)
            .reader(reader)
            .writer(writer)
            .stream(errorFileWriter)
            .build();
}
```

## Exercises

1. Write a job that reads a CSV and outputs both a JSON file and inserts into a database using `CompositeItemWriter`.
2. Implement a `ClassifierCompositeItemWriter` that routes valid records to a database and invalid records to an error CSV file.
3. Create a custom writer that sends batches to a REST API with retry logic on HTTP 429 responses.
4. Process 1M records from CSV to database using `JdbcBatchItemWriter`. Compare performance with chunk sizes of 100, 500, and 2000.
