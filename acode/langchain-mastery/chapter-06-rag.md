# Chapter 6: RAG — Retrieval Augmented Generation

[← Chapter 5](chapter-05-memory.md) · [Chapter 7: Document Loading & Chunking →](chapter-07-document-loading.md)

---

## The Scene

Elena uploads a 200-page merger agreement. She asks:

> "What does Section 7.3 say about the non-compete clause?"

The AI responds:

> "Non-compete clauses typically restrict parties from engaging in competing business activities for a specified period after the agreement terminates. Common durations range from 1-3 years..."

Elena slams her laptop shut.

> "I didn't ask what non-compete clauses *typically* say. I asked what *this specific contract* says in Section 7.3. The one I uploaded. The one sitting right there."

The AI is answering from its training data — general knowledge about non-competes. It has never seen Elena's contract. It can't. The contract isn't in the prompt.

You could shove the entire 200-page PDF into the prompt... but that's 80,000 tokens. At $0.01/1K tokens, that's $0.80 per question. Elena asks 50 questions a day. That's $40/day per lawyer. For 20 lawyers: $800/day.

There has to be a better way.

---

## What is RAG?

**Retrieval Augmented Generation** = find the relevant pieces first, then ask the LLM about only those pieces.

```
Without RAG:                          With RAG:
─────────────                         ─────────
"What does Section 7.3 say?"          "What does Section 7.3 say?"
         │                                     │
         ▼                                     ▼
┌─────────────────┐                  ┌──────────────────┐
│  LLM (guesses)  │                  │  Vector Search   │
│  from training  │                  │  → finds §7.3   │
│  data           │                  └────────┬─────────┘
└────────┬────────┘                           │
         │                                     ▼
         ▼                            ┌──────────────────┐
"Non-competes typically..."           │  LLM + context   │
(generic, wrong)                      │  "Section 7.3    │
                                      │   states that..."│
                                      └────────┬─────────┘
                                               │
                                               ▼
                                      "Section 7.3 of the Acme-Beta
                                       merger agreement restricts..."
                                      (specific, correct)
```

Instead of sending 200 pages, you send only the 2-3 relevant paragraphs. The LLM answers based on actual document content.

---

## The RAG Pipeline

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Upload  │────→│  Chunk   │────→│  Embed   │────→│  Store   │
│  (PDF)   │     │  (split) │     │ (vectors)│     │ (ChromaDB)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘

                    ... later, at query time ...

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Query   │────→│  Embed   │────→│  Search  │────→│  LLM +   │
│          │     │  query   │     │ (similar)│     │  context  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

Two phases:
1. **Indexing** (once per document): split → embed → store
2. **Querying** (every question): embed query → find similar chunks → answer with context

---

## Embeddings: Turning Text into Vectors

An embedding is a list of numbers that captures the *meaning* of text. Similar meanings → similar numbers → close in vector space.

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Turn text into a vector
vector = embeddings.embed_query("non-compete clause duration")
print(len(vector))  # 1536 dimensions
print(vector[:5])   # [0.023, -0.041, 0.018, ...]
```

The magic: "non-compete clause duration" and "restriction on competing business activities" produce *similar* vectors — even though they share no words.

---

## Vector Store: ChromaDB

A vector store indexes embeddings for fast similarity search:

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create a vector store
vectorstore = Chroma(
    collection_name="legal_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db",  # persists to disk
)
```

---

## Indexing Documents

Let's index Elena's contract:

```python
from langchain_core.documents import Document

# For now, manually create chunks (Chapter 7 covers automatic splitting)
chunks = [
    Document(
        page_content="Section 7.3 Non-Compete. For a period of two (2) years following "
                     "the Closing Date, neither Seller nor any of its Affiliates shall, "
                     "directly or indirectly, engage in any business that competes with "
                     "the Business in the Territory.",
        metadata={"source": "acme-beta-merger.pdf", "section": "7.3", "page": 42}
    ),
    Document(
        page_content="Section 7.4 Non-Solicitation. For a period of three (3) years "
                     "following the Closing Date, Seller shall not solicit any employee "
                     "of the Company or any of its subsidiaries.",
        metadata={"source": "acme-beta-merger.pdf", "section": "7.4", "page": 42}
    ),
    Document(
        page_content="Section 4.2 Indemnification. Seller shall indemnify and hold harmless "
                     "Buyer from any losses arising from breach of representations in Article III, "
                     "subject to the Cap of $5,000,000 and the Basket of $250,000.",
        metadata={"source": "acme-beta-merger.pdf", "section": "4.2", "page": 28}
    ),
    # ... hundreds more chunks
]

# Add to vector store
vectorstore.add_documents(chunks)
```

Each chunk is embedded and stored. Now you can search by meaning.

---

## Querying: Semantic Search

