# Chapter 1: Route a Message from A to B

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Transform HL7 to JSON →](chapter-02-transformers.md)

---

## The Task

Miriam's first assignment:

> "Start simple. The lab system drops result files into a folder. We need to pick them up and move them to an outbound folder for the hospital's system to collect. That's it. File in, file out. The ESB does this with Flow #1 — the only flow anyone understands."

File in. File out. How hard can it be?

---

## The Three Core Concepts

Before writing code, understand the three things that make Spring Integration tick:

### 1. Message

A message has two parts:

```java
// Conceptually:
Message<String> message = MessageBuilder
    .withPayload("Patient lab result: glucose 95 mg/dL")
    .setHeader("patientId", "P-12345")
    .setHeader("labType", "blood")
    .setHeader("priority", "normal")
    .build();

message.getPayload();  // "Patient lab result: glucose 95 mg/dL"
message.getHeaders();  // {patientId=P-12345, labType=blood, priority=normal, id=..., timestamp=...}
```

- **Payload**: The actual data (String, byte[], File, your domain object — anything)
- **Headers**: Metadata about the message (routing info, timestamps, correlation IDs)

Messages are **immutable**. You don't modify a message — you create a new one with different payload/headers.

### 2. Channel

A channel is a pipe between components. Two main types:

```java
// DirectChannel — synchronous, single subscriber (like a method call)
// The sender blocks until the receiver processes the message.
DirectChannel direct = new DirectChannel();

// QueueChannel — asynchronous, buffered (like a mailbox)
// The sender drops the message and moves on. Receiver polls when ready.
QueueChannel queue = new QueueChannel(100); // capacity 100
```

For now, we'll use `DirectChannel` (the default). We'll need `QueueChannel` in Chapter 8 when throughput matters.

### 3. Endpoint

An endpoint sits on a channel and does something with messages:

- **Transformer**: Changes the payload or headers
- **Filter**: Drops messages that don't match a condition
- **Router**: Sends messages to different channels based on content
- **Splitter**: Breaks one message into many
- **Aggregator**: Combines many messages into one
- **Service Activator**: Calls your business logic

---

## The First Flow: File In, File Out

```java
// src/main/java/com/medibridge/flows/FileTransferFlow.java
package com.medibridge.flows;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.Pollers;
import org.springframework.integration.file.dsl.Files;

import java.io.File;

@Configuration
public class FileTransferFlow {

    @Bean
    public IntegrationFlow labResultFileFlow() {
        return IntegrationFlow
            .from(Files.inboundAdapter(new File("input/labs"))
                    .autoCreateDirectory(true)
                    .patternFilter("*.txt"),
                e -> e.poller(Pollers.fixedDelay(1000)))  // Poll every 1 second
            .handle(Files.outboundAdapter(new File("output/labs"))
                    .autoCreateDirectory(true))
            .get();
    }
}
```

That's it. 15 lines. The ESB needed a 47-click GUI wizard for this.

### What's Happening

```
  input/labs/*.txt  →  [Inbound File Adapter]  →  channel  →  [Outbound File Adapter]  →  output/labs/
       (poll)              reads file                              writes file
```

1. Every 1 second, the **inbound adapter** checks `input/labs/` for `.txt` files
2. When it finds one, it creates a `Message<File>` with the file as payload
3. The message flows through an implicit `DirectChannel`
4. The **outbound adapter** writes the file to `output/labs/`
5. The original file is moved (default behavior — prevents re-processing)

### Test It

```bash
mkdir -p input/labs
echo "Patient: P-12345, Glucose: 95 mg/dL" > input/labs/result001.txt
./gradlew bootRun
```

Wait 1 second. Check `output/labs/`:

```bash
cat output/labs/result001.txt
# Patient: P-12345, Glucose: 95 mg/dL
```

The file moved. Flow #1 is migrated.

---

## Understanding the DSL

Let's break down the fluent API:

```java
IntegrationFlow.from(source)     // Where messages come FROM (inbound adapter)
    .channel("myChannel")         // Explicit channel name (optional — auto-created if omitted)
    .filter(condition)            // Drop messages that don't match
    .transform(transformation)    // Change the payload
    .handle(handler)              // Process the message (terminal operation)
    .get();                       // Build the flow
```

Each method in the chain adds a component to the flow. Spring Integration wires them together with channels automatically.

---

## Writing a Proper Test

Don't rely on manual file drops. Write an integration test:

