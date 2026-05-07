# Chapter 16: Cold Starts — "Cloud Function Is Slow on First Call"

[← Chapter 15: Pagination](chapter-15-pagination.md) | [Chapter 17: Cost Optimization →](chapter-17-cost-optimization.md)

---

## The Task

Marco: "I tap 'Join Team' and nothing happens for 4 seconds. Then it works. The second time it's instant. What's going on?"

You: "Cold starts. The function container was destroyed after being idle. Google had to spin up a new one."

---

## What's a Cold Start?

Cloud Functions run in containers. When a function hasn't been called recently:

```
Request arrives
    │
    ▼
No warm container available
    │
    ▼
Google provisions a new container (~1-5 seconds)
    │
    ▼
Node.js runtime starts
    │
    ▼
Your code loads (imports, initialization)
    │
    ▼
Function executes
    │
    ▼
Container stays warm (~15 minutes)
    │
    ▼
Next request reuses warm container (fast, <100ms)
    │
    ▼
After ~15 min idle → container destroyed → next call is cold again
```

Cold start time depends on:
- Runtime (Node.js is faster than Python/Java)
- Package size (more dependencies = slower)
- Region (closer to user = faster)
- Memory allocation (more memory = faster CPU)

---

## Measuring Cold Starts

Add timing to your functions:

```typescript
// functions/src/index.ts
const startTime = Date.now();
console.log("Module loaded"); // This runs on cold start only

export const joinTeam = onCall(async (request) => {
  const functionStart = Date.now();
  console.log(`Time since module load: ${functionStart - startTime}ms`);

  // ... function logic ...

  console.log(`Function execution: ${Date.now() - functionStart}ms`);
});
```

Check logs in Firebase console → Functions → Logs. Cold starts show the module load time; warm invocations skip it.

---

## Optimization 1: Minimize Dependencies

```typescript
// ❌ Importing everything — slow cold start
import * as admin from "firebase-admin";
import * as functions from "firebase-functions";
import moment from "moment"; // 300KB!
import lodash from "lodash"; // 500KB!

// ✅ Import only what you need
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";
import { onCall } from "firebase-functions/v2/https";
// Use native Date instead of moment
// Use specific lodash functions: import groupBy from "lodash/groupBy"
```

Every dependency adds to the container image size and initialization time.

---

## Optimization 2: Lazy Initialization

```typescript
// ❌ Initializes on every cold start, even if this function isn't called
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

const app = initializeApp();
const db = getFirestore(); // runs on module load

// ✅ Initialize lazily
import { initializeApp, getApps } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

let db: FirebaseFirestore.Firestore;

function getDb() {
  if (!db) {
    if (getApps().length === 0) initializeApp();
    db = getFirestore();
  }
  return db;
}

export const joinTeam = onCall(async (request) => {
  const firestore = getDb(); // only initializes on first call
  // ...
});
```

---

## Optimization 3: Min Instances (Keep Warm)

The nuclear option: keep containers warm permanently.

```typescript
import { onCall } from "firebase-functions/v2/https";

export const joinTeam = onCall(
  {
    minInstances: 1, // Always keep 1 container warm
    memory: "256MiB",
    region: "us-central1",
  },
  async (request) => {
    // No cold start — container is always ready
  }
);
```

Cost: you pay for idle time (~$0.40/month per idle instance for 256MB). Worth it for user-facing functions where latency matters.

Use `minInstances` for:
- Callable functions (user waits for response)
- HTTP endpoints (API calls)

