# Chapter 1: Your First Test — assert Is All You Need

[← Overview](chapter-00-overview.md) | [Chapter 2: Parametrize →](chapter-02-parametrize.md)

---

## The Bug

The billing system charged 200 customers twice. The `process_payment` function was called, returned success, but didn't check if the invoice was already paid. A retry loop called it again.

Marcus: "If we had ONE test — `test_cannot_pay_already_paid_invoice` — this never ships."

---

## The Simplest Test

```python
# tests/test_invoice.py
from ledgerly.invoice import Invoice

def test_create_invoice():
    invoice = Invoice(amount=5000, currency="USD", customer_id="cust_123")

    assert invoice.amount == 5000
    assert invoice.currency == "USD"
    assert invoice.status == "draft"
```

That's it. No imports from pytest (for basic tests). No classes. No decorators. Just a function that starts with `test_` and uses `assert`.

---

## Running Tests

```bash
# Run all tests
pytest

# Run a specific file
pytest tests/test_invoice.py

# Run a specific test function
pytest tests/test_invoice.py::test_create_invoice

# Run tests matching a keyword
pytest -k "invoice"
pytest -k "invoice and not payment"

# Verbose output (show each test name)
pytest -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run last failed tests only
pytest --lf

# Run failed tests first, then the rest
pytest --ff
```

---

## Assertion Power: Why Plain assert Works

pytest rewrites `assert` statements to show detailed failure information:

```python
def test_invoice_total():
    invoice = Invoice(amount=1000, currency="USD")
    total = invoice.total_with_tax(rate=0.1)

    assert total == 1100
```

If this fails, pytest shows:

```
FAILED tests/test_invoice.py::test_invoice_total
    assert total == 1100
AssertionError: assert 1000 == 1100
    where 1000 = <Invoice>.total_with_tax(rate=0.1)
```

Compare with unittest's `assertEqual(total, 1100)` — same information, more boilerplate.

### Rich Comparisons

```python
def test_line_items():
    invoice = Invoice(amount=1000, currency="USD")
    invoice.add_line("Widget", 500)
    invoice.add_line("Gadget", 500)

    assert invoice.line_items == [
        LineItem(description="Widget", amount=500),
        LineItem(description="Gadget", amount=500),
    ]
```

On failure, pytest shows a diff:

```
AssertionError: assert [LineItem(description='Widget', amount=500),
                        LineItem(description='Gadget', amount=300)]
                    == [LineItem(description='Widget', amount=500),
                        LineItem(description='Gadget', amount=500)]
At index 1:
  LineItem(description='Gadget', amount=300)
  !=
  LineItem(description='Gadget', amount=500)
```

---

## Testing the Billing Bug

```python
# src/ledgerly/invoice.py
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

@dataclass
class Invoice:
    amount: int  # cents
    currency: str
    customer_id: str
    status: InvoiceStatus = InvoiceStatus.DRAFT
    paid_at: datetime | None = None

    def mark_paid(self) -> None:
        if self.status == InvoiceStatus.PAID:
            raise AlreadyPaidError(f"Invoice already paid at {self.paid_at}")
        if self.status == InvoiceStatus.CANCELLED:
            raise InvalidStateError("Cannot pay a cancelled invoice")
        self.status = InvoiceStatus.PAID
        self.paid_at = datetime.now()

class AlreadyPaidError(Exception):
    pass

class InvalidStateError(Exception):
    pass
```

```python
# tests/test_invoice.py
import pytest
from ledgerly.invoice import Invoice, InvoiceStatus, AlreadyPaidError, InvalidStateError

def test_mark_paid_succeeds():
    invoice = Invoice(amount=5000, currency="USD", customer_id="cust_123")
    invoice.status = InvoiceStatus.SENT

    invoice.mark_paid()

    assert invoice.status == InvoiceStatus.PAID
    assert invoice.paid_at is not None

def test_cannot_pay_already_paid_invoice():
    """THE TEST THAT WOULD HAVE PREVENTED THE $50K BUG."""
    invoice = Invoice(amount=5000, currency="USD", customer_id="cust_123")
    invoice.status = InvoiceStatus.SENT
    invoice.mark_paid()  # first payment succeeds

    with pytest.raises(AlreadyPaidError):
        invoice.mark_paid()  # second payment must fail

def test_cannot_pay_cancelled_invoice():
    invoice = Invoice(amount=5000, currency="USD", customer_id="cust_123")
    invoice.status = InvoiceStatus.CANCELLED

    with pytest.raises(InvalidStateError, match="Cannot pay a cancelled"):
        invoice.mark_paid()
```

