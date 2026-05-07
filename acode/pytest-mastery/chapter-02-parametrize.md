# Chapter 2: Parametrize — One Test, Many Cases

[← Chapter 1: First Test](chapter-01-first-test.md) | [Chapter 3: Fixtures →](chapter-03-fixtures.md)

---

## The Problem

You need to test currency validation. Ledgerly supports USD, EUR, GBP, JPY, and CAD. It rejects empty strings, invalid codes, and lowercase input. That's 10+ cases. Writing 10 separate test functions is tedious and hides the pattern.

---

## @pytest.mark.parametrize

```python
import pytest
from ledgerly.invoice import Invoice

@pytest.mark.parametrize("currency,valid", [
    ("USD", True),
    ("EUR", True),
    ("GBP", True),
    ("JPY", True),
    ("CAD", True),
    ("", False),
    ("usd", False),
    ("INVALID", False),
    ("US", False),
    ("USDD", False),
])
def test_currency_validation(currency, valid):
    if valid:
        invoice = Invoice(amount=1000, currency=currency, customer_id="c1")
        assert invoice.currency == currency
    else:
        with pytest.raises(ValueError):
            Invoice(amount=1000, currency=currency, customer_id="c1")
```

Output:

```
tests/test_invoice.py::test_currency_validation[USD-True] PASSED
tests/test_invoice.py::test_currency_validation[EUR-True] PASSED
tests/test_invoice.py::test_currency_validation[GBP-True] PASSED
tests/test_invoice.py::test_currency_validation[JPY-True] PASSED
tests/test_invoice.py::test_currency_validation[CAD-True] PASSED
tests/test_invoice.py::test_currency_validation[-False] PASSED
tests/test_invoice.py::test_currency_validation[usd-False] PASSED
tests/test_invoice.py::test_currency_validation[INVALID-False] PASSED
tests/test_invoice.py::test_currency_validation[US-False] PASSED
tests/test_invoice.py::test_currency_validation[USDD-False] PASSED
```

10 test cases. 1 function. Each case runs independently — if one fails, the others still run.

---

## Basic Syntax

```python
@pytest.mark.parametrize("arg_name", [value1, value2, value3])
def test_something(arg_name):
    # arg_name takes each value in turn
    pass

# Multiple arguments
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_addition(a, b, expected):
    assert a + b == expected
```

---

## Real Example: Tax Calculation

```python
@pytest.mark.parametrize("amount,tax_rate,expected_total", [
    (10000, 0.0, 10000),      # no tax
    (10000, 0.1, 11000),      # 10% tax
    (10000, 0.2, 12000),      # 20% tax
    (1, 0.1, 1),              # rounds down (1 cent + 0.1 cent = 1 cent)
    (9999, 0.07, 10699),      # 7% tax on $99.99
    (0, 0.2, 0),              # zero amount
])
def test_total_with_tax(amount, tax_rate, expected_total):
    invoice = Invoice(amount=amount, currency="USD", customer_id="c1")
    assert invoice.total_with_tax(tax_rate) == expected_total
```

---

## Named Test Cases with pytest.param

For complex cases, use `pytest.param` with `id` for readable output:

```python
@pytest.mark.parametrize("invoice_status,can_pay", [
    pytest.param("draft", False, id="draft-cannot-pay"),
    pytest.param("sent", True, id="sent-can-pay"),
    pytest.param("paid", False, id="already-paid"),
    pytest.param("overdue", True, id="overdue-can-still-pay"),
    pytest.param("cancelled", False, id="cancelled-cannot-pay"),
])
def test_payment_eligibility(invoice_status, can_pay):
    invoice = Invoice(amount=1000, currency="USD", customer_id="c1")
    invoice.status = InvoiceStatus(invoice_status)

    if can_pay:
        invoice.mark_paid()
        assert invoice.status == InvoiceStatus.PAID
    else:
        with pytest.raises((AlreadyPaidError, InvalidStateError)):
            invoice.mark_paid()
```

Output:
```
test_payment_eligibility[draft-cannot-pay] PASSED
test_payment_eligibility[sent-can-pay] PASSED
test_payment_eligibility[already-paid] PASSED
test_payment_eligibility[overdue-can-still-pay] PASSED
test_payment_eligibility[cancelled-cannot-pay] PASSED
```

