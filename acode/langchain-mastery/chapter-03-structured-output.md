# Chapter 3: Structured Output

[← Chapter 2](chapter-02-prompt-templates.md) · [Chapter 4: Chains →](chapter-04-chains.md)

---

## The Scene

Elena's case management system expects JSON. Not prose. Not markdown. JSON with specific fields.

She shows you the import format:

```json
{
  "cases": [
    {
      "name": "Revlon Inc. v. MacAndrews & Forbes Holdings",
      "year": 1986,
      "court": "Delaware Supreme Court",
      "relevance": "Established duty to maximize shareholder value in sale",
      "confidence": "high"
    }
  ]
}
```

You try adding "respond in JSON" to the prompt. The model sometimes wraps it in markdown code fences. Sometimes it adds a preamble. Sometimes the field names are different. Sometimes it's not valid JSON at all.

> "I can't have my import script crash because the AI felt creative today." — Elena

You need **guaranteed** structured output.

---

## The Naive Approach (and Why It Fails)

```python
# Don't do this
prompt = ChatPromptTemplate.from_messages([
    ("system", "Respond in JSON format with fields: name, year, court, relevance"),
    ("human", "Find precedents for {query}"),
])

result = chain.invoke({"query": "breach of fiduciary duty in Delaware"})
# Sometimes: {"name": "..."} ✓
# Sometimes: ```json\n{"name": "..."}\n``` ✗
# Sometimes: "Here are the cases:\n{..." ✗
# Sometimes: {"case_name": "..."} ✗ (wrong field name!)
```

The model is probabilistic. "Please respond in JSON" is a suggestion, not a guarantee.

---

## Pydantic Output: Type-Safe Responses

LangChain integrates with Pydantic to enforce structure. You define a schema, and the model MUST conform to it.

```python
from pydantic import BaseModel, Field
from typing import Literal

class CaseCitation(BaseModel):
    """A single legal case citation."""
    name: str = Field(description="Full case name")
    year: int = Field(description="Year of the decision")
    court: str = Field(description="Court that issued the decision")
    relevance: str = Field(description="Why this case is relevant, one sentence")
    confidence: Literal["high", "medium", "low"] = Field(
        description="How confident you are this citation is accurate"
    )

class ResearchResult(BaseModel):
    """Structured research output."""
    query: str = Field(description="The original research question")
    jurisdiction: str = Field(description="Legal jurisdiction")
    cases: list[CaseCitation] = Field(description="Relevant cases found")
    summary: str = Field(description="Brief overall summary")
    limitations: str = Field(description="What this research does NOT cover")
```

### Using `with_structured_output()`

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Bind the schema to the model
structured_llm = llm.with_structured_output(ResearchResult)

# Now it ALWAYS returns a ResearchResult object
result = structured_llm.invoke(
    "Find precedents for breach of fiduciary duty in Delaware"
)

# Type-safe access
print(result.query)          # "breach of fiduciary duty in Delaware"
print(result.jurisdiction)   # "Delaware"
for case in result.cases:
    print(f"  {case.name} ({case.year}, {case.court})")
    print(f"  Relevance: {case.relevance}")
    print(f"  Confidence: {case.confidence}")
```

Output:
```
breach of fiduciary duty in Delaware
Delaware
  Revlon Inc. v. MacAndrews & Forbes Holdings (1986, Delaware Supreme Court)
  Relevance: Established enhanced scrutiny for board actions in sale of company
  Confidence: high
  
  Stone v. Ritter (2006, Delaware Supreme Court)
  Relevance: Defined oversight liability as breach of duty of loyalty
  Confidence: high
```

No markdown fences. No preambles. No wrong field names. Guaranteed structure.

---

## In a Chain

You can use structured output in LCEL chains:

```python
from langchain_core.prompts import ChatPromptTemplate

research_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a legal researcher. Find relevant case precedents. "
     "Only cite cases you are confident exist. "
     "If unsure about a citation, set confidence to 'low'."),
    ("human", "Research: {query}"),
])

# Chain with structured output
research_chain = research_prompt | llm.with_structured_output(ResearchResult)

# Returns a ResearchResult, not a string
result = research_chain.invoke({"query": "piercing the corporate veil in California"})

# Directly serializable to JSON for Elena's system
import json
print(json.dumps(result.model_dump(), indent=2))
```

---

## Multiple Output Schemas

Different endpoints need different structures:

```python
class ContractSummary(BaseModel):
    """Structured contract summary."""
    parties: list[str] = Field(description="All parties to the contract")
    term: str = Field(description="Duration and key dates")
    obligations: list[str] = Field(description="Key obligations of each party")
    risks: list[str] = Field(description="Specific risks identified in the contract")
    governing_law: str = Field(description="Jurisdiction governing the contract")

