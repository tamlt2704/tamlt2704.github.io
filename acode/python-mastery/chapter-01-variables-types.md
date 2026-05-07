# Chapter 1: "Read the Codebase"

[← Overview](chapter-00-overview.md) | [Chapter 2: Collections →](chapter-02-collections.md)

---

## The Task

First morning. Leo points at your screen. "Read `bot.py`. Understand what it does. Then explain it to me in 5 minutes."

You open the file. 2,000 lines. No comments (except the 2019 TODO). Variables named `x`, `r`, `tmp2`. You need to understand Python's building blocks before you can understand this mess.

Let's start with what things ARE in Python.

---

## Variables: Names for Things

```python
name = "PulseBot"
version = 3.2
is_running = True
max_retries = 5
```

A variable is a name that points to a value. No type declaration needed — Python figures it out.

```python
# You can reassign to a different type (dynamic typing)
x = 42        # int
x = "hello"   # now it's a str — Python doesn't complain
```

This flexibility is why Derek's `bot.py` is chaos. No one knows what type anything is. We'll fix that with type hints in Chapter 8.

### Naming Conventions

```python
# ✅ Python style (snake_case)
user_name = "Leo"
max_retry_count = 3
is_active = True

# ❌ Not Python style
userName = "Leo"      # camelCase (Java/JS)
MaxRetryCount = 3     # PascalCase (reserved for classes)
```

---

## Types: What Things Are

Python has a handful of built-in types. Everything else is built from these.

### Numbers

```python
# Integers (no size limit in Python)
count = 42
big_number = 1_000_000  # underscores for readability

# Floats (decimal numbers)
price = 29.99
ratio = 0.75

# Arithmetic
total = price * count          # 1259.58
remainder = 10 % 3             # 1 (modulo)
power = 2 ** 10                # 1024 (exponentiation)
integer_div = 7 // 2           # 3 (floor division)
```

⚠️ **Float trap**: `0.1 + 0.2 == 0.3` is `False` in Python (and every language). Floating point is approximate. For money, use integers (cents) or `decimal.Decimal`.

```python
from decimal import Decimal
price = Decimal("29.99")  # exact
```

### Strings

