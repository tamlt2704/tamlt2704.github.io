# REST Controller Testing

`@WebMvcTest` loads only the web layer — no database, no full context. Fast and focused.

## Controller Under Test

```java
package com.example.controller;

import com.example.service.Order;
import com.example.service.OrderNotFoundException;
import com.example.service.OrderService;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @GetMapping("/{id}")
    public Order getOrder(@PathVariable Long id) {
        return orderService.findById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Order createOrder(@RequestBody CreateOrderRequest request) {
        return orderService.placeOrder(request.product(), request.quantity());
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteOrder(@PathVariable Long id) {
        orderService.cancelOrder(id);
    }

    @ExceptionHandler(OrderNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(OrderNotFoundException ex) {
        return new ErrorResponse(ex.getMessage());
    }

    public record CreateOrderRequest(String product, int quantity) {}
    public record ErrorResponse(String message) {}
}
```

## WebMvcTest with MockMvc

```java
package com.example.controller;

import com.example.service.Order;
import com.example.service.OrderNotFoundException;
import com.example.service.OrderService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Test
    void getOrder_returnsOrder() throws Exception {
        Order order = new Order("Laptop", 1);
        order.setId(1L);
        when(orderService.findById(1L)).thenReturn(order);

        mockMvc.perform(get("/api/orders/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.product").value("Laptop"))
            .andExpect(jsonPath("$.quantity").value(1));
    }

    @Test
    void getOrder_returns404WhenNotFound() throws Exception {
        when(orderService.findById(99L))
            .thenThrow(new OrderNotFoundException("Order not found: 99"));

        mockMvc.perform(get("/api/orders/99"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.message").value("Order not found: 99"));
    }

    @Test
    void createOrder_returns201() throws Exception {
        Order saved = new Order("Phone", 2);
        saved.setId(5L);
        when(orderService.placeOrder("Phone", 2)).thenReturn(saved);

        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"product\":\"Phone\",\"quantity\":2}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(5))
            .andExpect(jsonPath("$.product").value("Phone"));
    }

    @Test
    void deleteOrder_returns204() throws Exception {
        doNothing().when(orderService).cancelOrder(1L);

        mockMvc.perform(delete("/api/orders/1"))
            .andExpect(status().isNoContent());

        verify(orderService).cancelOrder(1L);
    }
}
```

## Testing with Security (@WithMockUser)

```java
package com.example.controller;

import com.example.service.Order;
import com.example.service.OrderService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(OrderController.class)
class OrderControllerSecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Test
    void unauthenticated_returns401() throws Exception {
        mockMvc.perform(get("/api/orders/1"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(username = "admin", roles = {"ADMIN"})
    void authenticatedAdmin_canAccessOrder() throws Exception {
        Order order = new Order("Widget", 3);
        order.setId(1L);
        when(orderService.findById(1L)).thenReturn(order);

        mockMvc.perform(get("/api/orders/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.product").value("Widget"));
    }

    @Test
    @WithMockUser(username = "user", roles = {"USER"})
    void regularUser_canAccessOrder() throws Exception {
        Order order = new Order("Gadget", 1);
        order.setId(2L);
        when(orderService.findById(2L)).thenReturn(order);

        mockMvc.perform(get("/api/orders/2"))
            .andExpect(status().isOk());
    }
}
```

## Key Points

- `@WebMvcTest` loads only the controller layer — fast startup
- `@MockBean` replaces service beans with Mockito mocks in the Spring context
- `MockMvc` simulates HTTP requests without starting a real server
- `jsonPath()` validates JSON response structure
- `@WithMockUser` simulates authenticated requests for security testing
- Test each HTTP method: GET, POST, PUT, DELETE

[prev: Repeated Tests](/blog/junit-spring-testing/chapter-06-repeated) | [next: Advanced Topics](/blog/junit-spring-testing/chapter-08-advanced)
