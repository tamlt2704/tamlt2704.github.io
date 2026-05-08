"""
Payment Ledger — Core Implementation
======================================
Demonstrates: Idempotency keys, payment state machine,
double-entry ledger, reconciliation.

In a real system:
- Idempotency keys stored in Redis with TTL (48h typical)
- State machine transitions in PostgreSQL with row-level locks
- Ledger entries in append-only table (never UPDATE, never DELETE)
- Reconciliation runs as batch job comparing ledger vs bank statements
- Payment gateway integration: Stripe, Adyen (webhook-driven state updates)
- Saga pattern for distributed transactions across services
"""

import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─── Payment State Machine ────────────────────────────────────────────────────

class PaymentState(Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


# Valid state transitions
VALID_TRANSITIONS = {
    PaymentState.CREATED: {PaymentState.PROCESSING},
    PaymentState.PROCESSING: {PaymentState.SUCCEEDED, PaymentState.FAILED},
    PaymentState.SUCCEEDED: {PaymentState.REFUNDED},
    PaymentState.FAILED: set(),      # Terminal state
    PaymentState.REFUNDED: set(),    # Terminal state
}


@dataclass
class Payment:
    id: str
    amount: int              # In cents (avoid floating point!)
    currency: str
    sender: str
    recipient: str
    state: PaymentState = PaymentState.CREATED
    idempotency_key: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    failure_reason: Optional[str] = None

    def transition(self, new_state: PaymentState, reason: str = None) -> bool:
        """Attempt state transition. Returns False if invalid."""
        if new_state not in VALID_TRANSITIONS[self.state]:
            return False
        self.state = new_state
        self.updated_at = time.time()
        if reason:
            self.failure_reason = reason
        return True


# ─── Idempotency Key Store ───────────────────────────────────────────────────

class IdempotencyStore:
    """
    Prevents duplicate payment processing.
    Client sends same idempotency key → gets same response (no double charge).

    Production: Redis with TTL, or PostgreSQL unique constraint.
    Key format: client_id + unique_request_id (UUID from client).
    """

    def __init__(self, ttl_seconds: float = 86400 * 2):  # 48h TTL
        self.store: dict[str, dict] = {}  # key → {payment_id, response, timestamp}
        self.ttl = ttl_seconds

    def check_and_set(self, key: str, payment_id: str) -> Optional[dict]:
        """
        Returns existing response if key was seen before (idempotent replay).
        Returns None if this is a new request.
        """
        if key in self.store:
            entry = self.store[key]
            # Check TTL
            if time.time() - entry["timestamp"] < self.ttl:
                return entry  # Return cached response
            else:
                del self.store[key]  # Expired

        # New key — register it
        self.store[key] = {
            "payment_id": payment_id,
            "response": None,
            "timestamp": time.time(),
        }
        return None

    def set_response(self, key: str, response: dict):
        """Store the response for future idempotent replays."""
        if key in self.store:
            self.store[key]["response"] = response


# ─── Double-Entry Ledger ──────────────────────────────────────────────────────

@dataclass
class LedgerEntry:
    """
    Every financial transaction has TWO entries that sum to zero:
    - Debit: money leaves an account (positive amount)
    - Credit: money enters an account (negative amount)

    This is the fundamental invariant: sum of all entries = 0.
    """
    id: str
    payment_id: str
    account: str
    amount: int          # Positive = debit, Negative = credit
    entry_type: str      # "debit" or "credit"
    timestamp: float = field(default_factory=time.time)
    description: str = ""


class Ledger:
    """
    Append-only double-entry ledger.
    Invariant: for every payment, debit + credit = 0.
    """

    def __init__(self):
        self.entries: list[LedgerEntry] = []
        self.balances: dict[str, int] = defaultdict(int)  # account → balance

    def record_transfer(self, payment: Payment) -> tuple[LedgerEntry, LedgerEntry]:
        """Record a payment as two ledger entries (debit + credit)."""
        debit = LedgerEntry(
            id=f"le_{uuid.uuid4().hex[:8]}",
            payment_id=payment.id,
            account=payment.sender,
            amount=payment.amount,  # Positive: money leaves
            entry_type="debit",
            description=f"Payment to {payment.recipient}",
        )
        credit = LedgerEntry(
            id=f"le_{uuid.uuid4().hex[:8]}",
            payment_id=payment.id,
            account=payment.recipient,
            amount=-payment.amount,  # Negative: money enters
            entry_type="credit",
            description=f"Payment from {payment.sender}",
        )

        self.entries.append(debit)
        self.entries.append(credit)
        self.balances[payment.sender] -= payment.amount
        self.balances[payment.recipient] += payment.amount

        return debit, credit

    def record_refund(self, payment: Payment) -> tuple[LedgerEntry, LedgerEntry]:
        """Reverse a payment (refund). Creates opposite entries."""
        debit = LedgerEntry(
            id=f"le_{uuid.uuid4().hex[:8]}",
            payment_id=payment.id,
            account=payment.recipient,
            amount=payment.amount,
            entry_type="debit",
            description=f"Refund to {payment.sender}",
        )
        credit = LedgerEntry(
            id=f"le_{uuid.uuid4().hex[:8]}",
            payment_id=payment.id,
            account=payment.sender,
            amount=-payment.amount,
            entry_type="credit",
            description=f"Refund from {payment.recipient}",
        )

        self.entries.append(debit)
        self.entries.append(credit)
        self.balances[payment.recipient] -= payment.amount
        self.balances[payment.sender] += payment.amount

        return debit, credit

    def reconcile(self) -> dict:
        """
        Verify ledger integrity: all entries must sum to zero.
        Production: compare against bank statements and gateway records.
        """
        total = sum(e.amount for e in self.entries)
        per_payment: dict[str, int] = defaultdict(int)
        for entry in self.entries:
            per_payment[entry.payment_id] += entry.amount

        unbalanced = {pid: amt for pid, amt in per_payment.items() if amt != 0}

        return {
            "total_entries": len(self.entries),
            "global_sum": total,
            "balanced": total == 0,
            "unbalanced_payments": unbalanced,
            "all_payments_balanced": len(unbalanced) == 0,
        }


# ─── Payment Service ─────────────────────────────────────────────────────────

class PaymentService:
    """Orchestrates payment processing with idempotency and ledger."""

    def __init__(self):
        self.payments: dict[str, Payment] = {}
        self.idempotency = IdempotencyStore()
        self.ledger = Ledger()

    def create_payment(self, amount: int, currency: str, sender: str,
                       recipient: str, idempotency_key: str) -> dict:
        """Create and process a payment."""
        # Check idempotency
        payment_id = f"pay_{uuid.uuid4().hex[:8]}"
        existing = self.idempotency.check_and_set(idempotency_key, payment_id)
        if existing and existing["response"]:
            return {**existing["response"], "idempotent_replay": True}

        # Create payment
        payment = Payment(
            id=payment_id, amount=amount, currency=currency,
            sender=sender, recipient=recipient,
            idempotency_key=idempotency_key,
        )
        self.payments[payment_id] = payment

        # Process: CREATED → PROCESSING → SUCCEEDED/FAILED
        payment.transition(PaymentState.PROCESSING)

        # Simulate gateway call (would be async in production)
        success = amount < 100000  # Fail payments over $1000 for demo
        if success:
            payment.transition(PaymentState.SUCCEEDED)
            self.ledger.record_transfer(payment)
            response = {"payment_id": payment_id, "status": "succeeded"}
        else:
            payment.transition(PaymentState.FAILED, reason="Amount exceeds limit")
            response = {"payment_id": payment_id, "status": "failed",
                        "reason": payment.failure_reason}

        self.idempotency.set_response(idempotency_key, response)
        return response


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Payment Ledger Demo ===\n")
    service = PaymentService()

    # --- Normal payment flow ---
    print("--- Payment State Machine ---")
    result = service.create_payment(5000, "USD", "alice", "bob", "key_001")
    print(f"  Payment: $50.00 alice→bob: {result['status']}")
    payment = service.payments[result["payment_id"]]
    print(f"  State transitions: CREATED → PROCESSING → {payment.state.value.upper()}")

    # --- Idempotency ---
    print("\n--- Idempotency (duplicate request) ---")
    result2 = service.create_payment(5000, "USD", "alice", "bob", "key_001")
    print(f"  Same key 'key_001': {result2}")
    print(f"  → No double charge! Same response returned.")

    # --- Failed payment ---
    print("\n--- Failed Payment ---")
    result3 = service.create_payment(150000, "USD", "alice", "merchant", "key_002")
    print(f"  Payment: $1500.00 (over limit): {result3['status']}")
    print(f"  Reason: {result3.get('reason')}")

    # --- Multiple payments ---
    print("\n--- Multiple Payments ---")
    service.create_payment(2500, "USD", "bob", "charlie", "key_003")
    service.create_payment(1000, "USD", "charlie", "alice", "key_004")
    service.create_payment(7500, "USD", "alice", "charlie", "key_005")

    # --- Double-Entry Ledger ---
    print("\n--- Double-Entry Ledger ---")
    print(f"  {'Account':<12} {'Balance':>10}")
    print(f"  {'-'*22}")
    for account, balance in sorted(service.ledger.balances.items()):
        print(f"  {account:<12} ${balance/100:>9.2f}")

    # --- Reconciliation ---
    print("\n--- Reconciliation Check ---")
    recon = service.ledger.reconcile()
    print(f"  Total entries: {recon['total_entries']}")
    print(f"  Global sum: {recon['global_sum']} (should be 0)")
    print(f"  All balanced: {recon['all_payments_balanced']} ✓")

    # --- State machine validation ---
    print("\n--- Invalid State Transitions ---")
    p = Payment(id="test", amount=100, currency="USD", sender="x", recipient="y")
    print(f"  CREATED → SUCCEEDED: {p.transition(PaymentState.SUCCEEDED)} (invalid!)")
    print(f"  CREATED → PROCESSING: {p.transition(PaymentState.PROCESSING)} (valid)")
    print(f"  PROCESSING → CREATED: {p.transition(PaymentState.CREATED)} (invalid!)")
    print(f"  PROCESSING → SUCCEEDED: {p.transition(PaymentState.SUCCEEDED)} (valid)")
    print(f"  SUCCEEDED → REFUNDED: {p.transition(PaymentState.REFUNDED)} (valid)")
