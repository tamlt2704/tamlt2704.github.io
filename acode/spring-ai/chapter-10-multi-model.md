# Chapter 10: Multi-Model — Right Tool for the Job

[← Chapter 9: Guardrails](chapter-09-guardrails.md) | [Chapter 11: Performance →](chapter-11-performance.md)

---

## The Problem

Old Greg reviews your code. "You're using Llama 3.1 8B for everything. Product descriptions need creativity — use a bigger model. Order status lookups need speed — use a smaller one. Sentiment analysis is simple — Mistral 7B is faster for that."

One model doesn't fit all tasks.

---

## Multiple Models in Ollama

```bash
ollama pull llama3.1        # 8B — general purpose, good quality
ollama pull mistral         # 7B — fast, good at following instructions
ollama pull llama3.1:70b    # 70B — highest quality (needs big GPU)
ollama pull phi3:mini       # 3.8B — tiny, fast, good for simple tasks
```

---

## Task-Specific ChatClients

```java
// src/main/java/com/shopzilla/ai/config/AiConfig.java
package com.shopzilla.ai.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.api.OllamaOptions;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AiConfig {

    @Bean("creativeClient")
    public ChatClient creativeClient(ChatClient.Builder builder) {
        return builder
                .defaultOptions(OllamaOptions.builder()
                        .model("llama3.1")
                        .temperature(0.9)   // high creativity
                        .numPredict(800)    // longer output
                        .build())
                .defaultSystem("You are a creative marketing copywriter.")
                .build();
    }

    @Bean("preciseClient")
    public ChatClient preciseClient(ChatClient.Builder builder) {
        return builder
                .defaultOptions(OllamaOptions.builder()
                        .model("mistral")
                        .temperature(0.1)   // very deterministic
                        .numPredict(200)    // short, focused
                        .build())
                .defaultSystem("You are a precise, factual assistant. Be concise.")
                .build();
    }

    @Bean("fastClient")
    public ChatClient fastClient(ChatClient.Builder builder) {
        return builder
                .defaultOptions(OllamaOptions.builder()
                        .model("phi3:mini")
                        .temperature(0.3)
                        .numPredict(100)
                        .build())
                .defaultSystem("Classify the input. Be brief.")
                .build();
    }
}
```

---

## Using the Right Client Per Task

```java
// src/main/java/com/shopzilla/ai/service/SmartRouter.java
@Service
public class SmartRouter {

    private final ChatClient creativeClient;
    private final ChatClient preciseClient;
    private final ChatClient fastClient;

    public SmartRouter(
            @Qualifier("creativeClient") ChatClient creativeClient,
            @Qualifier("preciseClient") ChatClient preciseClient,
            @Qualifier("fastClient") ChatClient fastClient) {
        this.creativeClient = creativeClient;
        this.preciseClient = preciseClient;
        this.fastClient = fastClient;
    }

    // Creative tasks → big model, high temperature
    public String generateProductDescription(String product) {
        return creativeClient.prompt()
                .user("Write a compelling product description for: " + product)
                .call()
                .content();
    }

    // Factual tasks → precise model, low temperature
    public String summarizeOrder(String orderDetails) {
        return preciseClient.prompt()
                .user("Summarize this order status concisely:\n" + orderDetails)
                .call()
                .content();
    }

    // Classification → fast model, minimal output
    public String classifySentiment(String review) {
        return fastClient.prompt()
                .user("Classify sentiment as POSITIVE, NEGATIVE, or NEUTRAL:\n" + review)
                .call()
                .content();
    }
}
```

---

## Automatic Routing by Intent

Classify the user's intent first (fast model), then route to the appropriate model:

```java
@Service
public class IntentRouter {

    private final ChatClient fastClient;
    private final ChatClient creativeClient;
    private final ChatClient preciseClient;

    public enum Intent { ORDER_STATUS, PRODUCT_QUESTION, CREATIVE_REQUEST, GENERAL }

    public String route(String message) {
        // Step 1: Classify intent (fast, cheap)
        Intent intent = classifyIntent(message);

        // Step 2: Route to appropriate model
        return switch (intent) {
            case ORDER_STATUS -> preciseClient.prompt().user(message).call().content();
            case PRODUCT_QUESTION -> preciseClient.prompt().user(message).call().content();
            case CREATIVE_REQUEST -> creativeClient.prompt().user(message).call().content();
            case GENERAL -> preciseClient.prompt().user(message).call().content();
        };
    }

    private Intent classifyIntent(String message) {
        String classification = fastClient.prompt()
                .user("""
                    Classify this message into exactly one category:
                    ORDER_STATUS, PRODUCT_QUESTION, CREATIVE_REQUEST, GENERAL
                    
                    Message: %s
                    
                    Category:""".formatted(message))
                .call()
                .content()
                .trim()
                .toUpperCase();

        try {
            return Intent.valueOf(classification);
        } catch (IllegalArgumentException e) {
            return Intent.GENERAL;
        }
    }
}
```

---

## Fallback Pattern

If the primary model is slow or down, fall back to another:

```java
public String chatWithFallback(String message) {
    try {
        return preciseClient.prompt()
                .user(message)
                .options(OllamaOptions.builder()
                        .model("llama3.1")
                        .build())
                .call()
                .content();
    } catch (Exception e) {
        // Fallback to smaller, faster model
        return preciseClient.prompt()
                .user(message)
                .options(OllamaOptions.builder()
                        .model("mistral")
                        .build())
                .call()
                .content();
    }
}
```

---

## Model Selection Guide

| Task | Model | Temperature | Why |
|---|---|---|---|
| Product descriptions | llama3.1 (8B+) | 0.8-0.9 | Needs creativity |
| Customer support | mistral (7B) | 0.3-0.5 | Balanced quality/speed |
| Sentiment classification | phi3:mini (3.8B) | 0.1 | Simple task, speed matters |
| Structured output (JSON) | mistral (7B) | 0.1-0.2 | Follows format instructions well |
| Summarization | llama3.1 (8B) | 0.3 | Needs comprehension |
| Code generation | codellama (7B) | 0.2 | Specialized for code |

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ When to Use
────────────────────────────────┼──────────────────────────────────────
@Qualifier("clientName")        │ Inject specific ChatClient bean
OllamaOptions.model("x")       │ Override model per-request
Intent classification → route   │ Use fast model to pick the right big model
Fallback chain                  │ Primary fails → try secondary
Temperature tuning              │ Low = precise, High = creative
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Silent Bob sends a 🐌 emoji. The product description endpoint takes 8 seconds per request. Mrs. Jira wants to generate 200 descriptions. That's 26 minutes. Unacceptable.

Caching. Batching. Async. Make it fast.

---

[← Chapter 9: Guardrails](chapter-09-guardrails.md) | [Chapter 11: Performance →](chapter-11-performance.md)
