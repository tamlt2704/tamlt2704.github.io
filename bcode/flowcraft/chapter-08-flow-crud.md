# Chapter 8: Flow CRUD & Persistence

[← Chapter 7: Adapters](chapter-07-adapters.md) | [Chapter 9: Deploy from UI →](chapter-09-deploy-ui.md)

---

## Goal

Persist flow definitions to PostgreSQL so users can save, load, edit, and manage their flows. By the end: flows survive server restarts, and the UI can list/load saved flows.

## Step 1: JPA Entity

**src/main/kotlin/com/flowcraft/model/FlowEntity.kt:**
```kotlin
package com.flowcraft.model

import jakarta.persistence.*
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.time.Instant

@Entity
@Table(name = "flows")
data class FlowEntity(
    @Id
    val id: String,

    var name: String,

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    var definition: String,  // Full JSON stored as JSONB

    @Enumerated(EnumType.STRING)
    var status: FlowState = FlowState.STOPPED,

    val createdAt: Instant = Instant.now(),
    var updatedAt: Instant = Instant.now(),
    var deployedAt: Instant? = null,
)
```

**src/main/kotlin/com/flowcraft/repository/FlowRepository.kt:**
```kotlin
package com.flowcraft.repository

import com.flowcraft.model.FlowEntity
import com.flowcraft.model.FlowState
import org.springframework.data.jpa.repository.JpaRepository

interface FlowRepository : JpaRepository<FlowEntity, String> {
    fun findByStatus(status: FlowState): List<FlowEntity>
    fun findAllByOrderByUpdatedAtDesc(): List<FlowEntity>
}
```

## Step 2: Flow Service (CRUD + Deploy)

**src/main/kotlin/com/flowcraft/service/FlowService.kt:**
```kotlin
package com.flowcraft.service

import com.fasterxml.jackson.databind.ObjectMapper
import com.flowcraft.model.*
import com.flowcraft.repository.FlowRepository
import com.flowcraft.runtime.FlowRuntime
import org.springframework.stereotype.Service
import java.time.Instant

@Service
class FlowService(
    private val flowRepository: FlowRepository,
    private val flowRuntime: FlowRuntime,
    private val objectMapper: ObjectMapper,
) {

    /**
     * Save a flow definition (create or update).
     */
    fun save(definition: FlowDefinition): FlowEntity {
        val json = objectMapper.writeValueAsString(definition)

        val entity = flowRepository.findById(definition.id).orElse(null)?.apply {
            name = definition.name
            this.definition = json
            updatedAt = Instant.now()
        } ?: FlowEntity(
            id = definition.id,
            name = definition.name,
            definition = json,
        )

        return flowRepository.save(entity)
    }

    /**
     * Get a flow by ID.
     */
    fun get(flowId: String): FlowDefinition? {
        val entity = flowRepository.findById(flowId).orElse(null) ?: return null
        return objectMapper.readValue(entity.definition, FlowDefinition::class.java)
    }

    /**
     * List all flows (summary).
     */
    fun listAll(): List<FlowSummary> {
        return flowRepository.findAllByOrderByUpdatedAtDesc().map { entity ->
            FlowSummary(
                id = entity.id,
                name = entity.name,
                status = entity.status,
                updatedAt = entity.updatedAt,
                deployedAt = entity.deployedAt,
            )
        }
    }

    /**
     * Delete a flow. Undeploys if running.
     */
    fun delete(flowId: String): Boolean {
        if (flowRuntime.isRunning(flowId)) {
            flowRuntime.undeploy(flowId)
        }
        return if (flowRepository.existsById(flowId)) {
            flowRepository.deleteById(flowId)
            true
        } else false
    }

    /**
     * Deploy a saved flow.
     */
    fun deploy(flowId: String): FlowEntity {
        val entity = flowRepository.findById(flowId)
            .orElseThrow { IllegalArgumentException("Flow not found: $flowId") }

        val definition = objectMapper.readValue(entity.definition, FlowDefinition::class.java)
        flowRuntime.deploy(definition)

        entity.status = FlowState.RUNNING
        entity.deployedAt = Instant.now()
        entity.updatedAt = Instant.now()
        return flowRepository.save(entity)
    }

    /**
     * Undeploy a running flow.
     */
    fun undeploy(flowId: String): FlowEntity {
        val entity = flowRepository.findById(flowId)
            .orElseThrow { IllegalArgumentException("Flow not found: $flowId") }

        flowRuntime.undeploy(flowId)

        entity.status = FlowState.STOPPED
        entity.updatedAt = Instant.now()
        return flowRepository.save(entity)
    }

    /**
     * On startup: redeploy all flows that were running before shutdown.
     */
    fun redeployRunningFlows() {
        val runningFlows = flowRepository.findByStatus(FlowState.RUNNING)
        runningFlows.forEach { entity ->
            try {
                val definition = objectMapper.readValue(entity.definition, FlowDefinition::class.java)
                flowRuntime.deploy(definition)
            } catch (e: Exception) {
                entity.status = FlowState.ERROR
                flowRepository.save(entity)
            }
        }
    }
}

data class FlowSummary(
    val id: String,
    val name: String,
    val status: FlowState,
    val updatedAt: Instant,
    val deployedAt: Instant?,
)
```

## Step 3: Startup Listener

Redeploy flows that were running before the server restarted:

