# Chapter 7: The API Response Doesn't Match

[← Chapter 6: 47 Possible Values](chapter-06-unions.md) | [Chapter 8: A Refactor Breaks 200 Files →](chapter-08-utility-types.md)

---

## The Disaster

ShipFast integrates with an external carrier API. The code does this:

```typescript
const response = await fetch("https://carrier-api.example.com/track/SF-001");
const data = await response.json() as CarrierResponse;
console.log(data.tracking.events[0].location);
```

That `as CarrierResponse` is a **type assertion** — it tells TypeScript "trust me, this is the right shape." TypeScript believes you. It doesn't check.

Last Tuesday, the carrier changed their API. `tracking.events` became `tracking.history`. The code still compiles. It crashes at runtime. `Cannot read properties of undefined (reading '0')`.

Type assertions are lies you tell the compiler. Runtime validation is the truth.

---

## The Problem with `as`

```typescript
// 'as' doesn't validate anything — it just silences the compiler
const data = JSON.parse(rawJson) as Package;
// If rawJson is '{"name": "banana"}', data is typed as Package
// but has NONE of the Package fields. TypeScript won't warn you.

data.id;      // TypeScript says: string
              // Reality: undefined
data.weight;  // TypeScript says: number
              // Reality: undefined
```

`as` is useful in rare cases (when you genuinely know more than the compiler). For external data, it's dangerous.

---

## `unknown`: The Safe Starting Point

```typescript
// src/validation.ts

// JSON.parse returns 'any' by default. Override with 'unknown'.
function safeJsonParse(text: string): unknown {
  return JSON.parse(text);
}

const data = safeJsonParse(rawJson);
// Type: unknown — can't access any properties without checking first

data.id;
// Error: 'data' is of type 'unknown'
```

`unknown` forces you to validate before using. This is the correct type for any external data.

---

## Type Guards: Runtime Validation with Type Narrowing

A type guard is a function that checks a value at runtime and tells TypeScript what type it is:

```typescript
// Type predicate: "value is Package" tells TypeScript the return narrows the type
function isPackage(value: unknown): value is Package {
  if (typeof value !== "object" || value === null) return false;

  const obj = value as Record<string, unknown>;

  return (
    typeof obj.id === "string" &&
    typeof obj.origin === "string" &&
    typeof obj.destination === "string" &&
    typeof obj.weight === "number" &&
    typeof obj.status === "string"
  );
}

// Usage
const data: unknown = JSON.parse(rawJson);

if (isPackage(data)) {
  // TypeScript now knows data is Package
  console.log(data.id);      // ✓ string
  console.log(data.weight);  // ✓ number
} else {
  console.error("Invalid package data:", data);
}
```

The `value is Package` return type is a **type predicate**. When the function returns `true`, TypeScript narrows the type in the calling scope.

---

## Building Validators for Complex Types

```typescript
// Validate the carrier API response
interface CarrierEvent {
  timestamp: string;
  location: string;
  status: string;
  description: string;
}

interface CarrierResponse {
  trackingNumber: string;
  carrier: string;
  history: CarrierEvent[];
  estimatedDelivery: string | null;
}

function isCarrierEvent(value: unknown): value is CarrierEvent {
  if (typeof value !== "object" || value === null) return false;
  const obj = value as Record<string, unknown>;

  return (
    typeof obj.timestamp === "string" &&
    typeof obj.location === "string" &&
    typeof obj.status === "string" &&
    typeof obj.description === "string"
  );
}

function isCarrierResponse(value: unknown): value is CarrierResponse {
  if (typeof value !== "object" || value === null) return false;
  const obj = value as Record<string, unknown>;

  if (typeof obj.trackingNumber !== "string") return false;
  if (typeof obj.carrier !== "string") return false;
  if (!Array.isArray(obj.history)) return false;
  if (!obj.history.every(isCarrierEvent)) return false;
  if (obj.estimatedDelivery !== null && typeof obj.estimatedDelivery !== "string") return false;

  return true;
}
```

### Use It at the Boundary

```typescript
async function fetchCarrierData(trackingId: string): Promise<CarrierResponse> {
  const response = await fetch(`https://carrier-api.example.com/track/${trackingId}`);
  const raw: unknown = await response.json();

  if (!isCarrierResponse(raw)) {
    throw new Error(`Carrier API returned unexpected shape: ${JSON.stringify(raw).slice(0, 200)}`);
  }

  // After this point, 'raw' is typed as CarrierResponse — guaranteed at runtime
  return raw;
}
```

Now when the carrier changes their API, you get a clear error message instead of a cryptic crash.

---

## Assertion Functions

An alternative to type predicates — assertion functions throw instead of returning false:

```typescript
function assertIsPackage(value: unknown): asserts value is Package {
  if (typeof value !== "object" || value === null) {
    throw new Error(`Expected object, got ${typeof value}`);
  }

  const obj = value as Record<string, unknown>;

  if (typeof obj.id !== "string") {
    throw new Error(`Expected id to be string, got ${typeof obj.id}`);
  }
  if (typeof obj.weight !== "number") {
    throw new Error(`Expected weight to be number, got ${typeof obj.weight}`);
  }
  // ... more checks
}

