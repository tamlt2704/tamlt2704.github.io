# Chapter 3: Route Labs to the Right Hospital

[← Chapter 2: Transform HL7 to JSON](chapter-02-transformers.md) | [Chapter 4: Split a Batch File →](chapter-04-splitters.md)

---

## The Disaster

You deployed the transformation flow. All lab results now arrive as JSON in `output/labs-json/`. Beautiful.

Problem: there are 5 hospitals. Hospital A's results are going to the same folder as Hospital C's. Dr. Patel from Hospital A calls Miriam:

> "We're seeing lab results for patients that aren't ours. This is a HIPAA violation waiting to happen."

Miriam to you:

> "Route messages to the correct hospital based on the `destination` header. Hospital A gets their results. Hospital C gets theirs. Nobody sees anyone else's data."

---

## Routers: Directing Traffic

A **router** examines a message and decides which channel it goes to next. Think of it as a traffic cop at an intersection.

```java
// src/main/java/com/medibridge/flows/LabRoutingFlow.java
package com.medibridge.flows;

import com.medibridge.transformers.Hl7ToJsonTransformer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.Pollers;
import org.springframework.integration.file.dsl.Files;

import java.io.File;

@Configuration
public class LabRoutingFlow {

    @Bean
    public IntegrationFlow labRoutingFlow(Hl7ToJsonTransformer transformer) {
        return IntegrationFlow
            .from(Files.inboundAdapter(new File("input/labs"))
                    .autoCreateDirectory(true)
                    .patternFilter("*.hl7"),
                e -> e.poller(Pollers.fixedDelay(1000)))
            .transform(Files.toStringTransformer())
            // Extract destination before transforming (it's in the HL7 MSH segment)
            .enrichHeaders(h -> h
                .headerExpression("destination",
                    "payload.split('\\n')[0].split('\\|')[4]"))
            .transform(transformer, "transform")
            // Route based on the destination header
            .<String, String>route(
                msg -> msg.getHeaders().get("destination", String.class),
                mapping -> mapping
                    .subFlowMapping("HOSP_A", sf -> sf
                        .handle(Files.outboundAdapter(new File("output/hosp-a"))
                            .autoCreateDirectory(true)))
                    .subFlowMapping("HOSP_B", sf -> sf
                        .handle(Files.outboundAdapter(new File("output/hosp-b"))
                            .autoCreateDirectory(true)))
                    .subFlowMapping("HOSP_C", sf -> sf
                        .handle(Files.outboundAdapter(new File("output/hosp-c"))
                            .autoCreateDirectory(true)))
                    .defaultSubFlowMapping(sf -> sf
                        .handle(Files.outboundAdapter(new File("output/unknown"))
                            .autoCreateDirectory(true)))
            )
            .get();
    }
}
```

### What's Happening

```
  input/labs/*.hl7
       │
       ▼
  [Enrich Headers] — extract destination from HL7
       │
       ▼
  [Transform] — HL7 → JSON
       │
       ▼
  [Router] — check "destination" header
       │
       ├── "HOSP_A" → output/hosp-a/
       ├── "HOSP_B" → output/hosp-b/
       ├── "HOSP_C" → output/hosp-c/
       └── default  → output/unknown/
```

---

## Router Types

### Header Value Router (Simplest)

When routing is based on a single header value:

```java
.headerValueRouter("destination",
    mapping -> mapping
        .channelMapping("HOSP_A", "hospAChannel")
        .channelMapping("HOSP_B", "hospBChannel")
        .resolutionRequired(false)
        .defaultOutputChannel("unknownChannel"))
```

### Payload-Based Router

When the routing decision is in the payload itself:

```java
.<String, String>route(
    payload -> {
        // Parse JSON and extract destination
        JsonNode node = mapper.readTree(payload);
        return node.get("destination").asText();
    },
    mapping -> mapping
        .subFlowMapping("HOSP_A", sf -> sf.channel("hospAChannel"))
        .subFlowMapping("HOSP_B", sf -> sf.channel("hospBChannel"))
)
```

### Expression-Based Router

For simple routing logic, use SpEL expressions:

```java
.route("headers['priority']",
    mapping -> mapping
        .channelMapping("CRITICAL", "urgentChannel")
        .channelMapping("NORMAL", "standardChannel")
        .defaultOutputChannel("standardChannel"))
```

---

## Recipient List Router: Send to Multiple Destinations

Sometimes a message needs to go to more than one place. Insurance claims go to both the insurance provider AND the hospital's billing department:

```java
@Bean
public IntegrationFlow claimRoutingFlow() {
    return IntegrationFlow.from("claimChannel")
        .routeToRecipients(r -> r
            .recipient("insuranceChannel",
                "headers['claimType'] == 'INSURANCE'")
            .recipient("billingChannel")          // Always gets a copy
            .recipient("auditChannel")            // Compliance Carl's copy
        )
        .get();
}
```

