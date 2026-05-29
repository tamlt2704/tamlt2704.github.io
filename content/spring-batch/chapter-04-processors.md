# Chapter 4: ItemProcessors

[prev: Readers](chapter-03-readers.md) | [next: Writers](chapter-05-writers.md)

## Basic ItemProcessor

An `ItemProcessor<I, O>` transforms an input item of type I into an output item of type O.

```java
@Bean
public ItemProcessor<Person, PersonDto> personProcessor() {
    return person -> new PersonDto(
            person.firstName().toUpperCase(),
            person.lastName().toUpperCase(),
            person.email().toLowerCase(),
            person.age()
    );
}
```

## Filtering Items (Return null to Skip)

Returning `null` from a processor tells Spring Batch to skip the item — it will not be passed to the writer.

```java
@Bean
public ItemProcessor<Person, Person> adultFilter() {
    return person -> person.age() >= 18 ? person : null;
}
```

## CompositeItemProcessor (Chaining)

Chain multiple processors in sequence. Each processor's output becomes the next processor's input.

```java
@Bean
public CompositeItemProcessor<Person, PersonDto> compositeProcessor() {
    CompositeItemProcessor<Person, PersonDto> composite = new CompositeItemProcessor<>();
    composite.setDelegates(List.of(
            validatingProcessor(),
            adultFilter(),
            personTransformer()
    ));
    return composite;
}

@Bean
public ItemProcessor<Person, Person> validatingProcessor() {
    return person -> {
        if (person.email() == null || person.email().isBlank()) {
            return null; // skip invalid
        }
        return person;
    };
}

@Bean
public ItemProcessor<Person, Person> adultFilter() {
    return person -> person.age() >= 18 ? person : null;
}

@Bean
public ItemProcessor<Person, PersonDto> personTransformer() {
    return person -> new PersonDto(
            person.firstName().toUpperCase(),
            person.lastName().toUpperCase(),
            person.email().toLowerCase(),
            person.age()
    );
}
```

## ValidatingItemProcessor (Bean Validation)

Validates items using JSR-380 (Bean Validation) annotations. Throws `ValidationException` on failure.

Add dependency:

```groovy
implementation 'org.springframework.boot:spring-boot-starter-validation'
```

The validated model:

```java
public class PersonInput {
    @NotBlank
    private String firstName;

    @NotBlank
    private String lastName;

    @Email
    @NotBlank
    private String email;

    @Min(0)
    @Max(150)
    private int age;

    // constructors, getters, setters
}
```

Configure the validating processor:

```java
@Bean
public ValidatingItemProcessor<PersonInput> validatingProcessor(Validator validator) {
    ValidatingItemProcessor<PersonInput> processor = new ValidatingItemProcessor<>();
    processor.setValidator(new SpringValidator<>(validator));
    processor.setFilter(true); // filter instead of throwing exception
    return processor;
}
```

Custom Spring Batch Validator adapter:

```java
public class SpringValidator<T> implements org.springframework.batch.item.validator.Validator<T> {

    private final Validator validator;

    public SpringValidator(Validator validator) {
        this.validator = validator;
    }

    @Override
    public void validate(T value) throws ValidationException {
        Set<ConstraintViolation<T>> violations = validator.validate(value);
        if (!violations.isEmpty()) {
            String message = violations.stream()
                    .map(v -> v.getPropertyPath() + ": " + v.getMessage())
                    .collect(Collectors.joining(", "));
            throw new ValidationException(message);
        }
    }
}
```

## Conditional Processing

Apply different logic based on item properties:

```java
@Bean
public ItemProcessor<Order, Order> conditionalProcessor() {
    return order -> {
        if (order.total() > 1000) {
            return order.withDiscount(0.10); // 10% discount for large orders
        } else if (order.total() > 500) {
            return order.withDiscount(0.05); // 5% discount
        }
        return order; // no discount
    };
}
```

## ClassifierCompositeItemProcessor

Routes items to different processors based on a classifier. Each item type gets its own processing logic.

```java
@Bean
public ClassifierCompositeItemProcessor<Transaction, Transaction> classifierProcessor() {
    ClassifierCompositeItemProcessor<Transaction, Transaction> processor =
            new ClassifierCompositeItemProcessor<>();

    Map<String, ItemProcessor<Transaction, Transaction>> processorMap = Map.of(
            "CREDIT", creditProcessor(),
            "DEBIT", debitProcessor(),
            "TRANSFER", transferProcessor()
    );

    processor.setClassifier(new Classifier<Transaction, ItemProcessor<?, ? extends Transaction>>() {
        @Override
        public ItemProcessor<Transaction, Transaction> classify(Transaction transaction) {
            return processorMap.getOrDefault(transaction.type(), noOpProcessor());
        }
    });

    return processor;
}

@Bean
public ItemProcessor<Transaction, Transaction> creditProcessor() {
    return tx -> tx.withProcessedDate(LocalDate.now()).withFee(0.0);
}

@Bean
public ItemProcessor<Transaction, Transaction> debitProcessor() {
    return tx -> tx.withProcessedDate(LocalDate.now()).withFee(tx.amount() * 0.01);
}

@Bean
public ItemProcessor<Transaction, Transaction> transferProcessor() {
    return tx -> tx.withProcessedDate(LocalDate.now()).withFee(2.50);
}

@Bean
public ItemProcessor<Transaction, Transaction> noOpProcessor() {
    return tx -> tx;
}
```

## Complete Job Example with Processor

```java
@Configuration
public class PersonImportJobConfig {

    @Bean
    public Job personImportJob(JobRepository jobRepository, Step importStep) {
        return new JobBuilder("personImportJob", jobRepository)
                .start(importStep)
                .build();
    }

    @Bean
    public Step importStep(JobRepository jobRepository,
                           PlatformTransactionManager transactionManager,
                           FlatFileItemReader<Person> reader,
                           CompositeItemProcessor<Person, PersonDto> processor,
                           JdbcBatchItemWriter<PersonDto> writer) {
        return new StepBuilder("importStep", jobRepository)
                .<Person, PersonDto>chunk(500, transactionManager)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .build();
    }
}
```

## Exercises

1. Write a processor that filters out records with invalid email addresses (no @ sign) and transforms valid emails to lowercase.
2. Create a `CompositeItemProcessor` that chains: validation, deduplication (track seen emails in a Set), and transformation.
3. Implement a `ClassifierCompositeItemProcessor` that routes orders to different processors based on their region (US, EU, APAC).
4. Process a CSV of 1M records: filter out minors, validate emails, uppercase names. Measure throughput with chunk sizes of 100, 500, and 1000.
