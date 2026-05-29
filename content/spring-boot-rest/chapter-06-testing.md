---
title: "Chapter 6 - Testing"
date: 2026-05-29
series: "Spring Boot REST API"
chapter: 6
---

# Chapter 6: Testing

[Previous: Security](../chapter-05-security) | [Next: Documentation and Deployment](../chapter-07-docs)

---

## Overview

We write unit tests for the web layer with `@WebMvcTest`, repository tests with `@DataJpaTest`, full integration tests with `@SpringBootTest` and Testcontainers, and API tests with REST Assured.

## Test Dependencies

```kotlin
// build.gradle.kts
testImplementation("org.springframework.boot:spring-boot-starter-test")
testImplementation("org.springframework.security:spring-security-test")
testImplementation("org.testcontainers:junit-jupiter")
testImplementation("org.testcontainers:postgresql")
testImplementation("io.rest-assured:rest-assured")
```

## Controller Unit Test with @WebMvcTest

```java
package com.example.bookstore.controller;

import com.example.bookstore.dto.BookResponse;
import com.example.bookstore.service.BookService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.bean.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(BookController.class)
class BookControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private BookService bookService;

    @Test
    void shouldReturnAllBooks() throws Exception {
        var books = List.of(
                new BookResponse(1L, "Clean Code", "Robert Martin", "9780132350884", 464)
        );
        when(bookService.findAll()).thenReturn(books);

        mockMvc.perform(get("/api/books"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].title").value("Clean Code"))
                .andExpect(jsonPath("$[0].author").value("Robert Martin"));
    }
}
```

## Repository Test with @DataJpaTest

```java
package com.example.bookstore.repository;

import com.example.bookstore.model.Book;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class BookRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private BookRepository bookRepository;

    @Test
    void shouldFindBookByIsbn() {
        Book book = new Book();
        book.setTitle("Test Book");
        book.setAuthor("Author");
        book.setIsbn("1234567890");
        book.setPages(200);
        entityManager.persistAndFlush(book);

        var found = bookRepository.findByIsbn("1234567890");

        assertThat(found).isPresent();
        assertThat(found.get().getTitle()).isEqualTo("Test Book");
    }
}
```

## Integration Test with Testcontainers

```java
package com.example.bookstore;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class BookstoreIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void shouldReturnEmptyListInitially() {
        var response = restTemplate.getForEntity("/api/books", String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }
}
```

## API Test with REST Assured

```java
package com.example.bookstore;

import io.restassured.RestAssured;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class BookApiTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @LocalServerPort
    private int port;

    @BeforeEach
    void setUp() {
        RestAssured.port = port;
    }

    @Test
    void shouldCreateAndRetrieveBook() {
        String bookJson = """
                {
                    "title": "Effective Java",
                    "author": "Joshua Bloch",
                    "isbn": "9780134685991",
                    "pages": 416
                }
                """;

        String location = given()
                .contentType("application/json")
                .body(bookJson)
                .when()
                .post("/api/books")
                .then()
                .statusCode(201)
                .header("Location", containsString("/api/books/"))
                .extract().header("Location");

        given()
                .when()
                .get(location)
                .then()
                .statusCode(200)
                .body("title", equalTo("Effective Java"))
                .body("author", equalTo("Joshua Bloch"));
    }
}
```

## Running Tests

```bash
./gradlew test
```

---

[Previous: Security](../chapter-05-security) | [Next: Documentation and Deployment](../chapter-07-docs)
