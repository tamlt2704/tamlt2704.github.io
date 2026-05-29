# Messaging Concepts

[prev: Overview](/blog/activemq/chapter-00-overview) | [next: Setup](/blog/activemq/chapter-02-setup)

## What is a Message Broker?

A message broker is middleware that translates messages between formal messaging protocols, enabling applications to communicate without knowing each other's location or implementation details. It acts as an intermediary that receives messages from producers and routes them to consumers.

Key benefits:

- **Decoupling** — Producers and consumers are independent
- **Buffering** — Messages are stored until consumers are ready
- **Routing** — Messages are directed based on rules
- **Reliability** — Messages survive crashes via persistence

## JMS (Java Message Service)

JMS is a Java API specification for message-oriented middleware. It defines a standard interface for producing, sending, and consuming messages. ActiveMQ implements JMS 1.1 (Classic) and JMS 2.0 (Artemis).

Core JMS objects:

```java
// ConnectionFactory — creates connections
ConnectionFactory factory = new ActiveMQConnectionFactory("tcp://localhost:61616");

// Connection — network connection to the broker
Connection connection = factory.createConnection();

// Session — single-threaded context for producing/consuming
Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

// Destination — queue or topic
Destination queue = session.createQueue("orders");

// Producer — sends messages
MessageProducer producer = session.createProducer(queue);

// Consumer — receives messages
MessageConsumer consumer = session.createConsumer(queue);

connection.start();
Message message = consumer.receive(5000); // blocking with timeout
```

## Queues vs Topics

### Queue (Point-to-Point)

- Each message is consumed by **exactly one** consumer
- Messages are persisted until consumed or expired
- Supports load balancing across multiple consumers
- Use case: task processing, order handling

```
Producer -> [Queue] -> Consumer A (gets msg 1, 3, 5)
                    -> Consumer B (gets msg 2, 4, 6)
```

### Topic (Publish/Subscribe)

- Each message is delivered to **all** active subscribers
- Messages are lost if no subscriber is active (unless durable)
- Use case: event broadcasting, notifications

```
Publisher -> [Topic] -> Subscriber A (gets all messages)
                     -> Subscriber B (gets all messages)
                     -> Subscriber C (gets all messages)
```

### Durable Subscriptions

Topics can have durable subscribers that receive messages even when disconnected:

```java
Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
Topic topic = session.createTopic("events");
MessageConsumer durableSub = session.createDurableSubscriber(topic, "my-subscription");
```

## Message Structure

A JMS message has three parts: headers, properties, and body.

### Headers (set by broker or producer)

| Header           | Description                               |
| ---------------- | ----------------------------------------- |
| JMSMessageID     | Unique message identifier                 |
| JMSDestination   | Queue or topic the message is sent to     |
| JMSTimestamp     | Time the message was handed to the broker |
| JMSExpiration    | When the message expires (0 = never)      |
| JMSPriority      | 0-9, default 4 (higher = more urgent)     |
| JMSDeliveryMode  | PERSISTENT or NON_PERSISTENT              |
| JMSRedelivered   | True if message was redelivered           |
| JMSReplyTo       | Destination for reply messages            |
| JMSCorrelationID | Links reply to request                    |

### Properties (custom metadata)

```java
message.setStringProperty("orderType", "PREMIUM");
message.setIntProperty("retryCount", 0);
message.setBooleanProperty("urgent", true);
```

### Body Types

```java
// TextMessage — String content (JSON, XML, plain text)
TextMessage textMsg = session.createTextMessage("{\"orderId\": 123}");

// ObjectMessage — Serializable Java object
ObjectMessage objMsg = session.createObjectMessage(new Order(123, "item"));

// MapMessage — key-value pairs
MapMessage mapMsg = session.createMapMessage();
mapMsg.setString("name", "Widget");
mapMsg.setInt("quantity", 5);

// BytesMessage — raw bytes
BytesMessage bytesMsg = session.createBytesMessage();
bytesMsg.writeBytes(imageData);
```

**Best practice**: Prefer `TextMessage` with JSON for interoperability. `ObjectMessage` requires the same class on both sides and has security implications (deserialization attacks).

## Acknowledgment Modes

Acknowledgment tells the broker a message has been successfully processed:

| Mode                  | Behavior                                                                |
| --------------------- | ----------------------------------------------------------------------- |
| `AUTO_ACKNOWLEDGE`    | Acknowledged when `receive()` returns or `onMessage()` completes        |
| `CLIENT_ACKNOWLEDGE`  | Consumer must explicitly call `message.acknowledge()`                   |
| `DUPS_OK_ACKNOWLEDGE` | Lazy acknowledgment, may cause duplicates but improves performance      |
| `SESSION_TRANSACTED`  | Acknowledged on `session.commit()`, rolled back on `session.rollback()` |

```java
// Client acknowledge example
Session session = connection.createSession(false, Session.CLIENT_ACKNOWLEDGE);
Message msg = consumer.receive();
// process message...
msg.acknowledge(); // explicitly acknowledge
```

## Message Selectors

Selectors filter messages using a SQL92-like syntax on headers and properties:

```java
// Only receive premium orders
MessageConsumer consumer = session.createConsumer(queue, "orderType = 'PREMIUM'");

// Priority above 5
MessageConsumer urgent = session.createConsumer(queue, "JMSPriority > 5");

// Compound selector
MessageConsumer filtered = session.createConsumer(queue,
    "orderType = 'PREMIUM' AND amount > 1000");
```

Selectors are evaluated on the broker side, reducing network traffic.

## Classic vs Artemis: Concepts

| Concept       | Classic            | Artemis                            |
| ------------- | ------------------ | ---------------------------------- |
| Queue         | JMS Queue          | Address with anycast routing       |
| Topic         | JMS Topic          | Address with multicast routing     |
| Durable Sub   | Named subscription | Durable queue on multicast address |
| Selector      | Supported          | Supported (with filter syntax)     |
| Message types | All JMS types      | All JMS types + AMQP types         |

## Exercises

1. **Explore message types**: Write a producer that sends one of each message type (Text, Map, Object, Bytes) to a queue. Write a consumer that detects the type and prints the content.

2. **Selector filtering**: Create a producer that sends 20 messages with random `priority` property (1-10). Create two consumers: one that only receives `priority > 7`, another that receives `priority <= 7`.

3. **Queue vs Topic behavior**: Set up one queue and one topic. Send 10 messages to each with 2 consumers on each. Observe the distribution difference.

4. **Client acknowledgment**: Create a consumer with CLIENT_ACKNOWLEDGE that processes messages but only acknowledges every 3rd message. Restart the consumer and observe which messages are redelivered.
