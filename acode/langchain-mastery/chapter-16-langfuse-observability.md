# Chapter 16: Langfuse — Observability for LLM Apps

[← Chapter 15](chapter-15-persistence.md) · [Chapter 17: Cost Tracking →](chapter-17-cost-tracking.md)

---

## The Scene

It's Thursday. Elena reports: "The research feature took 45 seconds yesterday. Today it's taking 2 minutes. What changed?"

Raj checks the server logs:

```
[INFO] POST /api/research 200 — 127,342ms
[INFO] POST /api/research 200 — 98,201ms
[INFO] POST /api/research 200 — 143,892ms
```

That's all you have. The request took 127 seconds. But *why*? Was it the classification step? The retrieval? The memo generation? Did the model retry? Did it loop?

> "I can't debug what I can't see. We need tracing. Every LLM call, every retrieval, every tool use — I need to see the full execution trace." — Raj

Priya adds: "And I need to know how much we're spending. The token bill was $400 last month. I have no idea which features cost what."

You need **observability** — the ability to see inside your AI pipeline. Enter Langfuse.

---

## What is Langfuse?

Langfuse is an observability platform for LLM applications. It captures:

- **Traces**: The full execution path of a request
- **Spans**: Individual steps within a trace (LLM calls, retrievals, tool use)
- **Costs**: Token usage and dollar cost per call
- **Latency**: How long each step took
- **Inputs/Outputs**: What went in and what came out
- **Scores**: Quality metrics (manual or automated)

Think of it as Datadog/New Relic, but specifically designed for LLM pipelines.

```
Traditional logging:              Langfuse:
────────────────────              ────────
"Request took 45s"                Trace: research-memo
                                  ├── classify (1.2s, 340 tokens, $0.001)
                                  ├── retrieve (0.8s, 4 chunks found)
                                  ├── research (38s, 4200 tokens, $0.042) ← bottleneck!
                                  └── write_memo (5s, 1800 tokens, $0.018)
```

Now you know: the research step is the bottleneck. 38 seconds. 4200 tokens. You can optimize specifically that step.

---

## Setup

### Install

```bash
pip install langfuse
```

### Configure

```python
# .env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com  # or your self-hosted URL
```

### The LangChain Integration (Automatic)

Langfuse integrates with LangChain via a **callback handler**. Add it once, and every chain/graph execution is traced automatically:

```python
from langfuse.callback import CallbackHandler

# Create the handler
langfuse_handler = CallbackHandler()

# Pass it to any chain invocation
result = rag_chain.invoke(
    {"question": "What does Section 7.3 say?"},
    config={"callbacks": [langfuse_handler]}
)
```

That's it. Every LLM call, every retrieval, every tool use inside that chain is now traced in Langfuse.

---

## Automatic Tracing with LangChain

For global tracing (every call, automatically):

```python
from langfuse.callback import CallbackHandler
import os

# Set environment variables — LangChain picks them up automatically
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

# Create a global handler
langfuse_handler = CallbackHandler()

# Option 1: Pass to every invoke
result = chain.invoke(input, config={"callbacks": [langfuse_handler]})

# Option 2: Set as default for all chains
from langchain_core.globals import set_llm_cache
# Or configure at the chain level:
chain = chain.with_config(callbacks=[langfuse_handler])
```

---

## What a Trace Looks Like

After running the research memo pipeline, you open Langfuse and see:

```
Trace: research-memo-abc123
├── Span: classify
│   ├── Model: gpt-4o-mini
│   ├── Input: "Can a board member be held liable..."
│   ├── Output: {"area": "corporate", "jurisdiction": "Delaware"}
│   ├── Tokens: 142 in / 38 out
│   ├── Cost: $0.0003
│   └── Latency: 1.2s
│
├── Span: retrieve
│   ├── Type: retrieval
│   ├── Query: "board member liability merger Delaware"
│   ├── Results: 4 documents
│   └── Latency: 0.3s
│
├── Span: research
│   ├── Model: gpt-4o-mini
│   ├── Input: [system + context + question] (4200 tokens)
│   ├── Output: {"cases": [...], "key_principles": [...]}
│   ├── Tokens: 4200 in / 890 out
│   ├── Cost: $0.009
│   └── Latency: 8.4s
│
└── Span: write_memo
    ├── Model: gpt-4o-mini
    ├── Input: [formatted memo prompt] (1800 tokens)
    ├── Output: "QUESTION: Can a board member..."
    ├── Tokens: 1800 in / 620 out
    ├── Cost: $0.004
    └── Latency: 4.1s

Total: 14.0s | 7700 tokens | $0.013
```

Now you can see:
- Which step is slowest (research: 8.4s)
- Which step costs most (research: $0.009)
- What went into each LLM call
- What came out

---

## Custom Traces with the Decorator

For more control, use the `@observe` decorator:

```python
from langfuse.decorators import observe, langfuse_context

@observe()
def research_memo(question: str) -> str:
    """Full research memo pipeline — traced automatically."""
    
    # Each sub-call becomes a span
    classification = classify(question)
    documents = retrieve(question, classification)
    research = analyze(question, documents)
    memo = write_memo(question, research)
    
    return memo

@observe()
def classify(question: str) -> Classification:
    """Classify the legal question."""
    return classify_chain.invoke({"question": question})

@observe()
def retrieve(question: str, classification: Classification) -> list:
    """Retrieve relevant documents."""
    return retriever.invoke(question)

@observe()
def analyze(question: str, documents: list) -> ResearchResult:
    """Analyze retrieved documents."""
    return research_chain.invoke({
        "question": question,
        "context": format_docs(documents),
    })

@observe()
def write_memo(question: str, research: ResearchResult) -> str:
    """Write the final memo."""
    return memo_chain.invoke({
        "question": question,
        "cases": research.cases,
    })
```

