# Modern Java — The Refactoring Diaries

You're a mid-level developer at **FinPulse**, a fintech startup that processes payments, generates reports, and sends notifications. The codebase is Java 11. It works. It's also 400,000 lines of `instanceof` chains, null checks, and `StringBuilder` gymnastics that make your eyes bleed.

One Monday, the CTO drops a bomb: **"We're upgrading to Java 21."**

Your mission: refactor the codebase to use modern Java features. Every chapter is a real refactoring task — a piece of ugly legacy code, a cleaner way to write it, and the concept behind the change.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Mid-level Dev | Comfortable with Java 11, suspicious of new syntax |
| **Priya** | Tech Lead | Loves clean code. "If it's more than 3 lines, it's wrong." |
| **Marcus** | Junior Dev | Just graduated. Thinks everything should be a stream. |
| **The Architect** | Principal Engineer | Speaks in design patterns. Hasn't written code since 2020. |
| **Compliance Carl** | Security/Compliance | "Can you prove this is immutable?" |
| **Jenkins** | The CI server | Breaks at 5pm on Fridays. Every Friday. |

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Java 21 (LTS) | Latest long-term support, virtual threads, pattern matching |
| Build | Gradle (Kotlin DSL) | Fast incremental builds, version catalogs |
| Framework | Spring Boot 3.2+ | Jakarta EE, native compilation support |
| Testing | JUnit 5 + AssertJ | Modern assertions, parameterized tests |

## Chapters

Every chapter starts with **ugly legacy code**, refactors it using a modern Java feature, and explains why the new version is better.

| Ch | Title | The Legacy Code | What You Learn |
|---|---|---|---|
| 1 | The DTO Graveyard | 47 getter/setter classes | Records, compact constructors |
| 2 | The instanceof Staircase | 200-line if/else type checks | Sealed classes, pattern matching |
| 3 | The Switch From Hell | Nested switch with fall-through bugs | Switch expressions, pattern matching for switch |
| 4 | The String Butcher | StringBuilder + escape sequences | Text blocks, string templates |
| 5 | The Null Minefield | NullPointerException in production | Helpful NPEs, Optional patterns, records as value objects |
| 6 | The Thread Avalanche | 10,000 platform threads, OOM | Virtual threads, structured concurrency |
| 7 | The Collection Ceremony | Verbose list/map creation, iteration hacks | Sequenced collections, collection factories, toList() |
| 8 | The Stream Spaghetti | Unreadable 15-line stream pipelines | Gatherers, mapMulti, teeing collector |

## What You'll Learn

### Chapter 1 — Records
`record`, compact constructors, custom validation, records as DTOs, records with builders, serialization, `@JsonProperty`

### Chapter 2 — Sealed Classes & Pattern Matching
`sealed`, `permits`, `instanceof` pattern matching, exhaustive switches, algebraic data types, the visitor pattern is dead

### Chapter 3 — Switch Expressions
Arrow syntax, expression returns, pattern matching in switch, guarded patterns, `null` in switch, exhaustiveness

### Chapter 4 — Text Blocks & String Templates
`"""` text blocks, indentation control, `\s` and `\` escape, `formatted()`, STR template processor (preview)

### Chapter 5 — Null Safety Patterns
Helpful NullPointerExceptions, `Optional` best practices, records as non-null value objects, `Objects.requireNonNull`

### Chapter 6 — Virtual Threads
`Thread.ofVirtual()`, `Executors.newVirtualThreadPerTaskExecutor()`, structured concurrency, when NOT to use virtual threads, pinning

### Chapter 7 — Collections
`List.of()`, `Map.of()`, `SequencedCollection`, `reversed()`, `getFirst()`/`getLast()`, `stream().toList()`, unmodifiable wrappers

### Chapter 8 — Advanced Streams
`Gatherers` (preview), `mapMulti()`, `Collectors.teeing()`, `Stream.toList()` vs `collect(toList())`, `takeWhile`/`dropWhile`
