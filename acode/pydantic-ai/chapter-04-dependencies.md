# Chapter 4: Dependencies — Injecting the Real World

[← Chapter 3: Tools](chapter-03-tools.md) | [Chapter 5: Dynamic Prompts →](chapter-05-dynamic-prompts.md)

---

## The Task

Priya: "Your tools have hardcoded dictionaries. In production, they need a database connection, an HTTP client for our internal APIs, and the customer's session info. And it needs to be testable — I don't want tests hitting the real database."

---

## The Problem with Globals

```python
# ❌ The old way — globals everywhere
import database  # global connection

@agent.tool_plain
def get_order(order_id: str) -> str:
    return database.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
    # How do you test this without a real database?
    # How do you use a different connection per request?
```

---

## Dependencies: The PydanticAI Way

Dependencies are objects you pass into the agent at runtime. Tools and prompts access them through `RunContext`.

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext


@dataclass
class SupportDeps:
    db: DatabaseClient
    customer_id: str
    customer_name: str


agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,  # ← declare the dependency type
    instructions='You are a support agent. Use tools to look up real data.',
)


@agent.tool
async def get_orders(ctx: RunContext[SupportDeps]) -> str:
    """Get all orders for the current customer."""
    orders = await ctx.deps.db.fetch(
        "SELECT id, status, total FROM orders WHERE customer_id = $1",
        ctx.deps.customer_id,
    )
    return str(orders)


@agent.tool
async def get_subscription(ctx: RunContext[SupportDeps]) -> str:
    """Get the current customer's subscription details."""
    sub = await ctx.deps.db.fetch_one(
        "SELECT plan, status, renewal_date FROM subscriptions WHERE customer_id = $1",
        ctx.deps.customer_id,
    )
    return str(sub)
```

Running it:

```python
async def handle_ticket(customer_id: str, message: str):
    async with get_db_pool() as db:
        deps = SupportDeps(
            db=db,
            customer_id=customer_id,
            customer_name="Alice",
        )
        result = await agent.run(message, deps=deps)
        return result.output
```

---

## How It Works

```
1. Define a deps type (dataclass, plain class, or any Python type)
2. Pass deps_type=MyDeps to the Agent
3. Tools use @agent.tool and receive RunContext[MyDeps] as first arg
4. At runtime, pass deps=MyDeps(...) to agent.run()
5. Tools access deps via ctx.deps
```

The key insight: `RunContext[SupportDeps]` is generic. If you get the type wrong, your type checker catches it:

```python
@agent.tool
async def bad_tool(ctx: RunContext[int]) -> str:  # ← Wrong type!
    # Type checker: "Agent expects SupportDeps, got int"
    ...
```

---

## A Complete Example

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, RunContext


@dataclass
class SupportDeps:
    http_client: httpx.AsyncClient
    api_key: str
    customer_email: str


agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions='You are a helpful support agent for Cortex.',
)


@agent.tool
async def get_account(ctx: RunContext[SupportDeps]) -> str:
    """Look up the current customer's account information."""
    response = await ctx.deps.http_client.get(
        f"https://api.cortex.io/accounts/{ctx.deps.customer_email}",
        headers={"Authorization": f"Bearer {ctx.deps.api_key}"},
    )
    response.raise_for_status()
    return response.text


@agent.tool
async def get_invoices(ctx: RunContext[SupportDeps]) -> str:
    """Get recent invoices for the current customer."""
    response = await ctx.deps.http_client.get(
        f"https://api.cortex.io/invoices?email={ctx.deps.customer_email}",
        headers={"Authorization": f"Bearer {ctx.deps.api_key}"},
    )
    response.raise_for_status()
    return response.text


# Running in production (e.g., inside a FastAPI endpoint)
async def handle_support_request(email: str, message: str):
    async with httpx.AsyncClient() as client:
        deps = SupportDeps(
            http_client=client,
            api_key="sk-cortex-...",
            customer_email=email,
        )
        result = await agent.run(message, deps=deps)
        return result.output
```

---

## Why This Matters for Testing

Without dependencies, you'd mock globals or patch modules. With dependencies, you just pass different objects:

```python
# test_support.py
from unittest.mock import AsyncMock
from pydantic_ai.models.test import TestModel


async def test_order_lookup():
    # Create mock dependencies
    mock_db = AsyncMock()
    mock_db.fetch.return_value = [
        {"id": "12345", "status": "shipped", "total": 49.99}
    ]

    deps = SupportDeps(
        db=mock_db,
        customer_id="cust_001",
        customer_name="Test User",
    )

    # Use TestModel — no real LLM calls
    with agent.override(model=TestModel()):
        result = await agent.run("Where's my order?", deps=deps)
        # TestModel returns a predefined response
```

No real database. No real LLM. Fast, deterministic tests.

---

## Dependencies in System Prompts

Dependencies aren't just for tools — system prompts can use them too:

```python
@agent.system_prompt
async def personalized_prompt(ctx: RunContext[SupportDeps]) -> str:
    return f"The customer's name is {ctx.deps.customer_name}. Address them by name."
```

Now the agent knows the customer's name without the LLM needing to ask.

---

## Multiple Dependencies with Dataclasses

Dataclasses are the recommended container:

```python
@dataclass
class SupportDeps:
    # Connections
    db: DatabasePool
    http_client: httpx.AsyncClient
    redis: RedisClient

    # Context
    customer_id: str
    customer_email: str
    customer_plan: str

    # Config
    api_key: str
    environment: str  # 'production' or 'staging'
```

Everything the agent needs in one typed container.

---

## Overriding Dependencies for Testing

PydanticAI provides an `override` context manager:

```python
# In your application code
async def app_endpoint(message: str):
    deps = SupportDeps(db=real_db, customer_id="real_customer", ...)
    result = await agent.run(message, deps=deps)
    return result.output


# In your tests
async def test_app_endpoint():
    test_deps = SupportDeps(db=mock_db, customer_id="test_customer", ...)

    with agent.override(deps=test_deps):
        # Even though app_endpoint creates its own deps,
        # the override takes precedence
        response = await app_endpoint("Help me")
```

`agent.override(deps=...)` replaces dependencies for all runs within the block — even if the application code passes different deps. This lets you test deep call stacks without changing application code.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Define deps type                │ Agent(..., deps_type=MyDeps)
Access deps in tool             │ @agent.tool + ctx: RunContext[MyDeps]
Access deps in prompt           │ @agent.system_prompt + ctx: RunContext[MyDeps]
Pass deps at runtime            │ agent.run(msg, deps=MyDeps(...))
Override for testing            │ with agent.override(deps=test_deps):
Deps container                  │ @dataclass class MyDeps: ...
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "The agent knows the customer's name from deps. But I want the system prompt to change based on the customer's plan, their history, the time of day. Static instructions aren't enough."

Dynamic system prompts — building context-aware instructions.

---

[← Chapter 3: Tools](chapter-03-tools.md) | [Chapter 5: Dynamic Prompts →](chapter-05-dynamic-prompts.md)
