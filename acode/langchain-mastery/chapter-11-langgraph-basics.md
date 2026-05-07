# Chapter 11: LangGraph — Stateful Agent Workflows

[← Chapter 10](chapter-10-agents.md) · [Chapter 12: Conditional Routing →](chapter-12-conditional-routing.md)

---

## The Scene

The ReAct agent from Chapter 10 works — mostly. But it has problems:

1. It sometimes loops forever, calling the same tool 15 times
2. There's no way to limit how many steps it takes
3. You can't add human approval before it takes an action
4. The flow is opaque — you can't see the decision tree

Raj pulls up the logs:

> "The agent searched for 'breach of fiduciary duty,' got results, then searched again with the same query. Then again. Then again. 12 times. Cost us $3 for one question."

Priya adds: "And for the legal draft feature — I need a lawyer to approve before the AI sends anything. The agent just... does things. There's no pause button."

You need more control than a simple agent loop gives you. You need a **graph** — explicit nodes, explicit edges, explicit state.

Enter LangGraph.

---

## What is LangGraph?

LangGraph lets you build AI workflows as **state machines**. Instead of "let the agent figure it out," you define:

- **Nodes**: steps in the workflow (functions that do things)
- **Edges**: connections between steps (what happens next)
- **State**: data that flows through the graph (and persists)
- **Conditional edges**: branching logic (if X, go to Y; else go to Z)

```
Simple Agent (Chapter 10):        LangGraph:
──────────────────────────        ──────────
"Figure it out"                   Explicit flow
No step limit                     Controlled iterations
No human approval                 Interrupt anywhere
Opaque decisions                  Visible graph
```

Think of it as the difference between "go explore" and a flowchart.

---

## Your First Graph

Let's rebuild the research workflow as a graph:

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage

# 1. Define the state
class ResearchState(TypedDict):
    question: str
    classification: str
    jurisdiction: str
    research_results: list[str]
    memo: str
    steps_taken: int

# 2. Define the nodes (functions)
def classify(state: ResearchState) -> dict:
    """Classify the legal question."""
    result = classify_chain.invoke({"question": state["question"]})
    return {
        "classification": result.area,
        "jurisdiction": result.jurisdiction,
        "steps_taken": state.get("steps_taken", 0) + 1,
    }

def research(state: ResearchState) -> dict:
    """Find relevant cases."""
    result = research_chain.invoke({
        "question": state["question"],
        "area": state["classification"],
        "jurisdiction": state["jurisdiction"],
    })
    return {
        "research_results": [f"{c.name} ({c.year})" for c in result.cases],
        "steps_taken": state["steps_taken"] + 1,
    }

def write_memo(state: ResearchState) -> dict:
    """Write the research memo."""
    result = memo_chain.invoke({
        "question": state["question"],
        "jurisdiction": state["jurisdiction"],
        "cases": "\n".join(state["research_results"]),
    })
    return {
        "memo": result,
        "steps_taken": state["steps_taken"] + 1,
    }

# 3. Build the graph
graph = StateGraph(ResearchState)

# Add nodes
graph.add_node("classify", classify)
graph.add_node("research", research)
graph.add_node("write_memo", write_memo)

# Add edges (the flow)
graph.add_edge(START, "classify")
graph.add_edge("classify", "research")
graph.add_edge("research", "write_memo")
graph.add_edge("write_memo", END)

# Compile
app = graph.compile()
```

### Running It

```python
result = app.invoke({
    "question": "Can a board member be held liable for approving a below-market merger in Delaware?",
    "steps_taken": 0,
})

print(result["memo"])
print(f"Steps taken: {result['steps_taken']}")
```

---

## Visualizing the Graph

```python
# Print the graph structure
app.get_graph().print_ascii()
```

```
        ┌───────────┐
        │   START   │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │  classify  │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │  research  │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │ write_memo │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │    END    │
        └───────────┘
```

The flow is explicit. No mystery. No infinite loops.

---

## State: The Heart of LangGraph

State is a `TypedDict` that flows through the graph. Each node reads from state and returns updates:

```python
class ResearchState(TypedDict):
    question: str                    # Input (set once)
    classification: str              # Set by classify node
    jurisdiction: str                # Set by classify node
    research_results: list[str]      # Set by research node
    memo: str                        # Set by write_memo node
    steps_taken: int                 # Incremented by each node
```

Key rules:
- Nodes receive the **full state**
- Nodes return a **partial dict** with only the fields they update
- LangGraph merges the updates into the state

```python
def classify(state: ResearchState) -> dict:
    # Reads: state["question"]
    # Returns: updates to classification, jurisdiction, steps_taken
    return {
        "classification": "corporate",
        "jurisdiction": "Delaware",
        "steps_taken": state["steps_taken"] + 1,
    }
