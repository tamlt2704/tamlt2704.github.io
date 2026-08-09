# Chapter 45: LangChain & LangGraph — Build AI Agents and RAG Applications

## What you'll learn

- What LangChain is and its core abstractions (models, prompts, chains, retrievers, agents)
- Building a RAG (Retrieval-Augmented Generation) pipeline
- Tool-calling agents that can search the web, query databases, and execute code
- LangGraph: stateful, multi-step agent workflows with cycles and branching
- Memory: short-term (conversation) and long-term (vector store)
- Build: a research assistant, a customer support bot, and a multi-agent system

---

## PART 1: LangChain Fundamentals

## 45.1 What LangChain does

LangChain is a framework for building applications powered by LLMs (Large Language Models). It provides:

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                        │
├─────────────────────────────────────────────────────────────┤
│  LangChain provides:                                         │
│                                                              │
│  Models    — unified interface to OpenAI, Anthropic, Ollama  │
│  Prompts   — templates with variables, system messages       │
│  Chains    — compose multiple steps (prompt → LLM → parse)   │
│  Retrieval — load docs, split, embed, vector store, query    │
│  Agents    — LLM decides which tools to use                  │
│  Memory    — conversation history, summaries                 │
│  Output    — structured parsing (JSON, lists, objects)       │
└─────────────────────────────────────────────────────────────┘
```

## 45.2 Setup

```bash
pip install langchain langchain-openai langchain-community
pip install chromadb     # vector store
pip install tiktoken     # token counting
pip install python-dotenv
```

```python
# .env
OPENAI_API_KEY=sk-...
```

```python
from dotenv import load_dotenv
load_dotenv()
```

## 45.3 Chat models — the foundation

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Create model
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Simple invocation
response = llm.invoke([
    SystemMessage(content="You are a helpful coding assistant."),
    HumanMessage(content="Explain recursion in one sentence."),
])
print(response.content)
# "Recursion is when a function calls itself with a smaller input until reaching a base case."

# Streaming
for chunk in llm.stream([HumanMessage(content="Write a haiku about Python")]):
    print(chunk.content, end="", flush=True)
```

## 45.4 Prompt templates

```python
from langchain_core.prompts import ChatPromptTemplate

# Template with variables
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert {language} developer. Be concise."),
    ("human", "{question}"),
])

# Fill in variables
messages = prompt.invoke({
    "language": "Python",
    "question": "How do I read a file?",
})

response = llm.invoke(messages)
print(response.content)
```

## 45.5 Chains — composing steps with LCEL (LangChain Expression Language)

```python
from langchain_core.output_parsers import StrOutputParser

# Chain: prompt → model → parse output
chain = prompt | llm | StrOutputParser()

# Invoke the whole chain
result = chain.invoke({
    "language": "JavaScript",
    "question": "How do I fetch a URL?",
})
print(result)  # string response

# Chains are composable (pipe operator |)
# prompt | llm | parser is equivalent to:
# parser(llm(prompt(input)))
```

## 45.6 Structured output (JSON parsing)

```python
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

# Define output schema
class CodeReview(BaseModel):
    issues: list[str] = Field(description="List of issues found")
    severity: str = Field(description="Overall severity: low, medium, high")
    suggestion: str = Field(description="Main improvement suggestion")

# Create parser
parser = JsonOutputParser(pydantic_object=CodeReview)

# Include format instructions in prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Review the following code. {format_instructions}"),
    ("human", "{code}"),
])

chain = prompt | llm | parser

result = chain.invoke({
    "code": "def add(a, b): return a + b",
    "format_instructions": parser.get_format_instructions(),
})
# result = {"issues": [...], "severity": "low", "suggestion": "..."}
```

**Or use LLM's native structured output (simpler):**
```python
# With OpenAI function calling
structured_llm = llm.with_structured_output(CodeReview)
result = structured_llm.invoke("Review this code: def add(a,b): return a+b")
# result is a CodeReview object
```

---

## PART 2: RAG (Retrieval-Augmented Generation)

## 45.7 What is RAG?

```
User question: "What's our refund policy?"

Without RAG:
  LLM responds from training data → hallucination risk, outdated info

With RAG:
  1. RETRIEVE: search your documents for relevant chunks
  2. AUGMENT: inject those chunks into the prompt as context
  3. GENERATE: LLM answers using YOUR data as source

┌──────────┐     ┌─────────────────┐     ┌─────────┐
│ Question │────►│  Vector Search  │────►│   LLM   │────► Answer
└──────────┘     │  (find relevant │     │ (answer │
                 │   chunks)       │     │  using  │
                 └────────┬────────┘     │ context)│
                          │              └─────────┘
                 ┌────────▼────────┐
                 │  Your Documents │
                 │  (embedded in   │
                 │   vector store) │
                 └─────────────────┘
```