Don't use for:
- Firestore triggers (background, user doesn't wait)
- Scheduled functions (runs on a timer anyway)

---

## Optimization 4: Reduce Memory (Faster CPU)

Higher memory allocation = proportionally faster CPU:

```typescript
export const processImage = onCall(
  {
    memory: "1GiB",  // 4x CPU compared to 256MiB
    timeoutSeconds: 60,
  },
  async (request) => {
    // CPU-intensive work runs faster with more memory
  }
);
```

| Memory | CPU | Cold Start |
|--------|-----|-----------|
| 128 MiB | 0.08 vCPU | Slowest |
| 256 MiB | 0.17 vCPU | Default |
| 512 MiB | 0.33 vCPU | Faster |
| 1 GiB | 0.58 vCPU | Fast |
| 2 GiB | 1 vCPU | Fastest |

---

## Optimization 5: Global vs Per-Request Work

Move expensive initialization outside the function handler:

```typescript
// This runs ONCE per container (on cold start)
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

initializeApp();
const db = getFirestore();

// Pre-compute or cache expensive data
const CONFIG = {
  maxTeamSize: 50,
  allowedStatuses: ["todo", "in_progress", "done", "archived"],
};

// This runs on EVERY invocation
export const createTask = onCall(async (request) => {
  // db is already initialized (warm)
  // CONFIG is already in memory
  await db.collection("tasks").add(request.data);
});
```

---

## Optimization 6: Separate Functions by Trigger Type

Don't put all functions in one file. Each deployed function loads the entire module:

```typescript
// ❌ One giant index.ts — every function loads all imports
// functions/src/index.ts
import heavyImageLib from "sharp";
import emailLib from "nodemailer";
import pdfLib from "pdfkit";

export const onTaskCreated = ...  // doesn't need sharp, nodemailer, or pdfkit
export const generateReport = ... // only needs pdfkit
export const sendEmail = ...      // only needs nodemailer
export const processImage = ...   // only needs sharp
```

```typescript
// ✅ Split into separate files with dynamic imports
// functions/src/index.ts
export { onTaskCreated } from "./triggers/tasks";
export { generateReport } from "./api/reports";
export { sendEmail } from "./triggers/email";
export { processImage } from "./triggers/images";

// functions/src/triggers/images.ts
export const processImage = onCall(async (request) => {
  const sharp = await import("sharp"); // loaded only when this function runs
  // ...
});
```

---

## Optimization 7: Concurrency

By default, each function instance handles one request at a time. Enable concurrency to handle multiple requests per instance:

```typescript
export const getTask = onCall(
  {
    concurrency: 80, // handle up to 80 concurrent requests per instance
    memory: "512MiB",
    minInstances: 1,
  },
  async (request) => {
    // Must be stateless — no shared mutable state between requests
  }
);
```

More concurrency = fewer instances needed = fewer cold starts.

---

## Scheduled Functions: No Cold Start Problem

Scheduled functions run on a timer. The container warms up before the scheduled time:

```typescript
export const dailyCleanup = onSchedule("every day 02:00", async () => {
  // Runs at 2 AM — no user waiting, cold start doesn't matter
  const oldTasks = await db
    .collectionGroup("tasks")
    .where("status", "==", "archived")
    .where("updatedAt", "<", thirtyDaysAgo)
    .get();

  // Delete old archived tasks in batches
  // ...
});
```

---

## Common Mistakes

### 1. Using `minInstances` on every function

At $0.40/month per instance, 20 functions with `minInstances: 1` = $8/month just for idle containers. Only use it for latency-sensitive, user-facing functions.

### 2. Importing unused dependencies

```typescript
// ❌ Imports 'sharp' (50MB) even for functions that don't use it
import sharp from "sharp";

// ✅ Dynamic import only when needed
const sharp = await import("sharp");
```

### 3. Not setting appropriate timeouts

Default timeout is 60 seconds. If your function should complete in 5 seconds, set `timeoutSeconds: 10`. This prevents runaway functions from burning budget.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Optimization                            │ Impact
────────────────────────────────────────┼──────────────────────────────────────
Minimize dependencies                   │ Faster module load
Lazy initialization                     │ Skip unused setup
minInstances: 1                         │ Eliminate cold starts ($)
Higher memory                           │ Faster CPU, faster cold start
Global initialization                   │ Run expensive work once
Split functions into files              │ Smaller per-function bundles
Dynamic imports                         │ Load heavy libs on demand
Concurrency                             │ Fewer instances needed
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena checks the Firebase billing dashboard: "$200 this month. We have 50 users. What happens when we have 5,000?"

Cost optimization. The chapter that saves your startup.

---

[← Chapter 15: Pagination](chapter-15-pagination.md) | [Chapter 17: Cost Optimization →](chapter-17-cost-optimization.md)
