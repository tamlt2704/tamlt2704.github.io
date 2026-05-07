# Chapter 4: Multi-Project Builds — "Split Into Modules"

[← Chapter 3: Testing](chapter-03-testing.md) | [Chapter 5: Convention Plugins →](chapter-05-conventions.md)

---

## The Task

Derek: "The monolith is getting unwieldy. Split it: `core` for domain logic, `api` for the REST layer, `batch` for the job processor, `sdk` for the client library. Each module should only depend on what it needs."

---

## Project Structure

```
vaultline/
├── settings.gradle.kts         ← declares all modules
├── build.gradle.kts            ← root build file (shared config)
├── gradle.properties           ← shared properties
├── core/
│   ├── build.gradle.kts
│   └── src/main/kotlin/
├── api/
│   ├── build.gradle.kts
│   └── src/main/kotlin/
├── batch/
│   ├── build.gradle.kts
│   └── src/main/kotlin/
└── sdk/
    ├── build.gradle.kts
    └── src/main/kotlin/
```

---

## settings.gradle.kts: Declaring Modules

```kotlin
// settings.gradle.kts
rootProject.name = "vaultline"

include("core")
include("api")
include("batch")
include("sdk")
```

That's it. Each `include` tells Gradle "there's a subdirectory with a `build.gradle.kts` that defines a subproject."

---

## Root build.gradle.kts: Shared Configuration

```kotlin
// build.gradle.kts (root)
plugins {
    kotlin("jvm") version "1.9.22" apply false  // declare but don't apply to root
}

// Configuration shared across ALL subprojects
subprojects {
    group = "com.vaultline"
    version = "0.1.0"

    repositories {
        mavenCentral()
    }
}
```

**`apply false`** — declares the plugin version centrally but doesn't apply it to the root project. Subprojects apply it individually.

---

## Module Build Files

### core/build.gradle.kts

```kotlin
plugins {
    kotlin("jvm")
    `java-library`  // This is a library — uses 'api' configuration
}

dependencies {
    api("com.fasterxml.jackson.core:jackson-databind:2.16.1")
    api("com.fasterxml.jackson.module:jackson-module-kotlin:2.16.1")

    implementation("com.google.guava:guava:33.0.0-jre")
    implementation("org.slf4j:slf4j-api:2.0.11")

    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("org.assertj:assertj-core:3.25.1")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}
```

### api/build.gradle.kts

```kotlin
plugins {
    kotlin("jvm")
    id("org.springframework.boot") version "3.2.1"
    id("io.spring.dependency-management") version "1.1.4"
}

dependencies {
    implementation(project(":core"))  // ← depends on core module

    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")

    runtimeOnly("org.postgresql:postgresql:42.7.1")
    runtimeOnly("ch.qos.logback:logback-classic:1.4.14")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}
```

### batch/build.gradle.kts

```kotlin
plugins {
    kotlin("jvm")
    application
}

dependencies {
    implementation(project(":core"))

    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("com.zaxxer:HikariCP:5.1.0")

    runtimeOnly("org.postgresql:postgresql:42.7.1")

    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

application {
    mainClass.set("com.vaultline.batch.MainKt")
}

tasks.test {
    useJUnitPlatform()
}
```

### sdk/build.gradle.kts

```kotlin
plugins {
    kotlin("jvm")
    `java-library`
    `maven-publish`  // We'll publish this to Maven Central
}

dependencies {
    api(project(":core"))  // SDK consumers need core types

    implementation("io.ktor:ktor-client-core:2.3.7")
    implementation("io.ktor:ktor-client-cio:2.3.7")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
    implementation("io.ktor:ktor-serialization-jackson:2.3.7")

    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("io.ktor:ktor-client-mock:2.3.7")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}
```

---

## Project Dependencies

```kotlin
// Depend on another module in the same build
implementation(project(":core"))

// Expose the module's types to YOUR consumers
api(project(":core"))
```

The dependency graph:

```
         ┌─────┐
    ┌───▶│ core │◀───┐
    │    └─────┘    │
    │       ▲       │
    │       │       │
┌───┴──┐ ┌─┴───┐ ┌─┴──┐
│ api  │ │batch│ │ sdk│
└──────┘ └─────┘ └────┘
```

`core` has no project dependencies. `api`, `batch`, and `sdk` all depend on `core`.

---

## Running Tasks Across Modules

```bash
# Build everything
./gradlew build

# Build a specific module
./gradlew :core:build
./gradlew :api:build

# Run tests for one module
./gradlew :core:test

# Run all tests across all modules
./gradlew test

# Run the API (Spring Boot)
./gradlew :api:bootRun

# Run the batch processor
./gradlew :batch:run

# Clean everything
./gradlew clean

# List tasks for a specific module
./gradlew :core:tasks
```

---

## The Problem: Copy-Paste Configuration

Look at the module build files. Every single one has:

```kotlin
tasks.test {
    useJUnitPlatform()
}
```

And they all need JUnit 5 + the same test logging. And they all share the same Kotlin version. And they all need `mavenCentral()`.

With 4 modules, it's annoying. With 20 modules, it's unmaintainable. When you need to change the JUnit version, you change it in 20 files.

---

## Quick Fix: allprojects / subprojects (Don't Do This)

```kotlin
// root build.gradle.kts
// This WORKS but is considered an anti-pattern in modern Gradle

subprojects {
    apply(plugin = "org.jetbrains.kotlin.jvm")

    repositories {
        mavenCentral()
    }

    dependencies {
        "testImplementation"("org.junit.jupiter:junit-jupiter:5.10.1")
        "testRuntimeOnly"("org.junit.platform:junit-platform-launcher")
    }

    tasks.withType<Test> {
        useJUnitPlatform()
    }
}
```

**Why this is bad:**
- Applies configuration to ALL subprojects, even ones that don't need it
- Breaks project isolation (Gradle can't cache/parallelize as well)
- Type-unsafe (string-based configuration names)
- Hard to override per-module

The correct solution: **convention plugins** (Chapter 5).

---

## Dependency Between Modules: What Gets Shared

```kotlin
// core exposes Jackson via 'api'
// core/build.gradle.kts
api("com.fasterxml.jackson.core:jackson-databind:2.16.1")

// api depends on core via 'implementation'
// api/build.gradle.kts
implementation(project(":core"))

// Result: api CAN use Jackson classes (because core declared it as 'api')
// But api's consumers CANNOT see Jackson (because api used 'implementation' for core)
```

```
sdk depends on core via 'api':
  → sdk's consumers CAN see core's classes AND Jackson

api depends on core via 'implementation':
  → api's consumers CANNOT see core's classes
```

---

## Circular Dependencies: The Error

```kotlin
// core/build.gradle.kts
implementation(project(":api"))  // core depends on api

// api/build.gradle.kts
implementation(project(":core"))  // api depends on core

// ERROR: Circular dependency between ':core' and ':api'
```

If you hit this, your module boundaries are wrong. Extract the shared code into a new module.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
include("module")               │ Declare a subproject in settings.gradle.kts
project(":module")              │ Reference another module as dependency
apply false                     │ Declare plugin version without applying
subprojects { }                 │ Configure all subprojects (anti-pattern)
./gradlew :module:task          │ Run task in specific module
./gradlew build                 │ Build all modules
./gradlew test                  │ Test all modules
Dependency graph must be a DAG  │ No circular dependencies allowed
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The multi-project build works, but every module repeats the same boilerplate. Convention plugins let you define shared configuration once and apply it selectively — "all Kotlin modules get JUnit 5 and this test logging" without copy-paste.

Derek: "I don't want to see `useJUnitPlatform()` in 20 build files. Write it once. Apply it everywhere."

---

[← Chapter 3: Testing](chapter-03-testing.md) | [Chapter 5: Convention Plugins →](chapter-05-conventions.md)
