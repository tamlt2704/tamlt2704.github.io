# Chapter 4: Streaming — Token by Token

[← Chapter 3: Structured Output](chapter-03-structured-output.md) | [Chapter 5: Conversation Memory →](chapter-05-memory.md)

---

## The Problem

Karen types a question. Waits 5 seconds. Gets a wall of text all at once. "Is it broken? Why is nothing happening?"

LLMs generate tokens one at a time. Instead of waiting for all 200 tokens, stream them to the browser as they're produced. The user sees words appearing in real-time — like ChatGPT.

---

## Streaming with Spring AI

```java
// src/main/java/com/shopzilla/ai/controller/ChatController.java
import org.springframework.web.bind.annotation.*;
import org.springframework.http.MediaType;
import reactor.core.publisher.Flux;

@GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStream(@RequestParam String message) {
    return chatClient.prompt()
            .system("You are ShopZilla's helpful customer support assistant.")
            .user(message)
            .stream()
            .content();
}
```

### What Changed

| Before (blocking) | After (streaming) |
|---|---|
| `.call()` | `.stream()` |
| Returns `String` | Returns `Flux<String>` |
| Waits for full response | Emits tokens as they arrive |
| `application/json` | `text/event-stream` (SSE) |

---

## Server-Sent Events (SSE)

The response is a stream of events:

```bash
curl -N "http://localhost:8080/api/chat/stream?message=What+is+your+return+policy?"
```

```
data:Our
data: return
data: policy
data: allows
data: you
data: to
data: return
data: items
data: within
data: 30
data: days
data:...
```

Each `data:` line is one token (or a few tokens). The browser receives them in real-time.

---

## Frontend: Consuming the Stream

```javascript
// Browser-side JavaScript (or React component)
const eventSource = new EventSource('/api/chat/stream?message=Hello');
let fullResponse = '';

eventSource.onmessage = (event) => {
    fullResponse += event.data;
    document.getElementById('response').textContent = fullResponse;
};

eventSource.onerror = () => {
    eventSource.close();
};
```

Or with `fetch` for more control:

```javascript
const response = await fetch('/api/chat/stream?message=Hello');
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    document.getElementById('response').textContent += chunk;
}
```

---

## Streaming with Full Response Metadata

```java
@GetMapping(value = "/stream/full", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ChatResponse> chatStreamFull(@RequestParam String message) {
    return chatClient.prompt()
            .user(message)
            .stream()
            .chatResponse();
}
```

Each event includes metadata (model, token count, finish reason). Useful for debugging and monitoring.

---

## POST Endpoint for Streaming (Real-World)

GET requests have URL length limits. For real chat, use POST:

```java
@PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStreamPost(@RequestBody ChatRequest request) {
    return chatClient.prompt()
            .system("You are ShopZilla's customer support assistant.")
            .user(request.message())
            .stream()
            .content();
}

record ChatRequest(String message) {}
```

---

## Timeout and Error Handling

```java
@GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStream(@RequestParam String message) {
    return chatClient.prompt()
            .user(message)
            .stream()
            .content()
            .timeout(Duration.ofSeconds(30))
            .onErrorResume(e -> Flux.just("[Error: " + e.getMessage() + "]"));
}
```

If Ollama is slow or crashes, the stream times out gracefully instead of hanging forever.

---

## When to Stream vs When to Block

| Use Case | Approach | Why |
|---|---|---|
| Chat interface | Stream | User sees progress, feels fast |
| Product descriptions (batch) | Block | Need complete text for database |
| Structured output (JSON) | Block | Can't parse partial JSON |
| Review analysis | Block | Need the full analysis object |
| Long-form content | Stream | User can start reading immediately |

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Method                          │ What It Does
────────────────────────────────┼──────────────────────────────────────
.stream().content()             │ Flux<String> — token stream
.stream().chatResponse()        │ Flux<ChatResponse> — with metadata
MediaType.TEXT_EVENT_STREAM_VALUE│ SSE content type
Flux.timeout(Duration)          │ Cancel if too slow
Flux.onErrorResume()            │ Graceful error handling
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Karen: "I asked it about my order and it forgot what I said 10 seconds ago. I said 'order #12345' and then asked 'what's the status?' and it said 'I don't know what order you're referring to.' It has no memory."

Conversation memory. Chat history. Context.

---

[← Chapter 3: Structured Output](chapter-03-structured-output.md) | [Chapter 5: Conversation Memory →](chapter-05-memory.md)
