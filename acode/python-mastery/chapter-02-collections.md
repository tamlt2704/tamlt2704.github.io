# Chapter 2: "Parse the Config File"

[← Chapter 1: Variables & Types](chapter-01-variables-types.md) | [Chapter 3: Control Flow →](chapter-03-control-flow.md)

---

## The Task

Leo hands you `config.json`:

```json
{
  "bot_name": "PulseBot",
  "channels": ["#support", "#engineering", "#sales"],
  "commands": {
    "help": {"handler": "show_help", "admin_only": false},
    "status": {"handler": "check_status", "admin_only": false},
    "deploy": {"handler": "trigger_deploy", "admin_only": true}
  },
  "retry": {"max_attempts": 3, "backoff_seconds": [1, 5, 15]},
  "admins": ["leo", "marcus"]
}
```

"Parse it. Give me a way to access `config.commands.status.handler` without the code exploding if a key is missing."

You need to understand Python's four core collections.

---

## Lists: Ordered, Mutable Sequences

```python
channels = ["#support", "#engineering", "#sales"]

# Access by index (0-based)
channels[0]       # "#support"
channels[-1]      # "#sales" (last item)

# Modify
channels.append("#ops")           # add to end
channels.insert(0, "#general")    # add at position
channels.remove("#sales")         # remove by value
popped = channels.pop()           # remove and return last item

# Length
len(channels)     # number of items

# Check membership
"#support" in channels    # True

# Slice (returns a new list)
channels[1:3]     # ["#engineering", "#sales"]
```

### List Methods

```python
numbers = [3, 1, 4, 1, 5, 9]

numbers.sort()                # [1, 1, 3, 4, 5, 9] — modifies in place
sorted(numbers)               # returns new sorted list (original unchanged)
numbers.reverse()             # reverses in place
numbers.count(1)              # 2 (how many times 1 appears)
numbers.index(4)              # 2 (first index of value 4)
numbers.extend([2, 6])        # add multiple items

# Copy (shallow)
copy = numbers[:]             # or numbers.copy()
```

### Iterating

```python
for channel in channels:
    print(channel)

# With index
for i, channel in enumerate(channels):
    print(f"{i}: {channel}")

# With enumerate starting at 1
for num, channel in enumerate(channels, start=1):
    print(f"{num}. {channel}")
```

---

## Dictionaries: Key-Value Pairs

The most important collection in Python. JSON maps directly to dicts.

```python
command = {
    "handler": "check_status",
    "admin_only": False,
    "cooldown": 5
}

# Access
command["handler"]          # "check_status"
command["missing"]          # KeyError! 💥
command.get("missing")      # None (safe)
command.get("missing", 0)   # 0 (safe with default)

# Modify
command["timeout"] = 30     # add new key
command["cooldown"] = 10    # update existing
del command["cooldown"]     # remove key
popped = command.pop("timeout", None)  # remove and return (or default)

# Check
"handler" in command        # True (checks keys, not values)
```

### Dict Methods

```python
config = {"name": "PulseBot", "version": 3, "debug": True}

config.keys()       # dict_keys(["name", "version", "debug"])
config.values()     # dict_values(["PulseBot", 3, True])
config.items()      # dict_items([("name", "PulseBot"), ("version", 3), ...])

# Merge (Python 3.9+)
defaults = {"timeout": 30, "debug": False}
settings = defaults | config   # config values override defaults
# → {"timeout": 30, "debug": True, "name": "PulseBot", "version": 3}

# Update in place
defaults.update(config)
```

### Iterating Dicts

```python
# Keys (default)
for key in config:
    print(key)

# Key-value pairs
for key, value in config.items():
    print(f"{key} = {value}")

# Only values
for value in config.values():
    print(value)
```

### Nested Access (Leo's Problem)

```python
import json

with open("config.json") as f:
    config = json.load(f)

# ❌ Dangerous: crashes if any key is missing
handler = config["commands"]["status"]["handler"]

# ✅ Safe: chain .get() calls
handler = config.get("commands", {}).get("status", {}).get("handler")
# Returns None if any level is missing

# ✅ Even safer: helper function
def deep_get(d, *keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return default
    return d if d is not None else default

handler = deep_get(config, "commands", "status", "handler")
# → "check_status"

missing = deep_get(config, "commands", "nonexistent", "handler", default="unknown")
# → "unknown"
```

---

## Tuples: Immutable Sequences

Like lists, but can't be changed after creation. Used for fixed collections.

```python
# Create
point = (10, 20)
rgb = (255, 128, 0)
single = (42,)        # trailing comma needed for single-element tuple

# Access (same as lists)
point[0]              # 10
point[-1]             # 20

# Can't modify
point[0] = 5          # TypeError!

# Unpacking
x, y = point          # x=10, y=20
r, g, b = rgb         # r=255, g=128, b=0

# Swap values (tuple unpacking trick)
a, b = b, a

# Return multiple values from a function
def get_status():
    return "ok", 200   # returns a tuple

status, code = get_status()
```