---

## Marking Expected Failures

```python
@pytest.mark.parametrize("amount,currency", [
    (1000, "USD"),
    (5000, "EUR"),
    pytest.param(1000, "BTC", marks=pytest.mark.xfail(reason="crypto not yet supported")),
    pytest.param(-1, "USD", marks=pytest.mark.xfail(raises=ValueError)),
])
def test_invoice_creation(amount, currency):
    invoice = Invoice(amount=amount, currency=currency, customer_id="c1")
    assert invoice.amount == amount
```

`xfail` = "expected to fail." If it fails, it's marked `xfail` (not a failure). If it unexpectedly passes, it's marked `xpass` (a surprise).

---

## Stacking Parametrize (Cartesian Product)

```python
@pytest.mark.parametrize("currency", ["USD", "EUR", "GBP"])
@pytest.mark.parametrize("amount", [100, 1000, 99999])
def test_invoice_creation_matrix(amount, currency):
    invoice = Invoice(amount=amount, currency=currency, customer_id="c1")
    assert invoice.amount == amount
    assert invoice.currency == currency
```

This runs 3 × 3 = 9 test cases (every combination).

---

## Parametrize with Fixtures

You can parametrize fixtures too (Chapter 3), but you can also combine parametrize with fixtures:

```python
@pytest.mark.parametrize("tax_rate", [0.0, 0.05, 0.1, 0.2, 0.25])
def test_tax_never_negative(sample_invoice, tax_rate):
    """Tax should never make the total less than the original amount."""
    total = sample_invoice.total_with_tax(tax_rate)
    assert total >= sample_invoice.amount
```

---

## Indirect Parametrize (Parametrize a Fixture)

```python
# conftest.py
@pytest.fixture
def invoice_with_status(request):
    """Create an invoice with the parametrized status."""
    invoice = Invoice(amount=1000, currency="USD", customer_id="c1")
    invoice.status = InvoiceStatus(request.param)
    return invoice

# test file
@pytest.mark.parametrize("invoice_with_status", ["sent", "overdue"], indirect=True)
def test_payable_invoices(invoice_with_status):
    invoice_with_status.mark_paid()
    assert invoice_with_status.status == InvoiceStatus.PAID
```

`indirect=True` tells pytest to pass the parameter to the fixture, not directly to the test.

---

## When to Use Parametrize vs. Separate Tests

**Use parametrize when:**
- Same logic, different inputs (validation, calculation, mapping)
- Testing boundaries (0, 1, max, negative)
- Testing multiple valid/invalid cases

**Use separate tests when:**
- Different setup/teardown needed
- Different assertions for each case
- The test logic itself differs (not just inputs)

```python
# GOOD — same logic, different inputs
@pytest.mark.parametrize("amount", [0, 1, 100, 99999, 10000000])
def test_valid_amounts(amount):
    invoice = Invoice(amount=amount, currency="USD", customer_id="c1")
    assert invoice.amount == amount

# BAD — forcing different logic into parametrize
@pytest.mark.parametrize("scenario", ["create", "pay", "cancel", "refund"])
def test_invoice_lifecycle(scenario):
    if scenario == "create":
        # ... completely different logic ...
    elif scenario == "pay":
        # ... completely different logic ...
    # This should be separate test functions
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
@pytest.mark.parametrize("a", [1,2,3]) │ Run test with each value
@pytest.mark.parametrize("a,b", [...]) │ Multiple arguments per case
pytest.param(val, id="name")    │ Named test case (readable output)
pytest.param(val, marks=xfail)  │ Expected failure
Stack two @parametrize          │ Cartesian product of values
indirect=True                   │ Pass param to fixture, not test
pytest -k "name"                │ Run specific parametrized case
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Every test creates its own `Invoice`. But what about tests that need a database connection? Or a configured HTTP client? Or a temporary directory? You'd repeat setup code in every test.

Fixtures solve this — reusable setup that pytest injects into your tests automatically.

---

[← Chapter 1: First Test](chapter-01-first-test.md) | [Chapter 3: Fixtures →](chapter-03-fixtures.md)
