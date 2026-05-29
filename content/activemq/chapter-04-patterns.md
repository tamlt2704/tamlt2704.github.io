# Messaging Patterns

[prev: Spring Boot + JMS](/blog/activemq/chapter-03-spring-jms) | [next: Reliability](/blog/activemq/chapter-05-reliability)

## Request-Reply

The request-reply pattern uses `JMSReplyTo` and `JMSCorrelationID` to correlate responses with requests.

### Producer (Requester)

```java
@Service
public class OrderService {

    private final JmsTemplate jmsTemplate;

    public OrderService(JmsTemplate jmsTemplate) {
        this.jmsTemplate = jmsTemplate;
    }

    public String placeOrder(Order order) {
        return jmsTemplate.sendAndReceive("order-requests", session -> {
            TextMessage msg = session.createTextMessage(toJson(order));
            msg.setJMSReplyTo(session.createTemporaryQueue());
            msg.setJMSCorrelationID(UUID.randomUUID().toString());
            return msg;
        }).getBody(String.class);
    }
}
```

### Consumer (Responder)

```java
@Component
public class OrderProcessor {

    @JmsListener(destination = "order-requests")
    @SendTo // replies to JMSReplyTo destination
    public String processOrder(Order order) {
        String result = processBusinessLogic(order);
        return result; // sent back to the reply queue
    }
}
```

### Manual Reply

```java
@JmsListener(destination = "order-requests")
public void processOrder(Message request, Session session) throws JMSException {
    String body = ((TextMessage) request).getText();
    // process...

    MessageProducer replyProducer = session.createProducer(request.getJMSReplyTo());
    TextMessage reply = session.createTextMessage("CONFIRMED");
    reply.setJMSCorrelationID(request.getJMSCorrelationID());
    replyProducer.send(reply);
}
```

## Competing Consumers (Load Balancing)

Multiple consumers on the same queue automatically load-balance messages:

```java
// All three instances share the "orders" queue
// Each message goes to exactly one consumer
@JmsListener(destination = "orders", concurrency = "5")
public void processOrder(Order order) {
    // heavy processing distributed across 5 threads
}
```

In Classic, configure prefetch to control distribution:

```
tcp://localhost:61616?jms.prefetchPolicy.queuePrefetch=1
```

Low prefetch (1) ensures fair distribution. High prefetch improves throughput but may cause uneven load.

## Message Groups (Ordered Processing)

Message groups ensure all messages with the same group ID go to the same consumer, preserving order within the group.

### Producer

```java
public void sendOrderEvent(OrderEvent event) {
    jmsTemplate.convertAndSend("order-events", event, message -> {
        message.setStringProperty("JMSXGroupID", event.orderId());
        return message;
    });
}
```

### Behavior

- All messages with `JMSXGroupID = "order-123"` go to the same consumer
- Different group IDs can go to different consumers
- If a consumer disconnects, the group is reassigned

### Artemis Configuration

```xml
<address-setting match="order-events">
  <default-group-rebalance>true</default-group-rebalance>
  <group-rebalance-pause-dispatch>true</group-rebalance-pause-dispatch>
</address-setting>
```

## Dead Letter Queue (DLQ)

Messages that cannot be processed after max retries are moved to a DLQ.

### Classic Configuration (activemq.xml)

```xml
<policyEntry queue=">">
  <deadLetterStrategy>
    <individualDeadLetterStrategy queuePrefix="DLQ." useQueueForQueueMessages="true"/>
  </deadLetterStrategy>
  <redeliveryPolicy maximumRedeliveries="3" initialRedeliveryDelay="1000"
                    backOffMultiplier="2" useExponentialBackOff="true"/>
</policyEntry>
```

### Artemis Configuration (broker.xml)

```xml
<address-setting match="#">
  <dead-letter-address>DLA</dead-letter-address>
  <max-delivery-attempts>3</max-delivery-attempts>
  <redelivery-delay>1000</redelivery-delay>
  <redelivery-multiplier>2.0</redelivery-multiplier>
</address-setting>
```

### DLQ Consumer

```java
@JmsListener(destination = "DLQ.orders")
public void handleDeadLetter(Message message) throws JMSException {
    String originalDest = message.getStringProperty("_AMQ_ORIG_ADDRESS");
    int deliveryCount = message.getIntProperty("JMSXDeliveryCount");
    // log, alert, or store for manual review
}
```

## Scheduled/Delayed Delivery

### Classic

```java
public void sendDelayed(Order order, long delayMs) {
    jmsTemplate.convertAndSend("orders", order, message -> {
        message.setLongProperty(ScheduledMessage.AMQ_SCHEDULED_DELAY, delayMs);
        return message;
    });
}

// Schedule for specific time
public void sendScheduled(Order order, long timestamp) {
    jmsTemplate.convertAndSend("orders", order, message -> {
        message.setLongProperty(ScheduledMessage.AMQ_SCHEDULED_PERIOD, timestamp);
        return message;
    });
}
```

### Artemis

```java
public void sendDelayed(Order order, long delayMs) {
    jmsTemplate.convertAndSend("orders", order, message -> {
        message.setLongProperty("_AMQ_SCHED_DELIVERY",
            System.currentTimeMillis() + delayMs);
        return message;
    });
}
```

## Priority Messages

JMS supports 10 priority levels (0-9, default 4):

```java
public void sendHighPriority(Order order) {
    jmsTemplate.convertAndSend("orders", order, message -> {
        message.setJMSPriority(9); // highest priority
        return message;
    });
}
```

Enable priority support:

**Classic** (activemq.xml):

```xml
<policyEntry queue="orders" prioritizedMessages="true"/>
```

**Artemis** — priority is supported by default. Messages are delivered highest priority first.

## Message TTL/Expiration

Messages can expire and be removed from the queue:

```java
// Set TTL on producer level
jmsTemplate.setExplicitQosEnabled(true);
jmsTemplate.setTimeToLive(60000); // 60 seconds

// Per-message TTL
public void sendWithTTL(Order order) {
    jmsTemplate.send("orders", session -> {
        TextMessage msg = session.createTextMessage(toJson(order));
        // TTL set via producer.send() overload
        return msg;
    });
}
```

Expired messages are moved to the expiry address (Artemis) or discarded (Classic, unless configured):

**Artemis** (broker.xml):

```xml
<address-setting match="#">
  <expiry-address>ExpiryQueue</expiry-address>
  <expiry-delay>-1</expiry-delay>
</address-setting>
```

## Exercises

1. **Request-reply**: Implement a service that sends an order request and waits for a confirmation reply. Use `JMSCorrelationID` to match responses.

2. **Competing consumers**: Start 3 consumer instances on the same queue. Send 30 messages and verify each consumer gets approximately 10.

3. **Message groups**: Send 30 messages with 3 different group IDs (10 each). Verify all messages in a group go to the same consumer.

4. **DLQ handling**: Configure a DLQ with max 3 retries. Create a listener that always throws an exception. Verify the message lands in the DLQ after 3 attempts. Write a DLQ consumer that logs the failure.

5. **Delayed delivery**: Send a message with a 10-second delay. Verify it is not consumed immediately but appears after the delay.
