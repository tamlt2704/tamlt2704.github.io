# Reliability

[prev: Messaging Patterns](/blog/activemq/chapter-04-patterns) | [next: ActiveMQ Artemis Specifics](/blog/activemq/chapter-06-artemis)

## Persistent vs Non-Persistent Messages

| Mode                 | Behavior                              | Use Case                            |
| -------------------- | ------------------------------------- | ----------------------------------- |
| PERSISTENT (default) | Written to disk before acknowledgment | Orders, payments, critical data     |
| NON_PERSISTENT       | Kept in memory only                   | Metrics, heartbeats, ephemeral data |

```java
// Non-persistent for performance (acceptable loss)
jmsTemplate.send("metrics", session -> {
    TextMessage msg = session.createTextMessage(payload);
    msg.setJMSDeliveryMode(DeliveryMode.NON_PERSISTENT);
    return msg;
});

// Persistent (default, explicit)
jmsTemplate.setDeliveryMode(DeliveryMode.PERSISTENT);
jmsTemplate.convertAndSend("orders", order);
```

### Storage Comparison

|             | Classic (KahaDB)         | Artemis (Journal)          |
| ----------- | ------------------------ | -------------------------- |
| Format      | B-tree index + data logs | Append-only journal files  |
| Sync        | Configurable             | libaio (Linux) or NIO      |
| Performance | Good                     | Better (sequential writes) |

## Transactions

### JMS Local Transactions

All sends/receives in a session are atomic — either all commit or all roll back:

```java
@JmsListener(destination = "orders", containerFactory = "transactedFactory")
public void processOrder(Order order, Session session) {
    try {
        processBusinessLogic(order);
        // implicit commit when method returns without exception
    } catch (Exception e) {
        // implicit rollback — message will be redelivered
        throw e;
    }
}
```

Factory configuration:

```java
@Bean
public DefaultJmsListenerContainerFactory transactedFactory(ConnectionFactory cf) {
    DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
    factory.setConnectionFactory(cf);
    factory.setSessionTransacted(true);
    return factory;
}
```

### Sending Within a Transaction

```java
@Transactional
public void transferOrder(Order order) {
    // Both sends succeed or both fail
    jmsTemplate.setSessionTransacted(true);
    jmsTemplate.convertAndSend("order-processing", order);
    jmsTemplate.convertAndSend("order-audit", order);
}
```

### XA/Distributed Transactions

When you need atomicity across JMS and a database:

```groovy
// build.gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-jta-atomikos'
}
```

```java
@Configuration
public class XAConfig {

    @Bean
    public ConnectionFactory xaConnectionFactory() {
        ActiveMQXAConnectionFactory xaFactory = new ActiveMQXAConnectionFactory();
        xaFactory.setBrokerURL("tcp://localhost:61616");
        AtomikosConnectionFactoryBean atomikos = new AtomikosConnectionFactoryBean();
        atomikos.setXaConnectionFactory(xaFactory);
        atomikos.setUniqueResourceName("activemq-xa");
        return atomikos;
    }
}

@Service
public class OrderService {

    @Transactional // JTA transaction spans DB + JMS
    public void placeOrder(Order order) {
        orderRepository.save(order);           // DB write
        jmsTemplate.convertAndSend("orders", order); // JMS send
        // both commit or both rollback
    }
}
```

## Acknowledgment Deep Dive

### AUTO_ACKNOWLEDGE

```java
// Message acknowledged immediately after onMessage() returns
@JmsListener(destination = "orders")
public void handle(Order order) {
    process(order); // if this throws, message is redelivered
}
```

Risk: If processing succeeds but acknowledgment fails (network issue), you get a duplicate.

### CLIENT_ACKNOWLEDGE

```java
@JmsListener(destination = "orders", containerFactory = "clientAckFactory")
public void handle(Message message) throws JMSException {
    Order order = extractOrder(message);
    process(order);
    message.acknowledge(); // explicit — acknowledges all messages up to this point
}
```

### DUPS_OK_ACKNOWLEDGE