```python
# Find chunks similar to the question
results = vectorstore.similarity_search(
    "What does the non-compete clause say?",
    k=3,  # return top 3 matches
)

for doc in results:
    print(f"[{doc.metadata['section']}] {doc.page_content[:100]}...")
```

Output:
```
[7.3] Section 7.3 Non-Compete. For a period of two (2) years following the Closing Date...
[7.4] Section 7.4 Non-Solicitation. For a period of three (3) years following the Closing...
[4.2] Section 4.2 Indemnification. Seller shall indemnify and hold harmless Buyer from...
```

The vector search found Section 7.3 (exact match) and 7.4 (related) — without keyword matching. It understood the *meaning*.

---

## The RAG Chain

Now combine retrieval with generation:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# The retriever (wraps the vector store)
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},  # retrieve top 4 chunks
)

# The prompt includes retrieved context
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a legal document analyst. Answer questions based ONLY on the "
     "provided context. If the answer is not in the context, say "
     "'I cannot find this information in the provided documents.'\n\n"
     "Context:\n{context}"),
    ("human", "{question}"),
])

def format_docs(docs):
    """Format retrieved documents into a string for the prompt."""
    return "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source', 'unknown')}, "
        f"Section: {d.metadata.get('section', 'N/A')}]\n{d.page_content}"
        for d in docs
    )

# The RAG chain
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Ask about the actual document
answer = rag_chain.invoke("What does Section 7.3 say about the non-compete?")
print(answer)
```

Output:
```
Section 7.3 of the Acme-Beta merger agreement establishes a non-compete 
restriction. For two (2) years following the Closing Date, neither the 
Seller nor any of its Affiliates may directly or indirectly engage in 
any business that competes with the Business in the Territory.
```

That's the actual contract language. Not a generic answer. Not a hallucination.

---

## Citing Sources

Elena needs to know *where* the answer came from:

```python
from pydantic import BaseModel, Field

class SourcedAnswer(BaseModel):
    answer: str = Field(description="The answer to the question")
    sources: list[str] = Field(description="Section numbers used to answer")
    confidence: Literal["high", "medium", "low"]
    direct_quotes: list[str] = Field(description="Exact quotes from the document")

rag_chain_with_sources = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | llm.with_structured_output(SourcedAnswer)
)

result = rag_chain_with_sources.invoke("What is the indemnification cap?")
print(f"Answer: {result.answer}")
print(f"Sources: {result.sources}")
print(f"Quotes: {result.direct_quotes}")
```

Output:
```
Answer: The indemnification cap is $5,000,000, with a basket (deductible) of $250,000.
Sources: ["Section 4.2"]
Quotes: ["subject to the Cap of $5,000,000 and the Basket of $250,000"]
```

Elena can verify the answer against the original document. Trust, but verify.

---

## The "I Don't Know" Problem

Without RAG, the AI hallucinates. With RAG, you can make it admit ignorance:

```python
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Answer based ONLY on the provided context. "
     "If the context does not contain the answer, respond with: "
     "'I cannot find this information in the uploaded documents. "
     "The relevant section may not have been uploaded, or the question "
     "may be outside the scope of the available documents.'\n\n"
     "Context:\n{context}"),
    ("human", "{question}"),
])
```

Now when Elena asks about something not in the uploaded documents:

> **Elena:** "What's the governing law clause?"
> **AI:** "I cannot find this information in the uploaded documents. The relevant section may not have been uploaded."

Honest. Verifiable. No hallucination.

---

## What You Built

```python
# rag.py — NovaMind document Q&A
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Setup
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="legal_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Chain
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a legal document analyst. Answer based ONLY on the context below. "
     "Cite the section numbers. If the answer isn't in the context, say so.\n\n"
     "Context:\n{context}"),
    ("human", "{question}"),
])

def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[{d.metadata.get('section', 'N/A')}] {d.page_content}" for d in docs
    )

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)
```

---

## What's Still Broken

Elena uploads a 200-page PDF. You need to:
1. Extract text from the PDF
2. Split it into meaningful chunks (not just every 500 characters)
3. Handle tables, headers, and section numbers
4. Deal with scanned documents (OCR)

Right now you're manually creating `Document` objects. That doesn't scale.

> "I have 500 contracts to upload. I'm not copy-pasting sections by hand." — Elena

That's Chapter 7 — document loading and chunking strategies.

---

## Recap

| Concept | What It Does |
|---------|--------------|
| Embeddings | Turn text into vectors that capture meaning |
| Vector store (Chroma) | Index and search vectors by similarity |
| Retriever | Find relevant document chunks for a query |
| RAG chain | Retrieve context → inject into prompt → generate answer |
| `format_docs` | Convert Document objects into prompt-friendly text |
| Source citation | Track which sections the answer came from |
| "I don't know" | Refuse to answer when context doesn't contain the answer |

---

[← Chapter 5](chapter-05-memory.md) · [Chapter 7: Document Loading & Chunking →](chapter-07-document-loading.md)
