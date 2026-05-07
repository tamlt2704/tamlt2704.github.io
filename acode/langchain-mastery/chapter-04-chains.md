# Chapter 4: Chains (LCEL Composition)

[← Chapter 3](chapter-03-structured-output.md) · [Chapter 5: Memory →](chapter-05-memory.md)

---

## The Scene

Priya wants a "research memo" feature. A lawyer types a question, and the system:

1. Classifies the legal area (contract, tort, corporate, etc.)
2. Identifies the jurisdiction
3. Researches relevant cases
4. Writes a structured memo

Four steps. Each depends on the previous. You could write this as four separate function calls glued together with Python — but that's what the prototype already does. Spaghetti.

LangChain's answer: **compose chains from chains**. Each step is a Runnable. Pipe them together.

---

## RunnableSequence: The Pipe

You've already seen the basic pipe:

```python
chain = prompt | llm | parser
```

This is a `RunnableSequence`. Each component:
- Takes input
- Produces output
- Passes it to the next component

The key insight: **the output of one step becomes the input of the next**.

---

## Multi-Step Chain: The Research Memo

### Step 1: Classify the Legal Area

```python
from pydantic import BaseModel, Field
from typing import Literal

class Classification(BaseModel):
    area: Literal["contract", "tort", "corporate", "criminal", "employment", "ip", "other"]
    jurisdiction: str = Field(description="Most likely jurisdiction")
    sub_topic: str = Field(description="Specific sub-topic within the area")

classify_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the following legal question. Identify the area of law and jurisdiction."),
    ("human", "{question}"),
])

classify_chain = classify_prompt | llm.with_structured_output(Classification)
```

### Step 2: Research Cases (uses classification output)

```python
class ResearchResult(BaseModel):
    cases: list[CaseCitation]
    key_principles: list[str]

research_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a legal researcher specializing in {area} law in {jurisdiction}. "
     "Find relevant precedents for the sub-topic: {sub_topic}. "
     "Only cite cases you are confident exist."),
    ("human", "{question}"),
])

research_chain = research_prompt | llm.with_structured_output(ResearchResult)
```

### Step 3: Write the Memo (uses research output)

```python
memo_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Write a legal research memo. Use this structure:\n"
     "QUESTION: [restate the question]\n"
     "JURISDICTION: [jurisdiction]\n"
     "RELEVANT CASES: [list with citations]\n"
     "ANALYSIS: [how the cases apply]\n"
     "CONCLUSION: [direct answer]\n"),
    ("human",
     "Question: {question}\n"
     "Area: {area}\n"
     "Jurisdiction: {jurisdiction}\n"
     "Cases found: {cases}\n"
     "Key principles: {key_principles}"),
])

memo_chain = memo_prompt | llm | StrOutputParser()
```

---

## Wiring Them Together with RunnableLambda

The challenge: Step 1 outputs a `Classification` object. Step 2 expects `{area}`, `{jurisdiction}`, `{sub_topic}`, and `{question}`. You need to transform the output.

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

def prepare_research_input(inputs):
    """Transform classification output into research input."""
    classification = inputs["classification"]
    return {
        "question": inputs["question"],
        "area": classification.area,
        "jurisdiction": classification.jurisdiction,
        "sub_topic": classification.sub_topic,
    }

def prepare_memo_input(inputs):
    """Transform research output into memo input."""
    research = inputs["research"]
    return {
        "question": inputs["question"],
        "area": inputs["area"],
        "jurisdiction": inputs["jurisdiction"],
        "cases": "\n".join(f"- {c.name} ({c.year}, {c.court})" for c in research.cases),
        "key_principles": "\n".join(f"- {p}" for p in research.key_principles),
    }
```

---

## RunnableParallel: Run Steps Side by Side

Sometimes you need to run multiple things and combine results. `RunnableParallel` runs branches concurrently:

```python
from langchain_core.runnables import RunnableParallel

# Run classification AND pass the question through
step1 = RunnableParallel(
    classification=classify_chain,
    question=RunnablePassthrough(),  # pass input through unchanged
)
```

`RunnablePassthrough` is the identity function — it passes the input through without modification. Useful for carrying data forward.

---

## The Full Pipeline

```python
from langchain_core.runnables import (
    RunnableParallel, RunnablePassthrough, RunnableLambda, RunnableSequence
)

# Step 1: Classify + carry question forward
step1 = RunnableParallel(
    classification=classify_chain,
    question=lambda x: x["question"],
)

# Step 2: Transform + research
step2 = RunnableLambda(prepare_research_input) | RunnableParallel(
    research=research_chain,
    question=lambda x: x["question"],
    area=lambda x: x["area"],
    jurisdiction=lambda x: x["jurisdiction"],
)

# Step 3: Transform + write memo
step3 = RunnableLambda(prepare_memo_input) | memo_chain

# Full pipeline
memo_pipeline = step1 | step2 | step3

# One call does everything
memo = memo_pipeline.invoke({"question": "Can a board member be held liable for approving a merger at below-market value in Delaware?"})
print(memo)
```

One `.invoke()`. Three LLM calls. Structured data flowing between them.

---

## RunnableBranch: Conditional Logic

Not every question needs the full pipeline. Simple questions (definitions, explanations) don't need case research.

```python
from langchain_core.runnables import RunnableBranch

