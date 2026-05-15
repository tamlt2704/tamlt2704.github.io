# Chapter 11: AST Manipulation

[← Chapter 10: The Import System](chapter-10-imports.md) | [Chapter 12: Concurrency →](chapter-12-concurrency.md)

---

## The Problem

FrameForge needs to generate Python code from JSON schemas. Users provide a schema, and the framework produces validated dataclasses. The naive approach: string templates.

```python
# String-based code generation — fragile and error-prone
def generate_class_from_schema(schema):
    name = schema["name"]
    fields = schema["fields"]

    code = f"class {name}:\n"
    code += f"    def __init__(self, {', '.join(f['name'] for f in fields)}):\n"
    for field in fields:
        code += f"        self.{field['name']} = {field['name']}\n"

    return code

# Problems:
# - No syntax validation until exec()
# - Indentation errors are invisible
# - Special characters in names break everything
# - No way to inspect or transform the generated code
```

Leo tried this. It works for simple cases. Then someone puts a quote in a field name and everything explodes.

Vera: "Don't generate strings. Generate syntax trees. The `ast` module lets you build Python code as a data structure — validated, transformable, correct by construction."

## The AST Module

Python can parse source code into an Abstract Syntax Tree:

```python
import ast

# Parse source code into a tree:
tree = ast.parse("""
x = 42
y = x + 1
print(y)
""")

# Inspect the tree:
print(ast.dump(tree, indent=2))
# Module(body=[
#   Assign(targets=[Name(id='x')], value=Constant(value=42)),
#   Assign(targets=[Name(id='y')], value=BinOp(left=Name(id='x'), op=Add(), right=Constant(value=1))),
#   Expr(value=Call(func=Name(id='print'), args=[Name(id='y')]))
# ])
```

## Building AST Nodes

Instead of string concatenation, build the tree programmatically:

```python
import ast

def make_assignment(name, value):
    """Create: name = value"""
    return ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store())],
        value=ast.Constant(value=value),
        lineno=0, col_offset=0
    )

def make_function(name, params, body_stmts):
    """Create a function definition."""
    return ast.FunctionDef(
        name=name,
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=p) for p in params],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=body_stmts,
        decorator_list=[],
        lineno=0, col_offset=0
    )

# Build a function:
func = make_function("greet", ["name"], [
    ast.Return(
        value=ast.JoinedStr(values=[
            ast.Constant(value="Hello, "),
            ast.FormattedValue(
                value=ast.Name(id="name", ctx=ast.Load()),
                conversion=-1
            ),
        ]),
        lineno=0, col_offset=0
    )
])
```

## Solution: Code Generator from JSON Schema

