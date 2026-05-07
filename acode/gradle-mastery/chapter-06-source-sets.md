# Chapter 6: Custom Source Sets — "Integration Tests Need Testcontainers"

[← Chapter 5: Convention Plugins](chapter-05-conventions.md) | [Chapter 7: Multiple Source Sets →](chapter-07-multiple-source-sets.md)

---

## The Problem

Priya: "Unit tests run in 3 seconds. Integration tests spin up PostgreSQL in Docker and take 45 seconds. I don't want them mixed together. I need:
1. A separate `src/integrationTest/kotlin` directory
2. Testcontainers as a dependency ONLY for integration tests
3. A separate `./gradlew integrationTest` task
4. Integration tests should see main code but NOT unit test code
5. `./gradlew test` should NOT run integration tests"

This is exactly what custom source sets are for.

---

## What Is a Source Set?

A source set is a logical grouping of:
- **Source directories** (where the code lives)
- **Dependencies** (what libraries it needs)
- **Compile task** (how to compile it)
- **Output** (where compiled classes go)

The `java` plugin gives you two by default: `main` and `test`. You can create as many as you want.

```
Source Set = {
    source directories:  src/integrationTest/kotlin, src/integrationTest/resources
    dependencies:        testcontainers, junit5, main classes
    compile task:        compileIntegrationTestKotlin
    output:              build/classes/kotlin/integrationTest
}
```

---

## Creating the integrationTest Source Set

```kotlin
// core/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    `java-library`
}

// Create the source set
sourceSets {
    create("integrationTest") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }
}

// Create dependency configurations for the new source set
val integrationTestImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
}
val integrationTestRuntimeOnly by configurations.getting {
    extendsFrom(configurations.runtimeOnly.get())
}
```

This creates:
- `src/integrationTest/kotlin/` — source directory
- `src/integrationTest/resources/` — resource directory
- `integrationTestImplementation` — compile dependencies
- `integrationTestRuntimeOnly` — runtime dependencies
- `compileIntegrationTestKotlin` — compile task

---

## Adding Dependencies to the Source Set

```kotlin
dependencies {
    // Main dependencies (production code)
    implementation("com.fasterxml.jackson.core:jackson-databind:2.16.1")
    implementation("com.zaxxer:HikariCP:5.1.0")
    runtimeOnly("org.postgresql:postgresql:42.7.1")

    // Unit test dependencies (src/test/)
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("io.mockk:mockk:1.13.9")

    // Integration test dependencies (src/integrationTest/)
    // These are ONLY available to integration tests — not unit tests, not production
    "integrationTestImplementation"("org.junit.jupiter:junit-jupiter:5.10.1")
    "integrationTestImplementation"("org.testcontainers:testcontainers:1.19.3")
    "integrationTestImplementation"("org.testcontainers:junit-jupiter:1.19.3")
    "integrationTestImplementation"("org.testcontainers:postgresql:1.19.3")
    "integrationTestImplementation"("org.assertj:assertj-core:3.25.1")
    "integrationTestRuntimeOnly"("org.junit.platform:junit-platform-launcher")
}
```

**Key insight:** `integrationTestImplementation` is a completely separate bucket from `testImplementation`. Testcontainers is NOT on the unit test classpath. MockK is NOT on the integration test classpath (unless you add it).

---

## Creating the integrationTest Task

```kotlin
// Register the test task for integration tests
val integrationTest by tasks.registering(Test::class) {
    description = "Runs integration tests."
    group = "verification"

    testClassesDirs = sourceSets["integrationTest"].output.classesDirs
    classpath = sourceSets["integrationTest"].runtimeClasspath

    useJUnitPlatform()

    // Integration tests are slow — don't run with 'check'
    // Run explicitly: ./gradlew integrationTest
    shouldRunAfter(tasks.test)

    testLogging {
        events("passed", "skipped", "failed")
        showStandardStreams = true  // show container logs
    }
}

// Optionally: make 'check' depend on integrationTest
// (uncomment if you want CI to always run them)
// tasks.check { dependsOn(integrationTest) }
```

---

## The Directory Structure

```
core/
├── build.gradle.kts
└── src/
    ├── main/kotlin/
    │   └── com/vaultline/
    │       ├── Transaction.kt
    │       ├── TransactionRepository.kt
    │       └── TransactionService.kt
    ├── test/kotlin/
    │   └── com/vaultline/
    │       └── TransactionServiceTest.kt        ← unit tests (fast, mocked)
    └── integrationTest/kotlin/
        └── com/vaultline/
            └── TransactionRepositoryIT.kt       ← integration tests (real DB)
```

