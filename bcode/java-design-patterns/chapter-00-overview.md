# Chapter 0: Before You Start

[Chapter 1: Singleton →](chapter-01-singleton.md)

---

## The Story

You're the tech lead at **PlugBoard**, a startup building a plugin-based document editor — think Notion meets VS Code. Users install plugins that add new block types, export formats, themes, and integrations.

The codebase is 18 months old and growing fast. The original developer (who left) believed in "just make it work." The result:

- A 2,000-line `DocumentManager` class that handles creation, rendering, saving, exporting, and undo
- A switch statement with 47 cases for creating different block types
- Copy-pasted code for every new export format (PDF, HTML, Markdown, DOCX)
- No plugin API — every "plugin" is a PR to the main repo
- Undo doesn't work for half the operations

Your CEO, **Mira**, has a vision: "I want a plugin marketplace by Q3." Your codebase can't support it. You need to refactor — but you can't rewrite everything at once. You need patterns that let you restructure incrementally.

Over 15 chapters, you'll apply one design pattern per chapter to fix one specific pain point. By the end, PlugBoard has a clean architecture that supports plugins, undo, theming, and lazy loading — without a rewrite.

## What Are Design Patterns?

Design patterns are named solutions to recurring design problems. They're not libraries or frameworks — they're structural ideas you implement yourself.

The Gang of Four (GoF) book defined 23 patterns in 1994. We'll cover 15 of the most useful ones, organized by what they solve:

### Creational (How objects are made)
| Pattern | Problem It Solves |
|---|---|
| Singleton | Need exactly one instance, globally accessible |
| Builder | Complex object construction with many optional parts |
| Factory Method | Subclasses decide which class to instantiate |
| Abstract Factory | Families of related objects without specifying classes |
| Prototype | Creating objects by cloning existing ones |

### Structural (How objects are composed)
| Pattern | Problem It Solves |
|---|---|
| Decorator | Add behavior without modifying existing classes |
| Facade | Simplify a complex subsystem interface |
| Composite | Treat individual objects and groups uniformly |
| Proxy | Control access to an object (lazy load, cache, protect) |
| Adapter | Make incompatible interfaces work together |

### Behavioral (How objects communicate)
| Pattern | Problem It Solves |
|---|---|
| Strategy | Swap algorithms at runtime |
| Command | Encapsulate actions as objects (undo, queue, log) |
| Observer | Notify dependents when state changes |
| State | Object behavior changes based on internal state |
| Iterator | Traverse collections without exposing internals |

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Tech Lead | Refactoring one pattern at a time |
| **Mira** | CEO | "Plugin marketplace by Q3. No excuses." |
| **Dev** | Junior Developer | "Why can't I just add another if-else?" |
| **Aisha** | Senior Engineer | Reviews your PRs. "This is over-engineered." |
| **Plugin Authors** | External devs | "Your API is impossible to extend." |

## Prerequisites

### Java 17+

```bash
java --version
# java 17.0.x or higher
```

We use records, sealed interfaces, and pattern matching where they make patterns cleaner.

### SOLID Principles (Quick Recap)

Design patterns build on SOLID. Quick refresher:

| Principle | One-liner |
|---|---|
| **S**ingle Responsibility | A class has one reason to change |
| **O**pen/Closed | Open for extension, closed for modification |
| **L**iskov Substitution | Subtypes must be substitutable for their base types |
| **I**nterface Segregation | Many specific interfaces > one fat interface |
| **D**ependency Inversion | Depend on abstractions, not concretions |

If these feel unfamiliar, you'll see them in action throughout the course. Every pattern is a concrete application of one or more SOLID principles.

## The Rules

1. **Feel the pain first** — every chapter starts with the bad code
2. **One pattern per problem** — don't combine patterns prematurely
3. **Patterns are tools, not goals** — if the simple code works, keep it simple
4. **Modern Java** — we use records, sealed types, and lambdas where they simplify

## Anti-Pattern Warning

The biggest mistake with design patterns: applying them everywhere. A Singleton for your logger? Fine. A Singleton for your user object? Disaster. An Abstract Factory for two object types? Over-engineering.

Every chapter includes a "When NOT to use this" section. Knowing when to skip a pattern is as important as knowing the pattern itself.

Let's fix PlugBoard's first problem: three different config loaders fighting over who loaded the settings.

---

[Chapter 1: Singleton →](chapter-01-singleton.md)
