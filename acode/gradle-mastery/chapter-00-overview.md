# Gradle Mastery: Build Systems That Don't Fight You

You just joined **Vaultline** — a fintech startup building a payment processing platform in Kotlin. The codebase is a multi-module monorepo: a core library, a REST API, a batch processor, a shared test harness, and an SDK published to Maven Central.

The build takes 4 minutes. Nobody understands why. The `build.gradle` files are 300 lines of copy-pasted magic. Dependencies conflict. The integration tests hit production because someone forgot to wire the test source set. And the CI pipeline breaks every Friday.

**Derek**, the tech lead, drops the bomb:

> "We're splitting the monolith into modules. Each module needs its own dependencies, its own test configurations, and its own publish pipeline. The current build is held together with duct tape. Fix it. Make it fast. Make it correct. And for the love of god, make it so new hires can understand it."

**Priya**, the platform engineer, adds:

> "I need separate source sets for integration tests, performance tests, and contract tests. Each with different dependencies. The integration tests need Testcontainers. The contract tests need Pact. The unit tests need nothing but JUnit. And none of this should leak into production."

You open `build.gradle.kts`. It's Kotlin DSL — at least that's good. But it's a wall of undocumented configuration. Plugins you've never heard of. Dependency declarations that might be wrong. A `buildSrc` folder with custom tasks that nobody remembers writing.

Time to understand Gradle from the ground up — not just "make it compile," but "make it correct, fast, and maintainable."

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Build Engineer / Backend Dev | "It's just a build tool... how hard can it be?" |
| **Derek** | Tech Lead | "If the build breaks on Friday, you're fixing it on Saturday." |
| **Priya** | Platform Engineer | "I need source sets. Proper ones. Not hacks." |
| **The Intern** | New hire | "I ran `./gradlew build` and my laptop caught fire." |
| **The Cache** | Gradle's build cache | "I already did this. Why are you asking again?" |
| **The Daemon** | Gradle's background process | "I'm always watching. Always ready. Don't kill me." |

---

## The Stack

| Tool | What It Does |
|---|---|
| **Gradle 8.x** | Build automation, dependency management |
| **Kotlin DSL (.kts)** | Type-safe build scripts |
| **Kotlin / Java** | Application code |
| **JUnit 5** | Unit testing |
| **Testcontainers** | Integration testing with real databases |
| **Spring Boot** | REST API framework (one module) |
| **Shadow / Application plugin** | Fat JARs, distribution |
| **Maven Publish** | Publishing artifacts |
| **GitHub Actions** | CI/CD |

---

## How to Read This

Every chapter follows the same loop:

```
  🏗️  Derek or Priya needs a build feature
   │
   ▼
  🤔 You learn the Gradle concept that enables it
   │
   ▼
  ⌨️  You configure it (with real build scripts)
   │
   ▼
  💥 Something breaks — dependency hell, slow builds, leaking configs
   │
   ▼
  🧠 You understand WHY and fix it properly
   │
   ▼
  🏗️  Next feature
```

No concept shows up before you need it. You won't learn source sets until Priya needs integration tests with different dependencies. You won't touch the build cache until the build is too slow. You won't learn version catalogs until dependency versions drift across modules.

---

## The Roadmap

### Part 1: Foundations — "Make It Build"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Set up the project, make it compile"  │ Project structure, Kotlin DSL, tasks, plugins
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "Add libraries without breaking things"│ Dependencies — api vs implementation vs compileOnly
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Run the tests"                        │ Test task, JUnit 5, test filtering
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Split into modules"                   │ Multi-project builds, project dependencies
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Share config across modules"          │ Convention plugins, buildSrc, precompiled scripts
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Source Sets — "Separate Concerns" (Your Focus)

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Integration tests need Testcontainers"│ Custom source sets, separate dependencies
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Contract tests need Pact"             │ Multiple source sets, classpath isolation
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Shared test fixtures across modules"  │ java-test-fixtures plugin, test libraries
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Feature flags with source sets"       │ Feature variants, capability conflicts
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Generated code (OpenAPI, protobuf)"   │ Generated source sets, task dependencies
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Performance — "Make It Fast"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "The build takes 4 minutes"            │ Build cache, incremental compilation
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "CI is even slower"                    │ Remote cache, parallel execution, configuration cache
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "Which task is slow?"                  │ Build scans, profiling, --scan
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Configuration phase is 20 seconds"    │ Lazy configuration, providers, avoiding eagerness
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Ship It"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Manage 50+ dependency versions"       │ Version catalogs (libs.versions.toml)
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "Publish the SDK to Maven Central"     │ Maven Publish plugin, signing, metadata
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Build a Docker image"                 │ Jib, application plugin, fat JARs
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "Custom tasks and plugins"             │ Task authoring, plugin development
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "CI/CD pipeline"                       │ GitHub Actions, caching, matrix builds
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ "The build is a product"               │ Reproducibility, security, upgrade strategy
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Architecture We're Building

By Chapter 20:

