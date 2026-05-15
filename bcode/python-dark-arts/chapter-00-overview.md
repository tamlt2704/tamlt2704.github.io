# Chapter 0: Before You Start

[Chapter 1: Everything Is an Object →](chapter-01-object-model.md)

---

## The Story

This is a series about advanced Python — but not the kind where you memorize "a metaclass is a class whose instances are classes" and move on.

You're a senior developer at **FrameForge**, a company that builds Python frameworks for other developers. Your users are backend teams who build APIs, CLIs, and data pipelines. They hate boilerplate. They want to write:

```python
class User(Model):
    name = StringField(max_length=100)
    email = StringField(unique=True)
    age = IntField(min_value=0)
```

And get a fully functional ORM model with validation, serialization, migrations, and query building — without writing any of that plumbing themselves.

Your CTO, **Vera**, sets the bar:

"Django does it. SQLAlchemy does it. Pydantic does it. Our users expect the same magic. They write a class with some fields, and everything else happens automatically. No boilerplate. No repetition. No ceremony. Figure out how the magic works, then build our own."

You nod. You've used these frameworks. You've never looked inside them. How hard can it be?

Over the next 15 chapters, you'll learn every technique Python's top frameworks use to eliminate boilerplate: decorators that inject behavior, descriptors that validate on assignment, metaclasses that register and transform classes, import hooks that discover plugins, AST manipulation that generates code. And every naive approach will produce too much code in a way that teaches you why the advanced technique exists.

The 50-line version comes first. The 5-line version follows.

## How to Read This

Every chapter is the same loop:

1. A user writes too much boilerplate — repetitive, error-prone, tedious
2. You try to eliminate it with basic Python
3. It works but doesn't scale (still repetitive at a different level)
4. You learn the advanced technique that frameworks use
5. The boilerplate disappears — users write declarations, the framework does the rest

No technique shows up before you need it. You won't hear about metaclasses until `__init_subclass__` isn't enough. You won't touch AST manipulation until decorators can't generate the code you need.

The verbose code comes first. The elegant code follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Senior Developer | "There must be a way to not write this 50 times." |
| **Vera** | CTO | "If the user has to write it, we failed." |
| **Leo** | Junior Framework Dev | "I just used eval(). Is that bad?" |
| **The Users** | Backend Teams | "I don't care how it works. I care that I write less." |
| **CPython** | The Runtime | Has opinions about everything. Surprisingly flexible. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | "What even is a class at runtime?" | Python's object model, type(), everything is an object |
| 2 | Same try/except/log wrapping 40 functions | Function decorators, @wraps, parameterized decorators |
| 3 | Same 5 methods added to 20 classes | Class decorators, automatic method injection |
| 4 | Validation logic copy-pasted in every class | Descriptors, __get__/__set__, reusable field types |
| 5 | Need auto-registration at class definition time | Metaclasses, __init_subclass__, class creation hooks |
| 6 | Proxy objects that forward attribute access | __getattr__, __getattribute__, dynamic dispatch |
| 7 | Resource cleanup patterns beyond files | Context managers, contextlib, generator-based CMs |
| 8 | Processing data larger than RAM | Generators, lazy evaluation, pipeline composition |
| 9 | Creating families of similar functions | Closures, nonlocal, function factories |
| 10 | Auto-discovering plugins at import time | Import system, importlib, sys.meta_path |
| 11 | Generating code from schemas | AST module, compile(), source transformation |
| 12 | I/O-bound work blocking everything | asyncio patterns, async generators, task groups |
| 13 | Runtime behavior from type annotations | get_type_hints(), TypeVar, Protocol, validation |
| 14 | Elegant code that's too slow | __slots__, caching, struct, memoryview |
| 15 | Building a declarative mini-framework | Combining all techniques into a cohesive system |

## Prerequisites

You should be comfortable with:

- Classes, inheritance, `@property`
- Functions as first-class objects (passing functions, returning functions)
- `*args`, `**kwargs`
- Basic type hints
- How modules and packages work

### Python 3.11+

```bash
python3 --version
# Python 3.11.x or higher
```

We use 3.11+ for `ExceptionGroup`, improved error messages, and `typing` features.

### Quick Check

```python
# If you can read this and understand what it does, you're ready
def make_validator(min_val, max_val):
    def validator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not (min_val <= result <= max_val):
                raise ValueError(f"{result} not in [{min_val}, {max_val}]")
            return result
        return wrapper
    return validator

@make_validator(0, 100)
def get_score():
    return 42
```

If you can trace through that and explain why `get_score()` returns 42 but `get_score` is actually `wrapper`, you're ready.

## The Key Idea

Python's advanced features all serve one goal: **write declarations, not implementations**.

Compare:

```python
# Implementation (what you write without metaprogramming):
class User:
    def __init__(self, name, email, age):
        if not isinstance(name, str) or len(name) > 100:
            raise ValueError("name must be str with max_length 100")
        if not isinstance(email, str):
            raise ValueError("email must be str")
        if not isinstance(age, int) or age < 0:
            raise ValueError("age must be non-negative int")
        self.name = name
        self.email = email
        self.age = age

    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age!r})"

    def __eq__(self, other):
        return isinstance(other, User) and self.name == other.name and ...

    def to_dict(self):
        return {"name": self.name, "email": self.email, "age": self.age}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["email"], data["age"])
```

```python
# Declaration (what you write WITH metaprogramming):
class User(Model):
    name = StringField(max_length=100)
    email = StringField(unique=True)
    age = IntField(min_value=0)
```

Same behavior. 4 lines instead of 25. The framework generates `__init__`, `__repr__`, `__eq__`, `to_dict`, `from_dict`, validation — all from the field declarations.

That's the power of metaprogramming: **you describe WHAT you want, the framework figures out HOW**.

## The Techniques Stack

Each technique builds on the previous:

```
Level 0: Functions
Level 1: Decorators (modify functions)
Level 2: Class decorators (modify classes)
Level 3: Descriptors (control attribute access)
Level 4: Metaclasses (control class creation)
Level 5: Import hooks (control module loading)
Level 6: AST manipulation (control code itself)
```

You almost never need Level 6. You rarely need Level 4. Most real-world metaprogramming lives at Levels 1-3. But understanding the full stack lets you choose the right tool.

## The Rule

Vera's rule for the team:

> "Use the simplest technique that eliminates the boilerplate. A decorator is simpler than a metaclass. A metaclass is simpler than AST manipulation. Don't be clever when simple works."

The progression:
1. Can a **function** solve it? Use a function.
2. Can a **decorator** solve it? Use a decorator.
3. Can a **class decorator** solve it? Use a class decorator.
4. Can **`__init_subclass__`** solve it? Use `__init_subclass__`.
5. Can a **descriptor** solve it? Use a descriptor.
6. Do you truly need a **metaclass**? Use a metaclass.
7. Do you truly need **AST manipulation**? Reconsider your life choices. Then use it.

Let's start by understanding what Python objects actually are at runtime.

---

[Chapter 1: Everything Is an Object →](chapter-01-object-model.md)
