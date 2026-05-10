# Chapter 4: Spring Integration Fundamentals

[← Chapter 3: Node Configuration](chapter-03-node-config.md) | [Chapter 5: Flow Compiler →](chapter-05-flow-compiler.md)

---

## Goal

Understand Spring Integration's core concepts and build your first hardcoded flow. By the end: a running Spring Boot app that receives an HTTP request, transforms the payload, and logs the result — all wired with Spring Integration.

## The Mental Model

Spring Integration implements **Enterprise Integration Patterns** (EIP). Think of it as a messaging system inside your app:

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Inbound │    │         │    │         │    │ Outbound│
│ Adapter │───→│ Channel │───→│ Handler │───→│ Adapter │
│ (Input) │    │ (Pipe)  │    │(Process)│    │ (Output)│
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

| EIP Concept | Spring Integration | Our "Lego Block" |
|---|---|---|
| Message Endpoint | Inbound Adapter | Input node |
| Message Channel | DirectChannel | Edge (connection) |
| Message Handler | Transformer, Filter, etc. | Processing node |
| Message Endpoint | Outbound Adapter | Output node |

**The Message** is the data flowing through:
```kotlin
interface Message<T> {
    val payload: T           // The actual data
    val headers: MessageHeaders  // Metadata (like HTTP headers)
}
```

## The Integration Flow DSL

Spring Integration has a Kotlin/Java DSL that reads almost like our visual flow:

```kotlin
@Bean
fun myFlow(): IntegrationFlow {
    return integrationFlow(Http.inboundGateway("/webhook")) {
        transform<String> { it.uppercase() }
        handle { message, _ ->
            println("Received: ${message.payload}")
            message.payload
        }
    }
}
```

This is equivalent to: `HTTP In → Transform → Log`

## Step 1: The Simplest Flow

**src/main/kotlin/com/flowcraft/FlowcraftApplication.kt:**
```kotlin
package com.flowcraft

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.integration.config.EnableIntegration
import org.springframework.integration.dsl.IntegrationFlow
import org.springframework.integration.dsl.integrationFlow
import org.springframework.integration.http.dsl.Http

@SpringBootApplication
@EnableIntegration
class FlowcraftApplication {

    @Bean
    fun helloFlow(): IntegrationFlow {
        return integrationFlow(Http.inboundGateway("/api/hello").requestMapping { it.methods(org.springframework.web.bind.annotation.RequestMethod.POST) }) {
            transform<String> { payload ->
                "Hello, ${payload.trim()}! Processed at ${java.time.Instant.now()}"
            }
        }
    }
}

fun main(args: Array<String>) {
    runApplication<FlowcraftApplication>(*args)
}
```

Test it:
```bash
curl -X POST http://localhost:8080/api/hello \
  -H "Content-Type: text/plain" \
  -d "World"

# Response: Hello, World! Processed at 2024-01-15T10:30:00Z
```

That's a complete Input → Process → Output flow in 10 lines.

## Step 2: Multi-Step Flow

```kotlin
@Bean
fun multiStepFlow(): IntegrationFlow {
    return integrationFlow(Http.inboundGateway("/api/process")
        .requestMapping { it.methods(RequestMethod.POST) }
        .requestPayloadType(String::class.java)) {

        // Step 1: Log incoming
        wireTap { channel("logChannel") }

        // Step 2: Transform
        transform<String> { payload ->
            payload.trim().uppercase()
        }

        // Step 3: Filter (only pass non-empty)
        filter<String> { it.isNotBlank() }

        // Step 4: Enrich with header
        enrich {
            header("processedAt", java.time.Instant.now().toString())
        }

        // Step 5: Final transform (wrap in JSON)
        transform<String> { payload ->
            """{"result": "$payload", "status": "ok"}"""
        }
    }
}

@Bean
fun logChannel(): org.springframework.integration.channel.DirectChannel {
    return org.springframework.integration.channel.DirectChannel()
}

@Bean
fun loggingFlow(): IntegrationFlow {
    return integrationFlow(logChannel()) {
        handle { message, _ ->
            println("[LOG] Received: ${message.payload}")
            null
        }
    }
}
```

## Step 3: Understanding Channels

Channels are the "edges" between nodes. Types:

```kotlin
// DirectChannel — synchronous, point-to-point (default)
// Like a direct function call. One consumer.
@Bean
fun directChannel() = DirectChannel()

// QueueChannel — asynchronous, buffered
// Messages queue up. Consumer polls.
@Bean
fun queueChannel() = QueueChannel(100) // capacity 100

// PublishSubscribeChannel — one-to-many
// All subscribers get every message (fan-out)
@Bean
fun pubSubChannel() = PublishSubscribeChannel()
```

