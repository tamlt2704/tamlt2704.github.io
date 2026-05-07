# Chapter 19: Emulator Suite — "Testing Without Hitting Production"

[← Chapter 18: REST API](chapter-18-rest-api.md) | [Chapter 20: Demo Day →](chapter-20-demo-day.md)

---

## The Task

Lena: "Last week Marco accidentally sent push notifications to all our beta testers at 2 AM. While debugging. We need a way to test everything locally without touching production."

---

## The Firebase Emulator Suite

The Emulator Suite runs Firebase services locally. No network calls. No billing. No accidental production writes.

```bash
firebase emulators:start
```

```
┌─────────────────────────────────────────────────────────┐
│  ✔  All emulators ready!                                 │
│                                                          │
│  Auth Emulator      → http://localhost:9099              │
│  Firestore Emulator → http://localhost:8080              │
│  Storage Emulator   → http://localhost:9199              │
│  Functions Emulator → http://localhost:5001              │
│  Hosting Emulator   → http://localhost:5000              │
│  Pub/Sub Emulator   → http://localhost:8085              │
│  Emulator UI        → http://localhost:4000              │
└─────────────────────────────────────────────────────────┘
```

The Emulator UI at `localhost:4000` gives you:
- Firestore data viewer (create, edit, delete documents)
- Auth user management (create users, view tokens)
- Functions logs (see console output in real-time)
- Storage file browser
- Request history

---

## Connecting Your App to Emulators

```typescript
// src/firebase.ts
import { initializeApp } from "firebase/app";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getStorage, connectStorageEmulator } from "firebase/storage";
import { getFunctions, connectFunctionsEmulator } from "firebase/functions";

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const storage = getStorage(app);
const functions = getFunctions(app);

if (import.meta.env.DEV) {
  connectFirestoreEmulator(db, "localhost", 8080);
  connectAuthEmulator(auth, "http://localhost:9099");
  connectStorageEmulator(storage, "localhost", 9199);
  connectFunctionsEmulator(functions, "localhost", 5001);
}

export { db, auth, storage, functions };
```

When connected to emulators:
- Auth creates fake users (no real emails sent)
- Firestore stores data in memory (resets on restart)
- Functions run locally (no deployment needed)
- Storage saves files locally

---

## Testing Security Rules

The `@firebase/rules-unit-testing` package lets you test rules programmatically:

```typescript
// tests/firestore.rules.test.ts
import {
  initializeTestEnvironment,
  assertSucceeds,
  assertFails,
  RulesTestEnvironment,
} from "@firebase/rules-unit-testing";
import { readFileSync } from "fs";
import { doc, getDoc, setDoc, deleteDoc, collection, getDocs } from "firebase/firestore";

let testEnv: RulesTestEnvironment;

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: "snaptask-test",
    firestore: {
      rules: readFileSync("firestore.rules", "utf8"),
    },
  });
});

afterEach(async () => {
  await testEnv.clearFirestore();
});

afterAll(async () => {
  await testEnv.cleanup();
});

describe("Team access rules", () => {
  test("team member can read team document", async () => {
    // Setup: create team with user1 as member
    await testEnv.withSecurityRulesDisabled(async (context) => {
      const db = context.firestore();
      await setDoc(doc(db, "teams", "team1"), {
        name: "Acme",
        members: ["user1", "user2"],
      });
    });

    // Test: user1 can read
    const user1Db = testEnv.authenticatedContext("user1").firestore();
    await assertSucceeds(getDoc(doc(user1Db, "teams", "team1")));
  });

  test("non-member cannot read team document", async () => {
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await setDoc(doc(context.firestore(), "teams", "team1"), {
        name: "Acme",
        members: ["user1"],
      });
    });

    // user3 is not a member
    const user3Db = testEnv.authenticatedContext("user3").firestore();
    await assertFails(getDoc(doc(user3Db, "teams", "team1")));
  });

  test("unauthenticated user cannot read anything", async () => {
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await setDoc(doc(context.firestore(), "teams", "team1"), {
        name: "Acme",
        members: ["user1"],
      });
    });

    const unauthDb = testEnv.unauthenticatedContext().firestore();
    await assertFails(getDoc(doc(unauthDb, "teams", "team1")));
  });
});

describe("Task creation rules", () => {
  test("member can create task with valid data", async () => {
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await setDoc(doc(context.firestore(), "teams", "team1"), {
        name: "Acme",
        members: ["user1"],
      });
    });

    const user1Db = testEnv.authenticatedContext("user1").firestore();
    await assertSucceeds(
      setDoc(doc(user1Db, "teams", "team1", "tasks", "task1"), {
        title: "New task",
        status: "todo",
        createdBy: "user1",
        createdAt: new Date(),
      })
    );
  });

  test("member cannot impersonate another user as creator", async () => {
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await setDoc(doc(context.firestore(), "teams", "team1"), {
        name: "Acme",
        members: ["user1"],
      });
    });

    const user1Db = testEnv.authenticatedContext("user1").firestore();
    await assertFails(
      setDoc(doc(user1Db, "teams", "team1", "tasks", "task1"), {
        title: "New task",
        status: "todo",
        createdBy: "user2", // impersonation!
        createdAt: new Date(),
      })
    );
  });
});
```