# Route based on classification
router = RunnableBranch(
    # If it's a simple definition question, just answer directly
    (lambda x: x["classification"].sub_topic == "definition", 
     simple_answer_chain),
    
    # If it's a research question, run the full pipeline
    (lambda x: x["classification"].area in ["corporate", "contract", "tort"],
     full_research_pipeline),
    
    # Default: general answer
    general_chain,
)
```

Simple questions get fast, cheap answers. Complex questions get the full research treatment.

---

## Debugging Chains

Raj is skeptical: "How do I know what's happening inside this pipeline?"

### Option 1: Print intermediate steps

```python
from langchain_core.runnables import RunnableLambda

def debug_step(name):
    """Print intermediate values for debugging."""
    def _debug(x):
        print(f"\n{'='*40}")
        print(f"[DEBUG] {name}:")
        print(f"  {x}")
        print(f"{'='*40}\n")
        return x
    return RunnableLambda(_debug)

# Insert debug steps
chain = (
    step1 
    | debug_step("After classification") 
    | step2 
    | debug_step("After research") 
    | step3
)
```

### Option 2: Get intermediate results with `.invoke()` on sub-chains

```python
# Test each step independently
classification = classify_chain.invoke({"question": "..."})
print(f"Classified as: {classification.area} / {classification.jurisdiction}")

research = research_chain.invoke({
    "question": "...",
    "area": classification.area,
    "jurisdiction": classification.jurisdiction,
    "sub_topic": classification.sub_topic,
})
print(f"Found {len(research.cases)} cases")
```

Each chain is independently testable. That's the power of composition.

---

## Error Handling in Chains

What if the classification step fails? What if the research step returns no cases?

```python
from langchain_core.runnables import RunnableWithFallbacks

# If GPT-4o-mini fails, try Claude
research_with_fallback = research_chain.with_fallbacks(
    [research_chain_claude]  # same chain, different model
)

# Custom error handling
def handle_empty_research(inputs):
    """If no cases found, return a helpful message instead of crashing."""
    research = inputs.get("research")
    if not research or not research.cases:
        return {
            **inputs,
            "cases": "No relevant cases found",
            "key_principles": "Unable to identify key principles for this query",
        }
    return prepare_memo_input(inputs)
```

---

## Real-World Pattern: The Research Pipeline

Here's the complete, production-ready pipeline:

```python
# pipeline.py — NovaMind research memo pipeline
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda
from models import Classification, ResearchResult, CaseCitation

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- Chains ---
classify_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Classify this legal question by area and jurisdiction."),
        ("human", "{question}"),
    ])
    | llm.with_structured_output(Classification)
)

research_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Find relevant cases in {area} law, {jurisdiction}. Sub-topic: {sub_topic}."),
        ("human", "{question}"),
    ])
    | llm.with_structured_output(ResearchResult)
)

memo_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Write a research memo with: QUESTION, JURISDICTION, CASES, ANALYSIS, CONCLUSION."),
        ("human", "Q: {question}\nArea: {area}\nJurisdiction: {jurisdiction}\nCases: {cases}"),
    ])
    | llm
    | StrOutputParser()
)

# --- Pipeline ---
def _classify_and_carry(inputs):
    classification = classify_chain.invoke(inputs)
    return {**inputs, "area": classification.area, 
            "jurisdiction": classification.jurisdiction,
            "sub_topic": classification.sub_topic}

def _research_and_carry(inputs):
    research = research_chain.invoke(inputs)
    return {**inputs, "cases": research.cases, "key_principles": research.key_principles}

def _format_for_memo(inputs):
    return {
        "question": inputs["question"],
        "area": inputs["area"],
        "jurisdiction": inputs["jurisdiction"],
        "cases": "\n".join(f"- {c.name} ({c.year})" for c in inputs["cases"]),
    }

memo_pipeline = (
    RunnableLambda(_classify_and_carry)
    | RunnableLambda(_research_and_carry)
    | RunnableLambda(_format_for_memo)
    | memo_chain
)

# Usage
memo = memo_pipeline.invoke({
    "question": "Can a minority shareholder sue for oppression in Delaware?"
})
```

---

## What's Still Broken

The pipeline works. Elena runs it three times with the same question. She gets slightly different answers each time — not because the model is non-deterministic (temperature=0), but because there's no conversation context.

She asks a follow-up: "What about in New York instead?"

The system has no idea what "instead" refers to. Every request starts fresh. There's no memory.

> "I asked about Delaware fiduciary duty five minutes ago. Now I'm asking a follow-up. Why does it act like we've never spoken?" — Elena

That's Chapter 5 — memory.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| `RunnableSequence` (`\|`) | Chain steps sequentially |
| `RunnableParallel` | Run multiple branches concurrently |
| `RunnablePassthrough` | Pass input through unchanged |
| `RunnableLambda` | Custom transformation function |
| `RunnableBranch` | Conditional routing |
| `.with_fallbacks()` | Try alternatives on failure |
| Composition | Build complex pipelines from simple, testable chains |

---

[← Chapter 3](chapter-03-structured-output.md) · [Chapter 5: Memory →](chapter-05-memory.md)