Strings are text. Immutable (can't change in place).

```python
name = "PulseBot"
greeting = 'Hello'          # single or double quotes — same thing
multiline = """This is
a multiline
string"""

# String operations
len(name)                    # 8
name.upper()                 # "PULSEBOT"
name.lower()                 # "pulsebot"
name.startswith("Pulse")     # True
name.replace("Bot", "AI")   # "PulseAI" (returns new string)
"bot" in name.lower()        # True
```

### f-strings: String Formatting

```python
user = "Leo"
tickets = 7

# f-string (Python 3.6+) — the modern way
message = f"Hey {user}, you have {tickets} open tickets."

# Expressions inside braces
message = f"Total: ${tickets * 15.99:.2f}"  # "Total: $111.93"

# Multiline f-string
report = f"""
Customer: {user}
Tickets:  {tickets}
Status:   {"critical" if tickets > 5 else "normal"}
"""
```

### Booleans

```python
is_active = True
is_deleted = False

# Truthy and falsy values
bool(0)         # False
bool("")        # False
bool([])        # False (empty list)
bool(None)      # False
bool(42)        # True
bool("hello")   # True
bool([1, 2])    # True (non-empty list)
```

**Rule**: In Python, empty things are falsy. Non-empty things are truthy. This matters for `if` checks:

```python
messages = []
if messages:          # False — list is empty
    process(messages)
if not messages:      # True
    print("No messages")
```

### None: The Absence of Value

```python
result = None  # "no value yet"

# Check for None with `is`, not `==`
if result is None:
    print("No result")

if result is not None:
    print(f"Got: {result}")
```

`None` is Python's null. Functions that don't explicitly return something return `None`.

---

## Type Checking at Runtime

```python
x = 42
type(x)              # <class 'int'>
isinstance(x, int)   # True
isinstance(x, str)   # False

# Check multiple types
isinstance(x, (int, float))  # True
```

---

## Operators

### Comparison

```python
5 == 5      # True (equality)
5 != 3      # True (not equal)
5 > 3       # True
5 >= 5      # True
5 < 10      # True

# Chaining (Python-specific, very readable)
1 < x < 10  # True if x is between 1 and 10
```

### Logical

```python
True and False   # False
True or False    # True
not True         # False

# Short-circuit evaluation
name = user_input or "Anonymous"  # if user_input is falsy, use "Anonymous"
```

### Identity vs Equality

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b    # True (same value)
a is b    # False (different objects in memory)
a is c    # True (same object)
```

Use `==` for value comparison. Use `is` only for `None`, `True`, `False`.

---

## String Methods You'll Use Daily

```python
text = "  Hello, World!  "

text.strip()              # "Hello, World!" (remove whitespace)
text.split(",")           # ["  Hello", " World!  "]
text.replace("World", "Python")  # "  Hello, Python!  "

# Join a list into a string
words = ["hello", "world"]
" ".join(words)           # "hello world"
", ".join(words)          # "hello, world"

# Check content
"hello" in text.lower()   # True
text.startswith("  H")    # True
text.endswith("!  ")      # True
text.isdigit()            # False
"42".isdigit()            # True
```

### Slicing

```python
s = "PulseBot"
s[0]      # "P" (first character)
s[-1]     # "t" (last character)
s[0:5]    # "Pulse" (index 0 to 4)
s[5:]     # "Bot" (index 5 to end)
s[:5]     # "Pulse" (start to index 4)
s[::2]    # "PlBt" (every 2nd character)
s[::-1]   # "toBesluP" (reversed)
```

---

## Type Conversion

```python
# String to number
int("42")        # 42
float("3.14")    # 3.14
int("hello")     # ValueError!

# Number to string
str(42)          # "42"
str(3.14)        # "3.14"

# Safe conversion
text = "maybe_a_number"
try:
    value = int(text)
except ValueError:
    value = 0
```

---

## Reading Leo's Code

Now you can parse `bot.py`:

```python
token = os.environ.get("SLACK_TOKEN") or config.get("token") or "no-token"
```

Translation:
1. Try to get `SLACK_TOKEN` from environment variables
2. If that's `None` (falsy), try `config.get("token")`
3. If that's also `None`, use `"no-token"`

This is the `or` short-circuit pattern. First truthy value wins.

```python
text = msg.get("text", "")
```

`.get("text", "")` — get the "text" key from the dict, or `""` if it doesn't exist. Safer than `msg["text"]` which crashes on missing keys.

```python
if r.status_code == 200:
```

Integer comparison. HTTP 200 = success.

```python
return {"text": f"All systems operational: {r.json()['status']}"}
```

Returns a dictionary with one key. The f-string interpolates the `status` field from the JSON response.

You explain it to Leo. He nods. "Good. Now parse the config file. It's a mess."

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────
Type                │ Example
────────────────────┼──────────────────────────────────────────────
int                 │ 42, 1_000_000, -5
float               │ 3.14, 0.001, -2.5
str                 │ "hello", 'world', f"{name}"
bool                │ True, False
None                │ None (absence of value)
────────────────────┼──────────────────────────────────────────────
f"text {expr}"      │ String interpolation
str.strip()         │ Remove whitespace
str.split(sep)      │ Split into list
sep.join(list)      │ Join list into string
str[start:end]      │ Slicing
────────────────────┼──────────────────────────────────────────────
==, !=, <, >, <=, >=│ Comparison
and, or, not        │ Logical operators
is, is not          │ Identity (use for None)
in, not in          │ Membership test
────────────────────┴──────────────────────────────────────────────
```

---

## What's Next

Leo: "The config file has nested settings, lists of channels, and a mapping of commands to handlers. You need to parse it, validate it, and make it accessible throughout the app."

That's collections — lists, dicts, tuples, sets. The data structures that hold everything together.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Collections →](chapter-02-collections.md)