Run tests:

```bash
firebase emulators:exec "npx vitest run tests/firestore.rules.test.ts"
```

`emulators:exec` starts emulators, runs the command, then shuts down. Perfect for CI.

---

## Testing Cloud Functions

```typescript
// tests/functions.test.ts
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

// Point admin SDK at emulator
process.env.FIRESTORE_EMULATOR_HOST = "localhost:8080";
process.env.FIREBASE_AUTH_EMULATOR_HOST = "localhost:9099";

initializeApp({ projectId: "snaptask-test" });
const db = getFirestore();

describe("onTaskAssigned function", () => {
  test("sends notification when assignee changes", async () => {
    // Create a user with FCM token
    await db.doc("users/user2").set({
      displayName: "Lena",
      fcmToken: "fake-token-123",
    });

    // Create a team
    await db.doc("teams/team1").set({
      name: "Acme",
      members: ["user1", "user2"],
    });

    // Create a task (triggers onDocumentCreated)
    await db.doc("teams/team1/tasks/task1").set({
      title: "Design page",
      status: "todo",
      assignee: null,
      createdBy: "user1",
    });

    // Update assignee (triggers onDocumentUpdated → onTaskAssigned)
    await db.doc("teams/team1/tasks/task1").update({
      assignee: "user2",
    });

    // Wait for function to execute
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Verify the function's side effects
    // (In emulator, FCM messages are logged but not sent)
    // Check function logs in emulator UI
  });
});
```

---

## Seeding Test Data

Create a seed script for consistent test data:

```typescript
// scripts/seed-emulator.ts
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

process.env.FIRESTORE_EMULATOR_HOST = "localhost:8080";
initializeApp({ projectId: "snaptask-dev" });
const db = getFirestore();

async function seed() {
  // Create users
  await db.doc("users/user1").set({
    displayName: "Alex",
    email: "alex@example.com",
    teams: ["team1"],
  });

  await db.doc("users/user2").set({
    displayName: "Lena",
    email: "lena@example.com",
    teams: ["team1"],
  });

  // Create team
  await db.doc("teams/team1").set({
    name: "Acme Startup",
    members: ["user1", "user2"],
    taskCounts: { todo: 3, in_progress: 1, done: 1 },
  });

  // Create tasks
  const tasks = [
    { title: "Design landing page", status: "in_progress", assignee: "user2" },
    { title: "Set up CI/CD", status: "todo", assignee: "user1" },
    { title: "Write API docs", status: "todo", assignee: null },
    { title: "Fix login bug", status: "done", assignee: "user1" },
    { title: "Add dark mode", status: "todo", assignee: "user2" },
  ];

  for (const task of tasks) {
    await db.collection("teams/team1/tasks").add({
      ...task,
      priority: "medium",
      createdBy: "user1",
      createdAt: new Date(),
      updatedAt: new Date(),
    });
  }

  console.log("Seed data created!");
}

seed();
```

