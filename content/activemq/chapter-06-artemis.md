# ActiveMQ Artemis Specifics

[prev: Reliability](/blog/activemq/chapter-05-reliability) | [next: Production](/blog/activemq/chapter-07-production)

## Architecture

Artemis uses a journal-based storage engine optimized for messaging workloads:

```
Client -> Acceptor -> Server Engine -> Journal (persistence)
                                    -> Paging (overflow to disk)
                                    -> Address Model (routing)
```

### Journal-Based Storage

- **Append-only** writes for maximum throughput
- **libaio** on Linux (kernel-level async I/O) or **NIO** on other platforms
- Journal files are pre-created and recycled (no filesystem allocation during operation)
- Compaction reclaims space from deleted messages

Configuration (broker.xml):

```xml
<journal-type>ASYNCIO</journal-type> <!-- or NIO -->
<journal-directory>data/journal</journal-directory>
<journal-min-files>2</journal-min-files>
<journal-pool-files>10</journal-pool-files>
<journal-file-size>10M</journal-file-size>
<journal-buffer-timeout>500000</journal-buffer-timeout>
<journal-max-io>4096</journal-max-io>
```

## Address Model

Artemis replaces the traditional queue/topic distinction with a unified address model:

```
Address (logical name)
  |
  +-- Queue (anycast)   -> point-to-point (like JMS Queue)
  +-- Queue (multicast) -> pub/sub (like JMS Topic)
```

### Anycast (Queue Semantics)

Each message goes to exactly one consumer:

```xml
<address name="orders">
  <anycast>
    <queue name="orders"/>
  </anycast>
</address>
```

### Multicast (Topic Semantics)

Each message goes to all subscriptions:

```xml
<address name="events">
  <multicast>
    <queue name="sub-1"/>
    <queue name="sub-2"/>
  </multicast>
</address>
```

### Both on Same Address

```xml
<address name="notifications">
  <anycast>
    <queue name="notifications"/>
  </anycast>
  <multicast>
    <queue name="notifications-audit"/>
  </multicast>
</address>
```

## Diverts

Diverts transparently redirect messages from one address to another:

### Exclusive Divert (redirect all)

```xml
<divert name="orders-divert">
  <address>orders</address>
  <forwarding-address>orders-archive</forwarding-address>
  <exclusive>true</exclusive>
</divert>
```

### Non-Exclusive Divert (copy)

```xml
<divert name="orders-copy">
  <address>orders</address>
  <forwarding-address>orders-audit</forwarding-address>
  <exclusive>false</exclusive>
  <filter string="orderType = 'PREMIUM'"/>
</divert>
```

Use cases:

- Audit logging without modifying producers
- Traffic splitting for A/B testing
- Migration (redirect old address to new)

## Last-Value Queues

Only the last message for each key is retained. Useful for status updates where only the latest matters:

```xml
<address name="stock-prices">
  <anycast>
    <queue name="stock-prices" last-value-key="symbol"/>
  </anycast>
</address>
```

```java
// Only the latest price per symbol is kept
public void sendPrice(String symbol, double price) {
    jmsTemplate.convertAndSend("stock-prices", price, message -> {
        message.setStringProperty("symbol", symbol);
        message.setStringProperty("_AMQ_LVQ_NAME", symbol);
        return message;
    });
}
```

If you send 100 updates for "AAPL", only the last one remains in the queue.

## Ring Queues

Fixed-size queues that drop the oldest message when full:

```xml
<address name="recent-events">
  <anycast>
    <queue name="recent-events" ring-size="1000"/>
  </anycast>
</address>
```

Use cases:

- Keep only the N most recent events
- Bounded memory usage for high-volume streams
- Dashboard feeds where old data is irrelevant

## Message Grouping

Artemis supports message grouping with automatic rebalancing:

```xml
<address-setting match="orders">
  <default-group-rebalance>true</default-group-rebalance>
  <group-rebalance-pause-dispatch>true</group-rebalance-pause-dispatch>
  <group-buckets>64</group-buckets>
</address-setting>
```

- `group-buckets` — Number of group buckets (limits memory usage for many groups)
- `default-group-rebalance` — Rebalance groups when consumers change
- `group-rebalance-pause-dispatch` — Pause delivery during rebalance

## Large Messages

Messages exceeding a threshold are stored outside the journal:

```xml
<large-messages-directory>data/large-messages</large-messages-directory>
```

Client-side configuration:

```java
ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("tcp://localhost:61616");
factory.setMinLargeMessageSize(100 * 1024); // 100KB threshold
```

Messages above this size are streamed to/from disk rather than held in memory. Useful for file transfers or large payloads.

## Paging

When queues exceed memory limits, messages are paged to disk:

```xml
<address-setting match="#">
  <max-size-bytes>100M</max-size-bytes>
  <page-size-bytes>10M</page-size-bytes>
  <address-full-policy>PAGE</address-full-policy>
</address-setting>
```

Policies when address is full:

- `PAGE` — Write to disk (default, safe)
- `DROP` — Discard new messages
- `BLOCK` — Block producers until space available
- `FAIL` — Reject with exception

## Protocol Support

Artemis supports multiple protocols on the same port:

```xml
<acceptors>
  <acceptor name="all-protocols">
    tcp://0.0.0.0:61616?protocols=AMQP,STOMP,MQTT,OPENWIRE,HORNETQ
  </acceptor>
  <!-- Or dedicated ports -->
  <acceptor name="amqp">tcp://0.0.0.0:5672?protocols=AMQP</acceptor>
  <acceptor name="mqtt">tcp://0.0.0.0:1883?protocols=MQTT</acceptor>
  <acceptor name="stomp">tcp://0.0.0.0:61613?protocols=STOMP</acceptor>
</acceptors>
```

### AMQP Client Example

```java
// Using Qpid JMS (AMQP 1.0)
// build.gradle: implementation 'org.apache.qpid:qpid-jms-client:1.10.0'

ConnectionFactory factory = new JmsConnectionFactory("amqp://localhost:5672");
Connection connection = factory.createConnection("admin", "admin");
```

### MQTT Client Example

```java
// Using Eclipse Paho
// build.gradle: implementation 'org.eclipse.paho:org.eclipse.paho.client.mqttv3:1.2.5'

MqttClient client = new MqttClient("tcp://localhost:1883", "client-1");
client.connect();
client.publish("sensors/temperature", "22.5".getBytes(), 1, false);
```

### STOMP Example

```bash
# Connect via telnet/netcat
echo -e "CONNECT\naccept-version:1.2\nhost:localhost\n\n\0" | nc localhost 61613
```

## Exercises

1. **Address model**: Create an address with both anycast and multicast queues. Send a message and observe which queues receive it based on routing type.

2. **Diverts**: Set up a non-exclusive divert that copies all messages from "orders" to "orders-audit". Send messages and verify both destinations receive them.

3. **Last-value queue**: Create a last-value queue for stock prices. Send 50 updates for 5 symbols. Verify only 5 messages remain (one per symbol).

4. **Ring queue**: Create a ring queue with size 10. Send 100 messages. Verify only the last 10 are available for consumption.

5. **Multi-protocol**: Connect to the same Artemis broker using JMS (OpenWire), AMQP, and MQTT. Send a message from one protocol and receive from another.
