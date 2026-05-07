# Chapter 8: Test Fixtures — "Shared Test Utilities Across Modules"

[← Chapter 7: Multiple Source Sets](chapter-07-multiple-source-sets.md) | [Chapter 9: Feature Variants →](chapter-09-feature-variants.md)

---

## The Problem

The `core` module has a `TransactionBuilder` helper for tests. The `api` module's integration tests need it too. The `batch` module's tests need it. You copy-pasted it into three modules.

Derek: "Stop. Gradle has `java-test-fixtures` for exactly this. One copy of the helper, shared properly across modules."

---

## What Are Test Fixtures?

Test fixtures are a special source set (`src/testFixtures/`) designed to be consumed by other modules' tests. They're like a "test library" that you publish alongside your main code.

```
core/
├── src/
│   ├── main/kotlin/           ← production code
│   ├── test/kotlin/           ← unit tests (private to this module)
│   └── testFixtures/kotlin/   ← shared test utilities (other modules can use)
```

---

## Enabling Test Fixtures

```kotlin
// core/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    `java-library`
    `java-test-fixtures`  // ← enables the testFixtures source set
}

dependencies {
    // Production
    api("com.fasterxml.jackson.core:jackson-databind:2.16.1")

    // Test fixtures dependencies (available to testFixtures AND consumers)
    testFixturesImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testFixturesImplementation("org.assertj:assertj-core:3.25.1")
    testFixturesImplementation("io.mockk:mockk:1.13.9")
}
```

---

## Writing Test Fixtures

```kotlin
// core/src/testFixtures/kotlin/com/vaultline/testing/TransactionBuilder.kt
package com.vaultline.testing

import com.vaultline.Transaction
import com.vaultline.Status
import java.time.Instant
import java.util.UUID

/**
 * Builder for creating test Transaction objects with sensible defaults.
 * Available to all modules that depend on core's test fixtures.
 */
class TransactionBuilder {
    private var id: String = "tx_${UUID.randomUUID().toString().take(8)}"
    private var amount: Long = 1000
    private var currency: String = "USD"
    private var status: Status = Status.PENDING
    private var createdAt: Instant = Instant.now()
    private var metadata: Map<String, String> = emptyMap()

    fun id(id: String) = apply { this.id = id }
    fun amount(amount: Long) = apply { this.amount = amount }
    fun currency(currency: String) = apply { this.currency = currency }
    fun status(status: Status) = apply { this.status = status }
    fun completed() = apply { this.status = Status.COMPLETED }
    fun failed() = apply { this.status = Status.FAILED }
    fun metadata(vararg pairs: Pair<String, String>) = apply { this.metadata = pairs.toMap() }

    fun build() = Transaction(
        id = id,
        amount = amount,
        currency = currency,
        status = status,
        createdAt = createdAt,
        metadata = metadata,
    )
}

fun aTransaction() = TransactionBuilder()
```

```kotlin
// core/src/testFixtures/kotlin/com/vaultline/testing/Assertions.kt
package com.vaultline.testing

import com.vaultline.Transaction
import com.vaultline.Status
import org.assertj.core.api.AbstractAssert

/**
 * Custom AssertJ assertions for Transaction objects.
 */
class TransactionAssert(actual: Transaction) :
    AbstractAssert<TransactionAssert, Transaction>(actual, TransactionAssert::class.java) {

    fun hasAmount(expected: Long): TransactionAssert {
        if (actual.amount != expected) {
            failWithMessage("Expected amount <%d> but was <%d>", expected, actual.amount)
        }
        return this
    }

    fun isCompleted(): TransactionAssert {
        if (actual.status != Status.COMPLETED) {
            failWithMessage("Expected COMPLETED but was <%s>", actual.status)
        }
        return this
    }

    fun isPending(): TransactionAssert {
        if (actual.status != Status.PENDING) {
            failWithMessage("Expected PENDING but was <%s>", actual.status)
        }
        return this
    }

    companion object {
        fun assertThat(actual: Transaction) = TransactionAssert(actual)
    }
}
```

```kotlin
// core/src/testFixtures/kotlin/com/vaultline/testing/FakeRepository.kt
package com.vaultline.testing

import com.vaultline.Transaction
import com.vaultline.TransactionRepository
import com.vaultline.Status

/**
 * In-memory repository for testing. No database needed.
 */
class FakeTransactionRepository : TransactionRepository {
    private val store = mutableMapOf<String, Transaction>()

    override fun save(tx: Transaction): Transaction {
        val saved = tx.copy(id = tx.id ?: "tx_${store.size + 1}")
        store[saved.id!!] = saved
        return saved
    }

    override fun findById(id: String): Transaction? = store[id]

    override fun findByStatus(status: Status): List<Transaction> =
        store.values.filter { it.status == status }

    fun clear() = store.clear()
    fun count() = store.size
}
```

