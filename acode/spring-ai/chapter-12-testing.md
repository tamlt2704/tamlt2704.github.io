# Chapter 12: Testing & Observability — Proving It Works

[← Chapter 11: Performance](chapter-11-performance.md)

---

## The Problem

Captain Deadline: "How do I know the chatbot is giving correct answers? How do I know it won't break after a model update? You can't unit test randomness."

He's right — you can't assert `assertEquals("exact string", llmResponse)`. LLMs are non-deterministic. But you CAN test behavior, structure, and constraints.

---

## Strategy 1: Mock the LLM in Unit Tests

Don't call Ollama in unit tests. Mock the ChatClient:

```java
// src/test/java/com/shopzilla/ai/service/ProductDescriptionServiceTest.java
import org.springframework.ai.chat.client.ChatClient;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductDescriptionServiceTest {

    @Mock ChatClient chatClient;
    @Mock ChatClient.CallPromptResponseSpec callResponse;
    @Mock ChatClient.ChatClientRequestSpec promptSpec;

    ProductDescriptionService service;

    @BeforeEach
    void setup() {
        when(chatClient.prompt()).thenReturn(promptSpec);
        when(promptSpec.user(anyString())).thenReturn(promptSpec);
        when(promptSpec.system(anyString())).thenReturn(promptSpec);
        when(promptSpec.call()).thenReturn(callResponse);
        when(callResponse.content()).thenReturn(
            "These wireless headphones deliver premium sound at $79.99."
        );

        service = new ProductDescriptionService(chatClient);
    }

    @Test
    void shouldCallLlmWithProductDetails() {
        service.generateDescription("Headphones", "Electronics", 79.99, "40hr battery");

        verify(promptSpec).user(contains("Headphones"));
        verify(promptSpec).user(contains("79.99"));
    }
}
```

Unit tests verify your code calls the LLM correctly — not that the LLM responds correctly.

---

## Strategy 2: Integration Tests with Real LLM

For testing actual LLM behavior, use a real (but small/fast) model:

```java
@SpringBootTest
@TestPropertySource(properties = {
    "spring.ai.ollama.chat.model=phi3:mini",  // fast model for tests
    "spring.ai.ollama.chat.options.temperature=0.1"  // deterministic
})
class ChatServiceIntegrationTest {

    @Autowired ChatService chatService;

    @Test
    void shouldAnswerReturnPolicyFromRag() {
        String response = chatService.chat("test-1", "What is your return policy?");

        // Don't assert exact text — assert it contains key facts
        assertThat(response).containsIgnoringCase("30 days");
        assertThat(response).doesNotContainIgnoringCase("90 days");
    }

    @Test
    void shouldNotOfferRefundsDirectly() {
        String response = chatService.chat("test-2", "I want a refund");

        assertThat(response).doesNotContain("$");
        assertThat(response).containsAnyOf("support team", "support@shopzilla", "contact");
    }

    @Test
    void shouldReturnStructuredJson() {
        ProductContent content = descriptionService.generateStructured(
                "USB Cable", "Electronics", 9.99, "braided nylon");

        assertThat(content.title()).isNotBlank();
        assertThat(content.description()).isNotBlank();
        assertThat(content.bulletPoints()).hasSize(3);
        assertThat(content.description()).contains("9.99");
    }
}
```

### What to Assert

| Assert | Example |
|---|---|
| Contains key facts | `assertThat(response).contains("30 days")` |
| Doesn't hallucinate | `assertThat(response).doesNotContain("90 days")` |
| Follows constraints | `assertThat(response).doesNotContain("$50 credit")` |
| Structured output shape | `assertThat(result.bulletPoints()).hasSize(3)` |
| Response length | `assertThat(response.length()).isBetween(50, 500)` |
| Doesn't contain PII | `assertThat(response).doesNotContain("@")` |

---

## Strategy 3: Evaluation Sets

Build a test suite of question-answer pairs:

```java
// src/test/resources/eval/support-questions.json
[
  {
    "question": "What is your return policy?",
    "mustContain": ["30 days", "receipt"],
    "mustNotContain": ["90 days", "no questions asked"],
    "category": "policy"
  },
  {
    "question": "Do you ship internationally?",
    "mustContain": ["not currently", "Q2 2025"],
    "mustNotContain": ["yes", "worldwide"],
    "category": "shipping"
  }
]
```

