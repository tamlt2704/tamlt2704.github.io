# Master Testing in Spring Boot

A comprehensive guide to testing Spring Boot applications with JUnit 5, Mockito 5, and Spring Boot 3.

## Chapters

1. [JUnit 5 Basics](/blog/junit-spring-testing/chapter-01-junit-basics) — Annotations, assertions, lifecycle, nested tests
2. [Mockito Fundamentals](/blog/junit-spring-testing/chapter-02-mockito) — Mocks, stubs, verification
3. [Argument Capture](/blog/junit-spring-testing/chapter-03-argument-capture) — Capturing and verifying complex arguments
4. [Lenient Stubbing](/blog/junit-spring-testing/chapter-04-lenient) — Strictness settings, unused stubs
5. [Parameterized Tests](/blog/junit-spring-testing/chapter-05-parameterized) — Data-driven testing with multiple sources
6. [Repeated and Dynamic Tests](/blog/junit-spring-testing/chapter-06-repeated) — Repetition, dynamic tests, flaky detection
7. [REST Controller Testing](/blog/junit-spring-testing/chapter-07-rest-testing) — MockMvc, WebMvcTest, security
8. [Advanced Topics](/blog/junit-spring-testing/chapter-08-advanced) — BDD, static mocks, SpyBean, coverage

## Dependencies (build.gradle.kts)

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
    jacoco
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.mockito:mockito-core:5.12.0")
    testImplementation("org.mockito:mockito-junit-jupiter:5.12.0")
    testImplementation("org.assertj:assertj-core:3.26.0")
    testImplementation("org.springframework.security:spring-security-test")
}

tasks.test {
    useJUnitPlatform()
    finalizedBy(tasks.jacocoTestReport)
}
```

[next: JUnit 5 Basics](/blog/junit-spring-testing/chapter-01-junit-basics)
