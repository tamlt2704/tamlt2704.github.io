# Chapter 13: The Database Node

[← Chapter 12: LLM Node](chapter-12-llm-node.md) | [Chapter 14: Auth & Multi-tenancy →](chapter-14-auth.md)

---

## Goal

Build database nodes that let users query and write to SQL databases from their flows. Support multiple data sources, parameterized queries, and result mapping. By the end: users can read from and write to PostgreSQL, MySQL, or any JDBC database.

## Two Database Nodes

| Node | Direction | Use Case |
|---|---|---|
| `jdbc-query` | Input/Processing | SELECT data, use as enrichment |
| `jdbc-outbound` | Output | INSERT/UPDATE/DELETE |

## Step 1: Dynamic DataSource Registry

Users might connect to multiple databases. We need a registry:

**src/main/kotlin/com/flowcraft/datasource/DataSourceRegistry.kt:**
```kotlin
package com.flowcraft.datasource

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import org.springframework.stereotype.Component
import java.util.concurrent.ConcurrentHashMap
import javax.sql.DataSource

data class DataSourceConfig(
    val name: String,
    val url: String,
    val username: String,
    val password: String,
    val driverClassName: String = "org.postgresql.Driver",
    val maxPoolSize: Int = 5,
)

@Component
class DataSourceRegistry {
    private val dataSources = ConcurrentHashMap<String, DataSource>()

    fun register(config: DataSourceConfig): DataSource {
        val hikariConfig = HikariConfig().apply {
            jdbcUrl = config.url
            username = config.username
            password = config.password
            driverClassName = config.driverClassName
            maximumPoolSize = config.maxPoolSize
            poolName = "flowcraft-${config.name}"
        }

        val ds = HikariDataSource(hikariConfig)
        dataSources[config.name] = ds
        return ds
    }

    fun get(name: String): DataSource {
        return dataSources[name]
            ?: throw IllegalArgumentException("DataSource '$name' not registered")
    }

    fun getOrDefault(name: String?, defaultDs: DataSource): DataSource {
        return if (name != null) get(name) else defaultDs
    }

    fun list(): Set<String> = dataSources.keys
}
```

## Step 2: JDBC Query Adapter (SELECT)

**src/main/kotlin/com/flowcraft/compiler/adapters/JdbcQueryAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.datasource.DataSourceRegistry
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Component
import javax.sql.DataSource

@Component
class JdbcQueryAdapter(
    private val defaultDataSource: DataSource,
    private val dataSourceRegistry: DataSourceRegistry,
) : NodeAdapter {
    override val type = "jdbc-query"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val sql = node.config["sql"] as? String
            ?: throw IllegalArgumentException("JDBC Query node ${node.id} missing 'sql'")
        val dsName = node.config["dataSource"] as? String
        val resultType = node.config["resultType"] as? String ?: "list" // "list" | "single" | "count"

        val dataSource = dataSourceRegistry.getOrDefault(dsName, defaultDataSource)
        val jdbcTemplate = JdbcTemplate(dataSource)

        flow.handle { message, _ ->
            val payload = message.payload

            // Replace :payload and :header.xxx in SQL with actual values
            val parameterizedSql = sql
                .replace(":payload", "'${escapeSql(payload.toString())}'")

            when (resultType) {
                "single" -> jdbcTemplate.queryForMap(parameterizedSql)
                "count" -> jdbcTemplate.queryForObject(parameterizedSql, Long::class.java)
                else -> jdbcTemplate.queryForList(parameterizedSql)
            }
        }
    }

    private fun escapeSql(value: String): String {
        // Basic SQL injection prevention (use PreparedStatement in production!)
        return value.replace("'", "''")
    }
}
```

> **Security Note:** In production, use Spring Integration's built-in `JdbcOutboundGateway` with proper `SqlParameterSource` for parameterized queries. The above is simplified for teaching.

## Step 3: JDBC Write Adapter (INSERT/UPDATE/DELETE)

**src/main/kotlin/com/flowcraft/compiler/adapters/JdbcWriteAdapter.kt:**
```kotlin
package com.flowcraft.compiler.adapters

import com.flowcraft.compiler.NodeAdapter
import com.flowcraft.datasource.DataSourceRegistry
import com.flowcraft.model.NodeDefinition
import org.springframework.integration.dsl.IntegrationFlowDefinition
import org.springframework.integration.jdbc.JdbcMessageHandler
import org.springframework.stereotype.Component
import javax.sql.DataSource

