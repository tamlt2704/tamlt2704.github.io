# Chapter 10: "Read and Write Files"

[← Chapter 9: Testing](chapter-09-testing.md) | [Chapter 11: Decorators →](chapter-11-decorators.md)

---

## The Request

Rina, in the #product channel:

> "Two things. First: I need a CSV export of all tickets so I can share them with the support team in a spreadsheet. Second: the bot config is hardcoded in a Python dict. Can we move it to a YAML file so I can change settings without asking a developer?"

You: "Sure, I'll—"

Rina: "Also JSON. Some of our integrations send JSON. And the log files are plain text. So... all the file formats."

---

## Reading Files: The Basics

```python
# ❌ Old way — easy to forget to close
f = open("config.yaml")
content = f.read()
f.close()  # what if an exception happens before this?

# ✅ Context manager — always closes the file
with open("config.yaml") as f:
    content = f.read()
# f is closed here, even if an exception occurred

# Read modes
with open("data.txt", "r") as f:       # text mode (default)
    text = f.read()

with open("image.png", "rb") as f:     # binary mode
    data = f.read()
```

### Reading Strategies

```python
# Read entire file as string
with open("README.md") as f:
    content = f.read()

# Read line by line (memory efficient for large files)
with open("access.log") as f:
    for line in f:
        if "ERROR" in line:
            print(line.strip())

# Read all lines into a list
with open("users.txt") as f:
    users = f.read().splitlines()  # no trailing \n

# Read first N lines
with open("huge.log") as f:
    head = [next(f) for _ in range(10)]
```

---

## Writing Files

```python
# Write (creates or overwrites)
with open("output.txt", "w") as f:
    f.write("Bot started at 2024-01-15\n")
    f.write("Watching 3 channels\n")

# Append (adds to end)
with open("bot.log", "a") as f:
    f.write(f"[{timestamp}] Message processed\n")

# Write multiple lines
lines = ["channel: #support", "channel: #engineering", "channel: #random"]
with open("channels.txt", "w") as f:
    f.writelines(line + "\n" for line in lines)
```

---

## pathlib: Modern File Paths

```python
from pathlib import Path

# Create paths
config_dir = Path("config")
config_file = config_dir / "bot.yaml"       # config/bot.yaml
data_file = Path("data") / "tickets.csv"    # data/tickets.csv

# Path properties
print(config_file.name)       # "bot.yaml"
print(config_file.stem)       # "bot"
print(config_file.suffix)     # ".yaml"
print(config_file.parent)     # Path("config")

# Check existence
if config_file.exists():
    content = config_file.read_text()

if not data_file.parent.exists():
    data_file.parent.mkdir(parents=True)

# Read and write (shorthand)
text = Path("config.yaml").read_text()
Path("output.txt").write_text("done")
data = Path("image.png").read_bytes()

# List files
for py_file in Path("src").glob("**/*.py"):
    print(py_file)

# Iterate directory
for item in Path("data").iterdir():
    if item.is_file():
        print(f"File: {item.name} ({item.stat().st_size} bytes)")
```

### Path Operations

```python
from pathlib import Path

project = Path("/home/dev/pulsebot")

# Join paths
handler_file = project / "src" / "handlers.py"

# Resolve relative paths
relative = Path("../config/bot.yaml")
absolute = relative.resolve()  # /home/dev/config/bot.yaml

# Home directory
home = Path.home()  # /home/dev
config = home / ".pulsebot" / "config.yaml"

# Current working directory
cwd = Path.cwd()
```

---

## JSON: API Data

```python
import json
from pathlib import Path


# Read JSON
def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)

# Or with pathlib
config = json.loads(Path("config.json").read_text())


# Write JSON
def save_state(state: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

# Pretty print
data = {"bot": "PulseBot", "channels": ["#support", "#eng"], "version": 3}
print(json.dumps(data, indent=2))
# {
#   "bot": "PulseBot",
#   "channels": ["#support", "#eng"],
#   "version": 3
# }
```

### Handling JSON Edge Cases

```python
from datetime import datetime
from dataclasses import dataclass, asdict


# Custom serialization (datetime isn't JSON-serializable)
class BotEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

data = {"started": datetime.now(), "name": "PulseBot"}
json.dumps(data, cls=BotEncoder)
# '{"started": "2024-01-15T10:30:00", "name": "PulseBot"}'


# Dataclass to JSON
@dataclass
class Ticket:
    title: str
    reporter: str
    priority: str

ticket = Ticket("Bot crashes", "leo", "high")
json.dumps(asdict(ticket))
# '{"title": "Bot crashes", "reporter": "leo", "priority": "high"}'
```

---

## CSV: Spreadsheet Data

Rina's ticket export:

```python
import csv
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Ticket:
    id: str
    title: str
    reporter: str
    priority: str
    status: str


def export_tickets(tickets: list[Ticket], path: Path) -> None:
    """Export tickets to CSV for the support team."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Title", "Reporter", "Priority", "Status"])
        for ticket in tickets:
            writer.writerow([
                ticket.id, ticket.title, ticket.reporter,
                ticket.priority, ticket.status
            ])


def import_tickets(path: Path) -> list[Ticket]:
    """Import tickets from CSV."""
    tickets = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(Ticket(
                id=row["ID"],
                title=row["Title"],
                reporter=row["Reporter"],
                priority=row["Priority"],
                status=row["Status"],
            ))
    return tickets
```

