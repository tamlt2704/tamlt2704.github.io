# Chapter 12: The LLM Node (AI Integration)

[← Chapter 11: Error Handling](chapter-11-error-handling.md) | [Chapter 13: Database Node →](chapter-13-database-node.md)

---

## Goal

Build a first-class LLM processing node using Spring AI. Users configure a model, prompt template, and parameters — the node sends the message payload to an LLM and passes the response downstream. By the end: users can build AI-powered flows visually.

## Why Spring AI (Not Raw HTTP)

Spring AI provides:
- Unified API across providers (OpenAI, Anthropic, Ollama, etc.)
- Structured output parsing (JSON mode)
- Prompt templates with variable substitution
- Streaming support
- Retry and rate-limit handling built-in

## Step 1: Add Spring AI Dependency

**build.gradle.kts:**
```kotlin
dependencies {
    // Spring AI
    implementation("org.springframework.ai:spring-ai-openai-spring-boot-starter:1.0.0")
    // For Ollama (local models):
    // implementation("org.springframework.ai:spring-ai-ollama-spring-boot-starter:1.0.0")
}
```

**application.yml:**
```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY:}
      chat:
        options:
          model: gpt-4o-mini
    # For Ollama:
    # ollama:
    #   base-url: http://localhost:11434
    #   chat:
    #     model: llama3
```

## Step 2: LLM Adapter with Spring AI

**src/main/kotlin/com/flowcraft/compiler/adapters/LlmAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.ai.chat.client.ChatClient
import org.springframework.ai.chat.prompt.PromptTemplate
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.stereotype.Component

