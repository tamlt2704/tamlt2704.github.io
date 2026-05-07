# Chapter 8: Multi-Agent — Delegation & Handoffs

[← Chapter 7: Streaming](chapter-07-streaming.md) | [Chapter 9: Conversation Memory →](chapter-09-conversation-memory.md)

---

## The Task

Priya: "One agent can't be an expert at everything. Billing questions need a billing specialist that knows refund policies. Technical issues need an agent trained on our docs. I need a triage agent that classifies and routes to the right specialist."

---

## The Pattern: Agent Delegation

In PydanticAI, multi-agent means one agent calls another agent as a tool. The outer agent decides when to delegate, the inner agent does the specialized work.

```
Customer Message
      │
      ▼
┌──────────┐
│  Triage  │ ← Classifies, decides who handles it
│  Agent   │
└────┬─────┘
     │ calls as tool
     ▼
┌──────────┐     ┌──────────┐
│ Billing  │     │ Technical│
│ Agent    │     │ Agent    │
└──────────┘     └──────────┘
```

---

## Building Specialist Agents

First, define the specialists:

```python
from pydantic_ai import Agent

# Billing specialist
billing_agent = Agent(
    'openai:gpt-4o',
    instructions="""
    You are a billing support specialist for Cortex.
    You know:
    - Refund policy: full refund within 30 days, pro-rated after
    - Plans: Free ($0), Pro ($29/mo), Enterprise (custom)
    - Payment methods: credit card, invoice (enterprise only)
    - Billing cycle: monthly, annual (20% discount)

    Be precise about amounts and policies. Never guess.
    """,
)

# Technical specialist
technical_agent = Agent(
    'openai:gpt-4o',
    instructions="""
    You are a technical support specialist for Cortex.
    You know:
    - Dashboard loads via /api/v2/dashboard endpoint
    - Common issues: cache invalidation, token expiry, rate limits
    - Status page: status.cortex.io
    - Supported browsers: Chrome 90+, Firefox 88+, Safari 15+

    Provide specific troubleshooting steps. Ask for error messages.
    """,
)
```

---

## The Triage Agent (Agent-as-Tool)

The triage agent uses specialists as tools:

```python
from pydantic_ai import Agent, RunContext

triage_agent = Agent(
    'openai:gpt-4o',
    instructions="""
    You are a triage agent. Your job is to:
    1. Understand the customer's issue
    2. Route to the appropriate specialist using the available tools
    3. Return the specialist's response to the customer

    Route billing questions to the billing specialist.
    Route technical issues to the technical specialist.
    For general questions, answer directly.
    """,
)


@triage_agent.tool_plain
async def ask_billing_specialist(question: str) -> str:
    """Route a billing-related question to the billing specialist.

    Use this for questions about charges, refunds, plans, invoices, or payments.
    """
    result = await billing_agent.run(question)
    return result.output


@triage_agent.tool_plain
async def ask_technical_specialist(question: str) -> str:
    """Route a technical issue to the technical specialist.

    Use this for questions about bugs, errors, performance, or how features work.
    """
    result = await technical_agent.run(question)
    return result.output
```

Usage:

```python
# Billing question → routes to billing specialist
result = await triage_agent.run("I was charged twice last month, can I get a refund?")
# Triage agent calls ask_billing_specialist(...)
# Returns the billing agent's response

# Technical question → routes to technical specialist
result = await triage_agent.run("My dashboard shows a 500 error when I click Analytics")
# Triage agent calls ask_technical_specialist(...)
# Returns the technical agent's response
```

---

## Passing Dependencies Through

When specialists need the same dependencies as the triage agent:

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, RunContext


@dataclass
class SupportDeps:
    db: DatabaseClient
    customer_id: str
    customer_plan: str


# Specialist with its own deps
billing_agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions='You are a billing specialist...',
)


@billing_agent.tool
async def get_invoices(ctx: RunContext[SupportDeps]) -> str:
    """Get the customer's recent invoices."""
    invoices = await ctx.deps.db.fetch(
        "SELECT * FROM invoices WHERE customer_id = $1 ORDER BY date DESC LIMIT 5",
        ctx.deps.customer_id,
    )
    return str(invoices)


# Triage agent passes deps to specialist
triage_agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions='Route to the appropriate specialist.',
)


@triage_agent.tool
async def ask_billing(ctx: RunContext[SupportDeps], question: str) -> str:
    """Route to billing specialist."""
    # Pass the same deps to the specialist
    result = await billing_agent.run(question, deps=ctx.deps)
    return result.output
