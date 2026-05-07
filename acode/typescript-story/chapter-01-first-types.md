# Chapter 1: `undefined is not a function`

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: A String Sneaks In →](chapter-02-primitives.md)

---

## The Disaster

It's your first Monday. You're reading the JavaScript codebase. You find this:

```javascript
// src/tracking.js
function getPackage(id) {
  return packages.find(p => p.id === id);
}

function getDeliveryDate(id) {
  const pkg = getPackage(id);
  return pkg.estimatedDelivery.toISOString();
}
```

Looks fine. Works in dev. Ships to production.

At 2:47am, a customer enters a tracking ID that doesn't exist. `getPackage` returns `undefined`. The next line calls `.estimatedDelivery` on `undefined`. The API crashes. 400 customers get a 500 error.

The fix in JavaScript? Add a null check. Hope you remember next time.

The fix in TypeScript? Make it **impossible to forget**.

---

## Your First TypeScript File

```typescript
// src/tracking.ts
interface Package {
  id: string;
  origin: string;
  destination: string;
  weight: number;
  estimatedDelivery: Date;
}

const packages: Package[] = [
  {
    id: "SF-2024-00042",
    origin: "Shanghai",
    destination: "Rotterdam",
    weight: 12.5,
    estimatedDelivery: new Date("2024-04-15"),
  },
];

function getPackage(id: string): Package | undefined {
  return packages.find(p => p.id === id);
}
```

Notice the return type: `Package | undefined`. TypeScript forces you to declare that this function might not find anything. Now watch what happens:

```typescript
function getDeliveryDate(id: string): string {
  const pkg = getPackage(id);
  return pkg.estimatedDelivery.toISOString();
  //     ^^^ Error: 'pkg' is possibly 'undefined'
}
```

The compiler catches it. Before you run the code. Before it reaches production. Before 400 customers get a 500 error.

### The Fix

```typescript
function getDeliveryDate(id: string): string | null {
  const pkg = getPackage(id);
  if (!pkg) {
    return null; // Explicitly handle the missing case
  }
  return pkg.estimatedDelivery.toISOString();
}
```

Now the caller knows this function might return `null` — and TypeScript will force *them* to handle it too. The null check propagates up the chain. No one can forget.

---

## Setting Up the Project

```bash
mkdir -p src
```

Create `src/index.ts`:

```typescript
// src/index.ts
console.log("ShipFast API starting...");

// Basic type annotations
const companyName: string = "ShipFast";
const foundedYear: number = 2022;
const isOperational: boolean = true;

console.log(`${companyName} (est. ${foundedYear}) — operational: ${isOperational}`);
```

Run it:

```bash
npx tsx src/index.ts
```

```
ShipFast API starting...
ShipFast (est. 2022) — operational: true
```

### Compile It

```bash
npx tsc
```

This creates `dist/index.js` — plain JavaScript with all types stripped out. TypeScript is a *build-time* tool. At runtime, it's just JavaScript.

```bash
node dist/index.js  # Same output, no TypeScript needed at runtime
```

---

## Type Annotations: The Basics

```typescript
// You can annotate variables
let trackingId: string = "SF-2024-00042";
let weight: number = 12.5;
let isDelivered: boolean = false;
let deliveryDate: Date = new Date("2024-04-15");

// Arrays
let trackingIds: string[] = ["SF-2024-00042", "SF-2024-00043"];
let weights: number[] = [12.5, 8.3, 22.1];

// TypeScript infers types when you assign immediately
let city = "Rotterdam";      // TypeScript knows this is string
let count = 42;              // TypeScript knows this is number
let items = ["a", "b"];      // TypeScript knows this is string[]
```

Rule: **annotate function parameters and return types. Let TypeScript infer the rest.**

```typescript
// ✓ Good: annotate parameters and return
function calculateShipping(weight: number, distance: number): number {
  return weight * 0.5 + distance * 0.01;
}

// ✗ Unnecessary: TypeScript already infers the variable type
const cost: number = calculateShipping(12.5, 8000); // redundant annotation
const cost = calculateShipping(12.5, 8000);          // TypeScript infers number
```

---

## What TypeScript Catches

