# Chapter 65: Local AI for Enterprise — Document Q&A with Ollama + LangGraph

## What you'll learn

- Architecture for a local (on-premise) AI document assistant
- Ollama setup: running LLMs locally with zero cloud dependency
- Model selection for low-spec hardware (4GB–16GB RAM)
- RAG pipeline: ingest documents → chunk → embed → retrieve → answer
- LangGraph: multi-step reasoning with routing, verification, and fallback
- Optimisation: fast responses on modest hardware
- Security: no data leaves the building
- Build: complete system from document upload to answer

---

## Why Local AI?

```
CLOUD AI (OpenAI, Anthropic):              LOCAL AI (Ollama):
  ✅ Best quality models                     ✅ Data NEVER leaves your network
  ✅ No hardware needed                      ✅ No API costs ($0/month)
  ❌ Data sent to third party               ✅ No internet required
  ❌ Monthly costs ($100-$10,000+)          ✅ Full control + customisation
  ❌ Internet dependency                    ✅ Compliance friendly (GDPR, finance)
  ❌ Rate limits                            ❌ Lower quality (but improving fast)
                                             ❌ Needs hardware (GPU helps)
                                             ❌ Slower on weak hardware

USE LOCAL WHEN:
  • Confidential documents (legal, financial, medical, HR)
  • Regulatory requirements (data residency, GDPR, banking)
  • Cost-sensitive (many users, high volume)
  • Air-gapped environments (no internet)
  • You want full control and no vendor lock-in
```

---

## PART 1: Architecture

## 65.1 System overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         YOUR COMPANY NETWORK                             │
│                                                                          │
│  ┌──────────────┐                                                        │
│  │  Users       │                                                        │
│  │  (Browser)   │                                                        │
│  └──────┬───────┘                                                        │
│         │ HTTP                                                            │
│  ┌──────▼───────────────────────────────────────────────────────────┐    │
│  │                    FRONTEND (Next.js)                              │    │
│  │   Chat UI + Document Upload + History                             │    │
│  └──────┬───────────────────────────────────────────────────────────┘    │
│         │ API calls                                                       │
│  ┌──────▼───────────────────────────────────────────────────────────┐    │
│  │                 BACKEND (Python FastAPI)                           │    │
│  │                                                                    │    │
│  │  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────┐  │    │
│  │  │  LangGraph      │   │  RAG Pipeline    │   │  Document    │  │    │
│  │  │  Agent          │   │  (retrieve +     │   │  Ingestion   │  │    │
│  │  │  (routing,      │   │   rerank +       │   │  (upload,    │  │    │
│  │  │   reasoning)    │   │   generate)      │   │   chunk,     │  │    │
│  │  └────────┬────────┘   └────────┬─────────┘   │   embed)     │  │    │
│  │           │                      │              └──────┬───────┘  │    │
│  └───────────┼──────────────────────┼─────────────────────┼──────────┘    │
│              │                      │                      │               │
│  ┌───────────▼──────────┐  ┌───────▼────────┐   ┌────────▼─────────┐    │
│  │   OLLAMA (LLM)       │  │ VECTOR DB      │   │  DOCUMENT STORE  │    │
│  │                      │  │ (ChromaDB)     │   │  (PostgreSQL     │    │
│  │  • llama3.1 (chat)   │  │                │   │   or filesystem) │    │
│  │  • nomic-embed (emb) │  │  Embeddings +  │   │                  │    │
│  │  • mistral (fallback)│  │  metadata      │   │  Original files  │    │
│  └──────────────────────┘  └────────────────┘   └──────────────────┘    │
│                                                                          │
│  NO DATA LEAVES THIS BOX. EVER.                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 65.2 Hardware requirements

| Spec | Minimum (usable) | Recommended | Ideal |
|------|-------------------|-------------|-------|
| RAM | 8 GB | 16 GB | 32 GB |
| CPU | 4 cores | 8 cores | 16 cores |
| GPU | None (CPU only) | 6GB VRAM (RTX 3060) | 12GB+ (RTX 4070/A4000) |
| Storage | 50 GB SSD | 100 GB NVMe | 500 GB NVMe |
| Model size | 3B-7B (quantized) | 7B-13B | 13B-70B |