## 45.8 Build a RAG pipeline

```python
from langchain_community.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 1. LOAD documents
loader = WebBaseLoader("https://docs.example.com/refund-policy")
docs = loader.load()

# Or from files:
# loader = PyPDFLoader("company_handbook.pdf")
# loader = TextLoader("faq.txt")

# 2. SPLIT into chunks (LLMs have limited context windows)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # characters per chunk
    chunk_overlap=200,     # overlap between chunks (don't lose context at boundaries)
    separators=["\n\n", "\n", ". ", " "]  # split at paragraphs first, then sentences
)
chunks = splitter.split_documents(docs)
print(f"Split into {len(chunks)} chunks")

# 3. EMBED and store (convert text → vectors, store in vector DB)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # persist to disk
)

# 4. CREATE retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",     # or "mmr" (diverse results)
    search_kwargs={"k": 4},       # return top 4 chunks
)

# 5. BUILD the RAG chain
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """Answer the question based ONLY on the following context.
If the answer isn't in the context, say "I don't have that information."

Context:
{context}"""),
    ("human", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

# 6. QUERY
answer = rag_chain.invoke("What is the return window for electronics?")
print(answer)
```

## 45.9 RAG improvements

```python
# Multi-query retrieval (rephrase question multiple ways → broader search)
from langchain.retrievers.multi_query import MultiQueryRetriever

multi_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm,
)
# Generates 3 variations of the question, searches each, deduplicates results

# Contextual compression (rerank/filter retrieved chunks)
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever,
)
# LLM extracts only the relevant portions from each chunk

# Hybrid search (combine vector similarity + keyword BM25)
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

bm25 = BM25Retriever.from_documents(chunks, k=4)
vector = vectorstore.as_retriever(search_kwargs={"k": 4})
ensemble = EnsembleRetriever(retrievers=[bm25, vector], weights=[0.4, 0.6])
```

---

## PART 3: Agents — LLMs That Use Tools

## 45.10 What is an agent?

```
Chain:  input → fixed steps → output (deterministic)
Agent:  input → LLM DECIDES which tool → execute → observe → decide again → output (dynamic)
```

The LLM acts as a reasoning engine that can:
- Decide which tool to call (search, calculator, database, API)
- Interpret tool results
- Call more tools if needed
- Generate a final answer

## 45.11 Build an agent with tools

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    # In production: use Tavily, SerpAPI, or Brave Search
    return f"Search results for: {query} — [simulated results]"

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        return str(eval(expression))  # ⚠️ use a safe evaluator in production
    except Exception as e:
        return f"Error: {e}"

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # In production: call a weather API
    return f"Weather in {city}: 22°C, partly cloudy"

# Create agent
llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [search_web, calculate, get_weather]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools when needed to answer accurately."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),  # where tool call/response history goes
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run
result = agent_executor.invoke({
    "input": "What's 15% tip on $87.50, and what's the weather in Tokyo?"
})
print(result["output"])
```

**Agent execution trace (verbose=True):**
```
> Entering new AgentExecutor chain...
Thought: I need to calculate the tip and check the weather. Let me do both.

Action: calculate
Action Input: 87.50 * 0.15
Observation: 13.125

Action: get_weather
Action Input: Tokyo
Observation: Weather in Tokyo: 22°C, partly cloudy

Final Answer: A 15% tip on $87.50 is $13.13. The weather in Tokyo is 22°C and partly cloudy.
```

## 45.12 Custom tools for real applications

```python
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase

# Database query tool
db = SQLDatabase.from_uri("postgresql://user:pass@localhost/ecommerce")

@tool
def query_database(sql: str) -> str:
    """Execute a read-only SQL query against the e-commerce database.
    Available tables: users, products, orders, order_items.
    Always use LIMIT to avoid huge results."""
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries allowed"
    return db.run(sql)

# Document search tool (your RAG pipeline as a tool!)
@tool
def search_docs(query: str) -> str:
    """Search the company knowledge base for information about policies, procedures, and FAQs."""
    docs = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

# API call tool
@tool
def create_support_ticket(subject: str, description: str, priority: str = "medium") -> str:
    """Create a customer support ticket. Priority: low, medium, high."""
    # In production: call your ticketing API
    ticket_id = "TKT-" + str(hash(subject))[:6]
    return f"Created ticket {ticket_id}: {subject} (priority: {priority})"
