# Chapter 1: Your First Agent — Hello, Structured World

[← Overview](chapter-00-overview.md) | [Chapter 2: Structured Output →](chapter-02-structured-output.md)

---

## The Task

Priya: "Prove it works. One agent. Takes a customer question, returns a helpful answer. Show Tomás by lunch."

---

## Setup

```bash
mkdir cortex && cd cortex
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install pydantic-ai
```

Set your API key:

```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
```

That's it. PydanticAI reads the key from the environment automatically.

---

## Your First Agent

```python
# support_agent.py
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    instructions='You are a helpful customer support agent for Cortex, an analytics platform. Be concise and friendly.',
)

result = agent.run_sync('How do I reset my password?')
print(result.output)
# → "To reset your password, go to Settings > Security > Reset Password.
#    You'll receive a confirmation email. Click the link within 24 hours."
```

Run it:

```bash
python support_agent.py
```

---

## What Just Happened

```
agent = Agent(
    'openai:gpt-4o',          ← The model to use
    instructions='...',        ← System prompt (always sent)
)

result = agent.run_sync(...)   ← Run synchronously
result.output                  ← The LLM's response (str by default)
```

The `Agent` is the core abstraction. It wraps:
1. A model (which LLM to call)
2. Instructions (system prompt)
3. Tools (functions the LLM can call — none yet)
4. Output type (what shape the response must be — `str` by default)

---

## Three Ways to Run

```python
# 1. Synchronous (simple scripts, testing)
result = agent.run_sync('Hello')

# 2. Async (production, FastAPI)
result = await agent.run('Hello')

# 3. Streaming (real-time UI)
async with agent.run_stream('Hello') as stream:
    async for chunk in stream.stream_text():
        print(chunk, end='')
```

Use `run_sync` for scripts and testing. Use `run` in async code (FastAPI, etc.). Use `run_stream` when you need real-time output.

---

## Model-Agnostic: Swap Models Freely

PydanticAI supports every major provider:

```python
# OpenAI
agent = Agent('openai:gpt-4o')
agent = Agent('openai:gpt-4o-mini')

# Anthropic
agent = Agent('anthropic:claude-sonnet-4-6')
agent = Agent('anthropic:claude-haiku-4')

# Google Gemini
agent = Agent('google-gla:gemini-2.0-flash')

# DeepSeek
agent = Agent('deepseek:deepseek-chat')

# Ollama (local)
agent = Agent('ollama:llama3.2')
```

The format is always `provider:model-name`. Your tools, prompts, and output types work identically across all models.

Priya: "We start with GPT-4o for quality. Switch to Claude for cost. Drop to GPT-4o-mini for high-volume triage. Same code."

---

## Override the Model at Runtime

```python
agent = Agent('openai:gpt-4o')  # default

# Override for a specific run
result = agent.run_sync('Hello', model='anthropic:claude-sonnet-4-6')
```

Useful for A/B testing models or falling back when one provider is down.

---

## Instructions vs. User Prompt

```python
agent = Agent(
    'openai:gpt-4o',
    instructions=(
        'You are a customer support agent for Cortex.\n'
        'Rules:\n'
        '- Be concise (max 3 sentences)\n'
        '- Never make up information\n'
        '- If unsure, say "Let me connect you with a human agent"\n'
        '- Always be friendly and professional'
    ),
)

# The user prompt changes per request
result = agent.run_sync('How do I export my data?')
```

- **Instructions** = system prompt. Sent with every request. Defines the agent's personality and rules.
- **User prompt** = the customer's message. Changes every time.

---

## The Result Object

```python
result = agent.run_sync('How do I reset my password?')

# The output (the LLM's response)
print(result.output)
# → "To reset your password..."

# Usage statistics
print(result.usage())
# → Usage(requests=1, request_tokens=52, response_tokens=38, total_tokens=90)

# All messages exchanged
print(result.all_messages())
# → [SystemPrompt(...), UserPrompt(...), ModelResponse(...)]
```

`result.usage()` tells you token counts — critical for cost tracking.

---

## Multiple Instructions

You can pass instructions as a list for clarity:

```python
agent = Agent(
    'openai:gpt-4o',
    instructions=[
        'You are a customer support agent for Cortex.',
        'Be concise — max 3 sentences per response.',
        'Never fabricate information.',
        'If you cannot help, offer to connect with a human.',
    ],
)
```

Each string becomes a separate line in the system prompt.

---

## The Old Way vs. PydanticAI

The prototype code Priya wants to replace:

```python
# ❌ The old way (raw OpenAI SDK)
import openai

client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a support agent..."},
        {"role": "user", "content": "How do I reset my password?"},
    ],
)

# Hope it's not None, hope it has content
answer = response.choices[0].message.content
# No validation. No typing. No structure.
```

```python
# ✓ PydanticAI
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='You are a support agent...')
result = agent.run_sync('How do I reset my password?')
# result.output is typed, validated, and tracked
```

Same result. But now you have:
- Type safety (your IDE knows `result.output` is a `str`)
- Usage tracking built in
- Message history captured
- Model-agnostic (swap providers in one line)
- Foundation for tools, structured output, and multi-agent flows

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Create an agent                 │ Agent('provider:model', instructions=...)
Run synchronously               │ agent.run_sync('prompt')
Run async                       │ await agent.run('prompt')
Run streaming                   │ async with agent.run_stream('prompt')
Get the output                  │ result.output
Get token usage                 │ result.usage()
Get message history             │ result.all_messages()
Override model                  │ agent.run_sync('...', model='other:model')
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Tomás: "Great, it answers questions. But I need to know: is this a billing issue or a technical issue? What's the priority? What department should handle it? I need structured data, not prose."

Structured output — making the agent return validated Pydantic models.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Structured Output →](chapter-02-structured-output.md)