class LegalQuestion(BaseModel):
    """Structured answer to a legal question."""
    answer: str = Field(description="Direct answer to the question")
    jurisdiction: str = Field(description="Applicable jurisdiction")
    key_statutes: list[str] = Field(description="Relevant statutes or regulations")
    caveats: list[str] = Field(description="Important limitations or exceptions")
    confidence: Literal["high", "medium", "low"]

# Different chains, different schemas
summarize_chain = summarize_prompt | llm.with_structured_output(ContractSummary)
question_chain = research_prompt | llm.with_structured_output(LegalQuestion)
```

Each chain guarantees its own output shape. The frontend knows exactly what to expect.

---

## Validation and Error Handling

Pydantic validates the output. If the model produces something invalid, you catch it:

```python
from pydantic import BaseModel, Field, field_validator

class CaseCitation(BaseModel):
    name: str
    year: int = Field(ge=1776, le=2026)  # reasonable year range
    court: str
    relevance: str
    confidence: Literal["high", "medium", "low"]
    
    @field_validator("name")
    @classmethod
    def name_must_contain_v(cls, v):
        """Case names should contain 'v.' or 'v' (versus)."""
        if " v. " not in v and " v " not in v:
            raise ValueError(f"'{v}' doesn't look like a case name (missing 'v.')")
        return v
```

If the model outputs `year: 2030` or a case name without "v." — Pydantic rejects it. You can retry or flag it for review.

---

## Enum Constraints

For fields with fixed options, use enums or Literals:

```python
from typing import Literal

class RiskAssessment(BaseModel):
    clause: str = Field(description="The specific contract clause")
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal[
        "termination", "liability", "ip_ownership", 
        "non_compete", "payment", "confidentiality"
    ]
    recommendation: str = Field(description="What to do about this risk")
```

The model can only choose from your predefined options. No creative interpretations.

---

## Fallback: When Structured Output Fails

Sometimes the model can't conform to your schema (complex nested structures, ambiguous input). Handle it gracefully:

```python
from langchain_core.runnables import RunnableWithFallbacks

# Primary: structured output
primary = research_prompt | llm.with_structured_output(ResearchResult)

# Fallback: just get the text and parse manually
fallback = research_prompt | llm | StrOutputParser()

# Try structured first, fall back to text
chain_with_fallback = primary.with_fallbacks([fallback])
```

---

## What You Built

```python
# models.py — NovaMind output schemas
from pydantic import BaseModel, Field
from typing import Literal

class CaseCitation(BaseModel):
    name: str = Field(description="Full case name, e.g. 'Smith v. Jones'")
    year: int = Field(ge=1776, le=2026, description="Year of decision")
    court: str = Field(description="Court name")
    relevance: str = Field(description="One-sentence relevance explanation")
    confidence: Literal["high", "medium", "low"]

class ResearchResult(BaseModel):
    query: str
    jurisdiction: str
    cases: list[CaseCitation]
    summary: str
    limitations: str

class ContractSummary(BaseModel):
    parties: list[str]
    term: str
    obligations: list[str]
    risks: list[str]
    governing_law: str

# chains.py
from langchain_openai import ChatOpenAI
from prompts import research_prompt, summarize_prompt

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

research_chain = research_prompt | llm.with_structured_output(ResearchResult)
summarize_chain = summarize_prompt | llm.with_structured_output(ContractSummary)
```

Elena can now import research results directly into her case management system. The JSON is always valid. The fields are always present. The confidence scores let her filter out uncertain citations.

---

## What's Still Broken

The research chain works for single questions. But Priya wants a pipeline:

1. Take a legal question
2. Identify the jurisdiction
3. Research relevant cases
4. Summarize the findings
5. Generate a memo

Five steps. Each depends on the output of the previous one. Right now you'd have to call each chain manually and wire the outputs together.

> "Can't we just... pipe them together? Like, the output of step 1 feeds into step 2?" — Priya

That's Chapter 4 — composing chains.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| `with_structured_output(Model)` | Force LLM to return a Pydantic model |
| Pydantic `BaseModel` | Define the exact shape of output |
| `Field(description=...)` | Guide the model on what each field means |
| `Literal[...]` | Constrain to specific allowed values |
| `field_validator` | Custom validation rules |
| `.with_fallbacks()` | Graceful degradation when structure fails |

---

[← Chapter 2](chapter-02-prompt-templates.md) · [Chapter 4: Chains →](chapter-04-chains.md)