```
vaultline/
├── gradle/
│   ├── wrapper/
│   │   ├── gradle-wrapper.jar
│   │   └── gradle-wrapper.properties
│   └── libs.versions.toml              ← version catalog
├── buildSrc/
│   ├── build.gradle.kts
│   └── src/main/kotlin/
│       ├── vaultline.kotlin-conventions.gradle.kts
│       ├── vaultline.testing-conventions.gradle.kts
│       └── vaultline.publish-conventions.gradle.kts
├── core/                               ← shared domain library
│   ├── build.gradle.kts
│   └── src/
│       ├── main/kotlin/                ← production code
│       ├── test/kotlin/                ← unit tests (JUnit 5)
│       ├── integrationTest/kotlin/     ← integration tests (Testcontainers)
│       ├── contractTest/kotlin/        ← contract tests (Pact)
│       └── testFixtures/kotlin/        ← shared test utilities
├── api/                                ← Spring Boot REST API
│   ├── build.gradle.kts
│   └── src/
│       ├── main/kotlin/
│       ├── test/kotlin/
│       └── integrationTest/kotlin/
├── batch/                              ← batch processor
│   ├── build.gradle.kts
│   └── src/main/kotlin/
├── sdk/                                ← published client SDK
│   ├── build.gradle.kts
│   └── src/main/kotlin/
├── settings.gradle.kts
├── build.gradle.kts                    ← root build file
└── gradlew / gradlew.bat
```

---

## Gradle vs. Maven: Why Gradle?

Derek asks: "Maven works. Why switch?"

```
Maven:                              Gradle:
──────────────────────────────      ──────────────────────────────
XML configuration (verbose)         Kotlin/Groovy DSL (concise, type-safe)
Fixed lifecycle (compile→test→pkg)  Task graph (flexible, composable)
No build cache                      Local + remote build cache
No incremental compilation          Incremental by default
Convention over configuration       Convention + configuration when needed
Plugins are rigid                   Plugins are composable
Multi-module = copy-paste POMs      Convention plugins = DRY
Build time: 4 minutes               Build time: 45 seconds (cached)
```

The tradeoff: Gradle has a steeper learning curve. Maven is "boring but predictable." Gradle is "powerful but you need to understand it." This series makes you understand it.

---

## The Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        Gradle Build Lifecycle                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. INITIALIZATION                                                │
│     settings.gradle.kts → which projects exist?                   │
│     │                                                             │
│     ▼                                                             │
│  2. CONFIGURATION                                                 │
│     build.gradle.kts (all projects) → define tasks, dependencies  │
│     │                                                             │
│     ▼                                                             │
│  3. EXECUTION                                                     │
│     Run only the requested tasks (+ their dependencies)           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│                        Source Set Model                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Source Set = source code + resources + dependencies + output     │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │    main     │  │    test     │  │  integrationTest     │    │
│  │             │  │             │  │                      │    │
│  │ src/main/   │  │ src/test/   │  │ src/integrationTest/ │    │
│  │ kotlin/     │  │ kotlin/     │  │ kotlin/              │    │
│  │             │  │             │  │                      │    │
│  │ Deps:       │  │ Deps:       │  │ Deps:                │    │
│  │ - ktor      │  │ - junit5    │  │ - testcontainers     │    │
│  │ - jackson   │  │ - mockk     │  │ - junit5             │    │
│  │             │  │ - main code │  │ - main code          │    │
│  │             │  │             │  │ - test fixtures       │    │
│  │ Output:     │  │ Output:     │  │ Output:              │    │
│  │ - JAR       │  │ - test run  │  │ - test run           │    │
│  └─────────────┘  └─────────────┘  └──────────────────────┘    │
│                                                                   │
│  Each source set is ISOLATED — its dependencies don't leak.       │
│  integrationTest can see main code but NOT test code (unless      │
│  you explicitly wire it).                                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Java 17+

```bash
java --version   # 17+
```

### Gradle 8.x (via wrapper)

You don't install Gradle globally. The wrapper (`gradlew`) downloads the correct version:

```bash
# Generate a new project with wrapper
gradle init --type kotlin-application --dsl kotlin

# Or if you have an existing project, update the wrapper
./gradlew wrapper --gradle-version 8.10
```

### Verify

```bash
./gradlew --version
# Gradle 8.10
# Kotlin DSL

./gradlew tasks
# Lists all available tasks
```

---

## Key Concepts (Preview)

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ One-Line Explanation
────────────────────────────────┼──────────────────────────────────────
Task                            │ A unit of work (compile, test, jar)
Plugin                          │ Adds tasks + conventions to a project
Source Set                      │ A group of source files + their dependencies
Configuration                   │ A named bucket of dependencies (implementation, api, etc.)
Project                         │ A module in a multi-project build
Convention Plugin               │ Shared build logic (DRY across modules)
Build Cache                     │ Reuse outputs from previous builds
Daemon                          │ Long-lived process that speeds up builds
Version Catalog                 │ Central dependency version management
Task Graph                      │ DAG of task dependencies (what runs when)
────────────────────────────────┴──────────────────────────────────────
```

---

[Next: Chapter 1 — Project Structure & First Build →](chapter-01-first-build.md)
