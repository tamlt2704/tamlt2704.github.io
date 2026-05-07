# LangChain, LangGraph & Langfuse Mastery: An AI Agent Survival Story

You just joined **NovaMind** — a startup building an AI-powered research assistant for law firms. Lawyers upload case files, ask questions in plain English, and the AI finds relevant precedents, summarizes documents, and drafts responses.

Day one, the founder — **Priya** — pulls you into a call.

> "We have a prototype. It's a single OpenAI API call wrapped in a Flask route. It hallucinates case law that doesn't exist. It forgets context after two messages. It costs us $400/day in tokens because it sends entire PDFs to GPT-4 every time. The lawyers are furious. We need chains, memory, retrieval, agents, and we need to see what the hell it's doing when it goes wrong. You're building the AI backend."

She shares a Notion doc with the requirements:

> Multi-step reasoning. Document retrieval. Tool use. Conversation memory. Observability. Cost tracking. Human-in-the-loop approval for legal drafts. Go.

You open your terminal. The cursor blinks.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | AI Engineer | "I've called the OpenAI API. That counts, right?" |
| **Priya** | Founder/CEO | Built the prototype in a weekend. Knows it's held together with string. |
| **Raj** | Senior Backend Dev | "If I can't debug it, it doesn't ship." Demands observability. |
| **Elena** | Lead Lawyer (client) | "Your AI cited a case that doesn't exist. In a filing. To a judge." |
| **The Prototype** | Legacy system | One giant prompt. No memory. No retrieval. $400/day. |
| **The Hallucination** | That one wrong answer | Invented *Smith v. OpenAI (2019)*. There is no such case. |
| **Token Bill** | The invoice | Grows every day. Nobody knows why. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **LangChain** | Framework for chaining LLM calls, prompts, tools, and retrieval |
| **LangGraph** | State machines for complex multi-step agent workflows |
| **Langfuse** | Observability — traces, costs, latency, prompt management |
| **OpenAI / Anthropic** | LLM providers (GPT-4o, Claude) |
| **ChromaDB / pgvector** | Vector store for document retrieval (RAG) |
| **FastAPI** | API layer |
| **Python 3.11+** | The language |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Elena or Priya needs the AI to do something
   │
   ▼
  🤔 You learn the LangChain/LangGraph/Langfuse concept needed
   │
   ▼
  ⌨️  You build it
   │
   ▼
  💥 It hallucinates, loops forever, costs $50, or loses context
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  📋 Next requirement
```

No concept shows up before you need it. You won't hear about RAG until the AI invents case law. You won't touch LangGraph until a simple chain can't handle conditional logic. You won't learn Langfuse until Raj asks "why did this response take 45 seconds and cost $2?"

The failures come first. The framework follows.

---

## The Roadmap

### Part 1: LangChain Foundations — "Make It Think"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ The prototype is a raw API call        │ LangChain basics, ChatModels, messages
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ Output is inconsistent garbage         │ Prompt templates, system messages, few-shot
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ Need structured JSON, not prose        │ Output parsers, Pydantic models, structured output
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ One prompt can't do everything         │ Chains (LCEL), pipe operator, RunnableSequence
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ AI forgets what you said 2 messages ago│ Memory — conversation buffer, summary, window
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: RAG & Tools — "Make It Know Things"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ AI invents case law that doesn't exist │ RAG — embeddings, vector stores, retrieval
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ PDFs are too big for context window    │ Document loaders, text splitting, chunking
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ Retrieved chunks are irrelevant        │ Retrieval strategies, reranking, hybrid search
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ AI can't check today's court schedule  │ Tools & function calling, custom tools
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ AI needs to search, then reason, then  │ Agents — ReAct, tool selection, agent executor
    │ search again                           │
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: LangGraph — "Make It Reason"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ Agent loops forever or picks wrong tool│ LangGraph basics — nodes, edges, state
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ Workflow needs conditional branching   │ Conditional edges, routing, decision nodes
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ Lawyer must approve before filing      │ Human-in-the-loop, interrupts, checkpoints
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ Research + drafting + review pipeline  │ Multi-agent graphs, subgraphs, handoffs
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ Long-running tasks need persistence    │ State persistence, checkpointing, resumption
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Langfuse & Production — "Make It Observable"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "Why did this take 45 seconds?"        │ Langfuse setup, traces, spans, latency
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ Token bill is $400/day, nobody knows   │ Cost tracking, token usage, model comparison
    │ why                                    │
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ Prompt changes break things silently   │ Prompt management, versioning, A/B testing
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "Is the AI getting better or worse?"   │ Evaluations, scoring, datasets, regression tests
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ Ship it: the full production pipeline  │ Deployment, error handling, fallbacks, guardrails
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Architecture We're Building

By Chapter 20, you'll have this:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NovaMind AI Backend                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FastAPI                                                             │
│  ├── /api/chat              → Conversational legal assistant         │
│  ├── /api/research          → Multi-step case research agent         │
│  ├── /api/summarize         → Document summarization                 │
│  └── /api/draft             → Legal draft generation (human-in-loop) │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    LangGraph Workflows                         │   │
│  │  ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌───────────┐  │   │
│  │  │ Retrieve │──→│  Reason  │──→│  Draft  │──→│  Approve  │  │   │
│  │  └─────────┘   └──────────┘   └─────────┘   └───────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  ChromaDB    │  │  OpenAI /    │  │  Langfuse               │  │
│  │  (vectors)   │  │  Anthropic   │  │  (traces, costs, evals) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Python 3.11+

```bash
python --version  # 3.11+
```

### Core Packages

```bash
pip install langchain langchain-openai langchain-community langgraph langfuse
pip install chromadb fastembed
pip install fastapi uvicorn python-dotenv
```

### An LLM Provider

You need at least one:

```bash
# Option A: OpenAI (recommended for starting)
export OPENAI_API_KEY="sk-..."

