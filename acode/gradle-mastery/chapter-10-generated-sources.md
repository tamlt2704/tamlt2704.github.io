# Chapter 10: Generated Sources — "OpenAPI, Protobuf, and Code Gen"

[← Chapter 9: Feature Variants](chapter-09-feature-variants.md) | [Chapter 11: Build Cache →](chapter-11-build-cache.md)

---

## The Problem

The `api` module has an OpenAPI spec (`openapi.yaml`). A Gradle plugin generates Kotlin server stubs from it. The `sdk` module uses protobuf definitions to generate message classes. Both need:

1. Generated code in a separate directory (not mixed with hand-written code)
2. Proper task dependencies (regenerate when spec changes)
3. IDE recognition (autocomplete works on generated classes)

Priya: "Generated code goes in `build/generated/`. It's in `.gitignore`. The build regenerates it. The IDE indexes it. Nobody edits it by hand."

---

## OpenAPI Code Generation

```kotlin
// api/build.gradle.kts
plugins {
    id("vaultline.testing-conventions")
    id("org.springframework.boot") version "3.2.1"
    id("org.openapi.generator") version "7.2.0"
}

openApiGenerate {
    generatorName.set("kotlin-spring")
    inputSpec.set("$projectDir/src/main/resources/openapi.yaml")
    outputDir.set("${layout.buildDirectory.get()}/generated/openapi")
    apiPackage.set("com.vaultline.api.generated")
    modelPackage.set("com.vaultline.api.generated.model")
    configOptions.set(mapOf(
        "interfaceOnly" to "true",
        "useSpringBoot3" to "true",
        "useTags" to "true",
    ))
}

// Add generated sources to the main source set
sourceSets {
    main {
        kotlin {
            srcDir("${layout.buildDirectory.get()}/generated/openapi/src/main/kotlin")
        }
    }
}

// Ensure generation runs before compilation
tasks.compileKotlin {
    dependsOn(tasks.openApiGenerate)
}
```

---

## The Generated Source Directory

```
api/
├── build/
│   └── generated/
│       └── openapi/
│           └── src/main/kotlin/
│               └── com/vaultline/api/generated/
│                   ├── TransactionsApi.kt        ← generated interface
│                   └── model/
│                       ├── TransactionRequest.kt ← generated model
│                       └── TransactionResponse.kt
├── src/
│   ├── main/
│   │   ├── kotlin/com/vaultline/api/
│   │   │   └── TransactionsController.kt        ← hand-written (implements generated interface)
│   │   └── resources/
│   │       └── openapi.yaml                     ← the spec (source of truth)
│   └── test/kotlin/
└── build.gradle.kts
```

**Rule:** Generated code lives in `build/`. It's never committed to git. It's regenerated on every build.

---

## Protobuf Code Generation

```kotlin
// sdk/build.gradle.kts
plugins {
    id("vaultline.library-conventions")
    id("com.google.protobuf") version "0.9.4"
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.25.2"
    }
    generateProtoTasks {
        all().forEach { task ->
            task.builtins {
                create("kotlin")
            }
        }
    }
}

dependencies {
    implementation("com.google.protobuf:protobuf-kotlin:3.25.2")
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")
}

// Protobuf plugin automatically adds generated sources to the source set
// Output goes to: build/generated/source/proto/main/kotlin/
```

```protobuf
// sdk/src/main/proto/transaction.proto
syntax = "proto3";
package com.vaultline.sdk;

message TransactionMessage {
  string id = 1;
  int64 amount = 2;
  string currency = 3;
  Status status = 4;

  enum Status {
    PENDING = 0;
    COMPLETED = 1;
    FAILED = 2;
  }
}
```

---

## Custom Code Generation Task

Sometimes you write your own code generator:

```kotlin
// Generate Kotlin code from a custom DSL/schema

val generateModels by tasks.registering {
    description = "Generates Kotlin models from schema."
    group = "generation"

    val schemaFile = file("src/main/resources/schema.json")
    val outputDir = layout.buildDirectory.dir("generated/models/kotlin")

    inputs.file(schemaFile)       // ← task re-runs when schema changes
    outputs.dir(outputDir)        // ← task is UP-TO-DATE if output exists

    doLast {
        val schema = schemaFile.readText()
        val output = outputDir.get().asFile
        output.mkdirs()

        // Your generation logic here
        val generated = generateKotlinFromSchema(schema)
        File(output, "GeneratedModels.kt").writeText(generated)
    }
}

// Add to source set
sourceSets {
    main {
        kotlin {
            srcDir(layout.buildDirectory.dir("generated/models/kotlin"))
        }
    }
}

// Wire task dependency
tasks.compileKotlin {
    dependsOn(generateModels)
}
```