**The realism:**
```
8GB RAM, no GPU, 7B model:
  → Response time: 10-30 seconds (usable for async, not great for real-time chat)
  → Quality: decent for simple Q&A, struggles with complex reasoning

16GB RAM, RTX 3060 (6GB), 7B model:
  → Response time: 2-5 seconds (good user experience)
  → Quality: good for document Q&A, summarisation, extraction

32GB RAM, RTX 4070 (12GB), 13B model:
  → Response time: 1-3 seconds (great)
  → Quality: near-GPT-3.5 level for most document tasks
```

## 65.3 Model selection for low-spec

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
# Windows: download from ollama.com

# Start Ollama
ollama serve

# Pull models:

# BEST BALANCE (7B, fast, good quality):
ollama pull llama3.1:8b-instruct-q4_K_M    # 4.9GB, good quality/speed
ollama pull mistral:7b-instruct-q4_K_M     # 4.4GB, fast, good at following instructions

# TINY (runs on 4GB RAM — lower quality but FAST):
ollama pull phi3:mini                        # 2.3GB, surprisingly good for size
ollama pull gemma2:2b                        # 1.6GB, fastest, basic tasks only

# EMBEDDING MODEL (for RAG — runs alongside chat model):
ollama pull nomic-embed-text                 # 274MB, excellent local embeddings
ollama pull mxbai-embed-large               # 670MB, higher quality embeddings

# LARGE (if you have 16GB+ RAM and GPU):
ollama pull llama3.1:13b-instruct-q4_K_M   # 7.4GB, much better reasoning
ollama pull mistral-nemo:12b               # 7.1GB, excellent at long context
```

**Quantization explained:**
```
Full precision (f16):    14GB for 7B model (too large for most)
Q8 (8-bit):             7GB  (high quality, still large)
Q4_K_M (4-bit medium):  4.5GB (best balance — recommended)
Q4_K_S (4-bit small):   4.0GB (slightly worse, slightly smaller)
Q2 (2-bit):             2.5GB (noticeable quality loss — last resort)

RULE: Use Q4_K_M for everything. It's the sweet spot of size vs quality.
```



---

## PART 2: Document Ingestion & RAG Pipeline

## 65.4 Document ingestion

```python
# pip install langchain-community chromadb pypdf python-docx unstructured
# pip install langchain-ollama sentence-transformers

from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os

# 1. Load documents (supports PDF, Word, Excel, TXT)
def load_document(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    loaders = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".txt": TextLoader,
        ".xlsx": UnstructuredExcelLoader,
    }
    loader_class = loaders.get(ext)
    if not loader_class:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader_class(file_path).load()

# 2. Chunk documents (split into digestible pieces)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # smaller chunks = faster retrieval + fits in small context
    chunk_overlap=100,    # overlap prevents losing info at boundaries
    separators=["\n\n", "\n", ". ", " "],
)

def ingest_document(file_path: str, collection: str = "company_docs"):
    """Load, split, embed, and store a document."""
    docs = load_document(file_path)
    chunks = splitter.split_documents(docs)
    
    # Add metadata
    for chunk in chunks:
        chunk.metadata["source_file"] = os.path.basename(file_path)
    
    # 3. Embed with local model (Ollama)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # 4. Store in ChromaDB (local, no server needed)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name=collection,
    )
    
    print(f"Ingested {len(chunks)} chunks from {file_path}")
    return vectorstore
```

## 65.5 Optimised retrieval

```python
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

def get_retriever(collection: str = "company_docs", k: int = 4):
    """Create a retriever that finds relevant document chunks."""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name=collection,
    )
    
    return vectorstore.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance (diverse results)
        search_kwargs={
            "k": k,
            "fetch_k": 20,  # fetch 20, then pick 4 most diverse
        },
    )

# Retrieval with metadata filtering
def retrieve_from_specific_doc(query: str, filename: str):
    """Search only within a specific document."""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="company_docs",
    )
    return vectorstore.similarity_search(
        query,
        k=4,
        filter={"source_file": filename},
    )
```

## 65.6 Speed optimisations for retrieval

```python
# OPTIMISATION 1: Pre-compute embeddings (don't re-embed on every query)
# ChromaDB caches embeddings automatically — they're computed once at ingest time.

