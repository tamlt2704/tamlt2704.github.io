# LangChain, LangGraph & Langfuse Mastery

An AI-powered legal research assistant — built chapter by chapter, disaster by disaster.

## The Story

You're the AI engineer at **NovaMind**, a startup building a research assistant for law firms. The prototype is a single OpenAI API call that hallucinates case law, forgets context, and costs $400/day. Your job: turn it into a production system with chains, retrieval, agents, workflows, and observability.

## Chapters

### Part 1: LangChain Foundations — "Make It Think"

| # | Problem | What You Learn |
|---|---------|----------------|
| 01 | Prototype is a raw API call | ChatModels, messages, LCEL basics |
| 02 | Output is inconsistent | Prompt templates, few-shot, system messages |
| 03 | Need JSON, not prose | Structured output, Pydantic, `with_structured_output` |
| 04 | One prompt can't do everything | Chains, RunnableSequence, composition |
| 05 | AI forgets context | Memory — window, summary, session-based |

### Part 2: RAG & Tools — "Make It Know Things"

| # | Problem | What You Learn |
|---|---------|----------------|
| 06 | AI invents case law | RAG — embeddings, vector stores, retrieval |
| 07 | PDFs are too big | Document loaders, text splitting, chunking |
| 08 | Retrieved chunks are irrelevant | Retrieval strategies, reranking, hybrid search |
| 09 | Can't check live data | Tools & function calling |
| 10 | Needs multi-step reasoning | Agents — ReAct, tool selection |

### Part 3: LangGraph — "Make It Reason"

| # | Problem | What You Learn |
|---|---------|----------------|
| 11 | Agent loops forever | LangGraph basics — nodes, edges, state |
| 12 | Workflow needs branching | Conditional edges, routing |
| 13 | Lawyer must approve first | Human-in-the-loop, interrupts |
| 14 | Multi-step pipeline | Multi-agent graphs, subgraphs |
| 15 | Long tasks need persistence | Checkpointing, resumption |

### Part 4: Langfuse & Production — "Make It Observable"

| # | Problem | What You Learn |
|---|---------|----------------|
| 16 | "Why did this take 45 seconds?" | Langfuse traces, spans, latency |
| 17 | Token bill is $400/day | Cost tracking, model comparison |
| 18 | Prompt changes break things | Prompt management, versioning |
| 19 | "Is the AI getting better?" | Evaluations, scoring, datasets |
| 20 | Ship it | Deployment, error handling, guardrails |

## Prerequisites

```bash
python --version  # 3.11+
pip install langchain langchain-openai langgraph langfuse chromadb fastapi
export OPENAI_API_KEY="sk-..."
```

## The Stack

| Tool | Role |
|------|------|
| LangChain | Chains, prompts, tools, retrieval |
| LangGraph | Stateful multi-step workflows |
| Langfuse | Observability, cost tracking, evals |
| OpenAI / Anthropic | LLM providers |
| ChromaDB | Vector store for RAG |
| FastAPI | API layer |