---

## Consuming Test Fixtures in Other Modules

```kotlin
// api/build.gradle.kts
plugins {
    id("vaultline.integration-test-conventions")
    id("org.springframework.boot") version "3.2.1"
}

dependencies {
    implementation(project(":core"))

    // Use core's test fixtures in unit tests
    testImplementation(testFixtures(project(":core")))

    // Use core's test fixtures in integration tests too
    "integrationTestImplementation"(testFixtures(project(":core")))
}
```

```kotlin
// batch/build.gradle.kts
dependencies {
    implementation(project(":core"))

    // Same — use core's test fixtures
    testImplementation(testFixtures(project(":core")))
}
```

The magic function: **`testFixtures(project(":core"))`** — gives you access to `core`'s `src/testFixtures/` classes.

---

## Using Fixtures in Tests

```kotlin
// api/src/test/kotlin/com/vaultline/api/TransactionControllerTest.kt
package com.vaultline.api

import com.vaultline.testing.aTransaction
import com.vaultline.testing.FakeTransactionRepository
import com.vaultline.testing.TransactionAssert.Companion.assertThat
import org.junit.jupiter.api.Test

class TransactionControllerTest {

    private val repository = FakeTransactionRepository()
    private val service = TransactionService(repository)

    @Test
    fun `processes transaction and returns completed`() {
        val tx = aTransaction()
            .amount(5000)
            .currency("EUR")
            .build()

        val result = service.process(tx)

        assertThat(result).isCompleted().hasAmount(5000)
    }

    @Test
    fun `handles multiple transactions`() {
        val transactions = (1..10).map {
            aTransaction().amount(it * 100L).build()
        }

        transactions.forEach { service.process(it) }

        assert(repository.count() == 10)
    }
}
```

---

## Test Fixtures vs. Other Approaches

```
Approach                        │ Problem
────────────────────────────────┼──────────────────────────────────────
Copy-paste helpers              │ Drift, maintenance nightmare
Put helpers in src/main/        │ Test code in production JAR
Separate "test-utils" module    │ Extra module, extra maintenance
testFixtures (Gradle built-in)  │ ✅ Proper: published alongside, type-safe
```

---

## What testFixtures Gives You Automatically

When you apply `java-test-fixtures`:

1. **Source set:** `src/testFixtures/kotlin/` (and `resources/`)
2. **Configurations:**
   - `testFixturesImplementation` — dependencies for fixtures
   - `testFixturesApi` — dependencies exposed to fixture consumers
   - `testFixturesRuntimeOnly` — runtime-only deps
3. **Visibility:** Fixtures can see `main` classes but NOT `test` classes
4. **Publishing:** If you publish the module, fixtures are published as a separate artifact (`core-test-fixtures.jar`)

---

## Fixtures with Custom Source Sets

Test fixtures work with custom source sets too:

```kotlin
// core/build.gradle.kts
sourceSets {
    create("integrationTest") {
        compileClasspath += sourceSets.main.get().output
        compileClasspath += sourceSets["testFixtures"].output  // ← fixtures visible
        runtimeClasspath += sourceSets.main.get().output
        runtimeClasspath += sourceSets["testFixtures"].output
    }
}

// Or via dependency:
dependencies {
    "integrationTestImplementation"(testFixtures(project(":core")))
}
```

---

## Fixture Dependencies: api vs implementation

```kotlin
dependencies {
    // Only fixtures themselves can use this
    testFixturesImplementation("io.mockk:mockk:1.13.9")

    // Fixture consumers ALSO get this on their classpath
    testFixturesApi("org.assertj:assertj-core:3.25.1")
}
```

Use `testFixturesApi` when your fixture's public API exposes types from the dependency (e.g., custom AssertJ assertions that return AssertJ types).

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
`java-test-fixtures` plugin     │ Enables src/testFixtures/ source set
testFixturesImplementation      │ Dependencies for fixtures (private)
testFixturesApi                 │ Dependencies exposed to consumers
testFixtures(project(":mod"))   │ Consume another module's fixtures
Fixtures see main, not test     │ Can use production classes only
Published as separate artifact  │ module-test-fixtures.jar
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Source sets can do more than separate test types. Gradle's **feature variants** let you create source sets that represent optional features — like a module that works with Redis OR Kafka, with different dependencies for each variant. Consumers choose which variant they want.

---

[← Chapter 7: Multiple Source Sets](chapter-07-multiple-source-sets.md) | [Chapter 9: Feature Variants →](chapter-09-feature-variants.md)
