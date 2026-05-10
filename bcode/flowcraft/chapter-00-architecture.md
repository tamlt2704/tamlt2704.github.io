# Chapter 0: Architecture & Project Setup

[Chapter 1: Node Palette →](chapter-01-node-palette.md)

---

## The Big Picture

We're building **FlowCraft** — a visual integration platform. Users drag blocks, connect them, and deploy flows that run on a Spring Integration engine.

The system has two halves:

```
┌─────────────────────┐         ┌─────────────────────┐
│   flowcraft-ui      │  REST   │  flowcraft-engine    │
│   (React + RF)      │────────→│  (Spring Boot)       │
│                     │←────────│                      │
│   Port 5173        │  WS     │  Port 8080           │
└─────────────────────┘         └─────────────────────┘
```

## Data Model: The Flow Graph

Everything revolves around one JSON structure — the **Flow Definition**:

```json
{
  "id": "flow-123",
  "name": "Form to Database",
  "nodes": [
    {
      "id": "node-1",
      "type": "http-inbound",
      "category": "input",
      "position": { "x": 100, "y": 200 },
      "config": {
        "path": "/api/webhook",
        "method": "POST"
      }
    },
    {
      "id": "node-2",
      "type": "transform",
      "category": "processing",
      "position": { "x": 350, "y": 200 },
      "config": {
        "expression": "payload.name.toUpperCase()"
      }
    },
    {
      "id": "node-3",
      "type": "jdbc-outbound",
      "category": "output",
      "position": { "x": 600, "y": 200 },
      "config": {
        "sql": "INSERT INTO users(name) VALUES(:payload)",
        "dataSource": "default"
      }
    }
  ],
  "edges": [
    { "id": "e1", "source": "node-1", "target": "node-2" },
    { "id": "e2", "source": "node-2", "target": "node-3" }
  ]
}
```

This JSON is:
- **Created** by the React Flow UI (user drags and connects)
- **Stored** in PostgreSQL via the REST API
- **Compiled** into a Spring Integration `IntegrationFlow` by the engine
- **Registered** dynamically at runtime (no restart needed)

## The Three Block Categories

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   INPUT     │     │  PROCESSING │     │   OUTPUT    │
│             │     │             │     │             │
│ • HTTP In   │────→│ • Transform │────→│ • HTTP Out  │
│ • Timer     │     │ • Filter    │     │ • DB Write  │
│ • File Watch│     │ • Enrich    │     │ • File Write│
│ • Kafka In  │     │ • Split     │     │ • Kafka Out │
│ • MQTT In   │     │ • Aggregate │     │ • Email     │
│ • Cron      │     │ • LLM Call  │     │ • Slack     │
│ • Webhook   │     │ • Script    │     │ • Webhook   │
└─────────────┘     └─────────────┘     └─────────────┘
     GREEN               BLUE               ORANGE
```

Rules:
- A flow MUST start with at least one Input node
- A flow MUST end with at least one Output node
- Processing nodes sit in between (0 or more)
- Input nodes have only output handles (right side)
- Output nodes have only input handles (left side)
- Processing nodes have both

## Project Structure

```
flowcraft/
├── flowcraft-ui/                 # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Canvas.tsx        # React Flow canvas
│   │   │   ├── Sidebar.tsx       # Draggable node palette
│   │   │   ├── ConfigPanel.tsx   # Node configuration
│   │   │   └── nodes/           # Custom node components
│   │   │       ├── InputNode.tsx
│   │   │       ├── ProcessNode.tsx
│   │   │       └── OutputNode.tsx
│   │   ├── store/
│   │   │   └── flowStore.ts      # Zustand state
│   │   ├── types/
│   │   │   └── flow.ts           # TypeScript types
│   │   ├── api/
│   │   │   └── client.ts         # REST client
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── flowcraft-engine/             # Spring Boot backend
│   ├── src/main/kotlin/com/flowcraft/
│   │   ├── FlowcraftApplication.kt
│   │   ├── api/
│   │   │   └── FlowController.kt       # REST endpoints
│   │   ├── model/
│   │   │   └── FlowDefinition.kt       # Data classes
│   │   ├── compiler/
│   │   │   └── FlowCompiler.kt         # JSON → IntegrationFlow
│   │   ├── runtime/
│   │   │   └── FlowRuntime.kt          # Register/start/stop
│   │   ├── adapters/
│   │   │   ├── HttpAdapter.kt
│   │   │   ├── TimerAdapter.kt
│   │   │   ├── JdbcAdapter.kt
│   │   │   └── TransformAdapter.kt
│   │   └── monitoring/
│   │       └── FlowMetrics.kt          # Micrometer + WebSocket
│   ├── src/main/resources/
│   │   └── application.yml
│   └── build.gradle.kts
│
└── docker-compose.yml            # PostgreSQL + app
```

## Setup: Frontend

```bash
npm create vite@latest flowcraft-ui -- --template react-ts
cd flowcraft-ui
npm install @xyflow/react zustand tailwindcss @tailwindcss/vite
```

**vite.config.ts:**
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8080'
    }
  }
})
```

