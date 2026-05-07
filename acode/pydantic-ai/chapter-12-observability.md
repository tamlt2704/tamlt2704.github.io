# Chapter 12: Observability — Seeing Inside the Agent

[← Chapter 11: Testing](chapter-11-testing.md) | [Chapter 13: Evals →](chapter-13-evals.md)

---

## The Task

Priya: "Yesterday the agent took 12 seconds to respond to a simple question. Was it the LLM? A slow tool? A retry loop? I have no idea. I need to see inside every agent run — timing, tool calls, token usage, costs."

---

## Logfire: PydanticAI's Observability Platform

PydanticAI integrates natively with Pydantic Logfire for tracing:

```bash
pip install logfire
logfire auth  # Authenticate with your Logfire account
```

```python
import logfire
from pydantic_ai import Agent

logfire.configure()  # ← One line to enable tracing

agent = Agent('openai:gpt-4o', instructions='You are a support agent.')
result = agent.run_sync("How do I reset my password?")
```

That's it. Every agent run is now traced — you see:
- Total duration
- LLM request/response time
- Tool calls and their duration
- Token usage (input, output, total)
- Retry attempts
- The full message exchange

---

## What You See in Logfire

A single agent run produces a trace like:

```
▼ agent.run ("How do I reset my password?")  [1.2s]
  ├─ LLM request (openai:gpt-4o)  [0.8s]
  │   ├─ tokens: input=120, output=45
  │   └─ cost: $0.0024
  ├─ tool: search_knowledge_base("reset password")  [0.3s]
  │   └─ result: "To reset your password, go to Settings..."
  ├─ LLM request (openai:gpt-4o)  [0.6s]
  │   ├─ tokens: input=180, output=62
  │   └─ cost: $0.0031
  └─ output: "To reset your password..."
```

You can see exactly where time is spent and what the agent decided at each step.

---

## Adding Custom Spans

Add your own tracing to tools and business logic:

```python
import logfire
from pydantic_ai import Agent, RunContext


@agent.tool
async def get_order(ctx: RunContext[SupportDeps], order_id: str) -> str:
    """Look up an order."""
    with logfire.span("database_query", order_id=order_id):
        order = await ctx.deps.db.fetch_one(
            "SELECT * FROM orders WHERE id = $1", order_id
        )

    if not order:
        logfire.warn("Order not found", order_id=order_id)
        return "Order not found"

    logfire.info("Order found", order_id=order_id, status=order['status'])
    return str(order)
```

---

## Cost Tracking

Track spending across all agent runs:

```python
result = await agent.run("Help me with my account")

usage = result.usage()
print(f"Requests: {usage.requests}")
print(f"Input tokens: {usage.request_tokens}")
print(f"Output tokens: {usage.response_tokens}")
print(f"Total tokens: {usage.total_tokens}")
```

In Logfire, you can aggregate costs by:
- Agent name
- Customer tier
- Time period
- Model used

---

## Debugging Failed Runs

When something goes wrong, the trace shows exactly what happened:

```
▼ agent.run ("Cancel my subscription")  [8.2s] ⚠️ RETRY
  ├─ LLM request  [1.1s]
  │   └─ response: tool_call(cancel_subscription, reason="customer request")
  ├─ tool: cancel_subscription  [0.1s]
  │   └─ ⚠️ ModelRetry: "Cannot cancel — customer has active annual contract"
  ├─ LLM request (retry 1)  [1.5s]
  │   └─ response: tool_call(get_contract_details, customer_id="cust_123")
  ├─ tool: get_contract_details  [0.2s]
  │   └─ result: "Annual contract, 8 months remaining, early termination fee: $150"
  ├─ LLM request  [1.8s]
  │   └─ response: text output
  └─ output: "I see you have an annual contract with 8 months remaining..."
```

You can see the retry, why it happened, and how the agent recovered.

---

## OpenTelemetry (Alternative to Logfire)

If you already have an observability platform (Datadog, Honeycomb, Jaeger), PydanticAI works with any OpenTelemetry backend:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure your OTel exporter
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

# PydanticAI automatically emits OTel spans
```

---

## Monitoring in Production

Key metrics to track:

```
────────────────────────────────────────────────────────────
 Metric                  │ Alert Threshold
────────────────────────────────────────────────────────────
 Response latency (p95)  │ > 5 seconds
 Retry rate              │ > 10% of runs
 Token cost per run      │ > $0.05 average
 Tool failure rate       │ > 5%
 Output validation fails │ > 15%
────────────────────────────────────────────────────────────
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Enable Logfire                  │ logfire.configure()
Custom span                     │ with logfire.span("name", key=val):
Log info                        │ logfire.info("message", key=val)
Log warning                     │ logfire.warn("message", key=val)
Get usage from result           │ result.usage()
Token counts                    │ usage.request_tokens, .response_tokens
OTel integration                │ Standard OTel setup (auto-detected)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Rin: "I can see what's happening. But how do I know if the agent is actually good? I need to measure accuracy, compare models, track quality over time. Systematically."

Evals — measuring and improving agent quality.

---

[← Chapter 11: Testing](chapter-11-testing.md) | [Chapter 13: Evals →](chapter-13-evals.md)
