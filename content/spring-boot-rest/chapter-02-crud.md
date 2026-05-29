---
title: "Chapter 2 - CRUD Operations"
date: 2026-05-29
series: "Spring Boot REST API"
chapter: 2
---

# Chapter 2: CRUD Operations

[Previous: Project Setup](../chapter-01-setup) | [Next: Validation and Error Handling](../chapter-03-validation)

---

## Overview

We implement full CRUD for a `Book` resource using `@RestController`, proper HTTP methods, DTOs for request/response separation, and `ResponseEntity` for status codes.

## The DTO Layer

```java
package com.example.bookstore.dto;

public record CreateBookRequest(
    String title,
    String author,
    String isbn,
    int pages
) {}
```

```java
package com.example.bookstore.dto;

public record BookResponse(
    Long id,
    String title,
    String author,
    String isbn,
    int pages
) {}
```

```java
package com.example.bookstore.dto;

public record UpdateBookRequest(
    String title,
    String author,
    int pages
) {}
```

## The Controller

```java
package com.example.bookstore.controller;

import com.example.bookstore.dto.BookResponse;
import com.example.bookstore.dto.CreateBookRequest;
import com.example.bookstore.dto.UpdateBookRequest;
import com.example.bookstore.service.BookService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.net.URI;
import java.util.List;

@RestController
@RequestMapping("/api/books")
public class BookController {

    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @GetMapping
    public ResponseEntity<List<BookResponse>> getAllBooks() {
        return ResponseEntity.ok(bookService.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<BookResponse> getBook(@PathVariable Long id) {
        return ResponseEntity.ok(bookService.findById(id));
    }

    @PostMapping
    public ResponseEntity<BookResponse> createBook(@RequestBody CreateBookRequest request) {
        BookResponse created = bookService.create(request);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(created.id())
                .toUri();
        return ResponseEntity.created(location).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<BookResponse> updateBook(
            @PathVariable Long id,
            @RequestBody UpdateBookRequest request) {
        return ResponseEntity.ok(bookService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBook(@PathVariable Long id) {
        bookService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## The Service Layer

```java
package com.example.bookstore.service;

import com.example.bookstore.dto.BookResponse;
import com.example.bookstore.dto.CreateBookRequest;
import com.example.bookstore.dto.UpdateBookRequest;
import com.example.bookstore.exception.ResourceNotFoundException;
import com.example.bookstore.model.Book;
import com.example.bookstore.repository.BookRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
public class BookService {

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    public List<BookResponse> findAll() {
        return bookRepository.findAll().stream()
                .map(this::toResponse)
                .toList();
    }

    public BookResponse findById(Long id) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Book", id));
        return toResponse(book);
    }

    @Transactional
    public BookResponse create(CreateBookRequest request) {
        Book book = new Book();
        book.setTitle(request.title());
        book.setAuthor(request.author());
        book.setIsbn(request.isbn());
        book.setPages(request.pages());
        return toResponse(bookRepository.save(book));
    }

    @Transactional
    public BookResponse update(Long id, UpdateBookRequest request) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Book", id));
        book.setTitle(request.title());
        book.setAuthor(request.author());
        book.setPages(request.pages());
        return toResponse(bookRepository.save(book));
    }

    @Transactional
    public void delete(Long id) {
        if (!bookRepository.existsById(id)) {
            throw new ResourceNotFoundException("Book", id);
        }
        bookRepository.deleteById(id);
    }

    private BookResponse toResponse(Book book) {
        return new BookResponse(
                book.getId(), book.getTitle(), book.getAuthor(),
                book.getIsbn(), book.getPages()
        );
    }
}
```

## Key Concepts

| Annotation       | HTTP Method | Typical Use        |
| ---------------- | ----------- | ------------------ |
| `@GetMapping`    | GET         | Retrieve resources |
| `@PostMapping`   | POST        | Create a resource  |
| `@PutMapping`    | PUT         | Full update        |
| `@DeleteMapping` | DELETE      | Remove a resource  |

**ResponseEntity status codes:**

- `200 OK` — successful GET/PUT
- `201 Created` — successful POST (include `Location` header)
- `204 No Content` — successful DELETE

**Why DTOs?** Decouple API contract from internal model, control exposed fields, allow different shapes for create vs. update vs. response.

---

[Previous: Project Setup](../chapter-01-setup) | [Next: Validation and Error Handling](../chapter-03-validation)
