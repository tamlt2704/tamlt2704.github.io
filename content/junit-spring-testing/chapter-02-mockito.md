# Mockito Fundamentals

## Class Under Test

```java
package com.example.service;

public class OrderService {

    private final OrderRepository orderRepository;
    private final NotificationService notificationService;

    public OrderService(OrderRepository orderRepository, NotificationService notificationService) {
        this.orderRepository = orderRepository;
        this.notificationService = notificationService;
    }

    public Order placeOrder(String product, int quantity) {
        Order order = new Order(product, quantity);
        Order saved = orderRepository.save(order);
        notificationService.sendConfirmation(saved.getId());
        return saved;
    }

    public Order findById(Long id) {
        return orderRepository.findById(id)
            .orElseThrow(() -> new OrderNotFoundException("Order not found: " + id));
    }

    public void cancelOrder(Long id) {
        orderRepository.deleteById(id);
    }
}
```

```java
package com.example.service;

public class Order {
    private Long id;
    private String product;
    private int quantity;

    public Order(String product, int quantity) {
        this.product = product;
        this.quantity = quantity;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getProduct() { return product; }
    public int getQuantity() { return quantity; }
}
```

## Test with @Mock and @InjectMocks

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void placeOrder_savesAndNotifies() {
        Order savedOrder = new Order("Laptop", 1);
        savedOrder.setId(42L);

        when(orderRepository.save(any(Order.class))).thenReturn(savedOrder);
        doNothing().when(notificationService).sendConfirmation(anyLong());

        Order result = orderService.placeOrder("Laptop", 1);

        assertEquals(42L, result.getId());
        verify(orderRepository).save(any(Order.class));
        verify(notificationService).sendConfirmation(42L);
    }

    @Test
    void findById_returnsOrder() {
        Order order = new Order("Phone", 2);
        order.setId(1L);
        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));

        Order result = orderService.findById(1L);

        assertEquals("Phone", result.getProduct());
        verify(orderRepository, times(1)).findById(1L);
    }

    @Test
    void findById_throwsWhenNotFound() {
        when(orderRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(OrderNotFoundException.class,
            () -> orderService.findById(99L));

        verify(notificationService, never()).sendConfirmation(anyLong());
    }

    @Test
    void cancelOrder_deletesById() {
        doNothing().when(orderRepository).deleteById(5L);

        orderService.cancelOrder(5L);

        verify(orderRepository).deleteById(5L);
        verify(notificationService, never()).sendConfirmation(anyLong());
    }
}
```

## Key Points

- `@ExtendWith(MockitoExtension.class)` — integrates Mockito with JUnit 5
- `@Mock` — creates a mock instance
- `@InjectMocks` — creates the real object and injects mocks into it
- `when(...).thenReturn(...)` — stubs a return value
- `doNothing().when(mock).voidMethod()` — stubs void methods
- `verify(mock)` — asserts the method was called once
- `verify(mock, times(n))` — asserts exact call count
- `verify(mock, never())` — asserts method was never called

[prev: JUnit 5 Basics](/blog/junit-spring-testing/chapter-01-junit-basics) | [next: Argument Capture](/blog/junit-spring-testing/chapter-03-argument-capture)
