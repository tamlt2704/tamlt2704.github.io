# Chapter 10: Strict Mode

[← Chapter 9: A Library Has No Types](chapter-09-declarations.md)

---

## The Task

Ren's final message:

> "Turn on `strict: true`. Fix everything that breaks. When it compiles clean, the migration is done."

You've been running with `strict: false` for 9 chapters. TypeScript has been lenient — allowing implicit `any`, unchecked nulls, and loose function types. Strict mode turns on every safety check at once.

You flip the switch. 312 errors.

Deep breath. Let's go.

---

## What `strict: true` Enables

`strict: true` is a shorthand for these individual flags:

```json
{
  "compilerOptions": {
    "strict": true
    // Equivalent to ALL of these:
    // "noImplicitAny": true,
    // "strictNullChecks": true,
    // "strictFunctionTypes": true,
    // "strictBindCallApply": true,
    // "strictPropertyInitialization": true,
    // "noImplicitThis": true,
    // "useUnknownInCatchVariables": true,
    // "alwaysStrict": true
  }
}
```

Let's tackle each one.

---

## `noImplicitAny`: No More Guessing

Without this flag, untyped parameters silently become `any`:

```typescript
// ❌ Before strict: this compiles fine (parameter is implicitly 'any')
function processPackage(pkg) {
  return pkg.whatever.you.want;  // No error — 'any' disables all checks
}

// ✓ After strict: must annotate
function processPackage(pkg: Package): void {
  return pkg.status;  // TypeScript checks this exists
}
```

**The fix:** Add type annotations to every function parameter that doesn't have one.

```typescript
// Common patterns that trigger noImplicitAny:

// Array callbacks
packages.forEach(pkg => { /* pkg was implicitly any */ });
// Fix: TypeScript infers from the array type — usually no change needed

// Event handlers
button.addEventListener("click", (e) => { /* e was implicitly any */ });
// Fix: TypeScript infers Event — usually no change needed

// Object destructuring from untyped sources
const { id, weight } = getPackageData();
// Fix: type the function's return value

// The real offenders: function parameters
function calculate(data, options) { /* both implicitly any */ }
// Fix: function calculate(data: PackageData, options: CalcOptions) { }
```

---

## `strictNullChecks`: Null is Not Invisible

This is the big one. Without it, `null` and `undefined` are assignable to every type:

```typescript
// ❌ Without strictNullChecks:
let name: string = null;      // Fine! (but wrong)
let weight: number = undefined; // Fine! (but wrong)

// ✓ With strictNullChecks:
let name: string = null;
// Error: Type 'null' is not assignable to type 'string'

let name: string | null = null;  // ✓ Explicit
```

Every function that might return `null` or `undefined` must declare it:

```typescript
// ❌ Before: return type is 'Package' but actually returns undefined sometimes
function findPackage(id: string): Package {
  return packages.find(p => p.id === id);  // .find() returns T | undefined!
}

// ✓ After: honest return type
function findPackage(id: string): Package | undefined {
  return packages.find(p => p.id === id);
}
```

**The fix patterns:**

```typescript
// Pattern 1: Early return
function getStatus(id: string): string {
  const pkg = findPackage(id);
  if (!pkg) return "UNKNOWN";
  return pkg.status;
}

// Pattern 2: Non-null assertion (use sparingly — you're telling TypeScript "trust me")
function getStatus(id: string): string {
  const pkg = findPackage(id);
  return pkg!.status;  // ! means "I guarantee this isn't null"
  // ⚠️ If you're wrong, it crashes at runtime. Use only when you're certain.
}

// Pattern 3: Optional chaining + nullish coalescing
function getCity(pkg: Package | undefined): string {
  return pkg?.sender?.city ?? "Unknown";
}

// Pattern 4: Throw on null (for cases that should never happen)
function getPackageOrThrow(id: string): Package {
  const pkg = findPackage(id);
  if (!pkg) throw new Error(`Package ${id} not found`);
  return pkg;  // TypeScript knows it's Package here (not undefined)
}
```

---

## `strictPropertyInitialization`: Initialize Your Fields

Class properties must be initialized in the constructor:

```typescript
// ❌ Before strict:
class PackageTracker {
  packages: Package[];  // Never initialized — undefined at runtime!

  addPackage(pkg: Package) {
    this.packages.push(pkg);  // Runtime: Cannot read properties of undefined
  }
}

// ✓ After strict:
class PackageTracker {
  packages: Package[] = [];  // Initialized with default

  // Or initialize in constructor:
  private db: Database;

  constructor(db: Database) {
    this.db = db;
  }
}

// If initialization happens elsewhere (e.g., async init), use definite assignment:
class PackageTracker {
  packages!: Package[];  // ! = "I'll initialize this before use, trust me"

  async init() {
    this.packages = await loadFromDb();
  }
}
```

---

## `strictFunctionTypes`: Function Compatibility

This prevents subtle bugs with callback types:

```typescript
interface Animal { name: string }
interface Dog extends Animal { breed: string }

// ❌ Without strictFunctionTypes: this is allowed (unsound!)
type AnimalHandler = (animal: Animal) => void;
const dogHandler: AnimalHandler = (dog: Dog) => {
  console.log(dog.breed);  // Crashes if called with a Cat!
};

// ✓ With strictFunctionTypes: correctly rejected
// Error: Type '(dog: Dog) => void' is not assignable to type '(animal: Animal) => void'
```