```kotlin
package com.flowcraft

import com.flowcraft.service.FlowService
import org.springframework.boot.context.event.ApplicationReadyEvent
import org.springframework.context.event.EventListener
import org.springframework.stereotype.Component

@Component
class StartupListener(private val flowService: FlowService) {

    @EventListener(ApplicationReadyEvent::class)
    fun onStartup() {
        flowService.redeployRunningFlows()
    }
}
```

## Step 4: Updated REST Controller

**src/main/kotlin/com/flowcraft/api/FlowController.kt:**
```kotlin
package com.flowcraft.api

import com.flowcraft.model.FlowDefinition
import com.flowcraft.service.FlowService
import com.flowcraft.service.FlowSummary
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/flows")
@CrossOrigin(origins = ["http://localhost:5173"])
class FlowController(private val flowService: FlowService) {

    /** Save (create or update) a flow definition */
    @PostMapping
    fun save(@RequestBody definition: FlowDefinition): ResponseEntity<Map<String, String>> {
        flowService.save(definition)
        return ResponseEntity.ok(mapOf("id" to definition.id, "status" to "saved"))
    }

    /** Get a flow definition by ID */
    @GetMapping("/{flowId}")
    fun get(@PathVariable flowId: String): ResponseEntity<FlowDefinition> {
        val flow = flowService.get(flowId)
        return if (flow != null) ResponseEntity.ok(flow)
        else ResponseEntity.notFound().build()
    }

    /** List all flows */
    @GetMapping
    fun list(): List<FlowSummary> = flowService.listAll()

    /** Delete a flow */
    @DeleteMapping("/{flowId}")
    fun delete(@PathVariable flowId: String): ResponseEntity<Void> {
        return if (flowService.delete(flowId)) ResponseEntity.noContent().build()
        else ResponseEntity.notFound().build()
    }

    /** Deploy a saved flow */
    @PostMapping("/{flowId}/deploy")
    fun deploy(@PathVariable flowId: String): ResponseEntity<Map<String, Any>> {
        val entity = flowService.deploy(flowId)
        return ResponseEntity.ok(mapOf(
            "id" to entity.id,
            "status" to entity.status.name,
            "deployedAt" to (entity.deployedAt?.toString() ?: ""),
        ))
    }

    /** Undeploy a running flow */
    @PostMapping("/{flowId}/undeploy")
    fun undeploy(@PathVariable flowId: String): ResponseEntity<Map<String, Any>> {
        val entity = flowService.undeploy(flowId)
        return ResponseEntity.ok(mapOf(
            "id" to entity.id,
            "status" to entity.status.name,
        ))
    }
}
```

## Step 5: Frontend API Client (Updated)

**src/api/client.ts:**
```ts
const API = '/api/flows';

export interface FlowSummary {
  id: string;
  name: string;
  status: 'STOPPED' | 'RUNNING' | 'ERROR';
  updatedAt: string;
  deployedAt: string | null;
}

// Save flow (create or update)
export async function saveFlow(flow: any): Promise<{ id: string }> {
  const res = await fetch(API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(flow),
  });
  return res.json();
}

// Load a specific flow
export async function loadFlow(flowId: string): Promise<any> {
  const res = await fetch(`${API}/${flowId}`);
  if (!res.ok) throw new Error('Flow not found');
  return res.json();
}

// List all flows
export async function listFlows(): Promise<FlowSummary[]> {
  const res = await fetch(API);
  return res.json();
}

// Delete a flow
export async function deleteFlow(flowId: string): Promise<void> {
  await fetch(`${API}/${flowId}`, { method: 'DELETE' });
}

// Deploy
export async function deployFlow(flowId: string): Promise<any> {
  const res = await fetch(`${API}/${flowId}/deploy`, { method: 'POST' });
  return res.json();
}

// Undeploy
export async function undeployFlow(flowId: string): Promise<any> {
  const res = await fetch(`${API}/${flowId}/undeploy`, { method: 'POST' });
  return res.json();
}
```

## The API Surface

| Method | Path | Action |
|---|---|---|
| POST | `/api/flows` | Save flow definition |
| GET | `/api/flows` | List all flows |
| GET | `/api/flows/:id` | Get flow definition |
| DELETE | `/api/flows/:id` | Delete flow |
| POST | `/api/flows/:id/deploy` | Deploy (start) |
| POST | `/api/flows/:id/undeploy` | Undeploy (stop) |

## The User Workflow

```
1. User builds flow in UI
2. Clicks "Save" → POST /api/flows → stored in PostgreSQL
3. Clicks "Deploy" → POST /api/flows/:id/deploy → flow goes live
4. Server restarts → on startup, redeploys all RUNNING flows
5. User clicks "Stop" → POST /api/flows/:id/undeploy → flow stops
6. User edits flow → Save again → Deploy again (hot-reload)
```

## Key Takeaways

1. **JSONB storage** — the full flow definition lives as JSON in PostgreSQL (queryable, indexable)
2. **Separate save and deploy** — users can draft flows without deploying them
3. **Startup recovery** — flows marked as RUNNING get redeployed on boot
4. **The service layer** coordinates between persistence and runtime
5. **Status tracking** — STOPPED, RUNNING, ERROR gives the UI clear state to display

---

[← Chapter 7: Adapters](chapter-07-adapters.md) | [Chapter 9: Deploy from UI →](chapter-09-deploy-ui.md)
