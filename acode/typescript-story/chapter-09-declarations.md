# Chapter 9: A Library Has No Types

[← Chapter 8: A Refactor Breaks 200 Files](chapter-08-utility-types.md) | [Chapter 10: Strict Mode →](chapter-10-strict-mode.md)

---

## The Disaster

You need to integrate `shipping-rates-calc` — a JavaScript library that calculates shipping costs based on weight, dimensions, and destination zone. It's well-maintained, fast, and has no TypeScript types.

```typescript
import { calculateRate } from "shipping-rates-calc";
// Error: Could not find a declaration file for module 'shipping-rates-calc'.
// 'node_modules/shipping-rates-calc/index.js' implicitly has an 'any' type.
```

You could slap `// @ts-ignore` on it. That's what the previous developer did — 47 times. You're not doing that.

---

## Option 1: Check DefinitelyTyped

Most popular libraries have community-maintained types in the `@types` namespace:

```bash
npm install --save-dev @types/shipping-rates-calc
```

If this works, you're done. The types are automatically picked up by TypeScript.

```typescript
// After installing @types/shipping-rates-calc:
import { calculateRate } from "shipping-rates-calc";
// ✓ No error — types are found in @types/shipping-rates-calc
```

**Check first:** [npmjs.com/~types](https://www.npmjs.com/~types) or just try `npm install @types/<package-name>`.

But `shipping-rates-calc` is niche. No `@types` package exists. Time for Option 2.

---

## Option 2: Write a Declaration File

A `.d.ts` file tells TypeScript the shape of a JavaScript module without modifying the library.

First, read the library's docs or source to understand its API:

```javascript
// What shipping-rates-calc actually exports (from its README):
// calculateRate(options) → { cost, currency, estimatedDays }
// options: { weight, dimensions: { l, w, h }, zone, service }
// getZone(originCountry, destCountry) → number
// SERVICES: { STANDARD: 'standard', EXPRESS: 'express', OVERNIGHT: 'overnight' }
```

Now write the declaration:

```typescript
// src/types/shipping-rates-calc.d.ts

declare module "shipping-rates-calc" {
  interface Dimensions {
    l: number;  // length in cm
    w: number;  // width in cm
    h: number;  // height in cm
  }

  type ServiceType = "standard" | "express" | "overnight";

  interface RateOptions {
    weight: number;          // kg
    dimensions: Dimensions;
    zone: number;            // 1-9
    service: ServiceType;
  }

  interface RateResult {
    cost: number;
    currency: string;
    estimatedDays: number;
  }

  export function calculateRate(options: RateOptions): RateResult;
  export function getZone(originCountry: string, destCountry: string): number;

  export const SERVICES: {
    STANDARD: "standard";
    EXPRESS: "express";
    OVERNIGHT: "overnight";
  };
}
```

Now TypeScript knows the library's shape:

```typescript
import { calculateRate, getZone, SERVICES } from "shipping-rates-calc";

const zone = getZone("CN", "NL");
const rate = calculateRate({
  weight: 12.5,
  dimensions: { l: 40, w: 30, h: 20 },
  zone,
  service: SERVICES.EXPRESS,
});

console.log(`Cost: ${rate.currency} ${rate.cost}`);  // ✓ Fully typed
console.log(`Delivery: ${rate.estimatedDays} days`); // ✓ TypeScript knows this is number

calculateRate({ weight: "heavy" });
// Error: Type 'string' is not assignable to type 'number'
```

### Where to Put Declaration Files

```
src/
├── types/
│   └── shipping-rates-calc.d.ts   ← custom declarations
├── index.ts
└── ...
```

Make sure `tsconfig.json` includes the types directory:

```json
{
  "compilerOptions": {
    "typeRoots": ["./src/types", "./node_modules/@types"]
  }
}
```

Or simply place `.d.ts` files anywhere in your `include` path — TypeScript finds them automatically.

---

## Option 3: Module Augmentation

Sometimes a library *has* types but they're incomplete. You can extend them:

```typescript
// The library exports a Package type but forgot the 'priority' field
// that was added in v2.3

// src/types/augment-shipping.d.ts
import "shipping-rates-calc";

declare module "shipping-rates-calc" {
  // Add to the existing interface
  interface RateOptions {
    priority?: 1 | 2 | 3;  // Added in v2.3, not in types yet
  }

  interface RateResult {
    trackingAvailable: boolean;  // Also missing from types
  }
}
```

Module augmentation **merges** with existing declarations. The original types still work — you're adding to them.

---

## Global Type Declarations

For things that exist globally (environment variables, window extensions, global utilities):

```typescript
// src/types/global.d.ts

// Type environment variables
declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: "development" | "production" | "test";
    PORT: string;
    DATABASE_URL: string;
    CARRIER_API_KEY: string;
  }
}

// Now process.env is typed:
const port = parseInt(process.env.PORT);  // ✓ TypeScript knows PORT is string
process.env.NONEXISTENT;
// Error: Property 'NONEXISTENT' does not exist on type 'ProcessEnv'
```

---

## Typing a JSON Import

```typescript
// src/types/json.d.ts
declare module "*.json" {
  const value: unknown;
  export default value;
}

// Or more specific for a known config file:
// src/types/config.d.ts
declare module "../config/zones.json" {
  const zones: Record<string, number>;
  export default zones;
}
```

---

## Wrapping an Untyped Library

Sometimes writing a full declaration file is overkill. Wrap the library in a typed adapter:

```typescript
// src/shipping-adapter.ts
// Only expose the parts we actually use, fully typed

// eslint-disable-next-line @typescript-eslint/no-var-requires
const lib = require("shipping-rates-calc") as {
  calculateRate: (opts: RateInput) => RateOutput;
  getZone: (from: string, to: string) => number;
};

interface RateInput {
  weight: number;
  dimensions: { l: number; w: number; h: number };
  zone: number;
  service: "standard" | "express" | "overnight";
}

interface RateOutput {
  cost: number;
  currency: string;
  estimatedDays: number;
}

export function getShippingRate(
  weight: number,
  dimensions: { length: number; width: number; height: number },
  originCountry: string,
  destCountry: string,
  service: "standard" | "express" | "overnight" = "standard"
): RateOutput {
  const zone = lib.getZone(originCountry, destCountry);
  return lib.calculateRate({
    weight,
    dimensions: { l: dimensions.length, w: dimensions.width, h: dimensions.height },
    zone,
    service,
  });
}
```

The rest of your codebase imports from `./shipping-adapter` — fully typed, no `any` leaking out.

---

## The Quick Escape: `declare module`

When you just need the error to go away while you figure out the types:

```typescript
// src/types/temp.d.ts
// TODO: Write proper types for these
declare module "shipping-rates-calc";
declare module "legacy-tracking-lib";
```

This tells TypeScript "this module exists" but types everything as `any`. It's a stepping stone, not a solution. Remove these as you write proper declarations.

---

## Decision Tree

```
Does the library have built-in types? (check package.json "types" field)
  ├── Yes → You're done. Import and use.
  └── No
      ├── Does @types/<package> exist? (npm install @types/<package>)
      │   ├── Yes → Install it. Done.
      │   └── No
      │       ├── Is the library's API small? (< 10 functions)
      │       │   ├── Yes → Write a .d.ts declaration file
      │       │   └── No → Write a typed wrapper/adapter
      │       └── Are you in a hurry?
      │           └── declare module "package" (temporary, fix later)
```

---

## Report to Ren

> **Untyped library integrated:**
> - `shipping-rates-calc` has no `@types` package
> - Wrote `shipping-rates-calc.d.ts` with full type declarations
> - All usages are now type-checked — wrong weight types, missing dimensions caught at compile time
> - Environment variables typed via global declaration — no more `process.env.TYPO`
>
> Zero `// @ts-ignore` comments. Zero `any` leaking into the codebase.

Ren: "The migration is almost done. One last step — turn on `strict: true` and fix whatever breaks. That's when you'll know the codebase is truly typed."

---

## What You Learned

- **`@types/<package>`** — check DefinitelyTyped first, it covers most popular libraries
- **Declaration files (`.d.ts`)** — describe a JS library's shape without modifying it
- **`declare module "x"`** — tells TypeScript about a module's exports
- **Module augmentation** — extend existing type declarations with missing fields
- **Global declarations** — type `process.env`, `window` extensions, etc.
- **Typed wrappers** — isolate untyped code behind a typed adapter
- **`declare module "x"`** (empty) — temporary escape hatch, types as `any`
- The goal: zero `any` leaking from external boundaries into your typed code

---

[Next: Chapter 10 — "Strict Mode" →](chapter-10-strict-mode.md)
