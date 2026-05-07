# Chapter 14: Graphs — Complex Workflows as State Machines

[← Chapter 13: Evals](chapter-13-evals.md) | [Chapter 15: Deployment →](chapter-15-deployment.md)

---

## The Task

Priya: "Some tickets need a multi-step workflow: classify → check sentiment → if angry + billing + enterprise → auto-escalate to VP. If technical + critical → page on-call. Simple agent delegation can't express this. I need a state machine."

---

## When Agents Aren't Enough

Agent-as-tool works for simple delegation. But when you need:
- Conditional branching (if X then agent A, else agent B)
- Loops (retry until quality threshold met)
- Parallel execution (run sentiment + classification simultaneously)
- State that accumulates across steps

...you need a graph.

---

## PydanticAI Graphs

PydanticAI provides graph support for complex workflows. Graphs are defined using type hints and dataclasses:

```python
from dataclasses import dataclass
from pydantic_ai.graph import Graph, Node, End


@dataclass
class TicketState:
    """State that flows through the graph."""
    message: str
    customer_id: str
    classification: TicketClassification | None = None
    sentiment: str | None = None
    response: str | None = None
    escalated: bool = False
```

---

## Defining Nodes

Each node is a step in the workflow:

```python
from pydantic_ai import Agent
from pydantic_ai.graph import Graph, Node, End


# Node 1: Classify the ticket
@dataclass
class ClassifyNode(Node[TicketState]):
    async def run(self, state: TicketState) -> str:
        result = await classifier_agent.run(state.message)
        state.classification = result.output
        return 'analyze_sentiment'  # Next node


# Node 2: Analyze sentiment
@dataclass
class SentimentNode(Node[TicketState]):
    async def run(self, state: TicketState) -> str:
        result = await sentiment_agent.run(state.message)
        state.sentiment = result.output

        # Conditional routing
        if state.sentiment == 'angry' and state.classification.priority == 'critical':
            return 'escalate'
        return 'respond'


# Node 3a: Generate response (normal path)
@dataclass
class RespondNode(Node[TicketState]):
    async def run(self, state: TicketState) -> str:
        specialist = specialists[state.classification.category]
        result = await specialist.run(state.message)
        state.response = result.output
        return End  # Done


# Node 3b: Escalate (angry + critical path)
@dataclass
class EscalateNode(Node[TicketState]):
    async def run(self, state: TicketState) -> str:
        state.escalated = True
        state.response = (
            "I understand this is frustrating. I've escalated your issue "
            "to our senior team. You'll hear back within 1 hour."
        )
        # Also notify the team
        await notify_oncall(state)
        return End
```

---

## Building the Graph

```python
# Define the graph
support_graph = Graph(
    nodes={
        'classify': ClassifyNode(),
        'analyze_sentiment': SentimentNode(),
        'respond': RespondNode(),
        'escalate': EscalateNode(),
    },
    start='classify',
)

# Run it
async def handle_ticket(customer_id: str, message: str):
    state = TicketState(message=message, customer_id=customer_id)
    final_state = await support_graph.run(state)
    return {
        'response': final_state.response,
        'classification': final_state.classification,
        'escalated': final_state.escalated,
    }
```

---

## The Flow

```
┌──────────┐     ┌───────────────┐     ┌──────────┐
│ Classify │────▶│   Sentiment   │──┬──▶│ Respond  │──▶ End
└──────────┘     └───────────────┘  │   └──────────┘
                                    │
                                    │   ┌──────────┐
                                    └──▶│ Escalate │──▶ End
                                        └──────────┘
                                   (angry + critical)
```

---

## Conditional Routing

Nodes return the name of the next node (or `End`):

```python
@dataclass
class RouterNode(Node[TicketState]):
    async def run(self, state: TicketState) -> str:
        cat = state.classification.category
        priority = state.classification.priority

        # Complex routing logic
        if cat == 'billing' and state.customer_plan == 'enterprise':
            return 'vip_billing'
        elif cat == 'technical' and priority == 'critical':
            return 'page_oncall'
        elif state.sentiment == 'angry':
            return 'empathy_response'
        else:
            return 'standard_response'
```

---

## Loops (Retry Until Quality)

```python
@dataclass
class QualityCheckNode(Node[TicketState]):
    max_retries: int = 3
    attempt: int = 0

    async def run(self, state: TicketState) -> str:
        # Check response quality
        quality = await quality_agent.run(
            f"Rate this response quality (1-10): {state.response}"
        )

        if quality.output >= 7:
            return End  # Good enough
        elif self.attempt >= self.max_retries:
            return 'escalate'  # Give up, escalate to human
        else:
            self.attempt += 1
            return 'respond'  # Try generating a better response
```

---

## When to Use Graphs vs Simple Agents

```
────────────────────────────────────────────────────────────
 Scenario                        │ Use
────────────────────────────────────────────────────────────
 Single question → answer        │ Single agent
 Route to specialist             │ Agent-as-tool
 Multi-step with conditions      │ Graph
 Retry loops with quality gates  │ Graph
 Parallel processing             │ Graph
 Audit trail required            │ Graph (state tracks everything)
 Simple enough for one prompt    │ Single agent (don't over-engineer)
────────────────────────────────────────────────────────────
```

Priya's rule: "Start with a single agent. Add tools. If the control flow gets complex enough that you're writing nested if/else in tools, switch to a graph."

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Define state                    │ @dataclass class MyState: ...
Define node                     │ class MyNode(Node[MyState]): async def run(...)
Route to next node              │ return 'node_name'
End the graph                   │ return End
Build graph                     │ Graph(nodes={...}, start='...')
Run graph                       │ await graph.run(initial_state)
Conditional routing             │ if/else in node's run() method
Loop                            │ Return to a previous node name
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "The agent system is complete. Now ship it. FastAPI endpoint, async handling, proper error handling, rate limiting, and deployment."

Deploying the agent platform — FastAPI integration and production concerns.

---

[← Chapter 13: Evals](chapter-13-evals.md) | [Chapter 15: Deployment →](chapter-15-deployment.md)
