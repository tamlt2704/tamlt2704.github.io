# PydanticAI: An Agent Engineering Story

You just joined **Cortex** — a startup building an AI-powered customer support platform. Think Intercom meets a team of specialized AI agents. Customers ask questions, agents route them, look up data, draft responses, escalate when needed — all structured, validated, observable.

Day one, the CTO — **Priya** — pulls you into a whiteboard session.

> "We have a prototype. It's 2,000 lines of raw OpenAI API calls. No types. No validation. The LLM returns whatever it wants — sometimes JSON, sometimes prose, sometimes hallucinated nonsense. We parse it with regex and pray. Every third response breaks the frontend. We're rewriting it with PydanticAI."

She draws a box on the whiteboard:

> "Agents. Tools. Structured output. Dependency injection. Multi-agent handoffs. Streaming. Observability. The whole thing — type-safe, testable, production-grade."

You open your terminal. The cursor blinks.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | AI Engineer | "I know Python. I know Pydantic. How hard can agents be?" |
| **Priya** | CTO | Draws agent graphs on whiteboards. Hates untyped LLM responses. |
| **Tomás** | Frontend Lead | "Give me structured JSON or give me death." |
| **Rin** | ML Engineer | Evaluates everything. "What's the accuracy on that?" |
| **The Old Prototype** | Legacy code | Raw API calls. Regex parsing. `json.loads(response.choices[0].message.content)` everywhere. |
| **The Hallucination** | That one bug | The agent confidently returns a refund policy that doesn't exist. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **PydanticAI** | Agent framework (type-safe, model-agnostic) |
| **Pydantic v2** | Data validation & structured output |
| **OpenAI / Anthropic / Gemini** | LLM providers (swap freely) |
| **httpx** | Async HTTP client (for tools) |
| **Logfire** | Observability & tracing |
| **pytest** | Testing with `TestModel` |

---

## How to Read This

Every chapter follows the same loop:

```
  🎫 A support ticket arrives
   │
   ▼
  🤔 You learn the PydanticAI concept needed
   │
   ▼
  ⌨️  You build the agent
   │
   ▼
  💥 Something breaks — wrong output, hallucination, no validation
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  🎫 Next ticket
```

No concept shows up before you need it. You won't hear about dependency injection until your tools need a database connection. You won't touch multi-agent handoffs until a single agent can't handle the complexity. You won't learn about streaming until Tomás needs real-time responses in the chat UI.

---

## The Roadmap

### Part 1: Foundations — "Make It Work"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Support Task                       │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ First agent: answer a question         │ Agent, run, instructions, models
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ Structured ticket classification       │ output_type, Pydantic models
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ Look up order status                   │ Tools, @agent.tool, RunContext
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ Connect to the database                │ Dependencies, deps_type, injection
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ Dynamic prompts from context           │ @agent.system_prompt, dynamic instructions
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Real Features — "Make It Reliable"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Support Task                       │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ Validate & retry bad responses         │ output_validator, ModelRetry
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ Stream responses to the chat UI        │ run_stream, StreamedRunResult
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ Route tickets to specialist agents     │ Multi-agent, agent-as-tool, handoffs
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ Conversation memory                    │ Message history, multi-turn
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ Connect external tools via MCP         │ Model Context Protocol, toolsets
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Production — "Make It Ship"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Support Task                       │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ Test without calling the LLM           │ TestModel, FunctionModel, overrides
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ Observe & debug in production          │ Logfire, tracing, cost tracking
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ Evaluate agent quality                 │ Pydantic Evals, datasets, metrics
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ Graphs for complex workflows           │ Graph support, state machines
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ Deploy the agent platform              │ FastAPI integration, async, scaling
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Prerequisites

- **Python 3.11+**
- **An LLM API key** (OpenAI, Anthropic, or Gemini)
- **Basic Pydantic knowledge** (you know what `BaseModel` and `Field` do)
- **A terminal**

```bash
python --version  # 3.11+
pip install pydantic-ai
```

---

## Why PydanticAI?

Priya explains it at the standup:

```
Raw LLM calls (old):               PydanticAI (new):
─────────────────────               ─────────────────────
Parse JSON with regex               Pydantic validates output
Hope the schema is right            Type-safe structured output
One model, locked in                Model-agnostic (swap freely)
No tool type safety                 Typed tools with RunContext
Test by calling the real API        TestModel (no API calls)
Debug with print statements         Logfire tracing
Manual retry on bad output          ModelRetry (automatic)
Spaghetti multi-agent code          Agent delegation & graphs
```

Tomás: "So the agent returns a Pydantic model and I know exactly what fields I get?"

You: "Yes. If the LLM returns garbage, PydanticAI retries automatically until it validates."

Tomás: "I love you."

---

## The Platform We're Building

```
┌─────────────────────────────────────────────────────────────┐
│                    Cortex Support Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Customer Message                                            │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Triage  │────▶│  Specialist  │────▶│   Response   │    │
│  │  Agent   │     │    Agent     │     │   Formatter  │    │
│  └──────────┘     └──────────────┘     └──────────────┘    │
│       │                   │                    │             │
│       ▼                   ▼                    ▼             │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │ Classify │     │  Tools:      │     │  Structured  │    │
│  │ Priority │     │  - DB lookup │     │  Output to   │    │
│  │ Route    │     │  - API calls │     │  Frontend    │    │
│  └──────────┘     │  - Knowledge │     └──────────────┘    │
│                   └──────────────┘                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Observability: Logfire traces, cost, latency        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

[Next: Chapter 1 — Your First Agent →](chapter-01-first-agent.md)
