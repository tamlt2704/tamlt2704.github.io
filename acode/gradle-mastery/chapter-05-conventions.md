# Chapter 5: Convention Plugins — "Write It Once"

[← Chapter 4: Multi-Project](chapter-04-multi-project.md) | [Chapter 6: Source Sets →](chapter-06-source-sets.md)

---

## The Problem

Every module has the same boilerplate:
- Kotlin JVM plugin
- `mavenCentral()` repository
- JUnit 5 dependencies
- `useJUnitPlatform()`
- Test logging configuration
- Java toolchain (17)

With 4 modules, it's annoying. With 20, it's a maintenance nightmare. Change the JUnit version? Edit 20 files.

Derek: "Convention plugins. Define the shared stuff once in `buildSrc`. Apply it with one line per module."

---

## What Is buildSrc?

`buildSrc` is a special directory that Gradle compiles BEFORE your build scripts. Code in `buildSrc` is available to all build scripts in the project. It's where you put convention plugins.

```
vaultline/
├── buildSrc/
│   ├── build.gradle.kts          ← buildSrc's own build file
│   └── src/main/kotlin/
│       ├── vaultline.kotlin-conventions.gradle.kts
│       └── vaultline.testing-conventions.gradle.kts
├── core/
│   └── build.gradle.kts          ← applies convention plugins
├── api/
│   └── build.gradle.kts
└── settings.gradle.kts
```

---

## buildSrc/build.gradle.kts

```kotlin
// buildSrc/build.gradle.kts
plugins {
    `kotlin-dsl`  // Enables writing convention plugins in Kotlin
}

repositories {
    gradlePluginPortal()  // Where Gradle plugins live
    mavenCentral()
}

dependencies {
    // Make these plugins available in convention plugins
    implementation("org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.22")
}
```

---

## Convention Plugin: Kotlin Conventions

```kotlin
// buildSrc/src/main/kotlin/vaultline.kotlin-conventions.gradle.kts

plugins {
    kotlin("jvm")
}

group = "com.vaultline"

repositories {
    mavenCentral()
}

kotlin {
    jvmToolchain(17)
}

// Kotlin compiler options
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    compilerOptions {
        freeCompilerArgs.add("-Xjsr305=strict")  // strict null-safety for Java interop
        allWarningsAsErrors.set(false)
    }
}
```

---

## Convention Plugin: Testing Conventions

```kotlin
// buildSrc/src/main/kotlin/vaultline.testing-conventions.gradle.kts

plugins {
    id("vaultline.kotlin-conventions")  // builds on top of kotlin conventions
}

dependencies {
    "testImplementation"("org.junit.jupiter:junit-jupiter:5.10.1")
    "testImplementation"("org.assertj:assertj-core:3.25.1")
    "testImplementation"("io.mockk:mockk:1.13.9")
    "testRuntimeOnly"("org.junit.platform:junit-platform-launcher")
}

tasks.withType<Test> {
    useJUnitPlatform()

    testLogging {
        events("passed", "skipped", "failed")
        showExceptions = true
        showCauses = true
        showStackTraces = true
    }

    // Parallel execution
    maxParallelForks = (Runtime.getRuntime().availableProcessors() / 2).coerceAtLeast(1)

    // Fail fast in CI
    if (System.getenv("CI") != null) {
        failFast = true
    }
}
```

---

## Using Convention Plugins

Now each module's build file is minimal:

```kotlin
// core/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    `java-library`
}

dependencies {
    api("com.fasterxml.jackson.core:jackson-databind:2.16.1")
    implementation("com.google.guava:guava:33.0.0-jre")
}
```

```kotlin
// api/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    id("org.springframework.boot") version "3.2.1"
    id("io.spring.dependency-management") version "1.1.4"
}

dependencies {
    implementation(project(":core"))
    implementation("org.springframework.boot:spring-boot-starter-web")
    runtimeOnly("org.postgresql:postgresql:42.7.1")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

```kotlin
// batch/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    application
}

dependencies {
    implementation(project(":core"))
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
}

application {
    mainClass.set("com.vaultline.batch.MainKt")
}
```

**Before:** 40 lines of boilerplate per module.
**After:** 10-15 lines of module-specific configuration.

---

## Convention Plugin Composition

Convention plugins can build on each other:

```
vaultline.kotlin-conventions
    └── vaultline.testing-conventions (includes kotlin-conventions)
        └── vaultline.library-conventions (includes testing + java-library + publish)
        └── vaultline.application-conventions (includes testing + application plugin)
```

```kotlin
// buildSrc/src/main/kotlin/vaultline.library-conventions.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    `java-library`
    `maven-publish`
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
        }
    }
}
```

```kotlin
// buildSrc/src/main/kotlin/vaultline.application-conventions.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    application
}

// Common application settings
tasks.withType<JavaExec> {
    jvmArgs("-Xmx512m")
}
```

Now modules are even simpler:

```kotlin
// sdk/build.gradle.kts
plugins {
    id("vaultline.library-conventions")
}

dependencies {
    api(project(":core"))
    implementation("io.ktor:ktor-client-core:2.3.7")
}
```

---

## Why Not `allprojects` / `subprojects`?

```kotlin
// ❌ Anti-pattern: subprojects block in root
subprojects {
    apply(plugin = "org.jetbrains.kotlin.jvm")
    // This applies to ALL subprojects, even ones that might not need Kotlin
    // It's also not type-safe and breaks project isolation
}

// ✅ Convention plugins: each module opts in explicitly
plugins {
    id("vaultline.kotlin-conventions")  // only modules that apply this get Kotlin
}
```

Convention plugins are:
- **Explicit** — each module declares what conventions it follows
- **Composable** — stack them as needed
- **Type-safe** — full IDE support in `.gradle.kts` files
- **Cacheable** — Gradle can optimize better with isolated projects

---

## Alternative: Composite Builds (for Large Teams)

For very large projects, `buildSrc` has a downside: any change to `buildSrc` invalidates the entire build cache. An alternative is a **composite build**:

```
vaultline/
├── build-logic/                    ← separate build (included)
│   ├── conventions/
│   │   ├── build.gradle.kts
│   │   └── src/main/kotlin/
│   │       └── vaultline.kotlin-conventions.gradle.kts
│   └── settings.gradle.kts
├── core/
├── api/
└── settings.gradle.kts
```

```kotlin
// settings.gradle.kts
pluginManagement {
    includeBuild("build-logic")
}

rootProject.name = "vaultline"
include("core", "api", "batch", "sdk")
```

This is the approach recommended by Gradle for production projects. But `buildSrc` is fine for most teams.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
buildSrc/                       │ Pre-compiled build logic (auto-included)
*.gradle.kts in buildSrc        │ Convention plugins (precompiled scripts)
id("vaultline.my-conventions")  │ Apply a convention plugin
`kotlin-dsl` plugin             │ Required in buildSrc/build.gradle.kts
Convention composition          │ Plugins can apply other plugins
Explicit > implicit             │ Modules opt-in to conventions
build-logic/ (composite)        │ Alternative to buildSrc (better caching)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The build is clean, modular, and DRY. Now Priya's request: "I need integration tests with Testcontainers. Separate source directory. Separate dependencies. Separate task. Don't pollute the unit tests."

This is the chapter you've been waiting for: **custom source sets with different dependencies**.

---

[← Chapter 4: Multi-Project](chapter-04-multi-project.md) | [Chapter 6: Source Sets →](chapter-06-source-sets.md)
