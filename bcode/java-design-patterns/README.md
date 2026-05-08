# Design Patterns in Java — From Spaghetti to Systems

A narrative-driven course on the Gang of Four design patterns, implemented in modern Java. You're a tech lead at **PlugBoard**, a plugin-based document editor. The codebase is a mess of if-else chains, god classes, and copy-pasted code. Each pattern you introduce fixes a real architectural pain point.

## Episodes

| # | Title | The Pain | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, SOLID principles recap, the cast |
| 01 | [One and Only](chapter-01-singleton.md) | Multiple config loaders fight over state | Singleton, thread-safe initialization, enum trick |
| 02 | [Building Complex Objects](chapter-02-builder.md) | 15-parameter constructor from hell | Builder pattern, fluent API, immutability |
| 03 | [Object Factory](chapter-03-factory-method.md) | Switch statement for every new document type | Factory Method, polymorphic creation |
| 04 | [Family of Objects](chapter-04-abstract-factory.md) | UI themes require coordinated object sets | Abstract Factory, theme consistency |
| 05 | [Clone Wars](chapter-05-prototype.md) | Deep copying complex document state | Prototype, Cloneable, copy constructors |
| 06 | [Wrapping Behavior](chapter-06-decorator.md) | Feature flags create 64 subclass combinations | Decorator, composition over inheritance |
| 07 | [Simplified Interface](chapter-07-facade.md) | Export requires calling 12 subsystems | Facade, API simplification |
| 08 | [Plug It In](chapter-08-strategy.md) | Hardcoded algorithms can't be swapped | Strategy, runtime algorithm selection |
| 09 | [Undo Everything](chapter-09-command.md) | No undo, no redo, no macro recording | Command, execute/undo, command queue |
| 10 | [Watch and React](chapter-10-observer.md) | Components don't know when data changes | Observer, event bus, loose coupling |
| 11 | [State Machine](chapter-11-state.md) | Nested if-else for document lifecycle | State pattern, transitions, state explosion |
| 12 | [Tree of Components](chapter-12-composite.md) | Groups of shapes behave differently than singles | Composite, uniform interface, recursive structures |
| 13 | [Lazy Loading](chapter-13-proxy.md) | Loading all images crashes memory | Proxy, virtual proxy, protection proxy |
| 14 | [Walking the Tree](chapter-14-iterator.md) | Different traversals hardcoded everywhere | Iterator, internal vs external, Java Iterable |
| 15 | [Adapting Legacy](chapter-15-adapter.md) | New plugin API vs old plugin API | Adapter, class vs object adapter, wrapper |

## Prerequisites

- Java 17+
- Any IDE (IntelliJ recommended for refactoring tools)

## Philosophy

Every pattern is introduced because the code is painful without it. You'll feel the pain of the naive approach before you see the pattern. The spaghetti comes first. The structure follows.