```

---

## PART 4: LangGraph — Stateful Agent Workflows

## 45.13 What is LangGraph?

LangChain agents are simple loops (decide → act → observe → repeat). LangGraph gives you:

- **Explicit state** — typed state that flows through the graph
- **Conditional routing** — different paths based on state/LLM output
- **Cycles** — loop back to earlier nodes (iterative refinement)
- **Human-in-the-loop** — pause and wait for human approval
- **Parallel execution** — run independent steps simultaneously
- **Persistence** — save/resume workflows across sessions

```
LangChain Agent:         LangGraph:
                         ┌───────────────────────────────┐
LLM → Tool → LLM →      │  research ──► analyze ──────► │
  (simple loop)          │     ↑              │         │
                         │     │         ┌────▼────┐    │
                         │     └─────────│ decide  │    │
                         │               │ (route) │    │
                         │               └────┬────┘    │
                         │                    │         │
                         │              ┌─────▼─────┐   │
                         │              │  respond   │   │
                         │              └───────────┘   │
                         └───────────────────────────────┘
```

## 45.14 Setup LangGraph

```bash
pip install langgraph
```

## 45.15 Build a research assistant with LangGraph

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

# 1. Define state (what flows through the graph)
class ResearchState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # append-only message list
    research_notes: str
    sources: list[str]
    draft: str
    iteration: int

# 2. Define nodes (functions that process state)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def research_node(state: ResearchState) -> dict:
    """Search for information on the topic."""
    messages = state["messages"]
    topic = messages[-1].content if messages else ""

    # Use tools to research (simplified)
    response = llm.invoke([
        {"role": "system", "content": "You are a research assistant. Find key facts about the topic. Be thorough."},
        {"role": "human", "content": f"Research this topic: {topic}\n\nExisting notes: {state.get('research_notes', '')}"},
    ])

    return {
        "research_notes": state.get("research_notes", "") + "\n" + response.content,
        "messages": [AIMessage(content=f"Research complete: {response.content[:100]}...")],
        "iteration": state.get("iteration", 0) + 1,
    }

def analyze_node(state: ResearchState) -> dict:
    """Analyze research and identify gaps."""
    response = llm.invoke([
        {"role": "system", "content": "Analyze the research notes. Identify gaps or areas needing more research. If sufficient, say 'SUFFICIENT'."},
        {"role": "human", "content": f"Research notes:\n{state['research_notes']}"},
    ])

    return {
        "messages": [AIMessage(content=response.content)],
    }

def write_node(state: ResearchState) -> dict:
    """Write the final response based on research."""
    response = llm.invoke([
        {"role": "system", "content": "Write a comprehensive answer based on the research notes. Cite sources where possible."},
        {"role": "human", "content": f"Research:\n{state['research_notes']}\n\nOriginal question: {state['messages'][0].content}"},
    ])

    return {
        "draft": response.content,
        "messages": [AIMessage(content=response.content)],
    }

# 3. Define routing (conditional edges)
def should_continue_research(state: ResearchState) -> str:
    """Decide: more research needed or ready to write?"""
    if state.get("iteration", 0) >= 3:
        return "write"  # max iterations reached

    last_message = state["messages"][-1].content
    if "SUFFICIENT" in last_message.upper():
        return "write"

    return "research"  # loop back

# 4. Build the graph
workflow = StateGraph(ResearchState)

# Add nodes
workflow.add_node("research", research_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("write", write_node)

# Add edges
workflow.set_entry_point("research")
workflow.add_edge("research", "analyze")
workflow.add_conditional_edges(
    "analyze",
    should_continue_research,
    {"research": "research", "write": "write"},
)
workflow.add_edge("write", END)

# Compile
graph = workflow.compile()

# 5. Run
result = graph.invoke({
    "messages": [HumanMessage(content="What are the latest developments in quantum computing?")],
    "research_notes": "",
    "sources": [],
    "draft": "",
    "iteration": 0,
})
print(result["draft"])
```

## 45.16 LangGraph patterns

### Human-in-the-loop (approval before action)

```python
from langgraph.checkpoint.memory import MemorySaver

# Add checkpointer for persistence
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory, interrupt_before=["write"])

# Run until interrupt
config = {"configurable": {"thread_id": "research-1"}}
result = graph.invoke(initial_state, config)

# Human reviews research notes...
print("Research notes:", result["research_notes"])
user_approval = input("Approve and write? (y/n): ")

if user_approval == "y":
    # Resume from checkpoint
    result = graph.invoke(None, config)  # continues from where it paused
```

### Parallel branches

```python
from langgraph.graph import StateGraph

# Multiple research agents working simultaneously
workflow.add_node("search_academic", search_academic_papers)
workflow.add_node("search_news", search_news_articles)
workflow.add_node("search_code", search_code_examples)

# Fan-out: run all three in parallel
workflow.add_edge("start", "search_academic")
workflow.add_edge("start", "search_news")
workflow.add_edge("start", "search_code")

# Fan-in: merge results
workflow.add_edge("search_academic", "synthesize")
workflow.add_edge("search_news", "synthesize")
workflow.add_edge("search_code", "synthesize")
```

