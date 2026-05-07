# Chapter 3: "Handle the Edge Cases"

[← Chapter 2: Collections](chapter-02-collections.md) | [Chapter 4: Functions →](chapter-04-functions.md)

---

## The Task

Rina's requirements:

1. If it's a DM → respond immediately
2. If it's in a channel → only respond if the bot was mentioned
3. If the user is an admin → allow dangerous commands
4. Retry failed API calls up to 3 times with increasing delay
5. Handle different message types: text, file upload, reaction, thread reply

Derek's `bot.py` handles all of this with 47 nested `if/elif/else` blocks. Time to learn control flow properly.

---

## if / elif / else

```python
message_type = "channel"
user = "leo"
admins = {"leo", "marcus"}

if message_type == "dm":
    print("Responding to DM")
elif message_type == "channel" and user in admins:
    print("Admin message in channel")
elif message_type == "channel":
    print("Regular channel message")
else:
    print("Unknown message type")
```

### Conditions Are Expressions

```python
# Ternary (inline if/else)
response = "allowed" if user in admins else "denied"

# Equivalent to:
if user in admins:
    response = "allowed"
else:
    response = "denied"
```

### Truthy/Falsy in Conditions

```python
messages = []
text = ""
count = 0
result = None

# All of these are False:
if messages:    pass  # empty list → False
if text:        pass  # empty string → False
if count:       pass  # zero → False
if result:      pass  # None → False

# Pythonic checks:
if not messages:
    print("No messages to process")

# ❌ Don't do this:
if len(messages) == 0:    # works but not Pythonic
if messages == []:        # works but not Pythonic
if result == None:        # use `is None` instead
```

### Combining Conditions

```python
# and, or, not
if user in admins and message_type == "channel":
    allow_command()

if priority == "critical" or priority == "high":
    escalate()

# Cleaner with `in`:
if priority in ("critical", "high"):
    escalate()

# Negation
if not is_authenticated:
    reject()
```

---

## for Loops

```python
# Iterate over a list
channels = ["#support", "#engineering", "#sales"]
for channel in channels:
    print(f"Joining {channel}")

# Iterate over a dict
commands = {"help": "show_help", "status": "check_status"}
for name, handler in commands.items():
    print(f"/{name} → {handler}")

# Iterate over a range
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 11):     # 1 through 10
    print(i)

for i in range(0, 20, 5):  # 0, 5, 10, 15 (step of 5)
    print(i)
```

### enumerate: Index + Value

```python
for i, channel in enumerate(channels):
    print(f"{i}: {channel}")
# 0: #support
# 1: #engineering
# 2: #sales
```

### zip: Parallel Iteration

```python
names = ["Leo", "Rina", "Marcus"]
roles = ["CTO", "PM", "Senior Dev"]

for name, role in zip(names, roles):
    print(f"{name} is {role}")
# Leo is CTO
# Rina is PM
# Marcus is Senior Dev
```

### break and continue

```python
# break: stop the loop entirely
for msg in messages:
    if msg["type"] == "shutdown":
        print("Shutting down")
        break
    process(msg)

# continue: skip this iteration, go to next
for msg in messages:
    if msg.get("bot_message"):
        continue  # skip bot's own messages
    process(msg)
```

### for/else (Unusual but Useful)

```python
# else runs if the loop completed WITHOUT break
for user in users:
    if user["name"] == "leo":
        print("Found Leo!")
        break
else:
    print("Leo not found")  # only runs if break was never hit
```

---

## while Loops

```python
# Retry with backoff (Rina's requirement #4)
attempts = 0
max_attempts = 3
backoff = [1, 5, 15]

while attempts < max_attempts:
    try:
        response = call_api()
        break  # success — exit loop
    except ConnectionError:
        attempts += 1
        if attempts < max_attempts:
            wait = backoff[attempts - 1]
            print(f"Retry {attempts}/{max_attempts} in {wait}s...")
            time.sleep(wait)
        else:
            print("All retries exhausted")
            raise
```

### Infinite Loop with Break

```python
# The bot's main loop (cleaned up from Derek's version)
while True:
    messages = fetch_messages()
    for msg in messages:
        handle(msg)
    time.sleep(5)
    
    if shutdown_requested:
        break
```

---

## match/case (Python 3.10+): Structural Pattern Matching

Derek's 47 `elif` blocks? Pattern matching handles this cleanly:

