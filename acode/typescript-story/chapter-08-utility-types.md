# Chapter 8: A Refactor Breaks 200 Files

[← Chapter 7: The API Response Doesn't Match](chapter-07-type-guards.md) | [Chapter 9: A Library Has No Types →](chapter-09-declarations.md)

---

## The Disaster

Ren asks you to rename `origin` → `sender` and `destination` → `recipient` in the `Package` interface. "Better domain language," he says.

You change the interface. `tsc` reports 247 errors across 83 files. Every place that reads `pkg.origin` or `pkg.destination` is now broken.

This is actually a *good* thing — the compiler found every reference. In JavaScript, you'd rename the field, miss 12 usages, and discover them in production over the next month.

But 247 errors is a lot. You need tools to make large-scale type changes manageable.

---

## Utility Types: Transform Types Without Rewriting Them

TypeScript ships with built-in utility types that derive new types from existing ones. They're the power tools of refactoring.

### `Partial<T>` — Make All Properties Optional

```typescript
interface Package {
  id: string;
  sender: string;
  recipient: string;
  weight: number;
  status: PackageStatus;
}

// Partial<Package> = all fields optional
type PackageUpdate = Partial<Package>;
// Equivalent to:
// {
//   id?: string;
//   sender?: string;
//   recipient?: string;
//   weight?: number;
//   status?: PackageStatus;
// }

function updatePackage(id: string, changes: Partial<Package>): Package {
  const existing = findById(id);
  return { ...existing, ...changes };
}

// Caller can pass any subset of fields
updatePackage("SF-001", { weight: 15.0 });           // ✓
updatePackage("SF-001", { status: "DELIVERED" });     // ✓
updatePackage("SF-001", { color: "red" });
// Error: 'color' does not exist in type 'Partial<Package>'
```

### `Required<T>` — Make All Properties Required

```typescript
interface Config {
  host?: string;
  port?: number;
  debug?: boolean;
}

// After merging with defaults, all fields are guaranteed present
type ResolvedConfig = Required<Config>;
// { host: string; port: number; debug: boolean }

function resolveConfig(input: Config): ResolvedConfig {
  return {
    host: input.host ?? "localhost",
    port: input.port ?? 3000,
    debug: input.debug ?? false,
  };
}
```

### `Pick<T, Keys>` — Select Specific Properties

```typescript
// Only expose what the frontend needs
type PackageSummary = Pick<Package, "id" | "status" | "recipient">;
// { id: string; status: PackageStatus; recipient: string }

function getPackageSummaries(): PackageSummary[] {
  return packages.map(pkg => ({
    id: pkg.id,
    status: pkg.status,
    recipient: pkg.recipient,
  }));
}
```

### `Omit<T, Keys>` — Remove Specific Properties

```typescript
// For creating a package, the ID is generated — don't accept it as input
type CreatePackageInput = Omit<Package, "id" | "status">;
// { sender: string; recipient: string; weight: number }

function createPackage(input: CreatePackageInput): Package {
  return {
    ...input,
    id: generateId(),
    status: "CREATED",
  };
}
```

### `Record<Keys, Value>` — Object with Known Keys

```typescript
// Map status to display color
type StatusColor = Record<PackageStatus["type"], string>;
// { CREATED: string; PICKED_UP: string; IN_TRANSIT: string; ... }

const statusColors: Record<string, string> = {
  CREATED: "#888",
  PICKED_UP: "#4ec9b0",
  IN_TRANSIT: "#2496ed",
  OUT_FOR_DELIVERY: "#e6a700",
  DELIVERED: "#28c840",
};
```

---

## `keyof` and `typeof`: Types from Values

### `keyof` — Get Property Names as a Union

```typescript
type PackageKeys = keyof Package;
// "id" | "sender" | "recipient" | "weight" | "status"

// Type-safe property access
function getField(pkg: Package, field: keyof Package): Package[keyof Package] {
  return pkg[field];
}

getField(pkg, "weight");    // ✓
getField(pkg, "color");
// Error: Argument of type '"color"' is not assignable to type 'keyof Package'
```

### `typeof` — Extract Type from a Value

```typescript
// You have a config object — derive the type from it
const defaultConfig = {
  host: "localhost",
  port: 3000,
  debug: false,
  maxRetries: 3,
} as const;

type Config = typeof defaultConfig;
// { readonly host: "localhost"; readonly port: 3000; readonly debug: false; readonly maxRetries: 3 }

// Without 'as const':
type Config = typeof defaultConfig;
// { host: string; port: number; debug: boolean; maxRetries: number }
```

`as const` makes TypeScript infer literal types instead of widening to `string`/`number`/`boolean`.

---

## Mapped Types: Transform Every Property

```typescript
// Make every property in T nullable
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};

type NullablePackage = Nullable<Package>;
// { id: string | null; sender: string | null; weight: number | null; ... }

// Make every property a getter function
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type PackageGetters = Getters<Package>;
// { getId: () => string; getSender: () => string; getWeight: () => number; ... }
```

---

## Conditional Types: Types That Branch

```typescript
// Extract the element type from an array
type ElementOf<T> = T extends (infer E)[] ? E : never;

type A = ElementOf<string[]>;    // string
type B = ElementOf<Package[]>;   // Package
type C = ElementOf<number>;      // never (not an array)

// Extract the return type of a function
type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never;

type D = ReturnOf<typeof createPackage>;  // Package
```

TypeScript has built-in versions: `ReturnType<T>`, `Parameters<T>`, `Awaited<T>`.

```typescript
// Built-in utility types for functions
type CreateFn = typeof createPackage;

type CreateReturn = ReturnType<CreateFn>;      // Package
type CreateParams = Parameters<CreateFn>;      // [CreatePackageInput]
type CreateFirstArg = Parameters<CreateFn>[0]; // CreatePackageInput

// For async functions
async function fetchPackage(id: string): Promise<Package> { /* ... */ }
type FetchResult = Awaited<ReturnType<typeof fetchPackage>>;  // Package (unwraps Promise)
```

---

## The Refactor: Rename with Confidence

Back to the original task — renaming `origin` → `sender`, `destination` → `recipient`:

```typescript
// Step 1: Change the interface
interface Package {
  readonly id: string;
  sender: string;      // was: origin
  recipient: string;   // was: destination
  weight: number;
  status: PackageStatus;
  readonly createdAt: Date;
}

// Step 2: Run tsc — it shows every broken reference
// Step 3: Fix them all (IDE rename helps, but tsc is the safety net)

// Step 4: For backward compatibility with the API, create a mapping type
type LegacyPackage = Omit<Package, "sender" | "recipient"> & {
  origin: string;
  destination: string;
};

// Convert between old and new shapes
function fromLegacy(legacy: LegacyPackage): Package {
  const { origin, destination, ...rest } = legacy;
  return { ...rest, sender: origin, recipient: destination };
}

function toLegacy(pkg: Package): LegacyPackage {
  const { sender, recipient, ...rest } = pkg;
  return { ...rest, origin: sender, destination: recipient };
}
```

The compiler found all 247 references. You fixed them. The legacy API still works through the adapter. Zero runtime bugs.

---

## Template Literal Types in Mapped Types

```typescript
// Auto-generate event names from a type
type PackageEvents = {
  [K in keyof Package as `package:${string & K}Changed`]: (
    oldValue: Package[K],
    newValue: Package[K]
  ) => void;
};

// Result:
// {
//   "package:senderChanged": (old: string, new: string) => void;
//   "package:recipientChanged": (old: string, new: string) => void;
//   "package:weightChanged": (old: number, new: number) => void;
//   "package:statusChanged": (old: PackageStatus, new: PackageStatus) => void;
// }
```

---

## The Cheat Sheet

| Utility Type | What It Does | Use Case |
|---|---|---|
| `Partial<T>` | All properties optional | Update/patch operations |
| `Required<T>` | All properties required | After applying defaults |
| `Pick<T, K>` | Select specific properties | API response subsets |
| `Omit<T, K>` | Remove specific properties | Create inputs (omit ID) |
| `Record<K, V>` | Object with known keys and value type | Lookup maps |
| `Readonly<T>` | All properties readonly | Immutable data |
| `ReturnType<F>` | Extract function return type | Infer types from functions |
| `Parameters<F>` | Extract function parameter types | Wrapper functions |
| `Awaited<T>` | Unwrap Promise type | Async function results |
| `NonNullable<T>` | Remove null and undefined | After null checks |

---

## Report to Ren

> **Refactor complete:**
> - `origin` → `sender`, `destination` → `recipient` across 83 files
> - Compiler caught all 247 references — zero missed
> - Legacy API compatibility via adapter functions (`fromLegacy`/`toLegacy`)
> - Using `Partial<Package>` for updates, `Omit<Package, "id">` for creation
>
> In JavaScript, this refactor would have taken weeks of grep + pray. TypeScript made it a 2-hour task with zero runtime risk.

Ren: "Last thing — we're integrating a shipping rate library that has no TypeScript types. The package is JavaScript-only. Make it work without losing type safety."

---

## What You Learned

- **Utility types** transform existing types without rewriting them
- `Partial`, `Required`, `Pick`, `Omit` are the daily workhorses
- **`keyof`** extracts property names as a union type
- **`typeof`** extracts the type of a value (useful with `as const`)
- **Mapped types** transform every property in a type systematically
- **Conditional types** branch based on type relationships (`T extends X ? A : B`)
- **`as const`** preserves literal types instead of widening
- TypeScript's type system is a programming language itself — you can compute types from types
- Large refactors are safe because the compiler finds every reference

---

[Next: Chapter 9 — "A Library Has No Types" →](chapter-09-declarations.md)
