# PydanticAI — An Agent Engineering Story

You joined Cortex. The old prototype is 2,000 lines of raw OpenAI API calls with regex parsing. You're rewriting it with PydanticAI. Type-safe. Testable. Production-grade. This is that story.

## Episodes

| # | The Support Task | What You Learn |
|---|---|---|
| 00 | [Overview](chapter-00-overview.md) | The story, the cast, the roadmap |
| 01 | [Answer a question](chapter-01-first-agent.md) | Agent, run, instructions, models |
| 02 | [Classify a ticket](chapter-02-structured-output.md) | output_type, Pydantic models, Literal |
| 03 | [Look up order status](chapter-03-tools.md) | Tools, @agent.tool, tool_plain |
| 04 | [Connect to the database](chapter-04-dependencies.md) | Dependencies, deps_type, RunContext |
| 05 | [Personalize the prompt](chapter-05-dynamic-prompts.md) | @agent.system_prompt, dynamic instructions |
| 06 | [Catch bad responses](chapter-06-validation-retry.md) | output_validator, ModelRetry |
| 07 | [Stream to the UI](chapter-07-streaming.md) | run_stream, StreamedRunResult |
| 08 | [Route to specialists](chapter-08-multi-agent.md) | Multi-agent, agent-as-tool, delegation |
| 09 | [Remember the conversation](chapter-09-conversation-memory.md) | Message history, multi-turn |
| 10 | [Connect external tools](chapter-10-mcp-toolsets.md) | MCP, toolsets, capabilities |
| 11 | [Test without the LLM](chapter-11-testing.md) | TestModel, FunctionModel, overrides |
| 12 | [Debug in production](chapter-12-observability.md) | Logfire, tracing, cost tracking |
| 13 | [Measure quality](chapter-13-evals.md) | Pydantic Evals, datasets, metrics |
| 14 | [Complex workflows](chapter-14-graphs.md) | Graphs, state machines, routing |
| 15 | [Ship it](chapter-15-deployment.md) | FastAPI, streaming, error handling |

## Prerequisites

- Python 3.11+
- An LLM API key (OpenAI, Anthropic, or Gemini)
- Basic Pydantic knowledge

## Quick Start

```bash
pip install pydantic-ai
export OPENAI_API_KEY="sk-..."
```

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='You are a helpful assistant.')
result = agent.run_sync('Hello!')
print(result.output)
```