```python
def handle_message(msg: dict) -> str | None:
    match msg:
        case {"type": "message", "subtype": "bot_message"}:
            return None  # ignore bot messages

        case {"type": "message", "text": text, "channel_type": "im"}:
            # DM — always respond
            return process_dm(text)

        case {"type": "message", "text": text} if "@pulsebot" in text.lower():
            # Channel message mentioning the bot
            return process_mention(text)

        case {"type": "message", "files": [*files]}:
            # File upload
            return process_files(files)

        case {"type": "reaction_added", "reaction": emoji}:
            return f"Someone reacted with :{emoji}:"

        case _:
            return None  # unhandled message type
```

### Pattern Matching Basics

```python
# Match on value
match status_code:
    case 200:
        print("OK")
    case 404:
        print("Not found")
    case 500 | 502 | 503:  # OR pattern
        print("Server error")
    case _:
        print(f"Unknown: {status_code}")

# Match on structure (destructuring)
match point:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"On x-axis at {x}")
    case (0, y):
        print(f"On y-axis at {y}")
    case (x, y):
        print(f"Point at ({x}, {y})")

# Match with guard (if condition)
match command:
    case {"name": name, "admin_only": True} if user not in admins:
        print(f"Permission denied for {name}")
    case {"name": name, "handler": handler}:
        run_handler(handler)
```

---

## Practical: The Message Router

Putting it all together — replacing Derek's 47 `elif` blocks:

```python
import time


def route_message(msg: dict, config: dict, user: str) -> str | None:
    """Route an incoming message to the appropriate handler."""
    
    # Skip bot's own messages
    if msg.get("subtype") == "bot_message":
        return None

    # Only respond in channels if mentioned
    if msg.get("channel_type") != "im" and f"@{config['bot_name'].lower()}" not in msg.get("text", "").lower():
        return None

    text = msg.get("text", "").strip().lower()
    
    # Extract command (first word after mention)
    command = extract_command(text)
    if not command:
        return None

    # Check permissions
    cmd_config = config.get("commands", {}).get(command)
    if cmd_config is None:
        return f"Unknown command: {command}. Try 'help'."

    if cmd_config.get("admin_only") and user not in config.get("admins", []):
        return f"Permission denied. '{command}' requires admin access."

    # Route to handler
    match command:
        case "help":
            available = [name for name, info in config["commands"].items()
                        if not info.get("admin_only") or user in config.get("admins", [])]
            return f"Available commands: {', '.join(available)}"
        case "status":
            return check_status(config)
        case "deploy" if user in config.get("admins", []):
            return trigger_deploy()
        case _:
            return f"Command '{command}' not yet implemented."


def extract_command(text: str) -> str | None:
    """Extract the command name from message text."""
    # Remove bot mention if present
    words = text.replace("@pulsebot", "").strip().split()
    return words[0] if words else None


def check_status_with_retry(url: str, max_attempts: int = 3) -> dict:
    """Check status endpoint with exponential backoff."""
    backoff = [1, 5, 15]
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_attempts - 1:
                raise
            wait = backoff[attempt]
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
```

---

## Walrus Operator `:=` (Python 3.8+)

Assign and test in one expression:

```python
# Without walrus
line = input()
while line != "quit":
    process(line)
    line = input()

# With walrus
while (line := input()) != "quit":
    process(line)

# Useful in comprehensions
results = [clean for raw in data if (clean := raw.strip())]

# Useful in if statements
if (match := re.search(r"ticket-(\d+)", text)):
    ticket_id = match.group(1)
```

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────
Pattern             │ Use When
────────────────────┼──────────────────────────────────────────────
if/elif/else        │ 2-4 conditions, simple checks
match/case          │ Complex structure matching, many branches
for x in iterable   │ Process each item in a collection
while condition     │ Loop until something changes
break               │ Exit loop early
continue            │ Skip to next iteration
for/else            │ "Did we find it?" pattern
x if cond else y    │ Inline conditional (ternary)
:= (walrus)         │ Assign + test in one expression
────────────────────┴──────────────────────────────────────────────
```

---

## What's Next

Marcus reviews your code. His comment: "This `route_message` function is 40 lines. `check_status_with_retry` duplicates retry logic. Extract functions. Make them composable."

Time to learn functions properly — arguments, return values, scope, and how to break big logic into small, reusable pieces.

---

[← Chapter 2: Collections](chapter-02-collections.md) | [Chapter 4: Functions →](chapter-04-functions.md)
