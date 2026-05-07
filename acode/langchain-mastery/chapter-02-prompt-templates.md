# Chapter 2: Prompt Templates

[← Chapter 1](chapter-01-first-chain.md) · [Chapter 3: Structured Output →](chapter-03-structured-output.md)

---

## The Scene

Elena sends you three contract summaries from the AI. They look like this:

**Summary 1:**
> "Sure! Here's a summary of the contract. The agreement is between Acme Corp and..."

**Summary 2:**
> "This contract establishes a partnership between two parties for the purpose of..."

**Summary 3:**
> "**PARTIES:** Acme Corp (Licensor), Beta Inc (Licensee)\n**TERM:** 3 years\n**KEY OBLIGATIONS:**..."

Same prompt, same model, three different formats. Elena is not amused.

> "I need every summary to look the same. Parties. Term. Key obligations. Risks. Every time. I'm putting these in client reports."

You need to control the output format — not by hoping the model cooperates, but by engineering the prompt.

---

## The Problem with Hardcoded Prompts

The prototype has this:

```python
messages = [
    {"role": "system", "content": "You are a legal research assistant."},
    {"role": "user", "content": user_message}
]
```

Problems:
1. The system message is vague — no format instructions
2. The user message is raw — no structure
3. Nothing is reusable — every endpoint has its own copy-pasted prompt
4. No variables — can't inject context dynamically

---

## ChatPromptTemplate

A prompt template is a reusable blueprint with variables:

```python
from langchain_core.prompts import ChatPromptTemplate

# Define once, reuse everywhere
summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a legal document analyst. "
     "When summarizing contracts, ALWAYS use this exact format:\n\n"
     "PARTIES: [list all parties and their roles]\n"
     "TERM: [duration and key dates]\n"
     "KEY OBLIGATIONS: [bullet list of main obligations]\n"
     "RISKS: [bullet list of potential risks or concerns]\n\n"
     "Be precise. Use the document's exact language for key terms."),
    ("human", "Summarize this contract:\n\n{contract_text}"),
])
```

The `{contract_text}` is a variable. At runtime, you fill it in:

```python
chain = summarize_prompt | llm | parser

result = chain.invoke({
    "contract_text": "This Software License Agreement is entered into by..."
})
```

Now every summary follows the same structure. Every time.

---

## Multiple Variables

Prompts can have multiple placeholders:

```python
research_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a legal researcher specializing in {jurisdiction} law. "
     "Focus on cases from the past {years} years. "
     "Always cite case names with year and court."),
    ("human", "{question}"),
])

chain = research_prompt | llm | parser

# Different jurisdictions, same chain
delaware = chain.invoke({
    "jurisdiction": "Delaware corporate",
    "years": 10,
    "question": "What is the business judgment rule?"
})

california = chain.invoke({
    "jurisdiction": "California employment",
    "years": 5,
    "question": "What constitutes wrongful termination?"
})
```

One template. Multiple use cases. No copy-paste.

---

## Few-Shot Prompting

Elena's next complaint: "The summaries are okay, but the risk analysis is too generic. It says things like 'there may be financial risk.' I need it to identify *specific* risks from the contract language."

The fix: show the model what good output looks like.

```python
few_shot_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a legal document analyst. Summarize contracts using the format below. "
     "For risks, identify SPECIFIC clauses that could be problematic, not generic warnings."),
    
    # Example 1: show what good output looks like
    ("human", "Summarize this contract:\n\nThis Consulting Agreement between Alpha Corp "
     "(Client) and Jane Smith (Consultant) provides that Consultant shall perform "
     "data analysis services for a period of 12 months at $150/hour. Client may "
     "terminate without cause with 7 days notice. All work product belongs to Client. "
     "Consultant may not work for competitors for 2 years after termination."),
    
    ("ai", 
     "PARTIES: Alpha Corp (Client), Jane Smith (Consultant)\n"
     "TERM: 12 months, $150/hour\n"
     "KEY OBLIGATIONS:\n"
     "• Consultant performs data analysis services\n"
     "• All work product assigned to Client\n"
     "RISKS:\n"
     "• 7-day termination without cause — Consultant has minimal job security\n"
     "• 2-year non-compete post-termination — unusually broad, may be unenforceable "
     "depending on jurisdiction\n"
     "• No cap on hours — potential for scope creep without rate renegotiation"),
    
    # The actual request
    ("human", "Summarize this contract:\n\n{contract_text}"),
])
```

The model sees a concrete example of the quality you expect. The risk analysis becomes specific: it points to actual clauses, not vague warnings.

---

## MessagesPlaceholder: Dynamic History

For the chat endpoint, you need conversation history — but you don't know how many messages there will be at template-definition time.

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a legal assistant. Be concise and precise."),
    MessagesPlaceholder(variable_name="history"),  # dynamic!
    ("human", "{question}"),
])
```

At runtime, you inject the conversation history:

```python
from langchain_core.messages import HumanMessage, AIMessage

