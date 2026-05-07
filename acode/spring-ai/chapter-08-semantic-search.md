# Chapter 8: Semantic Search — Understanding Intent

[← Chapter 7: Function Calling](chapter-07-function-calling.md) | [Chapter 9: Guardrails →](chapter-09-guardrails.md)

---

## The Problem

Mrs. Jira: "A customer searched 'something to keep my coffee warm' and got zero results. We sell a 'Thermal Insulated Travel Mug' — that's exactly what they want. But keyword search doesn't connect 'keep coffee warm' to 'thermal insulated mug.'"

Keyword search matches words. Semantic search matches meaning.

---

## How Semantic Search Works

```
Keyword search:
  "keep coffee warm" → search for "keep" OR "coffee" OR "warm" → no match for "Thermal Insulated Travel Mug"

Semantic search:
  "keep coffee warm" → [0.23, -0.45, 0.78, ...] (vector representing the MEANING)
  "Thermal Insulated Travel Mug" → [0.21, -0.42, 0.81, ...] (similar vector!)
  → similarity: 0.92 → MATCH
```

Both phrases mean the same thing. Their vectors are close together in embedding space.

---

## Embed Your Product Catalog

```java
// src/main/java/com/shopzilla/ai/service/ProductSearchService.java
package com.shopzilla.ai.service;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class ProductSearchService {

    private final VectorStore vectorStore;

    public ProductSearchService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    // Call this once to index your products
    public void indexProducts(List<Product> products) {
        List<Document> documents = products.stream()
                .map(p -> new Document(
                        // The text that gets embedded (searchable content)
                        String.format("%s. %s. Category: %s. Good for: %s",
                                p.name(), p.description(), p.category(), p.useCases()),
                        // Metadata (returned with results, not embedded)
                        Map.of(
                                "productId", p.id(),
                                "name", p.name(),
                                "price", String.valueOf(p.price()),
                                "category", p.category(),
                                "type", "product"
                        )
                ))
                .toList();

        vectorStore.add(documents);
    }

    // Semantic search
    public List<ProductResult> search(String query, int limit) {
        List<Document> results = vectorStore.similaritySearch(
                SearchRequest.builder()
                        .query(query)
                        .topK(limit)
                        .similarityThreshold(0.7)  // only return good matches
                        .filterExpression("type == 'product'")  // only search products, not policy docs
                        .build()
        );

        return results.stream()
                .map(doc -> new ProductResult(
                        doc.getMetadata().get("productId").toString(),
                        doc.getMetadata().get("name").toString(),
                        Double.parseDouble(doc.getMetadata().get("price").toString()),
                        doc.getMetadata().get("category").toString()
                ))
                .toList();
    }

    public record Product(String id, String name, String description,
                          String category, double price, String useCases) {}
    public record ProductResult(String id, String name, double price, String category) {}
}
```

---

## The Search Controller

```java
@RestController
@RequestMapping("/api/search")
public class SearchController {

    private final ProductSearchService searchService;

    public SearchController(ProductSearchService searchService) {
        this.searchService = searchService;
    }

    @GetMapping
    public List<ProductSearchService.ProductResult> search(
            @RequestParam String q,
            @RequestParam(defaultValue = "5") int limit) {
        return searchService.search(q, limit);
    }
}
```

---

## Test It

```bash
# Index some products first (one-time setup)
curl -X POST http://localhost:8080/api/search/index

# Now search semantically
curl "http://localhost:8080/api/search?q=something+to+keep+my+coffee+warm"
```

```json
[
  { "id": "prod-42", "name": "Thermal Insulated Travel Mug", "price": 24.99, "category": "Kitchen" },
  { "id": "prod-87", "name": "Electric Mug Warmer", "price": 19.99, "category": "Electronics" },
  { "id": "prod-15", "name": "Double-Wall Ceramic Cup", "price": 14.99, "category": "Kitchen" }
]
```

"Keep coffee warm" matched "Thermal Insulated Travel Mug" — because the embeddings understand they mean the same thing.

More examples:

```bash
curl "http://localhost:8080/api/search?q=gift+for+someone+who+works+from+home"
# → Laptop Stand, Ergonomic Keyboard, Desk Lamp

curl "http://localhost:8080/api/search?q=protect+my+phone+screen"
# → Tempered Glass Screen Protector, Phone Case with Raised Edges
```

---

## Combining Semantic Search with LLM

For a "smart assistant" that searches AND explains:

```java
@PostMapping("/recommend")
public String recommend(@RequestBody RecommendRequest request) {
    // Step 1: Semantic search for relevant products
    List<ProductResult> products = searchService.search(request.query(), 5);

    // Step 2: Ask LLM to recommend from the results
    String productList = products.stream()
            .map(p -> String.format("- %s ($%.2f, %s)", p.name(), p.price(), p.category()))
            .collect(Collectors.joining("\n"));

    return chatClient.prompt()
            .system("You are a helpful shopping assistant. Recommend products based on the customer's needs.")
            .user(String.format("""
                Customer is looking for: %s
                
                Available products:
                %s
                
                Recommend the best 1-2 options and explain why they fit.
                """, request.query(), productList))
            .call()
            .content();
}
```

```bash
curl -X POST http://localhost:8080/api/search/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "I commute by train and want to listen to podcasts without hearing other passengers"}'
```

```json
{
  "content": "I'd recommend the Wireless Noise-Cancelling Headphones ($79.99). The active noise cancellation will block out train noise, and the 40-hour battery means you won't need to charge during your commute week. If you prefer something more compact, the In-Ear ANC Buds ($49.99) are lighter and easier to pocket."
}
```

---

## Filter Expressions

Narrow search by metadata:

```java
// Only search in "Electronics" category
SearchRequest.builder()
    .query("wireless audio")
    .topK(5)
    .filterExpression("category == 'Electronics'")
    .build();

// Products under $50
SearchRequest.builder()
    .query("gift ideas")
    .topK(5)
    .filterExpression("price < 50")
    .build();

// Combine filters
SearchRequest.builder()
    .query("laptop accessories")
    .topK(5)
    .filterExpression("category == 'Electronics' AND price < 100")
    .build();
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
vectorStore.add(documents)      │ Index documents (embed + store)
vectorStore.similaritySearch()  │ Find similar documents by meaning
SearchRequest.topK(N)           │ Return top N results
.similarityThreshold(0.7)       │ Minimum similarity score (0-1)
.filterExpression("key == val") │ Filter by metadata
Document metadata               │ Stored but not embedded (for filtering)
Document content                │ The text that gets embedded
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The chatbot works. It has memory, RAG, function calling, and semantic search. Then it tells a customer "We'll give you a full refund AND a $50 credit" — something no human ever authorized.

Guardrails. Output validation. Stopping the LLM from making promises you can't keep.

---

[← Chapter 7: Function Calling](chapter-07-function-calling.md) | [Chapter 9: Guardrails →](chapter-09-guardrails.md)
