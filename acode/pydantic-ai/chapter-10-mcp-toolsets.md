# Chapter 10: MCP & Toolsets — External Capabilities

[← Chapter 9: Conversation Memory](chapter-09-conversation-memory.md) | [Chapter 11: Testing →](chapter-11-testing.md)

---

## The Task

Priya: "We need the agent to search our docs, query our knowledge base, and access Slack — but I don't want to write a custom tool for every external service. MCP gives us a standard protocol. One integration, dozens of tools."

---

## What is MCP?

Model Context Protocol (MCP) is a standard for connecting AI agents to external tools and data sources. Instead of writing custom tools for each service, you connect to MCP servers that expose tools in a standard format.

```
Agent ←→ MCP Client ←→ MCP Server (docs, database, Slack, etc.)
```

PydanticAI has built-in MCP support.

---

## Connecting to an MCP Server

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Connect to an MCP server that provides documentation search
docs_server = MCPServerStdio('npx', ['-y', '@cortex/docs-mcp-server'])

agent = Agent(
    'openai:gpt-4o',
    instructions='You are a support agent. Use the documentation tools to find accurate answers.',
    mcp_servers=[docs_server],  # ← Agent gets all tools from this server
)


async def main():
    async with agent.run_mcp_servers():  # ← Start MCP servers
        result = await agent.run("How do I set up SSO?")
        print(result.output)
```

The agent automatically discovers all tools the MCP server provides and can call them.

---

## MCP Server Types

PydanticAI supports two MCP transport types:

```python
from pydantic_ai.mcp import MCPServerStdio, MCPServerHTTP

# Stdio: runs as a subprocess (local tools)
local_server = MCPServerStdio(
    'python', ['-m', 'my_mcp_server'],
    env={'API_KEY': 'sk-...'},
)

# HTTP: connects to a remote server (SSE transport)
remote_server = MCPServerHTTP('https://mcp.cortex.io/tools')
```

---

## Multiple MCP Servers

An agent can connect to multiple servers simultaneously:

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

docs_server = MCPServerStdio('npx', ['-y', '@cortex/docs-mcp'])
db_server = MCPServerStdio('python', ['-m', 'cortex_db_mcp'])
slack_server = MCPServerStdio('npx', ['-y', '@modelcontextprotocol/server-slack'])

agent = Agent(
    'openai:gpt-4o',
    instructions='You are a support agent with access to docs, database, and Slack.',
    mcp_servers=[docs_server, db_server, slack_server],
)

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run(
            "Find the SSO setup guide in our docs, check if customer #123 has SSO enabled, "
            "and post a summary in #support-escalations on Slack."
        )
```

The agent sees all tools from all servers and decides which to use.

---

## Toolsets: Grouping Tools

Toolsets let you bundle related tools together and control which tools are available:

```python
from pydantic_ai import Agent
from pydantic_ai.tools import Toolset

# Define a toolset with related tools
support_tools = Toolset()


@support_tools.tool_plain
def search_knowledge_base(query: str) -> str:
    """Search the help center for relevant articles."""
    # ... implementation
    return "Found: How to reset password..."


@support_tools.tool_plain
def get_status_page() -> str:
    """Check current system status."""
    return "All systems operational"


# Use the toolset in an agent
agent = Agent(
    'openai:gpt-4o',
    instructions='You are a support agent.',
    toolsets=[support_tools],
)
```

Toolsets are reusable — the same toolset can be shared across multiple agents.

---

## Capabilities: Bundled Behavior

Capabilities are a higher-level concept — they bundle tools, instructions, hooks, and settings into reusable units:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import WebSearchCapability

# Built-in web search capability
agent = Agent(
    'openai:gpt-4o',
    instructions='You are a research assistant.',
    capabilities=[WebSearchCapability()],  # Adds web search tools + instructions
)
```

PydanticAI ships with built-in capabilities:
- `WebSearchCapability` — web search
- `ThinkingCapability` — chain-of-thought reasoning

You can also build custom capabilities that package your tools + instructions together.

---

## Combining MCP + Local Tools

MCP tools and local tools work together:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPServerStdio


docs_server = MCPServerStdio('npx', ['-y', '@cortex/docs-mcp'])

agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDeps,
    instructions='You are a support agent.',
    mcp_servers=[docs_server],  # External tools via MCP
)


# Local tool (has access to deps)
@agent.tool
async def get_customer_info(ctx: RunContext[SupportDeps]) -> str:
    """Get the current customer's account details."""
    return await ctx.deps.db.fetch_one(
        "SELECT * FROM customers WHERE id = $1",
        ctx.deps.customer_id,
    )
```

The agent sees both MCP tools (from the server) and local tools (decorated functions). It chooses the right one based on the task.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
MCP server (stdio)              │ MCPServerStdio('command', ['args'])
MCP server (HTTP)               │ MCPServerHTTP('https://...')
Attach to agent                 │ Agent(..., mcp_servers=[server])
Start servers                   │ async with agent.run_mcp_servers():
Multiple servers                │ mcp_servers=[server1, server2]
Toolset (group tools)           │ Toolset() + @toolset.tool_plain
Capabilities                    │ Agent(..., capabilities=[...])
Mix MCP + local tools           │ mcp_servers=[...] + @agent.tool
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Rin: "How do we test all of this without burning through API credits? I need deterministic tests that don't call the real LLM. And I need to verify the agent calls the right tools with the right arguments."

Testing — TestModel, FunctionModel, and deterministic agent tests.

---

[← Chapter 9: Conversation Memory](chapter-09-conversation-memory.md) | [Chapter 11: Testing →](chapter-11-testing.md)
