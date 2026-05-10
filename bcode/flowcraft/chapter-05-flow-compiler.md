# Chapter 5: The Flow Compiler

[← Chapter 4: Spring Integration](chapter-04-spring-integration.md) | [Chapter 6: Dynamic Registration →](chapter-06-dynamic-registration.md)

---

## Goal

Build the **Flow Compiler** — the heart of the product. It takes the JSON graph from the UI and compiles it into a runnable Spring Integration `IntegrationFlow`. By the end: you can POST a flow definition and the engine builds the corresponding integration pipeline.

## The Compilation Pipeline

```
JSON Graph (from UI)
       │
       ▼
┌─────────────────┐
│  Parse & Validate│  ← Deserialize, check structure
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Topological Sort│  ← Order nodes from input to output
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Resolve Adapters│  ← Map each node type to its SI component
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build Flow DSL  │  ← Chain components into IntegrationFlow
└────────┬────────┘
         │
         ▼
  IntegrationFlow (ready to register)
```

## Step 1: Data Model (Kotlin)

**src/main/kotlin/com/flowcraft/model/FlowDefinition.kt:**
```kotlin
package com.flowcraft.model

import java.util.UUID

data class FlowDefinition(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val nodes: List<NodeDefinition>,
    val edges: List<EdgeDefinition>,
)

data class NodeDefinition(
    val id: String,
    val type: String,
    val category: NodeCategory,
    val position: Position,
    val config: Map<String, Any> = emptyMap(),
)

data class EdgeDefinition(
    val id: String,
    val source: String,
    val target: String,
)

data class Position(val x: Double, val y: Double)

enum class NodeCategory {
    input, processing, output
}
```

## Step 2: Topological Sort

We need to process nodes in order (inputs first, then processing, then outputs). Since the graph is a DAG, we use topological sort:

**src/main/kotlin/com/flowcraft/compiler/GraphSorter.kt:**
```kotlin
package com.flowcraft.compiler

import com.flowcraft.model.FlowDefinition
import com.flowcraft.model.NodeDefinition

class GraphSorter {

    /**
     * Returns nodes in execution order (topological sort).
     * Throws if the graph has cycles.
     */
    fun sort(flow: FlowDefinition): List<NodeDefinition> {
        val adjacency = mutableMapOf<String, MutableList<String>>()
        val inDegree = mutableMapOf<String, Int>()

        // Initialize
        flow.nodes.forEach { node ->
            adjacency[node.id] = mutableListOf()
            inDegree[node.id] = 0
        }

        // Build adjacency list
        flow.edges.forEach { edge ->
            adjacency[edge.source]?.add(edge.target)
            inDegree[edge.target] = (inDegree[edge.target] ?: 0) + 1
        }

        // Kahn's algorithm
        val queue = ArrayDeque<String>()
        inDegree.filter { it.value == 0 }.keys.forEach { queue.add(it) }

        val sorted = mutableListOf<String>()
        while (queue.isNotEmpty()) {
            val current = queue.removeFirst()
            sorted.add(current)

            adjacency[current]?.forEach { neighbor ->
                inDegree[neighbor] = inDegree[neighbor]!! - 1
                if (inDegree[neighbor] == 0) {
                    queue.add(neighbor)
                }
            }
        }

        if (sorted.size != flow.nodes.size) {
            throw IllegalArgumentException("Flow graph contains a cycle!")
        }

        val nodeMap = flow.nodes.associateBy { it.id }
        return sorted.map { nodeMap[it]!! }
    }
}
```

## Step 3: Node Adapters

Each node type has an adapter that knows how to produce its Spring Integration DSL fragment.

**src/main/kotlin/com/flowcraft/compiler/NodeAdapter.kt:**
```kotlin
package com.flowcraft.compiler

import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition

/**
 * Each node type implements this to contribute its piece of the flow.
 */
interface NodeAdapter {
    /** The node type string this adapter handles */
    val type: String

    /** Apply this node's logic to the flow builder */
    fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition)
}
```

**src/main/kotlin/com/flowcraft/compiler/adapters/TransformAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.expression.spel.standard.SpelExpressionParser
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.transformer.ExpressionEvaluatingTransformer
import org.springframework.stereotype.Component

@Component
class TransformAdapter : NodeAdapter {
    override val type = "transform"

    private val parser = SpelExpressionParser()

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val expression = node.config["expression"] as? String
            ?: throw IllegalArgumentException("Transform node ${node.id} missing 'expression'")

