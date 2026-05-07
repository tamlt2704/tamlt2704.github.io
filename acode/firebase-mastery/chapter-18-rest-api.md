# Chapter 18: REST API — "Need an API for Integrations"

[← Chapter 17: Cost Optimization](chapter-17-cost-optimization.md) | [Chapter 19: Emulator Suite →](chapter-19-emulator-suite.md)

---

## The Task

Lena: "A partner company wants to integrate with SnapTask. They need REST endpoints — create tasks, list tasks, update status. They can't use our Firebase SDK."

You need a proper API. Cloud Functions can serve as HTTP endpoints.

---

## Two Approaches: Callable vs HTTP

| Feature | Callable (`onCall`) | HTTP (`onRequest`) |
|---------|--------------------|--------------------|
| Client | Firebase SDK only | Any HTTP client |
| Auth | Automatic (SDK handles tokens) | Manual (verify tokens yourself) |
| CORS | Handled automatically | You configure it |
| Request format | `{ data: {...} }` | Standard HTTP (JSON, form, etc.) |
| Use case | Your own app | External integrations, webhooks |

For a partner API, use `onRequest`.

---

## HTTP Functions with Express

```typescript
// functions/src/api.ts
import { onRequest } from "firebase-functions/v2/https";
import express from "express";
import cors from "cors";
import { getFirestore } from "firebase-admin/firestore";
import { getAuth } from "firebase-admin/auth";

const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

const db = getFirestore();

// Middleware: verify Firebase ID token
async function authenticate(req: express.Request, res: express.Response, next: express.NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith("Bearer ")) {
    res.status(401).json({ error: "Missing or invalid Authorization header" });
    return;
  }

  const token = authHeader.split("Bearer ")[1];

  try {
    const decoded = await getAuth().verifyIdToken(token);
    (req as any).user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: "Invalid token" });
  }
}

app.use(authenticate);

// GET /api/teams/:teamId/tasks
app.get("/teams/:teamId/tasks", async (req, res) => {
  const { teamId } = req.params;
  const userId = (req as any).user.uid;
  const { status, limit: limitParam } = req.query;

  // Verify user is team member
  const teamDoc = await db.doc(`teams/${teamId}`).get();
  if (!teamDoc.exists || !teamDoc.data()?.members.includes(userId)) {
    res.status(403).json({ error: "Not a team member" });
    return;
  }

  let query: any = db.collection(`teams/${teamId}/tasks`);

  if (status) {
    query = query.where("status", "==", status);
  }

  query = query.orderBy("createdAt", "desc").limit(Number(limitParam) || 50);

  const snapshot = await query.get();
  const tasks = snapshot.docs.map((doc: any) => ({ id: doc.id, ...doc.data() }));

  res.json({ tasks, count: tasks.length });
});

// POST /api/teams/:teamId/tasks
app.post("/teams/:teamId/tasks", async (req, res) => {
  const { teamId } = req.params;
  const userId = (req as any).user.uid;
  const { title, priority, assignee } = req.body;

  if (!title) {
    res.status(400).json({ error: "title is required" });
    return;
  }

  // Verify team membership
  const teamDoc = await db.doc(`teams/${teamId}`).get();
  if (!teamDoc.exists || !teamDoc.data()?.members.includes(userId)) {
    res.status(403).json({ error: "Not a team member" });
    return;
  }

  const taskRef = await db.collection(`teams/${teamId}/tasks`).add({
    title,
    status: "todo",
    priority: priority || "medium",
    assignee: assignee || null,
    createdBy: userId,
    createdAt: new Date(),
    updatedAt: new Date(),
  });

  res.status(201).json({ id: taskRef.id, message: "Task created" });
});

// PATCH /api/teams/:teamId/tasks/:taskId
app.patch("/teams/:teamId/tasks/:taskId", async (req, res) => {
  const { teamId, taskId } = req.params;
  const userId = (req as any).user.uid;
  const updates = req.body;

  // Verify team membership
  const teamDoc = await db.doc(`teams/${teamId}`).get();
  if (!teamDoc.exists || !teamDoc.data()?.members.includes(userId)) {
    res.status(403).json({ error: "Not a team member" });
    return;
  }

  // Whitelist allowed fields
  const allowed = ["title", "status", "priority", "assignee"];
  const filtered: Record<string, any> = {};
  for (const key of allowed) {
    if (key in updates) filtered[key] = updates[key];
  }

  if (Object.keys(filtered).length === 0) {
    res.status(400).json({ error: "No valid fields to update" });
    return;
  }

  filtered.updatedAt = new Date();

  await db.doc(`teams/${teamId}/tasks/${taskId}`).update(filtered);
  res.json({ message: "Task updated" });
});

// DELETE /api/teams/:teamId/tasks/:taskId
app.delete("/teams/:teamId/tasks/:taskId", async (req, res) => {
  const { teamId, taskId } = req.params;
  const userId = (req as any).user.uid;

  const teamDoc = await db.doc(`teams/${teamId}`).get();
  if (!teamDoc.exists || !teamDoc.data()?.members.includes(userId)) {
    res.status(403).json({ error: "Not a team member" });
    return;
  }

  await db.doc(`teams/${teamId}/tasks/${taskId}`).delete();
  res.json({ message: "Task deleted" });
});

// Export as a Cloud Function
export const api = onRequest(
  { cors: true, region: "us-central1" },
  app
);
```

---

## Calling the API