---

## Writing the Integration Test

```kotlin
// src/integrationTest/kotlin/com/vaultline/TransactionRepositoryIT.kt
package com.vaultline

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.*
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.junit.jupiter.Container
import org.testcontainers.junit.jupiter.Testcontainers
import java.sql.DriverManager

@Testcontainers
class TransactionRepositoryIT {

    companion object {
        @Container
        val postgres = PostgreSQLContainer("postgres:16-alpine").apply {
            withDatabaseName("vaultline_test")
            withUsername("test")
            withPassword("test")
        }
    }

    private lateinit var repository: TransactionRepository

    @BeforeEach
    fun setup() {
        val connection = DriverManager.getConnection(
            postgres.jdbcUrl, postgres.username, postgres.password
        )
        repository = TransactionRepository(connection)
        repository.createTable()
    }

    @Test
    fun `saves and retrieves transaction`() {
        val tx = Transaction(amount = 5000, currency = "USD", status = Status.PENDING)

        val saved = repository.save(tx)
        val found = repository.findById(saved.id!!)

        assertThat(found).isNotNull
        assertThat(found!!.amount).isEqualTo(5000)
        assertThat(found.currency).isEqualTo("USD")
    }

    @Test
    fun `finds transactions by status`() {
        repository.save(Transaction(amount = 1000, currency = "USD", status = Status.COMPLETED))
        repository.save(Transaction(amount = 2000, currency = "USD", status = Status.PENDING))
        repository.save(Transaction(amount = 3000, currency = "EUR", status = Status.COMPLETED))

        val completed = repository.findByStatus(Status.COMPLETED)

        assertThat(completed).hasSize(2)
        assertThat(completed.map { it.amount }).containsExactlyInAnyOrder(1000, 3000)
    }
}
```

---

## Running It

```bash
# Run only unit tests (fast — 3 seconds)
./gradlew test

# Run only integration tests (slow — 45 seconds, needs Docker)
./gradlew integrationTest

# Run both
./gradlew test integrationTest

# Run a specific integration test
./gradlew integrationTest --tests "*TransactionRepositoryIT"

# Build without integration tests (default — they're not in 'check')
./gradlew build
```

---

## The Complete Build File

```kotlin
// core/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    `java-library`
}

// === Source Sets ===
sourceSets {
    create("integrationTest") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }
}

val integrationTestImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
}
val integrationTestRuntimeOnly by configurations.getting {
    extendsFrom(configurations.runtimeOnly.get())
}

// === Dependencies ===
dependencies {
    // Production
    api("com.fasterxml.jackson.core:jackson-databind:2.16.1")
    implementation("com.zaxxer:HikariCP:5.1.0")
    implementation("org.slf4j:slf4j-api:2.0.11")
    runtimeOnly("org.postgresql:postgresql:42.7.1")

    // Unit tests (src/test/) — fast, mocked
    testImplementation("io.mockk:mockk:1.13.9")

    // Integration tests (src/integrationTest/) — slow, real infra
    "integrationTestImplementation"("org.testcontainers:testcontainers:1.19.3")
    "integrationTestImplementation"("org.testcontainers:junit-jupiter:1.19.3")
    "integrationTestImplementation"("org.testcontainers:postgresql:1.19.3")
    "integrationTestImplementation"("org.assertj:assertj-core:3.25.1")
    "integrationTestImplementation"("org.junit.jupiter:junit-jupiter:5.10.1")
    "integrationTestRuntimeOnly"("org.junit.platform:junit-platform-launcher")
    "integrationTestRuntimeOnly"("org.postgresql:postgresql:42.7.1")
}

// === Integration Test Task ===
val integrationTest by tasks.registering(Test::class) {
    description = "Runs integration tests with Testcontainers."
    group = "verification"

    testClassesDirs = sourceSets["integrationTest"].output.classesDirs
    classpath = sourceSets["integrationTest"].runtimeClasspath

    useJUnitPlatform()
    shouldRunAfter(tasks.test)

    testLogging {
        events("passed", "skipped", "failed")
        showStandardStreams = true
    }

    // Integration tests need more memory (Docker containers)
    jvmArgs("-Xmx1g")

    // Timeout — containers can be slow to start
    timeout.set(java.time.Duration.ofMinutes(10))
}
```

---

