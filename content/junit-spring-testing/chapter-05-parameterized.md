# Parameterized Tests

Run the same test logic with different inputs using `@ParameterizedTest`.

## Class Under Test

```java
package com.example.service;

public class StringValidator {

    public boolean isValidEmail(String email) {
        return email != null && email.matches("^[\\w.]+@[\\w.]+\\.[a-z]{2,}$");
    }

    public boolean isStrongPassword(String password) {
        return password != null && password.length() >= 8
            && password.chars().anyMatch(Character::isUpperCase)
            && password.chars().anyMatch(Character::isDigit);
    }

    public String classify(int score) {
        if (score >= 90) return "A";
        if (score >= 80) return "B";
        if (score >= 70) return "C";
        if (score >= 60) return "D";
        return "F";
    }
}
```

## @ValueSource — Single Argument

```java
package com.example.service;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

class ValueSourceTest {

    private final StringValidator validator = new StringValidator();

    @ParameterizedTest
    @ValueSource(strings = {"user@mail.com", "test@domain.org", "a.b@c.co"})
    void validEmails(String email) {
        assertTrue(validator.isValidEmail(email));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "noatsign", "@missing.com", "spaces in@mail.com"})
    void invalidEmails(String email) {
        assertFalse(validator.isValidEmail(email));
    }
}
```

## @CsvSource — Multiple Arguments

```java
package com.example.service;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.*;

class CsvSourceTest {

    private final StringValidator validator = new StringValidator();

    @ParameterizedTest
    @CsvSource({
        "95, A",
        "85, B",
        "75, C",
        "65, D",
        "50, F"
    })
    void classify_returnsCorrectGrade(int score, String expectedGrade) {
        assertEquals(expectedGrade, validator.classify(score));
    }
}
```

## @CsvFileSource — External CSV

Create `src/test/resources/grades.csv`:

```csv
score,expected
100,A
89,B
71,C
60,D
59,F
```

```java
package com.example.service;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvFileSource;

import static org.junit.jupiter.api.Assertions.*;

class CsvFileSourceTest {

    private final StringValidator validator = new StringValidator();

    @ParameterizedTest
    @CsvFileSource(resources = "/grades.csv", numLinesToSkip = 1)
    void classify_fromFile(int score, String expected) {
        assertEquals(expected, validator.classify(score));
    }
}
```

## @MethodSource — Complex Arguments

```java
package com.example.service;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

class MethodSourceTest {

    private final StringValidator validator = new StringValidator();

    static Stream<Arguments> passwordCases() {
        return Stream.of(
            Arguments.of("Abcdefg1", true),
            Arguments.of("short1A", false),
            Arguments.of("nouppercase1", false),
            Arguments.of("NoDigitsHere", false)
        );
    }

    @ParameterizedTest
    @MethodSource("passwordCases")
    void isStrongPassword(String password, boolean expected) {
        assertEquals(expected, validator.isStrongPassword(password));
    }
}
```

## @EnumSource

```java
package com.example.service;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

import java.time.DayOfWeek;

import static org.junit.jupiter.api.Assertions.*;

class EnumSourceTest {

    @ParameterizedTest
    @EnumSource(value = DayOfWeek.class, names = {"SATURDAY", "SUNDAY"})
    void weekendDays(DayOfWeek day) {
        assertTrue(day.getValue() >= 6);
    }

    @ParameterizedTest
    @EnumSource(value = DayOfWeek.class, mode = EnumSource.Mode.EXCLUDE, names = {"SATURDAY", "SUNDAY"})
    void weekdays(DayOfWeek day) {
        assertTrue(day.getValue() <= 5);
    }
}
```

## Custom ArgumentsProvider

```java
package com.example.service;

import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;

import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

class CustomProviderTest {

    static class BoundaryScoreProvider implements ArgumentsProvider {
        @Override
        public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
            return Stream.of(
                Arguments.of(89, "B"),
                Arguments.of(90, "A"),
                Arguments.of(79, "C"),
                Arguments.of(80, "B")
            );
        }
    }

    private final StringValidator validator = new StringValidator();

    @ParameterizedTest
    @ArgumentsSource(BoundaryScoreProvider.class)
    void classify_boundaryValues(int score, String expected) {
        assertEquals(expected, validator.classify(score));
    }
}
```

## Key Points

- `@ParameterizedTest` replaces `@Test` — do not use both
- `@ValueSource` for single-argument primitives/strings
- `@CsvSource` for inline multi-argument data
- `@CsvFileSource` for external test data files
- `@MethodSource` for complex objects or computed data
- `@EnumSource` for enum values with optional filtering
- `@ArgumentsSource` for reusable custom providers

[prev: Lenient Stubbing](/blog/junit-spring-testing/chapter-04-lenient) | [next: Repeated Tests](/blog/junit-spring-testing/chapter-06-repeated)