Run it:

```bash
npx ts-node scripts/seed-emulator.ts
```

---

## Export and Import Emulator Data

Save emulator state between sessions:

```bash
# Export current emulator data
firebase emulators:export ./emulator-data

# Start with previously exported data
firebase emulators:start --import=./emulator-data
```

Add `emulator-data/` to `.gitignore` — or commit it for shared test fixtures.

---

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Install Firebase CLI
        run: npm install -g firebase-tools

      - name: Install function dependencies
        run: cd functions && npm ci

      - name: Run tests with emulators
        run: firebase emulators:exec "npm test"
        env:
          FIREBASE_PROJECT: snaptask-test
```

`firebase emulators:exec` handles the full lifecycle:
1. Starts all emulators
2. Runs your test command
3. Shuts down emulators
4. Returns the test exit code

---

## Emulator Limitations

| Feature | Emulator Support |
|---------|-----------------|
| Firestore CRUD | ✅ Full |
| Security Rules | ✅ Full |
| Auth (email, anonymous) | ✅ Full |
| Auth (Google, OAuth) | ⚠️ Simulated (no real OAuth) |
| Cloud Functions (triggers) | ✅ Full |
| Cloud Functions (scheduled) | ⚠️ Must trigger manually |
| Storage (upload/download) | ✅ Full |
| FCM (push notifications) | ❌ Logged but not sent |
| Composite indexes | ❌ Not enforced |
| Billing/quotas | ❌ Not simulated |

Key gap: **indexes are not enforced in the emulator**. A query that works locally may fail in production if you haven't created the required composite index.

---

## Debugging Functions in the Emulator

Function logs appear in the terminal running `firebase emulators:start` and in the Emulator UI → Functions tab.

```typescript
// Use console.log liberally in development
export const onTaskCreated = onDocumentCreated("teams/{teamId}/tasks/{taskId}", async (event) => {
  console.log("Task created:", event.params);
  console.log("Data:", event.data?.data());

  // ... function logic ...

  console.log("Function complete");
});
```

For breakpoint debugging, start the emulator with inspect:

```bash
firebase emulators:start --inspect-functions
```

Then attach VS Code's debugger to port 9229.

---

## Common Mistakes

### 1. Forgetting to connect to emulators

If your app hits production during development, you'll see real data in the Firebase console and get billed. Always verify the emulator connection:

```typescript
// Add a visual indicator in dev
if (import.meta.env.DEV) {
  document.title = "🔧 SnapTask (DEV)";
}
```

### 2. Testing only with emulators

The emulator doesn't enforce indexes or simulate network latency. Test against a staging Firebase project before deploying to production.

### 3. Not resetting state between tests

```typescript
afterEach(async () => {
  await testEnv.clearFirestore(); // clean slate for each test
});
```

Without cleanup, tests depend on each other's state and become flaky.

### 4. Hardcoding emulator ports

Use `firebase.json` to configure ports. If port 8080 is taken, the emulator picks another — and your app can't connect.

```json
{
  "emulators": {
    "firestore": { "port": 8080 },
    "auth": { "port": 9099 }
  }
}
```

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Command                                 │ What It Does
────────────────────────────────────────┼──────────────────────────────────────
firebase emulators:start                │ Start all emulators
firebase emulators:start --only firestore│ Start specific emulator
firebase emulators:exec "npm test"      │ Run command with emulators (CI)
firebase emulators:export ./data        │ Save emulator state
firebase emulators:start --import=./data│ Load saved state
firebase emulators:start --inspect-functions │ Enable debugger
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

It's demo day. The investor is in the room. They're going to ask hard questions about security, scaling, and architecture.

Time to prepare.

---

[← Chapter 18: REST API](chapter-18-rest-api.md) | [Chapter 20: Demo Day →](chapter-20-demo-day.md)
