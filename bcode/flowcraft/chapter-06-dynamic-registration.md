# Chapter 6: Dynamic Flow Registration

[← Chapter 5: Flow Compiler](chapter-05-flow-compiler.md) | [Chapter 7: Built-in Adapters →](chapter-07-adapters.md)

---

## Goal

Register and unregister compiled flows at runtime without restarting the application. By the end: you can deploy a flow via API call and it immediately starts processing messages. Undeploy it, and it stops.

## The Magic: IntegrationFlowContext

Spring Integration provides `IntegrationFlowContext` — a runtime registry for flows. It lets you:
- Register a new flow (starts immediately)
- Remove a flow (stops and cleans up)
- Check if a flow is running

```kotlin
@Autowired
lateinit var flowContext: IntegrationFlowContext

// Register
val registration = flowContext.registration(compiledFlow)
    .id("flow-123")
    .register()

// Remove
flowContext.remove("flow-123")
```

## Step 1: Flow Runtime Service

**src/main/kotlin/com/flowcraft/runtime/FlowRuntime.kt:**
```kotlin
package com.flowcraft.runtime

import com.flowcraft.compiler.FlowCompiler
import com.flowcraft.model.FlowDefinition
import org.slf4j.LoggerFactory
import org.springframework.integration.dsl.context.IntegrationFlowContext
import org.springframework.stereotype.Service
import java.util.concurrent.ConcurrentHashMap

data class FlowStatus(
    val id: String,
    val name: String,
    val status: FlowState,
    val deployedAt: java.time.Instant? = null,
    val error: String? = null,
)

enum class FlowState {
    STOPPED, RUNNING, ERROR
}

@Service
class FlowRuntime(
    private val flowCompiler: FlowCompiler,
    private val flowContext: IntegrationFlowContext,
) {
    private val log = LoggerFactory.getLogger(FlowRuntime::class.java)
    private val deployedFlows = ConcurrentHashMap<String, FlowStatus>()

    /**
     * Deploy a flow definition. Compiles and registers it.
     * If already deployed, undeploys first (hot-reload).
     */
    fun deploy(definition: FlowDefinition): FlowStatus {
        val flowId = definition.id

        // Undeploy if already running (hot-reload)
        if (deployedFlows.containsKey(flowId)) {
            undeploy(flowId)
        }

        return try {
            // Compile JSON → IntegrationFlow
            val integrationFlow = flowCompiler.compile(definition)

            // Register with Spring Integration runtime
            flowContext.registration(integrationFlow)
                .id(flowId)
                .register()

            val status = FlowStatus(
                id = flowId,
                name = definition.name,
                status = FlowState.RUNNING,
                deployedAt = java.time.Instant.now(),
            )
            deployedFlows[flowId] = status

            log.info("✅ Flow deployed: {} ({})", definition.name, flowId)
            status
        } catch (e: Exception) {
            val status = FlowStatus(
                id = flowId,
                name = definition.name,
                status = FlowState.ERROR,
                error = e.message,
            )
            deployedFlows[flowId] = status

            log.error("❌ Flow deployment failed: {} - {}", definition.name, e.message)
            status
        }
    }

    /**
     * Undeploy (stop and remove) a running flow.
     */
    fun undeploy(flowId: String): Boolean {
        return try {
            flowContext.remove(flowId)
            deployedFlows.remove(flowId)
            log.info("🛑 Flow undeployed: {}", flowId)
            true
        } catch (e: Exception) {
            log.warn("Failed to undeploy flow {}: {}", flowId, e.message)
            false
        }
    }

    /**
     * Get status of all deployed flows.
     */
    fun listDeployed(): List<FlowStatus> {
        return deployedFlows.values.toList()
    }

    /**
     * Get status of a specific flow.
     */
    fun getStatus(flowId: String): FlowStatus? {
        return deployedFlows[flowId]
    }

    /**
     * Check if a flow is currently running.
     */
    fun isRunning(flowId: String): Boolean {
        return deployedFlows[flowId]?.status == FlowState.RUNNING
    }
}
```

## Step 2: REST API Controller

**src/main/kotlin/com/flowcraft/api/FlowController.kt:**
```kotlin
package com.flowcraft.api

import com.flowcraft.model.FlowDefinition
import com.flowcraft.runtime.FlowRuntime
import com.flowcraft.runtime.FlowStatus
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/flows")
@CrossOrigin(origins = ["http://localhost:5173"]) // Vite dev server
class FlowController(
    private val flowRuntime: FlowRuntime,
) {

    /**
     * Deploy a new flow or update an existing one.
     */
    @PostMapping("/deploy")
    fun deploy(@RequestBody definition: FlowDefinition): ResponseEntity<FlowStatus> {
        val status = flowRuntime.deploy(definition)
        val httpStatus = if (status.status == com.flowcraft.runtime.FlowState.ERROR)
            HttpStatus.BAD_REQUEST else HttpStatus.OK
        return ResponseEntity.status(httpStatus).body(status)
    }

    /**
     * Undeploy (stop) a running flow.
     */
    @DeleteMapping("/{flowId}")
    fun undeploy(@PathVariable flowId: String): ResponseEntity<Map<String, Any>> {
        val success = flowRuntime.undeploy(flowId)
        return if (success) {
            ResponseEntity.ok(mapOf("success" to true, "flowId" to flowId))
        } else {
            ResponseEntity.notFound().build()
        }
    }

    /**
     * List all deployed flows and their status.
     */
    @GetMapping
    fun list(): List<FlowStatus> {
        return flowRuntime.listDeployed()
    }

    /**
     * Get status of a specific flow.
     */
    @GetMapping("/{flowId}/status")
    fun status(@PathVariable flowId: String): ResponseEntity<FlowStatus> {
        val status = flowRuntime.getStatus(flowId)
        return if (status != null) {
            ResponseEntity.ok(status)
        } else {
            ResponseEntity.notFound().build()
        }
    }
}
```