```

---

## Structured Routing

For more control, have the triage agent return a structured classification first:

```python
from typing import Literal
from pydantic import BaseModel
from pydantic_ai import Agent


class TicketRoute(BaseModel):
    department: Literal['billing', 'technical', 'account', 'general']
    priority: Literal['low', 'medium', 'high', 'critical']
    summary: str


# Step 1: Classify
classifier = Agent(
    'openai:gpt-4o-mini',  # Fast, cheap model for classification
    output_type=TicketRoute,
    instructions='Classify the support ticket.',
)

# Step 2: Route to specialist
specialists = {
    'billing': billing_agent,
    'technical': technical_agent,
    'account': account_agent,
    'general': general_agent,
}


async def handle_ticket(message: str, deps: SupportDeps):
    # Classify
    classification = await classifier.run(message, deps=deps)
    route = classification.output

    # Route to specialist
    specialist = specialists[route.department]
    response = await specialist.run(message, deps=deps)

    return {
        "route": route,
        "response": response.output,
    }
```

This is programmatic routing — you control the flow in Python, not the LLM.

---

## Agent Delegation vs Programmatic Routing

```
────────────────────────────────────────────────────────────
 Pattern                │ When to Use
────────────────────────────────────────────────────────────
 Agent-as-tool          │ LLM decides when/whether to delegate
 (triage calls specialist as tool)
────────────────────────────────────────────────────────────
 Programmatic routing   │ You control the flow in Python
 (classify → route → specialist)
────────────────────────────────────────────────────────────
 Handoff                │ Full conversation transfer
 (triage hands off, specialist takes over)
────────────────────────────────────────────────────────────
```

Agent-as-tool: flexible, LLM decides. Good when routing isn't clear-cut.
Programmatic: predictable, you decide. Good when routing rules are well-defined.

---

## Sharing Message History

When a specialist needs the full conversation context:

```python
@triage_agent.tool
async def escalate_to_billing(ctx: RunContext[SupportDeps], reason: str) -> str:
    """Escalate to billing with full conversation context."""
    # Pass the conversation history so the specialist has context
    messages = ctx.messages  # All messages so far
    result = await billing_agent.run(
        f"Escalated from triage. Reason: {reason}",
        deps=ctx.deps,
        message_history=messages,  # Specialist sees the full conversation
    )
    return result.output
```

---

## The Complete Multi-Agent System

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext


@dataclass
class SupportDeps:
    db: DatabaseClient
    customer_id: str
    customer_plan: str


# Specialists
billing_agent = Agent('openai:gpt-4o', deps_type=SupportDeps,
                      instructions='Billing specialist. Know refund policies...')

technical_agent = Agent('openai:gpt-4o', deps_type=SupportDeps,
                        instructions='Technical specialist. Know the product...')

# Triage
triage_agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions=(
        'You are the first point of contact. '
        'Understand the issue, then route to the right specialist. '
        'For simple greetings or general questions, respond directly.'
    ),
)


@triage_agent.tool
async def billing_specialist(ctx: RunContext[SupportDeps], question: str) -> str:
    """Ask the billing specialist. Use for charges, refunds, plans, payments."""
    result = await billing_agent.run(question, deps=ctx.deps)
    return result.output


@triage_agent.tool
async def technical_specialist(ctx: RunContext[SupportDeps], question: str) -> str:
    """Ask the technical specialist. Use for bugs, errors, features, performance."""
    result = await technical_agent.run(question, deps=ctx.deps)
    return result.output


# Entry point
async def handle_message(customer_id: str, message: str):
    deps = SupportDeps(db=get_db(), customer_id=customer_id, customer_plan="pro")
    result = await triage_agent.run(message, deps=deps)
    return result.output
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Code
────────────────────────────────┼──────────────────────────────────────
Agent as tool                   │ @outer.tool: result = await inner.run(...)
Pass deps through               │ await inner.run(msg, deps=ctx.deps)
Programmatic routing            │ classify → pick agent → run
Share conversation history      │ await inner.run(msg, message_history=...)
Multiple specialists            │ One tool per specialist on triage agent
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Tomás: "The agents work for single questions. But customers have conversations — they ask a follow-up, reference something they said earlier. The agent forgets everything between messages."

Conversation memory — maintaining context across multiple turns.

---

[← Chapter 7: Streaming](chapter-07-streaming.md) | [Chapter 9: Conversation Memory →](chapter-09-conversation-memory.md)