**src/main.css:**
```css
@import "tailwindcss";
@import "@xyflow/react/dist/style.css";
```

## Setup: Backend

Use [start.spring.io](https://start.spring.io) or Gradle init:

**build.gradle.kts:**
```kotlin
plugins {
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
    kotlin("jvm") version "1.9.24"
    kotlin("plugin.spring") version "1.9.24"
}

dependencies {
    // Core
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-websocket")
    implementation("org.springframework.boot:spring-boot-starter-actuator")

    // Spring Integration
    implementation("org.springframework.integration:spring-integration-core")
    implementation("org.springframework.integration:spring-integration-http")
    implementation("org.springframework.integration:spring-integration-jdbc")
    implementation("org.springframework.integration:spring-integration-file")
    implementation("org.springframework.integration:spring-integration-kafka")

    // Database
    runtimeOnly("org.postgresql:postgresql")

    // Metrics
    implementation("io.micrometer:micrometer-registry-prometheus")

    // Kotlin
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("org.jetbrains.kotlin:kotlin-reflect")
}
```

**application.yml:**
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/flowcraft
    username: flowcraft
    password: flowcraft
  jpa:
    hibernate:
      ddl-auto: update

server:
  port: 8080
```

## Docker Compose (Development)

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: flowcraft
      POSTGRES_USER: flowcraft
      POSTGRES_PASSWORD: flowcraft
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## How the Pieces Connect

```
User drags nodes → React Flow state → Zustand store
                                           │
User clicks "Deploy" ─────────────────────→│
                                           ▼
                                    POST /api/flows
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │  FlowController          │
                              │  - validates graph       │
                              │  - saves to PostgreSQL   │
                              │  - calls FlowCompiler    │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │  FlowCompiler            │
                              │  - walks the node graph  │
                              │  - builds IntegrationFlow│
                              │  - resolves adapters     │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │  FlowRuntime             │
                              │  - registers flow        │
                              │  - starts message flow   │
                              │  - exposes metrics       │
                              └─────────────────────────┘
```

## Key Design Decisions

### 1. JSON as the contract
The flow graph JSON is the single source of truth. The UI produces it, the backend consumes it. This means:
- UI and backend can evolve independently
- Flows can be version-controlled (store JSON in Git)
- Import/export is trivial

### 2. Dynamic flow registration
Spring Integration's `IntegrationFlowContext` lets you register and remove flows at runtime without restarting the application context. This is the magic that makes "one-click deploy" possible.

### 3. Adapter pattern for nodes
Each node type (http-inbound, transform, jdbc-outbound) maps to an adapter class that knows how to produce the corresponding Spring Integration DSL fragment. Adding a new node type = adding one adapter class.

### 4. Category-based validation
The UI enforces: Input → Processing → Output. The backend validates the same rules before compiling. Double safety.

## What's Next

Chapter 1: We build the React Flow canvas with a draggable sidebar of Input/Processing/Output blocks. By the end, you'll have a working visual editor where users can construct flow graphs.

---

[Chapter 1: Node Palette →](chapter-01-node-palette.md)
