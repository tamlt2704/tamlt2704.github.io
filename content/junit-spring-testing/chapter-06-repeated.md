# Repeated and Dynamic Tests

## @RepeatedTest

Run the same test multiple times to detect flaky behavior or race conditions.

```java
package com.example.service;

import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.RepetitionInfo;

import static org.junit.jupiter.api.Assertions.*;

class RepeatedTestExample {

    @RepeatedTest(5)
    void randomAlwaysPositive() {
        double value = Math.random();
        assertTrue(value >= 0.0 && value < 1.0);
    }

    @RepeatedTest(value = 3, name = "Repetition {currentRepetition} of {totalRepetitions}")
    void withRepetitionInfo(RepetitionInfo info) {
        assertTrue(info.getCurrentRepetition() <= info.getTotalRepetitions());
    }
}
```

## @TestFactory — Dynamic Tests

Generate tests at runtime based on data or conditions.

```java
package com.example.service;

import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

import java.util.Map;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;
import static org.junit.jupiter.api.DynamicTest.dynamicTest;

class DynamicTestExample {

    private final StringValidator validator = new StringValidator();

    @TestFactory
    Stream<DynamicTest> dynamicGradeTests() {
        Map<Integer, String> cases = Map.of(
            100, "A",
            85, "B",
            72, "C",
            61, "D",
            45, "F"
        );

        return cases.entrySet().stream()
            .map(entry -> dynamicTest(
                "Score " + entry.getKey() + " -> " + entry.getValue(),
                () -> assertEquals(entry.getValue(), validator.classify(entry.getKey()))
            ));
    }
}
```

## Detecting Flaky Tests

A flaky test passes sometimes and fails other times. Common causes:

- Shared mutable state between tests
- Time-dependent logic
- Non-deterministic ordering
- External service dependencies

Strategy: use `@RepeatedTest` during investigation to reproduce intermittent failures.

```java
package com.example.service;

import org.junit.jupiter.api.RepeatedTest;

import java.time.LocalTime;

import static org.junit.jupiter.api.Assertions.*;

class FlakyDetectionTest {

    // This test is intentionally flaky — demonstrates the problem
    @RepeatedTest(10)
    void timeBasedLogic_canBeFlaky() {
        LocalTime now = LocalTime.of(10, 0); // Fix the time to avoid flakiness
        assertTrue(now.getHour() < 24);
    }
}
```

## Combining with @TestFactory for Data-Driven Suites

```java
package com.example.service;

import org.junit.jupiter.api.DynamicNode;
import org.junit.jupiter.api.DynamicContainer;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;
import static org.junit.jupiter.api.DynamicContainer.dynamicContainer;
import static org.junit.jupiter.api.DynamicTest.dynamicTest;

class DynamicContainerExample {

    private final StringValidator validator = new StringValidator();

    @TestFactory
    Stream<DynamicNode> groupedDynamicTests() {
        return Stream.of(
            dynamicContainer("Passing grades", Stream.of(
                dynamicTest("90 is A", () -> assertEquals("A", validator.classify(90))),
                dynamicTest("80 is B", () -> assertEquals("B", validator.classify(80)))
            )),
            dynamicContainer("Failing grades", Stream.of(
                dynamicTest("50 is F", () -> assertEquals("F", validator.classify(50))),
                dynamicTest("0 is F", () -> assertEquals("F", validator.classify(0)))
            ))
        );
    }
}
```

## Key Points

- `@RepeatedTest(n)` runs the test n times — useful for flaky test detection
- `RepetitionInfo` gives access to current/total repetition count
- `@TestFactory` returns `Stream<DynamicTest>` — tests generated at runtime
- `DynamicContainer` groups dynamic tests hierarchically
- Fix flaky tests by eliminating shared state and non-determinism

[prev: Parameterized Tests](/blog/junit-spring-testing/chapter-05-parameterized) | [next: REST Testing](/blog/junit-spring-testing/chapter-07-rest-testing)