# OPTIMISATION 2: Smaller chunk size (500 chars, not 1000)
# Smaller chunks = faster embedding + more precise retrieval + fits in small model context

# OPTIMISATION 3: Limit results (k=3-4, not k=10)
# Fewer results = less context for the LLM = faster generation

# OPTIMISATION 4: Use metadata pre-filtering
# If user selects a document category, filter BEFORE vector search (instant)
results = vectorstore.similarity_search(
    query, k=4,
    filter={"department": "HR"}  # only search HR documents
)

# OPTIMISATION 5: Cache frequent queries
from functools import lru_cache
import hashlib

@lru_cache(maxsize=200)
def cached_retrieve(query_hash: str):
    # Cache retrieval results for repeated questions
    ...
```

---

## PART 3: LangGraph Agent — Smart Routing & Reasoning

## 65.7 Why LangGraph (not a simple chain)

```
SIMPLE CHAIN (LangChain):
  Question → Retrieve → Generate → Answer
  (works for simple questions but fails on complex ones)

PROBLEMS WITH SIMPLE CHAIN:
  • "What's our leave policy?" → Works (direct retrieval)
  • "Compare our Q1 and Q2 revenue" → Fails (needs multi-step retrieval)
  • "Summarise all HR policies" → Fails (needs iterative retrieval)
  • "Is this compliant with regulation X?" → Fails (needs reasoning + verification)

LANGGRAPH (stateful agent):
  Question → Route → Retrieve → Grade relevance → Re-retrieve if bad
           → Generate → Verify answer → Respond (or ask for clarification)

  Handles: multi-step, ambiguous, complex questions with fallbacks
```

## 65.8 LangGraph implementation

```python
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
import operator

# --- STATE ---
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    question: str
    retrieved_docs: list[str]
    answer: str
    confidence: str  # "high", "medium", "low"
    route: str       # "retrieval", "clarify", "general"
    attempts: int

# --- LLM ---
llm = ChatOllama(
    model="llama3.1:8b-instruct-q4_K_M",
    temperature=0,
    num_ctx=4096,       # context window (keep small for speed)
    num_predict=512,    # max output tokens (limit for speed)
)

# --- NODES ---

def route_question(state: AgentState) -> dict:
    """Decide: does this need document retrieval or is it general?"""
    question = state["question"]
    
    response = llm.invoke(f"""Classify this question into ONE category:
- "retrieval": needs information from company documents
- "general": general knowledge question (no documents needed)
- "clarify": question is too vague to answer

Question: {question}
Category:""")
    
    route = response.content.strip().lower()
    if "retrieval" in route:
        return {"route": "retrieval"}
    elif "clarify" in route:
        return {"route": "clarify"}
    else:
        return {"route": "general"}


def retrieve_docs(state: AgentState) -> dict:
    """Retrieve relevant document chunks."""
    retriever = get_retriever(k=4)
    docs = retriever.invoke(state["question"])
    doc_texts = [doc.page_content for doc in docs]
    sources = [doc.metadata.get("source_file", "unknown") for doc in docs]
    
    return {
        "retrieved_docs": doc_texts,
        "messages": [AIMessage(content=f"Found {len(docs)} relevant chunks from: {', '.join(set(sources))}")],
    }


def grade_documents(state: AgentState) -> dict:
    """Check if retrieved docs are actually relevant to the question."""
    question = state["question"]
    docs = state["retrieved_docs"]
    
    if not docs:
        return {"confidence": "low"}
    
    # Quick relevance check (fast — don't use LLM for this)
    combined = " ".join(docs).lower()
    keywords = question.lower().split()
    matches = sum(1 for kw in keywords if kw in combined)
    relevance = matches / max(len(keywords), 1)
    
    if relevance > 0.3:
        return {"confidence": "high"}
    else:
        return {"confidence": "low"}


def generate_answer(state: AgentState) -> dict:
    """Generate answer from retrieved documents."""
    question = state["question"]
    context = "\n\n---\n\n".join(state["retrieved_docs"])
    
    prompt = f"""Answer the question based ONLY on the provided context.
If the context doesn't contain enough information, say "I don't have enough information to answer this fully."
Be concise and specific. Cite which document the information comes from if possible.

Context:
{context}

Question: {question}

Answer:"""
    
    response = llm.invoke(prompt)
    return {
        "answer": response.content,
        "messages": [AIMessage(content=response.content)],
    }