```python
import ast
import json

def generate_dataclass_from_schema(schema):
    """Generate a validated dataclass from a JSON schema.

    Schema format:
    {
        "name": "User",
        "fields": [
            {"name": "username", "type": "str", "min_length": 3},
            {"name": "age", "type": "int", "min_value": 0, "max_value": 150},
            {"name": "email", "type": "str", "pattern": ".*@.*"}
        ]
    }
    """
    class_name = schema["name"]
    fields = schema["fields"]

    # Build __init__ method
    init_params = ["self"] + [f["name"] for f in fields]
    init_body = []

    for field in fields:
        fname = field["name"]
        ftype = field["type"]

        # Type check
        init_body.append(_make_type_check(fname, ftype))

        # Range validation
        if "min_value" in field:
            init_body.append(_make_min_check(fname, field["min_value"]))
        if "max_value" in field:
            init_body.append(_make_max_check(fname, field["max_value"]))
        if "min_length" in field:
            init_body.append(_make_min_length_check(fname, field["min_length"]))

        # Assignment
        init_body.append(ast.Assign(
            targets=[ast.Attribute(
                value=ast.Name(id="self", ctx=ast.Load()),
                attr=fname, ctx=ast.Store()
            )],
            value=ast.Name(id=fname, ctx=ast.Load()),
            lineno=0, col_offset=0
        ))

    init_method = ast.FunctionDef(
        name="__init__",
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=p) for p in init_params],
            kwonlyargs=[], kw_defaults=[], defaults=[]
        ),
        body=init_body,
        decorator_list=[],
        lineno=0, col_offset=0
    )

    # Build __repr__ method
    repr_method = _make_repr(class_name, [f["name"] for f in fields])

    # Build the class
    class_def = ast.ClassDef(
        name=class_name,
        bases=[],
        keywords=[],
        body=[init_method, repr_method],
        decorator_list=[],
        lineno=0, col_offset=0
    )

    # Wrap in a module, fix locations, compile, execute
    module = ast.Module(body=[class_def], type_ignores=[])
    ast.fix_missing_locations(module)

    code = compile(module, f"<generated:{class_name}>", "exec")
    namespace = {}
    exec(code, namespace)
    return namespace[class_name]


def _make_type_check(name, type_str):
    """Generate: if not isinstance(name, type): raise TypeError(...)"""
    type_map = {"str": "str", "int": "int", "float": "float", "bool": "bool"}
    return ast.If(
        test=ast.UnaryOp(
            op=ast.Not(),
            operand=ast.Call(
                func=ast.Name(id="isinstance", ctx=ast.Load()),
                args=[
                    ast.Name(id=name, ctx=ast.Load()),
                    ast.Name(id=type_map[type_str], ctx=ast.Load()),
                ],
                keywords=[]
            )
        ),
        body=[ast.Raise(
            exc=ast.Call(
                func=ast.Name(id="TypeError", ctx=ast.Load()),
                args=[ast.Constant(value=f"{name} must be {type_str}")],
                keywords=[]
            )
        )],
        orelse=[],
        lineno=0, col_offset=0
    )


def _make_min_check(name, min_val):
    """Generate: if name < min_val: raise ValueError(...)"""
    return ast.If(
        test=ast.Compare(
            left=ast.Name(id=name, ctx=ast.Load()),
            ops=[ast.Lt()],
            comparators=[ast.Constant(value=min_val)]
        ),
        body=[ast.Raise(
            exc=ast.Call(
                func=ast.Name(id="ValueError", ctx=ast.Load()),
                args=[ast.Constant(value=f"{name} must be >= {min_val}")],
                keywords=[]
            )
        )],
        orelse=[],
        lineno=0, col_offset=0
    )


def _make_max_check(name, max_val):
    return ast.If(
        test=ast.Compare(
            left=ast.Name(id=name, ctx=ast.Load()),
            ops=[ast.Gt()],
            comparators=[ast.Constant(value=max_val)]
        ),
        body=[ast.Raise(exc=ast.Call(
            func=ast.Name(id="ValueError", ctx=ast.Load()),
            args=[ast.Constant(value=f"{name} must be <= {max_val}")],
            keywords=[]
        ))],
        orelse=[],
        lineno=0, col_offset=0
    )


def _make_min_length_check(name, min_len):
    return ast.If(
        test=ast.Compare(
            left=ast.Call(
                func=ast.Name(id="len", ctx=ast.Load()),
                args=[ast.Name(id=name, ctx=ast.Load())],
                keywords=[]
            ),
            ops=[ast.Lt()],
            comparators=[ast.Constant(value=min_len)]
        ),
        body=[ast.Raise(exc=ast.Call(
            func=ast.Name(id="ValueError", ctx=ast.Load()),
            args=[ast.Constant(value=f"{name} must be at least {min_len} characters")],
            keywords=[]
        ))],
        orelse=[],
        lineno=0, col_offset=0
    )


def _make_repr(class_name, field_names):
    """Generate __repr__ method."""
    # Build f-string: ClassName(field1={self.field1!r}, ...)
    values = [ast.Constant(value=f"{class_name}(")]
    for i, fname in enumerate(field_names):
        if i > 0:
            values.append(ast.Constant(value=", "))
        values.append(ast.Constant(value=f"{fname}="))
        values.append(ast.FormattedValue(
            value=ast.Attribute(
                value=ast.Name(id="self", ctx=ast.Load()),
                attr=fname, ctx=ast.Load()
            ),
            conversion=ord('r')
        ))
    values.append(ast.Constant(value=")"))

    return ast.FunctionDef(
        name="__repr__",
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg="self")],
            kwonlyargs=[], kw_defaults=[], defaults=[]
        ),
        body=[ast.Return(value=ast.JoinedStr(values=values))],
        decorator_list=[],
        lineno=0, col_offset=0
    )


# Usage:
schema = {
    "name": "User",
    "fields": [
        {"name": "username", "type": "str", "min_length": 3},
        {"name": "age", "type": "int", "min_value": 0, "max_value": 150},
        {"name": "email", "type": "str"},
    ]
}

User = generate_dataclass_from_schema(schema)
u = User("alice", 30, "alice@dev.io")
print(u)  # User(username='alice', age=30, email='alice@dev.io')

User("ab", 30, "x")  # ValueError: username must be at least 3 characters
User("alice", -1, "x")  # ValueError: age must be >= 0
User("alice", 200, "x")  # ValueError: age must be <= 150
```

