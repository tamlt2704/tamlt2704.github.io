# Gradle Mastery

Build systems that don't fight you. Build a fintech payment platform (Vaultline) with multi-module architecture, custom source sets, isolated test layers, and production-grade CI/CD.

## Chapters

| # | Topic | Key Concepts |
|---|---|---|
| 00 | [Overview](chapter-00-overview.md) | Architecture, mental model, roadmap |
| 01 | [First Build](chapter-01-first-build.md) | Project structure, Kotlin DSL, tasks, plugins, daemon |
| 02 | [Dependencies](chapter-02-dependencies.md) | api vs implementation vs compileOnly, BOMs, conflict resolution |
| 03 | [Testing](chapter-03-testing.md) | JUnit 5, test filtering, parallel execution, reports |
| 04 | [Multi-Project](chapter-04-multi-project.md) | Modules, project dependencies, task execution |
| 05 | [Convention Plugins](chapter-05-conventions.md) | buildSrc, precompiled scripts, DRY configuration |
| 06 | [Source Sets](chapter-06-source-sets.md) | Custom source sets, separate dependencies, integrationTest |
| 07 | [Multiple Source Sets](chapter-07-multiple-source-sets.md) | contractTest, jmh, classpath isolation, CI layers |
| 08 | [Test Fixtures](chapter-08-test-fixtures.md) | java-test-fixtures, shared test utilities across modules |
| 09 | [Feature Variants](chapter-09-feature-variants.md) | Optional features, capability conflicts, consumer choice |
| 10 | [Generated Sources](chapter-10-generated-sources.md) | OpenAPI, protobuf, task inputs/outputs, IDE integration |
| 11 | Build Cache | Local/remote cache, incremental compilation |
| 12 | CI Performance | Remote cache, parallel execution, configuration cache |
| 13 | Build Scans | Profiling, --scan, finding slow tasks |
| 14 | Lazy Configuration | Providers, avoiding eagerness, configuration avoidance |
| 15 | Version Catalogs | libs.versions.toml, central dependency management |
| 16 | Publishing | Maven Publish, signing, Maven Central |
| 17 | Docker Builds | Jib, application plugin, fat JARs |
| 18 | Custom Tasks & Plugins | Task authoring, plugin development |
| 19 | CI/CD Pipeline | GitHub Actions, caching, matrix builds |
| 20 | Production Build | Reproducibility, security, upgrade strategy |

## Special Focus: Source Sets (Chapters 6-10)

The core differentiator of this course. Covers:
- Creating custom source sets with isolated dependencies
- Integration tests (Testcontainers) separate from unit tests
- Contract tests (Pact) as a third layer
- Performance benchmarks (JMH) in their own source set
- Test fixtures shared across modules
- Feature variants (Redis vs Kafka)
- Generated code (OpenAPI, protobuf) in dedicated source sets

## Stack

- Gradle 8.x (Kotlin DSL)
- Kotlin / Java 17
- JUnit 5, Testcontainers, Pact
- Spring Boot (API module)
- Maven Publish
- GitHub Actions