```java
// Broker may redeliver — consumer must be idempotent
// Better performance due to lazy ack batching
@Bean
public DefaultJmsListenerContainerFactory dupsOkFactory(ConnectionFactory cf) {
    DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
    factory.setConnectionFactory(cf);
    factory.setSessionAcknowledgeMode(Session.DUPS_OK_ACKNOWLEDGE);
    return factory;
}
```

## Redelivery Policies

### Classic (activemq.xml)

```xml
<redeliveryPlugin>
  <redeliveryPolicyMap>
    <redeliveryPolicyEntries>
      <redeliveryPolicy queue="orders"
                        maximumRedeliveries="5"
                        initialRedeliveryDelay="1000"
                        backOffMultiplier="2"
                        useExponentialBackOff="true"
                        maximumRedeliveryDelay="60000"/>
      <redeliveryPolicy queue=">"
                        maximumRedeliveries="3"
                        initialRedeliveryDelay="500"/>
    </redeliveryPolicyEntries>
  </redeliveryPolicyMap>
</redeliveryPlugin>
```

### Artemis (broker.xml)

```xml
<address-setting match="orders">
  <max-delivery-attempts>5</max-delivery-attempts>
  <redelivery-delay>1000</redelivery-delay>
  <redelivery-multiplier>2.0</redelivery-multiplier>
  <max-redelivery-delay>60000</max-redelivery-delay>
  <redelivery-collision-avoidance-factor>0.15</redelivery-collision-avoidance-factor>
</address-setting>
```

### Spring Boot Client-Side Redelivery (Classic)

```java
@Bean
public ActiveMQConnectionFactory connectionFactory() {
    ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("tcp://localhost:61616");
    RedeliveryPolicy policy = new RedeliveryPolicy();
    policy.setMaximumRedeliveries(5);
    policy.setInitialRedeliveryDelay(1000);
    policy.setBackOffMultiplier(2.0);
    policy.setUseExponentialBackOff(true);
    factory.setRedeliveryPolicy(policy);
    return factory;
}
```

## Duplicate Detection

### Artemis Built-in Duplicate Detection

Artemis can detect and discard duplicate messages using a unique ID:

```java
public void sendWithDuplicateDetection(Order order) {
    jmsTemplate.convertAndSend("orders", order, message -> {
        message.setStringProperty("_AMQ_DUPL_ID", order.id() + "-" + order.version());
        return message;
    });
}
```

Artemis maintains an in-memory cache of recent message IDs. Configure cache size:

```xml
<address-setting match="orders">
  <id-cache-size>2000</id-cache-size>
</address-setting>
```

### Classic — No Built-in Support

Classic does not have built-in duplicate detection. Handle at the application level.

## Idempotent Consumers

Design consumers that produce the same result regardless of how many times a message is processed:

```java
@Component
public class IdempotentOrderConsumer {

    private final OrderRepository orderRepository;
    private final ProcessedMessageRepository processedRepo;

    @JmsListener(destination = "orders")
    @Transactional
    public void handleOrder(Order order, @Header("JMSMessageID") String messageId) {
        // Check if already processed
        if (processedRepo.existsById(messageId)) {
            return; // skip duplicate
        }

        // Process
        orderRepository.save(order);

        // Mark as processed
        processedRepo.save(new ProcessedMessage(messageId, Instant.now()));
    }
}
```

Strategies for idempotency:

- **Database unique constraint** on business key (order ID)
- **Processed message table** tracking message IDs
- **Conditional updates** (UPDATE WHERE version = expected)
- **Natural idempotency** (setting a value is inherently idempotent)

## Exercises

1. **Persistence test**: Send a persistent message, kill the broker (docker stop), restart it, and verify the message is still there. Repeat with non-persistent and observe the difference.

2. **Transaction rollback**: Configure a transacted listener. Process a message, throw an exception, and verify it is redelivered. Commit successfully on the second attempt.

3. **Redelivery policy**: Configure exponential backoff with max 3 retries. Log timestamps of each delivery attempt and verify the delays match the policy.

4. **Duplicate detection (Artemis)**: Send the same message (same `_AMQ_DUPL_ID`) twice. Verify only one copy is delivered to the consumer.

5. **Idempotent consumer**: Implement a consumer with a processed-message table. Send the same message 3 times and verify the business logic executes only once.
