---
title: "Chapter 4 - Database"
date: 2026-05-29
series: "Spring Boot REST API"
chapter: 4
---

# Chapter 4: Database

[Previous: Validation and Error Handling](../chapter-03-validation) | [Next: Security](../chapter-05-security)

---

## Overview

We set up Spring Data JPA with PostgreSQL, define entities, create repositories with pagination, use Specifications for dynamic queries, and manage schema with Flyway.

## Entity

```java
package com.example.bookstore.model;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "books")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String author;

    @Column(nullable = false, unique = true, length = 13)
    private String isbn;

    private int pages;

    @Column(name = "created_at", updatable = false)
    private Instant createdAt;

    @PrePersist
    void onCreate() {
        this.createdAt = Instant.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }
    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }
    public int getPages() { return pages; }
    public void setPages(int pages) { this.pages = pages; }
    public Instant getCreatedAt() { return createdAt; }
}
```

## Repository

```java
package com.example.bookstore.repository;

import com.example.bookstore.model.Book;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import java.util.Optional;

public interface BookRepository extends JpaRepository<Book, Long>,
        JpaSpecificationExecutor<Book> {

    Optional<Book> findByIsbn(String isbn);
    boolean existsByIsbn(String isbn);
}
```

## Pagination

```java
// In BookController
@GetMapping
public ResponseEntity<Page<BookResponse>> getAllBooks(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(defaultValue = "title") String sort) {
    Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
    return ResponseEntity.ok(bookService.findAll(pageable));
}
```

```java
// In BookService
public Page<BookResponse> findAll(Pageable pageable) {
    return bookRepository.findAll(pageable).map(this::toResponse);
}
```

## Specifications for Dynamic Queries

```java
package com.example.bookstore.repository;

import com.example.bookstore.model.Book;
import org.springframework.data.jpa.domain.Specification;

public class BookSpecifications {

    public static Specification<Book> hasAuthor(String author) {
        return (root, query, cb) ->
                author == null ? null : cb.equal(root.get("author"), author);
    }

    public static Specification<Book> titleContains(String keyword) {
        return (root, query, cb) ->
                keyword == null ? null : cb.like(
                        cb.lower(root.get("title")),
                        "%" + keyword.toLowerCase() + "%");
    }

    public static Specification<Book> minPages(Integer min) {
        return (root, query, cb) ->
                min == null ? null : cb.greaterThanOrEqualTo(root.get("pages"), min);
    }
}
```

Usage in the controller:

```java
@GetMapping("/search")
public ResponseEntity<Page<BookResponse>> searchBooks(
        @RequestParam(required = false) String author,
        @RequestParam(required = false) String title,
        @RequestParam(required = false) Integer minPages,
        Pageable pageable) {
    Specification<Book> spec = Specification
            .where(BookSpecifications.hasAuthor(author))
            .and(BookSpecifications.titleContains(title))
            .and(BookSpecifications.minPages(minPages));
    return ResponseEntity.ok(bookService.search(spec, pageable));
}
```

## Flyway Migrations

Place SQL files in `src/main/resources/db/migration/`:

```sql
-- V1__create_books_table.sql
CREATE TABLE books (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) NOT NULL UNIQUE,
    pages INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_isbn ON books(isbn);
```

```sql
-- V2__add_category_column.sql
ALTER TABLE books ADD COLUMN category VARCHAR(100);
```

## Running PostgreSQL with Docker

```bash
docker run -d \
  --name bookstore-db \
  -e POSTGRES_DB=bookstore \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

---

[Previous: Validation and Error Handling](../chapter-03-validation) | [Next: Security](../chapter-05-security)
