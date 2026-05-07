# Chapter 4: A Function Returns the Wrong Shape

[← Chapter 3: An Object is Missing a Field](chapter-03-interfaces.md) | [Chapter 5: Copy-Pasting the Same Function →](chapter-05-generics.md)

---

## The Disaster

The API has two response shapes. Some endpoints return:

```json
{ "success": true, "data": { ... } }
```

Others return:

```json
{ "ok": true, "package": { ... } }
```

The frontend checks `response.success` — which is `undefined` for half the endpoints. Features silently fail. Nobody notices until a customer reports that tracking updates "just stopped working."

Ren's PR comment: "Pick one response shape. Type it. Enforce it everywhere."

---

## Function Type Annotations

```typescript
// src/api.ts

// Basic function types
function calculateShipping(weight: number, zone: number): number {
  return weight * 2.5 + zone * 10;
}

// Arrow function with types
const formatCurrency = (amount: number, currency: string = "USD"): string => {
  return `${currency} ${amount.toFixed(2)}`;
};

// Function that doesn't return anything
function logShipment(id: string, message: string): void {
  console.log(`[${id}] ${message}`);
  // void means "I don't return a value" — different from undefined
}
```

### `void` vs `undefined` vs `never`

```typescript
// void: function doesn't return a meaningful value
function log(msg: string): void {
  console.log(msg);
}

// undefined: function explicitly returns undefined
function findIndex(arr: string[], target: string): number | undefined {
  const idx = arr.indexOf(target);
  return idx === -1 ? undefined : idx;
}

// never: function NEVER returns (throws or infinite loop)
function throwError(message: string): never {
  throw new Error(message);
}

function infiniteLoop(): never {
  while (true) {
    // process events forever
  }
}
```

`never` is useful for exhaustive checks — we'll see that in Chapter 6.

---

## The Unified API Response

```typescript
// src/response.ts

// Success response
interface ApiSuccess<T> {
  success: true;
  data: T;
  timestamp: string;
}

// Error response
interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
  };
  timestamp: string;
}

// Every endpoint returns one of these
type ApiResponse<T> = ApiSuccess<T> | ApiError;

// Helper to create responses
function success<T>(data: T): ApiSuccess<T> {
  return {
    success: true,
    data,
    timestamp: new Date().toISOString(),
  };
}

function error(code: string, message: string): ApiError {
  return {
    success: false,
    error: { code, message },
    timestamp: new Date().toISOString(),
  };
}
```

Now every endpoint is forced to return `ApiResponse<T>`:

```typescript
function getPackage(id: string): ApiResponse<Package> {
  const pkg = packages.find(p => p.id === id);
  if (!pkg) {
    return error("NOT_FOUND", `Package ${id} not found`);
  }
  return success(pkg);
}

// The frontend can now reliably check:
const response = await getPackage("SF-2024-00042");
if (response.success) {
  // TypeScript knows response.data exists and is Package
  console.log(response.data.status);
} else {
  // TypeScript knows response.error exists
  console.log(response.error.message);
}
```

No more `response.ok` vs `response.success` confusion. One shape. Enforced by the compiler.

---

## Function Overloads

Sometimes a function behaves differently based on its inputs. TypeScript lets you declare multiple signatures:

```typescript
// Overload signatures (what callers see)
function parseTrackingId(input: string): { prefix: string; year: number; sequence: number };
function parseTrackingId(input: string[]): { prefix: string; year: number; sequence: number }[];

// Implementation signature (must handle all overloads)
function parseTrackingId(
  input: string | string[]
): { prefix: string; year: number; sequence: number } | { prefix: string; year: number; sequence: number }[] {
  if (Array.isArray(input)) {
    return input.map(id => parseSingle(id));
  }
  return parseSingle(input);
}

function parseSingle(id: string) {
  const [prefix, yearStr, seqStr] = id.split("-");
  return { prefix, year: parseInt(yearStr), sequence: parseInt(seqStr) };
}

// Callers get precise return types:
const single = parseTrackingId("SF-2024-00042");
// Type: { prefix: string; year: number; sequence: number }

const batch = parseTrackingId(["SF-2024-00042", "SF-2024-00043"]);
// Type: { prefix: string; year: number; sequence: number }[]
```

Overloads are useful but verbose. Prefer generics (Chapter 5) when possible.

---

## Callback Types

Functions that accept other functions:

