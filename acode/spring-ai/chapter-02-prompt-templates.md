# Chapter 2: Prompt Templates — Consistent Output

[← Chapter 1: First Prompt](chapter-01-first-prompt.md) | [Chapter 3: Structured Output →](chapter-03-structured-output.md)

---

## The Problem

Mrs. Jira: "I asked it to write a product description for 'Wireless Headphones' and got a 500-word essay. Then I asked for 'USB Cable' and got two sentences. I need them ALL to be the same format — 2-3 sentences, include the price, mention a benefit."

The LLM is inconsistent because your prompts are inconsistent. You need templates.

---

## Prompt Templates: Fill-in-the-Blank Prompts

```java
// src/main/java/com/shopzilla/ai/service/ProductDescriptionService.java
package com.shopzilla.ai.service;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class ProductDescriptionService {

    private final ChatClient chatClient;

    private static final String TEMPLATE = """
            You are a product copywriter for ShopZilla, an e-commerce store.
            Write a product description following these rules:
            - Exactly 2-3 sentences
            - Mention the price naturally
            - Highlight one key benefit
            - Tone: friendly, confident, not salesy
            - Do NOT use exclamation marks
            
            Product: {name}
            Category: {category}
            Price: ${price}
            Key feature: {feature}
            
            Description:
            """;

    public ProductDescriptionService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String generateDescription(String name, String category,
                                       double price, String feature) {
        PromptTemplate template = new PromptTemplate(TEMPLATE);
        String prompt = template.render(Map.of(
                "name", name,
                "category", category,
                "price", String.valueOf(price),
                "feature", feature
        ));

        return chatClient.prompt()
                .user(prompt)
                .call()
                .content();
    }
}
```

### The Controller

```java
// src/main/java/com/shopzilla/ai/controller/ProductController.java
package com.shopzilla.ai.controller;

import com.shopzilla.ai.service.ProductDescriptionService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductDescriptionService descriptionService;

    public ProductController(ProductDescriptionService descriptionService) {
        this.descriptionService = descriptionService;
    }

    @PostMapping("/describe")
    public DescriptionResponse describe(@RequestBody DescriptionRequest request) {
        String description = descriptionService.generateDescription(
                request.name(), request.category(),
                request.price(), request.feature()
        );
        return new DescriptionResponse(description);
    }

    record DescriptionRequest(String name, String category, double price, String feature) {}
    record DescriptionResponse(String description) {}
}
```

### Try It

```bash
curl -X POST http://localhost:8080/api/products/describe \
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
  "description": "The Wireless Noise-Cancelling Headphones deliver premium sound with an impressive 40-hour battery life, so you can listen all week without reaching for a charger. At $79.99, they're a solid choice for commuters and remote workers who need focus without the fuss."
}
```

Consistent. Every time. Same tone, same length, same format.

---

## Template from Resource Files

For longer templates, put them in files:

```text
# src/main/resources/prompts/product-description.st
You are a product copywriter for ShopZilla, an e-commerce store.
Write a product description following these rules:
- Exactly 2-3 sentences
- Mention the price naturally
- Highlight one key benefit
- Tone: friendly, confident, not salesy
- Do NOT use exclamation marks

Product: {name}
Category: {category}
Price: ${price}
Key feature: {feature}

Description:
```

```java
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;

@Service
public class ProductDescriptionService {

    @Value("classpath:prompts/product-description.st")
    private Resource promptResource;

    public String generateDescription(String name, String category,
                                       double price, String feature) {
        PromptTemplate template = new PromptTemplate(promptResource);
        String prompt = template.render(Map.of(
                "name", name,
                "category", category,
                "price", String.valueOf(price),
                "feature", feature
        ));

        return chatClient.prompt()
                .user(prompt)
                .call()
                .content();
    }
}
```

Cleaner. Templates live in resource files. Developers can tweak prompts without touching Java code.

---

## System + User Message Pattern

Separate the role (system) from the task (user):

```java
public String generateDescription(String name, String category,
                                   double price, String feature) {
    return chatClient.prompt()
            .system("""
                You are a product copywriter for ShopZilla.
                Rules:
                - Exactly 2-3 sentences
                - Mention the price naturally
                - Highlight one key benefit
                - Tone: friendly, confident, not salesy
                - No exclamation marks
                """)
            .user(String.format("""
                Write a description for:
                Product: %s
                Category: %s
                Price: $%.2f
                Key feature: %s
                """, name, category, price, feature))
            .call()
            .content();
}
```

The system message stays constant across all requests. The user message changes per product. This is the standard pattern for production prompts.

---

## Prompt Engineering Tips

### Be Specific About Format

```
❌ "Write a short description"
✅ "Write exactly 2-3 sentences, under 50 words total"
```

### Give Examples (Few-Shot)

```java
private static final String TEMPLATE = """
    Write a product description in this exact style:
    
    Example input: "Running Shoes, $89.99, lightweight mesh"
    Example output: "These lightweight mesh running shoes keep your feet cool mile after mile. At $89.99, they're built for runners who want comfort without the premium price tag."
    
    Now write for:
    Product: {name}, ${price}, {feature}
    """;
```

### Constrain the Output

```
❌ "Describe this product"
✅ "Describe this product in exactly 2 sentences. First sentence: what it is. Second sentence: why buy it."
```

### Negative Instructions

```
- Do NOT mention competitors
- Do NOT use the word "revolutionary"
- Do NOT make claims about health benefits
```

LLMs follow negative instructions surprisingly well.

---

## Batch Generation

Mrs. Jira: "I have 200 products without descriptions. Generate them all."

```java
@PostMapping("/describe/batch")
public List<DescriptionResponse> describeBatch(@RequestBody List<DescriptionRequest> products) {
    return products.stream()
            .map(p -> new DescriptionResponse(
                    descriptionService.generateDescription(
                            p.name(), p.category(), p.price(), p.feature()
                    )))
            .toList();
}
```

⚠️ This is sequential — each request waits for the LLM. For 200 products at 2 seconds each, that's 400 seconds. We'll fix this with async/batching in Chapter 11.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
PromptTemplate                  │ Template with {placeholders}
template.render(Map.of(...))    │ Fill in the placeholders
@Value("classpath:prompts/x")   │ Load template from resource file
.system(text)                   │ Role/personality (constant)
.user(text)                     │ Task/input (varies per request)
Few-shot examples               │ Show the LLM what you want
Negative instructions           │ Tell it what NOT to do
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Mrs. Jira: "The descriptions are good. But I need them as JSON — with a title, description, and three bullet points. Not free text. Structured data I can put directly into the product database."

Getting structured output from an LLM. The LLM speaks prose — you need objects.

---

[← Chapter 1: First Prompt](chapter-01-first-prompt.md) | [Chapter 3: Structured Output →](chapter-03-structured-output.md)
