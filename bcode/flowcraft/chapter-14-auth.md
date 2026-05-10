# Chapter 14: Auth & Multi-tenancy

[← Chapter 13: Database Node](chapter-13-database-node.md) | [Chapter 15: Ship It →](chapter-15-ship-it.md)

---

## Goal

Add authentication and tenant isolation so multiple users/teams can use the platform without seeing each other's flows. By the end: users log in, own their flows, and can't access others'.

## Step 1: Spring Security Setup

**build.gradle.kts:**
```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
    implementation("io.jsonwebtoken:jjwt-api:0.12.5")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.5")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.5")
}
```

## Step 2: Security Configuration

**src/main/kotlin/com/flowcraft/config/SecurityConfig.kt:**
```kotlin
package com.flowcraft.config

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity
import org.springframework.security.config.http.SessionCreationPolicy
import org.springframework.security.web.SecurityFilterChain
import org.springframework.web.cors.CorsConfiguration

@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
        http
            .cors { cors ->
                cors.configurationSource {
                    CorsConfiguration().apply {
                        allowedOrigins = listOf("http://localhost:5173")
                        allowedMethods = listOf("*")
                        allowedHeaders = listOf("*")
                    }
                }
            }
            .csrf { it.disable() }
            .sessionManagement { it.sessionCreationPolicy(SessionCreationPolicy.STATELESS) }
            .authorizeHttpRequests { auth ->
                auth
                    .requestMatchers("/api/auth/**").permitAll()
                    .requestMatchers("/ws/**").permitAll()  // WebSocket
                    .requestMatchers("/actuator/**").permitAll()
                    .anyRequest().authenticated()
            }
            .oauth2ResourceServer { it.jwt {} }

        return http.build()
    }
}
```

## Step 3: User & Tenant Model

**src/main/kotlin/com/flowcraft/model/User.kt:**
```kotlin
package com.flowcraft.model

import jakarta.persistence.*

@Entity
@Table(name = "users")
data class UserEntity(
    @Id
    val id: String,
    val email: String,
    val name: String,
    val tenantId: String,  // Team/org isolation

    @Enumerated(EnumType.STRING)
    val role: UserRole = UserRole.EDITOR,
)

enum class UserRole {
    VIEWER,   // Can see flows, not edit
    EDITOR,   // Can create/edit flows
    ADMIN,    // Can manage users, data sources
}
```

## Step 4: Add Tenant to Flow Entity

```kotlin
@Entity
@Table(name = "flows")
data class FlowEntity(
    @Id val id: String,
    var name: String,
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    var definition: String,
    @Enumerated(EnumType.STRING)
    var status: FlowState = FlowState.STOPPED,

    // Ownership
    val tenantId: String,          // ← NEW
    val createdBy: String,         // ← NEW (user ID)

    val createdAt: Instant = Instant.now(),
    var updatedAt: Instant = Instant.now(),
    var deployedAt: Instant? = null,
)
```

Update repository:
```kotlin
interface FlowRepository : JpaRepository<FlowEntity, String> {
    fun findByTenantIdOrderByUpdatedAtDesc(tenantId: String): List<FlowEntity>
    fun findByIdAndTenantId(id: String, tenantId: String): FlowEntity?
}
```

## Step 5: Tenant-Aware Service

```kotlin
@Service
class FlowService(
    private val flowRepository: FlowRepository,
    private val flowRuntime: FlowRuntime,
    private val objectMapper: ObjectMapper,
) {

    fun save(definition: FlowDefinition, tenantId: String, userId: String): FlowEntity {
        val json = objectMapper.writeValueAsString(definition)

        val entity = flowRepository.findByIdAndTenantId(definition.id, tenantId)?.apply {
            name = definition.name
            this.definition = json
            updatedAt = Instant.now()
        } ?: FlowEntity(
            id = definition.id,
            name = definition.name,
            definition = json,
            tenantId = tenantId,
            createdBy = userId,
        )

        return flowRepository.save(entity)
    }

    fun listAll(tenantId: String): List<FlowSummary> {
        return flowRepository.findByTenantIdOrderByUpdatedAtDesc(tenantId).map { ... }
    }

    fun get(flowId: String, tenantId: String): FlowDefinition? {
        val entity = flowRepository.findByIdAndTenantId(flowId, tenantId) ?: return null
        return objectMapper.readValue(entity.definition, FlowDefinition::class.java)
    }

    fun delete(flowId: String, tenantId: String): Boolean {
        val entity = flowRepository.findByIdAndTenantId(flowId, tenantId) ?: return false
        if (flowRuntime.isRunning(flowId)) flowRuntime.undeploy(flowId)
        flowRepository.delete(entity)
        return true
    }
}
```

