# Advanced Topics

## BDDMockito — Given/When/Then Style

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceBDDTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void shouldReturnOrder_whenIdExists() {
        // given
        Order order = new Order("Laptop", 1);
        order.setId(1L);
        given(orderRepository.findById(1L)).willReturn(Optional.of(order));

        // when
        Order result = orderService.findById(1L);

        // then
        then(orderRepository).should().findById(1L);
        assertThat(result.getProduct()).isEqualTo("Laptop");
    }

    @Test
    void shouldNotify_whenOrderPlaced() {
        // given
        Order saved = new Order("Phone", 2);
        saved.setId(10L);
        given(orderRepository.save(any(Order.class))).willReturn(saved);
        willDoNothing().given(notificationService).sendConfirmation(anyLong());

        // when
        orderService.placeOrder("Phone", 2);

        // then
        then(notificationService).should().sendConfirmation(10L);
    }
}
```

## mockStatic — Mocking Static Methods

```java
package com.example.service;

import java.util.UUID;

public class TokenGenerator {

    public String generateToken(String prefix) {
        return prefix + "-" + UUID.randomUUID().toString();
    }
}
```

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class TokenGeneratorTest {

    @Test
    void generateToken_withMockedUUID() {
        UUID fixedUuid = UUID.fromString("12345678-1234-1234-1234-123456789abc");

        try (MockedStatic<UUID> mockedUuid = mockStatic(UUID.class)) {
            mockedUuid.when(UUID::randomUUID).thenReturn(fixedUuid);

            TokenGenerator generator = new TokenGenerator();
            String token = generator.generateToken("TKN");

            assertEquals("TKN-12345678-1234-1234-1234-123456789abc", token);
        }
        // Static mock is automatically closed after try block
    }
}
```

## @SpyBean — Partial Mocking in Spring Context

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.SpyBean;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class OrderServiceSpyTest {

    @SpyBean
    private OrderService orderService;

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void spyBean_callsRealMethodButCanVerify() {
        Order order = new Order("Tablet", 1);
        orderRepository.save(order);

        // Real method is called, but we can verify interactions
        Order result = orderService.findById(order.getId());

        assertNotNull(result);
        verify(orderService).findById(order.getId());
    }
}
```

## @TestConfiguration — Custom Beans for Tests

```java
package com.example.config;

import com.example.service.NotificationService;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;

@TestConfiguration
public class TestNotificationConfig {

    @Bean
    public NotificationService notificationService() {
        // Return a no-op implementation for tests
        return orderId -> { /* do nothing */ };
    }
}
```

```java
package com.example.service;

import com.example.config.TestNotificationConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Import(TestNotificationConfig.class)
class OrderServiceWithTestConfigTest {

    @Autowired
    private OrderService orderService;

    @Test
    void placeOrder_usesTestNotificationService() {
        Order result = orderService.placeOrder("Book", 3);
        assertNotNull(result);
    }
}
```

## AssertJ — Fluent Assertions

```java
package com.example.service;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.*;

class AssertJExampleTest {

    @Test
    void stringAssertions() {
        String result = "Hello Spring Boot";

        assertThat(result)
            .startsWith("Hello")
            .contains("Spring")
            .endsWith("Boot")
            .hasSize(17);
    }

    @Test
    void collectionAssertions() {
        List<Order> orders = List.of(
            new Order("Laptop", 1),
            new Order("Phone", 2),
            new Order("Tablet", 1)
        );

        assertThat(orders)
            .hasSize(3)
            .extracting(Order::getProduct)
            .containsExactly("Laptop", "Phone", "Tablet");
    }

    @Test
    void exceptionAssertions() {
        assertThatThrownBy(() -> {
            throw new OrderNotFoundException("Not found");
        })
            .isInstanceOf(OrderNotFoundException.class)
            .hasMessageContaining("Not found");
    }
}
```

## Parallel Test Execution

In `src/test/resources/junit-platform.properties`:

```properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=concurrent
junit.jupiter.execution.parallel.config.strategy=fixed
junit.jupiter.execution.parallel.config.fixed.parallelism=4
```

Ensure tests are independent — no shared mutable state.

## JaCoCo Coverage in build.gradle.kts

```kotlin
plugins {
    jacoco
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}

tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = "0.80".toBigDecimal()
            }
        }
    }
}

tasks.check {
    dependsOn(tasks.jacocoTestCoverageVerification)
}
```

Run: `./gradlew test jacocoTestReport`

Report at: `build/reports/jacoco/test/html/index.html`

## Key Points

- `BDDMockito` — `given()`/`then()` reads like specifications
- `mockStatic()` — must be in try-with-resources to auto-close
- `@SpyBean` — wraps a real bean, allows verify and selective stubbing
- `@TestConfiguration` + `@Import` — override beans for specific tests
- AssertJ — fluent, readable assertions with better error messages
- Parallel tests — enable in `junit-platform.properties`, ensure thread safety
- JaCoCo — enforce minimum coverage with `jacocoTestCoverageVerification`

[prev: REST Testing](/blog/junit-spring-testing/chapter-07-rest-testing)
