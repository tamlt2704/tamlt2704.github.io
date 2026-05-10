# Spring Tips & Tricks — The Stuff They Don't Teach in Tutorials

A collection of practical Spring Boot knowledge for working developers. Not a beginner course — this is the stuff you discover after 6 months of production Spring and wish someone had told you on day one.

## Episodes

| # | Title | What You Learn |
|---|---|---|
| 00 | [Event Publisher](chapter-00-events.md) | ApplicationEventPublisher, custom events, async events, transactional events |
| 01 | [Available Beans](chapter-01-beans.md) | List all beans, conditional beans, bean inspection, actuator |
| 02 | [Profiles & Configuration](chapter-02-profiles.md) | @Profile, @ConditionalOn*, environment-specific config |
| 03 | [Custom Annotations](chapter-03-annotations.md) | Meta-annotations, AOP, @Aspect for cross-cutting concerns |
| 04 | [Error Handling](chapter-04-errors.md) | @ControllerAdvice, ProblemDetail, global exception handling |
| 05 | [Scheduling & Async](chapter-05-async.md) | @Scheduled, @Async, virtual threads, TaskExecutor |
| 06 | [Caching](chapter-06-caching.md) | @Cacheable, cache managers, eviction, Redis cache |
| 07 | [Testing Tricks](chapter-07-testing.md) | @SpringBootTest slicing, @MockBean, Testcontainers, WireMock |
| 08 | [Actuator & Observability](chapter-08-actuator.md) | Health checks, metrics, custom endpoints, Micrometer |
| 09 | [Security Patterns](chapter-09-security.md) | Method security, JWT, OAuth2, custom filters |
| 10 | [Performance](chapter-10-performance.md) | Connection pools, lazy init, startup time, native image |

## Prerequisites

- Spring Boot 3.2+
- Java 21+
- Basic Spring knowledge (controllers, services, repositories)

## Philosophy

Spring is enormous. You can't learn it all. But there are ~50 tricks that cover 90% of real-world needs. This course is those 50 tricks, organized by topic, with copy-pasteable code.