### CSV with DictWriter

```python
def export_metrics(metrics: list[dict], path: Path) -> None:
    """Export bot metrics to CSV."""
    fieldnames = ["timestamp", "command", "user", "response_time_ms"]
    
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics)


# Reading back
with open("metrics.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['command']} took {row['response_time_ms']}ms")
```

---

## YAML: Configuration Files

```bash
pip install pyyaml
```

The new `config.yaml`:

```yaml
# config.yaml
bot:
  name: PulseBot
  token: ${SLACK_TOKEN}  # we'll resolve env vars
  
channels:
  - "#support"
  - "#engineering"
  - "#random"

commands:
  status:
    enabled: true
    cooldown_seconds: 30
  deploy:
    enabled: true
    admin_only: true
    
admins:
  - leo
  - marcus
```

```python
import yaml
import os
from pathlib import Path


def load_config(path: Path) -> dict:
    """Load YAML config with environment variable substitution."""
    raw = path.read_text()
    
    # Simple env var substitution
    for key, value in os.environ.items():
        raw = raw.replace(f"${{{key}}}", value)
    
    return yaml.safe_load(raw)


# Usage
config = load_config(Path("config.yaml"))
print(config["bot"]["name"])          # "PulseBot"
print(config["channels"])             # ["#support", "#engineering", "#random"]
print(config["commands"]["deploy"])   # {"enabled": True, "admin_only": True}
```

### Writing YAML

```python
def save_state(state: dict, path: Path) -> None:
    """Save bot state to YAML."""
    with open(path, "w") as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)

state = {
    "last_message_ts": "1700000000.000001",
    "active_tickets": 12,
    "handlers_loaded": ["status", "deploy", "ticket"],
}
save_state(state, Path("state.yaml"))
```

---

## Context Managers: Custom Cleanup

```python
from contextlib import contextmanager
from pathlib import Path
import tempfile
import shutil


@contextmanager
def temp_directory():
    """Create a temp directory, clean up when done."""
    path = Path(tempfile.mkdtemp())
    try:
        yield path
    finally:
        shutil.rmtree(path)


# Usage
with temp_directory() as tmp:
    export_file = tmp / "tickets.csv"
    export_tickets(tickets, export_file)
    upload_to_slack(export_file)
# tmp directory is deleted here


@contextmanager
def atomic_write(path: Path):
    """Write to a temp file, then rename — prevents partial writes."""
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w") as f:
            yield f
        tmp_path.rename(path)  # atomic on most filesystems
    except:
        tmp_path.unlink(missing_ok=True)  # clean up on failure
        raise


# Usage — config is never half-written
with atomic_write(Path("config.yaml")) as f:
    yaml.dump(config, f)
```

---

## Putting It Together: The Export Feature

```python
import csv
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Ticket:
    id: str
    title: str
    reporter: str
    priority: str
    status: str
    created_at: str


class TicketExporter:
    """Export tickets in multiple formats."""

    def __init__(self, tickets: list[Ticket]):
        self.tickets = tickets

    def to_csv(self, path: Path) -> None:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=Ticket.__dataclass_fields__.keys())
            writer.writeheader()
            writer.writerows(asdict(t) for t in self.tickets)

    def to_json(self, path: Path) -> None:
        data = [asdict(t) for t in self.tickets]
        path.write_text(json.dumps(data, indent=2))

    def to_yaml(self, path: Path) -> None:
        data = [asdict(t) for t in self.tickets]
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


# Usage in the bot
def handle_export_command(format: str, tickets: list[Ticket]) -> Path:
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exporter = TicketExporter(tickets)
    
    match format:
        case "csv":
            path = export_dir / f"tickets_{timestamp}.csv"
            exporter.to_csv(path)
        case "json":
            path = export_dir / f"tickets_{timestamp}.json"
            exporter.to_json(path)
        case "yaml":
            path = export_dir / f"tickets_{timestamp}.yaml"
            exporter.to_yaml(path)
        case _:
            raise ValueError(f"Unknown format: {format}")
    
    return path
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Operation                       │ Code
────────────────────────────────┼──────────────────────────────────────
Read text file                  │ Path("f.txt").read_text()
Write text file                 │ Path("f.txt").write_text(s)
Read with context manager       │ with open("f") as f: f.read()
Append to file                  │ open("f", "a")
────────────────────────────────┼──────────────────────────────────────
Path join                       │ Path("dir") / "file.txt"
Check exists                    │ path.exists()
Create directory                │ path.mkdir(parents=True)
List files                      │ path.glob("**/*.py")
────────────────────────────────┼──────────────────────────────────────
Read JSON                       │ json.load(f) / json.loads(s)
Write JSON                      │ json.dump(obj, f, indent=2)
Read CSV                        │ csv.DictReader(f)
Write CSV                       │ csv.DictWriter(f, fields)
Read YAML                       │ yaml.safe_load(f)
Write YAML                      │ yaml.dump(obj, f)
────────────────────────────────┼──────────────────────────────────────
@contextmanager                 │ Custom with-block cleanup
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The export works. Rina is happy. But Marcus notices something in the PR: "Every handler has the same logging boilerplate at the top. Timing code, error logging, permission checks — all duplicated. Learn decorators. Add logging to every handler without modifying them."

---

[← Chapter 9: Testing](chapter-09-testing.md) | [Chapter 11: Decorators →](chapter-11-decorators.md)
