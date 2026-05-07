# Chapter 7: Function Calling — The LLM Uses Your Code

[← Chapter 6: RAG](chapter-06-rag.md) | [Chapter 8: Semantic Search →](chapter-08-semantic-search.md)

---

## The Problem

Karen: "I asked 'where is my order #5678?' and it said 'I don't have access to order information.' But we have an order database. Can't it just... look it up?"

The LLM can't query databases. It generates text. But you can register functions that the LLM can CHOOSE to call when it needs real data.

---

## How Function Calling Works

```
1. User: "Where is my order #5678?"
2. LLM thinks: "I need order data. I have a function called 'getOrderStatus'."
3. LLM responds: "I want to call getOrderStatus(orderId: '5678')"
4. Spring AI intercepts, calls YOUR Java function
5. Your function queries the database, returns: {status: "shipped", eta: "Jan 20"}
6. Spring AI sends the result back to the LLM
7. LLM: "Your order #5678 has shipped and should arrive by January 20th."
```

The LLM decides WHEN to call a function. Your code decides WHAT the function does.

---

## Define a Function

```java
// src/main/java/com/shopzilla/ai/functions/OrderFunctions.java
package com.shopzilla.ai.functions;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Description;

import java.util.Map;
import java.util.function.Function;

@Configuration
public class OrderFunctions {

    // Simulated order database
    private static final Map<String, OrderInfo> ORDERS = Map.of(
        "5678", new OrderInfo("5678", "shipped", "Jan 20, 2025", "Wireless Headphones"),
        "9012", new OrderInfo("9012", "processing", "Jan 25, 2025", "USB-C Cable"),
        "3456", new OrderInfo("3456", "delivered", "Jan 10, 2025", "Laptop Stand")
    );

    public record OrderRequest(String orderId) {}
    public record OrderInfo(String orderId, String status, String estimatedDelivery, String product) {}

    @Bean
    @Description("Get the status of a customer order by order ID. Returns shipping status and estimated delivery date.")
    public Function<OrderRequest, OrderInfo> getOrderStatus() {
        return request -> {
            OrderInfo order = ORDERS.get(request.orderId());
            if (order == null) {
                return new OrderInfo(request.orderId(), "not_found", null, null);
            }
            return order;
        };
    }
}
```

### Key Points

- `@Bean` — registers it as a Spring bean
- `@Description` — tells the LLM what this function does (critical for the LLM to know WHEN to use it)
- Input: `OrderRequest` record (the LLM fills this in)
- Output: `OrderInfo` record (sent back to the LLM as context)

---

## Register Functions with ChatClient

```java
// src/main/java/com/shopzilla/ai/service/ChatService.java
@Service
public class ChatService {

    private final ChatClient chatClient;

    public ChatService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder
                .defaultSystem("""
                    You are ShopZilla's customer support assistant.
                    You can look up order status when customers ask about their orders.
                    You can check product inventory when customers ask about availability.
                    Always use the available tools when you need real data.
                    Never guess order statuses or inventory counts.
                    """)
                .defaultAdvisors(
                    MessageChatMemoryAdvisor.builder(new InMemoryChatMemory()).build(),
                    new QuestionAnswerAdvisor(vectorStore, SearchRequest.builder().topK(3).build())
                )
                .defaultFunctions("getOrderStatus", "checkInventory")
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

---

## More Functions: Inventory Check

```java
@Bean
@Description("Check if a product is in stock. Returns current inventory count and availability.")
public Function<InventoryRequest, InventoryInfo> checkInventory() {
    return request -> {
        // In production: query your inventory database
        int stock = inventoryRepository.getStock(request.productName());
        return new InventoryInfo(request.productName(), stock, stock > 0);
    };
}

public record InventoryRequest(String productName) {}
public record InventoryInfo(String product, int stockCount, boolean available) {}
```

---

## Test It

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversationId": "karen-1", "message": "Where is my order #5678?"}'
```

```json
{
  "content": "Your order #5678 (Wireless Headphones) has shipped and is estimated to arrive by January 20th, 2025."
}
```

The LLM:
1. Recognized this is an order status question
2. Decided to call `getOrderStatus`
3. Extracted `orderId: "5678"` from the message
4. Received the order data
5. Formatted a natural language response

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"conversationId": "karen-1", "message": "Is the Laptop Stand in stock?"}'
```

```json
{
  "content": "Yes, the Laptop Stand is currently in stock. Would you like me to help you place an order?"
}
```

---

## Multiple Function Calls in One Turn

The LLM can call multiple functions if needed:

```
User: "What's the status of order #5678 and is the USB-C Cable in stock?"

LLM decides to call:
  1. getOrderStatus(orderId: "5678")
  2. checkInventory(productName: "USB-C Cable")

Both results come back, LLM combines them:
"Your order #5678 has shipped (arriving Jan 20). And yes, the USB-C Cable is in stock!"
```

---

## Safety: What Functions Can't Do

Functions are read-only by default. The LLM can LOOK UP data but shouldn't MODIFY it without explicit confirmation:

```java
@Bean
@Description("Cancel a customer order. Only call this if the customer explicitly confirms they want to cancel.")
public Function<CancelRequest, CancelResult> cancelOrder() {
    return request -> {
        // Add confirmation check
        if (!request.confirmed()) {
            return new CancelResult(false, "Please confirm: are you sure you want to cancel order " + request.orderId() + "?");
        }
        orderService.cancel(request.orderId());
        return new CancelResult(true, "Order cancelled successfully.");
    };
}

public record CancelRequest(String orderId, boolean confirmed) {}
public record CancelResult(boolean success, String message) {}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
@Bean Function<In, Out>         │ Register a callable function
@Description("...")             │ Tell LLM when to use this function
.defaultFunctions("name")       │ Make functions available to ChatClient
Input record                    │ LLM fills this from the conversation
Output record                   │ Sent back to LLM as context
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Mrs. Jira: "Customers search for 'something to keep my coffee warm' and get zero results because no product is named that. Can the AI understand what they MEAN, not just what they type?"

Semantic search. Understanding intent, not just keywords.

---

[← Chapter 6: RAG](chapter-06-rag.md) | [Chapter 8: Semantic Search →](chapter-08-semantic-search.md)
