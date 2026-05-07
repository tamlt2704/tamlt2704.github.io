# Chapter 11: Performance — Caching, Batching, Async

[← Chapter 10: Multi-Model](chapter-10-multi-model.md) | [Chapter 12: Testing & Observability →](chapter-12-testing.md)

---

## The Problem

Mrs. Jira submits 200 products for description generation. At 8 seconds each (sequentially), that's 26 minutes. Silent Bob's monitoring shows Ollama at 100% GPU. Other requests queue behind the batch.

Three problems: too slow, no caching, no concurrency control.

---

## Problem 1: Response Caching

The same product asked twice shouldn't hit the LLM twice:

```java
// src/main/java/com/shopzilla/ai/service/CachedDescriptionService.java
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class CachedDescriptionService {

    private final ChatClient chatClient;

    @Cacheable(value = "descriptions", key = "#name + '-' + #category + '-' + #price")
    public String generateDescription(String name, String category,
                                       double price, String feature) {
        return chatClient.prompt()
                .user(/* prompt */)
                .call()
                .content();
    }
}
```

```java
// src/main/java/com/shopzilla/ai/config/CacheConfig.java
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import com.github.benmanes.caffeine.cache.Caffeine;

@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CaffeineCacheManager cacheManager() {
        CaffeineCacheManager manager = new CaffeineCacheManager("descriptions", "embeddings");
        manager.setCaffeine(Caffeine.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(Duration.ofHours(24))
                .recordStats());
        return manager;
    }
}
```

First request: 8 seconds (LLM generates). Second identical request: <1ms (cache hit). Mrs. Jira re-runs the batch after a typo fix — only changed products hit the LLM.

---

## Problem 2: Async Batch Processing

Don't process 200 products sequentially. Use virtual threads:

```java
// src/main/java/com/shopzilla/ai/service/BatchService.java
import java.util.concurrent.*;

@Service
public class BatchService {

    private final CachedDescriptionService descriptionService;
    private final ExecutorService executor;

    public BatchService(CachedDescriptionService descriptionService) {
        this.descriptionService = descriptionService;
        // Limit concurrency — don't overwhelm Ollama
        this.executor = Executors.newFixedThreadPool(3);
    }

    public CompletableFuture<List<BatchResult>> processBatch(List<ProductInput> products) {
        List<CompletableFuture<BatchResult>> futures = products.stream()
                .map(product -> CompletableFuture.supplyAsync(() -> {
                    try {
                        String description = descriptionService.generateDescription(
                                product.name(), product.category(),
                                product.price(), product.feature()
                        );
                        return new BatchResult(product.id(), description, null);
                    } catch (Exception e) {
                        return new BatchResult(product.id(), null, e.getMessage());
                    }
                }, executor))
                .toList();

        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .thenApply(v -> futures.stream()
                        .map(CompletableFuture::join)
                        .toList());
    }

    record ProductInput(String id, String name, String category, double price, String feature) {}
    record BatchResult(String productId, String description, String error) {}
}
```

3 concurrent requests to Ollama. 200 products at 8 seconds each with 3 threads: ~9 minutes instead of 26. With caching on re-runs: seconds.

---

## Problem 3: Backpressure

Don't let batch requests starve the chat endpoint. Use a semaphore:

```java
@Service
public class RateLimitedAiService {

    private final Semaphore ollamaSemaphore = new Semaphore(4); // max 4 concurrent LLM calls
    private final ChatClient chatClient;

    public String generate(String prompt) throws InterruptedException {
        ollamaSemaphore.acquire();
        try {
            return chatClient.prompt()
                    .user(prompt)
                    .call()
                    .content();
        } finally {
            ollamaSemaphore.release();
        }
    }
}
```

4 slots total. If the batch uses 3, chat still gets 1. No starvation.

---

## Problem 4: Timeout Handling

Ollama can hang on complex prompts. Set timeouts:

```yaml
# application.yml
spring:
  ai:
    ollama:
      chat:
        options:
          num-predict: 500    # cap output length
      init:
        timeout: 60s         # model loading timeout
        pull-model-strategy: never  # don't auto-pull (we manage models)
```

```java
// Per-request timeout
public String generateWithTimeout(String prompt) {
    try {
        return CompletableFuture.supplyAsync(() ->
                chatClient.prompt().user(prompt).call().content()
        ).get(30, TimeUnit.SECONDS);
    } catch (TimeoutException e) {
        return "Generation timed out. Please try a shorter request.";
    }
}
```

---

## Problem 5: Embedding Cache

Embedding the same document twice is wasteful:

```java
@Cacheable(value = "embeddings", key = "#text.hashCode()")
public float[] embed(String text) {
    return embeddingModel.embed(text);
}
```

Product catalog re-indexing goes from 10 minutes to 30 seconds (only new/changed products get embedded).

---

## Monitoring Performance

```java
// src/main/java/com/shopzilla/ai/metrics/AiMetrics.java
import io.micrometer.core.instrument.*;

@Component
public class AiMetrics {

    private final Timer llmLatency;
    private final Counter llmCalls;
    private final Counter cacheHits;

    public AiMetrics(MeterRegistry registry) {
        this.llmLatency = Timer.builder("ai.llm.latency")
                .description("LLM response time")
                .register(registry);
        this.llmCalls = Counter.builder("ai.llm.calls")
                .description("Total LLM calls")
                .register(registry);
        this.cacheHits = Counter.builder("ai.cache.hits")
                .description("Cache hits")
                .register(registry);
    }

    public <T> T timeCall(Supplier<T> call) {
        llmCalls.increment();
        return llmLatency.record(call);
    }
}
```

---

## Results

| Metric | Before | After |
|---|---|---|
| 200 products (sequential) | 26 minutes | 9 minutes |
| 200 products (with cache, re-run) | 26 minutes | 3 seconds |
| Chat response (during batch) | Timeout | <5 seconds |
| Embedding re-index (500 products) | 10 minutes | 30 seconds |

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Solves
────────────────────────────────┼──────────────────────────────────────
@Cacheable                      │ Don't call LLM twice for same input
Semaphore(N)                    │ Limit concurrent LLM calls
ExecutorService (fixed pool)    │ Parallel batch processing
CompletableFuture.get(timeout)  │ Don't wait forever
num-predict limit               │ Cap output length (faster responses)
Caffeine cache                  │ Fast in-memory cache with TTL
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Captain Deadline: "How do I know it's working? How do I know the answers are good? How do I test an AI system? You can't unit test randomness."

Testing LLM applications. Mocking. Evaluation. Observability.

---

[← Chapter 10: Multi-Model](chapter-10-multi-model.md) | [Chapter 12: Testing & Observability →](chapter-12-testing.md)
