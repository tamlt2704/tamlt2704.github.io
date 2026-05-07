# Chapter 6: RAG — Teach It Your Data

[← Chapter 5: Memory](chapter-05-memory.md) | [Chapter 7: Function Calling →](chapter-07-function-calling.md)

---

## The Incident

Karen asks the chatbot: "What's your return policy?"

The chatbot responds: "We offer a generous 90-day return window on all items, no questions asked."

Karen forwards this to a customer. The customer tries to return a laptop after 45 days. Your actual policy is 30 days. The customer is furious. Karen is furious. Captain Deadline is furious.

The LLM hallucinated. It doesn't know your policies — it guessed based on what "sounds right" from its training data.

---

## RAG: Retrieval Augmented Generation

Instead of hoping the LLM knows your data, you GIVE it your data at query time:

```
Without RAG:                         With RAG:
┌──────────────────────┐            ┌──────────────────────────────────┐
│ User: return policy? │            │ 1. User: return policy?          │
│                      │            │ 2. Search vector DB for relevant │
│ LLM: *guesses*      │            │    documents about "return policy"│
│ → 90 days (WRONG)   │            │ 3. Found: "Returns accepted within│
└──────────────────────┘            │    30 days with receipt..."       │
                                    │ 4. Send to LLM WITH the document │
                                    │ 5. LLM: "Our return policy is 30 │
                                    │    days with a valid receipt."    │
                                    └──────────────────────────────────┘
```

RAG = "look up the answer first, then ask the LLM to summarize it."

---

## The Pipeline

```
Documents → Chunks → Embeddings → Vector Store
                                       ↑
User Question → Embedding → Similarity Search → Top Results
                                                      ↓
                                    LLM Prompt + Retrieved Context → Answer
```

---

## Step 1: Add Dependencies

```groovy
// build.gradle
dependencies {
    implementation 'org.springframework.ai:spring-ai-ollama-spring-boot-starter'
    implementation 'org.springframework.ai:spring-ai-pgvector-store-spring-boot-starter'
    implementation 'org.springframework.ai:spring-ai-tika-document-reader'
    runtimeOnly 'org.postgresql:postgresql'
}
```

```yaml
# application.yml
spring:
  ai:
    ollama:
      base-url: http://localhost:11434
      chat:
        model: llama3.1
      embedding:
        model: nomic-embed-text  # embedding model for vector search
    vectorstore:
      pgvector:
        initialize-schema: true
        dimensions: 768  # must match embedding model output
  datasource:
    url: jdbc:postgresql://localhost:5432/shopzilla_ai
    username: postgres
    password: shopzilla
```

Pull the embedding model:

```bash
ollama pull nomic-embed-text
```

---

## Step 2: Load Your Documents

Create your knowledge base. Put company docs in `src/main/resources/docs/`:

```text
# src/main/resources/docs/return-policy.md
# ShopZilla Return Policy

## Standard Returns
- Items may be returned within 30 days of delivery
- Original receipt or order confirmation required
- Items must be unused and in original packaging
- Refund issued to original payment method within 5-7 business days

## Exceptions
- Electronics: 15-day return window
- Final sale items: No returns accepted
- Opened software: Exchange only

## Process
1. Log into your account
2. Go to Order History
3. Click "Return Item" next to the product
4. Print the prepaid shipping label
5. Drop off at any UPS location
```

```text
# src/main/resources/docs/shipping-policy.md
# ShopZilla Shipping Policy

## Standard Shipping
- Free on orders over $50
- 5-7 business days delivery
- Available to all 50 US states

## Express Shipping
- $12.99 flat rate
- 2-3 business days
- Order by 2 PM for same-day processing

## International
- Not currently available
- Coming Q2 2025
```

---

## Step 3: Ingest Documents into Vector Store