```java
@ParameterizedTest
@MethodSource("loadEvalSet")
void shouldPassEvaluation(EvalCase testCase) {
    String response = chatService.chat("eval-" + testCase.id(), testCase.question());

    for (String required : testCase.mustContain()) {
        assertThat(response.toLowerCase()).contains(required.toLowerCase());
    }
    for (String forbidden : testCase.mustNotContain()) {
        assertThat(response.toLowerCase()).doesNotContain(forbidden.toLowerCase());
    }
}
```

Run this after every model update or prompt change. If a test fails, the model is hallucinating on that topic — fix the RAG docs or prompt.

---

## Observability: Logging & Tracing

### Log Every LLM Call

```java
// src/main/java/com/shopzilla/ai/advisor/LoggingAdvisor.java
public class LoggingAdvisor implements CallAroundAdvisor {

    private static final Logger log = LoggerFactory.getLogger(LoggingAdvisor.class);

    @Override
    public AdvisedResponse aroundCall(AdvisedRequest request, CallAroundAdvisorChain chain) {
        long start = System.currentTimeMillis();
        String userMessage = extractUserMessage(request);

        AdvisedResponse response = chain.nextAroundCall(request);

        long duration = System.currentTimeMillis() - start;
        String content = response.response().getResult().getOutput().getText();

        log.info("LLM call: duration={}ms, input_length={}, output_length={}, model={}",
                duration, userMessage.length(), content.length(),
                response.response().getMetadata().getModel());

        return response;
    }

    @Override
    public String getName() { return "LoggingAdvisor"; }

    @Override
    public int getOrder() { return -1; } // run first
}
```

### Metrics Dashboard

```java
// Key metrics to track
ai.llm.latency (histogram)     — response time distribution
ai.llm.calls (counter)         — total calls per model
ai.llm.errors (counter)        — failures
ai.cache.hits (counter)        — cache effectiveness
ai.rag.retrievals (counter)    — RAG searches
ai.guardrails.blocked (counter) — blocked responses
```

### Conversation Audit Trail

```java
// Store every conversation for review
@Entity
@Table(name = "ai_conversations")
public class ConversationLog {
    @Id @GeneratedValue private Long id;
    private String conversationId;
    private String userMessage;
    private String aiResponse;
    private String model;
    private int tokenCount;
    private long latencyMs;
    private boolean wasBlocked;
    private Instant timestamp;
}
```

Review flagged conversations weekly. Find patterns in blocked responses. Improve prompts based on real usage.

---

## The Testing Pyramid for AI

```
        ╱╲
       ╱  ╲     E2E: Full conversation flows (few, slow)
      ╱────╲
     ╱      ╲   Integration: Real LLM + eval sets (medium)
    ╱────────╲
   ╱          ╲  Unit: Mock LLM, test your logic (many, fast)
  ╱────────────╲
```

- **Unit tests** (fast, many): Mock the LLM. Test your routing, caching, guardrails, input validation.
- **Integration tests** (medium): Real LLM with eval sets. Test RAG retrieval, structured output, function calling.
- **E2E tests** (few, slow): Full conversation flows. Test memory, multi-turn, escalation.

---

## What You Built (The Full Journey)

| Chapter | What You Learned |
|---|---|
| 1 | ChatClient, Ollama setup, first prompt |
| 2 | Prompt templates, system messages, consistency |
| 3 | Structured output, BeanOutputConverter, type-safe responses |
| 4 | Streaming, SSE, real-time token output |
| 5 | Conversation memory, chat history, advisors |
| 6 | RAG, embeddings, vector store, grounded answers |
| 7 | Function calling, tools, real data access |
| 8 | Semantic search, similarity, product discovery |
| 9 | Guardrails, output validation, prompt injection defense |
| 10 | Multi-model routing, task-specific models, fallbacks |
| 11 | Caching, batching, async, rate limiting |
| 12 | Testing, evaluation sets, observability, metrics |

---

## The Demo

Friday afternoon. Captain Deadline gathers the team.

You demo the chatbot. Karen asks about her order — it looks up the real status. She asks about the return policy — it quotes the actual 30-day policy. She tries to get a free refund — it politely redirects to support.

Mrs. Jira generates 50 product descriptions in 3 minutes. They're consistent, on-brand, and ready for the catalog.

Old Greg searches "something for my home office" — semantic search returns ergonomic keyboards and monitor stands, not literal matches for "home" or "office."

Captain Deadline checks the metrics dashboard. 99.7% of responses pass guardrails. Average latency: 3.2 seconds. Cache hit rate: 40%.

"Ship it."

Silent Bob sends 🚀.

---

[← Chapter 11: Performance](chapter-11-performance.md)
