# FlowCraft: Build a Visual Integration Platform

**React Flow (UI) + Spring Integration (Engine)**

A step-by-step guide to building a product where users visually design integration flows (Input → Process → Output) and deploy them to a production-grade Spring Integration runtime.

## The Product

FlowCraft lets users:
1. Drag "lego blocks" onto a canvas (React Flow)
2. Connect them into flows (Input → Processing → Output)
3. Deploy with one click to a Spring Integration engine
4. Monitor execution in real-time

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React + React Flow)                               │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  HTTP In │───→│ Transform│───→│ DB Write │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                                              │
│  Canvas → JSON graph → POST /api/flows                      │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  BACKEND (Spring Boot + Spring Integration)                   │
│                                                              │
│  /api/flows  →  FlowCompiler  →  IntegrationFlowContext      │
│                                                              │
│  JSON graph → IntegrationFlow DSL → Register & Run           │
│                                                              │
│  Metrics (Micrometer) → WebSocket → Live UI updates          │
└──────────────────────────────────────────────────────────────┘
```

## Chapters

### Part 1: Foundation (Chapters 0–3)
| Ch | Topic | What You Build |
|---|---|---|
| 0 | Architecture & Setup | Monorepo, both projects scaffolded |
| 1 | Node Palette | Draggable Input/Process/Output blocks |
| 2 | Canvas & Connections | Connect blocks, validate edges |
| 3 | Node Configuration | Side panel to configure each block |

### Part 2: Backend Engine (Chapters 4–7)
| Ch | Topic | What You Build |
|---|---|---|
| 4 | Spring Integration Basics | First hardcoded flow |
| 5 | Flow Compiler | JSON graph → IntegrationFlow DSL |
| 6 | Dynamic Registration | Deploy/undeploy flows at runtime |
| 7 | Built-in Adapters | HTTP, Timer, Database, REST call |

### Part 3: Connect UI to Engine (Chapters 8–11)
| Ch | Topic | What You Build |
|---|---|---|
| 8 | Flow CRUD API | Save, load, list, delete flows |
| 9 | Deploy & Execute | One-click deploy from UI |
| 10 | Live Monitoring | WebSocket metrics on canvas |
| 11 | Error Handling | Error channels, retry, dead-letter |

### Part 4: Production Features (Chapters 12–15)
| Ch | Topic | What You Build |
|---|---|---|
| 12 | LLM Node | OpenAI/Ollama as a processing block |
| 13 | Database Node | Query any SQL database |
| 14 | Auth & Multi-tenancy | Users own their flows |
| 15 | Ship It | Docker, health checks, deployment |

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | React 18 + TypeScript |
| Flow Editor | @xyflow/react (React Flow) |
| UI State | Zustand |
| Styling | Tailwind CSS |
| Backend | Spring Boot 3.x + Kotlin |
| Integration Engine | Spring Integration 6.x |
| Database | PostgreSQL (flow storage) |
| Real-time | WebSocket (STOMP) |
| Build | Gradle (backend), Vite (frontend) |

## Prerequisites

- React basics (hooks, components, state)
- Spring Boot basics (controllers, beans, DI)
- Basic understanding of messaging patterns (optional, taught in Ch 4)
