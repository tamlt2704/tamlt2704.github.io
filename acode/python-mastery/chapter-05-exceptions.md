# Chapter 5: "The Bot Crashes on Bad Input"

[← Chapter 4: Functions](chapter-04-functions.md) | [Chapter 6: Modules →](chapter-06-modules.md)

---

## The Incident

Tuesday. The bot crashes. Again. The error log:

```
Traceback (most recent call last):
  File "bot.py", line 47, in handle_message
    text = msg["text"]
KeyError: 'text'

During handling of the above exception, another exception occurred:
  File "bot.py", line 12, in main_loop
    result = handle_message(msg)
TypeError: 'NoneType' object is not subscriptable
```

A user sent a message with no `text` field (it was a file upload). The bot tried to access `msg["text"]`, got a `KeyError`, and the entire process died.

Leo: "The bot should never crash on bad input. Handle errors gracefully. Log them. Keep running."

---

## try / except: Catching Errors

```python
# ❌ Crashes on missing key
text = msg["text"]

# ✅ Handle the error
try:
    text = msg["text"]
except KeyError:
    text = ""  # safe fallback
```

### Multiple Exception Types

```python
try:
    response = requests.get(url, timeout=10)
    data = response.json()
    value = data["results"][0]["value"]
except requests.ConnectionError:
    print("Cannot reach the server")
    value = None
except requests.Timeout:
    print("Request timed out")
    value = None
except (KeyError, IndexError) as e:
    print(f"Unexpected response structure: {e}")
    value = None
```

### The Full try Block

```python
try:
    # Code that might fail
    result = risky_operation()
except SpecificError as e:
    # Handle specific error
    log_error(e)
    result = fallback_value
except Exception as e:
    # Catch-all (use sparingly)
    log_error(e)
    raise  # re-raise after logging
else:
    # Runs ONLY if no exception occurred
    save_result(result)
finally:
    # ALWAYS runs (cleanup)
    close_connection()
```