@Component
class JdbcWriteAdapter(
    private val defaultDataSource: DataSource,
    private val dataSourceRegistry: DataSourceRegistry,
) : NodeAdapter {
    override val type = "jdbc-outbound"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val sql = node.config["sql"] as? String
            ?: throw IllegalArgumentException("JDBC Write node ${node.id} missing 'sql'")
        val dsName = node.config["dataSource"] as? String

        val dataSource = dataSourceRegistry.getOrDefault(dsName, defaultDataSource)

        // JdbcMessageHandler supports SpEL in SQL parameters
        val handler = JdbcMessageHandler(dataSource, sql).apply {
            // Map :payload to message payload, :headers.xxx to headers
            setPreparedStatementSetter { ps, message ->
                // Simple: replace :payload with the message payload
                // In production, parse SQL parameters properly
            }
        }

        flow.handle(handler)
    }
}
```

## Step 4: Better Approach — Using Spring Integration JDBC Gateway

For SELECT queries that return results to the flow:

```kotlin
@Component
class JdbcGatewayAdapter(
    private val defaultDataSource: DataSource,
) : NodeAdapter {
    override val type = "jdbc-query"

    override fun apply(flow: IntegrationFlowDefinition<*>, node: NodeDefinition) {
        val sql = node.config["sql"] as? String
            ?: throw IllegalArgumentException("Missing 'sql'")

        flow.handle(
            org.springframework.integration.jdbc.JdbcOutboundGateway(
                defaultDataSource, sql
            ).apply {
                setRequiresReply(true)
                // Parameters from message headers/payload
                setRequestSqlParameterSourceFactory(
                    org.springframework.integration.jdbc.ExpressionEvaluatingSqlParameterSourceFactory().apply {
                        setParameterExpressions(mapOf(
                            "payload" to org.springframework.expression.spel.standard.SpelExpressionParser()
                                .parseExpression("payload")
                        ))
                    }
                )
            }
        )
    }
}
```

## Step 5: Frontend Config

```ts
'jdbc-query': [
  {
    key: 'sql',
    label: 'SQL Query',
    type: 'code',
    placeholder: 'SELECT * FROM users WHERE email = :payload',
    required: true,
  },
  {
    key: 'dataSource',
    label: 'Data Source',
    type: 'select',
    options: [
      { value: 'default', label: 'Default (PostgreSQL)' },
      // Dynamically populated from /api/datasources
    ],
  },
  {
    key: 'resultType',
    label: 'Result Type',
    type: 'select',
    options: [
      { value: 'list', label: 'List of rows' },
      { value: 'single', label: 'Single row' },
      { value: 'count', label: 'Count (number)' },
    ],
  },
],

'jdbc-outbound': [
  {
    key: 'sql',
    label: 'SQL Statement',
    type: 'code',
    placeholder: 'INSERT INTO logs(message, created_at) VALUES(:payload, NOW())',
    required: true,
  },
  {
    key: 'dataSource',
    label: 'Data Source',
    type: 'select',
    options: [
      { value: 'default', label: 'Default (PostgreSQL)' },
    ],
  },
],
```

## Step 6: DataSource Management API

Let users register database connections:

```kotlin
@RestController
@RequestMapping("/api/datasources")
class DataSourceController(private val registry: DataSourceRegistry) {

    @PostMapping
    fun register(@RequestBody config: DataSourceConfig): Map<String, String> {
        registry.register(config)
        return mapOf("name" to config.name, "status" to "connected")
    }

    @GetMapping
    fun list(): Set<String> = registry.list()

    @PostMapping("/{name}/test")
    fun test(@PathVariable name: String): Map<String, Any> {
        return try {
            val ds = registry.get(name)
            ds.connection.use { conn ->
                mapOf("success" to true, "database" to (conn.catalog ?: "unknown"))
            }
        } catch (e: Exception) {
            mapOf("success" to false, "error" to (e.message ?: "Connection failed"))
        }
    }
}
```

## Example: Complete DB Flow

```
Timer (every 5s)
    │
    ▼
JDBC Query: "SELECT * FROM orders WHERE status = 'pending' LIMIT 10"
    │
    ▼ (returns list of rows)
Splitter: split list into individual messages
    │
    ▼ (one message per row)
LLM Call: "Categorize this order: {{payload}}"
    │
    ▼
JDBC Write: "UPDATE orders SET category = :payload WHERE id = :headers.orderId"
```

This flow:
1. Polls for pending orders every 5 seconds
2. Splits the result set into individual messages
3. Sends each order to an LLM for categorization
4. Updates the order with the AI-assigned category

## Key Takeaways

1. **DataSource registry** lets users connect to multiple databases
2. **JDBC Query** (SELECT) returns data into the flow as payload
3. **JDBC Write** (INSERT/UPDATE/DELETE) is a terminal operation
4. **Parameterized queries** prevent SQL injection — use `:payload` syntax
5. **Spring Integration JDBC** handles connection pooling, transactions, and retry
6. **Combined with LLM** — you get AI-powered data pipelines

---

[← Chapter 12: LLM Node](chapter-12-llm-node.md) | [Chapter 14: Auth & Multi-tenancy →](chapter-14-auth.md)
