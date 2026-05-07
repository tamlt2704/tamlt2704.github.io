# Chapter 3: Testing — Unit Tests Done Right

[← Chapter 2: Dependencies](chapter-02-dependencies.md) | [Chapter 4: Multi-Project Builds →](chapter-04-multi-project.md)

---

## The Task

Derek: "Every module needs tests. JUnit 5. I want to see test results in the terminal. I want to filter tests by tag. And I want the build to fail if any test fails."

---

## Basic Test Setup

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "1.9.22"
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("io.mockk:mockk:1.13.9")
    testImplementation("org.assertj:assertj-core:3.25.1")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()  // REQUIRED for JUnit 5

    testLogging {
        events("passed", "skipped", "failed")
        showExceptions = true
        showCauses = true
        showStackTraces = true
    }
}
```

---

## Test Source Set (Built-in)

When you apply the `kotlin("jvm")` or `java` plugin, you automatically get two source sets:

```
src/
├── main/
│   ├── kotlin/       ← main source set (production code)
│   └── resources/    ← main resources
└── test/
    ├── kotlin/       ← test source set (unit tests)
    └── resources/    ← test resources
```

The `test` source set:
- Can see all classes from `main`
- Has its own dependencies (`testImplementation`, `testRuntimeOnly`)
- Compiles to a separate output directory
- Is executed by the `test` task

---

## Writing Tests

```kotlin
// src/test/kotlin/com/vaultline/TransactionServiceTest.kt
package com.vaultline

import io.mockk.every
import io.mockk.mockk
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.assertThrows

class TransactionServiceTest {

    private val repository = mockk<TransactionRepository>()
    private val service = TransactionService(repository)

    @Test
    fun `processes valid transaction`() {
        val tx = Transaction(amount = 1000, currency = "USD")
        every { repository.save(any()) } returns tx.copy(id = "tx_123")

        val result = service.process(tx)

        assertThat(result.id).isEqualTo("tx_123")
        assertThat(result.status).isEqualTo(Status.COMPLETED)
    }

    @Test
    fun `rejects negative amount`() {
        val tx = Transaction(amount = -100, currency = "USD")

        assertThrows<InvalidTransactionException> {
            service.process(tx)
        }
    }

    @Nested
    inner class `currency validation` {
        @Test
        fun `accepts USD`() {
            assertThat(service.isValidCurrency("USD")).isTrue()
        }

        @Test
        fun `rejects empty currency`() {
            assertThat(service.isValidCurrency("")).isFalse()
        }
    }
}
```

---

## Running Tests

```bash
# Run all tests
./gradlew test

# Run tests for a specific module
./gradlew :core:test

# Run a specific test class
./gradlew test --tests "com.vaultline.TransactionServiceTest"

# Run a specific test method
./gradlew test --tests "com.vaultline.TransactionServiceTest.processes valid transaction"

# Run tests matching a pattern
./gradlew test --tests "*Transaction*"

# Re-run tests even if nothing changed
./gradlew test --rerun

# Run with more output
./gradlew test --info
```

---

## Test Filtering with Tags

JUnit 5 tags let you categorize tests:

```kotlin
import org.junit.jupiter.api.Tag

@Tag("fast")
class UnitTests {
    @Test fun quickTest() { /* ... */ }
}

@Tag("slow")
class DatabaseTests {
    @Test fun queryTest() { /* ... */ }
}

@Tag("integration")
class ApiTests {
    @Test fun endpointTest() { /* ... */ }
}
```

```kotlin
// build.gradle.kts
tasks.test {
    useJUnitPlatform {
        // Only run fast tests by default
        includeTags("fast")
        // Or exclude slow ones
        // excludeTags("slow", "integration")
    }
}

// Create a separate task for slow tests
tasks.register<Test>("slowTest") {
    useJUnitPlatform {
        includeTags("slow")
    }
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
}
```

---

## Test Reports

Gradle generates HTML test reports:

```bash
./gradlew test

# Report at:
# build/reports/tests/test/index.html
```

```kotlin
tasks.test {
    reports {
        html.required.set(true)
        junitXml.required.set(true)  // for CI (Jenkins, GitHub Actions)
    }
}
```

---

## Parallel Test Execution

```kotlin
tasks.test {
    useJUnitPlatform()

    // Run test classes in parallel
    maxParallelForks = Runtime.getRuntime().availableProcessors() / 2

    // Or a fixed number
    // maxParallelForks = 4

    // Fork a new JVM for every N test classes (prevents memory leaks)
    forkEvery = 100
}
```

**Warning:** Parallel tests must be independent. No shared mutable state. No shared database without isolation.

---

## Test Resources

```
src/test/resources/
├── test-config.yaml          ← test-specific configuration
├── fixtures/
│   ├── valid-transaction.json
│   └── invalid-transaction.json
└── logback-test.xml          ← test logging config (quieter)
```

```kotlin
class TransactionParserTest {
    @Test
    fun `parses fixture file`() {
        val json = this::class.java.getResource("/fixtures/valid-transaction.json")!!.readText()
        val tx = parser.parse(json)
        assertThat(tx.amount).isEqualTo(1000)
    }
}
```

---

## JVM Test Configuration

```kotlin
tasks.test {
    useJUnitPlatform()

    // JVM arguments for tests
    jvmArgs("-Xmx1g", "-XX:+UseG1GC")

    // System properties available in tests
    systemProperty("env", "test")
    systemProperty("db.url", "jdbc:h2:mem:test")

    // Environment variables
    environment("API_KEY", "test-key-123")

    // Fail fast — stop on first failure
    failFast = true

    // Timeout per test class
    timeout.set(java.time.Duration.ofMinutes(5))
}
```

---

## The Problem: "Integration Tests Need Different Dependencies"

Priya: "I need Testcontainers for integration tests. But I don't want Testcontainers on the unit test classpath. And I don't want integration tests running with `./gradlew test` — they take 2 minutes."

This is the exact problem that **custom source sets** solve. You can't do it with tags alone — you need separate source directories, separate dependencies, and separate tasks.

That's Chapter 6. But first, we need to split the project into modules (Chapter 4) and share configuration across them (Chapter 5).

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command / Config                │ What It Does
────────────────────────────────┼──────────────────────────────────────
tasks.test { useJUnitPlatform() } │ Enable JUnit 5 (required!)
testImplementation(...)         │ Test-only compile dependency
testRuntimeOnly(...)            │ Test-only runtime dependency
./gradlew test                  │ Run all tests
./gradlew test --tests "*.Foo" │ Run specific tests
./gradlew test --rerun          │ Force re-run (ignore cache)
testLogging { events(...) }     │ Control terminal output
maxParallelForks                │ Parallel test execution
includeTags / excludeTags       │ Filter by JUnit 5 tags
failFast = true                 │ Stop on first failure
build/reports/tests/            │ HTML test reports
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

One module is fine. But Vaultline has `core`, `api`, `batch`, and `sdk`. Each needs its own build file, its own dependencies, and its own tests. But they also share conventions — Kotlin version, JUnit setup, code style.

Time to go multi-project.

---

[← Chapter 2: Dependencies](chapter-02-dependencies.md) | [Chapter 4: Multi-Project Builds →](chapter-04-multi-project.md)
