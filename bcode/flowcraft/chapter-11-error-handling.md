# Chapter 11: Error Handling & Retry

[← Chapter 10: Monitoring](chapter-10-monitoring.md) | [Chapter 12: LLM Node →](chapter-12-llm-node.md)

---

## Goal

Handle failures gracefully — retry transient errors, route failed messages to a dead-letter queue, and show errors in the UI. By the end: flows are resilient, and users can see and replay failed messages.

## Spring Integration Error Handling

Spring Integration has a built-in error handling mechanism:

```
Normal flow:  Input → Process → Output
                        │ (exception thrown)
                        ▼
Error channel:  errorChannel → Error Handler
```

Every flow gets a default `errorChannel`. When any component throws, the exception (wrapped in `ErrorMessage`) is sent there.

## Step 1: Per-Flow Error Channel

Each deployed flow gets its own error channel for isolation:

**src/main/kotlin/com/flowcraft/runtime/FlowErrorHandler.kt:**
```kotlin
package com.flowcraft.runtime

import com.flowcraft.monitoring.FlowEvent
import com.flowcraft.monitoring.EventType
import org.slf4j.LoggerFactory
import org.springframework.integration.dsl.IntegrationFlow
import org.springframework.integration.dsl.integrationFlow
import org.springframework.messaging.MessagingException
import org.springframework.messaging.simp.SimpMessagingTemplate
import org.springframework.stereotype.Component
import java.time.Instant
import java.util.concurrent.ConcurrentLinkedQueue

data class FailedMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val flowId: String,
    val nodeId: String?,
    val payload: Any?,
    val error: String,
    val timestamp: Instant = Instant.now(),
    val retryCount: Int = 0,
)

@Component
class FlowErrorHandler(
    private val messagingTemplate: SimpMessagingTemplate,
) {
    private val log = LoggerFactory.getLogger(FlowErrorHandler::class.java)

    // Dead letter queue (in-memory for now, use DB in production)
    private val deadLetterQueue = ConcurrentLinkedQueue<FailedMessage>()

    /**
     * Build an error handling flow for a specific flow ID.
     */
    fun buildErrorFlow(flowId: String): IntegrationFlow {
        return integrationFlow("${flowId}.errorChannel") {
            handle { message, _ ->
                val exception = message.payload as? MessagingException
                val originalPayload = exception?.failedMessage?.payload
                val nodeId = exception?.failedMessage?.headers?.get("flowcraft.nodeId") as? String

                val failed = FailedMessage(
                    flowId = flowId,
                    nodeId = nodeId,
                    payload = originalPayload,
                    error = exception?.cause?.message ?: exception?.message ?: "Unknown error",
                )

                // Store in DLQ
                deadLetterQueue.add(failed)

                // Notify UI via WebSocket
                val event = FlowEvent(
                    flowId = flowId,
                    nodeId = nodeId ?: "unknown",
                    type = EventType.ERROR,
                    error = failed.error,
                    payload = originalPayload?.toString()?.take(200),
                )
                messagingTemplate.convertAndSend("/topic/flow/$flowId", event)

                log.error("[Flow: {}] Error at node {}: {}", flowId, nodeId, failed.error)
                null
            }
        }
    }

    fun getDeadLetters(flowId: String? = null): List<FailedMessage> {
        return if (flowId != null) {
            deadLetterQueue.filter { it.flowId == flowId }
        } else {
            deadLetterQueue.toList()
        }
    }

    fun clearDeadLetters(flowId: String) {
        deadLetterQueue.removeIf { it.flowId == flowId }
    }
}
```

## Step 2: Retry with Exponential Backoff

Add retry logic to the flow compiler for specific node types:

```kotlin
// In FlowCompiler, wrap error-prone nodes with retry:
private fun applyNodeWithRetry(
    flow: IntegrationFlowDefinition<*>,
    node: NodeDefinition,
    flowId: String
) {
    val retryableTypes = setOf("http-outbound", "jdbc-outbound", "llm-call", "email-outbound")

    if (node.type in retryableTypes) {
        // Wrap in a request-handler-advice with retry
        val maxRetries = (node.config["maxRetries"] as? Number)?.toInt() ?: 3
        val backoffMs = (node.config["retryBackoffMs"] as? Number)?.toLong() ?: 1000L

        flow.handle({ message, _ ->
            // The actual adapter logic runs here with retry
            applyNodeLogic(node, message)
        }) { endpoint ->
            endpoint.advice(
                org.springframework.integration.handler.advice.RequestHandlerRetryAdvice().apply {
                    setRetryTemplate(
                        org.springframework.retry.support.RetryTemplate.builder()
                            .maxAttempts(maxRetries)
                            .exponentialBackoff(backoffMs, 2.0, backoffMs * 10)
                            .build()
                    )
                }
            )
        }
    } else {
        applyNode(flow, node)
    }
}
```

## Step 3: Circuit Breaker for External Calls

Prevent cascading failures when an external service is down:

