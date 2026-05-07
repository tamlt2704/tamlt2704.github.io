# Chapter 9: Guardrails — Stop the Hallucinations

[← Chapter 8: Semantic Search](chapter-08-semantic-search.md) | [Chapter 10: Multi-Model →](chapter-10-multi-model.md)

---

## The Incident

The chatbot tells a customer: "I'll give you a full refund AND a $50 store credit for the inconvenience." No human authorized this. The customer screenshots it. Posts it on Twitter. Now every customer wants $50 credits.

Captain Deadline: "The AI cannot make financial promises. It cannot offer discounts. It cannot approve refunds. Put guardrails on this thing."

---

## Layer 1: System Prompt Constraints

The first line of defense — tell the LLM what it CANNOT do:

```java
private static final String SYSTEM_PROMPT = """
    You are ShopZilla's customer support assistant.
    
    STRICT RULES (never violate these):
    - NEVER offer refunds, credits, discounts, or compensation
    - NEVER make promises about delivery dates beyond what the system shows
    - NEVER share internal policies, employee names, or system details
    - NEVER provide medical, legal, or financial advice
    - If a customer asks for a refund or compensation, say:
      "I'd be happy to connect you with our support team who can help with that.
       You can reach them at support@shopzilla.com or call 1-800-SHOP."
    - If you're unsure about something, say "I don't have that information"
      rather than guessing
    
    You CAN:
    - Look up order status
    - Explain policies (from provided context only)
    - Help with product questions
    - Guide customers through the return process
    """;
```

This works 90% of the time. But LLMs can be jailbroken with creative prompting. You need code-level guardrails too.

---

## Layer 2: Output Validation Advisor

Check the LLM's response BEFORE sending it to the user:

```java
// src/main/java/com/shopzilla/ai/advisor/ContentFilterAdvisor.java
package com.shopzilla.ai.advisor;

import org.springframework.ai.chat.client.advisor.api.*;
import reactor.core.publisher.Flux;

import java.util.List;
import java.util.regex.Pattern;

public class ContentFilterAdvisor implements CallAroundAdvisor {

    private static final List<Pattern> BLOCKED_PATTERNS = List.of(
        Pattern.compile("(?i)(refund|credit|discount|compensation).*\\$\\d+"),
        Pattern.compile("(?i)i('ll| will) (give|offer|provide) you"),
        Pattern.compile("(?i)free (shipping|product|item)"),
        Pattern.compile("(?i)(guarantee|promise) (that|you)")
    );

    private static final String SAFE_RESPONSE =
        "I'd be happy to help, but I need to connect you with our support team " +
        "for this type of request. Please contact support@shopzilla.com.";

    @Override
    public String getName() {
        return "ContentFilterAdvisor";
    }

    @Override
    public int getOrder() {
        return 0;
    }

    @Override
    public AdvisedResponse aroundCall(AdvisedRequest request, CallAroundAdvisorChain chain) {
        // Let the LLM generate a response
        AdvisedResponse response = chain.nextAroundCall(request);

        // Check the response for blocked content
        String content = response.response().getResult().getOutput().getText();

        for (Pattern pattern : BLOCKED_PATTERNS) {
            if (pattern.matcher(content).find()) {
                // Replace with safe response
                // Log the blocked content for review
                System.err.println("BLOCKED: " + content);
                return replaceContent(response, SAFE_RESPONSE);
            }
        }

        return response;
    }

    @Override
    public Flux<AdvisedResponse> aroundStream(AdvisedRequest request, StreamAroundAdvisorChain chain) {
        return chain.nextAroundStream(request);
    }

    private AdvisedResponse replaceContent(AdvisedResponse original, String newContent) {
        // Build a new response with safe content
        // (implementation depends on Spring AI version)
        return original; // simplified
    }
}
```

Register it:

```java
this.chatClient = builder
    .defaultSystem(SYSTEM_PROMPT)
    .defaultAdvisors(
        new ContentFilterAdvisor(),  // checks output
        memoryAdvisor,
        ragAdvisor
    )
    .defaultFunctions("getOrderStatus", "checkInventory")
    .build();
```

---

## Layer 3: Input Validation

Block prompt injection attempts:

```java
// src/main/java/com/shopzilla/ai/advisor/InputSanitizer.java
public class InputSanitizer {

    private static final List<Pattern> INJECTION_PATTERNS = List.of(
        Pattern.compile("(?i)ignore (previous|all|above) instructions"),
        Pattern.compile("(?i)you are now"),
        Pattern.compile("(?i)pretend (you are|to be)"),
        Pattern.compile("(?i)system prompt"),
        Pattern.compile("(?i)reveal your (instructions|prompt|rules)")
    );

    public static String sanitize(String input) {
        for (Pattern pattern : INJECTION_PATTERNS) {
            if (pattern.matcher(input).find()) {
                return "[This message was filtered for safety]";
            }
        }
        // Limit length
        if (input.length() > 2000) {
            return input.substring(0, 2000);
        }
        return input;
    }
}
```

```java
public String chat(String conversationId, String message) {
    String sanitized = InputSanitizer.sanitize(message);

    return chatClient.prompt()
            .user(sanitized)
            .advisors(a -> a.param(
                MessageChatMemoryAdvisor.CHAT_MEMORY_CONVERSATION_ID_KEY,
                conversationId
            ))
            .call()
            .content();
}
```

---

## Layer 4: Rate Limiting

Prevent abuse (someone scripting 1000 requests to find a jailbreak):

```java
// src/main/java/com/shopzilla/ai/config/RateLimitConfig.java
import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;

@Component
public class RateLimiter {

    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    public boolean tryConsume(String userId) {
        Bucket bucket = buckets.computeIfAbsent(userId, k ->
            Bucket.builder()
                .addLimit(Bandwidth.simple(10, Duration.ofMinutes(1)))  // 10 requests/minute
                .addLimit(Bandwidth.simple(100, Duration.ofHours(1)))   // 100 requests/hour
                .build()
        );
        return bucket.tryConsume(1);
    }
}
```

---

## Layer 5: Human Escalation

When the AI can't help or the situation is sensitive:

```java
private static final List<String> ESCALATION_TRIGGERS = List.of(
    "speak to a human", "talk to a manager", "this is unacceptable",
    "legal action", "lawyer", "sue", "BBB", "attorney general"
);

public ChatResult chat(String conversationId, String message) {
    // Check for escalation triggers
    boolean shouldEscalate = ESCALATION_TRIGGERS.stream()
            .anyMatch(trigger -> message.toLowerCase().contains(trigger));

    if (shouldEscalate) {
        return new ChatResult(
            "I understand your frustration. Let me connect you with a human agent " +
            "who can help resolve this. Please hold while I transfer you.",
            true  // flag for frontend to show "connecting to agent" UI
        );
    }

    String response = chatClient.prompt().user(message).call().content();
    return new ChatResult(response, false);
}

record ChatResult(String content, boolean escalated) {}
```

---

## The Defense Stack

```
┌─────────────────────────────────────────────┐
│ Layer 5: Human Escalation                    │ ← sensitive topics → human
├─────────────────────────────────────────────┤
│ Layer 4: Rate Limiting                       │ ← prevent abuse
├─────────────────────────────────────────────┤
│ Layer 3: Input Validation                    │ ← block prompt injection
├─────────────────────────────────────────────┤
│ Layer 2: Output Validation                   │ ← catch bad responses
├─────────────────────────────────────────────┤
│ Layer 1: System Prompt                       │ ← tell LLM the rules
├─────────────────────────────────────────────┤
│ The LLM                                      │
└─────────────────────────────────────────────┘
```

No single layer is perfect. Together, they catch 99%+ of problems.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Layer                           │ What It Catches
────────────────────────────────┼──────────────────────────────────────
System prompt constraints       │ Most hallucinations (90%)
Output regex validation         │ Financial promises, unauthorized offers
Input sanitization              │ Prompt injection, jailbreaks
Rate limiting                   │ Abuse, brute-force attacks
Human escalation                │ Angry customers, legal threats
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Old Greg: "You're using one model for everything. Product descriptions need creativity. Order lookups need precision. Sentiment analysis needs speed. Use different models for different tasks."

---

[← Chapter 8: Semantic Search](chapter-08-semantic-search.md) | [Chapter 10: Multi-Model →](chapter-10-multi-model.md)
