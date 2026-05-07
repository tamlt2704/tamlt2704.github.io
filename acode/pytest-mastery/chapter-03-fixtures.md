# Chapter 3: Fixtures — Setup That Doesn't Suck

[← Chapter 2: Parametrize](chapter-02-parametrize.md) | [Chapter 4: conftest.py →](chapter-04-conftest.md)

---

## The Problem

Every test needs an invoice. Some tests need a customer. Some need both. Some need a database connection. You're copy-pasting setup code into every test function.

Marcus: "In unittest, we had `setUp` and `tearDown`. They ran for EVERY test in the class, even tests that didn't need them. Fixtures are better — each test declares what it needs, and only that gets created."

---

## What Is a Fixture?

A fixture is a function that provides something a test needs. Tests request fixtures by name (as function arguments). pytest injects them automatically.

```python
import pytest
from ledgerly.invoice import Invoice, InvoiceStatus

@pytest.fixture
def draft_invoice():
    """A fresh draft invoice for testing."""
    return Invoice(amount=5000, currency="USD", customer_id="cust_123")

@pytest.fixture
def sent_invoice(draft_invoice):
    """An invoice that's been sent to the customer."""
    draft_invoice.status = InvoiceStatus.SENT
    return draft_invoice

# Tests request fixtures by parameter name
def test_mark_paid(sent_invoice):
    sent_invoice.mark_paid()
    assert sent_invoice.status == InvoiceStatus.PAID

def test_draft_cannot_be_paid(draft_invoice):
    with pytest.raises(InvalidStateError):
        draft_invoice.mark_paid()
```

**Key insight:** `sent_invoice` depends on `draft_invoice`. Fixtures can depend on other fixtures — pytest resolves the dependency graph automatically.

---

## Fixture Scope

By default, fixtures are created fresh for each test. You can change this:

```python
@pytest.fixture(scope="function")  # DEFAULT — new for each test
def invoice():
    return Invoice(amount=1000, currency="USD", customer_id="c1")

@pytest.fixture(scope="class")  # shared across all tests in a class
def db_connection():
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="module")  # shared across all tests in a file
def api_client():
    client = TestClient(app)
    return client

@pytest.fixture(scope="session")  # shared across the ENTIRE test run
def docker_postgres():
    container = start_postgres_container()
    yield container
    container.stop()
```

```
Scope       │ Created    │ Destroyed     │ Use Case
────────────┼────────────┼───────────────┼──────────────────────
function    │ Each test  │ After test    │ Default. Isolated data.
class       │ Per class  │ After class   │ Shared setup for a group
module      │ Per file   │ After file    │ Expensive setup (DB schema)
session     │ Once       │ After all     │ Docker containers, servers
```

---

## Teardown with yield

```python
@pytest.fixture
def temp_file():
    """Create a temp file, clean up after test."""
    path = Path("/tmp/test_data.json")
    path.write_text('{"test": true}')

    yield path  # ← test runs here

    # Teardown: runs after the test (even if it fails)
    path.unlink(missing_ok=True)


@pytest.fixture
def db_session():
    """Database session with automatic rollback."""
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()
```

Everything before `yield` is setup. Everything after is teardown. The yielded value is what the test receives.

---

## Built-in Fixtures

pytest provides several fixtures out of the box:

```python
def test_with_tmp_path(tmp_path):
    """tmp_path: a fresh temporary directory (Path object)."""
    file = tmp_path / "data.json"
    file.write_text('{"amount": 1000}')
    assert file.exists()
    # Automatically cleaned up after test

def test_capture_output(capsys):
    """capsys: capture stdout/stderr."""
    print("Processing invoice...")
    captured = capsys.readouterr()
    assert "Processing" in captured.out

def test_capture_logs(caplog):
    """caplog: capture log messages."""
    import logging
    logger = logging.getLogger("ledgerly")
    logger.warning("Payment retry #3")
    assert "retry #3" in caplog.text

def test_monkeypatch_env(monkeypatch):
    """monkeypatch: temporarily modify things."""
    monkeypatch.setenv("STRIPE_KEY", "sk_test_fake")
    monkeypatch.setattr("ledgerly.config.DEBUG", True)
    # Automatically restored after test
```

---

## monkeypatch: The Swiss Army Knife