result = chain.invoke({
    "history": [
        HumanMessage(content="What is a tort?"),
        AIMessage(content="A tort is a civil wrong that causes harm..."),
        HumanMessage(content="Give me an example"),
        AIMessage(content="A common example is negligence..."),
    ],
    "question": "How does that differ from a breach of contract?"
})
```

The model sees the full conversation and can reference earlier context. This is the foundation for memory (Chapter 5).

---

## Partial Prompts

Some variables are known at setup time, not at runtime. You can partially fill a template:

```python
# At app startup: we know the jurisdiction
base_prompt = ChatPromptTemplate.from_messages([
    ("system", "You specialize in {jurisdiction} law. Current date: {today}."),
    ("human", "{question}"),
])

# Partial: fill what we know now
from datetime import date
ny_prompt = base_prompt.partial(
    jurisdiction="New York",
    today=date.today().isoformat(),
)

# At runtime: only need the question
chain = ny_prompt | llm | parser
answer = chain.invoke({"question": "What is the filing deadline for a tort claim?"})
```

---

## Prompt Composition

Complex workflows need prompts built from smaller pieces:

```python
# Reusable system instructions
LEGAL_SYSTEM = (
    "You are a legal research assistant for NovaMind. "
    "Rules:\n"
    "1. Never invent case citations. If unsure, say 'I could not verify this.'\n"
    "2. Always specify the jurisdiction.\n"
    "3. Cite cases as: Case Name (Year, Court).\n"
    "4. If a question is outside your expertise, say so.\n"
)

# Different prompts share the same base rules
research_prompt = ChatPromptTemplate.from_messages([
    ("system", LEGAL_SYSTEM + "Focus on finding relevant precedents."),
    ("human", "{question}"),
])

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", LEGAL_SYSTEM + "Summarize documents in the standard format."),
    ("human", "Summarize:\n\n{document}"),
])

draft_prompt = ChatPromptTemplate.from_messages([
    ("system", LEGAL_SYSTEM + "Draft legal documents. Use formal language."),
    ("human", "Draft a {document_type} for:\n\n{details}"),
])
```

One set of rules. Multiple specialized prompts. Change the rules in one place, every prompt updates.

---

## Testing Prompts

Raj insists: "Prompts are code. They need tests."

```python
# test_prompts.py
def test_summarize_prompt_has_required_sections():
    """The system message must instruct the model to use our format."""
    messages = summarize_prompt.format_messages(contract_text="test")
    system_msg = messages[0].content
    
    assert "PARTIES" in system_msg
    assert "TERM" in system_msg
    assert "KEY OBLIGATIONS" in system_msg
    assert "RISKS" in system_msg

def test_research_prompt_forbids_hallucination():
    """The system message must tell the model not to invent citations."""
    messages = research_prompt.format_messages(question="test")
    system_msg = messages[0].content
    
    assert "never invent" in system_msg.lower() or "do not fabricate" in system_msg.lower()
```

Prompts are the most fragile part of your system. Test them like you test code.

---

## What You Built

```python
# prompts.py — NovaMind prompt library
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

LEGAL_SYSTEM = (
    "You are a legal research assistant for NovaMind. "
    "Rules:\n"
    "1. Never invent case citations. If unsure, say 'I could not verify this.'\n"
    "2. Always specify the jurisdiction.\n"
    "3. Cite cases as: Case Name (Year, Court).\n"
    "4. If a question is outside your expertise, say so.\n"
)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", LEGAL_SYSTEM + "Be concise. Ask clarifying questions if needed."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

summarize_prompt = ChatPromptTemplate.from_messages([
    ("system",
     LEGAL_SYSTEM +
     "When summarizing contracts, ALWAYS use this format:\n\n"
     "PARTIES: [list all parties and their roles]\n"
     "TERM: [duration and key dates]\n"
     "KEY OBLIGATIONS: [bullet list]\n"
     "RISKS: [specific risks referencing actual clauses]\n"),
    ("human", "Summarize this contract:\n\n{contract_text}"),
])

research_prompt = ChatPromptTemplate.from_messages([
    ("system",
     LEGAL_SYSTEM +
     "Focus on finding relevant precedents. "
     "Specify jurisdiction and court level for each citation."),
    ("human", "{question}"),
])
```

---

## What's Still Broken

Elena tests the research endpoint. She asks: "Find precedents for breach of fiduciary duty in Delaware."

The AI responds with a nicely formatted paragraph. But Elena needs structured data — case name, year, court, relevance score — so she can sort and filter in her case management tool.

> "I don't want prose. I want a table. Actually, I want JSON I can import into our system."

You need the model to output structured data — not free-form text. That's Chapter 3.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| `ChatPromptTemplate` | Reusable prompt with variables (`{var}`) |
| `from_messages()` | Define system/human/ai message sequence |
| Few-shot examples | Show the model what good output looks like |
| `MessagesPlaceholder` | Inject dynamic conversation history |
| `.partial()` | Pre-fill known variables |
| Prompt composition | Share rules across multiple prompts |

---

[← Chapter 1](chapter-01-first-chain.md) · [Chapter 3: Structured Output →](chapter-03-structured-output.md)
