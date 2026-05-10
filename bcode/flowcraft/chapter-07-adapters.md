# Chapter 7: Built-in Adapters

[← Chapter 6: Dynamic Registration](chapter-06-dynamic-registration.md) | [Chapter 8: Flow CRUD API →](chapter-08-flow-crud.md)

---

## Goal

Build out the full adapter library — every node type the user can drag onto the canvas gets a corresponding backend adapter. By the end: HTTP, Timer, File, Transform, Filter, Script, LLM, Database, and Logger all work.

## The Adapter Registry

Spring auto-discovers all `@Component` classes implementing `NodeAdapter`. The compiler looks them up by type:

```kotlin
// In FlowCompiler (already built):
private val adapterMap: Map<String, NodeAdapter> = adapters.associateBy { it.type }
```

Adding a new node type = adding one Kotlin file. No other changes needed.

## Input Adapters

### HTTP Inbound

Already handled in the compiler (Chapter 5) since it's the flow entry point. But here's the standalone adapter for reference:

**src/main/kotlin/com/flowcraft/compiler/adapters/HttpInboundAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlow
import org.springframework.integration.dsl.integrationFlow
import org.springframework.integration.http.dsl.Http
import org.springframework.stereotype.Component
import org.springframework.web.bind.annotation.RequestMethod

/**
 * HTTP Inbound is special — it's always the flow entry point.
 * This adapter is used by the compiler to build the inbound gateway.
 */
@Component
class HttpInboundAdapter {
    val type = "http-inbound"

    fun buildInbound(node: NodeDefinition): Any {
        val path = node.config["path"] as? String ?: "/webhook"
        val method = node.config["method"] as? String ?: "POST"

        return Http.inboundGateway(path)
            .requestMapping { it.methods(RequestMethod.valueOf(method)) }
            .requestPayloadType(String::class.java)
    }
}
```

### Timer Adapter

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.model.NodeDefinition
import org.springframework.messaging.support.GenericMessage
import org.springframework.stereotype.Component

@Component
class TimerInboundAdapter {
    val type = "timer"

    data class TimerConfig(
        val fixedDelay: Long = 5000,
        val cron: String? = null,
    )

    fun parseConfig(node: NodeDefinition): TimerConfig {
        return TimerConfig(
            fixedDelay = (node.config["fixedDelay"] as? Number)?.toLong() ?: 5000,
            cron = node.config["cron"] as? String,
        )
    }
}
```

### File Inbound Adapter

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.file.dsl.Files
import org.springframework.stereotype.Component
import java.io.File

@Component
class FileInboundAdapter {
    val type = "file-inbound"

    fun buildInbound(node: NodeDefinition): Any {
        val directory = node.config["directory"] as? String ?: "/tmp/input"
        val pattern = node.config["pattern"] as? String ?: "*.*"

        return Files.inboundAdapter(File(directory))
            .patternFilter(pattern)
            .preventDuplicates(true)
    }
}
```

## Processing Adapters

### Transform (already built in Ch 5)

Supports SpEL expressions evaluated against the message payload.

### Filter (already built in Ch 5)

Passes or discards messages based on a SpEL boolean expression.

### Script Adapter

Run arbitrary Groovy or JavaScript:

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.groovy.GroovyScriptExecutingMessageProcessor
import org.springframework.integration.handler.MessageProcessor
import org.springframework.scripting.support.StaticScriptSource
import org.springframework.stereotype.Component

@Component
class ScriptAdapter : NodeAdapter {
    override val type = "script"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val language = node.config["language"] as? String ?: "groovy"
        val code = node.config["code"] as? String
            ?: throw IllegalArgumentException("Script node ${node.id} missing 'code'")

        when (language) {
            "groovy" -> {
                val scriptSource = StaticScriptSource(code)
                val processor = GroovyScriptExecutingMessageProcessor(scriptSource)
                flow.handle { message, _ ->
                    processor.processMessage(message)
                }
            }
            else -> throw IllegalArgumentException("Unsupported script language: $language")
        }
    }
}
```

### Enricher Adapter

Add headers or enrich the payload with external data:

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.stereotype.Component

@Component
class EnrichAdapter : NodeAdapter {
    override val type = "enrich"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val headers = node.config["headers"] as? Map<*, *> ?: emptyMap<String, Any>()

        flow.enrich { enricher ->
            headers.forEach { (key, value) ->
                enricher.header(key.toString(), value)
            }
        }
    }
}
```

### Splitter Adapter

Split a collection into individual messages:

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.stereotype.Component

@Component
class SplitterAdapter : NodeAdapter {
    override val type = "splitter"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val expression = node.config["expression"] as? String

        if (expression != null) {
            // Split using SpEL (e.g., "payload.split(',')")
            flow.split<Any> { payload ->
                val parser = org.springframework.expression.spel.standard.SpelExpressionParser()
                val context = org.springframework.expression.spel.support.StandardEvaluationContext(payload)
                parser.parseExpression(expression).getValue(context) as Collection<*>
            }
        } else {
            // Default: assume payload is already iterable
            flow.split()
        }
    }
}
```

### LLM Call Adapter

The AI node — calls an LLM API:

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.stereotype.Component
import org.springframework.web.client.RestTemplate
import org.springframework.http.*