// Usage — after the assertion, TypeScript narrows the type
const data: unknown = JSON.parse(rawJson);
assertIsPackage(data);
// If we reach here, data is Package (otherwise an error was thrown)
console.log(data.id);  // ✓ TypeScript knows it's Package
```

The `asserts value is Package` return type tells TypeScript: "if this function returns normally (doesn't throw), the value is Package."

---

## Schema Validation Libraries

Writing validators by hand is tedious and error-prone. In production, use a schema library:

```typescript
// Using Zod (most popular TypeScript-first validation library)
import { z } from "zod";

// Define the schema — it's both a validator AND a type
const CarrierEventSchema = z.object({
  timestamp: z.string(),
  location: z.string(),
  status: z.string(),
  description: z.string(),
});

const CarrierResponseSchema = z.object({
  trackingNumber: z.string(),
  carrier: z.string(),
  history: z.array(CarrierEventSchema),
  estimatedDelivery: z.string().nullable(),
});

// Extract the TypeScript type from the schema (no duplication!)
type CarrierResponse = z.infer<typeof CarrierResponseSchema>;

// Validate at runtime
async function fetchCarrierData(trackingId: string): Promise<CarrierResponse> {
  const response = await fetch(`https://carrier-api.example.com/track/${trackingId}`);
  const raw = await response.json();

  // .parse() throws ZodError with detailed messages if validation fails
  return CarrierResponseSchema.parse(raw);
}
```

Zod gives you:
- Runtime validation (throws on invalid data)
- TypeScript types (inferred from the schema — single source of truth)
- Detailed error messages ("expected string at path `history[2].location`, got number")

---

## When to Use Each Approach

| Approach | Use When |
|---|---|
| `as` (type assertion) | You genuinely know more than the compiler (rare) |
| Type guard (`value is T`) | Simple checks, no dependencies, need boolean result |
| Assertion function (`asserts value is T`) | Want to throw on invalid data, cleaner control flow |
| Zod / schema library | Production code, complex shapes, need good error messages |

---

## The Refactored External Integration

```typescript
// src/carrier-client.ts
import { z } from "zod";

const CarrierEventSchema = z.object({
  timestamp: z.string().datetime(),
  location: z.string().min(1),
  status: z.enum(["picked_up", "in_transit", "delivered", "exception"]),
  description: z.string(),
});

const CarrierResponseSchema = z.object({
  trackingNumber: z.string(),
  carrier: z.string(),
  history: z.array(CarrierEventSchema).min(1),
  estimatedDelivery: z.string().datetime().nullable(),
});

type CarrierResponse = z.infer<typeof CarrierResponseSchema>;

export async function getCarrierTracking(id: string): Promise<CarrierResponse> {
  const res = await fetch(`https://carrier-api.example.com/track/${id}`);

  if (!res.ok) {
    throw new Error(`Carrier API error: ${res.status} ${res.statusText}`);
  }

  const raw = await res.json();
  const result = CarrierResponseSchema.safeParse(raw);

  if (!result.success) {
    console.error("Carrier API schema mismatch:", result.error.format());
    throw new Error(`Carrier API returned unexpected data for ${id}`);
  }

  return result.data;
}
```

Now when the carrier changes `events` to `history`, you get:

```
Carrier API schema mismatch:
{
  history: { _errors: ["Required"] }
}
```

Instead of `Cannot read properties of undefined (reading '0')` at 2am.

---

## Report to Ren

> **External data validation implemented:**
> - All `as CarrierResponse` assertions replaced with runtime validation
> - Using Zod schemas — single source of truth for types AND validation
> - Carrier API changes now produce clear error messages, not cryptic crashes
> - `unknown` used for all external data — compiler forces validation before use
>
> The Tuesday crash? Would have been caught with a clear "schema mismatch" error instead of `undefined is not a function`.

Ren: "Excellent. Now I need you to refactor the Package interface — rename `origin` to `sender` and `destination` to `recipient`. There are 200 files that reference these fields. Don't break anything."

---

## What You Learned

- **`as` (type assertions)** lie to the compiler — they don't validate at runtime
- **`unknown`** is the correct type for external data — forces validation before use
- **Type guards** (`value is T`) validate at runtime and narrow types at compile time
- **Assertion functions** (`asserts value is T`) throw on invalid data, narrow on success
- **Zod** (and similar libraries) provide runtime validation + TypeScript types from one schema
- Validate at the **boundary** (API responses, user input, file reads) — trust types internally
- `JSON.parse()` returns `any` — treat it as `unknown` and validate immediately
- Good error messages at the boundary save hours of debugging at 2am

---

[Next: Chapter 8 — "A Refactor Breaks 200 Files" →](chapter-08-utility-types.md)
