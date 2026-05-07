# Chapter 2: Dependencies — api vs implementation vs the Rest

[← Chapter 1: First Build](chapter-01-first-build.md) | [Chapter 3: Testing →](chapter-03-testing.md)

---

## The Problem

You added Jackson to the `core` module. The `api` module depends on `core`. Now the `api` module can see Jackson's classes — even though you never declared Jackson as a dependency of `api`.

Derek: "That's a transitive dependency leak. If you change Jackson's version in `core`, it silently breaks `api`. Use `implementation`, not `api`. Unless you actually WANT it to leak."

---

## The Two Key Configurations

### `implementation` — "I use this, but you don't need to know"

```kotlin
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.16.1")
}
```

- The dependency is available at compile time and runtime for THIS module
- It is **NOT** visible to modules that depend on this one
- This is the default choice for 90% of dependencies

### `api` — "I use this AND expose it in my public API"

```kotlin
plugins {
    `java-library`  // Required to use 'api' configuration
}

dependencies {
    api("com.fasterxml.jackson.core:jackson-databind:2.16.1")
}
```

- The dependency is visible to THIS module AND to any module that depends on this one
- Use when your public classes expose types from the dependency

---

## When to Use Which

```kotlin
// core/build.gradle.kts

// Your public function signature:
// fun parseTransaction(json: String): Transaction
// Jackson is used INTERNALLY to parse — callers never see Jackson types
implementation("com.fasterxml.jackson.core:jackson-databind:2.16.1")

// Your public function signature:
// fun getClient(): OkHttpClient
// The return type IS an OkHttp type — callers need it on their classpath
api("com.squareup.okhttp3:okhttp:4.12.0")
```

**Rule of thumb:** If the dependency's types appear in your public API (function signatures, return types, public fields), use `api`. Otherwise, use `implementation`.

---

## Visual: How Transitivity Works

```
Module: core                    Module: api
┌─────────────────────────┐    ┌─────────────────────────┐
│ dependencies {           │    │ dependencies {           │
│   api(jackson)           │    │   implementation(core)   │
│   implementation(guava)  │    │ }                        │
│ }                        │    │                          │
└─────────────────────────┘    └─────────────────────────┘

What 'api' module can see at compile time:
  ✅ core's classes
  ✅ jackson (because core declared it as 'api')
  ❌ guava (because core declared it as 'implementation')

What 'api' module gets at RUNTIME:
  ✅ core's classes
  ✅ jackson
  ✅ guava (it's on the runtime classpath — just not visible at compile time)
```

---

## All Dependency Configurations

```
────────────────────────────────┬──────────────────────────────────────
Configuration                   │ When to Use
────────────────────────────────┼──────────────────────────────────────
implementation                  │ Default. Internal dependency.
api                             │ Exposed in public API (needs java-library plugin)
compileOnly                     │ Needed at compile time, NOT at runtime
                                │ (e.g., annotations, Lombok, servlet-api)
runtimeOnly                     │ Needed at runtime, NOT at compile time
                                │ (e.g., JDBC drivers, SLF4J backends)
testImplementation              │ Test-only dependency
testRuntimeOnly                 │ Test runtime only (e.g., JUnit launcher)
annotationProcessor             │ Annotation processors (Dagger, MapStruct)
────────────────────────────────┴──────────────────────────────────────
```

---

## Real Examples

```kotlin
dependencies {
    // I use Ktor internally to make HTTP calls
    implementation("io.ktor:ktor-client-core:2.3.7")
    implementation("io.ktor:ktor-client-cio:2.3.7")

    // My public API returns Jackson's ObjectNode
    api("com.fasterxml.jackson.core:jackson-databind:2.16.1")

    // I use Lombok annotations but they're erased at runtime
    compileOnly("org.projectlombok:lombok:1.18.30")
    annotationProcessor("org.projectlombok:lombok:1.18.30")

    // SLF4J API at compile time, Logback implementation at runtime
    implementation("org.slf4j:slf4j-api:2.0.11")
    runtimeOnly("ch.qos.logback:logback-classic:1.4.14")

    // PostgreSQL driver — only needed when the app runs
    runtimeOnly("org.postgresql:postgresql:42.7.1")

    // Test dependencies
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("io.mockk:mockk:1.13.9")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}
```

---

## Dependency Conflicts: Version Resolution

What happens when two dependencies need different versions of the same library?

```kotlin
// Module A depends on guava:31.0
// Module B depends on guava:33.0
// Your project depends on both A and B
// Which version of guava do you get?
```

**Gradle's default: highest version wins.** This is usually correct but can break things.

```kotlin
// Force a specific version
dependencies {
    implementation("com.google.guava:guava:33.0.0-jre") {
        version { strictly("33.0.0-jre") }  // MUST be this version
    }
}

// Exclude a transitive dependency
dependencies {
    implementation("some.library:thing:1.0") {
        exclude(group = "com.google.guava", module = "guava")
    }
}

// See the full dependency tree
// ./gradlew :app:dependencies --configuration runtimeClasspath
```

