# Chapter 15: Deployment — Shipping the Agent Platform

[← Chapter 14: Graphs](chapter-14-graphs.md)

---

## The Task

Priya: "Ship it. FastAPI endpoint. Streaming responses. Proper error handling. Rate limiting. Health checks. The whole production stack."

---

## FastAPI Integration

PydanticAI is async-native — it fits naturally into FastAPI:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic_ai import Agent

app = FastAPI(title="Cortex Support API")

agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions='You are a customer support agent for Cortex.',
)


class ChatRequest(BaseModel):
    message: str
    customer_id: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    classification: TicketClassification | None = None
    tokens_used: int


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    deps = await build_deps(request.customer_id)
    history = await load_history(request.session_id) if request.session_id else []

    try:
        result = await agent.run(
            request.message,
            deps=deps,
            message_history=history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Save conversation history
    if request.session_id:
        await save_history(request.session_id, result.all_messages())

    return ChatResponse(
        response=result.output,
        tokens_used=result.usage().total_tokens,
    )
```

---

## Streaming Endpoint

```python
import json


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    deps = await build_deps(request.customer_id)
    history = await load_history(request.session_id) if request.session_id else []

    async def event_stream():
        try:
            async with agent.run_stream(
                request.message, deps=deps, message_history=history
            ) as stream:
                async for chunk in stream.stream_text(delta=True):
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"

            # Final metadata
            result = stream.result()
            yield f"data: {json.dumps({'type': 'done', 'tokens': result.usage().total_tokens})}\n\n"

            # Save history
            if request.session_id:
                await save_history(request.session_id, result.all_messages())

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

## Error Handling

```python
from pydantic_ai.exceptions import UnexpectedModelBehavior, UsageLimitExceeded


@app.post("/chat")
async def chat(request: ChatRequest):
    deps = await build_deps(request.customer_id)

    try:
        result = await agent.run(request.message, deps=deps)
    except UsageLimitExceeded:
        raise HTTPException(
            status_code=429,
            detail="Token limit exceeded. Please try a shorter message.",
        )
    except UnexpectedModelBehavior as e:
        # Agent failed after all retries
        logfire.error("Agent failed", error=str(e), customer_id=request.customer_id)
        raise HTTPException(
            status_code=502,
            detail="Our AI assistant is having trouble. Please try again.",
        )
    except Exception as e:
        logfire.error("Unexpected error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal error")

    return ChatResponse(response=result.output, tokens_used=result.usage().total_tokens)
```

---

## Usage Limits

Prevent runaway costs:

```python
from pydantic_ai import Agent
from pydantic_ai.settings import UsageLimits

agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions='...',
)

# Per-request limits
result = await agent.run(
    message,
    deps=deps,
    usage_limits=UsageLimits(
        request_limit=5,        # Max 5 LLM calls per run (including retries)
        request_tokens_limit=4000,  # Max input tokens
        response_tokens_limit=1000, # Max output tokens
        total_tokens_limit=5000,    # Max total tokens
    ),
)
```

If limits are exceeded, `UsageLimitExceeded` is raised.

---

## Health Check

```python
@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "ready"}


@app.get("/health/deep")
async def deep_health():
    """Verify the agent can actually respond."""
    try:
        result = await agent.run(
            "ping",
            usage_limits=UsageLimits(request_limit=1, response_tokens_limit=10),
        )
        return {"status": "healthy", "model_responsive": True}
    except Exception as e:
        return {"status": "degraded", "model_responsive": False, "error": str(e)}
```

---

## Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


@app.post("/chat")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat(request: ChatRequest):
    ...
```

Or per-customer limits:

```python
from fastapi import Depends


async def check_rate_limit(request: ChatRequest):
    """Check customer's rate limit based on their plan."""
    customer = await get_customer(request.customer_id)
    limits = {
        'free': 20,       # 20 messages/hour
        'pro': 100,       # 100 messages/hour
        'enterprise': 1000,  # 1000 messages/hour
    }
    current_usage = await get_hourly_usage(request.customer_id)
    if current_usage >= limits.get(customer.plan, 20):
        raise HTTPException(429, "Rate limit exceeded for your plan")


@app.post("/chat")
async def chat(request: ChatRequest, _=Depends(check_rate_limit)):
    ...
```

---

## Model Fallback

Handle provider outages gracefully:

```python
from pydantic_ai import Agent


async def run_with_fallback(message: str, deps: SupportDeps):
    """Try primary model, fall back to secondary on failure."""
    models = ['openai:gpt-4o', 'anthropic:claude-sonnet-4-6', 'openai:gpt-4o-mini']

    for model in models:
        try:
            result = await agent.run(message, deps=deps, model=model)
            return result
        except Exception as e:
            logfire.warn(f"Model {model} failed, trying next", error=str(e))
            continue

    raise HTTPException(502, "All models unavailable")
```

---

## The Complete Production Setup

```python
# main.py
import logfire
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic_ai import Agent

logfire.configure()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    # Startup: initialize connections
    app.state.db = await create_db_pool()
    app.state.redis = await create_redis_pool()
    logfire.info("Application started")
    yield
    # Shutdown: close connections
    await app.state.db.close()
    await app.state.redis.close()
    logfire.info("Application stopped")


app = FastAPI(title="Cortex Support API", lifespan=lifespan)

agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions=[
        'You are a customer support agent for Cortex.',
        'Use tools to look up real data. Never guess.',
        'Be concise, professional, and empathetic.',
    ],
)

