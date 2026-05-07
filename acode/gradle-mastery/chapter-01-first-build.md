# Chapter 1: Project Structure & First Build

[← Overview](chapter-00-overview.md) | [Chapter 2: Dependencies →](chapter-02-dependencies.md)

---

## The Task

Derek: "Set up the Vaultline project. Kotlin. Gradle Kotlin DSL. Make it compile. Make it run. I want to see 'Hello, Vaultline' in my terminal in 10 minutes."

---

## Generating a Project

```bash
mkdir vaultline && cd vaultline
gradle init --type kotlin-application --dsl kotlin --project-name vaultline
```

This creates:

```
vaultline/
├── app/
│   ├── build.gradle.kts        ← build script for the app module
│   └── src/
│       ├── main/kotlin/
│       │   └── org/example/App.kt
│       └── test/kotlin/
│           └── org/example/AppTest.kt
├── gradle/
│   ├── wrapper/
│   │   ├── gradle-wrapper.jar
│   │   └── gradle-wrapper.properties
│   └── libs.versions.toml      ← version catalog
├── settings.gradle.kts          ← project structure definition
├── gradlew                      ← Unix wrapper script
├── gradlew.bat                  ← Windows wrapper script
└── .gitignore
```

---

## settings.gradle.kts: What Exists

This file defines the project structure — which modules (subprojects) are part of the build:

```kotlin
// settings.gradle.kts
rootProject.name = "vaultline"

include("app")
```

That's it for now. Later, when we add modules:

```kotlin
rootProject.name = "vaultline"

include("core")
include("api")
include("batch")
include("sdk")
```

---

## build.gradle.kts: What to Build

```kotlin
// app/build.gradle.kts
plugins {
    kotlin("jvm") version "1.9.22"   // Kotlin compiler
    application                       // Adds 'run' task
}

repositories {
    mavenCentral()                    // Where to find dependencies
}

dependencies {
    // Production dependencies
    implementation("com.google.guava:guava:33.0.0-jre")

    // Test dependencies
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

application {
    mainClass.set("com.vaultline.AppKt")  // Entry point
}

tasks.test {
    useJUnitPlatform()  // Use JUnit 5
}
```

---

## The Build Lifecycle (In Practice)

```bash
./gradlew build
```

What actually happens:

```
1. INITIALIZATION
   → Reads settings.gradle.kts
   → Discovers: "there's one project called 'app'"

2. CONFIGURATION
   → Reads app/build.gradle.kts
   → Registers plugins, tasks, dependencies
   → Builds the task graph (DAG)

3. EXECUTION
   → Runs tasks in dependency order:
      :app:compileKotlin
      :app:compileJava (empty, but runs)
      :app:processResources
      :app:classes
      :app:jar
      :app:startScripts
      :app:distTar
      :app:distZip
      :app:assemble
      :app:compileTestKotlin
      :app:testClasses
      :app:test
      :app:check
      :app:build ✓
```

---

## Tasks: Units of Work

Everything Gradle does is a **task**. Tasks have inputs, outputs, and dependencies on other tasks.

```bash
# List all tasks
./gradlew tasks

# Run a specific task
./gradlew :app:compileKotlin

# Run the app
./gradlew :app:run

# Run tests
./gradlew :app:test

# Clean build outputs
./gradlew clean

# Build without tests
./gradlew build -x test
```

### Task Dependencies (The Graph)

```
build
  └── check
  │     └── test
  │           └── testClasses
  │           │     └── compileTestKotlin
  │           │           └── classes
  │           │                 └── compileKotlin
  │           └── classes
  └── assemble
        └── jar
              └── classes
                    └── compileKotlin
```

When you run `build`, Gradle walks the graph and executes tasks in the correct order.

---

## Plugins: Adding Capabilities

Plugins add tasks, configurations, and conventions:

```kotlin
plugins {
    // The Kotlin JVM plugin — adds compileKotlin, compileTestKotlin, etc.
    kotlin("jvm") version "1.9.22"

    // The application plugin — adds 'run', 'installDist', 'distZip'
    application

    // The java-library plugin — adds 'api' configuration (for libraries)
    `java-library`
}
```

