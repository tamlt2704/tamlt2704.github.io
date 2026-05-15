# Chapter 1: Everything Is an Object

[← Chapter 0: Before You Start](chapter-00-overview.md) | [Chapter 2: Decorators That Write Code →](chapter-02-decorators.md)

---

## The Problem

Your first week at FrameForge. Vera drops by your desk.

"Leo wrote a plugin system. It uses `isinstance()` checks everywhere and breaks when someone subclasses a handler. Before you fix it, I need you to understand something fundamental: in Python, **everything** is an object. Classes, functions, modules — all objects. Once you internalize that, the rest of metaprogramming clicks."

You open a REPL and start poking.

## Objects All the Way Down

```python
# Numbers are objects
>>> type(42)
<class 'int'>

# Strings are objects
>>> type("hello")
<class 'str'>

# Functions are objects
>>> def greet(name):
...     return f"Hello, {name}"
>>> type(greet)
<class 'function'>

# Classes are objects
>>> type(int)
<class 'type'>

# And here's the mind-bender:
>>> type(type)
<class 'type'>
```

That last line. `type` is an instance of itself. This is the foundation of Python's object model.

## The Three Questions

For any Python object, you can always ask:

```python
>>> x = 42

# 1. What IS it? (its type)
>>> type(x)
<class 'int'>

# 2. WHERE is it? (its identity)
>>> id(x)
140234866357040

# 3. What CAN it do? (its attributes)
>>> dir(x)
['__abs__', '__add__', '__and__', ...]
```

## Functions Are First-Class Objects

This is where it gets useful. Functions are objects, which means you can:

```python
# Store them in variables
handler = greet

# Put them in data structures
dispatch = {
    "greet": greet,
    "farewell": lambda name: f"Goodbye, {name}",
}

# Pass them as arguments
def apply(func, value):
    return func(value)

apply(greet, "Vera")  # "Hello, Vera"

# Return them from other functions
def make_greeter(greeting):
    def greeter(name):
        return f"{greeting}, {name}"
    return greeter

spanish_greet = make_greeter("Hola")
spanish_greet("Vera")  # "Hola, Vera"
```

This isn't a curiosity — it's the foundation of decorators (Chapter 2) and closures (Chapter 9).

## Classes Are Callable Objects

A class is just a callable that returns an instance:

```python
class User:
    def __init__(self, name):
        self.name = name

# These are equivalent:
u1 = User("Alice")
u2 = User.__call__("Alice")  # Don't actually write this

# A class is an object you can pass around:
def create_instance(cls, *args, **kwargs):
    """Factory that works with ANY class."""
    print(f"Creating {cls.__name__} with {args}")
    return cls(*args, **kwargs)

user = create_instance(User, "Alice")
# Creating User with ('Alice',)
```

## type() — The Dual Nature

`type()` does two completely different things depending on how you call it:

```python
# With ONE argument: returns the type of an object
>>> type(42)
<class 'int'>
>>> type("hello")
<class 'str'>

# With THREE arguments: CREATES a new class
>>> MyClass = type('MyClass', (object,), {'x': 42})
>>> MyClass.x
42
>>> obj = MyClass()
>>> type(obj)
<class '__main__.MyClass'>
```

The three-argument form is: `type(name, bases, namespace)`

- `name`: the class name (string)
- `bases`: tuple of parent classes
- `namespace`: dict of attributes and methods

## Creating Classes Dynamically

Here's the key insight. When you write:

```python
class Dog:
    species = "Canis familiaris"

    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says woof!"
```

Python translates that to roughly:

```python
def __init__(self, name):
    self.name = name

def bark(self):
    return f"{self.name} says woof!"

Dog = type('Dog', (object,), {
    'species': 'Canis familiaris',
    '__init__': __init__,
    'bark': bark,
})
```

The `class` statement is syntactic sugar for calling `type()`.

## The FrameForge Use Case

Leo's plugin system hardcodes handler classes. You want to generate them dynamically:

```python
# The verbose way — writing each handler class by hand:
class JsonHandler:
    format = "json"
    def parse(self, data):
        import json
        return json.loads(data)

class XmlHandler:
    format = "xml"
    def parse(self, data):
        from xml.etree import ElementTree
        return ElementTree.fromstring(data)

class CsvHandler:
    format = "csv"
    def parse(self, data):
        import csv, io
        return list(csv.reader(io.StringIO(data)))
```

With `type()`, you can generate these from a config:

```python
import json, csv, io
from xml.etree import ElementTree

PARSERS = {
    "json": lambda self, data: json.loads(data),
    "xml": lambda self, data: ElementTree.fromstring(data),
    "csv": lambda self, data: list(csv.reader(io.StringIO(data))),
}

def make_handler_class(format_name, parse_func):
    """Dynamically create a handler class."""
    return type(
        f"{format_name.title()}Handler",  # class name
        (object,),                         # bases
        {
            "format": format_name,
            "parse": parse_func,
            "__repr__": lambda self: f"<{format_name.title()}Handler>",
        }
    )

# Generate all handler classes from config
handlers = {
    name: make_handler_class(name, func)
    for name, func in PARSERS.items()
}

# Use them:
h = handlers["json"]()
h.parse('{"key": "value"}')  # {'key': 'value'}
type(h)  # <class '__main__.JsonHandler'>
```

Three classes generated from a dictionary. No repetition.

## isinstance() and the Type Hierarchy

```python
>>> isinstance(42, int)
True
>>> isinstance(42, object)
True  # Everything inherits from object

>>> isinstance(int, type)
True  # Classes are instances of type

>>> isinstance(type, object)
True  # type inherits from object

>>> isinstance(object, type)
True  # object is an instance of type
```

The circular relationship between `type` and `object` is bootstrapped by CPython at startup. Don't worry about it — just know that `type` creates classes, and all classes are objects.

## issubclass() vs isinstance()

```python
# isinstance: is this OBJECT an instance of this CLASS?
>>> isinstance(42, int)
True

# issubclass: is this CLASS a subclass of this other CLASS?
>>> issubclass(bool, int)
True
>>> issubclass(int, object)
True

# Common mistake:
>>> issubclass(42, int)
TypeError: issubclass() arg 1 must be a class
```

## The __class__ Attribute

Every object knows its own type:

```python
>>> (42).__class__
<class 'int'>
>>> "hello".__class__
<class 'str'>

# You can even change it (don't do this in production):
class A:
    def hello(self):
        return "I'm A"

class B:
    def hello(self):
        return "I'm B"

obj = A()
obj.hello()        # "I'm A"
obj.__class__ = B
obj.hello()        # "I'm B"  — same object, different class
```

## What You Learned

- **Everything in Python is an object** — integers, strings, functions, classes, modules
- **`type(x)`** returns the type of `x`; **`type(name, bases, dict)`** creates a new class
- **Classes are instances of `type`** — the `class` statement is sugar for `type()`
- **Functions are first-class** — store them, pass them, return them
- **`id()`** gives memory identity, **`isinstance()`** checks type relationships
- **Dynamic class creation** with `type()` eliminates repetitive class definitions

## Key Insight

> `type` is both a function (tells you what something is) and a metaclass (creates new classes). Every `class` statement secretly calls `type()`. Understanding this duality is the foundation for everything that follows.

Vera's voice in your head: "If classes are just objects created by `type()`, then we can intercept that creation process. That's what metaclasses do. But first — decorators."

---

[Chapter 2: Decorators That Write Code →](chapter-02-decorators.md)
