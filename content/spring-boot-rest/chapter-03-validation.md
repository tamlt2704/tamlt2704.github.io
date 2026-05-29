---
title: "Chapter 3 - Validation and Error Handling"
date: 2026-05-29
series: "Spring Boot REST API"
chapter: 3
---

# Chapter 3: Validation and Error Handling

[Previous: CRUD Operations](../chapter-02-crud) | [Next: Database](../chapter-04-database)

---

## Overview

We add input validation using Bean Validation annotations and build a global error handler that returns RFC 7807 Problem Detail responses.

## Adding Validation to DTOs

```java
package com.example.bookstore.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

public record CreateBookRequest(
    @NotBlank(message = "Title is required")
    @Size(max = 255, message = "Title must be at most 255 characters")
    String title,

    @NotBlank(message = "Author is required")
    String author,

    @NotBlank(message = "ISBN is required")
    @Size(min = 10, max = 13, message = "ISBN must be 10-13 characters")
    String isbn,

    @Positive(message = "Pages must be positive")
    int pages
) {}
```

## Activating Validation in the Controller

Add `@Valid` to the request body parameter:

```java
import jakarta.validation.Valid;

@PostMapping
public ResponseEntity<BookResponse> createBook(@Valid @RequestBody CreateBookRequest request) {
    BookResponse created = bookService.create(request);
    URI location = ServletUriComponentsBuilder.fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(created.id())
            .toUri();
    return ResponseEntity.created(location).body(created);
}
```

## Custom Exception

```java
package com.example.bookstore.exception;

public class ResourceNotFoundException extends RuntimeException {

    private final String resource;
    private final Object id;

    public ResourceNotFoundException(String resource, Object id) {
        super(String.format("%s with id %s not found", resource, id));
        this.resource = resource;
        this.id = id;
    }

    public String getResource() { return resource; }
    public Object getId() { return id; }
}
```

## Global Exception Handler with ProblemDetail

```java
package com.example.bookstore.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.net.URI;
import java.util.List;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Resource Not Found");
        problem.setType(URI.create("https://api.bookstore.com/errors/not-found"));
        problem.setProperty("resource", ex.getResource());
        problem.setProperty("id", ex.getId());
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        List<Map<String, String>> errors = ex.getBindingResult()
                .getFieldErrors().stream()
                .map(fe -> Map.of(
                        "field", fe.getField(),
                        "message", fe.getDefaultMessage() != null
                                ? fe.getDefaultMessage() : "Invalid value"
                ))
                .toList();

        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, "Validation failed");
        problem.setTitle("Validation Error");
        problem.setType(URI.create("https://api.bookstore.com/errors/validation"));
        problem.setProperty("errors", errors);
        return problem;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGeneric(Exception ex) {
        return ProblemDetail.forStatusAndDetail(
                HttpStatus.INTERNAL_SERVER_ERROR, "An unexpected error occurred");
    }
}
```

## Example Error Response

Request with invalid data:

```bash
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title":"","author":"","isbn":"x","pages":-1}'
```

Response (HTTP 400):

```json
{
  "type": "https://api.bookstore.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Validation failed",
  "errors": [
    { "field": "title", "message": "Title is required" },
    { "field": "author", "message": "Author is required" },
    { "field": "isbn", "message": "ISBN must be 10-13 characters" },
    { "field": "pages", "message": "Pages must be positive" }
  ]
}
```

## Common Bean Validation Annotations

| Annotation         | Purpose                    |
| ------------------ | -------------------------- |
| `@NotBlank`        | Non-null, non-empty string |
| `@NotNull`         | Non-null value             |
| `@Size(min, max)`  | String/collection length   |
| `@Positive`        | Number greater than 0      |
| `@Email`           | Valid email format         |
| `@Pattern(regexp)` | Regex match                |
| `@Min` / `@Max`    | Numeric bounds             |

---

[Previous: CRUD Operations](../chapter-02-crud) | [Next: Database](../chapter-04-database)