### Multi-agent collaboration

```python
# Define specialist agents as nodes
def researcher_agent(state):
    """Finds information and facts."""
    ...

def critic_agent(state):
    """Reviews draft and provides feedback."""
    ...

def writer_agent(state):
    """Writes polished content based on research and feedback."""
    ...

# Wire them up
workflow.add_node("researcher", researcher_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("critic", critic_agent)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "critic")
workflow.add_conditional_edges(
    "critic",
    lambda state: "done" if state["approval"] else "writer",  # loop until approved
    {"writer": "writer", "done": END},
)
```

---

## PART 5: Memory & Conversation

## 45.17 Conversation memory

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Store conversations by session ID
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Wrap chain with memory
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("placeholder", "{history}"),  # injected conversation history
    ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Conversation (state maintained across invocations)
config = {"configurable": {"session_id": "user-123"}}

r1 = chain_with_memory.invoke({"input": "My name is Alice"}, config)
print(r1)  # "Nice to meet you, Alice!"

r2 = chain_with_memory.invoke({"input": "What's my name?"}, config)
print(r2)  # "Your name is Alice."
```

## 45.18 Long-term memory with vector store

```python
# Store past interactions as searchable memory
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

memory_store = Chroma(
    collection_name="user_memories",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./memory_db",
)

# Save important facts
memory_store.add_texts(
    texts=["User prefers Python over JavaScript", "User works on e-commerce projects"],
    metadatas=[{"user_id": "123", "type": "preference"}, {"user_id": "123", "type": "context"}],
)

# Retrieve relevant memories when responding
relevant_memories = memory_store.similarity_search(
    "What language should I use?", k=3,
    filter={"user_id": "123"},
)
```

---

## PART 6: Production Patterns

## 45.19 When to use what

| Use case | Tool |
|----------|------|
| Simple Q&A with your docs | RAG chain (retriever + prompt + LLM) |
| Dynamic tool use (search, calculate, API calls) | LangChain Agent |
| Multi-step workflow with branching/loops | LangGraph |
| Conversational assistant | Chain + memory |
| Complex multi-agent collaboration | LangGraph with multiple agent nodes |
| Batch document processing | Chain with `.batch()` |

## 45.20 Error handling and observability

```python
# Retry with fallbacks
from langchain_core.runnables import RunnableWithFallbacks

main_llm = ChatOpenAI(model="gpt-4o")
fallback_llm = ChatOpenAI(model="gpt-4o-mini")

robust_llm = main_llm.with_fallbacks([fallback_llm])

# Tracing with LangSmith (observability)
# Set environment variables:
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=...
# Every chain invocation is logged with inputs, outputs, latency, tokens used

# Rate limiting / throttling
from langchain_core.rate_limiters import InMemoryRateLimiter
rate_limiter = InMemoryRateLimiter(requests_per_second=1)
llm = ChatOpenAI(model="gpt-4o", rate_limiter=rate_limiter)
```

---

## Summary

✅ LangChain basics: models, prompts, chains (LCEL pipe operator), structured output
✅ RAG pipeline: load → split → embed → store → retrieve → generate
✅ RAG improvements: multi-query, compression, hybrid search
✅ Agents: LLM decides which tools to call, iterates until answer found
✅ Custom tools: database queries, API calls, document search
✅ LangGraph: stateful workflows with conditional routing, cycles, parallel branches
✅ LangGraph patterns: human-in-the-loop, multi-agent, research loops
✅ Memory: conversation history, long-term vector memory
✅ Production: fallbacks, tracing (LangSmith), rate limiting

## Key takeaways

**RAG is the killer app.** Most production LLM applications use RAG — it grounds the model in YOUR data, reduces hallucination, and keeps responses current. Master the pipeline: chunk → embed → retrieve → generate.

**Agents add autonomy but reduce predictability.** A chain does the same thing every time (reliable). An agent decides what to do (powerful but harder to debug). Use agents when the user's intent varies widely; use chains when the workflow is known.

**LangGraph is for complex workflows.** If your agent needs: multiple steps with state, conditional branching, loops (iterative refinement), parallel execution, or human approval gates — LangGraph is the right abstraction. Simple tool-calling doesn't need it.

**Memory is what makes assistants useful.** Without memory, every interaction starts from zero. Conversation memory (short-term) + vector memory (long-term facts about the user) creates the experience of a persistent, personalized assistant.

---

→ [Back to Chapter 44: SQL with PostgreSQL](./44-SQL-POSTGRESQL.md)
