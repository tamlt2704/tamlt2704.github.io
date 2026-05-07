# Chapter 5: Memory

[← Chapter 4](chapter-04-chains.md) · [Chapter 6: RAG →](chapter-06-rag.md)

---

## The Scene

Elena is testing the chat interface. The conversation goes like this:

> **Elena:** "What's the statute of limitations for fraud in Delaware?"
> **AI:** "In Delaware, the statute of limitations for fraud is 3 years under 10 Del. C. § 8106..."
>
> **Elena:** "What about New York?"
> **AI:** "I'd be happy to help! Could you please clarify what you'd like to know about New York?"

The AI has amnesia. Every message is a fresh start. It doesn't remember that two seconds ago you were talking about fraud statutes.

Raj checks the code:

```python
# Current implementation — no memory
@app.route("/chat", methods=["POST"])
def chat():
    message = request.json["message"]
    result = chain.invoke({"question": message})  # no history!
    return jsonify({"response": result})
```

Every request is independent. The conversation context is gone.

---

## How LLMs "Remember"

LLMs are stateless. They don't remember previous calls. "Memory" is an illusion created by **sending the conversation history with every request**.

```
Request 1: [system, human("What's the SOL for fraud in DE?")]
Request 2: [system, human("What's the SOL for fraud in DE?"), ai("3 years..."), human("What about NY?")]
```

The model sees the full conversation every time. That's why it can answer follow-ups — it's reading the transcript.

The question is: how do you manage that transcript?

---

## Manual History (The Basics)

The simplest approach — maintain a list:

```python
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a legal research assistant. Be concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()

# Maintain history manually
history = []

def chat(question: str) -> str:
    response = chain.invoke({"history": history, "question": question})
    
    # Append to history
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=response))
    
    return response

# Conversation
print(chat("What's the SOL for fraud in Delaware?"))
# → "3 years under 10 Del. C. § 8106..."

print(chat("What about New York?"))
# → "In New York, the SOL for fraud is 6 years under CPLR § 213(8)..."
```

It works. The model sees the full conversation. But there's a problem.

---

## The Context Window Problem

After 20 messages, the history is 15,000 tokens. After 50 messages, it's 40,000 tokens. Eventually:

1. You hit the model's context window limit (128K for GPT-4o, but still finite)
2. You're paying for all those tokens on every request
3. The model gets confused by irrelevant old context

You need strategies to manage history size.

---

## Strategy 1: Window Memory

Keep only the last N messages:

```python
from langchain_core.messages import trim_messages

def get_trimmed_history(history, max_messages=20):
    """Keep only the last N messages."""
    return trim_messages(
        history,
        max_tokens=4000,          # or by token count
        strategy="last",           # keep most recent
        token_counter=llm,         # use the model to count tokens
        include_system=True,       # always keep system message
    )
```

Simple. Effective. But you lose early context — if the user said "I'm working on the Acme Corp case" 30 messages ago, that's gone.

---

## Strategy 2: Summary Memory

Summarize old messages instead of dropping them:

```python
from langchain_core.prompts import ChatPromptTemplate

summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize this conversation in 2-3 sentences, preserving key facts "
     "(case names, jurisdictions, dates, decisions made)."),
    MessagesPlaceholder(variable_name="messages"),
])

summary_chain = summarize_prompt | llm | StrOutputParser()

class ConversationWithSummary:
    def __init__(self, max_messages=10):
        self.summary = ""
        self.recent_messages = []
        self.max_messages = max_messages
    
    def add_message(self, role, content):
        if role == "human":
            self.recent_messages.append(HumanMessage(content=content))
        else:
            self.recent_messages.append(AIMessage(content=content))
        
        # When history gets too long, summarize older messages
        if len(self.recent_messages) > self.max_messages:
            self._compress()
    
    def _compress(self):
        """Summarize older messages, keep recent ones."""
        old = self.recent_messages[:self.max_messages // 2]
        self.recent_messages = self.recent_messages[self.max_messages // 2:]
        
        new_summary = summary_chain.invoke({"messages": old})
        self.summary = f"{self.summary}\n{new_summary}".strip()
    
    def get_messages(self):
        """Return summary + recent messages for the prompt."""
        messages = []
        if self.summary:
            messages.append(SystemMessage(
                content=f"Previous conversation summary: {self.summary}"
            ))
        messages.extend(self.recent_messages)
        return messages
```