```python
def test_with_env_vars(monkeypatch):
    # Set environment variables
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("API_KEY", "test-key")

    # Delete environment variables
    monkeypatch.delenv("PRODUCTION_SECRET", raising=False)

    config = load_config()
    assert config.database_url == "sqlite:///test.db"


def test_with_patched_function(monkeypatch):
    # Replace a function
    monkeypatch.setattr("ledgerly.services.billing.send_email", lambda *args: None)

    # Replace a method
    monkeypatch.setattr(PaymentGateway, "charge", lambda self, amount: {"status": "ok"})

    # Replace a module-level constant
    monkeypatch.setattr("ledgerly.config.MAX_RETRIES", 1)
```

---

## Fixture Composition

Fixtures can depend on other fixtures — build complex setups from simple pieces:

```python
@pytest.fixture
def customer():
    return Customer(id="cust_123", name="Acme Corp", email="billing@acme.com")

@pytest.fixture
def invoice(customer):
    return Invoice(amount=5000, currency="USD", customer_id=customer.id)

@pytest.fixture
def paid_invoice(invoice):
    invoice.status = InvoiceStatus.SENT
    invoice.mark_paid()
    return invoice

@pytest.fixture
def billing_service(customer, invoice):
    """A billing service with a customer and their invoice."""
    service = BillingService()
    service.register_customer(customer)
    service.add_invoice(invoice)
    return service

# Test only declares what it needs — pytest resolves the graph
def test_send_reminder(billing_service, invoice):
    billing_service.send_reminder(invoice.id)
    assert invoice.reminder_sent is True
```

---

## Fixture Factories

When you need multiple instances with different configurations:

```python
@pytest.fixture
def make_invoice():
    """Factory fixture — call it to create invoices with custom params."""
    created = []

    def _make_invoice(amount=1000, currency="USD", status="draft", **kwargs):
        invoice = Invoice(
            amount=amount,
            currency=currency,
            customer_id=kwargs.get("customer_id", "cust_default"),
        )
        invoice.status = InvoiceStatus(status)
        created.append(invoice)
        return invoice

    yield _make_invoice

    # Teardown: clean up all created invoices
    for inv in created:
        inv.delete()  # if needed


def test_multiple_invoices(make_invoice):
    small = make_invoice(amount=100)
    large = make_invoice(amount=99999, currency="EUR")
    paid = make_invoice(amount=5000, status="paid")

    assert small.amount == 100
    assert large.currency == "EUR"
    assert paid.status == InvoiceStatus.PAID
```

---

## autouse: Fixtures That Always Run

```python
@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset the rate limiter before every test (no need to request it)."""
    RateLimiter.reset()
    yield
    RateLimiter.reset()

@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    """Set up test logging once for the entire session."""
    logging.basicConfig(level=logging.WARNING)
    yield
```

`autouse=True` means every test in scope gets this fixture automatically — no need to add it as a parameter.

---

## Parametrized Fixtures

```python
@pytest.fixture(params=["USD", "EUR", "GBP"])
def currency(request):
    """Run the test once for each currency."""
    return request.param

def test_invoice_supports_currency(currency):
    invoice = Invoice(amount=1000, currency=currency, customer_id="c1")
    assert invoice.currency == currency
    # This test runs 3 times — once per currency
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
@pytest.fixture                 │ Define a fixture (setup function)
yield value                     │ Provide value + teardown after
scope="function/class/module/session" │ How long fixture lives
autouse=True                    │ Apply to all tests automatically
params=[...]                    │ Parametrize the fixture itself
request.param                   │ Access current parameter value
tmp_path                        │ Built-in: temporary directory
capsys                          │ Built-in: capture stdout/stderr
caplog                          │ Built-in: capture log messages
monkeypatch                     │ Built-in: patch env/attrs/functions
Fixtures depend on fixtures     │ Automatic dependency resolution
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You have fixtures in `test_invoice.py`. But `test_payment.py` needs the same `customer` fixture. And `test_billing.py` needs it too. Copy-pasting fixtures between files defeats the purpose.

`conftest.py` — the shared fixture file that pytest auto-discovers.

---

[← Chapter 2: Parametrize](chapter-02-parametrize.md) | [Chapter 4: conftest.py →](chapter-04-conftest.md)