## Step 3: Test the Full Pipeline

```bash
# 1. Deploy a flow via API
curl -X POST http://localhost:8080/api/flows/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "id": "flow-001",
    "name": "Echo Webhook",
    "nodes": [
      {
        "id": "n1",
        "type": "http-inbound",
        "category": "input",
        "position": {"x": 0, "y": 0},
        "config": {"path": "/echo", "method": "POST"}
      },
      {
        "id": "n2",
        "type": "transform",
        "category": "processing",
        "position": {"x": 200, "y": 0},
        "config": {"expression": "payload.toUpperCase()"}
      },
      {
        "id": "n3",
        "type": "log",
        "category": "output",
        "position": {"x": 400, "y": 0},
        "config": {"level": "INFO"}
      }
    ],
    "edges": [
      {"id": "e1", "source": "n1", "target": "n2"},
      {"id": "e2", "source": "n2", "target": "n3"}
    ]
  }'

# Response: {"id":"flow-001","name":"Echo Webhook","status":"RUNNING","deployedAt":"..."}

# 2. The flow is now LIVE! Test it:
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: text/plain" \
  -d "hello world"

# Response: HELLO WORLD

# 3. Check status
curl http://localhost:8080/api/flows

# 4. Undeploy
curl -X DELETE http://localhost:8080/api/flows/flow-001

# 5. Now /echo returns 404
curl -X POST http://localhost:8080/echo -d "test"
# 404 Not Found
```

## Step 4: Connect the UI Deploy Button

Update the frontend to call the API:

**src/api/client.ts:**
```ts
const API_BASE = '/api/flows';

export interface FlowStatus {
  id: string;
  name: string;
  status: 'STOPPED' | 'RUNNING' | 'ERROR';
  deployedAt?: string;
  error?: string;
}

export async function deployFlow(flowJson: any): Promise<FlowStatus> {
  const response = await fetch(`${API_BASE}/deploy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id: flowJson.id || `flow-${Date.now()}`,
      name: flowJson.name || 'Untitled Flow',
      ...flowJson,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Deployment failed');
  }

  return response.json();
}

export async function undeployFlow(flowId: string): Promise<void> {
  await fetch(`${API_BASE}/${flowId}`, { method: 'DELETE' });
}

export async function listFlows(): Promise<FlowStatus[]> {
  const response = await fetch(API_BASE);
  return response.json();
}
```

Update the Toolbar:
```tsx
import { deployFlow } from '../api/client';

const handleDeploy = async () => {
  const flow = getFlowJson();
  try {
    const status = await deployFlow(flow);
    if (status.status === 'RUNNING') {
      alert(`✅ Flow deployed! Status: ${status.status}`);
    } else {
      alert(`❌ Deployment failed: ${status.error}`);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
};
```

## The Lifecycle

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  DESIGN │────→│  DEPLOY │────→│ RUNNING │────→│ STOPPED │
│  (UI)   │     │  (API)  │     │ (Live)  │     │(Removed)│
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                     │                │
                     │                │ Hot-reload
                     │                │ (redeploy)
                     └────────────────┘
```

## Important: Thread Safety

`IntegrationFlowContext` is thread-safe, but you need to be careful:
- Don't deploy the same flow ID concurrently (use a lock or check-then-act)
- Undeploying while messages are in-flight will drop those messages
- Consider adding a "draining" state for graceful shutdown

```kotlin
// Simple lock per flow
private val deployLocks = ConcurrentHashMap<String, Any>()

fun deploy(definition: FlowDefinition): FlowStatus {
    val lock = deployLocks.computeIfAbsent(definition.id) { Any() }
    synchronized(lock) {
        // ... deploy logic
    }
}
```

## What You Have Now

The complete deploy pipeline works:

1. ✅ User builds flow in React Flow UI
2. ✅ Clicks "Deploy" → JSON sent to backend
3. ✅ Backend compiles JSON → IntegrationFlow
4. ✅ Flow registered at runtime → immediately live
5. ✅ User can undeploy → flow stops
6. ✅ User can redeploy → hot-reload

## Key Takeaways

1. **`IntegrationFlowContext`** is the runtime registry — register/remove flows without restart
2. **Flow IDs** must be unique — they're the key for lifecycle management
3. **Hot-reload** = undeploy old + deploy new (same ID)
4. **The REST API** is the contract between UI and engine
5. **ConcurrentHashMap** tracks deployed flow status in memory (persist to DB for production)

---

[← Chapter 5: Flow Compiler](chapter-05-flow-compiler.md) | [Chapter 7: Built-in Adapters →](chapter-07-adapters.md)
