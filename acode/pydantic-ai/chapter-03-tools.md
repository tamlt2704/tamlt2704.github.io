# Chapter 3: Tools — Giving the Agent Superpowers

[← Chapter 2: Structured Output](chapter-02-structured-output.md) | [Chapter 4: Dependencies →](chapter-04-dependencies.md)

---

## The Task

Priya: "A customer asks 'Where's my order?' The agent says 'I'd be happy to help! Please provide your order number.' The customer already gave the order number. The agent needs to actually look it up."

---

## What Are Tools?

Tools are Python functions the LLM can call during a conversation. The LLM decides when to call them based on the user's question.

```
Customer: "What's the status of order #12345?"

Agent thinks: "I need to look up order #12345"
  → Calls tool: get_order_status(order_id="12345")
  → Gets back: {"status": "shipped", "tracking": "1Z999..."}

Agent responds: "Your order #12345 has shipped! Tracking: 1Z999..."
```

The agent doesn't guess. It calls your function, gets real data, and uses it.

---

## Your First Tool

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    instructions='You are a customer support agent. Use tools to look up real data. Never guess.',
)


@agent.tool_plain  # (1)
def get_order_status(order_id: str) -> str:
    """Look up the current status of a customer order."""  # (2)
    # In reality, this would query a database
    orders = {
        "12345": "shipped — tracking: 1Z999AA10123456784",
        "12346": "processing — estimated ship date: tomorrow",
        "12347": "delivered — left at front door",
    }
    return orders.get(order_id, "Order not found")


result = agent.run_sync("What's the status of my order #12345?")
print(result.output)
# → "Your order #12345 has shipped! Here's your tracking number: 1Z999AA10123456784"
```

1. `@agent.tool_plain` — registers a function as a tool (no dependencies needed)
2. The docstring becomes the tool's description — the LLM reads it to decide when to use the tool

---

## How Tools Work Under the Hood

```
1. You call: agent.run_sync("Where's order #12345?")

2. PydanticAI sends to LLM:
   - System prompt (instructions)
   - User message
   - Available tools: [get_order_status(order_id: str)]

3. LLM responds: "I want to call get_order_status with order_id='12345'"

4. PydanticAI:
   - Validates the arguments (order_id must be str ✓)
   - Calls your function: get_order_status("12345")
   - Sends the result back to the LLM

5. LLM generates final response using the tool result

6. PydanticAI returns result.output
```

The LLM never calls your function directly. PydanticAI mediates — validating arguments, calling the function, and passing results back.

---

## Tool Arguments Are Validated

The LLM sees your function's type hints and uses them:

```python
@agent.tool_plain
def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """Search the help center for articles matching the query.

    Args:
        query: The search terms to look for.
        max_results: Maximum number of results to return (1-10).
    """
    # PydanticAI validates: query must be str, max_results must be int
    articles = [
        {"title": "How to reset password", "url": "/help/reset-password"},
        {"title": "Two-factor authentication", "url": "/help/2fa"},
    ]
    return str(articles[:max_results])
```

If the LLM tries to pass `max_results="five"`, PydanticAI catches it and asks the LLM to fix the arguments.

---

## Multiple Tools

An agent can have many tools. The LLM chooses which to call (or none, or multiple):

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    instructions='You are a customer support agent for Cortex. Use tools to look up real information.',
)


@agent.tool_plain
def get_order_status(order_id: str) -> str:
    """Look up the current status of a customer order by order ID."""
    orders = {"12345": "shipped", "12346": "processing"}
    return orders.get(order_id, "not found")


@agent.tool_plain
def get_account_info(email: str) -> str:
    """Look up account details by customer email address."""
    accounts = {
        "alice@example.com": "Plan: Pro, Status: Active, Since: 2023-01",
        "bob@example.com": "Plan: Free, Status: Active, Since: 2024-06",
    }
    return accounts.get(email, "Account not found")


@agent.tool_plain
def check_service_status() -> str:
    """Check if any Cortex services are currently experiencing issues."""
    return "All systems operational. No incidents reported."


# The LLM decides which tool(s) to call based on the question
result = agent.run_sync("Is there an outage? My dashboard won't load.")
# → Agent calls check_service_status(), then responds based on the result
```

---

## @agent.tool vs @agent.tool_plain

Two decorators for tools:

```python
# tool_plain — no access to run context (simple functions)
@agent.tool_plain
def get_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().isoformat()


# tool — gets RunContext as first argument (access to dependencies)
@agent.tool
def get_user_orders(ctx: RunContext[MyDeps], user_id: str) -> str:
    """Look up all orders for a user."""
    # ctx.deps gives you access to database connections, API clients, etc.
    return ctx.deps.db.query(f"SELECT * FROM orders WHERE user_id = '{user_id}'")
```

Use `@agent.tool_plain` when the function is self-contained.
Use `@agent.tool` when you need dependencies (database, HTTP client, etc.) — covered in Chapter 4.

---

## Tool Return Types

Tools should return strings (the LLM reads the result as text):

```python
@agent.tool_plain
def get_pricing() -> str:
    """Get current pricing information for all plans."""
    pricing = {
        "free": "$0/month — 1 user, 1GB storage",
        "pro": "$29/month — 10 users, 100GB storage",
        "enterprise": "Custom pricing — unlimited users",
    }
    # Return as formatted string for the LLM to read
    return "\n".join(f"{plan}: {details}" for plan, details in pricing.items())
```

You can return other types too — PydanticAI will serialize them. But strings are clearest for the LLM.

---

## Async Tools

Tools can be async (preferred for I/O operations):

```python
import httpx
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='Help customers with shipping questions.')


@agent.tool_plain
async def track_package(tracking_number: str) -> str:
    """Track a package using its tracking number."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.shipping.com/track/{tracking_number}"
        )
        if response.status_code == 200:
            data = response.json()
            return f"Status: {data['status']}, Location: {data['location']}"
        return "Tracking information not available"
```

If you use `agent.run_sync()`, async tools still work — PydanticAI handles the event loop.

---

## The LLM Can Call Multiple Tools

```python
result = agent.run_sync(
    "I'm alice@example.com. What's my account status and where's order #12345?"
)
# The LLM will:
# 1. Call get_account_info("alice@example.com")
# 2. Call get_order_status("12345")
# 3. Combine both results into a single response
```

The LLM can call tools in sequence or parallel, depending on the model's capabilities.

---

## Seeing Tool Calls in the Message History

```python
result = agent.run_sync("What's the status of order #12345?")

for msg in result.all_messages():
    print(f"{msg.kind}: {msg}")
```

You'll see:
1. `request` — system prompt + user message + tool definitions
2. `response` — LLM's decision to call `get_order_status`
3. `request` — tool result sent back
4. `response` — LLM's final answer

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Simple tool (no deps)           │ @agent.tool_plain
Tool with dependencies          │ @agent.tool (gets RunContext)
Tool description                │ Function docstring
Tool arguments                  │ Function parameters with type hints
Async tool                      │ async def my_tool(...) -> str
Multiple tools                  │ Decorate multiple functions
See tool calls                  │ result.all_messages()
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "The tools work, but you're hardcoding data in dictionaries. In production, tools need a database connection, an HTTP client, API keys. How do you pass those in without globals?"

Dependencies — PydanticAI's dependency injection system.

---

[← Chapter 2: Structured Output](chapter-02-structured-output.md) | [Chapter 4: Dependencies →](chapter-04-dependencies.md)
