# Chapter 6: 47 Possible Values

[← Chapter 5: Copy-Pasting the Same Function](chapter-05-generics.md) | [Chapter 7: The API Response Doesn't Match →](chapter-07-type-guards.md)

---

## The Disaster

The package status field started as 5 values. Then someone added `"RETURNED"`. Then `"HELD_AT_CUSTOMS"`. Then `"LOST"`. Then `"DAMAGED"`. The `switch` statement that handles status transitions has 12 cases — but there are now 15 possible statuses. Three statuses silently fall through to the `default` case, which does nothing.

A package marked `"HELD_AT_CUSTOMS"` never triggers a notification. The customer waits 3 weeks before calling support.

Ren: "If you add a status, the compiler should force you to handle it everywhere. No silent fallthrough."

---

## Discriminated Unions: Tagged Types

The key insight: different statuses carry different data. A delivered package has a `deliveredAt` date. An in-transit package has a `currentLocation`. A customs-held package has a `holdReason`.

```typescript
// src/status.ts

// Each status is its own type with a "tag" field
interface CreatedStatus {
  type: "CREATED";
  createdAt: Date;
}

interface PickedUpStatus {
  type: "PICKED_UP";
  pickedUpAt: Date;
  courier: string;
}

interface InTransitStatus {
  type: "IN_TRANSIT";
  currentLocation: string;
  lastScanAt: Date;
  estimatedArrival: Date;
}

interface HeldAtCustomsStatus {
  type: "HELD_AT_CUSTOMS";
  holdReason: string;
  heldSince: Date;
  requiredDocuments: string[];
}

interface OutForDeliveryStatus {
  type: "OUT_FOR_DELIVERY";
  driver: string;
  estimatedWindow: { start: Date; end: Date };
}

interface DeliveredStatus {
  type: "DELIVERED";
  deliveredAt: Date;
  signedBy: string;
  photoUrl?: string;
}

// The union of all possible statuses
type PackageStatus =
  | CreatedStatus
  | PickedUpStatus
  | InTransitStatus
  | HeldAtCustomsStatus
  | OutForDeliveryStatus
  | DeliveredStatus;
```

The `type` field is the **discriminant** — it tells TypeScript which variant you're dealing with.

---

## Exhaustive Switch Statements

```typescript
function getStatusMessage(status: PackageStatus): string {
  switch (status.type) {
    case "CREATED":
      return `Package created on ${status.createdAt.toLocaleDateString()}`;

    case "PICKED_UP":
      return `Picked up by ${status.courier} on ${status.pickedUpAt.toLocaleDateString()}`;

    case "IN_TRANSIT":
      return `In transit — last seen at ${status.currentLocation}`;

    case "HELD_AT_CUSTOMS":
      return `Held at customs: ${status.holdReason}`;

    case "OUT_FOR_DELIVERY":
      return `Out for delivery with ${status.driver}`;

    case "DELIVERED":
      return `Delivered on ${status.deliveredAt.toLocaleDateString()}, signed by ${status.signedBy}`;
  }
}
```

Inside each `case`, TypeScript **narrows** the type. In the `"DELIVERED"` case, it knows `status` is `DeliveredStatus` — so `status.deliveredAt` and `status.signedBy` are available.

### The Exhaustiveness Check

What happens when someone adds a new status? Let's say `"RETURNED"`:

```typescript
interface ReturnedStatus {
  type: "RETURNED";
  returnedAt: Date;
  reason: string;
}

type PackageStatus =
  | CreatedStatus
  | PickedUpStatus
  | InTransitStatus
  | HeldAtCustomsStatus
  | OutForDeliveryStatus
  | DeliveredStatus
  | ReturnedStatus;  // ← NEW
```

Now the `switch` statement is incomplete. Add an exhaustiveness check:

```typescript
function getStatusMessage(status: PackageStatus): string {
  switch (status.type) {
    case "CREATED":
      return `Package created on ${status.createdAt.toLocaleDateString()}`;
    case "PICKED_UP":
      return `Picked up by ${status.courier}`;
    case "IN_TRANSIT":
      return `In transit at ${status.currentLocation}`;
    case "HELD_AT_CUSTOMS":
      return `Held: ${status.holdReason}`;
    case "OUT_FOR_DELIVERY":
      return `Out for delivery with ${status.driver}`;
    case "DELIVERED":
      return `Delivered, signed by ${status.signedBy}`;
    default:
      // This line ensures ALL cases are handled
      const _exhaustive: never = status;
      //    ^^^^^^^^^^^ Error: Type 'ReturnedStatus' is not assignable to type 'never'
      return _exhaustive;
  }
}
```

The `never` trick: if all cases are handled, `status` in the `default` branch is `never` (impossible to reach). If a case is missing, `status` still has a type — and assigning it to `never` fails. **The compiler tells you exactly which case you forgot.**

---

## A Cleaner Exhaustiveness Helper

```typescript
// src/utils.ts
function assertNever(value: never, message?: string): never {
  throw new Error(message ?? `Unexpected value: ${JSON.stringify(value)}`);
}

// Usage
function getStatusMessage(status: PackageStatus): string {
  switch (status.type) {
    case "CREATED": return `Created`;
    case "PICKED_UP": return `Picked up`;
    case "IN_TRANSIT": return `In transit`;
    case "HELD_AT_CUSTOMS": return `Held at customs`;
    case "OUT_FOR_DELIVERY": return `Out for delivery`;
    case "DELIVERED": return `Delivered`;
    default: return assertNever(status);
    // If you add a new status and forget this switch,
    // you get a compile error pointing to this line.
  }
}
```

---

## Union Types Beyond Strings

Discriminated unions work for any "tagged" data:

```typescript
// API events from a webhook
type WebhookEvent =
  | { event: "package.created"; data: { packageId: string; createdAt: string } }
  | { event: "package.delivered"; data: { packageId: string; deliveredAt: string; signedBy: string } }
  | { event: "package.exception"; data: { packageId: string; reason: string; severity: "low" | "high" } };

function handleWebhook(event: WebhookEvent): void {
  switch (event.event) {
    case "package.created":
      // TypeScript knows: event.data has packageId and createdAt
      console.log(`New package: ${event.data.packageId}`);
      break;

    case "package.delivered":
      // TypeScript knows: event.data has packageId, deliveredAt, signedBy
      notifyCustomer(event.data.packageId, event.data.signedBy);
      break;

    case "package.exception":
      // TypeScript knows: event.data has packageId, reason, severity
      if (event.data.severity === "high") {
        alertOps(event.data.reason);
      }
      break;
  }
}
```

---

## Result Types: Success or Failure

A common pattern — functions that can fail in typed ways:

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function parseTrackingId(input: string): Result<{ prefix: string; year: number; seq: number }, string> {
  const parts = input.split("-");
  if (parts.length !== 3) {
    return { ok: false, error: `Expected format "XX-YYYY-NNNNN", got "${input}"` };
  }

  const [prefix, yearStr, seqStr] = parts;
  const year = parseInt(yearStr);
  const seq = parseInt(seqStr);

  if (isNaN(year) || isNaN(seq)) {
    return { ok: false, error: `Year and sequence must be numbers` };
  }

  return { ok: true, value: { prefix, year, seq } };
}

// Usage — caller MUST check ok before accessing value
const result = parseTrackingId("SF-2024-00042");
if (result.ok) {
  console.log(result.value.prefix);  // ✓ TypeScript knows value exists
} else {
  console.error(result.error);       // ✓ TypeScript knows error exists
}
```

No exceptions. No try/catch guessing. The type system tells you exactly what can go wrong.

---

## Narrowing Without Switch

```typescript
// if/else narrowing
function getETA(status: PackageStatus): Date | null {
  if (status.type === "IN_TRANSIT") {
    return status.estimatedArrival;  // ✓ narrowed to InTransitStatus
  }
  if (status.type === "OUT_FOR_DELIVERY") {
    return status.estimatedWindow.end;  // ✓ narrowed to OutForDeliveryStatus
  }
  return null;
}

// Array filtering with type narrowing
const inTransit = statuses.filter(
  (s): s is InTransitStatus => s.type === "IN_TRANSIT"
);
// Type: InTransitStatus[] — not PackageStatus[]!
```

The `s is InTransitStatus` is a **type predicate** — it tells TypeScript that the filter narrows the type. More on this in Chapter 7.

---

## Report to Ren

> **Status system rewritten with discriminated unions:**
> - Each status carries its own data (delivery date, location, hold reason)
> - `switch` statements are exhaustive — adding a new status causes compile errors everywhere it's unhandled
> - `assertNever` helper catches missing cases at both compile time and runtime
> - The customs notification bug? Impossible now — compiler forces handling `HELD_AT_CUSTOMS`
>
> No more silent fallthrough. No more forgotten cases.

Ren: "Perfect. Now we have a problem — the external tracking API returns raw JSON. We're casting it to our types with `as Package` and hoping for the best. Last week it returned a field we didn't expect and crashed the parser. We need runtime validation."

---

## What You Learned

- **Discriminated unions** = union types with a common "tag" field (`type`, `kind`, `event`)
- TypeScript **narrows** the type inside each `case` — you get access to variant-specific fields
- **Exhaustiveness checking** with `never` ensures every case is handled — adding a variant causes compile errors
- **`assertNever`** helper makes exhaustiveness checks clean and provides runtime safety
- **Result types** (`{ ok: true; value: T } | { ok: false; error: E }`) replace exceptions with typed errors
- **Type predicates** (`x is T`) let you narrow types in `.filter()` and custom guards
- Discriminated unions are TypeScript's most powerful pattern for modeling domain logic

---

[Next: Chapter 7 — "The API Response Doesn't Match" →](chapter-07-type-guards.md)