```

---

## Annotated State: Reducers

What if multiple nodes add to the same list? By default, LangGraph **replaces** the value. With `Annotated`, you can define how values combine:

```python
from typing import Annotated
from operator import add

class ResearchState(TypedDict):
    question: str
    messages: Annotated[list, add]  # append, don't replace!
    research_results: Annotated[list[str], add]  # accumulate results
    steps_taken: int
```

Now when a node returns `{"research_results": ["new case"]}`, it's **appended** to the existing list, not replacing it.

---

## Loops with Control

The agent from Chapter 10 looped forever. With LangGraph, you control loops explicitly:

```python
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    question: str
    messages: Annotated[list, add]
    tool_calls: int
    max_tool_calls: int

def should_continue(state: AgentState) -> str:
    """Decide whether to keep researching or stop."""
    if state["tool_calls"] >= state["max_tool_calls"]:
        return "stop"  # Force stop after N tool calls
    
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"  # Model wants to use a tool
    
    return "stop"  # Model is done

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", call_tools)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {
    "continue": "tools",
    "stop": END,
})
graph.add_edge("tools", "agent")  # After tools, back to agent

app = graph.compile()
```

The loop is explicit. The exit condition is explicit. No more runaway agents.

---

## Streaming Graph Execution

Watch the graph execute step by step:

```python
for event in app.stream({
    "question": "Fiduciary duty in Delaware",
    "messages": [],
    "tool_calls": 0,
    "max_tool_calls": 5,
}):
    for node_name, output in event.items():
        print(f"\n{'='*40}")
        print(f"Node: {node_name}")
        print(f"Output: {output}")
```

Output:
```
========================================
Node: classify
Output: {'classification': 'corporate', 'jurisdiction': 'Delaware'}

========================================
Node: research
Output: {'research_results': ['Revlon v. MacAndrews (1986)', 'Stone v. Ritter (2006)']}

========================================
Node: write_memo
Output: {'memo': 'QUESTION: Fiduciary duty in Delaware...'}
```

You see exactly what happened at each step. Debugging is trivial.

---

## Why LangGraph Over Simple Chains?

| Feature | LCEL Chains | LangGraph |
|---------|-------------|-----------|
| Linear flow | ✓ | ✓ |
| Branching | `RunnableBranch` (limited) | Conditional edges (powerful) |
| Loops | Not supported | Built-in with control |
| Human-in-the-loop | Not supported | Interrupts (Ch 13) |
| Persistence | Not built-in | Checkpointing (Ch 15) |
| Visibility | Debug with print | Graph visualization |
| State management | Pass-through | Typed, accumulated state |

Use LCEL chains for simple, linear pipelines. Use LangGraph when you need branching, loops, human approval, or complex state.

---

## What You Built

```python
# graph.py — NovaMind research workflow
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class ResearchState(TypedDict):
    question: str
    classification: str
    jurisdiction: str
    research_results: list[str]
    memo: str

def classify(state):
    result = classify_chain.invoke({"question": state["question"]})
    return {"classification": result.area, "jurisdiction": result.jurisdiction}

def research(state):
    result = research_chain.invoke({
        "question": state["question"],
        "area": state["classification"],
        "jurisdiction": state["jurisdiction"],
    })
    return {"research_results": [f"{c.name} ({c.year})" for c in result.cases]}

def write_memo(state):
    result = memo_chain.invoke({
        "question": state["question"],
        "jurisdiction": state["jurisdiction"],
        "cases": "\n".join(state["research_results"]),
    })
    return {"memo": result}

graph = StateGraph(ResearchState)
graph.add_node("classify", classify)
graph.add_node("research", research)
graph.add_node("write_memo", write_memo)
graph.add_edge(START, "classify")
graph.add_edge("classify", "research")
graph.add_edge("research", "write_memo")
graph.add_edge("write_memo", END)

app = graph.compile()
```

---

## What's Next

The graph is linear: classify → research → write. But what if the classification is "simple definition" — you don't need research at all? What if the research finds nothing — you should try a broader search?

You need **conditional edges** — the graph equivalent of if/else.

That's Chapter 12.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| `StateGraph` | Define a workflow as a graph |
| `TypedDict` state | Typed data flowing through the graph |
| Nodes | Functions that read/update state |
| Edges | Connections defining flow order |
| `START` / `END` | Entry and exit points |
| `.compile()` | Turn the graph definition into a runnable |
| `.stream()` | Watch execution step by step |
| Annotated reducers | Control how state values accumulate |

---

[← Chapter 10](chapter-10-agents.md) · [Chapter 12: Conditional Routing →](chapter-12-conditional-routing.md)