# Register tools, system prompts, validators...
# (imported from separate modules)
```

---

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Everything You Learned

```
────────────────────────────────────────────────────────────
 Chapter │ Concept                    │ Production Use
────────────────────────────────────────────────────────────
 01      │ Agent basics               │ Core abstraction
 02      │ Structured output          │ Typed API responses
 03      │ Tools                      │ Database/API access
 04      │ Dependencies               │ Testable, injectable services
 05      │ Dynamic prompts            │ Per-customer personalization
 06      │ Validation & retry         │ Self-correcting responses
 07      │ Streaming                  │ Real-time chat UI
 08      │ Multi-agent                │ Specialist routing
 09      │ Conversation memory        │ Multi-turn sessions
 10      │ MCP & toolsets             │ External integrations
 11      │ Testing                    │ Fast, deterministic CI
 12      │ Observability              │ Debugging & cost tracking
 13      │ Evals                      │ Quality measurement
 14      │ Graphs                     │ Complex workflows
 15      │ Deployment                 │ Production FastAPI
────────────────────────────────────────────────────────────
```

---

## Priya's Final Review

Priya opens the Logfire dashboard. Traces flowing. Costs tracked. Quality metrics green.

> "Type-safe. Testable. Observable. Model-agnostic. Streaming. Multi-agent. Validated outputs. Production-grade."

She pauses.

> "Ship it."

---

## Where to Go From Here

- **[PydanticAI Docs](https://ai.pydantic.dev/)** — the official reference
- **[Pydantic Logfire](https://pydantic.dev/logfire)** — observability platform
- **[Pydantic Evals](https://pydantic.dev/docs/evals)** — evaluation framework
- **[MCP Servers](https://github.com/modelcontextprotocol/servers)** — community MCP servers
- **[PydanticAI Examples](https://ai.pydantic.dev/examples/)** — official examples (SQL gen, RAG, weather)

---

## The Rules

What you'll tell the next engineer who joins:

1. **Type everything.** `output_type`, `deps_type`, `RunContext[T]` — let the type checker work.
2. **Validate aggressively.** Pydantic schema + `@output_validator` + `ModelRetry`.
3. **Inject dependencies.** Never use globals. Pass deps at runtime. Test with mocks.
4. **Test without the LLM.** `TestModel` for unit tests. Real LLM for integration tests only.
5. **Observe everything.** Logfire traces on every run. Alert on latency and cost.
6. **Eval continuously.** Run evals on every deploy. Track quality over time.
7. **Start simple.** Single agent → tools → multi-agent → graphs. Don't over-engineer.
8. **Model-agnostic.** Never couple to one provider. Swap models in one line.

---

[← Chapter 14: Graphs](chapter-14-graphs.md)