---

## pytest.raises: Testing Exceptions

```python
# Basic — just check the exception type
with pytest.raises(ValueError):
    Invoice(amount=-100, currency="USD")

# Check the error message
with pytest.raises(ValueError, match="Amount must be positive"):
    Invoice(amount=-100, currency="USD")

# Access the exception object
with pytest.raises(AlreadyPaidError) as exc_info:
    invoice.mark_paid()

assert "already paid" in str(exc_info.value)
assert exc_info.type is AlreadyPaidError
```

---

## Test Discovery Rules

pytest finds tests automatically:

1. **Files:** named `test_*.py` or `*_test.py`
2. **Functions:** named `test_*`
3. **Classes:** named `Test*` (no `__init__`)
4. **Methods:** named `test_*` inside `Test*` classes

```python
# All of these are discovered:

def test_something():          # ✅ function
    pass

class TestInvoice:             # ✅ class (no __init__)
    def test_create(self):     # ✅ method
        pass

    def test_delete(self):     # ✅ method
        pass

# These are NOT discovered:
def helper_function():         # ❌ doesn't start with test_
    pass

class InvoiceTests:            # ❌ doesn't start with Test
    pass
```

---

## Organizing Tests

```python
# Group related tests in a class (no inheritance needed)
class TestInvoiceCreation:
    def test_valid_invoice(self):
        invoice = Invoice(amount=1000, currency="USD", customer_id="c1")
        assert invoice.status == InvoiceStatus.DRAFT

    def test_rejects_negative_amount(self):
        with pytest.raises(ValueError):
            Invoice(amount=-1, currency="USD", customer_id="c1")

    def test_rejects_empty_currency(self):
        with pytest.raises(ValueError):
            Invoice(amount=1000, currency="", customer_id="c1")


class TestInvoicePayment:
    def test_mark_paid(self):
        invoice = Invoice(amount=1000, currency="USD", customer_id="c1")
        invoice.status = InvoiceStatus.SENT
        invoice.mark_paid()
        assert invoice.status == InvoiceStatus.PAID

    def test_double_payment_rejected(self):
        invoice = Invoice(amount=1000, currency="USD", customer_id="c1")
        invoice.status = InvoiceStatus.SENT
        invoice.mark_paid()
        with pytest.raises(AlreadyPaidError):
            invoice.mark_paid()
```

---

## Useful Command-Line Options

```bash
# Show print() output (normally captured)
pytest -s

# Show the 10 slowest tests
pytest --durations=10

# Run in parallel (needs pytest-xdist)
pytest -n auto

# Generate coverage report
pytest --cov=ledgerly --cov-report=html

# Only run tests that match a pattern
pytest -k "paid"           # runs test_mark_paid, test_double_payment_rejected
pytest -k "not slow"       # skip tests marked as slow

# Dry run — show what would run without running
pytest --collect-only
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
def test_name():                │ A test function (auto-discovered)
assert x == y                   │ The only assertion you need
pytest.raises(ExcType)          │ Assert code raises an exception
pytest.raises(E, match="msg")   │ Also check the error message
pytest -v                       │ Verbose output
pytest -x                       │ Stop on first failure
pytest -k "pattern"             │ Filter tests by name
pytest --lf                     │ Re-run last failed
pytest -s                       │ Show print output
class TestGroup:                │ Group related tests (optional)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You wrote 3 tests for invoice payment. But what about all the edge cases? Different currencies, different amounts, different statuses. You'd need 15 test functions that are almost identical. There's a better way.

Marcus: "Parametrize. One test function, 15 inputs. If any fail, you see exactly which case broke."

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Parametrize →](chapter-02-parametrize.md)
