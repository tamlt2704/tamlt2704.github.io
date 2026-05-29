# Lenient Stubbing and Strictness

Mockito 5 uses **STRICT** stubbing by default. If you stub a method but never call it, the test fails with `UnnecessaryStubbingException`.

## The Problem

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class StrictStubbingProblemTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void thisTestFails_unnecessaryStubbing() {
        // This stub is never used — cancelOrder does not call findById
        when(orderRepository.findById(1L)).thenReturn(Optional.of(new Order("X", 1)));

        orderService.cancelOrder(1L);

        verify(orderRepository).deleteById(1L);
        // FAILS: UnnecessaryStubbingException
    }
}
```

## Solution 1: lenient() Per Stub

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class LenientPerStubTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void lenientStub_doesNotFailOnUnused() {
        lenient().when(orderRepository.findById(1L))
            .thenReturn(Optional.of(new Order("X", 1)));

        orderService.cancelOrder(1L);

        verify(orderRepository).deleteById(1L);
    }
}
```

## Solution 2: @MockitoSettings at Class Level

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class LenientClassLevelTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void allStubsAreLenient() {
        when(orderRepository.findById(1L)).thenReturn(Optional.of(new Order("X", 1)));
        when(orderRepository.findById(2L)).thenReturn(Optional.empty());

        // Only uses one stub — no failure
        Order result = orderService.findById(1L);

        assertEquals("X", result.getProduct());
    }
}
```

## When to Use Lenient

| Scenario                                                        | Recommendation          |
| --------------------------------------------------------------- | ----------------------- |
| Shared setup in `@BeforeEach` with stubs not used by every test | `lenient()` per stub    |
| Parameterized tests where some params skip a code path          | `lenient()` per stub    |
| You simply forgot to remove an old stub                         | Remove the stub instead |

## Best Practice

Prefer **strict** stubbing. It catches dead code and copy-paste errors. Use `lenient()` only when shared setup genuinely requires it.

[prev: Argument Capture](/blog/junit-spring-testing/chapter-03-argument-capture) | [next: Parameterized Tests](/blog/junit-spring-testing/chapter-05-parameterized)
