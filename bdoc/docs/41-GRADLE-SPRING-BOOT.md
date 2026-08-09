# Chapter 41: Gradle for Spring Boot — Build System Mastery

## What you'll learn

- What Gradle does and how it differs from Maven
- Project structure: build.gradle.kts (Kotlin DSL)
- Dependency management: implementation, api, compileOnly, runtimeOnly
- The Spring Boot Gradle plugin
- Custom tasks: code generation, database migrations, Docker builds
- Multi-module projects (microservices)
- Build performance: caching, parallel execution, build scans
- CI/CD integration with Gradle
- Common problems and how to fix them

---

## PART 1: Gradle Fundamentals

## 41.1 What Gradle does

Gradle is a build automation tool. It handles:
- Compiling source code (Java, Kotlin)
- Managing dependencies (downloading JARs from Maven Central)
- Running tests
- Packaging (JAR, WAR, Docker images)
- Custom tasks (code generation, DB migrations, deployments)

## 41.2 Gradle vs Maven

| Aspect | Maven | Gradle |
|--------|-------|--------|
| Config format | XML (`pom.xml`) | Kotlin/Groovy (`build.gradle.kts`) |
| Flexibility | Convention-heavy, hard to customise | Fully programmable (it's code) |
| Performance | Moderate | Faster (incremental, cached, parallel) |
| Readability | Verbose XML | Concise DSL |
| Spring Boot | `spring-boot-starter-parent` | `spring-boot-gradle-plugin` |
| Multi-module | Works but verbose | Excellent (composite builds) |
| IDE support | Excellent | Excellent |
| Build cache | No | Yes (local + remote) |

**Rule of thumb:** Maven for simple projects where convention is enough. Gradle for complex builds, multi-module projects, or when you need custom build logic.

## 41.3 Build lifecycle

```
INITIALIZATION          CONFIGURATION              EXECUTION
(find projects)         (configure all tasks)      (run requested tasks)
      │                        │                        │
      ▼                        ▼                        ▼
settings.gradle.kts     build.gradle.kts           Selected tasks run
(which modules exist)   (define dependencies,      in dependency order
                         plugins, tasks)

Example: ./gradlew build
  → compileJava → processResources → classes → jar → test → check → build
```

## 41.4 Project structure

```
my-spring-app/
├── build.gradle.kts        ← Build configuration (dependencies, plugins, tasks)
├── settings.gradle.kts     ← Project name + modules (for multi-module)
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar        ← Gradle binary (committed to Git)
│       └── gradle-wrapper.properties ← Gradle version config
├── gradlew                 ← Linux/Mac build script (./gradlew build)
├── gradlew.bat             ← Windows build script
└── src/
    ├── main/
    │   ├── java/           ← Application code
    │   └── resources/      ← Config files (application.yml)
    └── test/
        ├── java/           ← Test code
        └── resources/      ← Test config
```

**The Gradle Wrapper (`gradlew`):** You never install Gradle globally. The wrapper downloads the exact version specified in `gradle-wrapper.properties`. Everyone on the team uses the same version.

```bash
# Always use the wrapper, not a globally installed gradle
./gradlew build        # Linux/Mac
gradlew.bat build      # Windows
```

## 41.5 settings.gradle.kts

```kotlin
// settings.gradle.kts
rootProject.name = "task-api"

// For multi-module projects:
// include("common", "api", "service", "infrastructure")
```

---

## PART 2: build.gradle.kts for Spring Boot

## 41.6 Complete Spring Boot build file

```kotlin
// build.gradle.kts
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    java
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
}

group = "com.example"
version = "1.0.0"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot starters
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-actuator")

    // Database
    runtimeOnly("org.postgresql:postgresql")
    runtimeOnly("org.flywaydb:flyway-core")
    runtimeOnly("org.flywaydb:flyway-database-postgresql")

    // JWT
    implementation("io.jsonwebtoken:jjwt-api:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.6")

    // Dev tools
    developmentOnly("org.springframework.boot:spring-boot-devtools")
    annotationProcessor("org.springframework.boot:spring-boot-configuration-processor")

    // Lombok (optional)
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // Testing
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.security:spring-security-test")
    testRuntimeOnly("com.h2database:h2")
}

tasks.withType<Test> {
    useJUnitPlatform()
}

// Boot JAR configuration
tasks.bootJar {
    archiveFileName.set("app.jar")
    launchScript()  // makes the JAR directly executable (./app.jar)
}
```

## 41.7 Understanding dependency configurations

```kotlin
dependencies {
    // IMPLEMENTATION: needed at compile time AND runtime
    // Transitive deps NOT exposed to consumers (in multi-module)
    implementation("org.springframework.boot:spring-boot-starter-web")

    // API: needed at compile time AND runtime
    // Transitive deps ARE exposed to consumers (for libraries)
    api("com.google.guava:guava:33.0.0-jre")

    // COMPILE_ONLY: needed at compile time, NOT at runtime
    // Use for: annotations processed at compile time (Lombok)
    compileOnly("org.projectlombok:lombok")

    // RUNTIME_ONLY: needed at runtime, NOT at compile time
    // Use for: JDBC drivers, SPI implementations
    runtimeOnly("org.postgresql:postgresql")

    // ANNOTATION_PROCESSOR: code generator that runs at compile time
    annotationProcessor("org.projectlombok:lombok")

    // DEVELOPMENT_ONLY: only in dev (not packaged in JAR)
    developmentOnly("org.springframework.boot:spring-boot-devtools")

    // TEST_IMPLEMENTATION: only for tests
    testImplementation("org.springframework.boot:spring-boot-starter-test")

    // TEST_RUNTIME_ONLY: test runtime deps (H2 for integration tests)
    testRuntimeOnly("com.h2database:h2")
}
```

**Visual:**
```
compile time ─────────────────────── runtime
     │                                   │
     ├── implementation ─────────────────┤  (both)
     ├── compileOnly                     │  (compile only)
     │                    runtimeOnly ───┤  (runtime only)
     ├── annotationProcessor             │  (compile — code gen)
     │                                   │
     ├── testImplementation ─────────────┤  (test both)
     │                    testRuntimeOnly┤  (test runtime)
```

## 41.8 The Spring Boot Gradle plugin

```kotlin
plugins {
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
}
```

**What it gives you:**

| Feature | What it does |
|---------|-------------|
| `bootJar` task | Creates executable fat JAR (all deps inside) |
| `bootRun` task | Runs the app with dev classpath |
| Dependency management | Auto-manages versions for ALL Spring-related deps (no version needed) |
| `bootBuildImage` task | Creates OCI container image (no Dockerfile needed!) |
| DevTools support | Auto-restart on code change |

```bash
# Run the app (dev mode with hot reload)
./gradlew bootRun

# Build the fat JAR
./gradlew bootJar
java -jar build/libs/app.jar

# Build Docker image (no Dockerfile required!)
./gradlew bootBuildImage --imageName=myregistry/task-api:1.0.0

# Skip tests
./gradlew build -x test
```

## 41.9 Dependency management — no versions needed

```kotlin
// Because of io.spring.dependency-management, you DON'T need versions
// for Spring ecosystem libraries — they're managed by the Spring Boot BOM

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")  // no version!
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.security:spring-security-oauth2-resource-server")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

// Only NON-Spring libs need explicit versions:
implementation("io.jsonwebtoken:jjwt-api:0.12.6")
implementation("com.google.guava:guava:33.0.0-jre")
```

---

## PART 3: Common Tasks

## 41.10 Essential Gradle commands

```bash
# Build
./gradlew build              # compile + test + package
./gradlew build -x test      # skip tests
./gradlew clean build        # delete build/ first, then build

# Run
./gradlew bootRun            # start Spring Boot app
./gradlew bootRun --args='--spring.profiles.active=dev'

# Test
./gradlew test               # run all tests
./gradlew test --tests "*.TaskServiceTest"   # specific test class
./gradlew test --tests "*.TaskServiceTest.createTask*"  # specific method
./gradlew test --info        # verbose output (see which tests run)

# Dependencies
./gradlew dependencies       # full dependency tree
./gradlew dependencies --configuration runtimeClasspath  # only runtime deps
./gradlew dependencyInsight --dependency spring-core     # why is this dep included?

# Info
./gradlew tasks              # list all available tasks
./gradlew properties         # all project properties
./gradlew --version          # Gradle version
```

## 41.11 Custom tasks

```kotlin
// build.gradle.kts

// Simple task
tasks.register("hello") {
    group = "custom"
    description = "Prints hello"
    doLast {
        println("Hello from Gradle!")
    }
}

// Task that generates a build info file
tasks.register("generateBuildInfo") {
    group = "custom"
    val outputFile = file("src/main/resources/build-info.properties")
    outputs.file(outputFile)

    doLast {
        outputFile.writeText("""
            build.version=${project.version}
            build.timestamp=${java.time.Instant.now()}
            build.jdk=${System.getProperty("java.version")}
        """.trimIndent())
    }
}

// Wire custom task into the build lifecycle
tasks.named("processResources") {
    dependsOn("generateBuildInfo")
}

// Task that runs Flyway migration
tasks.register<JavaExec>("migrateDb") {
    group = "database"
    description = "Run Flyway database migrations"
    mainClass.set("org.flywaydb.commandline.Main")
    classpath = sourceSets.main.get().runtimeClasspath
    args = listOf(
        "migrate",
        "-url=jdbc:postgresql://localhost:5432/taskapi",
        "-user=postgres",
        "-password=secret"
    )
}
```

## 41.12 Profiles and environment-specific builds

```kotlin
// build.gradle.kts

// Pass Spring profile via Gradle
tasks.named<org.springframework.boot.gradle.tasks.run.BootRun>("bootRun") {
    systemProperty("spring.profiles.active", project.findProperty("profile") ?: "dev")
}

// Usage: ./gradlew bootRun -Pprofile=prod
```

```kotlin
// Environment-specific resource filtering
tasks.processResources {
    filesMatching("application.yml") {
        expand(project.properties) // replaces ${version} in YAML with project.version
    }
}
```

---

## PART 4: Multi-Module Projects

## 41.13 When to use multi-module

Split into modules when:
- Shared code between microservices (DTOs, utils)
- Clear boundaries between layers (api / domain / infrastructure)
- Teams working on different modules independently
- Different deployment artifacts from same codebase

```
my-project/
├── settings.gradle.kts         ← declares all modules
├── build.gradle.kts            ← root (common config)
├── common/                     ← shared DTOs, utils
│   ├── build.gradle.kts
│   └── src/main/java/
├── api/                        ← REST controllers + Spring Boot app
│   ├── build.gradle.kts
│   └── src/main/java/
├── domain/                     ← business logic (no framework deps)
│   ├── build.gradle.kts
│   └── src/main/java/
└── infrastructure/             ← DB, messaging, external APIs
    ├── build.gradle.kts
    └── src/main/java/
```

## 41.14 Multi-module configuration

```kotlin
// settings.gradle.kts
rootProject.name = "task-platform"
include("common", "domain", "infrastructure", "api")
```

```kotlin
// build.gradle.kts (root — shared config for all modules)
plugins {
    java
    id("org.springframework.boot") version "3.3.0" apply false
    id("io.spring.dependency-management") version "1.1.5" apply false
}

subprojects {
    apply(plugin = "java")
    apply(plugin = "io.spring.dependency-management")

    group = "com.example.taskplatform"
    version = "1.0.0"

    java {
        toolchain {
            languageVersion = JavaLanguageVersion.of(21)
        }
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        testImplementation("org.springframework.boot:spring-boot-starter-test")
    }

    tasks.withType<Test> {
        useJUnitPlatform()
    }
}
```

```kotlin
// common/build.gradle.kts
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-annotations")
}
```

```kotlin
// domain/build.gradle.kts
dependencies {
    implementation(project(":common"))
    // No Spring deps here! Pure business logic.
}
```

```kotlin
// infrastructure/build.gradle.kts
dependencies {
    implementation(project(":common"))
    implementation(project(":domain"))
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    runtimeOnly("org.postgresql:postgresql")
}
```

```kotlin
// api/build.gradle.kts
plugins {
    id("org.springframework.boot")  // only the runnable module gets this
}

dependencies {
    implementation(project(":common"))
    implementation(project(":domain"))
    implementation(project(":infrastructure"))
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-security")
}
```

```bash
# Build everything
./gradlew build

# Run only the API module
./gradlew :api:bootRun

# Test only domain module
./gradlew :domain:test
```

---

## PART 5: Performance & CI/CD

## 41.15 Build performance

```kotlin
// gradle.properties (commit this to git)
org.gradle.parallel=true          # build modules in parallel
org.gradle.caching=true           # local build cache
org.gradle.daemon=true            # keep Gradle daemon alive between builds
org.gradle.jvmargs=-Xmx2g        # more memory for large projects

# Optional: configure test parallelism
# org.gradle.workers.max=4
```

**Build cache:** If input files + task config haven't changed → skip the task entirely (use cached output).

```bash
# See what's cached vs what ran
./gradlew build --info | grep "UP-TO-DATE\|FROM-CACHE"

# Build scan (detailed performance analysis)
./gradlew build --scan
# Opens a link in browser with timing per task, dependency resolution time, etc.
```

## 41.16 CI/CD with Gradle (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: "temurin"
          java-version: "21"

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      - name: Build
        run: ./gradlew build

      - name: Upload test reports
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: "**/build/reports/tests/"
```

**Gradle GitHub Action (`gradle/actions/setup-gradle`):**
- Caches `~/.gradle/caches` between runs (saves 30-60s)
- `cache-read-only` on PRs: read cache but don't pollute it with PR-specific deps

## 41.17 Docker build with Gradle

```kotlin
// Option 1: Spring Boot's built-in Buildpacks (no Dockerfile!)
tasks.named<org.springframework.boot.gradle.tasks.bundling.BootBuildImage>("bootBuildImage") {
    imageName.set("myregistry/task-api:${project.version}")
    environment.set(mapOf(
        "BP_JVM_VERSION" to "21",
        "BPE_JAVA_TOOL_OPTIONS" to "-XX:+UseZGC"
    ))
}
// ./gradlew bootBuildImage

// Option 2: Custom Dockerfile task
tasks.register<Exec>("dockerBuild") {
    group = "docker"
    dependsOn("bootJar")
    commandLine("docker", "build",
        "-t", "myregistry/task-api:${project.version}",
        "-f", "Dockerfile",
        "."
    )
}
```

## 41.18 Common problems and fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `Could not resolve dependency` | Version conflict or missing repo | `./gradlew dependencies` → find conflict, use `exclude` or `force` |
| `Incompatible versions` | Transitive dep brings old version | `implementation("lib") { exclude(group = "old-dep") }` |
| Build is slow | No cache, no parallel | Enable in `gradle.properties` |
| `OutOfMemoryError` | Heap too small | `org.gradle.jvmargs=-Xmx4g` |
| Tests pass locally, fail in CI | Environment difference | Use `@SpringBootTest` with embedded DB (H2) |
| `bootRun` doesn't pick up changes | No devtools | Add `developmentOnly("...spring-boot-devtools")` |
| `Cannot change dependencies after resolution` | Modifying deps in wrong phase | Move logic to `configurations.all { }` block |

```kotlin
// Force a specific version (override transitive)
configurations.all {
    resolutionStrategy {
        force("com.fasterxml.jackson.core:jackson-databind:2.17.0")
    }
}

// Exclude a transitive dependency
implementation("some-library:1.0") {
    exclude(group = "commons-logging", module = "commons-logging")
}
```

---

## Summary

✅ Gradle fundamentals: build lifecycle (init → configure → execute), wrapper, project structure
✅ build.gradle.kts: plugins, repositories, dependencies, tasks
✅ Dependency configurations: implementation, runtimeOnly, compileOnly, annotationProcessor, testImplementation
✅ Spring Boot plugin: bootRun, bootJar, bootBuildImage, dependency management
✅ Custom tasks: code generation, DB migration, Docker builds
✅ Multi-module projects: shared code, layer separation, module-specific plugins
✅ Performance: parallel builds, build cache, daemon, build scans
✅ CI/CD: GitHub Actions with Gradle cache, test reporting, Docker image building
✅ Troubleshooting: dependency conflicts, version forcing, excludes

## Key takeaways

**Gradle is code, not config.** Unlike Maven's XML, `build.gradle.kts` is Kotlin. You can use conditionals, loops, functions — any programming construct. This makes complex builds possible without plugins.

**The wrapper ensures reproducibility.** Everyone uses the same Gradle version. CI uses the same version. No "works on my machine" from build tool differences.

**Dependency configurations control visibility.** `implementation` hides transitive deps from consumers (faster compilation, less version conflict). Use `api` only in library modules that need to expose their deps.

**Spring Boot's dependency management is the killer feature.** You never manage Spring library versions manually. Add a starter, get all transitive deps at compatible versions automatically.

---

→ [Back to Chapter 40: React Native Games](./40-REACT-NATIVE-GAMES.md)