The recipient list router **copies** the message to each matching recipient. The original message is unchanged.

---

## Dynamic Routing: When Destinations Change

Hospitals join and leave. You can't hardcode every destination:

```java
// src/main/java/com/medibridge/routing/DynamicRouter.java
package com.medibridge.routing;

import org.springframework.integration.annotation.Router;
import org.springframework.messaging.Message;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class DynamicRouter {

    // In production, this would come from a database or config service
    private final Map<String, String> routingTable = new ConcurrentHashMap<>(Map.of(
        "HOSP_A", "hospAChannel",
        "HOSP_B", "hospBChannel",
        "HOSP_C", "hospCChannel",
        "HOSP_D", "hospDChannel",
        "HOSP_E", "hospEChannel"
    ));

    @Router(inputChannel = "routingChannel")
    public String route(Message<?> message) {
        String destination = message.getHeaders().get("destination", String.class);
        String channel = routingTable.getOrDefault(destination, "unknownChannel");
        return channel;
    }

    // Called by admin API to update routing at runtime
    public void addRoute(String destination, String channel) {
        routingTable.put(destination, channel);
    }

    public void removeRoute(String destination) {
        routingTable.remove(destination);
    }
}
```

Use it in a flow:

```java
@Bean
public IntegrationFlow dynamicRoutingFlow(DynamicRouter router) {
    return IntegrationFlow.from("transformedLabChannel")
        .route(router, "route")
        .get();
}
```

Now you can add hospitals without redeploying. Update the routing table via an admin endpoint.

---

## Filters: Drop Messages That Don't Belong

Sometimes you want to discard messages entirely — not route them, just drop them:

```java
@Bean
public IntegrationFlow filteredFlow() {
    return IntegrationFlow.from("rawLabChannel")
        .filter(Message.class,
            msg -> msg.getHeaders().get("priority", String.class) != null,
            f -> f.discardChannel("invalidMessageChannel"))  // Where rejected messages go
        .filter(String.class,
            payload -> payload.startsWith("MSH"),  // Must be valid HL7
            f -> f.discardChannel("malformedChannel"))
        .transform(transformer, "transform")
        .channel("routingChannel")
        .get();
    }
```

Filters return `true` (pass) or `false` (discard). The `discardChannel` catches rejected messages — useful for debugging and auditing.

---

## Testing the Router

```java
// src/test/java/com/medibridge/flows/LabRoutingFlowTest.java
package com.medibridge.flows;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.integration.test.context.SpringIntegrationTest;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.PollableChannel;
import org.springframework.messaging.support.MessageBuilder;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@SpringIntegrationTest
class LabRoutingFlowTest {

    @Autowired
    @Qualifier("routingChannel")
    private MessageChannel routingChannel;

    @Autowired
    @Qualifier("hospAChannel")
    private PollableChannel hospAChannel;

    @Autowired
    @Qualifier("hospBChannel")
    private PollableChannel hospBChannel;

    @Test
    void shouldRouteToCorrectHospital() {
        // Send a message destined for Hospital A
        routingChannel.send(MessageBuilder
            .withPayload("{\"destination\": \"HOSP_A\", \"patient\": {}}")
            .setHeader("destination", "HOSP_A")
            .build());

        // Verify it arrived at Hospital A's channel
        var received = hospAChannel.receive(1000);
        assertThat(received).isNotNull();
        assertThat(received.getHeaders().get("destination")).isEqualTo("HOSP_A");

        // Verify it did NOT go to Hospital B
        var wrongChannel = hospBChannel.receive(100);
        assertThat(wrongChannel).isNull();
    }
}
```

---

## Report to Miriam

> **Routing implemented:**
> - Messages routed to correct hospital based on `destination` header
> - 5 hospitals configured, unknown destinations go to a catch-all folder
> - Dynamic routing table — add/remove hospitals without redeployment
> - Filters reject malformed messages before routing (sent to discard channel for review)
> - Recipient list router for claims that need multiple destinations
>
> Dr. Patel's HIPAA concern? Resolved. Each hospital only sees their own data.

Miriam: "Good. Now the lab system sends batch files — 200 results in one file. We need to split them into individual messages and process each one separately."

---

## What You Learned

- **Routers** direct messages to different channels based on content or headers
- **Header value router** — simplest, routes on a single header
- **Payload router** — examines the payload to decide routing
- **Recipient list router** — sends copies to multiple destinations
- **Dynamic routing** — routing table can change at runtime (database, admin API)
- **Filters** discard messages that don't meet criteria — `discardChannel` catches rejects
- **`defaultSubFlowMapping`** / **`defaultOutputChannel`** — always handle the "none of the above" case
- Route decisions should be based on **headers** when possible (cheaper than parsing the payload)
- The `default` case is not optional — unroutable messages must go somewhere, not vanish

---

[Next: Chapter 4 — "Split a Batch File" →](chapter-04-splitters.md)
