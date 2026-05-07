# Chapter 9: "Write Tests"

[← Chapter 8: Type Hints](chapter-08-type-hints.md) | [Chapter 10: File I/O →](chapter-10-file-io.md)

---

## The Mandate

Monday standup. Leo is serious:

> "Nothing ships without tests. I don't care if it's a one-line fix — if there's no test, it doesn't get merged. Marcus spent three hours debugging a regression last week that a single test would have caught. We're using pytest. Learn it. Love it."

Rina: "Also, I need to know the bot actually handles edge cases. Users send... creative inputs."

---

## pytest: The Basics

```bash
# Install
pip install pytest pytest-cov

# Run tests
pytest                    # find and run all tests
pytest tests/             # run tests in a directory
pytest tests/test_bot.py  # run a specific file
pytest -v                 # verbose output
pytest -x                 # stop on first failure
```

### Your First Test

```python
# tests/test_message.py
from pulsebot.message import Message


def test_extract_command():
    msg = Message({"text": "status", "user": "leo", "channel": "#support"})
    assert msg.extract_command() == "status"


def test_extract_command_with_args():
    msg = Message({"text": "deploy production", "user": "leo", "channel": "#ops"})
    assert msg.extract_command() == "deploy"


def test_extract_command_empty():
    msg = Message({"text": "", "user": "leo", "channel": "#support"})
    assert msg.extract_command() is None


def test_mentions_bot():
    msg = Message({"text": "hey @pulsebot status", "user": "rina", "channel": "#general"})
    assert msg.mentions_bot("pulsebot") is True
    assert msg.mentions_bot("otherbot") is False
```

### Test Naming Convention

```
tests/
├── test_message.py       # tests for message.py
├── test_handlers.py      # tests for handlers.py
├── test_config.py        # tests for config.py
└── conftest.py           # shared fixtures
```

- Files start with `test_`
- Functions start with `test_`
- Classes start with `Test`

---

## Assertions: What to Check

```python
# Equality
assert result == "expected"
assert count == 42

# Truthiness
assert user.is_admin
assert not ticket.is_closed

# Identity
assert result is None
assert result is not None

# Containment
assert "error" in log_output
assert "leo" in admins
assert "secret" not in response_body

# Type
assert isinstance(result, Ticket)

# Exceptions
import pytest

def test_invalid_priority():
    with pytest.raises(ValueError, match="must be one of"):
        Ticket(title="Bug", reporter="leo", priority="urgent")

def test_missing_token():
    with pytest.raises(KeyError):
        Config.from_dict({})  # no "token" key
```

### Approximate Comparisons

```python
# Floating point
assert 0.1 + 0.2 == pytest.approx(0.3)

# With tolerance
assert response_time == pytest.approx(0.2, abs=0.05)  # 0.15 to 0.25
```

---

## Fixtures: Shared Setup

```python
# tests/conftest.py
import pytest
from pulsebot.bot import Bot
from pulsebot.config import BotConfig


@pytest.fixture
def config() -> BotConfig:
    """Test configuration — no real tokens."""
    return BotConfig(
        token="xoxb-test-token",
        name="TestBot",
        channels=["#test"],
        admins=["leo", "marcus"],
    )


@pytest.fixture
def bot(config) -> Bot:
    """A configured bot instance."""
    return Bot(config=config)


@pytest.fixture
def sample_message() -> dict:
    """A typical Slack message payload."""
    return {
        "text": "status",
        "user": "leo",
        "channel": "#support",
        "ts": "1700000000.000001",
    }
```

### Using Fixtures

```python
# tests/test_bot.py

def test_bot_handles_status(bot, sample_message):
    """Fixtures are injected by name."""
    result = bot.handle(sample_message)
    assert result == "✅ All systems operational"


def test_bot_unknown_command(bot):
    msg = {"text": "explode", "user": "leo", "channel": "#test"}
    result = bot.handle(msg)
    assert "unknown" in result.lower() or result is None
```

### Fixture Scopes

```python
@pytest.fixture(scope="session")
def database():
    """Created once for the entire test session."""
    db = create_test_database()
    yield db
    db.drop()  # cleanup after all tests


@pytest.fixture(scope="module")
def api_client():
    """Created once per test file."""
    return TestAPIClient()


@pytest.fixture  # default scope="function"
def ticket():
    """Created fresh for each test."""
    return Ticket(title="Test", reporter="test-user")
```

| Scope | Created | Destroyed |
|---|---|---|
| `function` | Each test | After each test |
| `class` | Each test class | After class |
| `module` | Each test file | After file |
| `session` | Once | After all tests |

---

## Parametrize: Test Many Inputs

```python
import pytest


@pytest.mark.parametrize("text,expected_command", [
    ("status", "status"),
    ("deploy production", "deploy"),
    ("HELP", "help"),
    ("  spaces  ", "spaces"),
    ("", None),
])
def test_extract_command(text, expected_command):
    msg = Message({"text": text, "user": "leo", "channel": "#test"})
    assert msg.extract_command() == expected_command


@pytest.mark.parametrize("priority,valid", [
    ("low", True),
    ("medium", True),
    ("high", True),
    ("critical", True),
    ("urgent", False),
    ("", False),
    ("LOW", False),  # case-sensitive
])
def test_priority_validation(priority, valid):
    if valid:
        ticket = Ticket(title="Bug", reporter="leo", priority=priority)
        assert ticket.priority == priority
    else:
        with pytest.raises(ValueError):
            Ticket(title="Bug", reporter="leo", priority=priority)
```

---

## Mocking: Fake External Dependencies