```typescript
// Type the callback explicitly
function onStatusChange(
  packageId: string,
  callback: (oldStatus: PackageStatus, newStatus: PackageStatus) => void
): void {
  // ... register the callback
}

// Usage — TypeScript checks the callback signature
onStatusChange("SF-2024-00042", (old, next) => {
  // TypeScript infers: old is PackageStatus, next is PackageStatus
  console.log(`${old} → ${next}`);
});

// Wrong callback shape:
onStatusChange("SF-2024-00042", (status) => {
  // ✓ Fine — you can ignore parameters
});

onStatusChange("SF-2024-00042", (a, b, c) => {
  // Error: callback expects 2 parameters, got 3
});
```

### Named Function Types

```typescript
// Define a reusable function type
type StatusHandler = (oldStatus: PackageStatus, newStatus: PackageStatus) => void;
type Validator<T> = (input: unknown) => T | null;
type AsyncFetcher<T> = (id: string) => Promise<T>;

// Use it
function registerHandler(event: string, handler: StatusHandler): void {
  // ...
}
```

---

## Async Functions

```typescript
// Async functions return Promise<T>
async function fetchPackage(id: string): Promise<Package | null> {
  const response = await fetch(`/api/packages/${id}`);
  if (!response.ok) {
    return null;
  }
  return response.json() as Promise<Package>;
}

// The caller knows it's async and what it resolves to:
const pkg = await fetchPackage("SF-2024-00042");
if (pkg) {
  console.log(pkg.status);  // TypeScript knows pkg is Package here
}
```

---

## `this` Parameter

In JavaScript, `this` is a footgun. TypeScript lets you type it:

```typescript
interface PackageTracker {
  packages: Package[];
  addPackage(pkg: Package): void;
  getById(id: string): Package | undefined;
}

// Explicitly type 'this' to prevent calling with wrong context
function addPackage(this: PackageTracker, pkg: Package): void {
  this.packages.push(pkg);
}

// If someone detaches the method:
const tracker: PackageTracker = { packages: [], addPackage, getById };
const detached = tracker.addPackage;
detached({ id: "test", /* ... */ } as Package);
// Error: The 'this' context of type 'void' is not assignable to type 'PackageTracker'
```

---

## The Refactored API Layer

```typescript
// src/api.ts — all endpoints use the same response shape

type PackageStatus = "CREATED" | "PICKED_UP" | "IN_TRANSIT" | "OUT_FOR_DELIVERY" | "DELIVERED";

interface Package {
  readonly id: string;
  origin: string;
  destination: string;
  weight: number;
  status: PackageStatus;
  readonly createdAt: Date;
}

// Every handler returns ApiResponse<T>
type RouteHandler<T> = (params: Record<string, string>) => Promise<ApiResponse<T>>;

const getPackageHandler: RouteHandler<Package> = async (params) => {
  const pkg = await findPackage(params.id);
  if (!pkg) {
    return error("NOT_FOUND", `Package ${params.id} not found`);
  }
  return success(pkg);
};

const listPackagesHandler: RouteHandler<Package[]> = async (params) => {
  const pkgs = await findPackages(params);
  return success(pkgs);
};

// Both handlers are guaranteed to return the same shape.
// The frontend can trust response.success without guessing.
```

---

## Report to Ren

> **API response shape unified:**
> - `ApiResponse<T> = ApiSuccess<T> | ApiError` — one shape for all endpoints
> - Helper functions `success()` and `error()` enforce the structure
> - Frontend checks `response.success` — works for every endpoint
> - All route handlers typed as `RouteHandler<T>` — can't return wrong shape
>
> The "tracking updates stopped working" bug? Impossible now. Every endpoint returns the same structure.

Ren: "Solid. But I noticed you wrote `findById` for packages, then `findById` for shipments, then `findById` for customers. Same logic, different types. There's a better way."

---

## What You Learned

- **Return types** on functions prevent returning the wrong shape
- **`void`** = no meaningful return; **`never`** = function never returns (throws/loops)
- **Function overloads** give callers precise return types based on input types
- **Callback types** ensure passed functions have the right signature
- **`Promise<T>`** types async function returns — callers know what they'll get
- **Named function types** (`type Handler = (...) => T`) are reusable and readable
- A unified response type (`ApiResponse<T>`) eliminates shape inconsistencies across endpoints
- Type the contract first, implement second — the compiler enforces the contract

---

[Next: Chapter 5 — "Copy-Pasting the Same Function" →](chapter-05-generics.md)
