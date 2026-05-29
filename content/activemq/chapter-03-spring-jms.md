# Spring Boot + JMS

[prev: Setup](/blog/activemq/chapter-02-setup) | [next: Messaging Patterns](/blog/activemq/chapter-04-patterns)

## Dependencies

```groovy
// build.gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.4'
    id 'io.spring.dependency-management' version '1.1.4'
}

dependencies {
    // For ActiveMQ Classic
    implementation 'org.springframework.boot:spring-boot-starter-activemq'

    // For ActiveMQ Artemis (use this instead for Artemis)
    // implementation 'org.springframework.boot:spring-boot-starter-artemis'

    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'com.fasterxml.jackson.core:jackson-databind'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

## Connection Configuration

```properties
# application.properties — Classic
spring.activemq.broker-url=tcp://localhost:61616
spring.activemq.user=admin
spring.activemq.password=admin
spring.activemq.pool.enabled=true
spring.activemq.pool.max-connections=10
```

```properties
# application.properties — Artemis
spring.artemis.mode=native
spring.artemis.broker-url=tcp://localhost:61616
spring.artemis.user=admin
spring.artemis.password=admin
```

## JmsTemplate: Sending Messages

```java
@Service
public class OrderProducer {

    private final JmsTemplate jmsTemplate;

    public OrderProducer(JmsTemplate jmsTemplate) {
        this.jmsTemplate = jmsTemplate;
    }

    // Send raw text
    public void sendRaw(String destination, String text) {
        jmsTemplate.send(destination, session -> session.createTextMessage(text));
    }

    // Send with convertAndSend (uses configured MessageConverter)
    public void sendOrder(Order order) {
        jmsTemplate.convertAndSend("orders", order);
    }

    // Send with headers/properties
    public void sendWithProperties(Order order) {
        jmsTemplate.convertAndSend("orders", order, message -> {
            message.setStringProperty("orderType", order.type());
            message.setIntProperty("priority", order.priority());
            return message;
        });
    }
}
```

## JmsListener: Receiving Messages

```java
@Component
public class OrderConsumer {

    @JmsListener(destination = "orders")
    public void handleOrder(Order order) {
        System.out.println("Received order: " + order.id());
    }

    // With headers
    @JmsListener(destination = "orders", concurrency = "3-5")
    public void handleWithHeaders(Order order,
                                   @Header("orderType") String type,
                                   @Header(name = "priority", required = false) Integer priority) {
        System.out.println("Order type: " + type + ", priority: " + priority);
    }

    // With selector
    @JmsListener(destination = "orders", selector = "orderType = 'PREMIUM'")
    public void handlePremiumOrders(Order order) {
        System.out.println("Premium order: " + order.id());
    }
}
```

## Message Converters (Jackson JSON)

```java
@Configuration
public class JmsConfig {

    @Bean
    public MessageConverter jacksonJmsMessageConverter() {
        MappingJackson2MessageConverter converter = new MappingJackson2MessageConverter();
        converter.setTargetType(MessageType.TEXT);
        converter.setTypeIdPropertyName("_type");
        return converter;
    }
}
```

This allows `convertAndSend` and `@JmsListener` to automatically serialize/deserialize POJOs as JSON.

```java
// Sent as TextMessage with JSON body and property _type = "com.example.Order"
public record Order(long id, String item, int quantity, String type, int priority) {}
```

## Connection Factory Configuration

### Classic with Caching

```java
@Configuration
public class ActiveMQConfig {

    @Bean
    public ActiveMQConnectionFactory connectionFactory() {
        ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory();
        factory.setBrokerURL("failover:(tcp://broker1:61616,tcp://broker2:61616)");
        factory.setUserName("admin");
        factory.setPassword("admin");
        factory.setTrustedPackages(List.of("com.example"));
        return factory;
    }

    @Bean
    public CachingConnectionFactory cachingConnectionFactory(ActiveMQConnectionFactory factory) {
        CachingConnectionFactory cachingFactory = new CachingConnectionFactory(factory);
        cachingFactory.setSessionCacheSize(10);
        return cachingFactory;
    }
}
```

## Concurrency Settings

```java
@JmsListener(destination = "orders", concurrency = "3-10")
public void handleOrder(Order order) {
    // 3 threads minimum, scales up to 10 under load
}
```

Global default:

```properties
spring.jms.listener.concurrency=3
spring.jms.listener.max-concurrency=10
```

## JmsListenerContainerFactory

```java
@Configuration
@EnableJms
public class JmsConfig {

    @Bean
    public DefaultJmsListenerContainerFactory defaultFactory(
            ConnectionFactory connectionFactory,
            MessageConverter messageConverter) {
        DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory);
        factory.setMessageConverter(messageConverter);
        factory.setConcurrency("3-10");
        factory.setSessionAcknowledgeMode(Session.CLIENT_ACKNOWLEDGE);
        return factory;
    }

    // Separate factory for topics
    @Bean
    public DefaultJmsListenerContainerFactory topicFactory(
            ConnectionFactory connectionFactory,
            MessageConverter messageConverter) {
        DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory);
        factory.setMessageConverter(messageConverter);
        factory.setPubSubDomain(true);
        factory.setSubscriptionDurable(true);
        factory.setClientId("order-service");
        return factory;
    }

    // Factory with transactions
    @Bean
    public DefaultJmsListenerContainerFactory transactedFactory(
            ConnectionFactory connectionFactory,
            MessageConverter messageConverter) {
        DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory);
        factory.setMessageConverter(messageConverter);
        factory.setSessionTransacted(true);
        factory.setErrorHandler(t -> System.err.println("JMS Error: " + t.getMessage()));
        return factory;
    }
}
```

Using a specific factory:

```java
@JmsListener(destination = "order-events", containerFactory = "topicFactory")
public void handleEvent(OrderEvent event) {
    // receives from topic with durable subscription
}

@JmsListener(destination = "payments", containerFactory = "transactedFactory")
public void handlePayment(Payment payment) {
    // transacted — auto rollback on exception
}
```

## Complete Example

```java
@SpringBootApplication
@EnableJms
public class MessagingApplication {
    public static void main(String[] args) {
        SpringApplication.run(MessagingApplication.class, args);
    }
}

@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderProducer producer;

    public OrderController(OrderProducer producer) {
        this.producer = producer;
    }

    @PostMapping
    public ResponseEntity<String> createOrder(@RequestBody Order order) {
        producer.sendOrder(order);
        return ResponseEntity.accepted().body("Order queued: " + order.id());
    }
}
```

## Exercises

1. **Basic producer/consumer**: Create a Spring Boot app that sends an Order object as JSON to a queue and consumes it with `@JmsListener`. Verify the JSON conversion works.

2. **Multiple factories**: Configure two factories — one for queues with concurrency 5, one for topics with durable subscriptions. Send messages to both and verify behavior.

3. **Message properties**: Send orders with a `priority` property. Create two listeners with selectors: one for high priority (> 7), one for normal.

4. **Error handling**: Configure a transacted factory. Throw an exception in the listener and observe the message being redelivered.
