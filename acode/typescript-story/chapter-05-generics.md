# Chapter 5: Copy-Pasting the Same Function

[← Chapter 4: A Function Returns the Wrong Shape](chapter-04-functions.md) | [Chapter 6: 47 Possible Values →](chapter-06-unions.md)

---

## The Disaster

You've written this function three times:

```typescript
function findPackageById(id: string): Package | undefined {
  return packages.find(p => p.id === id);
}

function findShipmentById(id: string): Shipment | undefined {
  return shipments.find(s => s.id === id);
}

function findCustomerById(id: string): Customer | undefined {
  return customers.find(c => c.id === id);
}
```

Same logic. Same pattern. Three copies. When you add error logging to one, you forget the others. When you change the lookup strategy, you update two out of three.

Ren's PR comment: "This is what generics are for."

---

## Generics: Functions That Work with Any Type

```typescript
// src/repository.ts

// T is a "type parameter" — a placeholder for whatever type the caller provides
function findById<T extends { id: string }>(items: T[], id: string): T | undefined {
  return items.find(item => item.id === id);
}

// Usage — TypeScript infers T from the arguments
const pkg = findById(packages, "SF-2024-00042");
// Type: Package | undefined (T = Package, inferred from packages: Package[])

const customer = findById(customers, "CUST-001");
// Type: Customer | undefined (T = Customer)

const shipment = findById(shipments, "SHIP-789");
// Type: Shipment | undefined (T = Shipment)
```

One function. Works for any type that has an `id: string` field. The constraint `T extends { id: string }` ensures you can't pass an array of numbers — only objects with an `id`.

---

## How Generics Work

Think of generics as "type arguments" — just like functions take value arguments, generic functions take type arguments.

```typescript
// Without generics: you lose type information
function first(arr: unknown[]): unknown {
  return arr[0];
}
const item = first(packages);  // Type: unknown — useless

// With generics: type flows through
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}
const item = first(packages);  // Type: Package | undefined — useful!
```

TypeScript usually **infers** the type parameter from usage. You rarely need to specify it explicitly:

```typescript
// Explicit (unnecessary here — TypeScript infers it)
const pkg = findById<Package>(packages, "SF-2024-00042");

// Inferred (preferred — less noise)
const pkg = findById(packages, "SF-2024-00042");
```

---

## Generic Constraints

Without constraints, `T` could be anything — even `null` or `number`:

```typescript
// Too loose — T could be anything
function getProperty<T>(obj: T, key: string): unknown {
  return (obj as any)[key];  // Unsafe!
}

// Constrained — T must be an object with string keys
function getProperty<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  key: K
): T[K] {
  return obj[key];
}

const pkg = { id: "SF-001", weight: 12.5, status: "CREATED" };
const weight = getProperty(pkg, "weight");  // Type: number
const status = getProperty(pkg, "status");  // Type: string

getProperty(pkg, "nonexistent");
// Error: Argument of type '"nonexistent"' is not assignable to
// parameter of type '"id" | "weight" | "status"'
```

`K extends keyof T` means "K must be one of T's actual keys." TypeScript checks this at compile time.

---

## Generic Interfaces and Types

```typescript
// A generic repository pattern
interface Repository<T extends { id: string }> {
  findById(id: string): Promise<T | undefined>;
  findAll(): Promise<T[]>;
  create(item: Omit<T, "id">): Promise<T>;
  update(id: string, changes: Partial<T>): Promise<T>;
  delete(id: string): Promise<boolean>;
}

// Concrete implementations
class PackageRepository implements Repository<Package> {
  async findById(id: string): Promise<Package | undefined> { /* ... */ }
  async findAll(): Promise<Package[]> { /* ... */ }
  async create(item: Omit<Package, "id">): Promise<Package> { /* ... */ }
  async update(id: string, changes: Partial<Package>): Promise<Package> { /* ... */ }
  async delete(id: string): Promise<boolean> { /* ... */ }
}

class CustomerRepository implements Repository<Customer> {
  async findById(id: string): Promise<Customer | undefined> { /* ... */ }
  // ... same interface, different type
}
```

Write the interface once. Implement it for each entity. The compiler ensures every implementation has the right methods with the right types.

---

## Multiple Type Parameters

```typescript
// Map one type to another
function mapArray<TInput, TOutput>(
  items: TInput[],
  transform: (item: TInput) => TOutput
): TOutput[] {
  return items.map(transform);
}

// Usage
const ids = mapArray(packages, pkg => pkg.id);
// Type: string[]

const summaries = mapArray(packages, pkg => ({
  id: pkg.id,
  status: pkg.status,
}));
// Type: { id: string; status: PackageStatus }[]
```

