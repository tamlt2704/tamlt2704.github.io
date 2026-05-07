# Chapter 5: Conversation Memory — The Chatbot Remembers

[← Chapter 4: Streaming](chapter-04-streaming.md) | [Chapter 6: RAG →](chapter-06-rag.md)

---

## The Problem

Karen: "I said 'I ordered headphones last week' and then asked 'when will they arrive?' and it said 'I don't know what you ordered.' It's like talking to a goldfish."

LLMs are stateless. Every request is independent. They don't remember previous messages unless you explicitly send the conversation history with each request.

---

## How Chat Memory Works

```
Without memory:                    With memory:
┌─────────────────────┐           ┌─────────────────────────────────┐
│ User: I ordered #123│           │ User: I ordered #123            │
│ AI: Got it!         │           │ AI: Got it!                     │
└─────────────────────┘           │ User: When will it arrive?      │
┌─────────────────────┐           │ AI: Let me check order #123...  │
│ User: When arrives? │           └─────────────────────────────────┘
│ AI: What order?     │             ↑ entire history sent each time
└─────────────────────┘
```

You send ALL previous messages with every new request. The LLM reads the full conversation and responds in context.

---

## MessageChatMemoryAdvisor

Spring AI provides advisors that automatically manage chat history:

```java
// src/main/java/com/shopzilla/ai/service/ChatService.java
package com.shopzilla.ai.service;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.InMemoryChatMemory;
import org.springframework.stereotype.Service;

@Service
public class ChatService {

    private final ChatClient chatClient;

    public ChatService(ChatClient.Builder builder) {
        this.chatClient = builder
                .defaultSystem("""
                    You are ShopZilla's customer support assistant.
                    Be helpful, concise, and friendly.
                    If you don't know something, say so.
                    """)
                .defaultAdvisors(
                    MessageChatMemoryAdvisor.builder(new InMemoryChatMemory())
                        .build()
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

### What the Advisor Does

1. Before sending to LLM: retrieves previous messages for this `conversationId` and prepends them
2. After receiving response: stores both the user message and AI response in memory
3. Next request: the full history is included automatically

---

## The Controller

```java
// src/main/java/com/shopzilla/ai/controller/ChatController.java
@PostMapping
public ChatResponse chat(@RequestBody ChatRequest request) {
    String response = chatService.chat(request.conversationId(), request.message());
    return new ChatResponse(response);
}

record ChatRequest(String conversationId, String message) {}
record ChatResponse(String content) {}
```

### Try It

```bash
# First message
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversationId": "karen-123", "message": "I ordered wireless headphones last week, order #5678"}'
# → "Got it! I can see you're asking about order #5678 for wireless headphones."

# Second message — it remembers!
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversationId": "karen-123", "message": "When will they arrive?"}'
# → "Let me check on order #5678 for you. Based on standard shipping..."

# Different conversation — doesn't know about Karen's order
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversationId": "bob-456", "message": "When will they arrive?"}'
# → "I'd be happy to help! Could you provide your order number?"
```

Each `conversationId` has its own isolated history.

---

## Limiting History Size

Conversations get long. Sending 100 messages to the LLM is slow and expensive (tokens). Limit it:

```java
MessageChatMemoryAdvisor.builder(new InMemoryChatMemory())
    .chatMemoryRetrieveSize(10)  // only send last 10 messages
    .build()
```

The advisor keeps the full history but only sends the last 10 messages to the LLM. Old context fades — like human memory.

---

## Persistent Memory (Database-Backed)

`InMemoryChatMemory` dies when the app restarts. For production, persist conversations:

```java
// Using JDBC-backed memory
import org.springframework.ai.chat.memory.JdbcChatMemory;
import javax.sql.DataSource;

@Bean
public ChatMemory chatMemory(DataSource dataSource) {
    return JdbcChatMemory.create(dataSource);
}
```

Or build your own:

```java
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.messages.Message;

@Component
public class RedisChatMemory implements ChatMemory {

    private final RedisTemplate<String, List<Message>> redis;

    @Override
    public void add(String conversationId, List<Message> messages) {
        redis.opsForList().rightPushAll("chat:" + conversationId, messages);
    }

    @Override
    public List<Message> get(String conversationId, int lastN) {
        List<Message> all = redis.opsForList().range("chat:" + conversationId, 0, -1);
        if (all == null) return List.of();
        int start = Math.max(0, all.size() - lastN);
        return all.subList(start, all.size());
    }

    @Override
    public void clear(String conversationId) {
        redis.delete("chat:" + conversationId);
    }
}
```

---

## Streaming with Memory

Memory works with streaming too:

```java
public Flux<String> chatStream(String conversationId, String message) {
    return chatClient.prompt()
            .user(message)
            .advisors(a -> a.param(
                MessageChatMemoryAdvisor.CHAT_MEMORY_CONVERSATION_ID_KEY,
                conversationId
            ))
            .stream()
            .content();
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
MessageChatMemoryAdvisor        │ Auto-manages conversation history
InMemoryChatMemory              │ Stores history in RAM (dev/test)
JdbcChatMemory                  │ Stores history in database (prod)
conversationId                  │ Isolates conversations per user/session
chatMemoryRetrieveSize(N)       │ Only send last N messages to LLM
.defaultAdvisors(...)           │ Apply advisor to all requests
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Karen: "I asked about our return policy and it made something up. It said we accept returns within 90 days. Our policy is 30 days. It's LYING to customers."

The LLM doesn't know your company's policies. It's guessing based on training data. You need to feed it real information.

RAG — Retrieval Augmented Generation. Teach the LLM your actual data.

---

[← Chapter 4: Streaming](chapter-04-streaming.md) | [Chapter 6: RAG →](chapter-06-rag.md)
