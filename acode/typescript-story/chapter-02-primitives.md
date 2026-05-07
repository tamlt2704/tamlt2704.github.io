# Chapter 2: A String Sneaks In

[← Chapter 1: First Types](chapter-01-first-types.md) | [Chapter 3: An Object is Missing a Field →](chapter-03-interfaces.md)

---

## The Disaster

The package creation endpoint accepts weight from a form. In JavaScript, form values are always strings. Someone posts `weight: "12.5"` and the code does:

```javascript
const totalCost = package.weight * ratePerKg;
```

JavaScript silently coerces `"12.5" * 2.5` to `31.25`. Works fine. Until someone posts `weight: "12.5kg"`. Now `"12.5kg" * 2.5` = `NaN`. The invoice shows `$NaN`. The customer is confused. Accounting is furious.

TypeScript's type system makes this category of bug structurally impossible.

---

## Primitive Types

```typescript
// src/primitives.ts

// The 7 primitive types you'll use daily
let trackingId: string = "SF-2024-00042";
let weight: number = 12.5;           // integers and floats are both 'number'
let isDelivered: boolean = false;
let deliveryDate: Date = new Date(); // technically an object, but fundamental
let nothing: null = null;
let missing: undefined = undefined;
let uniqueKey: symbol = Symbol("id");

// BigInt for very large numbers (rare in most apps)
let hugeNumber: bigint = 9007199254740993n;
```

### The `number` Type is Strict

```typescript
let weight: number = 12.5;

weight = "12.5";
// Error: Type 'string' is not assignable to type 'number'

weight = "12.5kg";
// Error: Type 'string' is not assignable to type 'number'

weight = NaN;
// ⚠️ This compiles! NaN is technically a number in JavaScript.
// TypeScript can't save you from everything.
```

---

## Literal Types: Even More Specific

Sometimes `string` is too broad. You don't want *any* string — you want specific values.

```typescript
// A status can only be one of these exact strings
type PackageStatus = "CREATED" | "PICKED_UP" | "IN_TRANSIT" | "OUT_FOR_DELIVERY" | "DELIVERED";

let status: PackageStatus = "IN_TRANSIT";  // ✓
status = "LOST";
// Error: Type '"LOST"' is not assignable to type 'PackageStatus'

// Literal numbers work too
type Priority = 1 | 2 | 3;
let priority: Priority = 2;  // ✓
priority = 5;
// Error: Type '5' is not assignable to type 'Priority'
```

In JavaScript, `status = "LSOT"` (typo) would silently work and break a `switch` statement downstream. TypeScript catches it immediately.

---

## Type Narrowing: Teaching TypeScript What You Know

TypeScript tracks what type a value *could be* at each point in your code. When you check a condition, it narrows the possibilities.

```typescript
function processWeight(input: string | number): number {
  // Here, input is: string | number

  if (typeof input === "string") {
    // Here, TypeScript knows input is: string
    const parsed = parseFloat(input);
    if (isNaN(parsed)) {
      throw new Error(`Invalid weight: "${input}"`);
    }
    return parsed;
  }

  // Here, TypeScript knows input is: number (string was handled above)
  return input;
}

// Both work:
processWeight(12.5);    // → 12.5
processWeight("12.5");  // → 12.5
processWeight("12.5kg"); // → throws Error
```

TypeScript follows your `if` statements and narrows types automatically. This is called **control flow analysis**.

### Common Narrowing Patterns

```typescript
// typeof (for primitives)
function double(x: string | number): string | number {
  if (typeof x === "string") {
    return x + x;        // string concatenation
  }
  return x * 2;          // number multiplication
}

// Truthiness (for null/undefined)
function getCity(address: { city: string } | null): string {
  if (!address) {
    return "Unknown";    // address is null here
  }
  return address.city;   // address is { city: string } here
}

// "in" operator (for objects)
interface Express { type: "express"; guaranteedDays: number }
interface Standard { type: "standard"; estimatedDays: number }

function getDays(shipping: Express | Standard): number {
  if ("guaranteedDays" in shipping) {
    return shipping.guaranteedDays;  // TypeScript knows it's Express
  }
  return shipping.estimatedDays;     // TypeScript knows it's Standard
}
```

---

## The Fix: Validate at the Boundary

The real lesson: validate external data (form inputs, API responses, database rows) at the boundary, then use strict types internally.

