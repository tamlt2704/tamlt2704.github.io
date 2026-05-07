# Chapter 7: Streaming — Real-Time Responses

[← Chapter 6: Validation & Retry](chapter-06-validation-retry.md) | [Chapter 8: Multi-Agent →](chapter-08-multi-agent.md)

---

## The Task

Tomás: "The user sends a message and stares at a loading spinner for 4 seconds. Then the entire response appears at once. It feels broken. I need the response to stream in word by word — like ChatGPT does."

---

## run_stream: Streaming Text

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='You are a helpful support agent.')


async def stream_response(message: str):
    async with agent.run_stream(message) as stream:
        async for chunk in stream.stream_text():
            print(chunk, end='', flush=True)
    print()  # newline at the end
```

`stream.stream_text()` yields text chunks as the LLM generates them. Each chunk is a few words or a sentence fragment.

---

## Streaming in a FastAPI Endpoint

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic_ai import Agent

app = FastAPI()
agent = Agent('openai:gpt-4o', instructions='You are a helpful support agent.')


@app.post("/chat")
async def chat(message: str):
    async def generate():
        async with agent.run_stream(message) as stream:
            async for chunk in stream.stream_text():
                yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

The frontend receives text as it's generated — no waiting for the full response.

---

## Streaming with Delta vs Full Text

PydanticAI offers two streaming modes:

```python
async with agent.run_stream(message) as stream:
    # Option 1: Deltas (each chunk is NEW text only)
    async for delta in stream.stream_text(delta=True):
        print(delta, end='')  # "Hello" → " world" → "!" (incremental)

    # Option 2: Full text so far (each chunk is the COMPLETE text up to that point)
    async for text in stream.stream_text(delta=False):
        print(text)  # "Hello" → "Hello world" → "Hello world!" (cumulative)
```

Use `delta=True` (default) for chat UIs where you append text.
Use `delta=False` when you need the full text at each step (e.g., for a preview).

---

## Streaming Structured Output

You can stream structured output too — get partial results as they're generated:

```python
from pydantic import BaseModel
from pydantic_ai import Agent


class SupportResponse(BaseModel):
    answer: str
    category: str
    confidence: float


agent = Agent(
    'openai:gpt-4o',
    output_type=SupportResponse,
    instructions='Classify and respond to support tickets.',
)


async def stream_structured(message: str):
    async with agent.run_stream(message) as stream:
        async for partial in stream.stream_output():
            # partial is a partially-filled SupportResponse
            # Fields appear as the LLM generates them
            print(f"So far: {partial}")
            # → SupportResponse(answer='Your order...', category=None, confidence=None)
            # → SupportResponse(answer='Your order has shipped...', category='shipping', confidence=None)
            # → SupportResponse(answer='Your order has shipped...', category='shipping', confidence=0.95)

    # Final validated result
    result = stream.result()
    print(f"Final: {result.output}")
```

---

## Streaming with Tool Calls

When the agent calls tools during streaming, the stream pauses while the tool executes, then resumes:

```python
agent = Agent('openai:gpt-4o', instructions='Look up orders when asked.')


@agent.tool_plain
def get_order(order_id: str) -> str:
    """Look up order status."""
    return "Order #12345: Shipped, arriving tomorrow"


async def stream_with_tools(message: str):
    async with agent.run_stream(message) as stream:
        async for chunk in stream.stream_text(delta=True):
            print(chunk, end='')
            # Stream pauses during tool call, resumes after
```

The user sees:
1. Nothing (agent is deciding to call a tool)
2. Text starts flowing (agent got tool result, now generating response)

---

## Synchronous Streaming

For scripts and testing, there's a sync version:

```python
with agent.run_stream_sync(message) as stream:
    for chunk in stream.stream_text_sync():
        print(chunk, end='')
```

---

## Getting the Final Result After Streaming

After the stream completes, you can access the full result:

```python
async with agent.run_stream(message) as stream:
    async for chunk in stream.stream_text():
        send_to_frontend(chunk)

# After the context manager exits, get the final result
result = stream.result()
print(result.output)        # Full text or structured output
print(result.usage())       # Token usage
print(result.all_messages())  # Full message history
```

---

## Server-Sent Events (SSE) Pattern

For production chat UIs, SSE is the standard pattern:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()


@app.post("/chat/stream")
async def chat_stream(message: str, customer_id: str):
    deps = await build_deps(customer_id)

    async def event_stream():
        async with agent.run_stream(message, deps=deps) as stream:
            async for chunk in stream.stream_text(delta=True):
                # SSE format
                yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"

        # Send final metadata
        result = stream.result()
        usage = result.usage()
        yield f"data: {json.dumps({'type': 'done', 'tokens': usage.total_tokens})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Stream text (async)             │ async with agent.run_stream(msg) as s
Stream deltas                   │ async for chunk in s.stream_text(delta=True)
Stream full text                │ async for text in s.stream_text(delta=False)
Stream structured output        │ async for partial in s.stream_output()
Sync streaming                  │ with agent.run_stream_sync(msg) as s
Get final result                │ stream.result()
Stream with deps                │ agent.run_stream(msg, deps=deps)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "One agent can't do everything. Billing questions need a billing specialist. Technical issues need an engineer-trained agent. I need a triage agent that routes to specialists."

Multi-agent patterns — delegation, handoffs, and agent-as-tool.

---

[← Chapter 6: Validation & Retry](chapter-06-validation-retry.md) | [Chapter 8: Multi-Agent →](chapter-08-multi-agent.md)
