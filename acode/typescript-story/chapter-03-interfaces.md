# Chapter 3: An Object is Missing a Field

[← Chapter 2: A String Sneaks In](chapter-02-primitives.md) | [Chapter 4: A Function Returns the Wrong Shape →](chapter-04-functions.md)

---

## The Disaster

The tracking page shows package details. The frontend calls your API and renders:

```javascript
// Frontend code
const pkg = await fetch(`/api/packages/${id}`).then(r => r.json());
document.getElementById("zip").textContent = pkg.destination.zipCode;
```

Works for domestic packages. Crashes for international ones — because international packages store destination as a free-text `country` field, not a structured address. `pkg.destination.zipCode` → `Cannot read properties of undefined`.

The problem: the `destination` field has different shapes depending on the package type, and nothing in the code documents which shape to expect.

---

## Interfaces: Describing Object Shapes

```typescript
// src/models.ts

interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

interface Package {
  id: string;
  origin: Address;
  destination: Address;
  weight: number;
  status: PackageStatus;
  createdAt: Date;
}
```

Now if you try to create a package without a complete address:

```typescript
const pkg: Package = {
  id: "SF-2024-00042",
  origin: {
    street: "123 Warehouse Rd",
    city: "Shanghai",
    state: "Shanghai",
    zipCode: "200000",
    country: "CN",
  },
  destination: {
    city: "Rotterdam",
    country: "NL",
  },
  // Error: Type '{ city: string; country: string; }' is missing the following
  // properties from type 'Address': street, state, zipCode
  weight: 12.5,
  status: "CREATED",
  createdAt: new Date(),
};
```

The compiler tells you exactly which fields are missing.

---

## Optional Properties

Not every field is always present. Use `?` to mark optional properties:

```typescript
interface Address {
  street: string;
  city: string;
  state?: string;        // Optional — not all countries have states
  zipCode?: string;      // Optional — some addresses don't have zip codes
  country: string;
}

// Now this is valid:
const addr: Address = {
  street: "Keizersgracht 123",
  city: "Amsterdam",
  country: "NL",
};
// ✓ No error — state and zipCode are optional
```

But when you *access* an optional property, TypeScript knows it might be `undefined`:

```typescript
function formatZip(address: Address): string {
  return address.zipCode.toUpperCase();
  //     ^^^^^^^^^^^^^^^ Error: 'address.zipCode' is possibly 'undefined'
}

// Fix: handle the undefined case
function formatZip(address: Address): string {
  if (!address.zipCode) {
    return "N/A";
  }
  return address.zipCode.toUpperCase();
}
```

---

## `readonly`: Prevent Accidental Mutation

```typescript
interface Package {
  readonly id: string;           // Can't change after creation
  readonly createdAt: Date;      // Can't change after creation
  origin: Address;
  destination: Address;
  weight: number;
  status: PackageStatus;         // This one CAN change (packages move through statuses)
}

const pkg: Package = {
  id: "SF-2024-00042",
  createdAt: new Date(),
  origin: { street: "...", city: "Shanghai", country: "CN" },
  destination: { street: "...", city: "Rotterdam", country: "NL" },
  weight: 12.5,
  status: "CREATED",
};

pkg.status = "PICKED_UP";  // ✓ Fine — status is mutable
pkg.id = "SF-2024-99999";
// Error: Cannot assign to 'id' because it is a read-only property
```

`readonly` prevents bugs where code accidentally overwrites an ID or creation timestamp.

---

## Extending Interfaces

Interfaces can build on each other:

```typescript
// Base tracking event
interface TrackingEvent {
  timestamp: Date;
  location: string;
  description: string;
}

// Specific events add fields
interface StatusChangeEvent extends TrackingEvent {
  previousStatus: PackageStatus;
  newStatus: PackageStatus;
}

interface ExceptionEvent extends TrackingEvent {
  exceptionCode: string;
  resolution?: string;  // Optional — might not be resolved yet
}

// Package with full history
interface PackageWithHistory extends Package {
  history: TrackingEvent[];
}
```

