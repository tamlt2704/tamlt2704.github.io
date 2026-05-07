# Chapter 5: Dynamic Prompts — Context-Aware Instructions

[← Chapter 4: Dependencies](chapter-04-dependencies.md) | [Chapter 6: Validation & Retry →](chapter-06-validation-retry.md)

---

## The Task

Priya: "Enterprise customers get a different tone than free-tier users. The agent should know the customer's plan, their ticket history, and the current time. Static instructions can't do this."

---

## Static vs Dynamic Instructions

Static instructions are set once:

```python
agent = Agent(
    'openai:gpt-4o',
    instructions='You are a support agent. Be helpful.',  # Same for everyone
)
```

Dynamic instructions are computed at runtime using dependencies:

```python
@agent.system_prompt
async def build_context(ctx: RunContext[SupportDeps]) -> str:
    return f"""
    Customer: {ctx.deps.customer_name}
    Plan: {ctx.deps.customer_plan}
    Account age: {ctx.deps.account_age_days} days
    Open tickets: {ctx.deps.open_ticket_count}
    """
```

---

## @agent.system_prompt

Decorate a function to add dynamic content to the system prompt:

```python
from dataclasses import dataclass
from datetime import datetime
from pydantic_ai import Agent, RunContext


@dataclass
class SupportDeps:
    customer_name: str
    customer_plan: str
    customer_since: str
    vip: bool


agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions='You are a customer support agent for Cortex.',  # (1)
)


@agent.system_prompt  # (2)
def add_customer_context(ctx: RunContext[SupportDeps]) -> str:
    return f"""
Current customer information:
- Name: {ctx.deps.customer_name}
- Plan: {ctx.deps.customer_plan}
- Customer since: {ctx.deps.customer_since}
- VIP status: {ctx.deps.vip}
"""


@agent.system_prompt  # (3)
def add_tone_guidelines(ctx: RunContext[SupportDeps]) -> str:
    if ctx.deps.vip:
        return (
            "This is a VIP customer. Be extra attentive. "
            "Offer proactive solutions. Use their name frequently."
        )
    return "Be friendly and professional. Keep responses concise."


@agent.system_prompt  # (4)
def add_time_context() -> str:
    hour = datetime.now().hour
    if hour < 9 or hour > 17:
        return "Note: It's outside business hours. If escalation is needed, set expectations for next business day."
    return "Business hours — human agents are available for escalation if needed."
```

1. Static `instructions` — always included first
2. First dynamic prompt — adds customer context
3. Second dynamic prompt — adjusts tone based on VIP status
4. Third dynamic prompt — no `ctx` needed (just uses current time)

All system prompt functions are called and their results concatenated into the final system prompt.

---

## How the Final Prompt Looks

When the agent runs, PydanticAI assembles:

```
[System Prompt]
You are a customer support agent for Cortex.

Current customer information:
- Name: Alice Chen
- Plan: Enterprise
- Customer since: 2022-03-15
- VIP status: True

This is a VIP customer. Be extra attentive. Offer proactive solutions. Use their name frequently.

Business hours — human agents are available for escalation if needed.

[User Message]
My dashboard has been slow for the past week.
```

The LLM sees all of this as one system prompt. It naturally adapts its behavior.

---

## Multiple @system_prompt Decorators

You can have as many as you want. They're all called and concatenated:

```python
@agent.system_prompt
def base_rules() -> str:
    return """
    Rules:
    - Never reveal internal system details
    - Never make up information — use tools
    - If you can't help, offer human escalation
    """


@agent.system_prompt
async def load_faq(ctx: RunContext[SupportDeps]) -> str:
    # Load relevant FAQ entries from the database
    faqs = await ctx.deps.db.fetch(
        "SELECT question, answer FROM faqs WHERE plan = $1 LIMIT 5",
        ctx.deps.customer_plan,
    )
    if faqs:
        faq_text = "\n".join(f"Q: {f['question']}\nA: {f['answer']}" for f in faqs)
        return f"Relevant FAQ entries for this customer's plan:\n{faq_text}"
    return ""


@agent.system_prompt
async def load_recent_tickets(ctx: RunContext[SupportDeps]) -> str:
    tickets = await ctx.deps.db.fetch(
        "SELECT subject, status FROM tickets WHERE customer_id = $1 ORDER BY created_at DESC LIMIT 3",
        ctx.deps.customer_id,
    )
    if tickets:
        history = "\n".join(f"- {t['subject']} ({t['status']})" for t in tickets)
        return f"Customer's recent tickets:\n{history}"
    return ""
```

---

## Combining Static + Dynamic

The `instructions` parameter and `@agent.system_prompt` work together:

```python
agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions=[
        'You are a customer support agent for Cortex.',
        'Always be professional and empathetic.',
        'Use tools to look up real data — never guess.',
    ],
)

# Dynamic prompts ADD to the static instructions
@agent.system_prompt
def customer_context(ctx: RunContext[SupportDeps]) -> str:
    return f"Customer: {ctx.deps.customer_name} ({ctx.deps.customer_plan} plan)"
```

Order in the final prompt:
1. Static `instructions` (always first)
2. Dynamic `@system_prompt` functions (in decoration order)

---

## Async System Prompts

System prompts can be async — useful for fetching context from databases or APIs:

```python
@agent.system_prompt
async def load_product_knowledge(ctx: RunContext[SupportDeps]) -> str:
    """Load relevant product docs based on the customer's plan."""
    response = await ctx.deps.http_client.get(
        f"https://docs.cortex.io/api/context?plan={ctx.deps.customer_plan}"
    )
    if response.status_code == 200:
        return f"Product context:\n{response.text}"
    return ""
```

---

## Template Strings (Alternative Syntax)

For simpler cases, PydanticAI supports template strings that reference dependency fields directly:

```python
from pydantic_ai import Agent
from pydantic_ai.common_tools import TemplateStr

agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions=TemplateStr(
        'You are a support agent helping {{customer_name}} '
        'who is on the {{customer_plan}} plan.'
    ),
)
```

`{{customer_name}}` is resolved from `deps.customer_name` at runtime. Useful for simple interpolation without writing a full function.

---

## The Pattern: Layered Context

Priya's architecture for the system prompt:

```
Layer 1: Identity (static)
  "You are a Cortex support agent..."

Layer 2: Rules (static)
  "Never fabricate. Use tools. Escalate when unsure."

Layer 3: Customer context (dynamic, from deps)
  "Customer: Alice, Enterprise plan, VIP"

Layer 4: Behavioral adjustment (dynamic, from deps)
  "VIP tone: extra attentive, proactive"

Layer 5: Situational context (dynamic, from time/state)
  "Outside business hours. Set expectations."

Layer 6: Knowledge (dynamic, from database)
  "Relevant FAQs: ..."
```

Each layer is a separate `@system_prompt` function. Easy to test individually. Easy to add or remove.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Static instructions             │ Agent(..., instructions='...')
Dynamic prompt (with deps)      │ @agent.system_prompt + ctx: RunContext[Deps]
Dynamic prompt (no deps)        │ @agent.system_prompt + def func() -> str
Async dynamic prompt            │ @agent.system_prompt + async def func(ctx)
Multiple prompts                │ Decorate multiple functions
Template strings                │ instructions=TemplateStr('Hello {{name}}')
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Rin: "The agent sometimes returns confidence scores above 1.0. And yesterday it classified a billing issue as 'urgnet' — a typo that broke our routing. We need validation that catches these before they reach the frontend."

Output validation and automatic retry — making the agent self-correct.

---

[← Chapter 4: Dependencies](chapter-04-dependencies.md) | [Chapter 6: Validation & Retry →](chapter-06-validation-retry.md)
