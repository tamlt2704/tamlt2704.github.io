# Chapter 9: Feature Variants — "Redis OR Kafka, Not Both"

[← Chapter 8: Test Fixtures](chapter-08-test-fixtures.md) | [Chapter 10: Generated Sources →](chapter-10-generated-sources.md)

---

## The Problem

The `core` module has a `MessageBroker` interface. Some deployments use Redis. Others use Kafka. You don't want both on the classpath — they're heavy, they conflict, and consumers should choose.

Priya: "I want `implementation(project(':core')) { capabilities { requireCapability('com.vaultline:core-kafka') } }` — the consumer picks which implementation they get. Like Maven optional dependencies, but type-safe."

---

## What Are Feature Variants?

Feature variants let a single module publish multiple "flavors" — each with its own source set, dependencies, and JAR. Consumers declare which capability they need.

```
core module publishes:
  - core.jar (base — always included)
  - core-redis.jar (Redis implementation + redis dependencies)
  - core-kafka.jar (Kafka implementation + kafka dependencies)

Consumer chooses:
  implementation(project(":core"))  // gets base
  implementation(project(":core")) { capabilities { requireCapability("...core-redis") } }
```

---

## Setting Up Feature Variants

```kotlin
// core/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    `java-library`
}

// Register feature variants
java {
    registerFeature("redis") {
        usingSourceSet(sourceSets.create("redis"))
    }
    registerFeature("kafka") {
        usingSourceSet(sourceSets.create("kafka"))
    }
}

// Wire source sets to see main code
sourceSets {
    named("redis") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }
    named("kafka") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }
}

dependencies {
    // Base dependencies (always present)
    api("com.fasterxml.jackson.core:jackson-databind:2.16.1")

    // Redis feature dependencies
    "redisImplementation"("redis.clients:jedis:5.1.0")

    // Kafka feature dependencies
    "kafkaImplementation"("org.apache.kafka:kafka-clients:3.6.1")
}
```

---

## The Source Structure

```
core/
├── src/
│   ├── main/kotlin/com/vaultline/
│   │   ├── MessageBroker.kt          ← interface
│   │   └── Transaction.kt
│   ├── redis/kotlin/com/vaultline/redis/
│   │   └── RedisMessageBroker.kt     ← Redis implementation
│   └── kafka/kotlin/com/vaultline/kafka/
│       └── KafkaMessageBroker.kt     ← Kafka implementation
```

```kotlin
// src/main/kotlin/com/vaultline/MessageBroker.kt
package com.vaultline

interface MessageBroker {
    fun publish(topic: String, message: String)
    fun subscribe(topic: String, handler: (String) -> Unit)
}
```

```kotlin
// src/redis/kotlin/com/vaultline/redis/RedisMessageBroker.kt
package com.vaultline.redis

import com.vaultline.MessageBroker
import redis.clients.jedis.JedisPool

class RedisMessageBroker(private val pool: JedisPool) : MessageBroker {
    override fun publish(topic: String, message: String) {
        pool.resource.use { jedis ->
            jedis.publish(topic, message)
        }
    }

    override fun subscribe(topic: String, handler: (String) -> Unit) {
        // Redis pub/sub implementation
    }
}
```

```kotlin
// src/kafka/kotlin/com/vaultline/kafka/KafkaMessageBroker.kt
package com.vaultline.kafka

import com.vaultline.MessageBroker
import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.ProducerRecord

class KafkaMessageBroker(private val producer: KafkaProducer<String, String>) : MessageBroker {
    override fun publish(topic: String, message: String) {
        producer.send(ProducerRecord(topic, message))
    }

    override fun subscribe(topic: String, handler: (String) -> Unit) {
        // Kafka consumer implementation
    }
}
```

---

## Consuming Feature Variants

```kotlin
// api/build.gradle.kts — this deployment uses Redis
dependencies {
    implementation(project(":core"))
    implementation(project(":core")) {
        capabilities {
            requireCapability("com.vaultline:core-redis")
        }
    }
}

// batch/build.gradle.kts — this deployment uses Kafka
dependencies {
    implementation(project(":core"))
    implementation(project(":core")) {
        capabilities {
            requireCapability("com.vaultline:core-kafka")
        }
    }
}
```

The `api` module gets Jedis on its classpath. The `batch` module gets Kafka. Neither gets the other's dependencies.

---

## Capability Conflicts

What if someone tries to use both?

```kotlin
// This will FAIL at dependency resolution time:
dependencies {
    implementation(project(":core")) {
        capabilities { requireCapability("com.vaultline:core-redis") }
    }
    implementation(project(":core")) {
        capabilities { requireCapability("com.vaultline:core-kafka") }
    }
}
// Error: Module 'core' has incompatible variants selected
```

You can make them mutually exclusive or allow both — depending on your design.

---

## Simpler Alternative: Optional Dependencies

If feature variants feel heavy, you can use `compileOnly` + runtime selection:

```kotlin
// core/build.gradle.kts
dependencies {
    // Optional — available at compile time, consumer provides at runtime
    compileOnly("redis.clients:jedis:5.1.0")
    compileOnly("org.apache.kafka:kafka-clients:3.6.1")
}

// api/build.gradle.kts
dependencies {
    implementation(project(":core"))
    runtimeOnly("redis.clients:jedis:5.1.0")  // consumer provides Redis
}
```

This is simpler but less type-safe — you won't get a compile error if the dependency is missing, just a runtime `ClassNotFoundException`.

---

## When to Use Feature Variants vs. Separate Modules

```
Feature Variants:                    Separate Modules:
──────────────────────────────       ──────────────────────────────
One module, multiple flavors         core-redis/ and core-kafka/ modules
Shared main code                     Shared via project(":core")
Consumer picks at dependency time    Consumer picks by which module to include
More complex build config            Simpler build, more modules
Good for: optional integrations      Good for: fundamentally different impls
```

For most teams, separate modules (`core-redis`, `core-kafka`) are simpler to understand. Feature variants shine when you're publishing a library and want consumers to pick features without pulling in everything.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
java.registerFeature("name")    │ Create a feature variant
usingSourceSet(sourceSets["x"]) │ Associate source set with feature
"featureImplementation"("dep")  │ Dependencies for that feature only
requireCapability("group:name") │ Consumer selects a feature
Capability conflict             │ Prevents incompatible features together
compileOnly (simpler alt)       │ Optional dep, consumer provides at runtime
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The `api` module uses an OpenAPI spec to generate server stubs. The `sdk` module uses protobuf to generate message classes. Generated code needs its own source set — it shouldn't mix with hand-written code, and it needs to be regenerated when the spec changes.

---

[← Chapter 8: Test Fixtures](chapter-08-test-fixtures.md) | [Chapter 10: Generated Sources →](chapter-10-generated-sources.md)