## Step 6: Extract Tenant from JWT

```kotlin
package com.flowcraft.api

import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.oauth2.jwt.Jwt

fun currentUserId(): String {
    val jwt = SecurityContextHolder.getContext().authentication.principal as Jwt
    return jwt.subject
}

fun currentTenantId(): String {
    val jwt = SecurityContextHolder.getContext().authentication.principal as Jwt
    return jwt.getClaimAsString("tenant_id")
        ?: throw IllegalStateException("No tenant_id in token")
}
```

Updated controller:
```kotlin
@PostMapping
fun save(@RequestBody definition: FlowDefinition): ResponseEntity<*> {
    val entity = flowService.save(definition, currentTenantId(), currentUserId())
    return ResponseEntity.ok(mapOf("id" to entity.id))
}

@GetMapping
fun list(): List<FlowSummary> {
    return flowService.listAll(currentTenantId())
}
```

## Step 7: Frontend Auth

**src/api/auth.ts:**
```ts
let token: string | null = null;

export function setToken(t: string) {
  token = t;
}

export function getAuthHeaders(): Record<string, string> {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

// Update all API calls to include auth:
export async function listFlows(): Promise<FlowSummary[]> {
  const res = await fetch('/api/flows', {
    headers: getAuthHeaders(),
  });
  return res.json();
}
```

## Step 8: RBAC on Flow Operations

```kotlin
// In controller or service:
fun deploy(flowId: String, tenantId: String, userRole: UserRole): FlowEntity {
    if (userRole == UserRole.VIEWER) {
        throw AccessDeniedException("Viewers cannot deploy flows")
    }
    // ... deploy logic
}

fun deleteDataSource(name: String, userRole: UserRole) {
    if (userRole != UserRole.ADMIN) {
        throw AccessDeniedException("Only admins can manage data sources")
    }
    // ... delete logic
}
```

## Isolation Model

```
┌─────────────────────────────────────────────────┐
│  Tenant: Acme Corp                               │
│                                                  │
│  Users: alice (ADMIN), bob (EDITOR), carol (VIEWER)│
│                                                  │
│  Flows:                                          │
│  ├── flow-001 (created by alice) [RUNNING]       │
│  ├── flow-002 (created by bob)   [STOPPED]       │
│  └── flow-003 (created by alice) [RUNNING]       │
│                                                  │
│  Data Sources:                                   │
│  ├── production-db (managed by alice)            │
│  └── analytics-db (managed by alice)             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Tenant: StartupXYZ                              │
│                                                  │
│  Users: dave (ADMIN)                             │
│                                                  │
│  Flows:                                          │
│  └── flow-101 (created by dave) [RUNNING]        │
│                                                  │
│  ← Cannot see Acme Corp's flows or data sources  │
└─────────────────────────────────────────────────┘
```

## Key Takeaways

1. **JWT tokens** carry user ID and tenant ID — stateless auth
2. **Tenant isolation** at the repository level — queries always filter by `tenantId`
3. **RBAC** (Viewer/Editor/Admin) controls who can deploy, edit, manage
4. **Data source isolation** — each tenant manages their own DB connections
5. **Flow runtime isolation** — flows from different tenants run in the same JVM but are logically separated (for true isolation, use separate pods per tenant)

---

[← Chapter 13: Database Node](chapter-13-database-node.md) | [Chapter 15: Ship It →](chapter-15-ship-it.md)