**Core plugins** (no version needed): `java`, `application`, `java-library`, `maven-publish`
**Community plugins** (need version): `kotlin("jvm")`, `org.springframework.boot`, `com.github.johnrengelman.shadow`

---

## Kotlin DSL vs. Groovy DSL

```kotlin
// Kotlin DSL (build.gradle.kts) — type-safe, IDE autocomplete
plugins {
    kotlin("jvm") version "1.9.22"
}

dependencies {
    implementation("com.google.guava:guava:33.0.0-jre")
}

tasks.test {
    useJUnitPlatform()
}
```

```groovy
// Groovy DSL (build.gradle) — dynamic, less IDE support
plugins {
    id 'org.jetbrains.kotlin.jvm' version '1.9.22'
}

dependencies {
    implementation 'com.google.guava:guava:33.0.0-jre'
}

test {
    useJUnitPlatform()
}
```

**Use Kotlin DSL.** It catches errors at configuration time, has full IDE support, and is the modern standard.

---

## The Gradle Wrapper

Never install Gradle globally. The wrapper ensures everyone uses the same version:

```bash
# These are committed to git:
gradle/wrapper/gradle-wrapper.jar         # tiny bootstrap JAR
gradle/wrapper/gradle-wrapper.properties  # specifies Gradle version
gradlew                                   # Unix script
gradlew.bat                               # Windows script
```

```properties
# gradle/wrapper/gradle-wrapper.properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.10-bin.zip
```

```bash
# Update Gradle version
./gradlew wrapper --gradle-version 8.10

# Always use ./gradlew, never bare 'gradle'
./gradlew build
```

---

## The Daemon

Gradle runs a background process (daemon) that stays alive between builds. First build is slow (JVM startup). Subsequent builds are fast.

```bash
# Check daemon status
./gradlew --status

# Stop the daemon
./gradlew --stop

# Run without daemon (CI sometimes does this)
./gradlew build --no-daemon
```

---

## Project Properties and System Properties

```bash
# Pass properties from command line
./gradlew build -Penv=production
./gradlew build -Dorg.gradle.parallel=true

# In build.gradle.kts
val env: String by project  // reads -Penv=production
```

```properties
# gradle.properties (committed — shared settings)
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.jvmargs=-Xmx2g -XX:+UseParallelGC
kotlin.code.style=official
```

---

## Your First Real Build Script

```kotlin
// app/build.gradle.kts
plugins {
    kotlin("jvm") version "1.9.22"
    application
}

group = "com.vaultline"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("io.ktor:ktor-client-core:2.3.7")
    implementation("io.ktor:ktor-client-cio:2.3.7")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.16.1")
    implementation("ch.qos.logback:logback-classic:1.4.14")

    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("io.mockk:mockk:1.13.9")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

kotlin {
    jvmToolchain(17)  // Use Java 17
}

application {
    mainClass.set("com.vaultline.MainKt")
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events("passed", "skipped", "failed")
    }
}
```

```kotlin
// app/src/main/kotlin/com/vaultline/Main.kt
package com.vaultline

fun main() {
    println("Vaultline Payment Platform v0.1.0")
    println("Ready to process transactions.")
}
```

```bash
./gradlew :app:run
# > Task :app:run
# Vaultline Payment Platform v0.1.0
# Ready to process transactions.
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
settings.gradle.kts             │ Defines which projects exist
build.gradle.kts                │ Configures one project (tasks, deps)
plugins { }                     │ Add capabilities (kotlin, application)
repositories { mavenCentral() } │ Where to download dependencies
dependencies { }                │ What libraries you need
tasks.test { }                  │ Configure the test task
./gradlew build                 │ Compile + test + package
./gradlew run                   │ Run the application
./gradlew tasks                 │ List available tasks
./gradlew build -x test         │ Build without tests
gradle.properties               │ Shared build settings
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The project compiles. But you just added 4 dependencies by guessing. What's the difference between `implementation` and `api`? What about `compileOnly`? And why did adding Guava to the `core` module suddenly break the `api` module?

That's dependency configurations — the most misunderstood part of Gradle.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Dependencies →](chapter-02-dependencies.md)
