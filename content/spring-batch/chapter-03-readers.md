# Chapter 3: ItemReaders

[prev: Setup](chapter-02-setup.md) | [next: Processors](chapter-04-processors.md)

## FlatFileItemReader (CSV)

The most common reader. Reads delimited or fixed-width files line by line.

```java
@Bean
@StepScope
public FlatFileItemReader<Person> csvReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new FlatFileItemReaderBuilder<Person>()
            .name("csvReader")
            .resource(new FileSystemResource(inputFile))
            .linesToSkip(1) // skip header
            .delimited()
            .delimiter(",")
            .names("firstName", "lastName", "email", "age")
            .targetType(Person.class)
            .build();
}
```

The `Person` model:

```java
public record Person(String firstName, String lastName, String email, int age) {}
```

### Custom FieldSetMapper

When the default `BeanWrapperFieldSetMapper` is not enough:

```java
@Bean
public FlatFileItemReader<Person> readerWithCustomMapper() {
    return new FlatFileItemReaderBuilder<Person>()
            .name("customMapperReader")
            .resource(new ClassPathResource("people.csv"))
            .delimited()
            .names("first", "last", "mail", "years")
            .fieldSetMapper(fieldSet -> new Person(
                    fieldSet.readString("first").trim(),
                    fieldSet.readString("last").trim(),
                    fieldSet.readString("mail").toLowerCase(),
                    fieldSet.readInt("years")
            ))
            .build();
}
```

### BeanWrapperFieldSetMapper

Maps columns to bean properties by name automatically:

```java
.fieldSetMapper(new BeanWrapperFieldSetMapper<>() {{
    setTargetType(Person.class);
}})
```

## JdbcCursorItemReader

Opens a database cursor and streams rows one at a time. Low memory footprint.

```java
@Bean
public JdbcCursorItemReader<Person> cursorReader(DataSource dataSource) {
    return new JdbcCursorItemReaderBuilder<Person>()
            .name("cursorReader")
            .dataSource(dataSource)
            .sql("SELECT first_name, last_name, email, age FROM person WHERE status = ?")
            .preparedStatementSetter(ps -> ps.setString(1, "ACTIVE"))
            .rowMapper((rs, rowNum) -> new Person(
                    rs.getString("first_name"),
                    rs.getString("last_name"),
                    rs.getString("email"),
                    rs.getInt("age")
            ))
            .build();
}
```

## JdbcPagingItemReader

Reads in pages using SQL pagination. Thread-safe — suitable for multi-threaded steps.

```java
@Bean
@StepScope
public JdbcPagingItemReader<Person> pagingReader(DataSource dataSource) {
    Map<String, Order> sortKeys = Map.of("id", Order.ASCENDING);

    return new JdbcPagingItemReaderBuilder<Person>()
            .name("pagingReader")
            .dataSource(dataSource)
            .selectClause("SELECT id, first_name, last_name, email, age")
            .fromClause("FROM person")
            .whereClause("WHERE status = :status")
            .parameterValues(Map.of("status", "ACTIVE"))
            .sortKeys(sortKeys)
            .pageSize(1000)
            .rowMapper((rs, rowNum) -> new Person(
                    rs.getString("first_name"),
                    rs.getString("last_name"),
                    rs.getString("email"),
                    rs.getInt("age")
            ))
            .build();
}
```

## JpaPagingItemReader

Uses JPA/Hibernate for reading. Convenient when you already have entity mappings.

```java
@Bean
@StepScope
public JpaPagingItemReader<PersonEntity> jpaReader(EntityManagerFactory emf) {
    return new JpaPagingItemReaderBuilder<PersonEntity>()
            .name("jpaReader")
            .entityManagerFactory(emf)
            .queryString("SELECT p FROM PersonEntity p WHERE p.status = :status")
            .parameterValues(Map.of("status", "ACTIVE"))
            .pageSize(500)
            .build();
}
```

## JsonItemReader

Reads a JSON array file item by item:

```java
@Bean
@StepScope
public JsonItemReader<Person> jsonReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new JsonItemReaderBuilder<Person>()
            .name("jsonReader")
            .resource(new FileSystemResource(inputFile))
            .jsonObjectReader(new JacksonJsonObjectReader<>(Person.class))
            .build();
}
```

Input format:

```json
[
  { "firstName": "John", "lastName": "Doe", "email": "john@example.com", "age": 30 },
  { "firstName": "Jane", "lastName": "Doe", "email": "jane@example.com", "age": 25 }
]
```

## Custom ItemReader

Implement `ItemReader<T>` — return `null` to signal end of input.

```java
@Component
@StepScope
public class ApiItemReader implements ItemReader<Person> {

    private final RestClient restClient;
    private Iterator<Person> iterator;

    public ApiItemReader(RestClient.Builder builder) {
        this.restClient = builder.baseUrl("https://api.example.com").build();
    }

    @Override
    public Person read() {
        if (iterator == null) {
            List<Person> people = restClient.get()
                    .uri("/people")
                    .retrieve()
                    .body(new ParameterizedTypeReference<>() {});
            iterator = people.iterator();
        }
        return iterator.hasNext() ? iterator.next() : null;
    }
}
```

## Reading from APIs with Pagination

```java
@Component
@StepScope
public class PaginatedApiReader implements ItemReader<Person> {

    private final RestClient restClient;
    private int currentPage = 0;
    private Iterator<Person> currentBatch;
    private boolean exhausted = false;

    public PaginatedApiReader(RestClient.Builder builder) {
        this.restClient = builder.baseUrl("https://api.example.com").build();
    }

    @Override
    public Person read() {
        if (exhausted) return null;

        if (currentBatch == null || !currentBatch.hasNext()) {
            List<Person> page = restClient.get()
                    .uri("/people?page={page}&size=100", currentPage++)
                    .retrieve()
                    .body(new ParameterizedTypeReference<>() {});

            if (page == null || page.isEmpty()) {
                exhausted = true;
                return null;
            }
            currentBatch = page.iterator();
        }
        return currentBatch.next();
    }
}
```

## StepScope for Late Binding

`@StepScope` creates a new bean instance for each step execution, enabling:

- Access to `jobParameters` via SpEL
- Access to `stepExecutionContext` for partitioning
- Proper lifecycle management

```java
@Bean
@StepScope
public FlatFileItemReader<Person> reader(
        @Value("#{jobParameters['inputFile']}") String inputFile,
        @Value("#{stepExecutionContext['partitionIndex']}") Integer partition) {
    return new FlatFileItemReaderBuilder<Person>()
            .name("partitionedReader")
            .resource(new FileSystemResource(inputFile + ".part" + partition))
            .delimited()
            .names("firstName", "lastName", "email", "age")
            .targetType(Person.class)
            .build();
}
```

Without `@StepScope`, SpEL expressions like `#{jobParameters['inputFile']}` cannot be resolved because the job has not started yet at bean creation time.

## Exercises

1. Create a CSV file with 10,000 rows and read it using `FlatFileItemReader`. Log every 1000th item.
2. Set up an H2 table with sample data and read it using both `JdbcCursorItemReader` and `JdbcPagingItemReader`. Compare behavior.
3. Implement a custom `ItemReader` that reads from a paginated REST API (mock with WireMock or a local controller).
4. Use `@StepScope` with job parameters to make the input file path configurable at runtime.
