# Spring AI Mastery: An LLM-Powered Survival Story

You're back at **ShopZilla Inc.** — the chaotic e-commerce company from the job engine days. The job engine works. Karen's CSVs import fine. The exchange-rate API stopped banning your IP.

Then Captain Deadline calls a meeting.

> "Every competitor has AI now. Chatbots. Product recommendations. Smart search. Our support team answers the same 50 questions every day. Our product descriptions are written by interns who copy-paste from Amazon. Fix it."

He slides a laptop across the table. It's running Ollama with a local LLM.

> "No OpenAI. No API keys. No sending customer data to the cloud. Everything runs on our hardware. Use Spring AI. You have two weeks."

You open IntelliJ. The cursor blinks.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Dev (promoted from intern) | "I survived the job engine. How hard can AI be?" |
| **Captain Deadline** | CTO | "Every competitor has AI. We need it yesterday." |
| **Karen from Sales** | Stakeholder | "The chatbot better know our return policy." |
| **Mrs. Jira** | Product Manager | "Can it write product descriptions? Like, good ones?" |
| **Old Greg** | Senior Dev | "RAG is just a fancy SELECT statement." |
| **Silent Bob** | DevOps | Runs Ollama on a GPU box. Communicates via Slack emoji. |
| **The Hallucination** | That one wrong answer | Told a customer we accept Bitcoin. We don't. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **Spring Boot 3.4+** | Application framework |
| **Spring AI** | LLM integration framework |
| **Ollama** | Local LLM runtime (no cloud, no API keys) |
| **Llama 3.1 / Mistral** | The actual language models |
| **PostgreSQL + pgvector** | Vector database for RAG |
| **Docker** | Runs Ollama and Postgres |

Everything runs locally. No OpenAI account. No cloud bills. No data leaving your network.

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Someone needs AI to do something
   │
   ▼
  🤔 You learn the Spring AI concept needed
   │
   ▼
  ⌨️  You build it
   │
   ▼
  💥 The LLM hallucinates, is slow, or gives garbage
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  📋 Next request
```

No concept shows up before you need it. You won't hear about RAG until the chatbot invents a return policy. You won't touch function calling until Mrs. Jira wants the AI to check real inventory. You won't learn about prompt templates until the output is inconsistent garbage.

---

## The Roadmap

### Part 1: Foundations — "Make It Talk"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ Setup Ollama + first prompt            │ Spring AI basics, ChatClient, models
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ Product description generator          │ Prompt templates, system messages
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ Structured output (JSON from LLM)      │ BeanOutputConverter, type-safe responses
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ Streaming responses                    │ Flux, SSE, real-time token output
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Real Features — "Make It Useful"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ Customer support chatbot               │ Conversation memory, chat history
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ RAG: teach it our return policy        │ Embeddings, vector store, retrieval
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ Function calling: check real inventory │ Tool/function registration, callbacks
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ Smart product search                   │ Semantic search, similarity, embeddings
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Production — "Make It Reliable"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ Guardrails: stop hallucinations        │ Output validation, content filtering
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ Multi-model: route by task             │ Advisors, model selection, fallbacks
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ Performance: caching & batching        │ Response caching, async, rate limiting
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ Testing & observability                │ Mocking LLMs, metrics, tracing
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Prerequisites

### Java 21

```bash
java -version  # 21+
```

### Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

Start Ollama and pull a model:

```bash
ollama serve  # starts the server on port 11434

# Pull a model (pick one)
ollama pull llama3.1      # 8B params, good general purpose (~4.7GB)
ollama pull mistral       # 7B params, fast, good at instructions (~4.1GB)
ollama pull nomic-embed-text  # embedding model for RAG (Chapter 6)
```

Verify:

```bash
curl http://localhost:11434/api/generate -d '{"model":"llama3.1","prompt":"Hello"}'
```

If you get a response, Ollama is running.

### PostgreSQL with pgvector (for Chapter 6+)

```bash
docker run -d --name shopzilla-ai-db -p 5432:5432 \
  -e POSTGRES_DB=shopzilla_ai \
  -e POSTGRES_PASSWORD=shopzilla \
  pgvector/pgvector:pg16
```

---

## The Project

We're building an AI layer on top of ShopZilla's existing e-commerce platform. The AI doesn't replace the backend — it enhances it.

```
┌─────────────────────────────────────────────────────────────┐
│                     ShopZilla AI Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Spring Boot App (Spring AI)                                 │
│  ├── /api/chat          → Customer support chatbot           │
│  ├── /api/describe      → Product description generator      │
│  ├── /api/search        → Semantic product search            │
│  └── /api/recommend     → Product recommendations            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Ollama     │  │  pgvector    │  │  ShopZilla API   │  │
│  │  (LLM host)  │  │ (embeddings) │  │  (products, etc) │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

[Next: Chapter 1 — Your First Prompt →](chapter-01-first-prompt.md)
