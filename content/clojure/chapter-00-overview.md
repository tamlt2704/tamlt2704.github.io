# Practical Clojure: From Zero to Production

A hands-on guide to Clojure inspired by Peter Seibel's _Practical Common Lisp_ — 32 chapters alternating concepts with real projects. Learn by building, not by reading.

## Part 1: Foundations

1. [Introduction: Why Clojure?](chapter-01-why-clojure.md) — What makes Clojure different
2. [Lather, Rinse, Repeat: The REPL](chapter-02-repl.md) — Interactive development workflow
3. [Practical: A Contact Book](chapter-03-contact-book.md) — Atoms, maps, file I/O
4. [Syntax and Evaluation](chapter-04-syntax.md) — Forms, special forms, threading
5. [Functions](chapter-05-functions.md) — Higher-order, composition, closures, recursion
6. [Data Structures](chapter-06-data-structures.md) — Vectors, maps, sets, structural sharing
7. [Sequences and Laziness](chapter-07-sequences.md) — Lazy seqs, transducers, infinite data
8. [Practical: A Data Pipeline](chapter-08-data-pipeline.md) — CSV processing, aggregation

## Part 2: Power Tools

9. [Namespaces and Project Structure](chapter-09-namespaces.md) — deps.edn, organization
10. [Destructuring and Pattern Matching](chapter-10-destructuring.md) — Elegant data access
11. [Polymorphism: Multimethods and Protocols](chapter-11-polymorphism.md) — Dispatch without classes
12. [Practical: A REST API](chapter-12-rest-api.md) — Ring, Reitit, JSON, middleware
13. [Concurrency and State](chapter-13-concurrency.md) — Atoms, refs, agents, core.async
14. [Macros: Code as Data](chapter-14-macros.md) — Metaprogramming, syntax extension
15. [Practical: A Testing Framework](chapter-15-testing-framework.md) — Build your own deftest
16. [Error Handling](chapter-16-errors.md) — ex-info, error values, conditions

## Part 3: Specification and Quality

17. [Spec and Validation](chapter-17-spec.md) — Data specs, generative testing
18. [Practical: A Spam Filter](chapter-18-spam-filter.md) — Naive Bayes classifier

## Part 4: Real-World Projects

19. [Practical: A Web Scraper](chapter-19-web-scraper.md) — HTTP, HTML parsing, concurrency
20. [Practical: A Chat Server](chapter-20-chat-server.md) — WebSockets, pub/sub
21. [Practical: A Build Tool](chapter-21-build-tool.md) — Task graphs, dependency resolution
22. [Interop: Calling Java](chapter-22-java-interop.md) — Using any Java library
23. [Practical: A Database Layer](chapter-23-database.md) — JDBC, migrations, transactions
24. [ClojureScript and the Browser](chapter-24-clojurescript.md) — Reagent, re-frame, full-stack

## Part 5: Advanced Patterns

25. [core.async Patterns](chapter-25-async.md) — Pipelines, fan-out, backpressure, batching
26. [Practical: Parsing Binary Files](chapter-26-binary-parsing.md) — PNG, ID3, ZIP formats
27. [Practical: An MP3 Database](chapter-27-mp3-database.md) — File scanning, indexing, search
28. [Practical: A Web Application](chapter-28-web-app.md) — Full-stack with HTML views + API

## Part 6: Mastery

29. [Practical: An HTML Generation Library](chapter-29-html-generation.md) — Interpreter and compiler
30. [Practical: Building a DSL](chapter-30-dsl.md) — Domain-specific languages with macros
31. [Production Deployment](chapter-31-production.md) — Docker, monitoring, CI/CD, REPL in prod
32. [Conclusion: What's Next?](chapter-32-conclusion.md) — Libraries, community, project ideas

## Prerequisites

- Any programming background (Java, Python, JavaScript, etc.)
- A text editor (VS Code + Calva, Emacs + CIDER, or IntelliJ + Cursive)
- Java 17+

## What You Will Build

By the end of this guide you will have built:

- A contact management CLI (atoms, maps, persistence)
- A data processing pipeline (sequences, transducers, CSV)
- A REST API with middleware (Ring, JSON, routing)
- Your own testing framework (macros, metaprogramming)
- A Bayesian spam filter (functional data processing)
- A concurrent web scraper (core.async, HTTP)
- A real-time chat server (WebSockets, channels)
- A build tool with dependency resolution (graphs, macros)
- A database access layer (Java interop, JDBC)
- A ClojureScript todo app (Reagent, React)
- A binary file parser (PNG, ID3, ZIP)
- An MP3 library manager (file I/O, indexing)
- A full web application (server-side rendering + API)
- An HTML generation library (interpreter + compiler)
- A domain-specific language (macros, multimethod dispatch)
