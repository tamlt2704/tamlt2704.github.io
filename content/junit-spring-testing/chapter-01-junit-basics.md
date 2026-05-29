# JUnit 5 Basics

## Test Lifecycle

JUnit 5 creates a **new test instance per test method** by default:

1. `@BeforeAll` — once before all tests (static method)
2. `@BeforeEach` — before each test method
3. `@Test` — the test itself
4. `@AfterEach` — after each test method
5. `@AfterAll` — once after all tests (static method)

## Class Under Test

```java
package com.example.service;

public class Calculator {

    public int add(int a, int b) {
        return a + b;
    }

    public int divide(int a, int b) {
        if (b == 0) {
            throw new ArithmeticException("Cannot divide by zero");
        }
        return a / b;
    }

    public boolean isPositive(int number) {
        return number > 0;
    }
}
```

## Basic Test with @Test and Assertions

```java
package com.example.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {

    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    @Test
    @DisplayName("should add two numbers correctly")
    void shouldAdd() {
        assertEquals(5, calculator.add(2, 3));
    }

    @Test
    @DisplayName("should throw when dividing by zero")
    void shouldThrowOnDivideByZero() {
        ArithmeticException ex = assertThrows(
            ArithmeticException.class,
            () -> calculator.divide(10, 0)
        );
        assertEquals("Cannot divide by zero", ex.getMessage());
    }

    @Test
    @DisplayName("should validate multiple assertions together")
    void shouldValidateMultipleAssertions() {
        assertAll("calculator operations",
            () -> assertEquals(4, calculator.add(2, 2)),
            () -> assertEquals(5, calculator.divide(10, 2)),
            () -> assertTrue(calculator.isPositive(1)),
            () -> assertFalse(calculator.isPositive(-1))
        );
    }
}
```

## @Nested Tests for Grouping

```java
package com.example.service;

import org.junit.jupiter.api.*;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Calculator")
class CalculatorNestedTest {

    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    @Nested
    @DisplayName("add")
    class Add {

        @Test
        @DisplayName("returns sum of two positive numbers")
        void positiveNumbers() {
            assertEquals(7, calculator.add(3, 4));
        }

        @Test
        @DisplayName("returns sum with negative numbers")
        void negativeNumbers() {
            assertEquals(-1, calculator.add(2, -3));
        }
    }

    @Nested
    @DisplayName("divide")
    class Divide {

        @Test
        @DisplayName("returns quotient for valid inputs")
        void validDivision() {
            assertEquals(3, calculator.divide(9, 3));
        }

        @Test
        @DisplayName("throws for zero divisor")
        void zeroDivisor() {
            assertThrows(ArithmeticException.class,
                () -> calculator.divide(1, 0));
        }
    }
}
```

## Key Points

- `@DisplayName` provides readable test names in reports
- `assertAll` runs all assertions even if one fails — reports all failures
- `assertThrows` returns the exception for further assertions
- `@Nested` classes share the outer `@BeforeEach` setup
- Each `@Nested` class can have its own `@BeforeEach`

[prev: Overview](/blog/junit-spring-testing/chapter-00-overview) | [next: Mockito](/blog/junit-spring-testing/chapter-02-mockito)
