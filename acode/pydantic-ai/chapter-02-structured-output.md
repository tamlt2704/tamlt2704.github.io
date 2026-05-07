# Chapter 2: Structured Output — Validated Responses

[← Chapter 1: First Agent](chapter-01-first-agent.md) | [Chapter 3: Tools →](chapter-03-tools.md)

---

## The Task

Tomás: "I need the agent to classify every ticket. Category, priority, suggested department, one-line summary. As JSON. Every time. No exceptions. If it returns prose, the frontend crashes."

---

## The Problem with Unstructured Output

The old prototype:

```python
# ❌ The old way
response = llm.chat("Classify this ticket: 'I can't log in'")
# → "This appears to be a technical issue with high priority..."
# How do you extract the category? Regex? Split on colons? Prayer?
```

Sometimes the LLM returns:
- `"Category: Technical, Priority: High"` (parseable... maybe)
- `"I'd classify this as a technical issue."` (prose, not data)
- `"{'category': 'technical'}"` (looks like JSON but isn't always)

---

## output_type: The Solution

```python
from pydantic import BaseModel
from pydantic_ai import Agent


class TicketClassification(BaseModel):
    category: str
    priority: str
    department: str
    summary: str


agent = Agent(
    'openai:gpt-4o',
    output_type=TicketClassification,
    instructions='Classify customer support tickets. Be precise and consistent.',
)

result = agent.run_sync('I was charged twice for my subscription last month')
print(result.output)
# → TicketClassification(
#     category='billing',
#     priority='high',
#     department='finance',
#     summary='Customer reports duplicate subscription charge'
# )
```

`result.output` is now a `TicketClassification` instance — not a string. Fully typed. Fully validated. Your IDE autocompletes `result.output.category`.

---

## How It Works

When you set `output_type`, PydanticAI:

1. Tells the LLM to return structured data matching your schema
2. Receives the LLM's response
3. Validates it against your Pydantic model
4. If validation fails → automatically retries with the error message
5. Returns a typed, validated instance

```
LLM Response → Pydantic Validation → ✓ Valid → result.output
                                    → ✗ Invalid → Retry with error
```

No regex. No `json.loads`. No hoping.

---

## Constrained Fields with Literal and Enum

Make the LLM choose from specific values:

```python
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class TicketClassification(BaseModel):
    category: Literal['billing', 'technical', 'account', 'feature_request', 'other']
    priority: Literal['low', 'medium', 'high', 'critical']
    department: Literal['engineering', 'finance', 'customer_success', 'product']
    summary: str = Field(description='One-sentence summary of the issue')
    requires_human: bool = Field(description='Whether this needs human escalation')


agent = Agent(
    'openai:gpt-4o',
    output_type=TicketClassification,
    instructions='Classify customer support tickets accurately.',
)

result = agent.run_sync("My dashboard has been showing a loading spinner for 3 days")
print(result.output.category)     # → 'technical'
print(result.output.priority)     # → 'high'
print(result.output.department)   # → 'engineering'
print(result.output.requires_human)  # → False
```

`Literal` constrains the LLM to only those values. If it tries to return `"urgent"` instead of `"critical"`, Pydantic rejects it and PydanticAI retries.

`Field(description=...)` adds context for the LLM — it sees the description in the schema and uses it to understand what you want.

---

## Nested Models

Complex structures work naturally:

```python
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class SuggestedAction(BaseModel):
    action: str = Field(description='What to do next')
    automated: bool = Field(description='Can this be done without human intervention?')


class TicketAnalysis(BaseModel):
    classification: TicketClassification
    sentiment: Literal['positive', 'neutral', 'frustrated', 'angry']
    suggested_actions: list[SuggestedAction]
    confidence: float = Field(ge=0.0, le=1.0, description='Confidence in classification (0-1)')


agent = Agent(
    'openai:gpt-4o',
    output_type=TicketAnalysis,
    instructions='Analyze customer support tickets thoroughly.',
)

result = agent.run_sync("I've been waiting 2 weeks for a refund and nobody responds to my emails!")
print(result.output.sentiment)  # → 'angry'
print(result.output.confidence)  # → 0.95
print(result.output.suggested_actions[0].action)  # → 'Escalate to finance team immediately'
```

`Field(ge=0.0, le=1.0)` — Pydantic validates the confidence is between 0 and 1. If the LLM returns `1.5`, it retries.

---

## Multiple Output Types (Union)

Sometimes the agent needs to return different shapes depending on the input:

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.output import ToolOutput


class BillingIssue(BaseModel):
    amount_disputed: float
    transaction_date: str
    refund_eligible: bool


class TechnicalIssue(BaseModel):
    affected_feature: str
    error_message: str | None
    workaround_available: bool


agent = Agent(
    'openai:gpt-4o',
    output_type=[
        ToolOutput(BillingIssue, name='billing_issue'),
        ToolOutput(TechnicalIssue, name='technical_issue'),
    ],
    instructions='Analyze the support ticket and return the appropriate structured response.',
)

result = agent.run_sync("I was charged $49.99 on March 3rd but I cancelled last month")
print(type(result.output))  # → <class 'BillingIssue'>
print(result.output.refund_eligible)  # → True
```

The LLM chooses which output type to use based on the input. PydanticAI validates whichever one it picks.

---

## Plain Types Work Too

You don't always need a full model:

```python
# Boolean output
agent = Agent('openai:gpt-4o', output_type=bool,
              instructions='Determine if this message is spam.')
result = agent.run_sync("BUY NOW!!! CLICK HERE!!!")
print(result.output)  # → True

# Integer output
agent = Agent('openai:gpt-4o', output_type=int,
              instructions='Rate the urgency of this ticket from 1-10.')
result = agent.run_sync("My production database is down")
print(result.output)  # → 10

# List output
agent = Agent('openai:gpt-4o', output_type=list[str],
              instructions='Extract all product names mentioned.')
result = agent.run_sync("I need help with Cortex Pro and Cortex Teams")
print(result.output)  # → ['Cortex Pro', 'Cortex Teams']
```

---

## The Validation Loop

What happens when the LLM returns invalid data:

```
Attempt 1:
  LLM returns: {"priority": "urgent", "category": "billing", ...}
  Validation: ✗ "urgent" not in ['low', 'medium', 'high', 'critical']
  → Sends error back to LLM: "priority: Input should be 'low', 'medium', 'high' or 'critical'"

Attempt 2:
  LLM returns: {"priority": "high", "category": "billing", ...}
  Validation: ✓
  → Returns validated TicketClassification instance
```

This happens automatically. You don't write retry logic. PydanticAI handles it.

By default, it retries up to 1 time. You can configure this:

```python
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings

agent = Agent(
    'openai:gpt-4o',
    output_type=TicketClassification,
    retries=3,  # retry up to 3 times on validation failure
)
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Structured output               │ Agent(..., output_type=MyModel)
Constrain values                │ Literal['a', 'b', 'c']
Add field descriptions          │ Field(description='...')
Numeric constraints             │ Field(ge=0, le=1)
Nested models                   │ class Parent(BaseModel): child: Child
Multiple output types           │ output_type=[ToolOutput(A), ToolOutput(B)]
Simple types                    │ output_type=bool / int / list[str]
Configure retries               │ Agent(..., retries=3)
Access typed output             │ result.output.field_name
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Tomás: "Classification works. But the agent is guessing — it doesn't actually know the customer's order status or account details. It needs to look things up."

Tools — giving the agent functions it can call to get real data.

---

[← Chapter 1: First Agent](chapter-01-first-agent.md) | [Chapter 3: Tools →](chapter-03-tools.md)
