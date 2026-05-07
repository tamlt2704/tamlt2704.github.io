# Chapter 3: Structured Output — JSON From the LLM

[← Chapter 2: Prompt Templates](chapter-02-prompt-templates.md) | [Chapter 4: Streaming →](chapter-04-streaming.md)

---

## The Problem

Mrs. Jira: "I don't want free text. I need a JSON object with `title`, `description`, and `bulletPoints` — an array of exactly 3 strings. I'm putting this directly into the product database."

LLMs output text. You need Java objects. Spring AI bridges the gap.

---

## BeanOutputConverter: LLM → Java Object

Define what you want:

```java
// src/main/java/com/shopzilla/ai/model/ProductContent.java
package com.shopzilla.ai.model;

import java.util.List;

public record ProductContent(
        String title,
        String description,
        List<String> bulletPoints
) {}
```

Ask the LLM to fill it:

```java
// src/main/java/com/shopzilla/ai/service/ProductDescriptionService.java
public ProductContent generateStructured(String name, String category,
                                          double price, String feature) {
    return chatClient.prompt()
            .system("""
                You are a product copywriter for ShopZilla.
                Generate marketing content for products.
                """)
            .user(String.format("""
                Generate content for:
                Product: %s
                Category: %s
                Price: $%.2f
                Key feature: %s
                
                Requirements:
                - title: catchy product title (5-8 words)
                - description: 2 sentences, mention price and benefit
                - bulletPoints: exactly 3 short selling points
                """, name, category, price, feature))
            .call()
            .entity(ProductContent.class);
}
```

### The Magic: `.entity(ProductContent.class)`

Spring AI:
1. Appends format instructions to your prompt (tells the LLM to respond in JSON matching the schema)
2. Sends the prompt to the LLM
3. Parses the JSON response
4. Maps it to your Java record

```bash
curl -X POST http://localhost:8080/api/products/describe/structured \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Noise-Cancelling Headphones",
    "category": "Electronics",
    "price": 79.99,
    "feature": "40-hour battery life"
  }'
```

```json
{
  "title": "Wireless Bliss for All-Day Listening",
  "description": "These noise-cancelling headphones deliver 40 hours of uninterrupted audio on a single charge. At $79.99, they're the commuter's best friend.",
  "bulletPoints": [
    "40-hour battery life — charge once, listen all week",
    "Active noise cancellation blocks distractions",
    "Lightweight, foldable design for easy travel"
  ]
}
```

Type-safe. Structured. Ready for the database.

---

## How It Works Under the Hood

Spring AI adds this to your prompt automatically:

```
Your response should be in JSON format.
Do not include any explanations, only provide a RFC8259 compliant JSON response
following this format without deviation.
Do not include markdown code blocks.

Here is the JSON Schema instance your output must adhere to:
{
  "type": "object",
  "properties": {
    "title": { "type": "string" },
    "description": { "type": "string" },
    "bulletPoints": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["title", "description", "bulletPoints"]
}
```

The LLM sees the schema and formats its response accordingly. Most modern LLMs (Llama 3.1, Mistral) handle this well.

---

## Lists and Complex Types

```java
// Get a list of objects
public record ProductSuggestion(String name, String reason, int confidencePercent) {}

public List<ProductSuggestion> suggestRelatedProducts(String productName) {
    return chatClient.prompt()
            .user("Suggest 3 products related to: " + productName)
            .call()
            .entity(new ParameterizedTypeReference<List<ProductSuggestion>>() {});
}
```

```json
[
  { "name": "Headphone Stand", "reason": "Keeps headphones organized", "confidencePercent": 90 },
  { "name": "Replacement Ear Pads", "reason": "Common accessory purchase", "confidencePercent": 85 },
  { "name": "Bluetooth Adapter", "reason": "For non-Bluetooth devices", "confidencePercent": 70 }
]
```

---

## Enums

```java
public enum Sentiment { POSITIVE, NEGATIVE, NEUTRAL, MIXED }

public record ReviewAnalysis(
        Sentiment sentiment,
        String summary,
        List<String> keyTopics
) {}

public ReviewAnalysis analyzeReview(String reviewText) {
    return chatClient.prompt()
            .user("Analyze this product review:\n\n" + reviewText)
            .call()
            .entity(ReviewAnalysis.class);
}
```

```bash
curl -X POST http://localhost:8080/api/reviews/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Great headphones but the case feels cheap. Sound quality is amazing though."}'
```

```json
{
  "sentiment": "MIXED",
  "summary": "Excellent sound quality but build quality of case is disappointing",
  "keyTopics": ["sound quality", "build quality", "case"]
}
```

---

## Handling Parse Failures

Sometimes the LLM doesn't produce valid JSON. Handle it:

```java
public ProductContent generateStructuredSafe(String name, String category,
                                              double price, String feature) {
    try {
        return chatClient.prompt()
                .user(/* ... */)
                .call()
                .entity(ProductContent.class);
    } catch (Exception e) {
        // Retry with lower temperature (more deterministic)
        return chatClient.prompt()
                .user(/* ... */)
                .options(OllamaOptions.builder()
                        .temperature(0.1)
                        .build())
                .call()
                .entity(ProductContent.class);
    }
}
```

Lower temperature = more predictable output = better JSON compliance. Use 0.1-0.3 for structured output, 0.7-0.9 for creative text.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Method                          │ What It Returns
────────────────────────────────┼──────────────────────────────────────
.call().content()               │ Raw String
.call().entity(MyClass.class)   │ Parsed Java object
.call().entity(new PTR<List>()) │ Parsed generic type (List, Map, etc.)
────────────────────────────────┼──────────────────────────────────────
Low temperature (0.1-0.3)       │ Better for structured output
High temperature (0.7-0.9)      │ Better for creative text
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Karen: "The chatbot takes 5 seconds to respond. I'm staring at a blank screen. Can it show words as they come in? Like ChatGPT does?"

Streaming. Token by token.

---

[← Chapter 2: Prompt Templates](chapter-02-prompt-templates.md) | [Chapter 4: Streaming →](chapter-04-streaming.md)
