# Chapter 7: Multiple Source Sets — "Contract Tests, Perf Tests, and More"

[← Chapter 6: Source Sets](chapter-06-source-sets.md) | [Chapter 8: Test Fixtures →](chapter-08-test-fixtures.md)

---

## The Task

Priya: "I need three test layers:
1. **Unit tests** (`src/test/`) — fast, mocked, run on every commit
2. **Integration tests** (`src/integrationTest/`) — Testcontainers, run on PR
3. **Contract tests** (`src/contractTest/`) — Pact, verify API contracts, run nightly

Each has different dependencies. Each has its own Gradle task. None should interfere with the others."

---

## Adding a contractTest Source Set

Same pattern as Chapter 6, but with Pact dependencies:

```kotlin
// api/build.gradle.kts
plugins {
    id("vaultline.integration-test-conventions")  // gives us integrationTest
    id("org.springframework.boot") version "3.2.1"
    id("io.spring.dependency-management") version "1.1.4"
}

// === Contract Test Source Set ===
sourceSets {
    create("contractTest") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }
}

val contractTestImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
}
val contractTestRuntimeOnly by configurations.getting {
    extendsFrom(configurations.runtimeOnly.get())
}

dependencies {
    // Production
    implementation(project(":core"))
    implementation("org.springframework.boot:spring-boot-starter-web")

    // Unit tests — mocks, no network
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("io.mockk:mockk:1.13.9")

    // Integration tests — real database
    "integrationTestImplementation"("org.testcontainers:postgresql:1.19.3")
    "integrationTestImplementation"("org.testcontainers:junit-jupiter:1.19.3")
    "integrationTestImplementation"("org.springframework.boot:spring-boot-starter-test")

    // Contract tests — Pact (completely different framework)
    "contractTestImplementation"("au.com.dius.pact.provider:junit5:4.6.5")
    "contractTestImplementation"("au.com.dius.pact.provider:spring:4.6.5")
    "contractTestImplementation"("org.junit.jupiter:junit-jupiter:5.10.1")
    "contractTestImplementation"("org.springframework.boot:spring-boot-starter-test")
    "contractTestRuntimeOnly"("org.junit.platform:junit-platform-launcher")
}

// === Contract Test Task ===
val contractTest by tasks.registering(Test::class) {
    description = "Runs contract tests with Pact."
    group = "verification"

    testClassesDirs = sourceSets["contractTest"].output.classesDirs
    classpath = sourceSets["contractTest"].runtimeClasspath

    useJUnitPlatform()
    shouldRunAfter(tasks.test)

    // Pact broker configuration
    systemProperty("pact.verifier.publishResults", "true")
    systemProperty("pact.provider.version", project.version.toString())

    testLogging {
        events("passed", "skipped", "failed")
    }
}
```

---

## The Directory Structure (Three Test Layers)

```
api/
├── build.gradle.kts
└── src/
    ├── main/kotlin/com/vaultline/api/
    │   ├── TransactionController.kt
    │   └── Application.kt
    ├── test/kotlin/com/vaultline/api/
    │   └── TransactionControllerTest.kt       ← unit (MockMvc, mocked service)
    ├── integrationTest/kotlin/com/vaultline/api/
    │   └── TransactionApiIT.kt                ← integration (real DB, real HTTP)
    └── contractTest/kotlin/com/vaultline/api/
        └── TransactionProviderPactTest.kt     ← contract (Pact verification)
```

---

## Running Each Layer

```bash
# Unit tests only (fast — every commit)
./gradlew :api:test

# Integration tests (medium — every PR)
./gradlew :api:integrationTest

# Contract tests (slow — nightly)
./gradlew :api:contractTest

# All tests
./gradlew :api:test :api:integrationTest :api:contractTest

# Everything except contract tests
./gradlew :api:test :api:integrationTest
```

---

## Classpath Isolation Visualized

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  test (unit):                                                             │
│    ✅ main classes                                                        │
│    ✅ spring-boot-starter-test, mockk, junit5                             │
│    ❌ testcontainers (not here)                                           │
│    ❌ pact (not here)                                                     │
│                                                                           │
│  integrationTest:                                                         │
│    ✅ main classes                                                        │
│    ✅ spring-boot-starter-test, testcontainers, junit5                    │
│    ❌ mockk (not here — integration tests use real implementations)       │
│    ❌ pact (not here)                                                     │
│                                                                           │
│  contractTest:                                                            │
│    ✅ main classes                                                        │
│    ✅ pact-provider, spring-boot-starter-test, junit5                     │
│    ❌ testcontainers (not here)                                           │
│    ❌ mockk (not here)                                                    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

Each source set is a walled garden. Dependencies don't leak between them.

---

## Sharing Code Between Test Source Sets

What if integration tests and contract tests both need a helper class (e.g., `TestDatabaseSetup`)?