Every function decorated with `@observe()` becomes a span in the trace. Nesting is automatic — `research_memo` is the parent, the others are children.

---

## Adding Metadata

Tag traces with useful context for filtering:

```python
@observe()
def research_memo(question: str, user_id: str, session_id: str) -> str:
    # Add metadata to the current trace
    langfuse_context.update_current_trace(
        user_id=user_id,
        session_id=session_id,
        metadata={
            "feature": "research_memo",
            "client": "elena",
        },
        tags=["production", "legal-research"],
    )
    
    # ... rest of the pipeline
```

Now you can filter in Langfuse:
- "Show me all traces from Elena"
- "Show me all research_memo traces that took > 30s"
- "Show me all traces tagged 'production' from last week"

---

## Scoring: Is the Output Good?

Langfuse lets you attach quality scores to traces:

```python
from langfuse import Langfuse

langfuse = Langfuse()

# After Elena reviews a response
langfuse.score(
    trace_id="trace-abc123",
    name="accuracy",
    value=1,  # 1 = correct, 0 = incorrect
    comment="Citations verified, all cases exist",
)

langfuse.score(
    trace_id="trace-abc123",
    name="helpfulness",
    value=0.8,  # 0-1 scale
    comment="Good analysis but missed one relevant case",
)
```

Over time, you build a dataset of scored traces. This lets you answer: "Is the AI getting better or worse?"

---

## LangGraph + Langfuse

LangGraph traces work the same way — each node becomes a span:

```python
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler()

# Trace the entire graph execution
result = app.invoke(
    {"question": "Fiduciary duty in Delaware"},
    config={"callbacks": [langfuse_handler]},
)
```

In Langfuse, you'll see:

```
Trace: langgraph-execution
├── Node: classify (1.1s)
├── Node: research (7.2s)
└── Node: write_memo (4.8s)
```

Each node's LLM calls are nested inside:

```
├── Node: research (7.2s)
│   ├── LLM Call: gpt-4o-mini (6.8s, 4200 tokens)
│   └── Retrieval: chroma (0.4s, 4 results)
```

---

## The Dashboard

Langfuse gives you a dashboard with:

| Metric | What It Shows |
|--------|---------------|
| Trace count | How many requests per day |
| Latency (P50, P95) | How fast/slow responses are |
| Cost per trace | Average cost per request |
| Token usage | Total tokens consumed |
| Error rate | How often things fail |
| Score trends | Quality over time |

Priya can now answer:
- "How much does the research feature cost per query?" → $0.013 average
- "What's our P95 latency?" → 14 seconds
- "Is quality improving?" → Accuracy score trending up from 0.7 to 0.85

---

## Debugging a Slow Request

Remember Elena's 45-second request? With Langfuse:

1. Filter traces by latency > 30s
2. Open the trace
3. See that the `research` node took 38 seconds
4. Drill into the LLM call — the input was 12,000 tokens (too much context)
5. The retriever returned 15 chunks instead of 4 (a bug in the search config)

Fix: limit retriever to `k=4`. Latency drops to 12 seconds.

Without Langfuse, you'd be guessing. With it, you see the exact bottleneck.

---

## What You Built

```python
# observability.py — NovaMind Langfuse integration
from langfuse.callback import CallbackHandler
from langfuse.decorators import observe, langfuse_context
from langfuse import Langfuse

# Global handler for LangChain/LangGraph
langfuse_handler = CallbackHandler()

# Client for manual operations (scoring, datasets)
langfuse_client = Langfuse()

@observe()
def research_memo(question: str, user_id: str) -> str:
    """Traced research memo pipeline."""
    langfuse_context.update_current_trace(
        user_id=user_id,
        metadata={"feature": "research_memo"},
    )
    
    classification = classify_chain.invoke({"question": question})
    documents = retriever.invoke(question)
    research = research_chain.invoke({...})
    memo = memo_chain.invoke({...})
    
    return memo

# For LangGraph
result = app.invoke(
    {"question": question},
    config={"callbacks": [langfuse_handler]},
)
```

---

## What's Next

You can see latency. But Priya's real question is: "Why is the token bill $400/day? Which feature costs the most? Which users are the heaviest? Can we use a cheaper model for simple questions?"

That's Chapter 17 — cost tracking and optimization.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| Trace | Full execution path of one request |
| Span | Individual step within a trace |
| `CallbackHandler` | Auto-traces LangChain/LangGraph calls |
| `@observe()` | Decorator for custom function tracing |
| `langfuse_context` | Add metadata, user_id, tags to traces |
| Scores | Attach quality ratings to traces |
| Dashboard | Latency, cost, token usage, error rates |
| Filtering | Find slow/expensive/failing traces |

---

[← Chapter 15](chapter-15-persistence.md) · [Chapter 17: Cost Tracking →](chapter-17-cost-tracking.md)
