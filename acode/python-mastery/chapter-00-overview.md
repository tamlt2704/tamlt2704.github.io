# Python Mastery: A Startup Survival Story

You thought you'd be doing data entry. Then **Leo**, the CTO of **PulseBot** — a scrappy startup that builds Slack bots for customer support teams — sends you a message:

> "Our Python dev moved to Berlin. The codebase is yours now. Ship the next feature by Friday."

You show up. The codebase is a single 2,000-line file called `bot.py`. No tests. No types. A function called `do_stuff()` that's 400 lines long. A comment that says `# TODO: fix this later (2019)`.

Your mission: understand Python from the ground up, refactor the chaos, build new features, and ship production code. Before the demo on Friday.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | The New Dev | "I know print('hello')... that counts, right?" |
| **Leo** | CTO | Draws architecture on whiteboards. Speaks in abstractions. |
| **Rina** | Product Manager | "Can we just add one more thing?" (It's never one thing.) |
| **Marcus** | Senior Dev (remote) | Reviews PRs at midnight. Leaves cryptic one-line comments. |
| **Dani** | Designer | "The CLI output needs to be ✨ pretty ✨." |
| **The Bot** | PulseBot itself | Crashes every Tuesday. No one knows why. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **Python 3.12+** | The language |
| **pip / uv** | Package management |
| **pytest** | Testing |
| **mypy** | Type checking |
| **ruff** | Linting and formatting |

```bash
# Install Python (if not already)
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt install python3.12 python3.12-venv

# Windows
winget install Python.Python.3.12

# Verify
python3 --version
```

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Rina or Leo assigns a task
   │
   ▼
  🤔 You learn the Python concept needed
   │
   ▼
  ⌨️  You write the code
   │
   ▼
  💥 Something breaks or behaves unexpectedly
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  📋 Next task arrives
```

No concept shows up before you need it. You won't hear about decorators until you need to add logging to every function. You won't touch async until the bot needs to handle 50 Slack messages simultaneously.

The bugs come first. The Python follows.

---

## The Roadmap

### Part 1: Foundations — "Make It Work"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Read the codebase"                    │ Variables, types, strings, numbers, booleans
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "Parse the config file"                │ Lists, dicts, tuples, sets, comprehensions
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Handle the edge cases"                │ Control flow: if/elif/else, for, while, match
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Break up do_stuff()"                  │ Functions, args, kwargs, returns, scope
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "The bot crashes on bad input"         │ Exceptions, try/except, custom errors
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Structure — "Make It Clean"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Split into modules"                   │ Modules, packages, imports, __init__.py
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Model the domain"                     │ Classes, OOP, inheritance, composition
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Add type safety"                      │ Type hints, dataclasses, Protocols, mypy
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Write tests"                          │ pytest, fixtures, mocking, parametrize
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Read and write files"                 │ File I/O, pathlib, JSON, CSV, context managers
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Intermediate — "Make It Powerful"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Add logging to everything"            │ Decorators, closures, functools
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "Process 10,000 messages"              │ Generators, iterators, lazy evaluation
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "Handle 50 requests at once"           │ async/await, asyncio, aiohttp
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Build the CLI"                        │ argparse, click, rich, stdin/stdout
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Talk to the database"                 │ SQLAlchemy, connection pools, migrations
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Make It Ship"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Task                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "Build the HTTP API"                   │ FastAPI, Pydantic, routing, middleware
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Package and deploy"                   │ Virtual envs, pyproject.toml, Docker, CI
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "It's slow"                            │ Profiling, caching, multiprocessing, C extensions
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "Make it bulletproof"                  │ Logging, monitoring, graceful shutdown, signals
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ The Friday demo                        │ Design patterns, architecture, code review
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Codebase: What You Inherit

This is `bot.py` on day one. Leo wrote it in a weekend hackathon in 2019. It grew.

```python
# bot.py - PulseBot main file
# TODO: fix this later (2019)
import os, sys, json, time, random, requests

config = json.load(open("config.json"))
token = os.environ.get("SLACK_TOKEN") or config.get("token") or "no-token"

def do_stuff(msg):
    # handles everything
    if msg["type"] == "message":
        text = msg.get("text", "")
        if "help" in text.lower():
            return {"text": "I can help! Try: status, ticket, escalate"}
        elif "status" in text.lower():
            r = requests.get(config["status_url"])
            if r.status_code == 200:
                return {"text": f"All systems operational: {r.json()['status']}"}
            else:
                return {"text": "Status check failed"}
        elif "ticket" in text.lower():
            # create ticket... somehow
            return {"text": "Ticket created (maybe)"}
        # ... 350 more lines of elif
    return None

# main loop
while True:
    try:
        msgs = requests.get(f"https://slack.com/api/conversations.history",
                           headers={"Authorization": f"Bearer {token}"}).json()
        for m in msgs.get("messages", []):
            result = do_stuff(m)
            if result:
                requests.post("https://slack.com/api/chat.postMessage",
                            headers={"Authorization": f"Bearer {token}"},
                            json={"channel": m["channel"], "text": result["text"]})
    except Exception as e:
        print(f"error: {e}")
    time.sleep(5)
```

By Chapter 20, this will be a properly structured, typed, tested, async application with a CLI, an API, and a deployment pipeline. But first — you need to understand what you're looking at.

---

## Prerequisites

- **Python 3.12+** installed
- **A terminal** (any shell)
- **A text editor** (VS Code, PyCharm, vim — doesn't matter)
- **Willingness to break things** — every bug teaches you something

---

[Next: Chapter 1 — "Read the Codebase" →](chapter-01-variables-types.md)
