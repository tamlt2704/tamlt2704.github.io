# Chapter 7: Testing Tricks — Fast, Focused, Reliable Tests

[← Chapter 6: Caching](chapter-06-caching.md) | [Chapter 8: Actuator →](chapter-08-actuator.md)

---

## The Problem

"My test suite takes 8 minutes because every test loads the full application context. I can't test my controller without a real database. External API tests are flaky."

## Test Slicing — Load Only What You Need

### @WebMvcTest — Controller Layer Only

```java
@WebMvcTest(UserController.class)  // Only loads web layer for this controller
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean  // Mock the service layer
    private UserService userService;

    @Test
    void getUser_returnsUser() throws Exception {
        when(userService.getUser(1L)).thenReturn(new User(1L, "Alice", "alice@test.com"));

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Alice"))
            .andExpect(jsonPath("$.email").value("alice@test.com"));
    }

    @Test
    void getUser_notFound_returns404() throws Exception {
        when(userService.getUser(99L)).thenThrow(new NotFoundException("User", 99L));

        mockMvc.perform(get("/api/users/99"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.detail").value("User with id '99' not found"));
    }

    @Test
    void createUser_validationError() throws Exception {
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "not-an-email", "name": ""}
                    """))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors.email").exists());
    }
}
```

### @DataJpaTest — Repository Layer Only

```java
@DataJpaTest  // Loads JPA, embedded DB, no web layer
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findByEmail_returnsUser() {
        entityManager.persistAndFlush(new User(null, "Alice", "alice@test.com"));

        Optional<User> found = userRepository.findByEmail("alice@test.com");

        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Alice");
    }
}
```

### @JsonTest — Serialization Only

```java
@JsonTest
class ProductDtoTest {

    @Autowired
    private JacksonTester<ProductDto> json;

    @Test
    void serialize() throws Exception {
        var dto = new ProductDto("Widget", new BigDecimal("9.99"), "ACTIVE");

        assertThat(json.write(dto)).extractingJsonPathStringValue("$.name")
            .isEqualTo("Widget");
        assertThat(json.write(dto)).doesNotHaveJsonPath("$.internalCode");
    }
}
```

## @MockBean vs @SpyBean

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @MockBean   // Full mock — all methods return null/default unless stubbed
    private PaymentService paymentService;

    @SpyBean    // Real implementation — but you can override specific methods
    private OrderMapper orderMapper;

    @Test
    void placeOrder_callsPayment() throws Exception {
        when(paymentService.charge(any())).thenReturn(new PaymentResult("txn-123", true));
        // orderMapper uses real logic, but we could verify or override if needed

        mockMvc.perform(post("/api/orders").contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"productId": 1, "quantity": 2}
                    """))
            .andExpect(status().isCreated());

        verify(paymentService).charge(any());
    }
}
```

## Testcontainers — Real Database in Tests

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest
@Testcontainers
class OrderIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private OrderService orderService;

    @Test
    void createOrder_persistsToRealDatabase() {
        Order order = orderService.create(new OrderRequest("product-1", 2));

        assertThat(order.getId()).isNotNull();
        assertThat(orderService.getOrder(order.getId())).isEqualTo(order);
    }
}
```

## WireMock — Mock External APIs

```xml
<dependency>
    <groupId>org.wiremock</groupId>
    <artifactId>wiremock-standalone</artifactId>
    <version>3.4.2</version>
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest
@WireMockTest(httpPort = 8089)
class PaymentClientTest {

    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry registry) {
        registry.add("app.payment-api.base-url", () -> "http://localhost:8089");
    }

    @Autowired
    private PaymentClient paymentClient;

    @Test
    void charge_success() {
        stubFor(post("/v1/charges")
            .willReturn(okJson("""
                {"id": "ch_123", "status": "succeeded"}
                """)));

        PaymentResult result = paymentClient.charge(new ChargeRequest("tok_visa", 2500));

        assertThat(result.id()).isEqualTo("ch_123");
        assertThat(result.status()).isEqualTo("succeeded");
    }

    @Test
    void charge_timeout_throwsException() {
        stubFor(post("/v1/charges")
            .willReturn(ok().withFixedDelay(5000)));  // Simulate timeout

        assertThatThrownBy(() -> paymentClient.charge(new ChargeRequest("tok_visa", 100)))
            .isInstanceOf(PaymentTimeoutException.class);
    }
}
```

## What You Learned

- **@WebMvcTest** — test controllers without starting the full app
- **@DataJpaTest** — test repositories with embedded DB
- **@JsonTest** — test serialization/deserialization in isolation
- **@MockBean vs @SpyBean** — full mock vs partial override
- **Testcontainers** — real Postgres/Redis/Kafka in tests via Docker
- **@DynamicPropertySource** — inject container URLs into Spring config
- **WireMock** — deterministic external API mocking with timeout simulation

---

[← Chapter 6: Caching](chapter-06-caching.md) | [Chapter 8: Actuator →](chapter-08-actuator.md)
