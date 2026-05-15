# Python Dark Arts — Write Less, Do More

A narrative-driven course on advanced Python techniques. You're a senior developer at a framework company where boilerplate is the enemy. Over 15 chapters, you'll bend Python to your will — one metaprogramming trick at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, Python's object model, the cast |
| 01 | [Everything Is an Object](chapter-01-object-model.md) | "What even IS a class?" | type(), id(), first-class everything |
| 02 | [Decorators That Write Code](chapter-02-decorators.md) | Same boilerplate wrapping 40 functions | Function decorators, @wraps, parameterized decorators |
| 03 | [Class Decorators](chapter-03-class-decorators.md) | Same 5 methods added to 20 classes | Class decorators, automatic method injection |
| 04 | [Descriptors: Reusable Properties](chapter-04-descriptors.md) | Validation logic copy-pasted everywhere | __get__, __set__, __set_name__, descriptor protocol |
| 05 | [Metaclasses: Classes That Build Classes](chapter-05-metaclasses.md) | Need auto-registration, validation at class creation | type as metaclass, __new__, __init_subclass__ |
| 06 | [__getattr__ and Dynamic Dispatch](chapter-06-dynamic-attrs.md) | Proxy objects, lazy loading, API wrappers | __getattr__, __getattribute__, __missing__ |
| 07 | [Context Managers Beyond Files](chapter-07-context-managers.md) | Resource cleanup, timing, transactions | __enter__/__exit__, contextlib, generator-based |
| 08 | [Generators and Lazy Pipelines](chapter-08-generators.md) | Processing 10GB without loading into memory | yield, generator expressions, itertools, lazy chains |
| 09 | [Closures and Factory Functions](chapter-09-closures.md) | Creating families of similar functions | Closures, nonlocal, function factories, partial |
| 10 | [The Import System](chapter-10-imports.md) | Plugin discovery, lazy imports, import hooks | __import__, importlib, sys.meta_path, lazy modules |
| 11 | [AST Manipulation](chapter-11-ast.md) | Auto-generating code from schemas | ast module, code generation, source transformation |
| 12 | [Concurrency Patterns](chapter-12-concurrency.md) | I/O-bound tasks blocking the main thread | asyncio, async generators, concurrent.futures |
| 13 | [Type System Tricks](chapter-13-typing.md) | Runtime validation from type hints | get_type_hints, TypeVar, Protocol, runtime checking |
| 14 | [Performance: Write Less, Run Faster](chapter-14-performance.md) | Code is elegant but slow | __slots__, lru_cache, struct, memoryview, C extensions |
| 15 | [Building a Mini-Framework](chapter-15-framework.md) | Putting it all together | Declarative API, auto-wiring, zero-boilerplate |

## Prerequisites

- Python 3.11+
- Solid understanding of classes, functions, and modules
- Comfort reading Python source code

## Philosophy

Every technique is introduced because writing the obvious way produced too much code. No metaprogramming without a boilerplate problem first. The verbose version comes first. The elegant version follows.