### Key-Value Pairs

```typescript
// A type-safe event emitter
interface EventMap {
  "package:created": Package;
  "package:delivered": { packageId: string; deliveredAt: Date };
  "error": Error;
}

function emit<K extends keyof EventMap>(event: K, payload: EventMap[K]): void {
  // ... dispatch event
}

emit("package:created", pkg);           // ✓ payload must be Package
emit("package:delivered", { packageId: "SF-001", deliveredAt: new Date() });  // ✓
emit("package:created", "wrong");
// Error: Argument of type 'string' is not assignable to parameter of type 'Package'
```

---

## Generic Defaults

```typescript
// Default type parameter — used when caller doesn't specify
interface PaginatedResponse<T, TMeta = { total: number; page: number }> {
  data: T[];
  meta: TMeta;
}

// Uses default meta type
const response: PaginatedResponse<Package> = {
  data: packages,
  meta: { total: 100, page: 1 },
};

// Override with custom meta
const detailed: PaginatedResponse<Package, { total: number; page: number; hasMore: boolean }> = {
  data: packages,
  meta: { total: 100, page: 1, hasMore: true },
};
```

---

## Real-World Example: A Type-Safe API Client

```typescript
// src/client.ts

interface ApiEndpoints {
  "/packages": { list: Package[]; get: Package; create: Package };
  "/shipments": { list: Shipment[]; get: Shipment; create: Shipment };
  "/customers": { list: Customer[]; get: Customer; create: Customer };
}

type Endpoint = keyof ApiEndpoints;

async function apiGet<E extends Endpoint>(
  endpoint: E,
  id: string
): Promise<ApiEndpoints[E]["get"]> {
  const response = await fetch(`${endpoint}/${id}`);
  return response.json();
}

async function apiList<E extends Endpoint>(
  endpoint: E
): Promise<ApiEndpoints[E]["list"]> {
  const response = await fetch(endpoint);
  return response.json();
}

// Usage — return types are inferred from the endpoint
const pkg = await apiGet("/packages", "SF-001");
// Type: Package

const customers = await apiList("/customers");
// Type: Customer[]

const wrong = await apiGet("/nonexistent", "id");
// Error: Argument of type '"/nonexistent"' is not assignable to type 'Endpoint'
```

One client. Type-safe for every endpoint. Add a new endpoint to `ApiEndpoints` and the client automatically supports it.

---

## When NOT to Use Generics

```typescript
// ❌ Unnecessary generic — just use the concrete type
function getPackageId<T extends Package>(pkg: T): string {
  return pkg.id;
}

// ✓ Simpler — no generic needed
function getPackageId(pkg: Package): string {
  return pkg.id;
}

// Rule: use generics when the TYPE FLOWS THROUGH the function.
// If you're just reading from the input, a concrete type is fine.
```

**Use generics when:**
- The return type depends on the input type
- You're writing reusable utilities (find, map, filter, wrap)
- You want to preserve type information through a transformation

**Don't use generics when:**
- A concrete type works fine
- You're adding complexity without type-safety benefit
- The generic parameter is only used once (it's not "flowing" anywhere)

---

## Report to Ren

> **Generics implemented:**
> - `findById<T>` replaces 3 copy-pasted functions
> - `Repository<T>` interface — one contract, multiple implementations
> - Type-safe event emitter — payload type enforced per event name
> - API client — return type inferred from endpoint string
>
> Copy-paste eliminated. When we add error logging to `findById`, it works for all entity types automatically.

Ren: "Good. Now we need to handle the status field properly. Right now it's a string union, but different statuses carry different data. A 'DELIVERED' package has a delivery date. An 'IN_TRANSIT' package has a current location. Model that."

---

## What You Learned

- **Generics** (`<T>`) let functions/interfaces work with any type while preserving type information
- **Type parameters** are like function parameters but for types — they flow through
- **Constraints** (`T extends X`) limit what types are acceptable
- **`keyof T`** gives you the union of T's property names — enables type-safe property access
- **Multiple type parameters** (`<TInput, TOutput>`) handle transformations
- **Generic defaults** (`<T = DefaultType>`) provide fallback types
- TypeScript **infers** generic types from usage — you rarely need to specify them explicitly
- Don't use generics when a concrete type works — they add complexity

---

[Next: Chapter 6 — "47 Possible Values" →](chapter-06-unions.md)
