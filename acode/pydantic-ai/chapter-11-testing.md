# Chapter 11: Testing — No LLM Required

[← Chapter 10: MCP & Toolsets](chapter-10-mcp-toolsets.md) | [Chapter 12: Observability →](chapter-12-observability.md)

---

## The Task

Rin: "Every test run costs money and takes 2-5 seconds per call. I need tests that are free, fast, and deterministic. And I need to verify the agent calls the right tools — not just that it returns something."

---

## The Problem with Testing LLM Agents

Real LLM calls in tests are:
- **Slow** (2-5 seconds per call)
- **Expensive** ($0.01-0.10 per call × hundreds of tests)
- **Non-deterministic** (same input → different output each time)
- **Flaky** (API rate limits, network issues)

---

## TestModel: Deterministic Fake

PydanticAI provides `TestModel` — a fake model that returns predictable responses without calling any API:

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

agent = Agent('openai:gpt-4o', instructions='You are a support agent.')


def test_basic_response():
    with agent.override(model=TestModel()):
        result = agent.run_sync("Hello")
        # TestModel returns a generic response
        assert result.output is not None
```

`TestModel` doesn't call any API. It generates a response based on the output type:
- `str` output → returns a generic text response
- `BaseModel` output → returns an instance with plausible values
- `bool` output → returns `True`

---

## TestModel with Custom Responses

Control exactly what TestModel returns:

```python
from pydantic_ai.models.test import TestModel


def test_specific_response():
    with agent.override(model=TestModel(custom_output_text='Your order has shipped!')):
        result = agent.run_sync("Where's my order?")
        assert result.output == 'Your order has shipped!'
```

For structured output:

```python
from pydantic_ai.models.test import TestModel


def test_structured_response():
    expected = TicketClassification(
        category='billing',
        priority='high',
        confidence=0.9,
        summary='Duplicate charge reported',
    )

    with agent.override(model=TestModel(custom_output_args=expected.model_dump())):
        result = agent.run_sync("I was charged twice")
        assert result.output.category == 'billing'
        assert result.output.priority == 'high'
```

---

## FunctionModel: Full Control

For complex test scenarios, `FunctionModel` lets you write a Python function that acts as the model:

```python
from pydantic_ai import Agent
from pydantic_ai.models.function import FunctionModel, AgentInfo
from pydantic_ai.messages import ModelResponse, TextPart


def my_fake_model(messages, info: AgentInfo) -> ModelResponse:
    """A fake model that responds based on the user's message."""
    # Get the last user message
    last_message = messages[-1]
    user_text = str(last_message)

    if 'order' in user_text.lower():
        return ModelResponse(parts=[TextPart('Let me look up your order.')])
    elif 'refund' in user_text.lower():
        return ModelResponse(parts=[TextPart('I can help with your refund.')])
    else:
        return ModelResponse(parts=[TextPart('How can I help you today?')])


def test_routing_logic():
    with agent.override(model=FunctionModel(my_fake_model)):
        result = agent.run_sync("Where's my order #12345?")
        assert 'order' in result.output.lower()
```

---

## Testing Tool Calls

Verify the agent calls the right tools with the right arguments:

```python
from pydantic_ai.models.test import TestModel


def test_tool_is_called():
    # TestModel can be configured to call tools
    with agent.override(model=TestModel()):
        result = agent.run_sync("What's the status of order #12345?")

        # Check which tools were called by inspecting messages
        messages = result.all_messages()
        tool_calls = [
            part
            for msg in messages
            for part in getattr(msg, 'parts', [])
            if hasattr(part, 'tool_name')
        ]

        # Verify the right tool was called
        assert any(tc.tool_name == 'get_order_status' for tc in tool_calls)
```

---

## Overriding Dependencies in Tests

```python
from unittest.mock import AsyncMock


async def test_with_mock_deps():
    # Create mock dependencies
    mock_db = AsyncMock()
    mock_db.fetch.return_value = [{"id": "12345", "status": "shipped"}]

    test_deps = SupportDeps(
        db=mock_db,
        customer_id="test_customer",
        customer_plan="pro",
    )

    with agent.override(model=TestModel(), deps=test_deps):
        result = await agent.run("Where's my order?")
        # The tool will use mock_db, not a real database
```

`agent.override()` can override both the model AND dependencies simultaneously.

---

## Testing the Full Pipeline

```python
import pytest
from pydantic_ai.models.test import TestModel


@pytest.fixture
def test_agent():
    """Provide agent with TestModel for all tests."""
    with agent.override(model=TestModel()):
        yield agent


@pytest.fixture
def mock_deps():
    """Provide mock dependencies."""
    mock_db = AsyncMock()
    mock_db.fetch_one.return_value = {"plan": "pro", "status": "active"}
    return SupportDeps(db=mock_db, customer_id="test_001", customer_plan="pro")


async def test_classification_output_type(test_agent, mock_deps):
    """Verify the agent returns the correct output type."""
    with agent.override(deps=mock_deps):
        result = await agent.run("I can't log in")
        assert isinstance(result.output, TicketClassification)


async def test_billing_routes_correctly(test_agent, mock_deps):
    """Verify billing questions get classified as billing."""
    with agent.override(
        model=TestModel(custom_output_args={
            'category': 'billing',
            'priority': 'high',
            'confidence': 0.9,
            'summary': 'Refund request',
        }),
        deps=mock_deps,
    ):
        result = await agent.run("I want a refund")
        assert result.output.category == 'billing'
```

---

## Testing Without override (Direct)

For simpler tests, pass TestModel directly:

```python
from pydantic_ai.models.test import TestModel


async def test_direct():
    result = await agent.run(
        "Hello",
        model=TestModel(),  # Override just for this run
    )
    assert result.output is not None
```

---

## Integration Tests (Real LLM, Sparingly)

For critical paths, run a few tests against the real LLM:

```python
import pytest


@pytest.mark.integration  # Mark so they can be skipped in CI
@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason='No API key')
async def test_real_classification():
    """Integration test — calls real LLM."""
    result = await agent.run("I was charged $50 but my plan is $29")
    assert result.output.category == 'billing'
    assert result.output.priority in ('medium', 'high')
```

Run integration tests separately: `pytest -m integration`

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Fake model (no API calls)       │ TestModel()
Custom text response            │ TestModel(custom_output_text='...')
Custom structured response      │ TestModel(custom_output_args={...})
Full control fake               │ FunctionModel(my_function)
Override model                  │ with agent.override(model=TestModel()):
Override deps                   │ with agent.override(deps=mock_deps):
Override both                   │ with agent.override(model=..., deps=...):
Per-run override                │ agent.run(msg, model=TestModel())
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "Tests pass. But in production, I need to see what's happening. Which tools are being called? How long do they take? How much are we spending on tokens? I need observability."

Logfire integration — tracing, debugging, and cost tracking.

---

[← Chapter 10: MCP & Toolsets](chapter-10-mcp-toolsets.md) | [Chapter 12: Observability →](chapter-12-observability.md)