**The fix:** Make callbacks accept the broader type, or use generics.

---

## `useUnknownInCatchVariables`: Errors Aren't `any`

```typescript
// ❌ Before: catch variable is 'any'
try {
  await fetchPackage(id);
} catch (error) {
  console.log(error.message);  // No error — but 'error' might not have .message
}

// ✓ After: catch variable is 'unknown'
try {
  await fetchPackage(id);
} catch (error) {
  // Must narrow before using
  if (error instanceof Error) {
    console.log(error.message);  // ✓ Safe
  } else {
    console.log("Unknown error:", error);
  }
}
```

---

## The Migration Strategy

Don't fix 312 errors at once. Enable strict flags one at a time:

```json
{
  "compilerOptions": {
    "strict": false,
    "noImplicitAny": true,           // Week 1: fix these first
    "strictNullChecks": false,        // Week 2: the big one
    "strictFunctionTypes": false,     // Week 3: usually few errors
    "strictPropertyInitialization": false,  // Week 4: class fixes
    "useUnknownInCatchVariables": false     // Week 5: catch blocks
  }
}
```

Fix one flag at a time. Once all are `true`, replace with `"strict": true`.

---

## The Final `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,

    "strict": true,

    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,

    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### The Extra Flags (Beyond Strict)

| Flag | What It Does |
|---|---|
| `noUncheckedIndexedAccess` | `arr[0]` is `T \| undefined`, not `T` — forces bounds checking |
| `noUnusedLocals` | Error on unused variables |
| `noUnusedParameters` | Error on unused function parameters |
| `noFallthroughCasesInSwitch` | Error on switch cases without break/return |
| `exactOptionalPropertyTypes` | `{ x?: string }` means "missing or string", not "missing or string or undefined" |

---

## The Migration is Done

```bash
npx tsc --noEmit
# No errors. Clean build.
```

The codebase that started as 12,000 lines of untyped JavaScript is now fully typed TypeScript with strict mode. Every function has typed parameters. Every null is handled. Every external boundary is validated.

---

## Before and After

```typescript
// ── BEFORE (JavaScript) ─────────────────────────
function processShipment(data) {
  const pkg = getPackage(data.id);
  const rate = calculateRate(pkg.weight, data.zone);
  return { cost: rate, delivery: pkg.estimatedDate.toISOString() };
}
// Bugs: data could be anything, pkg could be undefined,
// estimatedDate could be null, rate could be NaN

// ── AFTER (TypeScript, strict) ──────────────────
function processShipment(data: ShipmentRequest): Result<ShipmentResponse, ShipmentError> {
  const pkg = findPackage(data.id);
  if (!pkg) {
    return { ok: false, error: { code: "NOT_FOUND", message: `Package ${data.id} not found` } };
  }

  const rate = calculateRate({
    weight: pkg.weight,
    dimensions: pkg.dimensions,
    zone: data.zone,
    service: data.service,
  });

  return {
    ok: true,
    value: {
      cost: rate.cost,
      currency: rate.currency,
      estimatedDelivery: pkg.estimatedDelivery?.toISOString() ?? null,
    },
  };
}
// Every edge case handled. Every type checked. Compiles = works.
```

---

## Report to Ren

> **Migration complete. Strict mode enabled.**
>
> | Metric | Before | After |
> |---|---|---|
> | `// @ts-ignore` comments | 47 | 0 |
> | Implicit `any` types | ~400 | 0 |
> | Unhandled null accesses | ~120 | 0 |
> | Runtime type errors (last month) | 23 | 0 |
> | `strict: true` | ❌ | ✓ |
>
> The compiler is now the strictest code reviewer on the team. It catches bugs before they reach a PR, let alone production.

Ren: "Welcome to TypeScript. You'll never go back."

---

## What You Learned (Series Recap)

1. **TypeScript = JavaScript + types** — compiles to JS, zero runtime cost
2. **Type annotations** on function boundaries catch bugs at build time
3. **Primitives and literals** prevent cross-type operations and restrict values
4. **Interfaces** describe object shapes — missing fields are compile errors
5. **Function types** enforce input/output contracts across the codebase
6. **Generics** eliminate duplication while preserving type information
7. **Discriminated unions** model domain states — exhaustive checks prevent forgotten cases
8. **Type guards** validate external data at runtime while narrowing types at compile time
9. **Utility types** transform types without rewriting — `Partial`, `Pick`, `Omit`, `Record`
10. **Declaration files** bring type safety to untyped JavaScript libraries
11. **Strict mode** is the finish line — every null handled, every type explicit

---

## Next Steps (If You Keep Going)

- **Advanced generics** — conditional types, infer, template literal types
- **Decorators** — metadata and metaprogramming (Stage 3 proposal, supported in TS 5+)
- **Project references** — monorepo TypeScript with incremental builds
- **Type-level programming** — branded types, phantom types, type-safe builders
- **Framework-specific patterns** — React props, Express middleware, Prisma schemas

But that's another series.

---

*The compiler is your co-pilot. Trust it. Fight it. Learn from it. Ship with confidence.*