        flow.transform<Any> { message ->
            // Evaluate SpEL expression against the payload
            val context = org.springframework.expression.spel.support.StandardEvaluationContext(message)
            parser.parseExpression(expression).getValue(context)
        }
    }
}
```

**src/main/kotlin/com/flowcraft/compiler/adapters/FilterAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.expression.spel.standard.SpelExpressionParser
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.stereotype.Component

@Component
class FilterAdapter : NodeAdapter {
    override val type = "filter"

    private val parser = SpelExpressionParser()

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val expression = node.config["expression"] as? String
            ?: throw IllegalArgumentException("Filter node ${node.id} missing 'expression'")

        flow.filter<Any> { payload ->
            val context = org.springframework.expression.spel.support.StandardEvaluationContext(payload)
            parser.parseExpression(expression).getValue(context, Boolean::class.java) ?: false
        }
    }
}
```

**src/main/kotlin/com/flowcraft/compiler/adapters/LogAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.handler.LoggingHandler
import org.springframework.stereotype.Component

@Component
class LogAdapter : NodeAdapter {
    override val type = "log"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val level = node.config["level"] as? String ?: "INFO"
        val logLevel = LoggingHandler.Level.valueOf(level)

        flow.log(logLevel)
    }
}
```

**src/main/kotlin/com/flowcraft/compiler/adapters/HttpOutboundAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.http.dsl.Http
import org.springframework.stereotype.Component
import org.springframework.http.HttpMethod

@Component
class HttpOutboundAdapter : NodeAdapter {
    override val type = "http-outbound"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val url = node.config["url"] as? String
            ?: throw IllegalArgumentException("HTTP Outbound node ${node.id} missing 'url'")
        val method = node.config["method"] as? String ?: "POST"

        flow.handle(
            Http.outboundGateway(url)
                .httpMethod(HttpMethod.valueOf(method))
                .expectedResponseType(String::class.java)
        )
    }
}
```

**src/main/kotlin/com/flowcraft/compiler/adapters/JdbcOutboundAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.jdbc.JdbcMessageHandler
import org.springframework.stereotype.Component
import javax.sql.DataSource

@Component
class JdbcOutboundAdapter(private val dataSource: DataSource) : NodeAdapter {
    override val type = "jdbc-outbound"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val sql = node.config["sql"] as? String
            ?: throw IllegalArgumentException("JDBC node ${node.id} missing 'sql'")

        flow.handle(JdbcMessageHandler(dataSource, sql))
    }
}
```

## Step 4: The Flow Compiler

The main compiler that orchestrates everything:

**src/main/kotlin/com/flowcraft/compiler/FlowCompiler.kt:**
```kotlin
package com.flowcraft.compiler

import com.flowcraft.model.FlowDefinition
import com.flowcraft.model.NodeCategory
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlow
import org.springframework.integration.dsl.integrationFlow
import org.springframework.integration.http.dsl.Http
import org.springframework.stereotype.Service
import org.springframework.web.bind.annotation.RequestMethod

@Service
class FlowCompiler(
    adapters: List<NodeAdapter>,  // Spring auto-injects all NodeAdapter beans
    private val graphSorter: GraphSorter = GraphSorter(),
) {
    // Map of type → adapter for quick lookup
    private val adapterMap: Map<String, NodeAdapter> = adapters.associateBy { it.type }

    /**
     * Compile a flow definition into a runnable IntegrationFlow.
     */
    fun compile(definition: FlowDefinition): IntegrationFlow {
        // 1. Sort nodes in execution order
        val sortedNodes = graphSorter.sort(definition)

        // 2. Separate input node (first) from the rest
        val inputNode = sortedNodes.first()
        require(inputNode.category == NodeCategory.input) {
            "First node must be an input node, got: ${inputNode.type}"
        }

        val processingAndOutputNodes = sortedNodes.drop(1)

        // 3. Build the flow starting from the input adapter
        return buildFlow(inputNode, processingAndOutputNodes)
    }

    private fun buildFlow(
        inputNode: NodeDefinition,
        remainingNodes: List<NodeDefinition>
    ): IntegrationFlow {
        // Build the inbound part based on input type
        return when (inputNode.type) {
            "http-inbound" -> buildHttpInboundFlow(inputNode, remainingNodes)
            "timer" -> buildTimerFlow(inputNode, remainingNodes)
            else -> throw IllegalArgumentException("Unknown input type: ${inputNode.type}")
        }
    }

    private fun buildHttpInboundFlow(
        inputNode: NodeDefinition,
        remainingNodes: List<NodeDefinition>
    ): IntegrationFlow {
        val path = inputNode.config["path"] as? String ?: "/webhook"
        val method = inputNode.config["method"] as? String ?: "POST"

        return integrationFlow(
            Http.inboundGateway(path)
                .requestMapping { it.methods(RequestMethod.valueOf(method)) }
                .requestPayloadType(String::class.java)
        ) {
            // Apply each subsequent node
            remainingNodes.forEach { node ->
                applyNode(this, node)
            }
        }
    }

    private fun buildTimerFlow(
        inputNode: NodeDefinition,
        remainingNodes: List<NodeDefinition>
    ): IntegrationFlow {
        val fixedDelay = (inputNode.config["fixedDelay"] as? Number)?.toLong() ?: 5000L

        return integrationFlow(
            { org.springframework.messaging.support.GenericMessage("tick") },
            { poller { it.fixedDelay(fixedDelay) } }
        ) {
            remainingNodes.forEach { node ->
                applyNode(this, node)
            }
        }
    }

    private fun applyNode(
        flow: org.springframework.integration.dsl.IntegrationFlowDefinition<*>,
        node: NodeDefinition
    ) {
        val adapter = adapterMap[node.type]
            ?: throw IllegalArgumentException("No adapter found for node type: ${node.type}")
        adapter.apply(flow, node)
    }
}
```

## Step 5: Test the Compiler

```kotlin
@SpringBootTest
class FlowCompilerTest {

