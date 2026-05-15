# Chapter 0: Before You Start

[Chapter 1: The God Script →](chapter-01-classes.md)

---

## The Story

This is a series about object-oriented programming in Python — but not the kind where you memorize "a class is a blueprint for objects" and move on.

You're a developer at **ShipFast**, a logistics startup that tracks packages, routes drivers, and manages warehouse inventory. The company started as a weekend hackathon project. The codebase started as a single Python script. That script is now 4,000 lines long, has 200 global variables, and breaks every time someone adds a feature.

Your tech lead, **Dana**, pulls you aside:

"The tracking script crashed again. Someone changed the `package_status` variable in the billing section and it broke the routing section 800 lines away. Nobody understands how the pieces connect. We need to split this into something maintainable. You know OOP — restructure it."

You nod. You've written classes before. `class Dog: def bark(self)`. How hard can it be to apply that to a real system?

Over the next 15 chapters, you'll refactor ShipFast's codebase from a tangled script into a clean object-oriented system. Every concept you learn solves a real problem — encapsulating state, eliminating duplication, enforcing contracts, making code extensible. And every naive refactoring will break in a way that teaches you why OOP patterns exist.

The inheritance hierarchy will become 7 levels deep and unmaintainable. The god class will just be a god class with methods instead of functions. The abstract base class will be too rigid. The mixin will create a diamond problem.

Each failure teaches you something about software design that no textbook definition could.

By the end, you'll have a production-quality package with clean abstractions, enforced interfaces, and extensible architecture — and you'll understand *when* OOP helps and *when* it's overkill.

## How to Read This

Every chapter is the same loop:

1. The codebase has a problem — something is fragile, duplicated, or incomprehensible
2. You try the obvious OOP solution
3. It works partially but creates a new problem
4. You learn the proper technique
5. You refactor, verify it's better, and move on

No concept shows up before you need it. You won't hear about abstract base classes until a subclass silently forgets to implement a critical method. You won't touch metaclasses until you need automatic registration of plugins.

The messy code comes first. The clean design follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Developer | Pragmatic. "Does this actually make the code better?" |
| **Dana** | Tech Lead | Experienced. "Inheritance isn't always the answer." |
| **Marcus** | Junior Dev | Enthusiastic. Creates 12-level class hierarchies. |
| **The Script** | `tracking.py` | 4,000 lines. 200 globals. Held together by comments. |
| **The Tests** | `test_tracking.py` | Barely exist. Break constantly. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | 2000-line script with tangled state | Classes, instances, __init__, methods |
| 2 | External code corrupts object state | Encapsulation, properties, name mangling |
| 3 | Same logic copy-pasted in 5 places | Inheritance, super(), method overriding |
| 4 | Multiple inheritance creates conflicts | MRO, C3 linearization, mixin pattern |
| 5 | Giant if/elif chains for different types | Polymorphism, duck typing, protocols |
| 6 | print(obj) shows `<__main__.Package at 0x...>` | __repr__, __str__, __eq__, __hash__ |
| 7 | Can't sort or compare custom objects | Operator overloading, rich comparisons |
| 8 | Inheritance hierarchy is too deep | Composition, delegation, strategy pattern |
| 9 | Subclass forgets to implement required method | ABC, abstractmethod, contracts |
| 10 | Need factory methods and shared counters | classmethod, staticmethod, class variables |
| 11 | Validation logic duplicated in every class | Descriptors, reusable property validators |
| 12 | Need to auto-discover all handler subclasses | __init_subclass__, metaclasses |
| 13 | Writing __init__ and __repr__ for the 50th time | @dataclass, __slots__, frozen |
| 14 | Same structural problems keep recurring | Factory, Observer, Repository patterns |
| 15 | From script to installable package | SOLID principles, full refactoring arc |

## Prerequisites

One thing: Python 3.10+ and comfort with basic Python.

### Python 3.10+

```bash
python3 --version
# Python 3.10.x or higher
```

We use 3.10+ for `match` statements and modern type hints (`list[str]` instead of `List[str]`).

### What You Should Already Know

- Variables, functions, loops, conditionals
- Lists, dicts, tuples, sets
- Importing modules
- Basic file I/O
- What `def` and `return` do

### What You Don't Need to Know Yet

- Classes (we'll build from scratch)
- Decorators (we'll explain them when needed)
- Type hints (introduced gradually)
- Design patterns (that's the whole course)

### Quick Check

```python
# If you can read this and understand what it does, you're ready
def process_packages(packages, status_filter):
    results = []
    for pkg in packages:
        if pkg["status"] == status_filter:
            results.append({
                "id": pkg["id"],
                "destination": pkg["destination"],
                "weight": pkg["weight"],
            })
    return sorted(results, key=lambda p: p["weight"], reverse=True)
```

If that makes sense, you have enough Python for this course.

## The Key Idea

Object-oriented programming answers one question: **How do you organize code that manages complex state?**

A script with 200 variables and 100 functions works fine at 500 lines. At 4,000 lines, nobody knows which functions modify which variables, which variables depend on which other variables, or what happens if you change one thing.

OOP's answer: **bundle related data and behavior together into objects**. A `Package` object knows its own weight, destination, and status. A `Driver` object knows its own route and capacity. They don't touch each other's internals.

```python
# Without OOP: which functions modify which variables?
package_id = "PKG-001"
package_weight = 2.5
package_status = "in_transit"
driver_name = "Alice"
driver_capacity = 50.0
# ... 200 more variables ...
# ... 100 functions that read/write these ...

# With OOP: state is bundled with behavior
class Package:
    def __init__(self, id, weight):
        self.id = id
        self.weight = weight
        self.status = "pending"

    def ship(self):
        self.status = "in_transit"

    def deliver(self):
        self.status = "delivered"
```

The `Package` class owns its state. Nothing outside can accidentally corrupt it (well, in Python they can — that's Chapter 2). The interface is clear: create a package, ship it, deliver it.

## When OOP Is Overkill

Not everything needs a class. OOP adds complexity. Use it when:

- You have **state** that changes over time (not just data flowing through functions)
- Multiple **instances** of the same concept exist simultaneously
- You need to **enforce invariants** (a package can't be delivered before it's shipped)
- The system has **multiple interacting entities** with their own behavior

Don't use it for:
- Simple data transformation pipelines (use functions)
- One-off scripts (use functions)
- Stateless utilities (use modules with functions)

Dana's rule: "If you're writing a class with no `__init__` and only `@staticmethod`s, you wanted a module."

## The ShipFast Domain

Throughout this course, we'll model:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Package   │────→│    Route     │────→│    Warehouse    │
│ id, weight  │     │ stops, ETA   │     │ capacity, items │
│ status, dest│     │ driver       │     │ location        │
└─────────────┘     └──────────────┘     └─────────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐     ┌──────────────┐
│   Customer  │     │    Driver    │
│ name, addr  │     │ name, truck  │
│ orders      │     │ capacity     │
└─────────────┘     └──────────────┘
```

Packages, routes, warehouses, customers, drivers. Each has state. Each has behavior. They interact in complex ways. This is exactly the kind of system OOP was designed for.

Let's look at the mess we're starting from.

---

[Chapter 1: The God Script →](chapter-01-classes.md)