---

## Dependency Tree: Debugging Conflicts

```bash
# Show all dependencies for a configuration
./gradlew :core:dependencies --configuration runtimeClasspath

# Output:
# runtimeClasspath
# +--- com.fasterxml.jackson.core:jackson-databind:2.16.1
# |    +--- com.fasterxml.jackson.core:jackson-core:2.16.1
# |    \--- com.fasterxml.jackson.core:jackson-annotations:2.16.1
# +--- io.ktor:ktor-client-core:2.3.7
# |    +--- org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3
# |    \--- io.ktor:ktor-utils:2.3.7
# \--- com.google.guava:guava:33.0.0-jre
#      +--- com.google.guava:failureaccess:1.0.2
#      \--- com.google.guava:listenablefuture:9999.0-empty-to-avoid-conflict-with-guava

# Find why a specific dependency is included
./gradlew :core:dependencyInsight --dependency jackson-core --configuration runtimeClasspath
```

---

## BOMs (Bill of Materials): Aligned Versions

When using a framework with many artifacts (Spring, Ktor, Jackson), use a BOM to align versions:

```kotlin
dependencies {
    // Import the BOM — doesn't add dependencies, just constrains versions
    implementation(platform("com.fasterxml.jackson:jackson-bom:2.16.1"))

    // Now you can omit versions — the BOM provides them
    implementation("com.fasterxml.jackson.core:jackson-databind")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("com.fasterxml.jackson.datatype:jackson-datatype-jsr310")

    // Spring Boot BOM
    implementation(platform("org.springframework.boot:spring-boot-dependencies:3.2.1"))
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
}
```

---

## Project Dependencies (Between Modules)

```kotlin
// api/build.gradle.kts
dependencies {
    // Depend on the 'core' module
    implementation(project(":core"))

    // If core exposes types you need in YOUR public API:
    api(project(":core"))
}
```

---

## The Classpath Diagram

```
                    COMPILE classpath        RUNTIME classpath
                    (what you can import)    (what's available when running)
────────────────────────────────────────────────────────────────────────
implementation      ✅                       ✅
api                 ✅ (+ consumers)         ✅ (+ consumers)
compileOnly         ✅                       ❌
runtimeOnly         ❌                       ✅
testImplementation  ✅ (tests only)          ✅ (tests only)
testRuntimeOnly     ❌                       ✅ (tests only)
```

---

## Common Mistakes

### 1. Using `api` everywhere

```kotlin
// BAD — leaks everything to consumers, slows compilation
api("com.google.guava:guava:33.0.0-jre")
api("io.ktor:ktor-client-core:2.3.7")
api("ch.qos.logback:logback-classic:1.4.14")

// GOOD — only expose what's in your public API
implementation("com.google.guava:guava:33.0.0-jre")
implementation("io.ktor:ktor-client-core:2.3.7")
runtimeOnly("ch.qos.logback:logback-classic:1.4.14")
api("com.fasterxml.jackson.core:jackson-databind:2.16.1")  // only this is public
```

### 2. Forgetting `runtimeOnly` for drivers

```kotlin
// BAD — you never import PostgreSQL classes directly
implementation("org.postgresql:postgresql:42.7.1")

// GOOD — it's only needed at runtime (JDBC loads it reflectively)
runtimeOnly("org.postgresql:postgresql:42.7.1")
```

### 3. Not using `compileOnly` for provided dependencies

```kotlin
// BAD — bundles servlet-api into your WAR (conflicts with Tomcat's copy)
implementation("javax.servlet:javax.servlet-api:4.0.1")

// GOOD — Tomcat provides this at runtime
compileOnly("javax.servlet:javax.servlet-api:4.0.1")
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command / Config                │ What It Does
────────────────────────────────┼──────────────────────────────────────
implementation("group:name:ver")│ Internal dependency (default choice)
api("group:name:ver")           │ Exposed to consumers (needs java-library)
compileOnly(...)                │ Compile only, not bundled at runtime
runtimeOnly(...)                │ Runtime only, not visible at compile
testImplementation(...)         │ Test compile + runtime
platform("group:bom:ver")      │ Import a BOM for version alignment
project(":module")              │ Depend on another module
./gradlew dependencies          │ Show dependency tree
./gradlew dependencyInsight     │ Why is this dependency here?
exclude(group, module)          │ Remove a transitive dependency
version { strictly("x.y.z") }  │ Force exact version
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Dependencies are wired. Now you need to run tests. But not just unit tests — Priya wants integration tests with Testcontainers that spin up a real PostgreSQL. Those need different dependencies than unit tests. And they shouldn't run with `./gradlew test` (too slow for local dev).

That's the beginning of source sets — but first, let's get basic testing right.

---

[← Chapter 1: First Build](chapter-01-first-build.md) | [Chapter 3: Testing →](chapter-03-testing.md)
