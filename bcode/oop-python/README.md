# Object-Oriented Python — From Scripts to Systems

A narrative-driven course on object-oriented programming in Python. You're a developer at a growing startup where spaghetti scripts are collapsing under their own weight. Over 15 chapters, you'll refactor chaos into clean architecture — one broken abstraction at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, why OOP, the cast |
| 01 | [The God Script](chapter-01-classes.md) | 2000-line script nobody can modify | Classes, instances, attributes, methods |
| 02 | [State That Lies](chapter-02-encapsulation.md) | External code corrupts internal state | Encapsulation, properties, private attributes |
| 03 | [Copy-Paste Inheritance](chapter-03-inheritance.md) | Same logic in 5 files | Inheritance, super(), method overriding |
| 04 | [The Diamond Problem](chapter-04-mro.md) | Multiple inheritance breaks | MRO, C3 linearization, mixins |
| 05 | [One Interface, Many Forms](chapter-05-polymorphism.md) | Giant if/elif chains for types | Polymorphism, duck typing, protocols |
| 06 | [Objects That Describe Themselves](chapter-06-dunder.md) | print(obj) shows garbage | Dunder methods, __repr__, __eq__, __hash__ |
| 07 | [Objects That Behave Like Built-ins](chapter-07-operators.md) | Can't add or compare custom objects | Operator overloading, __add__, __lt__, __contains__ |
| 08 | [Composition Over Inheritance](chapter-08-composition.md) | Inheritance hierarchy is 7 levels deep | Has-a vs is-a, delegation, strategy pattern |
| 09 | [Abstract Contracts](chapter-09-abc.md) | Subclass forgets to implement a method | ABC, abstractmethod, interface enforcement |
| 10 | [Class Machinery](chapter-10-classmethod.md) | Need alternative constructors and shared state | classmethod, staticmethod, class variables |
| 11 | [Descriptors & Properties](chapter-11-descriptors.md) | Validation logic duplicated everywhere | Descriptors, __get__/__set__, reusable validators |
| 12 | [Metaclasses](chapter-12-metaclasses.md) | Need to auto-register all subclasses | __init_subclass__, metaclasses, class creation |
| 13 | [Dataclasses & Slots](chapter-13-dataclasses.md) | Boilerplate __init__ everywhere | @dataclass, __slots__, frozen classes |
| 14 | [Design Patterns](chapter-14-patterns.md) | Recurring structural problems | Factory, Observer, Singleton, Repository |
| 15 | [Refactoring: The Full Arc](chapter-15-refactoring.md) | Putting it all together | From script to package, SOLID principles |

## Prerequisites

- Python 3.10+
- Basic Python (functions, lists, dicts, loops)

## Philosophy

Every OOP concept is introduced because a script became unmaintainable without it. No abstraction without a concrete pain point first. The messy code comes first. The clean design follows.