---

## Task Inputs/Outputs: Incremental Builds

The key to fast builds with generated code: **declare inputs and outputs**.

```kotlin
val generateModels by tasks.registering {
    // INPUTS: what triggers regeneration
    inputs.file("src/main/resources/schema.json")
    inputs.property("version", project.version)

    // OUTPUTS: what the task produces
    outputs.dir(layout.buildDirectory.dir("generated/models"))

    doLast { /* ... */ }
}
```

If inputs haven't changed since last run → task is `UP-TO-DATE` → skipped. This is how Gradle avoids regenerating code on every build.

---

## IDE Integration

Generated sources need to be recognized by the IDE for autocomplete:

```kotlin
// Method 1: Add to source set (shown above)
sourceSets.main {
    kotlin.srcDir("${layout.buildDirectory.get()}/generated/openapi/src/main/kotlin")
}

// Method 2: Use the idea plugin
plugins {
    idea
}

idea {
    module {
        generatedSourceDirs.add(file("${layout.buildDirectory.get()}/generated/openapi/src/main/kotlin"))
    }
}
```

After adding generated sources, run:
```bash
./gradlew :api:openApiGenerate  # generate the code
# Then refresh/sync your IDE
```

---

## Separate Source Set for Generated Code

For cleaner separation, put generated code in its own source set:

```kotlin
sourceSets {
    create("generated") {
        kotlin.srcDir("${layout.buildDirectory.get()}/generated/openapi/src/main/kotlin")
    }

    main {
        compileClasspath += sourceSets["generated"].output
        runtimeClasspath += sourceSets["generated"].output
    }
}

val generatedImplementation by configurations.getting {
    extendsFrom(configurations.implementation.get())
}

tasks.named("compileGeneratedKotlin") {
    dependsOn(tasks.openApiGenerate)
}

tasks.compileKotlin {
    dependsOn("compileGeneratedKotlin")
}
```

This keeps generated and hand-written code in separate compilation units. Useful when generated code has different compiler settings or when you want to suppress warnings only for generated code.

---

## .gitignore for Generated Code

```gitignore
# Never commit generated code
build/
**/build/generated/
```

---

## Convention Plugin for Code Generation

```kotlin
// buildSrc/src/main/kotlin/vaultline.openapi-conventions.gradle.kts
plugins {
    id("org.openapi.generator")
}

// Default configuration — modules override inputSpec
openApiGenerate {
    generatorName.set("kotlin-spring")
    outputDir.set("${layout.buildDirectory.get()}/generated/openapi")
    configOptions.set(mapOf(
        "interfaceOnly" to "true",
        "useSpringBoot3" to "true",
    ))
}

sourceSets {
    named("main") {
        kotlin {
            srcDir("${layout.buildDirectory.get()}/generated/openapi/src/main/kotlin")
        }
    }
}

tasks.named("compileKotlin") {
    dependsOn(tasks.named("openApiGenerate"))
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
kotlin.srcDir("path")           │ Add directory to source set
layout.buildDirectory.dir(...)  │ Reference build output directory
inputs.file / inputs.dir        │ Declare task inputs (for caching)
outputs.dir                     │ Declare task outputs (for caching)
dependsOn(generateTask)         │ Compile waits for generation
UP-TO-DATE                      │ Task skipped (inputs unchanged)
build/generated/                │ Convention for generated code
.gitignore build/               │ Never commit generated code
idea { module { generatedSourceDirs } } │ IDE recognizes generated code
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The build works. Source sets are clean. But it's slow — 4 minutes for a full build. Derek is tired of waiting. Time to make it fast: build cache, incremental compilation, and parallel execution.

---

[← Chapter 9: Feature Variants](chapter-09-feature-variants.md) | [Chapter 11: Build Cache →](chapter-11-build-cache.md)