Old context is compressed into a summary. Recent messages stay verbatim. You get the best of both worlds.

---

## Strategy 3: Per-Session Memory with LangGraph (Preview)

For production, you need memory that persists across requests and is tied to a session/user. LangGraph (Chapter 11+) handles this natively with checkpointing. But here's the pattern:

```python
from langgraph.checkpoint.memory import MemorySaver

# Memory persists across invocations for the same thread
memory = MemorySaver()

# Each conversation gets a thread_id
config = {"configurable": {"thread_id": "elena-session-42"}}

# The graph remembers everything for this thread
result = graph.invoke({"question": "What about NY?"}, config=config)
```

We'll build this properly in Part 3. For now, let's use the manual approach.

---

## Production Pattern: Session-Based Chat

```python
# chat_service.py — NovaMind chat with memory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, trim_messages

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a legal research assistant for NovaMind. "
     "Be precise and concise. Reference earlier parts of the conversation "
     "when relevant. Never invent case citations."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()

# In-memory session store (use Redis/DB in production)
sessions: dict[str, list] = {}

def chat(session_id: str, question: str) -> str:
    """Chat with conversation memory."""
    # Get or create session history
    if session_id not in sessions:
        sessions[session_id] = []
    
    history = sessions[session_id]
    
    # Trim to last 4000 tokens
    trimmed = trim_messages(
        history,
        max_tokens=4000,
        strategy="last",
        token_counter=llm,
    )
    
    # Get response
    response = chain.invoke({"history": trimmed, "question": question})
    
    # Save to history
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=response))
    
    return response
```

### FastAPI Integration

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    response = chat(req.session_id, req.message)
    return ChatResponse(response=response)
```

Now Elena can have a conversation:

```
POST /chat {"session_id": "elena-1", "message": "SOL for fraud in Delaware?"}
→ "3 years under 10 Del. C. § 8106..."

POST /chat {"session_id": "elena-1", "message": "What about New York?"}
→ "In New York, the SOL for fraud is 6 years under CPLR § 213(8)..."

POST /chat {"session_id": "elena-1", "message": "Which is longer?"}
→ "New York's 6-year SOL is longer than Delaware's 3-year SOL for fraud."
```

Context preserved. Follow-ups work.

---

## Memory Anti-Patterns

| Anti-Pattern | Problem |
|---|---|
| Unlimited history | Hits context window, costs explode |
| No history at all | AI has amnesia, can't handle follow-ups |
| Sharing history across users | Privacy violation, confused responses |
| Storing history only in memory | Lost on server restart |
| Including irrelevant history | Confuses the model, wastes tokens |

---

## What's Still Broken

Memory works. Elena can have conversations. But she asks:

> "I uploaded a 200-page contract last week. Can you tell me what Section 4.2 says about indemnification?"

The AI has no idea. It wasn't in the conversation history. It's not in the prompt. The contract exists in a file somewhere, but the AI can't access it.

> "I need it to know our documents. Not just what I type in chat — the actual case files, contracts, and precedents we've uploaded."

That's RAG — Retrieval Augmented Generation. Chapter 6.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| `MessagesPlaceholder` | Inject dynamic history into prompts |
| `trim_messages` | Keep history within token budget |
| Window memory | Keep last N messages |
| Summary memory | Compress old messages into a summary |
| Session-based storage | Isolate conversations per user/session |
| Token counting | Track cost and stay within limits |

---

[← Chapter 4](chapter-04-chains.md) · [Chapter 6: RAG →](chapter-06-rag.md)