```typescript
// ── Type mismatches ─────────────────────────────
let weight: number = 12.5;
weight = "heavy";
// Error: Type 'string' is not assignable to type 'number'

// ── Wrong argument types ────────────────────────
function ship(destination: string, weight: number): void {
  console.log(`Shipping ${weight}kg to ${destination}`);
}

ship(42, "Rotterdam");
// Error: Argument of type 'number' is not assignable to parameter of type 'string'

// ── Missing properties ──────────────────────────
interface Address {
  street: string;
  city: string;
  country: string;
}

const addr: Address = {
  street: "123 Port Road",
  city: "Rotterdam",
};
// Error: Property 'country' is missing in type

// ── Accessing properties that don't exist ───────
const pkg = { id: "SF-001", weight: 12.5 };
console.log(pkg.destination);
// Error: Property 'destination' does not exist on type '{ id: string; weight: number; }'
```

Every one of these would silently succeed in JavaScript — and fail at runtime.

---

## The `tsconfig.json` Explained

```json
{
  "compilerOptions": {
    "target": "ES2022",          // What JS version to emit
    "module": "NodeNext",        // Module system (ESM for Node)
    "moduleResolution": "NodeNext", // How to find imports
    "outDir": "./dist",          // Where compiled JS goes
    "rootDir": "./src",          // Where source TS lives
    "strict": false,             // We'll turn this on in Ch10
    "esModuleInterop": true,     // Fixes CommonJS/ESM interop
    "skipLibCheck": true,        // Don't type-check node_modules
    "forceConsistentCasingInFileNames": true  // Prevents case bugs on macOS
  },
  "include": ["src/**/*"]
}
```

For now, `strict: false` means TypeScript is lenient. It won't complain about implicit `any` types or unchecked nulls (unless you annotate them explicitly). We'll tighten this as we learn.

---

## Migrating the First File

Here's the original JavaScript:

```javascript
// BEFORE: src/utils.js
function formatTrackingId(prefix, number) {
  return `${prefix}-${new Date().getFullYear()}-${String(number).padStart(5, "0")}`;
}

function parseWeight(input) {
  const num = parseFloat(input);
  if (isNaN(num)) return null;
  if (num < 0) return null;
  return num;
}

module.exports = { formatTrackingId, parseWeight };
```

And the TypeScript version:

```typescript
// AFTER: src/utils.ts
export function formatTrackingId(prefix: string, number: number): string {
  return `${prefix}-${new Date().getFullYear()}-${String(number).padStart(5, "0")}`;
}

export function parseWeight(input: string): number | null {
  const num = parseFloat(input);
  if (isNaN(num)) return null;
  if (num < 0) return null;
  return num;
}
```

Changes:
1. Parameter types added (`prefix: string`, `number: number`, `input: string`)
2. Return types declared (`string`, `number | null`)
3. `module.exports` → `export` (ESM)

Now anyone calling `parseWeight` knows it might return `null` — and the compiler enforces handling it.

---

## Run the Tests

Add to `package.json`:

```json
{
  "scripts": {
    "build": "tsc",
    "dev": "tsx watch src/index.ts",
    "test": "vitest run"
  }
}
```

Create `src/utils.test.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { formatTrackingId, parseWeight } from "./utils";

describe("formatTrackingId", () => {
  it("formats with zero-padded number", () => {
    const id = formatTrackingId("SF", 42);
    expect(id).toMatch(/^SF-\d{4}-00042$/);
  });
});

describe("parseWeight", () => {
  it("parses valid numbers", () => {
    expect(parseWeight("12.5")).toBe(12.5);
  });

  it("returns null for non-numbers", () => {
    expect(parseWeight("banana")).toBeNull();
  });

  it("returns null for negative weights", () => {
    expect(parseWeight("-5")).toBeNull();
  });
});
```

```bash
npx vitest run
```

```
 ✓ src/utils.test.ts (3 tests) 2ms
 Tests  3 passed
```

---

## Report to Ren

> **First file migrated:**
> - `utils.js` → `utils.ts` — all functions typed
> - `getPackage` now returns `Package | undefined` — impossible to forget null checks
> - Compiler catches type mismatches, missing properties, wrong arguments
> - Tests passing
>
> The 2am crash? Would have been caught at compile time. Zero runtime cost.

Ren: "Good start. Now migrate the package creation endpoint. Someone's been passing strings where numbers should go."

---

## What You Learned

- TypeScript = JavaScript + types. It compiles to plain JS. Zero runtime overhead.
- **Type annotations** on function parameters and return types catch bugs at build time
- `| undefined` and `| null` force callers to handle missing values
- `tsc` compiles TypeScript to JavaScript; `tsx` runs it directly for development
- `tsconfig.json` configures the compiler — start lenient, tighten over time
- TypeScript **infers** types from assignments — you don't need to annotate everything
- The migration path: rename `.js` → `.ts`, add types, fix errors. One file at a time.

---

[Next: Chapter 2 — "A String Sneaks In" →](chapter-02-primitives.md)