```typescript
// src/validation.ts

interface CreatePackageInput {
  trackingId: string;
  weight: number;        // Already validated — guaranteed to be a number
  origin: string;
  destination: string;
}

// This function is the boundary — it validates raw input
function validatePackageInput(raw: Record<string, unknown>): CreatePackageInput {
  const trackingId = raw.trackingId;
  if (typeof trackingId !== "string" || trackingId.length === 0) {
    throw new Error("trackingId must be a non-empty string");
  }

  const weight = Number(raw.weight);
  if (isNaN(weight) || weight <= 0) {
    throw new Error(`weight must be a positive number, got: ${raw.weight}`);
  }

  const origin = raw.origin;
  if (typeof origin !== "string") {
    throw new Error("origin must be a string");
  }

  const destination = raw.destination;
  if (typeof destination !== "string") {
    throw new Error("destination must be a string");
  }

  return { trackingId, weight, origin, destination };
}
```

After `validatePackageInput`, every function downstream receives `CreatePackageInput` — where `weight` is guaranteed to be a `number`. No more `"12.5kg" * 2.5`.

---

## `any` vs `unknown`: The Escape Hatches

```typescript
// 'any' — disables type checking entirely. The nuclear option.
let dangerous: any = "hello";
dangerous.foo.bar.baz();  // No error! TypeScript gives up.
// This WILL crash at runtime. TypeScript won't save you.

// 'unknown' — "I don't know what this is, but I'll check before using it"
let safe: unknown = "hello";
safe.foo;
// Error: 'safe' is of type 'unknown'

// You must narrow it first:
if (typeof safe === "string") {
  console.log(safe.toUpperCase());  // ✓ TypeScript knows it's a string now
}
```

**Rule: never use `any` unless you're migrating legacy code and will fix it later. Use `unknown` for values you genuinely don't know the type of.**

```typescript
// ❌ Bad: any spreads like a virus
function parseJSON(text: string): any {
  return JSON.parse(text);  // Caller gets no type safety
}

// ✓ Good: unknown forces the caller to validate
function parseJSON(text: string): unknown {
  return JSON.parse(text);  // Caller must narrow before using
}
```

---

## Template Literal Types

TypeScript can even type string patterns:

```typescript
// Tracking IDs must match "XX-YYYY-NNNNN" format
type TrackingId = `${string}-${number}-${string}`;

// More specific:
type ShipFastId = `SF-${number}-${string}`;

let id: ShipFastId = "SF-2024-00042";  // ✓
let bad: ShipFastId = "UPS-2024-00042";
// Error: Type '"UPS-2024-00042"' is not assignable to type '`SF-${number}-${string}`'
```

---

## Putting It Together: The Package Creator

```typescript
// src/packages.ts
type PackageStatus = "CREATED" | "PICKED_UP" | "IN_TRANSIT" | "OUT_FOR_DELIVERY" | "DELIVERED";
type Priority = 1 | 2 | 3;

interface Package {
  id: string;
  origin: string;
  destination: string;
  weight: number;
  status: PackageStatus;
  priority: Priority;
  createdAt: Date;
}

const packages: Package[] = [];

function createPackage(input: CreatePackageInput, priority: Priority = 2): Package {
  const pkg: Package = {
    id: input.trackingId,
    origin: input.origin,
    destination: input.destination,
    weight: input.weight,
    status: "CREATED",
    priority,
    createdAt: new Date(),
  };

  packages.push(pkg);
  return pkg;
}

// Try to create with wrong status:
createPackage({ trackingId: "SF-2024-00001", weight: 5, origin: "Berlin", destination: "Paris" });
// ✓ Works

// Try to set invalid status later:
packages[0].status = "LOST_IN_SPACE";
// Error: Type '"LOST_IN_SPACE"' is not assignable to type 'PackageStatus'
```

---

## Report to Ren

> **Primitives and validation migrated:**
> - All form inputs validated at the boundary — `"12.5kg"` caught before it reaches business logic
> - `PackageStatus` is a literal union — typos caught at compile time
> - `any` replaced with `unknown` + narrowing — no more silent type erasure
> - Weight is guaranteed `number` after validation — `NaN` invoices impossible
>
> The `$NaN` invoice? Would have been a compile error.

Ren: "Good. Now type the package objects properly. Someone's been accessing `.address.zipCode` on packages that don't have an address field."

---

## What You Learned

- **Primitive types** (`string`, `number`, `boolean`) prevent cross-type operations
- **Literal types** (`"CREATED" | "DELIVERED"`) restrict values to specific options
- **Type narrowing** — TypeScript follows your `if`/`typeof`/`in` checks and narrows automatically
- **`any`** disables type checking — avoid it. **`unknown`** forces you to validate first.
- **Validate at boundaries** (API input, form data, DB rows) — then use strict types internally
- **Template literal types** can enforce string patterns
- JavaScript's silent coercion (`"12.5kg" * 2.5 = NaN`) becomes a compile error in TypeScript

---

[Next: Chapter 3 — "An Object is Missing a Field" →](chapter-03-interfaces.md)