```java
// src/test/java/com/medibridge/flows/FileTransferFlowTest.java
package com.medibridge.flows;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.integration.test.context.SpringIntegrationTest;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.support.GenericMessage;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;
import static org.awaitility.Awaitility.await;
import java.time.Duration;

@SpringBootTest
@SpringIntegrationTest
class FileTransferFlowTest {

    @TempDir
    Path tempDir;

    @Test
    void shouldTransferFileFromInputToOutput() throws Exception {
        // Given: a file in the input directory
        Path inputDir = tempDir.resolve("input/labs");
        Path outputDir = tempDir.resolve("output/labs");
        Files.createDirectories(inputDir);

        Path inputFile = inputDir.resolve("test-result.txt");
        Files.writeString(inputFile, "Patient: P-99999, Glucose: 110 mg/dL");

        // When: the poller picks it up (wait for async processing)
        await().atMost(Duration.ofSeconds(5)).untilAsserted(() -> {
            // Then: the file appears in the output directory
            File outputFile = outputDir.resolve("test-result.txt").toFile();
            assertThat(outputFile).exists();
            assertThat(Files.readString(outputFile.toPath()))
                .contains("Patient: P-99999");
        });
    }
}
```

Add Awaitility to `build.gradle`:

```groovy
testImplementation 'org.awaitility:awaitility:4.2.1'
```

```bash
./gradlew test
```

---

## Sending Messages Programmatically

You don't always need file adapters. You can send messages directly to channels:

```java
// src/main/java/com/medibridge/flows/SimpleFlow.java
package com.medibridge.flows;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.channel.DirectChannel;
import org.springframework.messaging.MessageChannel;

@Configuration
public class SimpleFlow {

    @Bean
    public MessageChannel labResultChannel() {
        return new DirectChannel();
    }

    @Bean
    public IntegrationFlow processLabResult() {
        return IntegrationFlow.from("labResultChannel")
            .log()  // Log the message (useful for debugging)
            .handle((payload, headers) -> {
                System.out.println("Received: " + payload);
                System.out.println("Headers: " + headers);
                return null;  // null = don't pass to next endpoint
            })
            .get();
    }
}
```

### Send a Message via Gateway

```java
// src/main/java/com/medibridge/gateways/LabResultGateway.java
package com.medibridge.gateways;

import org.springframework.integration.annotation.Gateway;
import org.springframework.integration.annotation.MessagingGateway;

@MessagingGateway
public interface LabResultGateway {

    @Gateway(requestChannel = "labResultChannel")
    void sendLabResult(String labResult);
}
```

A **gateway** is the entry point from your application code into the messaging system. It hides the messaging infrastructure — callers just invoke a method.

```java
// Usage in a REST controller or service:
@RestController
public class LabController {

    private final LabResultGateway gateway;

    public LabController(LabResultGateway gateway) {
        this.gateway = gateway;
    }

    @PostMapping("/labs")
    public ResponseEntity<String> submitLab(@RequestBody String labResult) {
        gateway.sendLabResult(labResult);
        return ResponseEntity.accepted().build();
    }
}
```

The controller doesn't know about channels, messages, or integration flows. It just calls a method. Spring Integration handles the rest.

---

## The Message Lifecycle

```
  Gateway.sendLabResult("glucose: 95")
       │
       ▼
  Message<String> created automatically:
    payload = "glucose: 95"
    headers = {id=uuid, timestamp=..., replyChannel=...}
       │
       ▼
  labResultChannel (DirectChannel)
       │
       ▼
  .log() endpoint — prints message to console
       │
       ▼
  .handle() endpoint — your business logic
```

Every method call on the gateway becomes a `Message`. Every step in the flow receives that message, optionally transforms it, and passes it to the next channel.

---

## Report to Miriam

> **Flow #1 migrated:**
> - File inbound adapter polls `input/labs/` every second
> - Files transferred to `output/labs/` automatically
> - Integration test verifies the flow end-to-end
> - Gateway interface allows programmatic message submission
>
> 15 lines of code. The ESB needed 47 GUI clicks and a prayer.

Miriam: "Good. Now the hard part — the lab system sends HL7 format. The hospital wants JSON. Transform it."

---

## What You Learned

- **Message** = payload + headers. Immutable. The unit of work in Spring Integration.
- **Channel** = pipe between components. `DirectChannel` (sync) or `QueueChannel` (async).
- **Endpoint** = something that processes messages (transform, filter, route, handle).
- **Inbound Adapter** = reads from external system, creates messages.
- **Outbound Adapter** = receives messages, writes to external system.
- **Gateway** = entry point from application code into the messaging system.
- The **DSL** (`IntegrationFlow.from(...).transform(...).handle(...)`) chains components fluently.
- **Pollers** drive inbound adapters — they check for new data on a schedule.
- Always write integration tests — don't rely on manual file drops.

---

[Next: Chapter 2 — "Transform HL7 to JSON" →](chapter-02-transformers.md)