## NodeVisitor: Analyzing Code

```python
import ast

class FunctionCounter(ast.NodeVisitor):
    """Count functions and their complexity."""

    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        self.functions.append({
            "name": node.name,
            "args": len(node.args.args),
            "lines": node.end_lineno - node.lineno + 1,
        })
        self.generic_visit(node)  # Visit child nodes

source = """
def simple():
    return 42

def complex_func(a, b, c):
    if a > b:
        for i in range(c):
            print(i)
    return a + b
"""

tree = ast.parse(source)
counter = FunctionCounter()
counter.visit(tree)
print(counter.functions)
# [{'name': 'simple', 'args': 0, 'lines': 2},
#  {'name': 'complex_func', 'args': 3, 'lines': 5}]
```

## NodeTransformer: Rewriting Code

```python
class AddLogging(ast.NodeTransformer):
    """Add print statements at the start of every function."""

    def visit_FunctionDef(self, node):
        log_stmt = ast.Expr(value=ast.Call(
            func=ast.Name(id="print", ctx=ast.Load()),
            args=[ast.Constant(value=f"Entering {node.name}")],
            keywords=[]
        ))
        ast.fix_missing_locations(log_stmt)
        node.body.insert(0, log_stmt)
        return node

source = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""

tree = ast.parse(source)
tree = AddLogging().visit(tree)
ast.fix_missing_locations(tree)

code = compile(tree, "<transformed>", "exec")
exec(code)
add(2, 3)  # prints "Entering add", returns 5
```

## Warning: When NOT to Use AST

AST manipulation is powerful but:
- **Hard to debug** — errors in generated code have no meaningful line numbers
- **Hard to read** — AST construction code is 10x longer than the code it generates
- **Fragile** — Python AST changes between versions
- **Overkill** — most code generation can use simpler techniques

**Use AST when:**
- Generating code from external schemas (OpenAPI, protobuf, GraphQL)
- Building source-to-source transformers (linters, formatters)
- Creating compile-time optimizations

**Don't use AST when:**
- A decorator or metaclass would work
- String formatting with `textwrap.dedent` is sufficient
- You're just trying to be clever

## What You Learned

- **`ast.parse()`** converts source code to a syntax tree
- **`ast.dump()`** shows the tree structure for debugging
- **`NodeVisitor`** walks the tree (read-only analysis)
- **`NodeTransformer`** walks and modifies the tree (rewriting)
- **`compile()` + `exec()`** turns an AST back into executable code
- **`ast.fix_missing_locations()`** fills in required line/column info
- **Code generation from schemas** is the primary real-world use case
- **AST is a last resort** — use simpler metaprogramming first

## Key Insight

> AST manipulation generates code at import time or build time. But what about runtime performance? When your elegant metaprogramming code needs to handle 100 concurrent HTTP requests, each taking 200ms, you can't process them sequentially. That's concurrency.

---

[Chapter 12: Concurrency Patterns →](chapter-12-concurrency.md)
