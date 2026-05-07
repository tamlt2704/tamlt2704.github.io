# Chapter 4: Split a Batch File into Individual Records

[← Chapter 3: Route Labs to the Right Hospital](chapter-03-routers.md) | [Chapter 5: Poll the FTP Server →](chapter-05-inbound-adapters.md)

---

## The Disaster

The lab system doesn't send one result per file. It sends a **batch** — 200 results concatenated in a single file, separated by `MSH` segments. Your flow processes the entire batch as one message. Hospital A gets a 200-result JSON blob instead of 200 individual results.

Their system chokes. It expects one result per file. 200 results arrive as one. The import fails. 200 patients don't get their results.

Miriam:

> "Split the batch into individual messages. Process each one separately. But here's the catch — at the end, I need a summary: how many succeeded, how many failed, which ones. That means you need to split AND re-aggregate."

---

## Splitters: One Message Becomes Many

A **splitter** takes one message and produces multiple messages — one per item in a collection, one per line in a file, one per segment in a batch.

```java
// src/main/java/com/medibridge/flows/BatchSplitFlow.java
package com.medibridge.flows;

import com.medibridge.transformers.Hl7ToJsonTransformer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.Pollers;
import org.springframework.integration.file.dsl.Files;

import java.io.File;
import java.util.Arrays;
import java.util.List;

@Configuration
public class BatchSplitFlow {

    @Bean
    public IntegrationFlow batchLabFlow(Hl7ToJsonTransformer transformer) {
        return IntegrationFlow
            .from(Files.inboundAdapter(new File("input/batch-labs"))
                    .autoCreateDirectory(true)
                    .patternFilter("*.hl7"),
                e -> e.poller(Pollers.fixedDelay(5000)))
            .transform(Files.toStringTransformer())
            // Split the batch file into individual HL7 messages
            .split(String.class, this::splitHl7Batch)
            // Each split message is now one HL7 result
            .transform(transformer, "transform")
            .handle((payload, headers) -> {
                System.out.println("Processed: " + headers.get("correlationId")
                    + " [" + headers.get("sequenceNumber") + "/" + headers.get("sequenceSize") + "]");
                return payload;
            })
            .channel("processedLabChannel")
            .get();
    }

    private List<String> splitHl7Batch(String batchContent) {
        // Split on MSH segment boundaries
        // Each HL7 message starts with "MSH|"
        String[] messages = batchContent.split("(?=MSH\\|)");
        return Arrays.stream(messages)
            .filter(s -> !s.isBlank())
            .toList();
    }
}
```

### What Happens to Headers

When a splitter produces N messages from 1, Spring Integration automatically adds:

| Header | Value | Purpose |
|---|---|---|
| `correlationId` | Original message ID | Links split messages back to their parent |
| `sequenceNumber` | 1, 2, 3, ... N | Position in the batch |
| `sequenceSize` | N | Total number of split messages |

These headers are critical for **aggregation** — reassembling the pieces later.

---

## Aggregators: Many Messages Become One

After processing each lab result individually, Miriam wants a summary. The **aggregator** waits for all split messages to arrive, then combines them:

```java
// src/main/java/com/medibridge/flows/BatchWithAggregationFlow.java
package com.medibridge.flows;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.IntegrationMessageHeaderAccessor;
import org.springframework.integration.aggregator.DefaultAggregatingMessageGroupProcessor;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.Pollers;
import org.springframework.integration.file.dsl.Files;
import org.springframework.messaging.Message;

import java.io.File;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

@Configuration
public class BatchWithAggregationFlow {

    @Bean
    public IntegrationFlow batchWithSummaryFlow(Hl7ToJsonTransformer transformer) {
        return IntegrationFlow
            .from(Files.inboundAdapter(new File("input/batch-labs"))
                    .autoCreateDirectory(true)
                    .patternFilter("*.hl7"),
                e -> e.poller(Pollers.fixedDelay(5000)))
            .transform(Files.toStringTransformer())
            .split(String.class, this::splitHl7Batch)
            // Process each individual message
            .transform(transformer, "transform")
            // Aggregate back into a summary
            .aggregate(a -> a
                .outputProcessor(group -> {
                    List<Message<?>> messages = group.getMessages().stream().toList();
                    int total = messages.size();
                    long successful = messages.stream()
                        .filter(m -> m.getPayload() != null)
                        .count();

                    Map<String, Object> summary = Map.of(
                        "batchId", group.getGroupId(),
                        "totalMessages", total,
                        "successful", successful,
                        "failed", total - successful,
                        "processedAt", java.time.Instant.now().toString()
                    );
                    return summary;
                })
                .correlationStrategy(msg ->
                    msg.getHeaders().get(IntegrationMessageHeaderAccessor.CORRELATION_ID))
                .releaseStrategy(group ->
                    group.size() == group.getSequenceSize())
                .expireGroupsUponCompletion(true)
            )
            .handle((payload, headers) -> {
                System.out.println("Batch summary: " + payload);
                return null;
            })
            .get();
    }

    private List<String> splitHl7Batch(String batchContent) {
        String[] messages = batchContent.split("(?=MSH\\|)");
        return Arrays.stream(messages)
            .filter(s -> !s.isBlank())
            .toList();
    }
}
```

### How Aggregation Works