@Component
class LlmAdapter(
    private val chatClientBuilder: ChatClient.Builder,
) : NodeAdapter {
    override val type = "llm-call"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val promptTemplateStr = node.config["prompt"] as? String ?: "{{payload}}"
        val model = node.config["model"] as? String ?: "gpt-4o-mini"
        val temperature = (node.config["temperature"] as? Number)?.toDouble() ?: 0.7
        val systemPrompt = node.config["systemPrompt"] as? String

        val chatClient = chatClientBuilder
            .defaultOptions(
                org.springframework.ai.openai.OpenAiChatOptions.builder()
                    .model(model)
                    .temperature(temperature)
                    .build()
            )
            .build()

        flow.handle { message, _ ->
            val payload = message.payload.toString()

            // Replace {{payload}} and any {{header.xxx}} placeholders
            val prompt = promptTemplateStr
                .replace("{{payload}}", payload)
                .replace(Regex("\\{\\{header\\.(\\w+)\\}\\}")) { match ->
                    message.headers[match.groupValues[1]]?.toString() ?: ""
                }

            // Call the LLM
            val response = chatClient.prompt()
                .apply {
                    if (systemPrompt != null) system(systemPrompt)
                }
                .user(prompt)
                .call()
                .content()

            response ?: "No response from LLM"
        }
    }
}
```

## Step 3: Structured Output (JSON Mode)

Sometimes users want the LLM to return structured data:

```kotlin
@Component
class LlmStructuredAdapter(
    private val chatClientBuilder: ChatClient.Builder,
) : NodeAdapter {
    override val type = "llm-structured"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val prompt = node.config["prompt"] as? String ?: "{{payload}}"
        val schema = node.config["outputSchema"] as? String  // JSON Schema

        val chatClient = chatClientBuilder.build()

        flow.handle { message, _ ->
            val payload = message.payload.toString()
            val filledPrompt = prompt.replace("{{payload}}", payload)

            val fullPrompt = if (schema != null) {
                "$filledPrompt\n\nRespond ONLY with valid JSON matching this schema:\n$schema"
            } else {
                filledPrompt
            }

            chatClient.prompt()
                .user(fullPrompt)
                .call()
                .content()
        }
    }
}
```

## Step 4: Frontend Config for LLM Node

Update `configFields.ts`:
```ts
'llm-call': [
  {
    key: 'model',
    label: 'Model',
    type: 'select',
    options: [
      { value: 'gpt-4o', label: 'GPT-4o' },
      { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
      { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet' },
      { value: 'ollama/llama3', label: 'Llama 3 (Local)' },
    ],
  },
  {
    key: 'systemPrompt',
    label: 'System Prompt',
    type: 'textarea',
    placeholder: 'You are a helpful assistant that...',
  },
  {
    key: 'prompt',
    label: 'User Prompt Template',
    type: 'code',
    placeholder: 'Summarize the following text:\n\n{{payload}}',
  },
  {
    key: 'temperature',
    label: 'Temperature',
    type: 'number',
    placeholder: '0.7',
  },
  {
    key: 'maxTokens',
    label: 'Max Tokens',
    type: 'number',
    placeholder: '1000',
  },
],
```

## Step 5: Example Flows with LLM

### Flow 1: Webhook → Summarize → Slack

```json
{
  "name": "Auto-Summarizer",
  "nodes": [
    {
      "id": "n1", "type": "http-inbound", "category": "input",
      "config": { "path": "/summarize", "method": "POST" }
    },
    {
      "id": "n2", "type": "llm-call", "category": "processing",
      "config": {
        "model": "gpt-4o-mini",
        "systemPrompt": "You are a concise summarizer. Respond in 2-3 sentences.",
        "prompt": "Summarize this:\n\n{{payload}}",
        "temperature": 0.3
      }
    },
    {
      "id": "n3", "type": "http-outbound", "category": "output",
      "config": {
        "url": "https://hooks.slack.com/services/xxx",
        "method": "POST"
      }
    }
  ],
  "edges": [
    { "id": "e1", "source": "n1", "target": "n2" },
    { "id": "e2", "source": "n2", "target": "n3" }
  ]
}
```

### Flow 2: File → Classify → Route to DB

```json
{
  "name": "Document Classifier",
  "nodes": [
    {
      "id": "n1", "type": "file-inbound", "category": "input",
      "config": { "directory": "/uploads", "pattern": "*.txt" }
    },
    {
      "id": "n2", "type": "llm-call", "category": "processing",
      "config": {
        "model": "gpt-4o-mini",
        "prompt": "Classify this document into one category: invoice, receipt, contract, other.\nRespond with ONLY the category name.\n\nDocument:\n{{payload}}",
        "temperature": 0
      }
    },
    {
      "id": "n3", "type": "jdbc-outbound", "category": "output",
      "config": {
        "sql": "INSERT INTO documents(content, category) VALUES(:headers.originalPayload, :payload)"
      }
    }
  ],
  "edges": [
    { "id": "e1", "source": "n1", "target": "n2" },
    { "id": "e2", "source": "n2", "target": "n3" }
  ]
}
```

## Step 6: RAG Node (Retrieval-Augmented Generation)

A more advanced LLM node that queries a vector store first:

```kotlin
@Component
class RagAdapter(
    private val chatClientBuilder: ChatClient.Builder,
    private val vectorStore: VectorStore,  // Spring AI VectorStore
) : NodeAdapter {
    override val type = "rag"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val topK = (node.config["topK"] as? Number)?.toInt() ?: 5
        val prompt = node.config["prompt"] as? String
            ?: "Answer based on the context:\n\nContext:\n{{context}}\n\nQuestion: {{payload}}"

        val chatClient = chatClientBuilder.build()

        flow.handle { message, _ ->
            val query = message.payload.toString()

            // 1. Retrieve relevant documents
            val results = vectorStore.similaritySearch(query, topK)
            val context = results.joinToString("\n---\n") { it.content }

            // 2. Build prompt with context
            val filledPrompt = prompt
                .replace("{{payload}}", query)
                .replace("{{context}}", context)

            // 3. Call LLM with context
            chatClient.prompt()
                .user(filledPrompt)
                .call()
                .content()
        }
    }
}
```

## The LLM Node Family

| Node Type | Use Case |
|---|---|
| `llm-call` | Simple prompt → response |
| `llm-structured` | Get JSON output from LLM |
| `rag` | Query vector store + LLM |
| `embedding` | Convert text to vector (for storage) |
| `llm-classify` | Classify into categories |
| `llm-extract` | Extract structured data from text |

Each is just another adapter — same pattern, different logic.

## Key Takeaways

1. **Spring AI** abstracts provider differences — swap OpenAI for Ollama with one config change
2. **Prompt templates** with `{{payload}}` let users reference the message without code
3. **Temperature = 0** for classification/extraction, higher for creative tasks
4. **RAG** is just "retrieve then prompt" — two steps in one node
5. **The LLM node is the differentiator** — n8n has this, but yours runs at scale with retry/circuit-breaker built in

---

[← Chapter 11: Error Handling](chapter-11-error-handling.md) | [Chapter 13: Database Node →](chapter-13-database-node.md)