For our product:
- **Direct edges** (most connections) → DirectChannel
- **Fan-out** (one output to multiple nodes) → PublishSubscribeChannel
- **Buffered** (backpressure handling) → QueueChannel

## Step 4: Error Handling

Spring Integration has a built-in error channel:

```kotlin
@Bean
fun errorHandlingFlow(): IntegrationFlow {
    return integrationFlow(Http.inboundGateway("/api/risky")
        .requestMapping { it.methods(RequestMethod.POST) }
        .requestPayloadType(String::class.java)) {

        transform<String> { payload ->
            if (payload.contains("bomb")) {
                throw RuntimeException("Dangerous payload detected!")
            }
            payload.uppercase()
        }
    }
}

// Global error handler
@Bean
fun errorFlow(): IntegrationFlow {
    return integrationFlow("errorChannel") {
        handle { message, _ ->
            val error = message.payload as org.springframework.messaging.MessagingException
            println("[ERROR] Flow failed: ${error.message}")
            println("[ERROR] Original payload: ${error.failedMessage?.payload}")
            null
        }
    }
}
```

## Step 5: Timer (Polling) Input

Not all flows start with HTTP. Here's a timer-triggered flow:

```kotlin
@Bean
fun timerFlow(): IntegrationFlow {
    return integrationFlow(
        // Poll every 5 seconds
        MessageSources.from { GenericMessage("tick-${System.currentTimeMillis()}") },
        { poller { it.fixedDelay(5000) } }
    ) {
        transform<String> { "Timer fired: $it" }
        handle { message, _ ->
            println(message.payload)
            null
        }
    }
}
```

## Step 6: File Input Adapter

Watch a directory for new files:

```kotlin
@Bean
fun fileFlow(): IntegrationFlow {
    return integrationFlow(
        Files.inboundAdapter(File("/tmp/flowcraft/input"))
            .patternFilter("*.txt"),
        { poller { it.fixedDelay(1000) } }
    ) {
        transform(Files.toStringTransformer())  // File → String
        transform<String> { "File content: ${it.take(100)}" }
        handle { message, _ ->
            println(message.payload)
            null
        }
    }
}
```

## The Key Insight: Flows Are Composable

Each `IntegrationFlow` is a bean. They can be composed:

```kotlin
// Flow A: receives HTTP, sends to a channel
@Bean
fun inputFlow(): IntegrationFlow {
    return integrationFlow(Http.inboundGateway("/api/data")) {
        channel("processingChannel")
    }
}

// Flow B: reads from channel, processes, sends to output channel
@Bean
fun processingFlow(): IntegrationFlow {
    return integrationFlow("processingChannel") {
        transform<String> { it.uppercase() }
        channel("outputChannel")
    }
}

// Flow C: reads from output channel, writes to DB
@Bean
fun outputFlow(): IntegrationFlow {
    return integrationFlow("outputChannel") {
        handle(Jdbc.outboundAdapter(dataSource)
            .sql("INSERT INTO results(data) VALUES(:payload)"))
    }
}
```

This is exactly how our compiler will work: each node becomes a fragment, connected by channels.

## Spring Integration vs Our Lego Blocks

| Our Block | Spring Integration Equivalent |
|---|---|
| HTTP Input | `Http.inboundGateway()` or `Http.inboundChannelAdapter()` |
| Timer | `MessageSources.from()` with poller |
| File Watcher | `Files.inboundAdapter()` |
| Transform | `.transform<T> { ... }` |
| Filter | `.filter<T> { ... }` |
| LLM Call | `.handle(llmServiceActivator)` |
| Script | `.handle(Scripts.processor(script))` |
| HTTP Output | `Http.outboundGateway(url)` |
| DB Write | `Jdbc.outboundAdapter(dataSource)` |
| Logger | `.log()` or `.handle(LoggingHandler())` |

## What We Learned

1. **Message** = payload + headers (the data flowing through edges)
2. **Channel** = the pipe between nodes (our edges)
3. **IntegrationFlow** = a chain of handlers (our connected nodes)
4. **Adapters** = connect to external systems (our Input/Output blocks)
5. **The DSL** reads like a pipeline — each step is a method call

## What's Next

Chapter 5: We build the **Flow Compiler** — the component that takes our JSON graph from the UI and dynamically generates Spring Integration flows at runtime. This is the core innovation of the product.

---

[← Chapter 3: Node Configuration](chapter-03-node-config.md) | [Chapter 5: Flow Compiler →](chapter-05-flow-compiler.md)
