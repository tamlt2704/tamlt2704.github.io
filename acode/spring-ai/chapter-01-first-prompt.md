# Chapter 1: Your First Prompt — Hello, Ollama

[← Overview](chapter-00-overview.md) | [Chapter 2: Prompt Templates →](chapter-02-prompt-templates.md)

---

## The Task

Captain Deadline: "Prove it works. Send a prompt to the local LLM. Get a response. Show me in the browser."

---

## Create the Project

```bash
mkdir shopzilla-ai && cd shopzilla-ai
```

`build.gradle`:

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.4.1'
    id 'io.spring.dependency-management' version '1.1.7'
}

group = 'com.shopzilla'
version = '1.0.0'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
    maven { url 'https://repo.spring.io/milestone' }
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.ai:spring-ai-ollama-spring-boot-starter'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

dependencyManagement {
    imports {
        mavenBom 'org.springframework.ai:spring-ai-bom:1.0.0'
    }
}
```

`settings.gradle`:

```groovy
rootProject.name = 'shopzilla-ai'
```

---

## Configuration

```yaml
# src/main/resources/application.yml
spring:
  ai:
    ollama:
      base-url: http://localhost:11434
      chat:
        model: llama3.1
        options:
          temperature: 0.7
          num-predict: 500
```

| Property | What It Does |
|---|---|
| `base-url` | Where Ollama is running |
| `model` | Which model to use (must be pulled first) |
| `temperature` | Creativity (0 = deterministic, 1 = creative) |
| `num-predict` | Max tokens in response |

---

## The Main Class

```java
// src/main/java/com/shopzilla/ai/ShopZillaAiApplication.java
package com.shopzilla.ai;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ShopZillaAiApplication {
    public static void main(String[] args) {
        SpringApplication.run(ShopZillaAiApplication.class, args);
    }
}
```

---

## ChatClient: The Core Abstraction

Spring AI's `ChatClient` is your interface to any LLM. It works the same whether you're talking to Ollama, OpenAI, Anthropic, or any other provider. Switch models by changing config — not code.

```java
// src/main/java/com/shopzilla/ai/controller/ChatController.java
package com.shopzilla.ai.controller;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatClient chatClient;

    public ChatController(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }

    @GetMapping
    public String chat(@RequestParam String message) {
        return chatClient.prompt()
                .user(message)
                .call()
                .content();
    }
}
```

### Breaking It Down

```java
chatClient.prompt()      // start building a prompt
    .user(message)       // the user's message
    .call()              // send to LLM, wait for response
    .content();          // extract the text content
```

That's it. One dependency. One config. One method chain. You're talking to a local LLM.

---

## Try It

```bash
./gradlew bootRun
```

```bash
curl "http://localhost:8080/api/chat?message=What+is+Spring+Boot+in+one+sentence?"
```

```
Spring Boot is a Java framework that simplifies building production-ready
applications by providing auto-configuration, embedded servers, and
opinionated defaults.
```

It works. The LLM is running locally on your machine. No API key. No cloud. No data leaving your network.

---

## System Messages: Setting the Personality

Right now the LLM is generic. It doesn't know it's ShopZilla's assistant. Fix that:

```java
@GetMapping
public String chat(@RequestParam String message) {
    return chatClient.prompt()
            .system("You are ShopZilla's customer support assistant. " +
                    "You help customers with product questions, orders, and returns. " +
                    "Be friendly, concise, and helpful. " +
                    "If you don't know something, say so — never make up information.")
            .user(message)
            .call()
            .content();
}
```

The system message sets the LLM's role and behavior. It's like giving an employee their job description before they start answering phones.

```bash
curl "http://localhost:8080/api/chat?message=Do+you+accept+Bitcoin?"
```

Before system message: "Yes, many companies accept Bitcoin..."
After system message: "I'm not sure about our payment methods. Let me check — could you contact our support team for the most up-to-date payment options?"

Better. But still not perfect — we'll fix hallucinations properly in Chapter 6 (RAG) and Chapter 9 (guardrails).

---

## Understanding the Request/Response

```java
// For more control, use the full response object
@GetMapping("/detailed")
public Map<String, Object> chatDetailed(@RequestParam String message) {
    var response = chatClient.prompt()
            .user(message)
            .call()
            .chatResponse();

    var result = response.getResult();
    var metadata = result.getMetadata();

    return Map.of(
        "content", result.getOutput().getText(),
        "model", metadata.getModel(),
        "finishReason", metadata.getFinishReason(),
        "totalTokens", response.getMetadata().getUsage().getTotalTokens()
    );
}
```

```bash
curl "http://localhost:8080/api/chat/detailed?message=Hello"
```

```json
{
  "content": "Hello! Welcome to ShopZilla. How can I help you today?",
  "model": "llama3.1",
  "finishReason": "stop",
  "totalTokens": 47
}
```

Token usage tells you how much "compute" each request costs. Important for capacity planning when Silent Bob asks "how many GPUs do we need?"

---

## Multiple Models

Ollama can run multiple models. You might want a fast model for simple tasks and a larger one for complex reasoning:

```yaml
# application.yml
spring:
  ai:
    ollama:
      base-url: http://localhost:11434
      chat:
        model: llama3.1  # default model
```

```java
// Override per-request
@GetMapping("/fast")
public String fastChat(@RequestParam String message) {
    return chatClient.prompt()
            .user(message)
            .options(OllamaOptions.builder()
                    .model("mistral")  // use faster model
                    .temperature(0.3)   // less creative, more focused
                    .build())
            .call()
            .content();
}
```

---

## What Just Happened

```
Your App (Spring AI)          Ollama (localhost:11434)         LLM (llama3.1)
       │                              │                              │
       ├─ POST /api/chat ────────────►├─ tokenize prompt ───────────►│
       │                              │                              │
       │                              │◄── generate tokens ──────────┤
       │                              │    (one by one)              │
       │◄── complete response ────────┤                              │
       │                              │                              │
```

Spring AI sends your prompt to Ollama's HTTP API. Ollama feeds it to the model. The model generates tokens. Ollama collects them and returns the full response. Spring AI wraps it in a nice Java object.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
ChatClient.Builder              │ Injected by Spring AI auto-config
chatClient.prompt()             │ Start building a request
.system(text)                   │ Set the LLM's role/personality
.user(text)                     │ The user's message
.call()                         │ Send and wait for full response
.content()                      │ Extract text from response
.chatResponse()                 │ Full response with metadata
OllamaOptions.builder()         │ Override model, temperature per-request
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Mrs. Jira: "I need product descriptions. Give it a product name, category, and price — get back a marketing description. But they need to be consistent. Same tone. Same length. Same format every time."

Prompt templates.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Prompt Templates →](chapter-02-prompt-templates.md)