### When to Use Tuples vs Lists

| Use Tuple | Use List |
|---|---|
| Fixed data (coordinates, RGB) | Collection that grows/shrinks |
| Dict keys (tuples are hashable) | Ordered items you'll modify |
| Function return values | Sequences you'll sort/filter |
| Data you don't want accidentally changed | Mutable sequences |

---

## Sets: Unique, Unordered

```python
admins = {"leo", "marcus"}
online = {"leo", "dani", "rina"}

# Operations
admins & online          # {"leo"} — intersection (who's admin AND online)
admins | online          # {"leo", "marcus", "dani", "rina"} — union
admins - online          # {"marcus"} — difference (admins not online)
online - admins          # {"dani", "rina"} — non-admins who are online

# Membership (O(1) — fast!)
"leo" in admins          # True

# Modify
admins.add("you")
admins.remove("marcus")  # KeyError if missing
admins.discard("ghost")  # no error if missing

# Deduplicate a list
channels = ["#support", "#support", "#eng", "#eng", "#sales"]
unique = list(set(channels))  # ["#support", "#eng", "#sales"] (order not guaranteed)
```

---

## Comprehensions: One-Line Transformations

The Pythonic way to create collections from other collections.

### List Comprehension

```python
# Traditional loop
upper_channels = []
for ch in channels:
    upper_channels.append(ch.upper())

# Comprehension (same result, one line)
upper_channels = [ch.upper() for ch in channels]

# With filter
admin_commands = [cmd for cmd, info in commands.items() if info["admin_only"]]

# Nested
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### Dict Comprehension

```python
# Invert a dict
commands = {"help": "show_help", "status": "check_status"}
handlers = {v: k for k, v in commands.items()}
# → {"show_help": "help", "check_status": "status"}

# Filter a dict
admin_only = {k: v for k, v in config["commands"].items() if v["admin_only"]}

# Transform values
prices_dollars = {item: cents / 100 for item, cents in prices_cents.items()}
```

### Set Comprehension

```python
# Unique first characters
first_chars = {ch[0] for ch in channels}  # {"#"}
```

### Generator Expression (Lazy)

```python
# Parentheses instead of brackets — doesn't create the full list in memory
total = sum(order["amount"] for order in orders)
any_admin = any(user in admins for user in online_users)
```

---

## Putting It Together: Parsing the Config

```python
import json
from pathlib import Path


def load_config(path: str = "config.json") -> dict:
    """Load and validate the bot configuration."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with open(config_path) as f:
        config = json.load(f)

    # Validate required keys
    required = ["bot_name", "channels", "commands"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Missing config keys: {missing}")

    return config


def get_command(config: dict, command_name: str) -> dict | None:
    """Safely get a command's configuration."""
    return config.get("commands", {}).get(command_name)


def is_admin(config: dict, username: str) -> bool:
    """Check if a user is in the admin list."""
    return username in set(config.get("admins", []))


# Usage
config = load_config()
print(f"Bot: {config['bot_name']}")
print(f"Channels: {', '.join(config['channels'])}")

status_cmd = get_command(config, "status")
if status_cmd:
    print(f"Status handler: {status_cmd['handler']}")

print(f"Leo is admin: {is_admin(config, 'leo')}")
```

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────
Collection          │ Properties
────────────────────┼──────────────────────────────────────────────
list []             │ Ordered, mutable, allows duplicates
dict {}             │ Key-value pairs, mutable, keys unique
tuple ()            │ Ordered, immutable, allows duplicates
set {}              │ Unordered, mutable, no duplicates
────────────────────┼──────────────────────────────────────────────
list.append(x)      │ Add to end
list.pop()          │ Remove and return last
dict.get(k, default)│ Safe access with fallback
dict.items()        │ Key-value pairs for iteration
set & set           │ Intersection
set | set           │ Union
────────────────────┼──────────────────────────────────────────────
[x for x in iter]   │ List comprehension
{k: v for ...}      │ Dict comprehension
{x for x in iter}   │ Set comprehension
(x for x in iter)   │ Generator expression (lazy)
────────────────────┴──────────────────────────────────────────────
```

---

## What's Next

Rina walks over. "The bot needs to handle different message types differently. If it's a DM, respond immediately. If it's in a channel, check if the bot was mentioned. If the user is an admin, allow dangerous commands. Oh, and retry up to 3 times on failure."

That's control flow — if/else, loops, and pattern matching.

---

[← Chapter 1: Variables & Types](chapter-01-variables-types.md) | [Chapter 3: Control Flow →](chapter-03-control-flow.md)