The bot calls Slack's API. Tests shouldn't make real HTTP requests.

```python
from unittest.mock import Mock, patch, MagicMock


# Mock an object
def test_bot_sends_response():
    mock_client = Mock()
    mock_client.send_message.return_value = {"ok": True}
    
    bot = Bot(client=mock_client, config=test_config)
    bot.respond("#support", "Hello!")
    
    mock_client.send_message.assert_called_once_with(
        channel="#support",
        text="Hello!"
    )


# Patch a module-level function
@patch("pulsebot.handlers.requests.get")
def test_status_handler_api_down(mock_get):
    mock_get.side_effect = ConnectionError("timeout")
    
    handler = StatusHandler(config={})
    result = handler.handle({"text": "status", "user": "leo"})
    
    assert "unavailable" in result.lower()


# Patch with context manager
def test_config_from_env():
    env = {"SLACK_TOKEN": "xoxb-test", "BOT_NAME": "TestBot"}
    
    with patch.dict("os.environ", env):
        config = Config.from_env()
        assert config.token == "xoxb-test"
        assert config.name == "TestBot"
```

### Mock Return Values and Side Effects

```python
mock_api = Mock()

# Return a fixed value
mock_api.get_user.return_value = {"name": "Leo", "admin": True}

# Return different values on successive calls
mock_api.fetch.side_effect = [
    {"messages": [{"text": "hello"}]},
    {"messages": []},
]

# Raise an exception
mock_api.connect.side_effect = ConnectionError("refused")

# Custom function
mock_api.process.side_effect = lambda x: x.upper()
```

---

## Testing Async Code

```python
import pytest
import asyncio


@pytest.mark.asyncio
async def test_async_handler():
    handler = AsyncStatusHandler()
    result = await handler.handle({"text": "status"})
    assert result == "✅ All systems operational"


@pytest.mark.asyncio
async def test_concurrent_handlers():
    handlers = [AsyncHandler() for _ in range(5)]
    results = await asyncio.gather(
        *[h.handle({"text": "ping"}) for h in handlers]
    )
    assert all(r == "pong" for r in results)
```

Install: `pip install pytest-asyncio`

---

## Coverage: What's Tested?

```bash
# Run with coverage
pytest --cov=pulsebot --cov-report=term-missing

# Output:
# Name                    Stmts   Miss  Cover   Missing
# -----------------------------------------------------
# pulsebot/bot.py            45      3    93%   67-69
# pulsebot/handlers.py       32      0   100%
# pulsebot/message.py        18      2    89%   41-42
# -----------------------------------------------------
# TOTAL                      95      5    95%

# Generate HTML report
pytest --cov=pulsebot --cov-report=html
# Open htmlcov/index.html in browser
```

### pyproject.toml Coverage Config

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=pulsebot --cov-report=term-missing"

[tool.coverage.run]
branch = true
source = ["pulsebot"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "if TYPE_CHECKING:",
]
```

---

## Test Organization: The PulseBot Suite

```python
# tests/test_handlers.py
import pytest
from unittest.mock import Mock, patch
from pulsebot.handlers import StatusHandler, DeployHandler, TicketHandler


class TestStatusHandler:
    """All tests for the status command."""

    def test_returns_ok_when_healthy(self, config):
        handler = StatusHandler(config)
        with patch("pulsebot.handlers.check_health") as mock:
            mock.return_value = True
            assert "operational" in handler.handle({"text": "status"})

    def test_returns_warning_when_degraded(self, config):
        handler = StatusHandler(config)
        with patch("pulsebot.handlers.check_health") as mock:
            mock.return_value = False
            assert "degraded" in handler.handle({"text": "status"}).lower()


class TestDeployHandler:
    """All tests for the deploy command."""

    def test_admin_can_deploy(self, config):
        handler = DeployHandler(config)
        assert handler.can_execute("leo") is True

    def test_non_admin_cannot_deploy(self, config):
        handler = DeployHandler(config)
        assert handler.can_execute("random-user") is False

    def test_deploy_triggers_pipeline(self, config):
        handler = DeployHandler(config)
        with patch("pulsebot.handlers.trigger_deploy") as mock:
            mock.return_value = {"status": "started", "id": "deploy-123"}
            result = handler.handle({"text": "deploy production", "user": "leo"})
            assert "deploy-123" in result
            mock.assert_called_once_with("production")
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command / Pattern               │ Purpose
────────────────────────────────┼──────────────────────────────────────
pytest                          │ Run all tests
pytest -x                       │ Stop on first failure
pytest -k "status"              │ Run tests matching name
pytest --cov=pkg                │ Measure coverage
────────────────────────────────┼──────────────────────────────────────
assert x == y                   │ Equality check
pytest.raises(Error)            │ Expect an exception
pytest.approx(val)              │ Float comparison
────────────────────────────────┼──────────────────────────────────────
@pytest.fixture                 │ Shared test setup
@pytest.mark.parametrize        │ Test multiple inputs
@pytest.mark.asyncio            │ Test async functions
────────────────────────────────┼──────────────────────────────────────
Mock()                          │ Fake object
@patch("module.func")           │ Replace function in tests
mock.return_value = x           │ Set return value
mock.side_effect = Error()      │ Make it raise
mock.assert_called_once_with()  │ Verify it was called
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The tests pass. Coverage is at 94%. Leo is happy. Then Rina walks over: "Can the bot export ticket data to a CSV? And read its config from a YAML file instead of hardcoded dicts?" Time to learn file I/O.

---

[← Chapter 8: Type Hints](chapter-08-type-hints.md) | [Chapter 10: File I/O →](chapter-10-file-io.md)
