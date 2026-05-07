# Chapter 13: Evals — Measuring Agent Quality

[← Chapter 12: Observability](chapter-12-observability.md) | [Chapter 14: Graphs →](chapter-14-graphs.md)

---

## The Task

Rin: "The agent 'works' — but is it good? Does it classify billing tickets correctly 90% of the time? Does it hallucinate? If I switch from GPT-4o to Claude, does quality drop? I need numbers, not vibes."

---

## What Are Evals?

Evals (evaluations) are systematic tests that measure agent quality against a dataset of known inputs and expected outputs.

```
Input: "I was charged twice"
Expected: category='billing', priority='high'
Actual:   category='billing', priority='high'
Score: ✓ PASS
```

Unlike unit tests (pass/fail), evals give you metrics: accuracy, precision, recall, cost.

---

## Pydantic Evals

PydanticAI includes `pydantic-evals` for structured evaluation:

```bash
pip install pydantic-evals
```

```python
from pydantic_evals import Case, Dataset


# Define test cases
dataset = Dataset(
    name='ticket_classification',
    cases=[
        Case(
            inputs='I was charged twice for my subscription',
            expected_output={'category': 'billing', 'priority': 'high'},
        ),
        Case(
            inputs='My dashboard shows a 500 error',
            expected_output={'category': 'technical', 'priority': 'high'},
        ),
        Case(
            inputs='How do I invite team members?',
            expected_output={'category': 'account', 'priority': 'low'},
        ),
        Case(
            inputs='Can you add dark mode?',
            expected_output={'category': 'feature_request', 'priority': 'low'},
        ),
    ],
)
```

---

## Running Evals Against Your Agent

```python
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset

agent = Agent(
    'openai:gpt-4o',
    output_type=TicketClassification,
    instructions='Classify support tickets.',
)


# Define the task function (what gets evaluated)
async def classify_ticket(inputs: str) -> dict:
    result = await agent.run(inputs)
    return {
        'category': result.output.category,
        'priority': result.output.priority,
    }


# Run the evaluation
report = await dataset.evaluate(task=classify_ticket)
print(report)
```

The report shows:
- Pass/fail for each case
- Overall accuracy
- Which cases failed and why
- Token usage and cost

---

## Custom Evaluators

Define what "correct" means for your use case:

```python
from pydantic_evals import Case, Dataset, Evaluator


class CategoryAccuracy(Evaluator):
    """Check if the category matches expected."""

    def evaluate(self, inputs, output, expected_output):
        if output['category'] == expected_output['category']:
            return {'score': 1.0, 'reason': 'Category matches'}
        return {'score': 0.0, 'reason': f"Expected {expected_output['category']}, got {output['category']}"}


class PriorityAccuracy(Evaluator):
    """Check if priority matches (with partial credit for being close)."""

    priority_order = ['low', 'medium', 'high', 'critical']

    def evaluate(self, inputs, output, expected_output):
        expected_idx = self.priority_order.index(expected_output['priority'])
        actual_idx = self.priority_order.index(output['priority'])
        distance = abs(expected_idx - actual_idx)

        if distance == 0:
            return {'score': 1.0, 'reason': 'Exact match'}
        elif distance == 1:
            return {'score': 0.5, 'reason': 'Off by one level'}
        return {'score': 0.0, 'reason': f"Expected {expected_output['priority']}, got {output['priority']}"}


dataset = Dataset(
    name='ticket_classification',
    cases=[...],
    evaluators=[CategoryAccuracy(), PriorityAccuracy()],
)
```

---

## Comparing Models

Run the same eval against different models:

```python
models = ['openai:gpt-4o', 'openai:gpt-4o-mini', 'anthropic:claude-sonnet-4-6']

for model_name in models:
    with agent.override(model=model_name):
        report = await dataset.evaluate(task=classify_ticket)
        print(f"\n{model_name}:")
        print(f"  Accuracy: {report.accuracy:.1%}")
        print(f"  Cost: ${report.total_cost:.4f}")
        print(f"  Avg latency: {report.avg_latency:.2f}s")
```

Output:

```
openai:gpt-4o:
  Accuracy: 92.5%
  Cost: $0.0340
  Avg latency: 1.8s

openai:gpt-4o-mini:
  Accuracy: 85.0%
  Cost: $0.0045
  Avg latency: 0.9s

anthropic:claude-sonnet-4-6:
  Accuracy: 90.0%
  Cost: $0.0280
  Avg latency: 2.1s
```

Now you can make informed decisions: GPT-4o-mini is 7.5x cheaper with only 7.5% accuracy drop — acceptable for triage?

---

## LLM-as-Judge Evaluator

For subjective quality (tone, helpfulness), use another LLM as evaluator:

```python
from pydantic_evals import LLMEvaluator

tone_evaluator = LLMEvaluator(
    model='openai:gpt-4o',
    prompt="""
    Rate the following support response on a scale of 1-5 for:
    - Helpfulness (does it solve the problem?)
    - Tone (is it professional and empathetic?)
    - Accuracy (does it contain correct information?)

    Customer message: {inputs}
    Agent response: {output}

    Return scores as JSON: {"helpfulness": int, "tone": int, "accuracy": int}
    """,
)

dataset = Dataset(
    name='response_quality',
    cases=[...],
    evaluators=[tone_evaluator],
)
```

---

## Tracking Quality Over Time

Run evals on every deploy and track trends:

```python
# In CI/CD pipeline
report = await dataset.evaluate(task=classify_ticket)

# Send to Logfire for tracking
logfire.info(
    "eval_results",
    dataset=dataset.name,
    accuracy=report.accuracy,
    cost=report.total_cost,
    model=agent.model_name,
    commit=os.getenv('GIT_SHA'),
)
```

Set alerts: "If accuracy drops below 85%, block the deploy."

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Define test cases               │ Case(inputs='...', expected_output={...})
Create dataset                  │ Dataset(name='...', cases=[...])
Run evaluation                  │ await dataset.evaluate(task=my_func)
Custom evaluator                │ class MyEval(Evaluator): def evaluate(...)
LLM-as-judge                    │ LLMEvaluator(model='...', prompt='...')
Compare models                  │ Run same dataset with different models
Track over time                 │ Log results to Logfire per deploy
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "Some workflows are too complex for a single agent or even agent-as-tool. I need state machines — if the customer is angry AND it's a billing issue AND they're enterprise, follow this specific escalation path. Conditional branching, loops, parallel steps."

Graphs — complex workflows as state machines.

---

[← Chapter 12: Observability](chapter-12-observability.md) | [Chapter 14: Graphs →](chapter-14-graphs.md)