| Block | When It Runs |
|---|---|
| `try` | Always (the code you're protecting) |
| `except` | Only if an exception matches |
| `else` | Only if NO exception occurred |
| `finally` | ALWAYS (even if exception propagates) |

---

## Exception Hierarchy

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ValueError        (wrong value: int("hello"))
    ├── TypeError         (wrong type: len(42))
    ├── KeyError          (missing dict key: d["x"])
    ├── IndexError        (list index out of range)
    ├── AttributeError    (obj.missing_attr)
    ├── FileNotFoundError (open("nope.txt"))
    ├── IOError           (disk/network I/O failure)
    ├── RuntimeError      (generic runtime error)
    └── ... many more
```

**Rule**: Catch specific exceptions. Never bare `except:` (catches everything including `KeyboardInterrupt`).

```python
# ❌ Too broad — hides bugs, catches Ctrl+C
try:
    do_work()
except:
    pass

# ❌ Still too broad for most cases
try:
    do_work()
except Exception:
    pass

# ✅ Specific
try:
    do_work()
except (ConnectionError, TimeoutError) as e:
    handle_network_error(e)
```

---

## Raising Exceptions

```python
def set_priority(priority: str) -> None:
    valid = ("low", "medium", "high", "critical")
    if priority not in valid:
        raise ValueError(f"Invalid priority '{priority}'. Must be one of: {valid}")
    # ... set it

# Calling code
try:
    set_priority("urgent")
except ValueError as e:
    print(e)  # "Invalid priority 'urgent'. Must be one of: ..."
```

### Re-raising

```python
try:
    result = call_api()
except ConnectionError as e:
    log.error(f"API call failed: {e}")
    raise  # re-raise the same exception (preserves traceback)

# Or raise a different exception with context
try:
    data = json.loads(raw_text)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid config format") from e
```

`from e` chains the exceptions — the original error is preserved in the traceback.

---

## Custom Exceptions

For your application's specific error cases:

```python
class BotError(Exception):
    """Base exception for PulseBot."""
    pass


class CommandNotFoundError(BotError):
    """Raised when a command doesn't exist."""
    def __init__(self, command: str):
        self.command = command
        super().__init__(f"Unknown command: '{command}'")


class PermissionDeniedError(BotError):
    """Raised when a user lacks permission."""
    def __init__(self, user: str, command: str):
        self.user = user
        self.command = command
        super().__init__(f"User '{user}' cannot run '{command}'")


class APIError(BotError):
    """Raised when an external API call fails."""
    def __init__(self, url: str, status_code: int, body: str = ""):
        self.url = url
        self.status_code = status_code
        self.body = body
        super().__init__(f"API error {status_code} from {url}")
```

### Using Custom Exceptions

```python
def execute_command(command: str, user: str, config: dict) -> str:
    cmd_config = config.get("commands", {}).get(command)
    if cmd_config is None:
        raise CommandNotFoundError(command)
    
    if cmd_config.get("admin_only") and user not in config.get("admins", []):
        raise PermissionDeniedError(user, command)
    
    return run_handler(cmd_config["handler"])


# Caller handles gracefully
def handle_message(msg: dict, config: dict) -> str:
    try:
        return execute_command(msg["command"], msg["user"], config)
    except CommandNotFoundError as e:
        return f"❌ {e.command} is not a valid command. Try 'help'."
    except PermissionDeniedError as e:
        return f"🔒 Sorry, '{e.command}' requires admin access."
    except APIError as e:
        return f"⚠️ External service error (HTTP {e.status_code}). Try again later."
```

---

## Patterns: Graceful Error Handling

### Pattern 1: Default on Failure

```python
def safe_get_status(url: str) -> str:
    """Always returns a string, never crashes."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json().get("status", "unknown")
    except requests.RequestException:
        return "unavailable"
```

### Pattern 2: Collect Errors, Don't Stop

```python
def process_messages(messages: list[dict]) -> tuple[list[str], list[str]]:
    """Process all messages, collecting successes and errors."""
    results = []
    errors = []
    
    for msg in messages:
        try:
            result = handle_message(msg)
            results.append(result)
        except BotError as e:
            errors.append(f"Message {msg.get('id')}: {e}")
    
    return results, errors
```

### Pattern 3: Context Manager for Cleanup

```python
# Ensures file is closed even if an error occurs
with open("config.json") as f:
    config = json.load(f)
# f is automatically closed here, even if json.load() raises

# Ensures database connection is returned to pool
with db.connection() as conn:
    conn.execute("INSERT INTO ...")
# connection is released here, even on error
```

### Pattern 4: Logging + Re-raise

```python
import logging

logger = logging.getLogger(__name__)

def critical_operation():
    try:
        result = do_important_thing()
    except Exception as e:
        logger.exception(f"Critical operation failed: {e}")
        raise  # let it propagate after logging
    return result
```

`logger.exception()` automatically includes the full traceback.

---

## The Fixed Bot: Never Crashes

```python
import logging
import time

logger = logging.getLogger("pulsebot")


def main_loop(config: dict) -> None:
    """Main bot loop — runs forever, never crashes on message errors."""
    logger.info(f"PulseBot starting. Watching {len(config['channels'])} channels.")
    
    while True:
        try:
            messages = fetch_messages(config)
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch messages: {e}")
            time.sleep(30)  # back off on network errors
            continue
        
        for msg in messages:
            try:
                response = handle_message(msg, config)
                if response:
                    send_response(msg["channel"], response, config)
            except BotError as e:
                logger.warning(f"Handler error: {e}")
                # Don't crash — skip this message and continue
            except Exception as e:
                logger.exception(f"Unexpected error processing message: {e}")
                # Still don't crash — but log the full traceback
        
        time.sleep(5)


if __name__ == "__main__":
    try:
        config = load_config()
        main_loop(config)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise
```

The bot handles three levels:
1. **Network errors** → back off and retry
2. **Message handling errors** → log and skip the message
3. **Fatal errors** → log and exit cleanly

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ When to Use
────────────────────────────────┼──────────────────────────────────────
try/except SpecificError        │ Handle known failure modes
except Exception as e           │ Catch-all (log + re-raise)
raise ValueError("msg")         │ Signal invalid input
raise CustomError() from e      │ Chain exceptions (preserve context)
else (after except)             │ Code that runs only on success
finally                         │ Cleanup (always runs)
────────────────────────────────┼──────────────────────────────────────
class MyError(Exception)        │ Custom exception for your domain
logger.exception(msg)           │ Log with full traceback
with open(...) as f:            │ Auto-cleanup on error
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The bot works. It doesn't crash. But it's still one file — `bot.py` is now 800 lines of well-structured code, but it's still one file. Marcus: "Split it into modules. Handlers in one file, config in another, API client separate."

Time to learn Python's module system.

---

[← Chapter 4: Functions](chapter-04-functions.md) | [Chapter 6: Modules →](chapter-06-modules.md)