# Option B: Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Option C: Local with Ollama (free, no API key)
ollama pull llama3.1
```

Verify:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("Say hello in exactly 3 words")
print(response.content)
```

If you get a response, you're in business.

### Langfuse (for Part 4)

Two options:

```bash
# Option A: Langfuse Cloud (free tier, easiest)
# Sign up at https://langfuse.com → get keys
export LANGFUSE_PUBLIC_KEY="pk-..."
export LANGFUSE_SECRET_KEY="sk-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"

# Option B: Self-hosted (Docker)
docker run -d --name langfuse \
  -p 3000:3000 \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/langfuse" \
  langfuse/langfuse:latest
```

### Quick Check

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
result = llm.invoke("What is 2 + 2? Answer with just the number.")
print(result.content)  # "4"
print("Ready to go ✓")
```

---

## What You'll Understand by the End

| Concept | Why It Matters |
|---------|---------------|
| **Chains** | Compose LLM calls like Unix pipes — each step transforms data |
| **RAG** | Ground the AI in real documents so it stops hallucinating |
| **Agents** | Let the AI decide which tools to use and in what order |
| **LangGraph** | Build complex workflows with branching, loops, and human approval |
| **Langfuse** | See exactly what happened in every AI call — latency, cost, quality |
| **Evaluations** | Measure whether your AI is getting better or worse over time |

---

## The Prototype: What You Inherit

This is `app.py` on day one. Priya built it in a weekend. It grew.

```python
# app.py - NovaMind "AI" backend
# "It works on my laptop" - Priya, 3 months ago
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
client = openai.OpenAI()

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    
    # The entire "AI pipeline"
    response = client.chat.completions.create(
        model="gpt-4",  # $$$
        messages=[
            {"role": "system", "content": "You are a legal research assistant."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=4000
    )
    
    return jsonify({"response": response.choices[0].message.content})

@app.route("/research", methods=["POST"])
def research():
    query = request.json["query"]
    documents = request.json.get("documents", [])
    
    # Shove entire documents into the prompt
    context = "\n\n".join(documents)  # hope it fits in context window!
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal researcher."},
            {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"}
        ],
        max_tokens=4000
    )
    
    return jsonify({"response": response.choices[0].message.content})

# No memory. No retrieval. No tools. No observability.
# Cost: ~$400/day. Accuracy: "vibes-based."
```

Problems with this:
- No memory — every request starts fresh
- No retrieval — shoves entire documents into the prompt (or truncates them)
- No tools — can't look up real data
- No observability — when it's wrong, nobody knows why
- No cost control — GPT-4 for everything, even simple questions
- No structure — output is unpredictable prose

By Chapter 20, this will be a multi-agent system with retrieval, memory, tool use, human-in-the-loop approval, full observability, and cost tracking. But first — you need to understand what LangChain actually is.

---

[Next: Chapter 1 — Your First Chain →](chapter-01-first-chain.md)
