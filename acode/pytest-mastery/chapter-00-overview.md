# Pytest Mastery: Tests That Actually Catch Bugs

You just became the tech lead at **Ledgerly** — a fintech startup building an invoicing and payments platform. The codebase has 40,000 lines of Python, zero tests, and a deployment history that reads like a horror novel. Last month, a billing bug charged 200 customers twice. The month before, a timezone issue sent invoices at 3 AM. Nobody caught either before production.

**Ava**, the CEO, lays down the law:

> "No more shipping without tests. I don't care if it slows us down for two weeks. Every new feature gets tested. Every bug fix gets a regression test. If it's not tested, it doesn't ship."

**Marcus**, the senior backend dev, is skeptical:

> "I've written tests before. They were slow, brittle, and nobody maintained them. They tested implementation details and broke every time we refactored. If we're doing this, we're doing it right — tests that catch real bugs, not tests that make us feel good."

You open pytest's docs. It looks simple — `assert` statements, no boilerplate. But the real power is in fixtures, parametrize, mocking, and knowing WHAT to test. Time to build a test suite that actually prevents production incidents.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Tech Lead | "Tests should catch bugs, not slow us down." |
| **Ava** | CEO | "If it shipped broken, it wasn't tested." |
| **Marcus** | Senior Backend | "I'll write tests when they're not a waste of time." |
| **The Billing Bug** | Production incident | Charged 200 customers twice. No test caught it. |
| **The Flaky Test** | CI nightmare | Passes locally, fails in CI. Nobody knows why. |
| **The Mock** | Test double | "I pretend to be the database. Don't trust me too much." |

---

## The Stack

| Tool | What It Does |
|---|---|
| **pytest** | Test framework (discovery, execution, assertions) |
| **pytest fixtures** | Setup/teardown, dependency injection for tests |
| **pytest.mark.parametrize** | Run one test with many inputs |
| **pytest-mock / unittest.mock** | Replace dependencies with fakes |
| **pytest-asyncio** | Test async code |
| **pytest-cov** | Code coverage reporting |
| **factory-boy** | Generate test data |
| **hypothesis** | Property-based testing |
| **testcontainers** | Real databases in tests |
| **freezegun** | Control time in tests |

---

## How to Read This

```
  🐛 A bug ships to production (or almost does)
   │
   ▼
  🤔 You learn the pytest technique that would have caught it
   │
   ▼
  ⌨️  You write the test (and the code it protects)
   │
   ▼
  💥 The test is slow, flaky, or tests the wrong thing
   │
   ▼
  🧠 You fix the test design — make it fast, reliable, and meaningful
   │
   ▼
  🐛 Next bug
```

---

## The Roadmap

### Part 1: Foundations — "Write Your First Tests"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Write a test that catches the bug"    │ assert, test discovery, running pytest
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "Test 15 cases without 15 functions"   │ parametrize — data-driven tests
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "I need a database for every test"     │ Fixtures — setup, teardown, scope
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Tests share setup code"               │ conftest.py, fixture composition
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Test that it raises an error"         │ pytest.raises, exception testing
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Real-World Testing — "Test Like Production"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Don't hit the real payment API"       │ Mocking — patch, MagicMock, when to mock
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Test the async endpoint"              │ pytest-asyncio, async fixtures
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Test with a real database"            │ Testcontainers, database fixtures
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "The timezone bug"                     │ freezegun, time-dependent tests
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Generate realistic test data"         │ factory-boy, fixtures at scale
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Advanced Patterns — "Tests That Scale"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Find bugs I didn't think of"          │ Hypothesis — property-based testing
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "Tests take 5 minutes"                 │ Parallelism, markers, test selection
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "The test passes alone, fails in CI"   │ Flaky tests, isolation, debugging
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Test the CLI / API end-to-end"        │ Integration tests, test client, fixtures
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Custom assertions and plugins"        │ Writing pytest plugins, custom markers
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "A Test Suite That Lasts"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "What should I even test?"             │ Testing strategy, test pyramid, ROI
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Coverage says 80% but bugs still ship"│ Meaningful coverage, mutation testing
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "Tests break every refactor"           │ Testing behavior not implementation
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "CI pipeline for tests"               │ pytest in CI, caching, reporting
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ "The test suite is an asset"           │ Maintenance, documentation, culture
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Why pytest (Not unittest)