    @Autowired
    lateinit var compiler: FlowCompiler

    @Test
    fun `compiles simple HTTP to Log flow`() {
        val definition = FlowDefinition(
            name = "Test Flow",
            nodes = listOf(
                NodeDefinition(
                    id = "n1",
                    type = "http-inbound",
                    category = NodeCategory.input,
                    position = Position(0.0, 0.0),
                    config = mapOf("path" to "/test", "method" to "POST")
                ),
                NodeDefinition(
                    id = "n2",
                    type = "transform",
                    category = NodeCategory.processing,
                    position = Position(200.0, 0.0),
                    config = mapOf("expression" to "payload.toUpperCase()")
                ),
                NodeDefinition(
                    id = "n3",
                    type = "log",
                    category = NodeCategory.output,
                    position = Position(400.0, 0.0),
                    config = mapOf("level" to "INFO")
                ),
            ),
            edges = listOf(
                EdgeDefinition("e1", "n1", "n2"),
                EdgeDefinition("e2", "n2", "n3"),
            )
        )

        val flow = compiler.compile(definition)
        assertNotNull(flow)
        // Flow is ready to be registered!
    }
}
```

## How It All Connects

```
UI exports JSON:
{
  nodes: [{type: "http-inbound", config: {path: "/hook"}}],
  edges: [...]
}
        │
        ▼ POST /api/flows
        │
        ▼ Deserialize to FlowDefinition
        │
        ▼ GraphSorter.sort() → ordered nodes
        │
        ▼ FlowCompiler.compile()
        │   ├── Identifies input node → Http.inboundGateway("/hook")
        │   ├── For each remaining node:
        │   │   └── adapterMap["transform"].apply(flow, node)
        │   └── Returns IntegrationFlow
        │
        ▼ Register with IntegrationFlowContext (next chapter)
        │
        ▼ Flow is LIVE — /hook now accepts requests
```

## Handling Branching (Fan-Out)

What if a node connects to multiple targets? We use `PublishSubscribeChannel`:

```kotlin
// If node-1 connects to both node-2 AND node-3:
// node-1 → [pubsub channel] → node-2
//                            → node-3

private fun handleFanOut(
    flow: IntegrationFlowDefinition<*>,
    sourceNodeId: String,
    targets: List<NodeDefinition>,
    definition: FlowDefinition
) {
    flow.publishSubscribeChannel { pubSub ->
        targets.forEach { target ->
            pubSub.subscribe { subFlow ->
                applyNode(subFlow, target)
                // Continue with target's children...
            }
        }
    }
}
```

This is a more advanced pattern we'll refine in later chapters.

## Key Takeaways

1. **The compiler is the bridge** between the visual UI and the runtime engine
2. **Adapter pattern** makes it extensible — one class per node type, auto-discovered by Spring
3. **Topological sort** ensures nodes execute in the right order
4. **SpEL expressions** give users power without writing Java (Spring Expression Language)
5. **The flow is data** — JSON in, IntegrationFlow out. No code generation, no compilation step.

## What's Next

Chapter 6: We register compiled flows dynamically at runtime using `IntegrationFlowContext` — the mechanism that lets us deploy/undeploy flows without restarting the application.

---

[← Chapter 4: Spring Integration](chapter-04-spring-integration.md) | [Chapter 6: Dynamic Registration →](chapter-06-dynamic-registration.md)
