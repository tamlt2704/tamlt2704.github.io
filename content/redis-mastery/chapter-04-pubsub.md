# Chapter 4: Pub/Sub & Streams

[← Caching Patterns](./chapter-03-caching.md) | [Next: Distributed Patterns →](./chapter-05-distributed.md)

---

## 4.1 Pub/Sub Basics

Redis Pub/Sub provides fire-and-forget messaging. Messages are not persisted.

```bash
# Terminal 1: Subscribe
redis-cli SUBSCRIBE notifications

# Terminal 2: Publish
redis-cli PUBLISH notifications "Order #123 placed"
redis-cli PUBLISH notifications "Payment received"

# Pattern subscribe
redis-cli PSUBSCRIBE "order:*"
redis-cli PUBLISH order:created "Order #456"
redis-cli PUBLISH order:shipped "Order #123"
```

## 4.2 Spring Boot Pub/Sub

**Publisher**

```java
@Service
@RequiredArgsConstructor
public class RedisPublisher {

    private final StringRedisTemplate redisTemplate;

    public void publish(String channel, String message) {
        redisTemplate.convertAndSend(channel, message);
    }
}
```

**Subscriber (Listener)**

```java
@Component
public class OrderEventListener implements MessageListener {

    @Override
    public void onMessage(Message message, byte[] pattern) {
        String channel = new String(message.getChannel());
        String body = new String(message.getBody());
        System.out.println("Received on [" + channel + "]: " + body);
    }
}
```

**Configuration**

```java
@Configuration
public class PubSubConfig {

    @Bean
    public RedisMessageListenerContainer listenerContainer(
            RedisConnectionFactory connectionFactory,
            OrderEventListener listener) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(connectionFactory);
        container.addMessageListener(listener, new ChannelTopic("notifications"));
        container.addMessageListener(listener, new PatternTopic("order:*"));
        return container;
    }
}
```

## 4.3 Redis Streams

Streams provide persistent, append-only log with consumer groups. Unlike Pub/Sub, messages are retained.

```bash
# Add entries to a stream
redis-cli XADD orders * product "laptop" quantity "1" customer "alice"
redis-cli XADD orders * product "phone" quantity "2" customer "bob"

# Read all entries
redis-cli XRANGE orders - +

# Read last 2 entries
redis-cli XREVRANGE orders + - COUNT 2

# Stream length
redis-cli XLEN orders

# Read new entries (blocking)
redis-cli XREAD BLOCK 5000 STREAMS orders 0
```

## 4.4 Consumer Groups

Consumer groups allow multiple consumers to process a stream cooperatively.

```bash
# Create consumer group (start from beginning)
redis-cli XGROUP CREATE orders order-processors 0

# Consumer 1 reads
redis-cli XREADGROUP GROUP order-processors consumer-1 COUNT 1 STREAMS orders >

# Consumer 2 reads (gets next unread message)
redis-cli XREADGROUP GROUP order-processors consumer-2 COUNT 1 STREAMS orders >

# Acknowledge processing
redis-cli XACK orders order-processors <message-id>

# Check pending messages
redis-cli XPENDING orders order-processors
```

## 4.5 Spring Boot Streams

**Producer**

```java
@Service
@RequiredArgsConstructor
public class StreamProducer {

    private final StringRedisTemplate redisTemplate;

    public RecordId sendOrder(Map<String, String> order) {
        StringRecord record = StreamRecords.string(order).withStreamKey("orders");
        return redisTemplate.opsForStream().add(record);
    }
}
```

**Consumer with StreamListener**

```java
@Component
@Slf4j
public class OrderStreamConsumer implements StreamListener<String, MapRecord<String, String, String>> {

    @Override
    public void onMessage(MapRecord<String, String, String> message) {
        log.info("Stream ID: {}", message.getId());
        log.info("Order data: {}", message.getValue());
    }
}
```

**Stream Configuration**

```java
@Configuration
public class StreamConfig {

    @Bean
    public Subscription orderSubscription(
            RedisConnectionFactory connectionFactory,
            OrderStreamConsumer consumer) {

        StreamMessageListenerContainer.StreamMessageListenerContainerOptions<String, MapRecord<String, String, String>> options =
            StreamMessageListenerContainer.StreamMessageListenerContainerOptions.builder()
                .pollTimeout(Duration.ofSeconds(2))
                .build();

        StreamMessageListenerContainer<String, MapRecord<String, String, String>> container =
            StreamMessageListenerContainer.create(connectionFactory, options);

        Subscription subscription = container.receiveAutoAck(
            Consumer.from("order-processors", "consumer-1"),
            StreamOffset.create("orders", ReadOffset.lastConsumed()),
            consumer);

        container.start();
        return subscription;
    }
}
```

## 4.6 Pub/Sub vs Streams

| Feature            | Pub/Sub                 | Streams                     |
| ------------------ | ----------------------- | --------------------------- |
| Persistence        | No                      | Yes                         |
| Consumer groups    | No                      | Yes                         |
| Message replay     | No                      | Yes                         |
| Delivery guarantee | At-most-once            | At-least-once               |
| Use case           | Real-time notifications | Event sourcing, task queues |

## Exercises

1. Implement a chat system using Pub/Sub with multiple channels.
2. Create a stream-based order processing pipeline with two consumer groups.
3. Implement dead-letter handling for failed stream messages using XPENDING and XCLAIM.
4. Build a real-time notification system that falls back to streams for offline users.

---

[← Caching Patterns](./chapter-03-caching.md) | [Next: Distributed Patterns →](./chapter-05-distributed.md)
