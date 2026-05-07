# Chapter 2: Transform HL7 to JSON

[← Chapter 1: Messages and Channels](chapter-01-messages-channels.md) | [Chapter 3: Route Labs to the Right Hospital →](chapter-03-routers.md)

---

## The Task

Miriam's morning standup:

> "The lab system sends results in HL7 v2 format — pipe-delimited, segment-based, designed in 1987. The hospitals want JSON. The ESB has a 'transformation map' that nobody can edit because the GUI crashes when you open it. Rebuild it."

Here's what an HL7 lab result looks like:

```
MSH|^~\&|LAB_SYS|MEDIBRIDGE|HOSP_A|CARDIOLOGY|20240315120000||ORU^R01|MSG001|P|2.5
PID|||P-12345||DOE^JOHN||19800115|M
OBR|1||LAB-001|GLU^Glucose^LOCAL|||20240315080000
OBX|1|NM|GLU^Glucose^LOCAL||95|mg/dL|70-100|N|||F
OBX|2|NM|HBA1C^HbA1c^LOCAL||5.4|%|4.0-5.6|N|||F
```

And what the hospital wants:

```json
{
  "messageId": "MSG001",
  "patient": {
    "id": "P-12345",
    "lastName": "DOE",
    "firstName": "JOHN",
    "dateOfBirth": "1980-01-15",
    "gender": "M"
  },
  "results": [
    { "code": "GLU", "name": "Glucose", "value": 95, "unit": "mg/dL", "range": "70-100", "flag": "N" },
    { "code": "HBA1C", "name": "HbA1c", "value": 5.4, "unit": "%", "range": "4.0-5.6", "flag": "N" }
  ],
  "orderDate": "2024-03-15T08:00:00",
  "destination": "HOSP_A",
  "department": "CARDIOLOGY"
}
```

---

## Transformers: Changing the Payload

A **transformer** takes a message in, changes the payload (and optionally headers), and sends a new message out. The original message is never modified — transformers create new messages.

```java
// src/main/java/com/medibridge/flows/LabTransformFlow.java
package com.medibridge.flows;

import com.medibridge.transformers.Hl7ToJsonTransformer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.Pollers;
import org.springframework.integration.file.dsl.Files;

import java.io.File;

@Configuration
public class LabTransformFlow {

    @Bean
    public IntegrationFlow labTransformationFlow(Hl7ToJsonTransformer transformer) {
        return IntegrationFlow
            .from(Files.inboundAdapter(new File("input/labs"))
                    .autoCreateDirectory(true)
                    .patternFilter("*.hl7"),
                e -> e.poller(Pollers.fixedDelay(1000)))
            .transform(Files.toStringTransformer())       // File → String
            .transform(transformer, "transform")           // HL7 String → JSON String
            .handle(Files.outboundAdapter(new File("output/labs-json"))
                    .autoCreateDirectory(true)
                    .fileNameGenerator(msg ->
                        msg.getHeaders().get("messageId") + ".json"))
            .get();
    }
}
```

The flow:
```
  input/labs/*.hl7 → [File→String] → [HL7→JSON] → output/labs-json/{messageId}.json
```

---

## The Transformer Implementation

