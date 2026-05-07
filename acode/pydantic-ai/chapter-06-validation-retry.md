# Chapter 6: Validation & Retry — Self-Correcting Agents

[← Chapter 5: Dynamic Prompts](chapter-05-dynamic-prompts.md) | [Chapter 7: Streaming →](chapter-07-streaming.md)

---

## The Task

Rin: "The agent returned a confidence score of 1.7 yesterday. And it classified a ticket as 'urgnet'. Pydantic caught the typo because we used `Literal`, but the confidence field was just a `float` with no bounds. We need custom validation that goes beyond schema."

---

## Pydantic Validation (Built-in)

The first line of defense is your Pydantic model:

```python
from typing import Literal
from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    category: Literal['billing', 'technical', 'account', 'feature_request']
    priority: Literal['low', 'medium', 'high', 'critical']
    confidence: float = Field(ge=0.0, le=1.0)  # ← Pydantic enforces 0-1
    summary: str = Field(min_length=10, max_length=200)  # ← Length constraints
```

If the LLM returns `confidence: 1.7`, Pydantic rejects it. PydanticAI sends the validation error back to the LLM and retries. The LLM sees "confidence must be ≤ 1.0" and corrects itself.

This is automatic. No code needed beyond the model definition.

---

## @agent.output_validator: Custom Logic

For validation that goes beyond schema — business rules, cross-field checks, external lookups:

```python
from pydantic_ai import Agent, RunContext, ModelRetry


agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    output_type=TicketClassification,
    instructions='Classify support tickets accurately.',
)


@agent.output_validator
def validate_classification(ctx: RunContext[SupportDeps], output: TicketClassification) -> TicketClassification:
    # Rule: billing issues from enterprise customers are always high priority
    if output.category == 'billing' and ctx.deps.customer_plan == 'enterprise':
        if output.priority == 'low':
            raise ModelRetry(
                "Enterprise billing issues should be at least 'medium' priority. "
                "Please re-classify with appropriate priority."
            )

    # Rule: confidence below 0.5 should suggest human review
    if output.confidence < 0.5:
        raise ModelRetry(
            "Low confidence classification. Please reconsider and provide "
            "a more confident classification, or set requires_human=True."
        )

    return output  # ← Return the output if valid
```

---

## How ModelRetry Works

```
1. LLM returns: {"category": "billing", "priority": "low", "confidence": 0.8}
2. Pydantic validates schema: ✓
3. output_validator runs:
   - Enterprise customer + billing + low priority → INVALID
   - Raises ModelRetry("Enterprise billing issues should be at least 'medium'...")
4. PydanticAI sends the error message back to the LLM
5. LLM retries: {"category": "billing", "priority": "high", "confidence": 0.85}
6. Pydantic validates: ✓
7. output_validator runs: ✓
8. Returns validated TicketClassification
```

`ModelRetry` is special — it doesn't crash your program. It tells PydanticAI to ask the LLM to try again with the error message as guidance.

---

## Multiple Validators

You can have multiple output validators. They run in order:

```python
@agent.output_validator
def check_business_rules(ctx: RunContext[SupportDeps], output: TicketClassification) -> TicketClassification:
    """Enforce business rules."""
    if output.category == 'technical' and output.priority == 'critical':
        # Critical technical issues must suggest human escalation
        if not output.requires_human:
            raise ModelRetry(
                "Critical technical issues require human escalation. "
                "Set requires_human=True."
            )
    return output


@agent.output_validator
async def check_not_duplicate(ctx: RunContext[SupportDeps], output: TicketClassification) -> TicketClassification:
    """Check if this looks like a duplicate of a recent ticket."""
    recent = await ctx.deps.db.fetch(
        "SELECT summary FROM tickets WHERE customer_id = $1 AND created_at > now() - interval '1 hour'",
        ctx.deps.customer_id,
    )
    for ticket in recent:
        if ticket['summary'].lower() == output.summary.lower():
            raise ModelRetry(
                f"This looks like a duplicate of a recent ticket: '{ticket['summary']}'. "
                "Please provide a more specific summary that distinguishes this issue."
            )
    return output
```

---

## Configuring Retries