```bash
# Get an ID token (for testing)
TOKEN=$(curl -s "http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=fake-api-key" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","returnSecureToken":true}' \
  | jq -r '.idToken')

# List tasks
curl -H "Authorization: Bearer $TOKEN" \
  https://us-central1-snaptask-dev.cloudfunctions.net/api/teams/team-abc/tasks

# Create a task
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "API-created task", "priority": "high"}' \
  https://us-central1-snaptask-dev.cloudfunctions.net/api/teams/team-abc/tasks

# Update a task
curl -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}' \
  https://us-central1-snaptask-dev.cloudfunctions.net/api/teams/team-abc/tasks/task-123
```

---

## API Keys for Partners (Alternative Auth)

For server-to-server integrations, Firebase ID tokens are awkward. Use API keys instead:

```typescript
// Store API keys in Firestore
// apiKeys/{keyHash} → { teamId, permissions, createdBy, createdAt }

async function authenticateApiKey(req: express.Request, res: express.Response, next: express.NextFunction) {
  const apiKey = req.headers["x-api-key"] as string;

  if (!apiKey) {
    // Fall back to Bearer token auth
    return authenticate(req, res, next);
  }

  // Hash the key and look it up
  const crypto = await import("crypto");
  const keyHash = crypto.createHash("sha256").update(apiKey).digest("hex");

  const keyDoc = await db.doc(`apiKeys/${keyHash}`).get();
  if (!keyDoc.exists) {
    res.status(401).json({ error: "Invalid API key" });
    return;
  }

  const keyData = keyDoc.data()!;
  (req as any).teamId = keyData.teamId;
  (req as any).permissions = keyData.permissions;
  (req as any).authType = "apiKey";
  next();
}
```

---

## Rate Limiting

Protect your API from abuse:

```typescript
const rateLimits = new Map<string, { count: number; resetAt: number }>();

function rateLimit(maxRequests: number, windowMs: number) {
  return (req: express.Request, res: express.Response, next: express.NextFunction) => {
    const key = (req as any).user?.uid || req.ip;
    const now = Date.now();
    const entry = rateLimits.get(key);

    if (!entry || now > entry.resetAt) {
      rateLimits.set(key, { count: 1, resetAt: now + windowMs });
      next();
      return;
    }

    if (entry.count >= maxRequests) {
      res.status(429).json({ error: "Rate limit exceeded" });
      return;
    }

    entry.count++;
    next();
  };
}

app.use(rateLimit(100, 60 * 1000)); // 100 requests per minute
```

Note: This in-memory rate limiter resets on cold starts. For production, use Redis or Firestore-based rate limiting.

---

## Callable Functions (For Your Own App)

For your own frontend, callable functions are simpler:

```typescript
// functions/src/callable.ts
import { onCall, HttpsError } from "firebase-functions/v2/https";

export const createTeam = onCall(async (request) => {
  if (!request.auth) {
    throw new HttpsError("unauthenticated", "Must be signed in");
  }

  const { name } = request.data;
  if (!name || typeof name !== "string") {
    throw new HttpsError("invalid-argument", "Team name is required");
  }

  const teamRef = await db.collection("teams").add({
    name,
    members: [request.auth.uid],
    createdBy: request.auth.uid,
    createdAt: new Date(),
  });

  await db.doc(`users/${request.auth.uid}`).update({
    teams: FieldValue.arrayUnion(teamRef.id),
  });

  return { teamId: teamRef.id };
});
```

Client:

```typescript
import { httpsCallable } from "firebase/functions";

const createTeamFn = httpsCallable(functions, "createTeam");
const result = await createTeamFn({ name: "New Team" });
console.log(result.data.teamId);
```

---

## When to Use Each

| Scenario | Approach |
|----------|----------|
| Your own app calling backend logic | Callable (`onCall`) |
| Partner/third-party integration | HTTP (`onRequest`) with Express |
| Webhook receiver (Stripe, GitHub) | HTTP (`onRequest`) |
| Public API | HTTP with API key auth |
| Internal microservice | HTTP with service account auth |

---

## Common Mistakes

### 1. Not validating input

```typescript
// ❌ Trusting client data
app.post("/tasks", async (req, res) => {
  await db.collection("tasks").add(req.body); // anything goes!
});

// ✅ Validate and whitelist
app.post("/tasks", async (req, res) => {
  const { title, priority } = req.body;
  if (!title || typeof title !== "string" || title.length > 200) {
    return res.status(400).json({ error: "Invalid title" });
  }
  // ...
});
```

### 2. Exposing internal errors

```typescript
// ❌ Leaks internal details
catch (error) {
  res.status(500).json({ error: error.message, stack: error.stack });
}

// ✅ Generic error, log internally
catch (error) {
  console.error("API error:", error);
  res.status(500).json({ error: "Internal server error" });
}
```

### 3. No CORS configuration

Without CORS, browsers block requests from your frontend to the API. Use `cors({ origin: true })` for development, restrict origins in production.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Pattern                                 │ Use Case
────────────────────────────────────────┼──────────────────────────────────────
onCall(handler)                         │ Your app (auto-auth, auto-CORS)
onRequest(expressApp)                   │ REST API (manual auth, full control)
verifyIdToken(token)                    │ Validate Firebase user tokens
x-api-key header                        │ Partner/server-to-server auth
Express middleware                      │ Auth, rate limiting, validation
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "We need to test all of this without hitting production. I don't want to accidentally send push notifications to real users while debugging."

The Firebase Emulator Suite. Local development, testing, and CI.

---

[← Chapter 17: Cost Optimization](chapter-17-cost-optimization.md) | [Chapter 19: Emulator Suite →](chapter-19-emulator-suite.md)