```
  Batch file (200 results)
       │
       ▼
  [Splitter] → 200 individual messages
       │         (each has correlationId=X, sequenceNumber=1..200, sequenceSize=200)
       ▼
  [Transform] → each message processed individually
       │
       ▼
  [Aggregator] — waits until all 200 arrive (correlationId=X, count=200)
       │
       ▼
  Summary: {total: 200, successful: 198, failed: 2}
```

The aggregator needs three strategies:

| Strategy | Question It Answers | Default |
|---|---|---|
| **Correlation** | "Which messages belong together?" | `correlationId` header |
| **Release** | "Do I have all the messages yet?" | `sequenceSize` matches group size |
| **Output Processor** | "How do I combine them?" | List of payloads |

---

## The Timeout Problem

What if message 147 out of 200 fails and never arrives at the aggregator? The aggregator waits forever. The batch never completes. No summary is produced.

```java
.aggregate(a -> a
    .correlationStrategy(msg ->
        msg.getHeaders().get(IntegrationMessageHeaderAccessor.CORRELATION_ID))
    .releaseStrategy(group ->
        group.size() == group.getSequenceSize())
    // Don't wait forever — release after 30 seconds even if incomplete
    .groupTimeout(30_000)
    .sendPartialResultOnExpiry(true)
    .expireGroupsUponCompletion(true)
)
```

`groupTimeout(30_000)` means: if the group isn't complete after 30 seconds, release what you have. `sendPartialResultOnExpiry(true)` sends the partial result to the output processor instead of discarding it.

---

## Scatter-Gather: Split, Process in Parallel, Reassemble

A more advanced pattern — send the same message to multiple processors and gather their results:

```java
@Bean
public IntegrationFlow scatterGatherFlow() {
    return IntegrationFlow.from("labValidationChannel")
        .scatterGather(
            scatterer -> scatterer
                .recipientFlow(sf -> sf
                    .handle((payload, headers) -> validateFormat(payload)))
                .recipientFlow(sf -> sf
                    .handle((payload, headers) -> validatePatientId(payload)))
                .recipientFlow(sf -> sf
                    .handle((payload, headers) -> validateResultRanges(payload))),
            gatherer -> gatherer
                .outputProcessor(group -> {
                    // Combine all validation results
                    List<String> errors = group.getMessages().stream()
                        .map(m -> (String) m.getPayload())
                        .filter(s -> s.startsWith("ERROR"))
                        .toList();
                    return errors.isEmpty() ? "VALID" : "INVALID: " + errors;
                })
        )
        .get();
}
```

Three validators run on the same message. The gatherer waits for all three, combines their results, and produces a single validation verdict.

---

## Testing Splitter + Aggregator

```java
@SpringBootTest
@SpringIntegrationTest
class BatchSplitFlowTest {

    @Autowired
    @Qualifier("processedLabChannel")
    private PollableChannel outputChannel;

    @Test
    void shouldSplitBatchIntoIndividualMessages() {
        String batch = String.join("\n",
            "MSH|^~\\&|LAB|MB|HOSP_A|CARD|20240315||ORU^R01|MSG001|P|2.5",
            "PID|||P-001||DOE^JOHN||19800115|M",
            "OBX|1|NM|GLU||95|mg/dL|70-100|N|||F",
            "MSH|^~\\&|LAB|MB|HOSP_A|CARD|20240315||ORU^R01|MSG002|P|2.5",
            "PID|||P-002||SMITH^JANE||19900220|F",
            "OBX|1|NM|GLU||110|mg/dL|70-100|H|||F"
        );

        // Send the batch
        inputChannel.send(MessageBuilder.withPayload(batch).build());

        // Should receive 2 individual messages
        var msg1 = outputChannel.receive(5000);
        var msg2 = outputChannel.receive(5000);

        assertThat(msg1).isNotNull();
        assertThat(msg2).isNotNull();
        assertThat(msg1.getHeaders().get("sequenceSize")).isEqualTo(2);
    }
}
```

---

## Report to Miriam

> **Batch splitting implemented:**
> - Batch files split on `MSH|` boundaries — 200 results become 200 messages
> - Each message processed individually (transform, route)
> - Aggregator produces batch summary: total, successful, failed
> - 30-second timeout prevents stuck batches from blocking forever
> - Correlation headers link split messages back to their parent batch
>
> Hospital A now gets 200 individual files instead of one blob. Their import works.

Miriam: "Perfect. Now here's the thing — the lab system doesn't put files in a local folder. It puts them on an FTP server. We need to poll it."

---

## What You Learned

- **Splitters** break one message into many — each item gets its own message with correlation headers
- **Aggregators** reassemble split messages — they wait for all pieces before producing output
- **Correlation strategy** — "which messages belong together?" (usually `correlationId` header)
- **Release strategy** — "do I have all the pieces?" (usually `sequenceSize` matches count)
- **Group timeout** prevents stuck aggregations — release partial results after a deadline
- **Scatter-gather** — send to multiple processors in parallel, combine results
- Split messages automatically get `correlationId`, `sequenceNumber`, `sequenceSize` headers
- Always handle the case where not all split messages arrive — timeouts are not optional

---

[Next: Chapter 5 — "Poll the FTP Server" →](chapter-05-inbound-adapters.md)