**Option 1: Put it in a shared source set that both extend**

```kotlin
sourceSets {
    create("testSupport") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }

    create("integrationTest") {
        compileClasspath += sourceSets.main.get().output + sourceSets["testSupport"].output
        runtimeClasspath += sourceSets.main.get().output + sourceSets["testSupport"].output
    }

    create("contractTest") {
        compileClasspath += sourceSets.main.get().output + sourceSets["testSupport"].output
        runtimeClasspath += sourceSets.main.get().output + sourceSets["testSupport"].output
    }
}
```

**Option 2: Use test fixtures (Chapter 8)** — the proper Gradle way.

---

## Letting integrationTest See Unit Test Code

Sometimes integration tests need helpers from `src/test/`:

```kotlin
sourceSets {
    create("integrationTest") {
        compileClasspath += sourceSets.main.get().output + sourceSets.test.get().output
        runtimeClasspath += sourceSets.main.get().output + sourceSets.test.get().output
    }
}

// Also need to extend test dependencies
val integrationTestImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
    extendsFrom(configurations.testImplementation.get())  // ← inherit test deps too
}
```

**Be careful:** This couples your integration tests to your unit test code. Usually it's better to extract shared utilities into test fixtures (Chapter 8).

---

## Performance Test Source Set (JMH)

```kotlin
sourceSets {
    create("jmh") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }
}

val jmhImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
}

dependencies {
    "jmhImplementation"("org.openjdk.jmh:jmh-core:1.37")
    "jmhImplementation"("org.openjdk.jmh:jmh-generator-annprocess:1.37")
    "jmhAnnotationProcessor"("org.openjdk.jmh:jmh-generator-annprocess:1.37")
}

val jmhRun by tasks.registering(JavaExec::class) {
    description = "Runs JMH benchmarks."
    group = "benchmark"
    mainClass.set("org.openjdk.jmh.Main")
    classpath = sourceSets["jmh"].runtimeClasspath

    // JMH options
    args("-f", "1", "-wi", "3", "-i", "5")
}
```

```kotlin
// src/jmh/kotlin/com/vaultline/TransactionBenchmark.kt
package com.vaultline

import org.openjdk.jmh.annotations.*
import java.util.concurrent.TimeUnit

@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@State(Scope.Benchmark)
open class TransactionBenchmark {

    private lateinit var service: TransactionService

    @Setup
    fun setup() {
        service = TransactionService(InMemoryRepository())
    }

    @Benchmark
    fun processTransaction(): Transaction {
        return service.process(Transaction(amount = 1000, currency = "USD"))
    }
}
```

---

## CI Configuration: Different Layers at Different Times

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin' }
      - run: ./gradlew test

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests  # only run if unit tests pass
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin' }
      - run: ./gradlew integrationTest

  contract-tests:
    runs-on: ubuntu-latest
    # Only on main branch (nightly) or manual trigger
    if: github.ref == 'refs/heads/main'
    needs: integration-tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin' }
      - run: ./gradlew contractTest
```

---

## The Full Picture: Source Set Dependency Graph

```
                    ┌──────────────────┐
                    │   main source    │
                    │   (production)   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┬──────────────┐
              │              │              │              │
              ▼              ▼              ▼              ▼
     ┌────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────┐
     │    test    │  │integrationTest│  │contractTest│  │ jmh  │
     │  (unit)   │  │  (real DB)    │  │  (Pact)   │  │(perf)│
     └────────────┘  └──────────────┘  └──────────┘  └──────┘
     
     Dependencies:   Dependencies:      Dependencies:   Dependencies:
     - junit5        - junit5           - junit5        - jmh-core
     - mockk         - testcontainers   - pact          - jmh-annprocess
     - assertj       - assertj          - spring-test
     - spring-test   - spring-test
                     - postgresql
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
sourceSets.create("name")       │ New source set → src/name/kotlin/
configurations.getting { }      │ Access auto-created config for source set
extendsFrom(implementation)     │ Inherit production deps
extendsFrom(testImplementation) │ Also inherit test deps (use carefully)
+ sourceSets["x"].output        │ Source set can see another's classes
tasks.registering(Test::class)  │ New test task for the source set
tasks.registering(JavaExec::class) │ New run task (for benchmarks)
shouldRunAfter(tasks.test)      │ Ordering hint
./gradlew integrationTest       │ Run specific test layer
./gradlew contractTest          │ Run specific test layer
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Multiple modules each have integration tests. They all need the same test utilities — database setup helpers, fixture builders, assertion extensions. Copy-pasting these across modules is wrong.

Gradle has a first-class solution: **test fixtures**. A special source set designed to be shared across modules.

---

[← Chapter 6: Source Sets](chapter-06-source-sets.md) | [Chapter 8: Test Fixtures →](chapter-08-test-fixtures.md)