```java
// src/main/java/com/medibridge/transformers/Hl7ToJsonTransformer.java
package com.medibridge.transformers;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.integration.annotation.Transformer;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.stereotype.Component;

@Component
public class Hl7ToJsonTransformer {

    private final ObjectMapper mapper = new ObjectMapper();

    @Transformer
    public String transform(String hl7Message) {
        String[] segments = hl7Message.split("\r|\n");
        ObjectNode json = mapper.createObjectNode();

        for (String segment : segments) {
            String[] fields = segment.split("\\|");
            String segmentType = fields[0];

            switch (segmentType) {
                case "MSH" -> parseMsh(fields, json);
                case "PID" -> parsePid(fields, json);
                case "OBR" -> parseObr(fields, json);
                case "OBX" -> parseObx(fields, json);
            }
        }

        return json.toPrettyString();
    }

    private void parseMsh(String[] fields, ObjectNode json) {
        // MSH|^~\&|LAB_SYS|MEDIBRIDGE|HOSP_A|CARDIOLOGY|20240315120000||ORU^R01|MSG001|P|2.5
        json.put("messageId", fields.length > 9 ? fields[9] : "UNKNOWN");
        json.put("destination", fields.length > 4 ? fields[4] : "UNKNOWN");
        json.put("department", fields.length > 5 ? fields[5] : "UNKNOWN");
    }

    private void parsePid(String[] fields, ObjectNode json) {
        // PID|||P-12345||DOE^JOHN||19800115|M
        ObjectNode patient = mapper.createObjectNode();
        patient.put("id", fields.length > 3 ? fields[3] : "");

        if (fields.length > 5) {
            String[] name = fields[5].split("\\^");
            patient.put("lastName", name.length > 0 ? name[0] : "");
            patient.put("firstName", name.length > 1 ? name[1] : "");
        }

        if (fields.length > 7) {
            String dob = fields[7]; // YYYYMMDD
            if (dob.length() == 8) {
                patient.put("dateOfBirth",
                    dob.substring(0, 4) + "-" + dob.substring(4, 6) + "-" + dob.substring(6, 8));
            }
        }

        patient.put("gender", fields.length > 8 ? fields[8] : "");
        json.set("patient", patient);
    }

    private void parseObr(String[] fields, ObjectNode json) {
        // OBR|1||LAB-001|GLU^Glucose^LOCAL|||20240315080000
        if (fields.length > 7) {
            String dt = fields[7]; // YYYYMMDDHHMMSS
            if (dt.length() >= 12) {
                json.put("orderDate",
                    dt.substring(0, 4) + "-" + dt.substring(4, 6) + "-" + dt.substring(6, 8) +
                    "T" + dt.substring(8, 10) + ":" + dt.substring(10, 12) + ":00");
            }
        }
    }

    private void parseObx(String[] fields, ObjectNode json) {
        // OBX|1|NM|GLU^Glucose^LOCAL||95|mg/dL|70-100|N|||F
        if (!json.has("results")) {
            json.set("results", mapper.createArrayNode());
        }
        ArrayNode results = (ArrayNode) json.get("results");

        ObjectNode result = mapper.createObjectNode();
        if (fields.length > 3) {
            String[] code = fields[3].split("\\^");
            result.put("code", code.length > 0 ? code[0] : "");
            result.put("name", code.length > 1 ? code[1] : "");
        }
        if (fields.length > 5) {
            try {
                result.put("value", Double.parseDouble(fields[5]));
            } catch (NumberFormatException e) {
                result.put("value", fields[5]);
            }
        }
        result.put("unit", fields.length > 6 ? fields[6] : "");
        result.put("range", fields.length > 7 ? fields[7] : "");
        result.put("flag", fields.length > 8 ? fields[8] : "");

        results.add(result);
    }
}
```

---

## Enriching Headers

Transformers change payloads. But sometimes you need to add metadata without touching the payload. That's **header enrichment**:

```java
@Bean
public IntegrationFlow labFlowWithHeaders(Hl7ToJsonTransformer transformer) {
    return IntegrationFlow
        .from(Files.inboundAdapter(new File("input/labs"))
                .autoCreateDirectory(true)
                .patternFilter("*.hl7"),
            e -> e.poller(Pollers.fixedDelay(1000)))
        .transform(Files.toStringTransformer())
        // Enrich headers BEFORE transformation (extract routing info from HL7)
        .enrichHeaders(h -> h
            .headerExpression("destination",
                "payload.split('\\|').length > 4 ? payload.split('\\|')[4] : 'UNKNOWN'")
            .header("contentType", "application/json")
            .header("source", "LAB_SYSTEM"))
        .transform(transformer, "transform")
        .handle(Files.outboundAdapter(new File("output/labs-json"))
                .autoCreateDirectory(true))
        .get();
}
```

Headers travel with the message through the entire flow. Routers (Chapter 3) will use them to decide where messages go.

---

## Multiple Transformers in a Chain

Real flows often need multiple transformation steps:

```java
@Bean
public IntegrationFlow multiStepTransform() {
    return IntegrationFlow.from("rawLabChannel")
        .transform(Files.toStringTransformer())          // Step 1: File → String
        .transform(String.class, this::stripBom)         // Step 2: Remove BOM characters
        .transform(String.class, this::normalizeLineEndings)  // Step 3: \r\n → \n
        .transform(transformer, "transform")              // Step 4: HL7 → JSON
        .transform(String.class, this::prettyPrint)       // Step 5: Compact → Pretty JSON
        .channel("processedLabChannel")
        .get();
}

private String stripBom(String input) {
    return input.startsWith("\uFEFF") ? input.substring(1) : input;
}

private String normalizeLineEndings(String input) {
    return input.replace("\r\n", "\n").replace("\r", "\n");
}

private String prettyPrint(String json) {
    // re-parse and pretty-print
    try {
        Object parsed = new ObjectMapper().readValue(json, Object.class);
        return new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(parsed);
    } catch (Exception e) {
        return json; // If it fails, return as-is
    }
}
```

Each `.transform()` creates a new message with the transformed payload. Headers pass through unchanged (unless you explicitly modify them).

---

## Testing the Transformer

```java
// src/test/java/com/medibridge/transformers/Hl7ToJsonTransformerTest.java
package com.medibridge.transformers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class Hl7ToJsonTransformerTest {

    private final Hl7ToJsonTransformer transformer = new Hl7ToJsonTransformer();
    private final ObjectMapper mapper = new ObjectMapper();

    @Test
    void shouldTransformHl7ToJson() throws Exception {
        String hl7 = String.join("\n",
            "MSH|^~\\&|LAB_SYS|MEDIBRIDGE|HOSP_A|CARDIOLOGY|20240315120000||ORU^R01|MSG001|P|2.5",
            "PID|||P-12345||DOE^JOHN||19800115|M",
            "OBR|1||LAB-001|GLU^Glucose^LOCAL|||20240315080000",
            "OBX|1|NM|GLU^Glucose^LOCAL||95|mg/dL|70-100|N|||F"
        );

        String json = transformer.transform(hl7);
        JsonNode node = mapper.readTree(json);

        assertThat(node.get("messageId").asText()).isEqualTo("MSG001");
        assertThat(node.get("destination").asText()).isEqualTo("HOSP_A");
        assertThat(node.get("patient").get("id").asText()).isEqualTo("P-12345");
        assertThat(node.get("patient").get("lastName").asText()).isEqualTo("DOE");
        assertThat(node.get("results")).hasSize(1);
        assertThat(node.get("results").get(0).get("code").asText()).isEqualTo("GLU");
        assertThat(node.get("results").get(0).get("value").asDouble()).isEqualTo(95.0);
    }

    @Test
    void shouldHandleMissingFields() throws Exception {
        String hl7 = "MSH|^~\\&|LAB_SYS|MEDIBRIDGE\nPID|||P-99999";

        String json = transformer.transform(hl7);
        JsonNode node = mapper.readTree(json);

        assertThat(node.get("messageId").asText()).isEqualTo("UNKNOWN");
        assertThat(node.get("patient").get("id").asText()).isEqualTo("P-99999");
    }
}
```

```bash
./gradlew test
```

Test the transformer in isolation. Test the flow end-to-end. Both matter.

---

## Report to Miriam

> **HL7 → JSON transformation migrated:**
> - `Hl7ToJsonTransformer` parses MSH, PID, OBR, OBX segments
> - Headers enriched with destination, content type, source system
> - Multi-step chain: File → String → normalize → transform → output
> - Unit tests for transformer logic, integration test for the full flow
>
> The ESB's "transformation map" that crashed the GUI? 80 lines of testable Java.

Miriam: "Nice. But we have 5 hospitals. Lab results need to go to the right one based on the destination in the message. Right now everything goes to one folder."

---

## What You Learned

- **Transformers** change the message payload — they don't modify the original message, they create a new one
- **`@Transformer`** annotation marks a method as a transformer component
- **`.transform()`** in the DSL adds a transformation step to the flow
- **Header enrichment** adds metadata without touching the payload — useful for routing decisions later
- **Chaining transformers** handles multi-step conversions (File → String → normalize → parse → format)
- **Messages are immutable** — each transformation creates a new `Message` object
- Test transformers in isolation (unit test) AND in the flow (integration test)
- The DSL reads like a pipeline: `from → transform → transform → handle`

---

[Next: Chapter 3 — "Route Labs to the Right Hospital" →](chapter-03-routers.md)