`extends` means "has everything from the parent, plus these additional fields." It's composition, not inheritance.

---

## Type Aliases vs Interfaces

```typescript
// Interface — for object shapes. Can be extended and merged.
interface Package {
  id: string;
  weight: number;
}

// Type alias — for anything. Unions, intersections, primitives, tuples.
type PackageStatus = "CREATED" | "PICKED_UP" | "IN_TRANSIT" | "OUT_FOR_DELIVERY" | "DELIVERED";
type PackageOrNull = Package | null;
type Coordinates = [number, number];  // Tuple
```

**Rule of thumb:**
- Use `interface` for object shapes (they're extendable and show better error messages)
- Use `type` for unions, intersections, tuples, and aliases of primitives

---

## Index Signatures: Dynamic Keys

Sometimes you don't know all the keys ahead of time:

```typescript
// Package metadata — arbitrary key-value pairs
interface PackageMetadata {
  [key: string]: string | number | boolean;
}

const meta: PackageMetadata = {
  fragile: true,
  insuranceValue: 5000,
  customsCode: "HS-8471.30",
  specialInstructions: "Keep upright",
};

// You can access any string key:
console.log(meta.fragile);           // ✓
console.log(meta.nonExistent);       // ✓ (type is string | number | boolean)
// TypeScript can't know which keys exist at compile time
```

Use index signatures sparingly. Prefer explicit interfaces when you know the shape.

---

## Intersection Types: Combining Shapes

```typescript
// Combine types with &
type Timestamped = {
  createdAt: Date;
  updatedAt: Date;
};

type SoftDeletable = {
  deletedAt: Date | null;
  isDeleted: boolean;
};

// A package that has both timestamp and soft-delete fields
type ManagedPackage = Package & Timestamped & SoftDeletable;

// ManagedPackage has ALL fields from Package, Timestamped, and SoftDeletable
```

---

## The Fix: Model the Real Domain

Back to the original problem — domestic vs international destinations:

```typescript
interface DomesticAddress {
  type: "domestic";
  street: string;
  city: string;
  state: string;
  zipCode: string;
}

interface InternationalAddress {
  type: "international";
  street?: string;
  city: string;
  country: string;
  postalCode?: string;
}

type Destination = DomesticAddress | InternationalAddress;

interface Package {
  readonly id: string;
  origin: Address;
  destination: Destination;
  weight: number;
  status: PackageStatus;
  readonly createdAt: Date;
}

// Now the frontend MUST check the type:
function getZipCode(dest: Destination): string | null {
  if (dest.type === "domestic") {
    return dest.zipCode;  // ✓ TypeScript knows zipCode exists here
  }
  return dest.postalCode ?? null;  // International might not have one
}
```

The crash is now impossible. The compiler forces you to handle both cases.

---

## Report to Ren

> **Object models typed:**
> - `Package`, `Address`, `TrackingEvent` interfaces defined
> - Optional fields marked with `?` — compiler forces null checks on access
> - `readonly` on IDs and timestamps — prevents accidental mutation
> - Domestic vs International addresses modeled as a union — impossible to access `zipCode` on international packages without checking first
>
> The frontend crash? Compile error now. Can't ship it.

Ren: "Nice. Now type the API functions. Someone's returning `{ success: true, data: pkg }` from one endpoint and `{ ok: true, package: pkg }` from another. Pick a shape and enforce it."

---

## What You Learned

- **Interfaces** describe the shape of objects — TypeScript enforces every field
- **Optional properties** (`?`) mean the field might be `undefined` — compiler forces checks
- **`readonly`** prevents mutation after creation — catches accidental overwrites
- **`extends`** builds interfaces on top of each other — composition over inheritance
- **Type aliases** (`type`) handle unions, tuples, and complex types that interfaces can't
- **Index signatures** (`[key: string]: T`) allow dynamic keys — use sparingly
- **Intersection types** (`&`) combine multiple types into one
- Model your domain accurately — if two shapes exist, type them separately and use a union

---

[Next: Chapter 4 — "A Function Returns the Wrong Shape" →](chapter-04-functions.md)