def generate_general(state: AgentState) -> dict:
    """Answer general questions without document retrieval."""
    response = llm.invoke(f"""Answer this general question concisely:
{state["question"]}""")
    return {
        "answer": response.content,
        "messages": [AIMessage(content=response.content)],
    }


def ask_clarification(state: AgentState) -> dict:
    """Ask user to clarify their question."""
    return {
        "answer": "Could you please be more specific? For example:\n- Which document or topic are you asking about?\n- What time period are you interested in?\n- Are you looking for a policy, a number, or a procedure?",
        "messages": [AIMessage(content="I need more clarity to give you a good answer.")],
    }


def retry_with_broader_search(state: AgentState) -> dict:
    """If first retrieval was poor, try broader search."""
    retriever = get_retriever(k=8)  # more results
    docs = retriever.invoke(state["question"])
    doc_texts = [doc.page_content for doc in docs]
    return {
        "retrieved_docs": doc_texts,
        "attempts": state.get("attempts", 0) + 1,
    }


# --- ROUTING LOGIC ---

def decide_route(state: AgentState) -> str:
    """Route based on classification."""
    return state["route"]

def decide_after_grading(state: AgentState) -> str:
    """After grading docs: generate or retry?"""
    if state["confidence"] == "high":
        return "generate"
    elif state.get("attempts", 0) >= 2:
        return "generate"  # give best effort after 2 attempts
    else:
        return "retry"


# --- BUILD GRAPH ---

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("route", route_question)
workflow.add_node("retrieve", retrieve_docs)
workflow.add_node("grade", grade_documents)
workflow.add_node("generate", generate_answer)
workflow.add_node("general", generate_general)
workflow.add_node("clarify", ask_clarification)
workflow.add_node("retry", retry_with_broader_search)

# Set entry point
workflow.set_entry_point("route")

# Routing edges
workflow.add_conditional_edges("route", decide_route, {
    "retrieval": "retrieve",
    "general": "general",
    "clarify": "clarify",
})

# Retrieval → Grade → Generate or Retry
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges("grade", decide_after_grading, {
    "generate": "generate",
    "retry": "retry",
})
workflow.add_edge("retry", "grade")  # retry loops back to grading

# Terminal edges
workflow.add_edge("generate", END)
workflow.add_edge("general", END)
workflow.add_edge("clarify", END)

# Compile
graph = workflow.compile()
```

## 65.9 Using the agent

```python
# Query the agent
result = graph.invoke({
    "messages": [],
    "question": "What is our company's remote work policy?",
    "retrieved_docs": [],
    "answer": "",
    "confidence": "",
    "route": "",
    "attempts": 0,
})

print(result["answer"])
# "Based on the Employee Handbook (Section 3.2), employees may work
#  remotely up to 3 days per week with manager approval..."
```



---

## PART 4: FastAPI Server

## 65.10 API endpoints

```python
# server.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os

app = FastAPI(title="Local AI Document Assistant")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryRequest(BaseModel):
    question: str
    collection: str = "company_docs"
    
class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: str

# --- ENDPOINTS ---

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), collection: str = "company_docs"):
    """Upload and ingest a document."""
    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        ingest_document(file_path, collection)
        return {"status": "success", "filename": file.filename, "message": "Document ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Ask a question about your documents."""
    result = graph.invoke({
        "messages": [],
        "question": request.question,
        "retrieved_docs": [],
        "answer": "",
        "confidence": "",
        "route": "",
        "attempts": 0,
    })
    
    return QueryResponse(
        answer=result["answer"],
        sources=list(set(doc.split("Source:")[-1].strip() for doc in result.get("retrieved_docs", []) if "Source:" in doc)) or ["company_docs"],
        confidence=result.get("confidence", "medium"),
    )


@app.get("/api/documents")
async def list_documents(collection: str = "company_docs"):
    """List all ingested documents."""
    vectorstore = Chroma(persist_directory="./chroma_db", collection_name=collection,
                         embedding_function=OllamaEmbeddings(model="nomic-embed-text"))
    # Get unique source files from metadata
    results = vectorstore.get(include=["metadatas"])
    files = set(m.get("source_file", "unknown") for m in results["metadatas"])
    return {"documents": sorted(files), "total_chunks": len(results["metadatas"])}


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str, collection: str = "company_docs"):
    """Remove a document from the knowledge base."""
    vectorstore = Chroma(persist_directory="./chroma_db", collection_name=collection,
                         embedding_function=OllamaEmbeddings(model="nomic-embed-text"))
    # Delete chunks with matching source_file
    results = vectorstore.get(where={"source_file": filename}, include=["metadatas"])
    if results["ids"]:
        vectorstore.delete(ids=results["ids"])
    return {"status": "deleted", "filename": filename, "chunks_removed": len(results["ids"])}


