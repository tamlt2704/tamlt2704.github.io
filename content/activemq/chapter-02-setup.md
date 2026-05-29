# Setup

[prev: Messaging Concepts](/blog/activemq/chapter-01-concepts) | [next: Spring Boot + JMS](/blog/activemq/chapter-03-spring-jms)

## Docker Setup

### ActiveMQ Classic

```bash
docker run -d --name activemq-classic \
  -p 61616:61616 \
  -p 8161:8161 \
  apache/activemq-classic:latest
```

Ports:

- `61616` — OpenWire (JMS) protocol
- `8161` — Web console

Default credentials: `admin` / `admin`

Web console: http://localhost:8161/admin

### ActiveMQ Artemis

```bash
docker run -d --name activemq-artemis \
  -p 61616:61616 \
  -p 8161:8161 \
  -e ARTEMIS_USER=admin \
  -e ARTEMIS_PASSWORD=admin \
  apache/activemq-artemis:latest
```

Ports:

- `61616` — All protocols (AMQP, STOMP, MQTT, OpenWire, HornetQ)
- `8161` — Hawtio web console

Web console: http://localhost:8161/console

### Docker Compose (Both)

```yaml
version: "3.8"
services:
  activemq-classic:
    image: apache/activemq-classic:latest
    ports:
      - "61616:61616"
      - "8161:8161"

  activemq-artemis:
    image: apache/activemq-artemis:latest
    ports:
      - "61617:61616"
      - "8162:8161"
    environment:
      ARTEMIS_USER: admin
      ARTEMIS_PASSWORD: admin
```

## Web Console

### Classic Web Console

Navigate to http://localhost:8161/admin:

- **Queues** — View, create, delete queues; browse messages; send test messages
- **Topics** — View active topics and subscribers
- **Connections** — Monitor active connections
- **Subscribers** — View durable subscribers

### Artemis Hawtio Console

Navigate to http://localhost:8161/console:

- **Artemis** tab — Addresses, queues, connections, sessions
- **JMX** tab — Full MBean access
- **Create Address** — Define new addresses with routing type

## CLI Tools

### Artemis CLI

```bash
# Enter the container
docker exec -it activemq-artemis /bin/bash

# Create a queue
./artemis queue create --name orders --address orders --anycast --durable --auto-create-address

# Send a message
./artemis producer --destination orders --message-count 10 --message "Hello ActiveMQ"

# Consume messages
./artemis consumer --destination orders --message-count 10

# Browse queue without consuming
./artemis browser --destination orders

# Queue stats
./artemis queue stat
```

### Classic: activemq CLI

```bash
docker exec -it activemq-classic /bin/bash

# Basic producer
activemq producer --destination queue://orders --messageCount 10

# Basic consumer
activemq consumer --destination queue://orders --messageCount 10
```

## Creating Queues and Topics

### Via Web Console

**Classic**: Navigate to Queues tab, enter queue name, click Create.

**Artemis**: Navigate to Artemis tab, Create Address, specify name and routing type (anycast for queue, multicast for topic).

### Programmatically (auto-create)

Both Classic and Artemis support auto-creation. When a producer sends to a non-existent destination, it is created automatically.

In Artemis `broker.xml`:

```xml
<address-setting match="#">
  <auto-create-queues>true</auto-create-queues>
  <auto-create-addresses>true</auto-create-addresses>
</address-setting>
```

## Sending Test Messages via Console

### Artemis CLI

```bash
# Send text message
./artemis producer --destination orders --message "Test order message"

# Send multiple with properties
./artemis producer --destination orders \
  --message-count 5 \
  --message "Order payload"

# Send from file
./artemis producer --destination orders --data /path/to/message.txt
```

### Classic Web Console

1. Go to http://localhost:8161/admin/queues.jsp
2. Click on the queue name
3. Click "Send To" tab
4. Enter message body and optional headers
5. Click "Send"

## Connection URLs

### Basic TCP

```
tcp://localhost:61616
```

### Failover (Client-side HA)

Automatically reconnects to another broker on failure:

```
failover:(tcp://broker1:61616,tcp://broker2:61616)?randomize=true&maxReconnectAttempts=10
```

Options:

- `randomize=true` — Random broker selection
- `maxReconnectAttempts` — Max reconnection attempts (-1 = infinite)
- `initialReconnectDelay` — Milliseconds before first retry
- `maxReconnectDelay` — Max delay between retries

## Embedded Broker for Testing

### Classic Embedded Broker

```java
// build.gradle
dependencies {
    testImplementation 'org.apache.activemq:activemq-broker:5.18.3'
    testImplementation 'org.apache.activemq:activemq-kahadb-store:5.18.3'
}
```

```java
import org.apache.activemq.broker.BrokerService;

public class EmbeddedBrokerTest {
    private BrokerService broker;

    void startBroker() throws Exception {
        broker = new BrokerService();
        broker.addConnector("tcp://localhost:61616");
        broker.setPersistent(false);
        broker.setUseJmx(false);
        broker.start();
    }

    void stopBroker() throws Exception {
        broker.stop();
    }
}
```

### Artemis Embedded Broker

```java
// build.gradle
dependencies {
    testImplementation 'org.apache.activemq:artemis-server:2.31.2'
    testImplementation 'org.apache.activemq:artemis-jms-server:2.31.2'
}
```

```java
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.core.config.impl.ConfigurationImpl;

public class EmbeddedArtemisTest {
    private EmbeddedActiveMQ server;

    void startBroker() throws Exception {
        var config = new ConfigurationImpl()
            .setPersistenceEnabled(false)
            .setSecurityEnabled(false)
            .addAcceptorConfiguration("invm", "vm://0")
            .addAcceptorConfiguration("tcp", "tcp://localhost:61616");

        server = new EmbeddedActiveMQ();
        server.setConfiguration(config);
        server.start();
    }

    void stopBroker() throws Exception {
        server.stop();
    }
}
```

### Spring Boot Test with Embedded Artemis

```java
// build.gradle
dependencies {
    testImplementation 'org.apache.activemq:artemis-junit-5:2.31.2'
}
```

```java
import org.apache.activemq.artemis.junit.EmbeddedActiveMQExtension;
import org.junit.jupiter.api.extension.RegisterExtension;

class MessagingIntegrationTest {

    @RegisterExtension
    static EmbeddedActiveMQExtension artemis = new EmbeddedActiveMQExtension();

    @Test
    void shouldSendAndReceiveMessage() {
        // test with real broker
    }
}
```

## Exercises

1. **Run both brokers**: Start Classic on ports 61616/8161 and Artemis on 61617/8162. Send a message via each web console and consume it.

2. **CLI exploration**: Use the Artemis CLI to create a queue, send 100 messages, browse them without consuming, then consume all.

3. **Failover URL**: Start two Artemis instances. Configure a client with a failover URL. Send messages, stop one broker, and verify the client reconnects.

4. **Embedded test**: Write a JUnit 5 test that starts an embedded Artemis broker, sends a message, and asserts it is received correctly.