## How Classpath Isolation Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Classpath Visibility                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  main source set:                                                     │
│    compile: jackson, hikari, slf4j                                    │
│    runtime: + postgresql                                              │
│                                                                       │
│  test source set:                                                     │
│    compile: main classes + junit5 + mockk + assertj                   │
│    runtime: + junit-platform-launcher                                 │
│    CANNOT see: testcontainers (not on this classpath)                 │
│                                                                       │
│  integrationTest source set:                                          │
│    compile: main classes + junit5 + testcontainers + assertj          │
│    runtime: + postgresql + junit-platform-launcher                    │
│    CANNOT see: mockk (not on this classpath)                          │
│    CANNOT see: test classes (unit test code is invisible)             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

This isolation is the whole point:
- Unit tests don't accidentally use Testcontainers
- Integration tests don't accidentally use mocks
- Production code sees neither test framework

---

## extendsFrom: Inheriting Dependencies

```kotlin
val integrationTestImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
}
```

This means `integrationTestImplementation` inherits ALL dependencies from `implementation`. So integration tests automatically get Jackson, HikariCP, etc. — everything production code uses.

Without `extendsFrom`, you'd have to re-declare every production dependency for integration tests.

```
implementation dependencies:
  jackson, hikari, slf4j
       │
       │ extendsFrom
       ▼
integrationTestImplementation:
  jackson, hikari, slf4j (inherited)
  + testcontainers (added specifically)
  + junit5 (added specifically)
```

---

## Making It a Convention Plugin

Since multiple modules need integration tests, extract this into a convention:

```kotlin
// buildSrc/src/main/kotlin/vaultline.integration-test-conventions.gradle.kts

plugins {
    id("vaultline.testing-conventions")
}

sourceSets {
    create("integrationTest") {
        compileClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets.main.get().output
    }
}

val integrationTestImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
}
val integrationTestRuntimeOnly by configurations.getting {
    extendsFrom(configurations.runtimeOnly.get())
}

// Base integration test dependencies (every module gets these)
dependencies {
    "integrationTestImplementation"("org.junit.jupiter:junit-jupiter:5.10.1")
    "integrationTestImplementation"("org.assertj:assertj-core:3.25.1")
    "integrationTestRuntimeOnly"("org.junit.platform:junit-platform-launcher")
}

val integrationTest by tasks.registering(Test::class) {
    description = "Runs integration tests."
    group = "verification"
    testClassesDirs = sourceSets["integrationTest"].output.classesDirs
    classpath = sourceSets["integrationTest"].runtimeClasspath
    useJUnitPlatform()
    shouldRunAfter(tasks.test)
    testLogging {
        events("passed", "skipped", "failed")
    }
}
```

Now modules just apply it and add their specific dependencies:

```kotlin
// core/build.gradle.kts
plugins {
    id("vaultline.integration-test-conventions")
    `java-library`
}

dependencies {
    // Module-specific integration test deps
    "integrationTestImplementation"("org.testcontainers:postgresql:1.19.3")
    "integrationTestImplementation"("org.testcontainers:junit-jupiter:1.19.3")
}
```

```kotlin
// api/build.gradle.kts
plugins {
    id("vaultline.integration-test-conventions")
    id("org.springframework.boot") version "3.2.1"
}

dependencies {
    "integrationTestImplementation"("org.springframework.boot:spring-boot-starter-test")
    "integrationTestImplementation"("org.testcontainers:postgresql:1.19.3")
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
sourceSets.create("name")       │ Create a new source set
compileClasspath += main.output │ Source set can see main classes
configurations.getting { }      │ Access auto-created configurations
extendsFrom(implementation)     │ Inherit production dependencies
"nameImplementation"("dep")     │ Add dependency to custom source set
tasks.registering(Test::class)  │ Create a test task for the source set
testClassesDirs = ...output     │ Point task at the source set's classes
classpath = ...runtimeClasspath │ Point task at the source set's classpath
shouldRunAfter(tasks.test)      │ Order hint (not a hard dependency)
./gradlew integrationTest       │ Run the custom test task
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

One custom source set down. But Priya wants more: contract tests with Pact (different dependencies again), performance tests with JMH, and maybe even a `functionalTest` source set for end-to-end API tests.

Each with its own dependencies. Each isolated. Each with its own task.

---

[← Chapter 5: Convention Plugins](chapter-05-conventions.md) | [Chapter 7: Multiple Source Sets →](chapter-07-multiple-source-sets.md)