@Component
class LlmCallAdapter(
    private val restTemplate: RestTemplate = RestTemplate(),
) : NodeAdapter {
    override val type = "llm-call"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val model = node.config["model"] as? String ?: "gpt-4o"
        val promptTemplate = node.config["prompt"] as? String ?: "{{payload}}"
        val temperature = (node.config["temperature"] as? Number)?.toDouble() ?: 0.7
        val apiKey = System.getenv("OPENAI_API_KEY") ?: ""

        flow.handle { message, _ ->
            val payload = message.payload.toString()
            val prompt = promptTemplate.replace("{{payload}}", payload)

            // Call OpenAI-compatible API
            val requestBody = mapOf(
                "model" to model,
                "messages" to listOf(mapOf("role" to "user", "content" to prompt)),
                "temperature" to temperature,
            )

            val headers = HttpHeaders().apply {
                contentType = MediaType.APPLICATION_JSON
                setBearerAuth(apiKey)
            }

            val request = HttpEntity(requestBody, headers)
            val response = restTemplate.postForObject(
                "https://api.openai.com/v1/chat/completions",
                request,
                Map::class.java
            )

            // Extract the response text
            val choices = response?.get("choices") as? List<*>
            val firstChoice = choices?.firstOrNull() as? Map<*, *>
            val messageContent = firstChoice?.get("message") as? Map<*, *>
            messageContent?.get("content")?.toString() ?: "No response"
        }
    }
}
```

> **Note:** In production, use Spring AI instead of raw REST calls. This is simplified for clarity.

## Output Adapters

### HTTP Outbound (already built in Ch 5)

### JDBC Outbound (already built in Ch 5)

### Email Adapter

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.stereotype.Component

@Component
class EmailAdapter : NodeAdapter {
    override val type = "email-outbound"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val to = node.config["to"] as? String
            ?: throw IllegalArgumentException("Email node ${node.id} missing 'to'")
        val subject = node.config["subject"] as? String ?: "FlowCraft Notification"

        flow.handle { message, _ ->
            // In production: use Spring Integration Mail adapter
            // Mail.outboundAdapter("smtp.gmail.com")
            println("[EMAIL] To: $to, Subject: $subject, Body: ${message.payload}")
            message.payload
        }
    }
}
```

### File Outbound Adapter

```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.file.dsl.Files
import org.springframework.stereotype.Component
import java.io.File

@Component
class FileOutboundAdapter : NodeAdapter {
    override val type = "file-outbound"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val directory = node.config["directory"] as? String ?: "/tmp/output"
        val filename = node.config["filename"] as? String // null = auto-generate

        flow.handle(
            Files.outboundAdapter(File(directory))
                .autoCreateDirectory(true)
                .let { adapter ->
                    if (filename != null) {
                        adapter.fileNameGenerator { filename }
                    } else {
                        adapter
                    }
                }
        )
    }
}
```

## The Complete Adapter Map

| Node Type | Adapter Class | Spring Integration Component |
|---|---|---|
| `http-inbound` | HttpInboundAdapter | `Http.inboundGateway()` |
| `timer` | TimerInboundAdapter | `MessageSources.from()` + poller |
| `file-inbound` | FileInboundAdapter | `Files.inboundAdapter()` |
| `transform` | TransformAdapter | `.transform<T> { }` |
| `filter` | FilterAdapter | `.filter<T> { }` |
| `script` | ScriptAdapter | GroovyScriptExecutingMessageProcessor |
| `splitter` | SplitterAdapter | `.split()` |
| `enrich` | EnrichAdapter | `.enrich { }` |
| `llm-call` | LlmCallAdapter | Custom handler (REST to OpenAI) |
| `http-outbound` | HttpOutboundAdapter | `Http.outboundGateway()` |
| `jdbc-outbound` | JdbcOutboundAdapter | `JdbcMessageHandler` |
| `email-outbound` | EmailAdapter | `Mail.outboundAdapter()` |
| `file-outbound` | FileOutboundAdapter | `Files.outboundAdapter()` |
| `log` | LogAdapter | `.log()` |

## Adding a New Node Type (Recipe)

To add a new block to the product:

**1. Frontend** — Add to `NODE_CATALOG` in `types/flow.ts`:
```ts
{ type: 'kafka-outbound', label: 'Kafka Publish', category: 'output', ... }
```

**2. Frontend** — Add config fields in `types/configFields.ts`:
```ts
'kafka-outbound': [
  { key: 'topic', label: 'Topic', type: 'text', required: true },
  { key: 'bootstrapServers', label: 'Servers', type: 'text' },
]
```

**3. Frontend** — Register in `nodeTypes.ts`:
```ts
'kafka-outbound': OutputNode,
```

**4. Backend** — Create adapter:
```kotlin
@Component
class KafkaOutboundAdapter : NodeAdapter {
    override val type = "kafka-outbound"
    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val topic = node.config["topic"] as String
        flow.handle(Kafka.outboundChannelAdapter(kafkaTemplate).topic(topic))
    }
}
```

That's it. Four touches, and the new block works end-to-end.

## Key Takeaways

1. **One adapter per node type** — clean separation, easy to test individually
2. **Spring auto-discovery** — `@Component` + interface = automatic registration
3. **SpEL** is the user-facing expression language — powerful but sandboxable
4. **The LLM adapter** shows how any HTTP API becomes a processing block
5. **Adding nodes is O(1) effort** — the architecture scales to dozens of node types

---

[← Chapter 6: Dynamic Registration](chapter-06-dynamic-registration.md) | [Chapter 8: Flow CRUD API →](chapter-08-flow-crud.md)