```java
// src/main/java/com/shopzilla/ai/config/DocumentIngestion.java
package com.shopzilla.ai.config;

import org.springframework.ai.document.Document;
import org.springframework.ai.reader.tika.TikaDocumentReader;
import org.springframework.ai.transformer.splitter.TokenTextSplitter;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class DocumentIngestion implements CommandLineRunner {

    private final VectorStore vectorStore;

    public DocumentIngestion(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    @Override
    public void run(String... args) throws Exception {
        var resolver = new PathMatchingResourcePatternResolver();
        Resource[] resources = resolver.getResources("classpath:docs/*.md");

        List<Document> allDocuments = new ArrayList<>();

        for (Resource resource : resources) {
            var reader = new TikaDocumentReader(resource);
            List<Document> documents = reader.get();

            // Split into chunks (LLMs have context limits)
            var splitter = new TokenTextSplitter();
            List<Document> chunks = splitter.apply(documents);

            allDocuments.addAll(chunks);
        }

        vectorStore.add(allDocuments);
        System.out.println("Ingested " + allDocuments.size() + " document chunks");
    }
}
```

### What Happens

1. **Read** — Tika reads markdown/PDF/text files
2. **Split** — TokenTextSplitter breaks them into chunks (~500 tokens each)
3. **Embed** — Each chunk is converted to a vector (array of numbers) using `nomic-embed-text`
4. **Store** — Vectors are stored in pgvector for fast similarity search

---

## Step 4: Query with RAG (QuestionAnswerAdvisor)

```java
// src/main/java/com/shopzilla/ai/service/ChatService.java
import org.springframework.ai.chat.client.advisor.QuestionAnswerAdvisor;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;

@Service
public class ChatService {

    private final ChatClient chatClient;

    public ChatService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder
                .defaultSystem("""
                    You are ShopZilla's customer support assistant.
                    Answer questions based ONLY on the provided context.
                    If the context doesn't contain the answer, say "I don't have that information."
                    Never make up policies or facts.
                    """)
                .defaultAdvisors(
                    MessageChatMemoryAdvisor.builder(new InMemoryChatMemory()).build(),
                    new QuestionAnswerAdvisor(vectorStore,
                        SearchRequest.builder().topK(3).build())
                )
                .build();
    }

    public String chat(String conversationId, String message) {
        return chatClient.prompt()
                .user(message)
                .advisors(a -> a.param(
                    MessageChatMemoryAdvisor.CHAT_MEMORY_CONVERSATION_ID_KEY,
                    conversationId
                ))
                .call()
                .content();
    }
}
```

### What QuestionAnswerAdvisor Does

1. Takes the user's question
2. Converts it to a vector (embedding)
3. Searches pgvector for the 3 most similar document chunks
4. Appends those chunks to the prompt as context
5. The LLM answers based on the retrieved context

---

## Test It

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversationId": "karen-1", "message": "What is your return policy?"}'
```

```json
{
  "content": "Our return policy allows returns within 30 days of delivery. You'll need your original receipt or order confirmation, and items must be unused and in original packaging. Note that electronics have a shorter 15-day window, and final sale items cannot be returned. Refunds are issued to your original payment method within 5-7 business days."
}
```

Correct. Grounded in real data. No hallucination.

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversationId": "karen-1", "message": "Do you accept Bitcoin?"}'
```

```json
{
  "content": "I don't have information about Bitcoin payments in our documentation. I'd recommend contacting our support team directly for the most up-to-date payment options."
}
```

It doesn't hallucinate. It says "I don't know" — because the docs don't mention Bitcoin.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
Embedding model (nomic-embed)   │ Converts text → vector (numbers)
VectorStore (pgvector)          │ Stores and searches vectors
TikaDocumentReader              │ Reads PDF, MD, DOCX, etc.
TokenTextSplitter               │ Splits docs into LLM-sized chunks
QuestionAnswerAdvisor           │ Auto-retrieves relevant docs
SearchRequest.topK(3)           │ Return top 3 most similar chunks
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Karen: "I asked about my order status and it said 'I don't have that information.' But we HAVE that data — in the order database. Can it look up real orders?"

The LLM can't query databases. But you can give it tools — functions it can call to get real data.

Function calling.

---

[← Chapter 5: Memory](chapter-05-memory.md) | [Chapter 7: Function Calling →](chapter-07-function-calling.md)
