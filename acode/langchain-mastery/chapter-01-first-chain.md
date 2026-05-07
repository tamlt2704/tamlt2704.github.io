# Chapter 1: Your First Chain

[← Overview](chapter-00-overview.md) · [Chapter 2: Prompt Templates →](chapter-02-prompt-templates.md)

---

## The Scene

It's Monday morning. Priya shows you the prototype. You open the Flask app, type a question:

> "What are the key precedents for breach of fiduciary duty in Delaware?"

The AI responds with a confident, well-structured answer. It cites *Henderson v. Kite Pharma (2017)* and *Morrison v. Berry (2019)*.

Elena, the lead lawyer, reads it. Her face goes pale.

> "Henderson v. Kite Pharma isn't about fiduciary duty. And Morrison v. Berry — the year is wrong. You can't cite this in a filing. A judge will sanction us."

Priya turns to you: "Step one — let's at least get the AI calls structured properly. Right now it's a raw `openai.chat.completions.create()` call. We need something we can compose, test, and extend."

Time to replace the raw API call with LangChain.

---

## What is LangChain?

LangChain is a framework for building applications with LLMs. Instead of making raw API calls, you work with composable building blocks:

```
Raw API call:          LangChain:
─────────────          ──────────
One function           Composable components
Hardcoded prompt       Prompt templates
String output          Parsed, typed output
No memory              Memory built in
No tools               Tool integration
No tracing             Observable by default
```

The core idea: **everything is a Runnable**. A prompt is a Runnable. A model is a Runnable. A parser is a Runnable. You pipe them together like Unix commands.

---

## ChatModels and Messages

The foundation of everything in LangChain is the **ChatModel** — a wrapper around an LLM that speaks in messages.

```python
from langchain_openai import ChatOpenAI

# Create a model instance
llm = ChatOpenAI(
    model="gpt-4o-mini",   # cheaper, faster — good for dev
    temperature=0,          # deterministic output (important for legal!)
)

# The simplest possible call
response = llm.invoke("What is a tort?")
print(response.content)
```

Output:
```
A tort is a civil wrong that causes harm to another person, 
giving the injured party the right to sue for damages...
```

### Messages Have Roles

LLMs don't just receive text — they receive **messages** with roles:

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="You are a legal research assistant. Be precise. Cite sources."),
    HumanMessage(content="What is the statute of limitations for fraud in New York?"),
]

response = llm.invoke(messages)
print(response.content)
```

| Role | Purpose |
|------|---------|
| `SystemMessage` | Sets behavior, personality, constraints |
| `HumanMessage` | The user's input |
| `AIMessage` | The model's previous responses (for context) |

The system message is your control lever. It's where you tell the AI to be precise, to cite sources, to refuse to speculate.

---

## From Raw API to LangChain

Here's the prototype's code:

```python
# Before: raw OpenAI call
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a legal research assistant."},
        {"role": "user", "content": user_message}
    ],
)
answer = response.choices[0].message.content
```

Here's the LangChain equivalent:

```python
# After: LangChain
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

messages = [
    SystemMessage(content="You are a legal research assistant."),
    HumanMessage(content=user_message),
]

response = llm.invoke(messages)
answer = response.content
```

"That's the same thing with extra steps," Raj says, looking over your shoulder.

He's right — for now. The power shows up when you start composing.

---

## LCEL: The Pipe Operator

LangChain Expression Language (LCEL) lets you chain components with the `|` operator. Each component is a **Runnable** — it takes input and produces output.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Define the chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a legal research assistant. Be concise."),
    ("human", "{question}"),
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# Compose with pipe
chain = prompt | llm | parser

# Run it
answer = chain.invoke({"question": "What is habeas corpus?"})
print(answer)
```

What's happening:

```
{"question": "What is habeas corpus?"}
         │
         ▼
┌─────────────────┐
│  Prompt Template │  → Formats the messages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    ChatModel     │  → Calls the LLM
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Output Parser   │  → Extracts the string
└────────┬────────┘
         │
         ▼
"Habeas corpus is a legal principle that..."
```

Each step transforms the data and passes it to the next. Like Unix pipes: `cat file | grep pattern | sort`.

---

## Streaming

Elena is testing the chat. She types a question and stares at a blank screen for 8 seconds before the full response appears.

> "Is it broken? Nothing's happening."

LLMs generate tokens one at a time. You can stream them:

```python
# Stream tokens as they're generated
for chunk in chain.stream({"question": "Explain res judicata"}):
    print(chunk, end="", flush=True)
```

The response appears word by word — feels instant, even if the full generation takes 5 seconds.

---

## Async Support

The Flask prototype handles one request at a time. When 10 lawyers ask questions simultaneously, 9 of them wait.

LangChain is async-native:

```python
import asyncio

async def research(question: str) -> str:
    return await chain.ainvoke({"question": question})

# Handle multiple requests concurrently
results = await asyncio.gather(
    research("What is a tort?"),
    research("Define negligence"),
    research("Explain strict liability"),
)
```

Three questions, processed concurrently. No blocking.

---

## Batch Processing

Priya wants to generate summaries for 50 case files overnight:

```python
questions = [
    {"question": "Summarize the key holding in Roe v. Wade"},
    {"question": "Summarize the key holding in Brown v. Board"},
    {"question": "Summarize the key holding in Miranda v. Arizona"},
    # ... 47 more
]

# Process in batch (with concurrency control)
results = chain.batch(questions, config={"max_concurrency": 5})
```

Batch sends multiple requests with controlled parallelism. No rate-limit explosions.

---

## Swapping Models

Raj asks: "What if OpenAI goes down? What if we want to compare models?"

Because everything is a Runnable, swapping models is one line:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# OpenAI
chain_openai = prompt | ChatOpenAI(model="gpt-4o-mini") | parser

# Anthropic
chain_claude = prompt | ChatAnthropic(model="claude-3-5-sonnet-20241022") | parser

# Local (Ollama)
from langchain_community.chat_models import ChatOllama
chain_local = prompt | ChatOllama(model="llama3.1") | parser
```

Same prompt, same parser, different brain. The chain doesn't care which model powers it.

---

## What You Built

```python
# legal_chain.py — NovaMind v0.1
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a legal research assistant for a law firm. "
     "Be precise and concise. If you are unsure about something, "
     "say so explicitly. Never invent case citations."),
    ("human", "{question}"),
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

chain = prompt | llm | parser

# Usage
if __name__ == "__main__":
    answer = chain.invoke({
        "question": "What is the standard for piercing the corporate veil in Delaware?"
    })
    print(answer)
```

---

## What's Still Broken

You show Elena the new system. She asks:

> "Summarize this contract for me."

You realize: the prompt says "Never invent case citations" — but the output is still unstructured prose. Sometimes it's a paragraph. Sometimes it's bullet points. Sometimes it starts with "Sure!" and sometimes it dives straight in.

Elena: "I need consistent formatting. Every summary should have: parties, key terms, obligations, and risks. Every time. Not sometimes."

That's Chapter 2 — prompt templates and few-shot examples.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| `ChatOpenAI` | Wrapper around OpenAI's chat API |
| Messages (System/Human/AI) | Structured input with roles |
| LCEL (`\|` operator) | Compose components into chains |
| `StrOutputParser` | Extract string from model response |
| `.invoke()` | Run the chain (sync) |
| `.stream()` | Stream tokens as they generate |
| `.ainvoke()` | Run async |
| `.batch()` | Process multiple inputs in parallel |

---

[← Overview](chapter-00-overview.md) · [Chapter 2: Prompt Templates →](chapter-02-prompt-templates.md)