# --- STREAMING (for real-time token output) ---
from fastapi.responses import StreamingResponse
from langchain_ollama import ChatOllama

@app.post("/api/query/stream")
async def query_stream(request: QueryRequest):
    """Stream the answer token by token (better UX)."""
    # Retrieve docs first
    retriever = get_retriever(k=4)
    docs = retriever.invoke(request.question)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    prompt = f"""Answer based on context. Be concise.
Context: {context}
Question: {request.question}
Answer:"""
    
    llm = ChatOllama(model="llama3.1:8b-instruct-q4_K_M", temperature=0)
    
    async def generate():
        for chunk in llm.stream(prompt):
            yield chunk.content
    
    return StreamingResponse(generate(), media_type="text/plain")
```

```bash
# Run the server
pip install fastapi uvicorn python-multipart
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

---

## PART 5: Performance — Fast Responses on Low-Spec Hardware

## 65.11 Speed optimisation checklist

| Technique | Impact | Implementation |
|-----------|--------|---------------|
| **Smaller model** | 3-5× faster | Use phi3:mini (2B) or llama3.1:8b-q4 instead of 13B |
| **Limit output tokens** | 2× faster | `num_predict=256` (don't let model ramble) |
| **Smaller context** | 1.5× faster | `num_ctx=2048` (enough for RAG, saves RAM) |
| **Fewer retrieved chunks** | Faster prompt | k=3 instead of k=10 |
| **Smaller chunks** | Faster embedding | 500 chars, not 1000 |
| **GPU offloading** | 5-10× faster | Even 4GB VRAM helps (`num_gpu=99`) |
| **Embedding cache** | Instant re-queries | Cache results for repeated questions |
| **Streaming** | Perceived faster | First token appears in 1s vs waiting 10s for full answer |
| **Pre-warm model** | No cold start | Keep Ollama running, send a ping on app startup |
| **Batch embedding** | Faster ingestion | Embed multiple chunks in one call |

## 65.12 Ollama performance tuning

```bash
# Model configuration (create a Modelfile for custom settings)
cat > Modelfile << 'EOF'
FROM llama3.1:8b-instruct-q4_K_M

# Tuned for fast, concise responses on low-spec hardware
PARAMETER num_ctx 2048        # smaller context = less RAM, faster
PARAMETER num_predict 256     # limit output length
PARAMETER temperature 0       # deterministic (no randomness = slightly faster)
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1

SYSTEM """You are a helpful document assistant for a company.
Answer questions concisely based on provided context.
If you don't know, say so. Don't make things up.
Keep answers under 3 paragraphs."""
EOF

# Create the optimised model
ollama create company-assistant -f Modelfile

# Use it
ollama run company-assistant "What is our leave policy?"
```

## 65.13 Two-model strategy (fast + smart)

```python
# Use a SMALL model for routing/classification (fast)
# Use a LARGER model for answer generation (quality)

fast_llm = ChatOllama(model="phi3:mini", num_predict=50, num_ctx=512)  # routing only
smart_llm = ChatOllama(model="llama3.1:8b-instruct-q4_K_M", num_predict=256, num_ctx=2048)  # answers

# In the graph:
# route_question → uses fast_llm (< 1 second)
# generate_answer → uses smart_llm (3-5 seconds)
# Total: 4-6 seconds (vs 10+ if smart_llm does everything)
```

## 65.14 Caching for instant repeated answers

```python
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("./cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cached_answer(question: str) -> str | None:
    key = hashlib.md5(question.lower().strip().encode()).hexdigest()
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        return data["answer"]
    return None

def cache_answer(question: str, answer: str):
    key = hashlib.md5(question.lower().strip().encode()).hexdigest()
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(json.dumps({"question": question, "answer": answer}))

# Use in query flow:
cached = get_cached_answer(question)
if cached:
    return cached  # instant! no LLM call needed
```

---

## PART 6: Deployment

## 65.15 Docker Compose (one command to deploy everything)

```yaml
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]  # use GPU if available
    # Pull models on first start:
    entrypoint: ["/bin/sh", "-c"]
    command:
      - |
        ollama serve &
        sleep 5
        ollama pull llama3.1:8b-instruct-q4_K_M
        ollama pull nomic-embed-text
        wait

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - CHROMA_DIR=/data/chroma
    volumes:
      - chroma_data:/data/chroma
      - uploads:/data/uploads
    depends_on:
      - ollama

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  ollama_data:
  chroma_data:
  uploads:
```

```bash
# Deploy everything with one command:
docker compose up -d

# Check status:
docker compose logs -f backend

# Access:
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs (Swagger)
# Ollama: http://localhost:11434
```

## 65.16 Security considerations

```
FOR ENTERPRISE DEPLOYMENT:
  □ Run on internal network only (no public internet exposure)
  □ Add authentication to API (JWT or API key)
  □ Encrypt stored documents at rest
  □ Audit log: who asked what, when
  □ Role-based document access (HR docs only for HR team)
  □ Regular backups of ChromaDB + uploads
  □ Network segmentation (AI server in its own VLAN)
  □ No telemetry (Ollama sends no data by default — verify)
  □ Document retention policies (auto-delete after N days)
  □ Input sanitisation (prevent prompt injection attacks)
```

---

## PART 7: Complete File Structure

```
local-ai-assistant/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── server.py              ← FastAPI endpoints
│   ├── agent.py               ← LangGraph agent
│   ├── ingestion.py           ← Document loading + chunking
│   ├── retrieval.py           ← Vector search logic
│   ├── config.py              ← Model names, chunk sizes, etc.
│   └── Modelfile             ← Custom Ollama model config
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── app/
│   │   ├── page.tsx           ← Chat UI
│   │   └── upload/page.tsx    ← Document upload page
│   └── components/
│       ├── ChatInterface.tsx
│       ├── MessageBubble.tsx
│       └── DocumentList.tsx
├── uploads/                    ← Uploaded documents
├── chroma_db/                  ← Vector store (persistent)
└── cache/                      ← Query result cache
```

---

## Summary

✅ Architecture: Next.js frontend → FastAPI backend → Ollama (LLM) + ChromaDB (vectors)
✅ Model selection: llama3.1:8b-q4 (balance) or phi3:mini (speed) — both run on 8-16GB RAM
✅ Document ingestion: PDF/Word/Excel → chunk (500 chars) → embed (nomic-embed-text) → store (Chroma)
✅ LangGraph agent: route → retrieve → grade relevance → generate or retry → answer
✅ Performance: smaller model + limited tokens + fewer chunks + streaming + caching = 2-5s responses
✅ Two-model strategy: fast model for routing, smart model for answering
✅ Streaming: first token in 1s (user sees typing, not a blank screen for 10s)
✅ Deployment: Docker Compose (one command), GPU optional, runs on any machine
✅ Security: internal network, auth, audit logs, encryption, no data leaves the network

## Key takeaways

**Start small, scale later.** Begin with phi3:mini or llama3.1:8b on CPU. Get the pipeline working. Then upgrade hardware and model size. A working 8B system today is better than a planned 70B system next quarter.

**Streaming changes perception.** A 10-second response feels instant if the first token appears in 1 second and text flows in progressively. Without streaming, users stare at a blank screen wondering if it's broken.

**RAG quality depends on chunking, not model size.** A 7B model with well-chunked, relevant context outperforms a 70B model with poorly retrieved, irrelevant chunks. Invest time in: chunk size, overlap, metadata filtering, and relevance grading.

**The LangGraph advantage:** Simple chains fail silently on bad retrieval. LangGraph grades results, retries with broader search, routes non-document questions differently, and asks for clarification when confused. This turns a "sometimes works" demo into a reliable tool.

---

→ [Back to Chapter 64: Math Animations](./64-MATH-ANIMATIONS.md)