```kotlin
import org.springframework.integration.handler.advice.RequestHandlerCircuitBreakerAdvice

// For HTTP outbound and LLM calls:
val circuitBreaker = RequestHandlerCircuitBreakerAdvice().apply {
    setThreshold(5)           // Open after 5 failures
    setHalfOpenAfter(30_000)  // Try again after 30 seconds
}

flow.handle(httpOutboundGateway) { endpoint ->
    endpoint.advice(circuitBreaker)
}
```

## Step 4: Dead Letter API

**src/main/kotlin/com/flowcraft/api/ErrorController.kt:**
```kotlin
package com.flowcraft.api

import com.flowcraft.runtime.FailedMessage
import com.flowcraft.runtime.FlowErrorHandler
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/errors")
@CrossOrigin(origins = ["http://localhost:5173"])
class ErrorController(private val errorHandler: FlowErrorHandler) {

    /** Get all dead-letter messages, optionally filtered by flow */
    @GetMapping
    fun getDeadLetters(@RequestParam flowId: String? = null): List<FailedMessage> {
        return errorHandler.getDeadLetters(flowId)
    }

    /** Clear dead letters for a flow */
    @DeleteMapping("/{flowId}")
    fun clearDeadLetters(@PathVariable flowId: String) {
        errorHandler.clearDeadLetters(flowId)
    }
}
```

## Step 5: Error UI Component

**src/components/ErrorPanel.tsx:**
```tsx
import { useEffect, useState } from 'react';

interface FailedMessage {
  id: string;
  flowId: string;
  nodeId: string | null;
  payload: any;
  error: string;
  timestamp: string;
  retryCount: number;
}

export function ErrorPanel({ flowId }: { flowId: string }) {
  const [errors, setErrors] = useState<FailedMessage[]>([]);

  useEffect(() => {
    fetch(`/api/errors?flowId=${flowId}`)
      .then(r => r.json())
      .then(setErrors);
  }, [flowId]);

  if (errors.length === 0) return null;

  return (
    <div className="border-t border-red-200 bg-red-50 p-4">
      <h4 className="text-sm font-medium text-red-700 mb-2">
        ⚠️ Failed Messages ({errors.length})
      </h4>
      <div className="space-y-2 max-h-40 overflow-y-auto">
        {errors.map(err => (
          <div key={err.id} className="bg-white border border-red-200 rounded p-2 text-xs">
            <div className="flex justify-between">
              <span className="font-medium text-red-600">{err.error}</span>
              <span className="text-gray-400">
                {new Date(err.timestamp).toLocaleTimeString()}
              </span>
            </div>
            {err.nodeId && (
              <span className="text-gray-500">at node: {err.nodeId}</span>
            )}
            {err.payload && (
              <pre className="mt-1 text-gray-600 truncate">
                {JSON.stringify(err.payload).slice(0, 100)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Step 6: Error Node (Visual)

Users can add an explicit "On Error" node to their flow for custom error handling:

```kotlin
@Component
class ErrorHandlerNodeAdapter : NodeAdapter {
    override val type = "on-error"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val action = node.config["action"] as? String ?: "log"

        // This node subscribes to the flow's error channel
        // and performs the configured action
        when (action) {
            "log" -> flow.log(LoggingHandler.Level.ERROR)
            "slack" -> {
                val webhookUrl = node.config["webhookUrl"] as? String ?: return
                flow.handle { message, _ ->
                    // POST to Slack webhook
                    val error = (message.payload as? MessagingException)?.message
                    restTemplate.postForObject(webhookUrl, mapOf("text" to "🚨 Flow error: $error"), String::class.java)
                    null
                }
            }
            "retry" -> {
                // Re-route to the beginning of the flow
                flow.channel("${node.config["retryChannel"]}")
            }
        }
    }
}
```

## Error Handling Strategy Summary

```
Message enters flow
       │
       ▼
  ┌─────────┐     Success     ┌─────────┐
  │  Node A  │───────────────→│  Node B  │───→ ...
  └─────────┘                 └─────────┘
       │
       │ Exception
       ▼
  ┌─────────────────────────────────────┐
  │  Retry Advice (3 attempts, backoff) │
  └─────────────────────────────────────┘
       │
       │ Still failing
       ▼
  ┌─────────────────────────────────────┐
  │  Circuit Breaker (if external call) │
  └─────────────────────────────────────┘
       │
       │ Circuit open or retries exhausted
       ▼
  ┌─────────────────────────────────────┐
  │  Error Channel                       │
  │  → Store in Dead Letter Queue        │
  │  → Notify UI via WebSocket           │
  │  → Execute "On Error" node if exists │
  └─────────────────────────────────────┘
```

## Key Takeaways

1. **Error channels** isolate failures per flow — one flow's errors don't affect others
2. **Retry with backoff** handles transient failures (network blips, rate limits)
3. **Circuit breaker** prevents hammering a dead service
4. **Dead letter queue** preserves failed messages for inspection and replay
5. **WebSocket notifications** show errors in the UI immediately
6. **The "On Error" node** gives users control over error handling without code

---

[← Chapter 10: Monitoring](chapter-10-monitoring.md) | [Chapter 12: LLM Node →](chapter-12-llm-node.md)
