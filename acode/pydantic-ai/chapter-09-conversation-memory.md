# Chapter 9: Conversation Memory — Multi-Turn Chat

[← Chapter 8: Multi-Agent](chapter-08-multi-agent.md) | [Chapter 10: MCP & Toolsets →](chapter-10-mcp-toolsets.md)

---

## The Task

Tomás: "Customer says 'What's my order status?' Agent responds. Then customer says 'Can you cancel it?' Agent says 'Cancel what?' It forgot the entire previous exchange. We need memory."

---

## The Problem: Stateless by Default

Each `agent.run()` call is independent. The agent has no memory of previous calls:

```python
result1 = await agent.run("What's the status of order #12345?")
# → "Order #12345 has shipped!"

result2 = await agent.run("Can you cancel it?")
# → "Cancel what? I don't see any order reference."
# The agent doesn't know what "it" refers to
```

---

## The Solution: message_history

Pass the previous conversation back to the agent:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='You are a support agent.')

# First turn
result1 = await agent.run("What's the status of order #12345?")
print(result1.output)
# → "Order #12345 has shipped! It's arriving tomorrow."

# Second turn — pass message history
result2 = await agent.run(
    "Can you cancel it?",
    message_history=result1.all_messages(),  # ← Previous conversation
)
print(result2.output)
# → "I'm sorry, order #12345 has already shipped and can't be cancelled.
#    Would you like to initiate a return instead?"
```

`result1.all_messages()` returns the full conversation (system prompt, user message, tool calls, assistant response). Passing it as `message_history` gives the agent context.

---

## Building a Conversation Loop

```python
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

agent = Agent('openai:gpt-4o', instructions='You are a helpful support agent.')


async def chat_session():
    history: list[ModelMessage] = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ('quit', 'exit'):
            break

        result = await agent.run(user_input, message_history=history)
        print(f"Agent: {result.output}")

        # Update history with the full conversation so far
        history = result.all_messages()
```

Each turn:
1. Pass the accumulated history
2. Get the response
3. Update history with `result.all_messages()` (includes the new exchange)

---

## Conversation Memory in a Web App

In a real application, you store conversation history per session:

```python
from fastapi import FastAPI
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

app = FastAPI()
agent = Agent('openai:gpt-4o', deps_type=SupportDeps, instructions='...')

# In production, use Redis or a database — not a dict
conversations: dict[str, list[ModelMessage]] = {}


@app.post("/chat/{session_id}")
async def chat(session_id: str, message: str, customer_id: str):
    # Load conversation history
    history = conversations.get(session_id, [])

    # Build deps
    deps = await build_deps(customer_id)

    # Run with history
    result = await agent.run(message, deps=deps, message_history=history)

    # Save updated history
    conversations[session_id] = result.all_messages()

    return {"response": result.output}
```

---

## Streaming with History

Streaming works with message history too:

```python
async def stream_with_memory(message: str, history: list[ModelMessage]):
    async with agent.run_stream(message, message_history=history) as stream:
        async for chunk in stream.stream_text(delta=True):
            yield chunk

    # Update history after stream completes
    return stream.result().all_messages()
```

---

## What's in the Message History?

```python
result = await agent.run("What's order #12345?")

for msg in result.all_messages():
    print(f"Kind: {msg.kind}")
    print(f"Parts: {msg.parts}")
    print("---")
```

You'll see messages like:
- `kind='request'` — contains system prompt, user message, tool definitions
- `kind='response'` — contains the LLM's response (text or tool calls)
- `kind='request'` — contains tool results (if tools were called)
- `kind='response'` — contains the final text response

---

## Trimming History (Token Management)

Long conversations accumulate tokens. You'll hit context limits. Strategies:

```python
from pydantic_ai.messages import ModelMessage


def trim_history(history: list[ModelMessage], max_messages: int = 20) -> list[ModelMessage]:
    """Keep the most recent messages, always preserving the first (system prompt)."""
    if len(history) <= max_messages:
        return history
    # Keep first message (system prompt context) + last N messages
    return history[:1] + history[-(max_messages - 1):]


# Use before each run
result = await agent.run(
    message,
    message_history=trim_history(history),
)
```

More sophisticated approaches:
- Summarize old messages into a condensed system prompt
- Keep only messages with tool calls (they contain key facts)
- Use token counting to stay within model limits

---

## Serializing History (Persistence)

For storing conversations in a database:

```python
import json
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

# Serialize to JSON
history_json = ModelMessagesTypeAdapter.dump_json(history)
# Store in database as bytes/string

# Deserialize from JSON
history = ModelMessagesTypeAdapter.validate_json(history_json)
# Pass back to agent.run(message_history=history)
```

`ModelMessagesTypeAdapter` handles serialization of all message types, including tool calls and their results.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Pass history                    │ agent.run(msg, message_history=history)
Get history from result         │ result.all_messages()
Build conversation loop         │ history = result.all_messages() each turn
Serialize history               │ ModelMessagesTypeAdapter.dump_json(history)
Deserialize history             │ ModelMessagesTypeAdapter.validate_json(data)
Trim history                    │ Keep first + last N messages
Stream with history             │ agent.run_stream(msg, message_history=...)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "We need the agent to access our knowledge base, search our docs, and use external APIs — without writing a custom tool for each one. MCP gives us a standard protocol for connecting tools."

MCP (Model Context Protocol) and toolsets — plugging in external capabilities.

---

[← Chapter 8: Multi-Agent](chapter-08-multi-agent.md) | [Chapter 10: MCP & Toolsets →](chapter-10-mcp-toolsets.md)