```python
agent = Agent(
    'openai:gpt-4o',
    output_type=TicketClassification,
    retries=3,  # ← Max retry attempts (default is 1)
)
```

The retry count covers both:
- Pydantic schema validation failures
- `ModelRetry` raised in output validators

If all retries are exhausted, PydanticAI raises an exception.

---

## Retry in Tools

Tools can also trigger retries using `ModelRetry`:

```python
from pydantic_ai import Agent, RunContext, ModelRetry


@agent.tool
async def get_order(ctx: RunContext[SupportDeps], order_id: str) -> str:
    """Look up an order by ID. The ID must be numeric."""
    if not order_id.isdigit():
        raise ModelRetry(
            f"Invalid order ID '{order_id}'. Order IDs are numeric (e.g., '12345'). "
            "Please extract the correct order ID from the customer's message."
        )

    order = await ctx.deps.db.fetch_one(
        "SELECT * FROM orders WHERE id = $1", order_id
    )
    if not order:
        raise ModelRetry(
            f"Order '{order_id}' not found. Please confirm the order ID with the customer."
        )
    return str(order)
```

When a tool raises `ModelRetry`, the LLM gets the error message and can:
- Try different arguments
- Ask the user for clarification
- Use a different tool

---

## The Validation Stack

```
┌─────────────────────────────────────────┐
│ Layer 1: Type hints                      │
│   output_type=bool → must be boolean     │
├─────────────────────────────────────────┤
│ Layer 2: Pydantic schema                 │
│   Field(ge=0, le=1) → range check       │
│   Literal['a','b'] → enum check          │
│   min_length, max_length → string length │
├─────────────────────────────────────────┤
│ Layer 3: Pydantic validators             │
│   @field_validator, @model_validator     │
│   Cross-field checks within the model    │
├─────────────────────────────────────────┤
│ Layer 4: @agent.output_validator         │
│   Business rules, external checks        │
│   Access to dependencies (ctx.deps)      │
│   Can be async (database lookups)        │
└─────────────────────────────────────────┘
```

Each layer catches different kinds of errors. Together, they make it nearly impossible for bad data to reach your application.

---

## Real Example: The Complete Validation Pipeline

```python
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from pydantic_ai import Agent, RunContext, ModelRetry


class SupportResponse(BaseModel):
    answer: str = Field(min_length=20, max_length=500)
    category: Literal['billing', 'technical', 'account', 'general']
    confidence: float = Field(ge=0.0, le=1.0)
    sources_used: list[str] = Field(description='Which tools/sources informed this answer')
    needs_followup: bool

    @model_validator(mode='after')
    def check_sources(self):
        """If confidence is high, sources should be provided."""
        if self.confidence > 0.8 and not self.sources_used:
            raise ValueError('High confidence answers must cite sources')
        return self


agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    output_type=SupportResponse,
    retries=3,
)


@agent.output_validator
def validate_no_hallucination(ctx: RunContext[SupportDeps], output: SupportResponse) -> SupportResponse:
    """Ensure the agent isn't making up features."""
    forbidden_phrases = ['unlimited storage', 'free upgrade', '100% uptime guarantee']
    for phrase in forbidden_phrases:
        if phrase.lower() in output.answer.lower():
            raise ModelRetry(
                f"Response contains '{phrase}' which is not part of our offering. "
                "Please provide accurate information only."
            )
    return output
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Schema validation               │ Field(ge=0, le=1), Literal[...]
Custom output validator         │ @agent.output_validator
Trigger retry                   │ raise ModelRetry("fix this...")
Set max retries                 │ Agent(..., retries=3)
Retry in tools                  │ raise ModelRetry(...) inside @agent.tool
Pydantic model validator        │ @model_validator(mode='after')
Async validator                 │ async def validate(ctx, output)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Tomás: "The responses are validated and correct. But the user stares at a blank screen for 3-5 seconds while the agent thinks. I need streaming — show the response as it's generated, word by word."

Streaming — real-time output for the chat UI.

---

[← Chapter 5: Dynamic Prompts](chapter-05-dynamic-prompts.md) | [Chapter 7: Streaming →](chapter-07-streaming.md)