Marcus asks: "Python has `unittest` built in. Why add a dependency?"

```python
# unittest — verbose, class-based, Java-style
import unittest

class TestInvoice(unittest.TestCase):
    def setUp(self):
        self.invoice = Invoice(amount=1000, currency="USD")

    def test_total_with_tax(self):
        self.assertEqual(self.invoice.total_with_tax(0.1), 1100)

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            Invoice(amount=-100, currency="USD")

if __name__ == "__main__":
    unittest.main()
```

```python
# pytest — minimal, function-based, Pythonic
import pytest
from ledgerly.invoice import Invoice

def test_total_with_tax():
    invoice = Invoice(amount=1000, currency="USD")
    assert invoice.total_with_tax(0.1) == 1100

def test_invalid_amount():
    with pytest.raises(ValueError):
        Invoice(amount=-100, currency="USD")
```

Differences:
- No classes required (but supported)
- Plain `assert` (no `assertEqual`, `assertTrue`, etc.)
- Better error messages (pytest rewrites assertions to show values)
- Fixtures > setUp/tearDown (composable, scoped, injectable)
- Parametrize (no equivalent in unittest)
- Plugin ecosystem (500+ plugins)

---

## The Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        pytest Execution                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. COLLECTION                                                    │
│     Find test files (test_*.py) → find test functions (test_*)    │
│     │                                                             │
│     ▼                                                             │
│  2. FIXTURE RESOLUTION                                            │
│     For each test, resolve its fixture dependencies               │
│     (setup databases, create objects, configure mocks)            │
│     │                                                             │
│     ▼                                                             │
│  3. EXECUTION                                                     │
│     Run the test function with fixtures injected                  │
│     │                                                             │
│     ▼                                                             │
│  4. ASSERTION                                                     │
│     assert statements → PASS or FAIL with detailed diff           │
│     │                                                             │
│     ▼                                                             │
│  5. TEARDOWN                                                      │
│     Fixtures clean up (close connections, delete data)            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

```bash
pip install pytest
# or
uv add --group test pytest

pytest --version
# pytest 8.x
```

### Project Structure

```
ledgerly/
├── src/
│   └── ledgerly/
│       ├── __init__.py
│       ├── invoice.py
│       ├── payment.py
│       ├── customer.py
│       └── services/
│           ├── billing.py
│           └── notification.py
├── tests/
│   ├── conftest.py          ← shared fixtures
│   ├── test_invoice.py
│   ├── test_payment.py
│   ├── unit/
│   │   └── test_billing.py
│   └── integration/
│       └── test_api.py
├── pyproject.toml
└── pytest.ini (or in pyproject.toml)
```

### Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### Verify

```bash
# Create a minimal test
echo 'def test_sanity(): assert 1 + 1 == 2' > tests/test_sanity.py

pytest
# ========================= test session starts =========================
# tests/test_sanity.py::test_sanity PASSED
# ========================= 1 passed in 0.01s ============================
```

---

## Key Concepts (Preview)

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ One-Line Explanation
────────────────────────────────┼──────────────────────────────────────
assert                          │ The only assertion you need
Fixture                         │ Setup/teardown injected into tests
@pytest.mark.parametrize        │ Run one test with many inputs
conftest.py                     │ Shared fixtures (auto-discovered)
Marker                          │ Tag tests (@pytest.mark.slow)
monkeypatch                     │ Replace attributes/env vars in tests
tmp_path                        │ Temporary directory (auto-cleaned)
capsys                          │ Capture stdout/stderr
pytest.raises                   │ Assert that code raises an exception
Plugin                          │ Extend pytest (coverage, async, etc.)
────────────────────────────────┴──────────────────────────────────────
```

---

[Next: Chapter 1 — Your First Test →](chapter-01-first-test.md)
