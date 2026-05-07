# Chapter 5: Security Rules — "Anyone Can Read Anyone's Tasks" 😱

[← Chapter 4: Real-Time](chapter-04-realtime.md) | [Chapter 6: Storage →](chapter-06-storage.md)

---

## The Task

Lena: "I opened the app without logging in and I can see everyone's tasks. Every team. Everything. This is a disaster."

You check `firestore.rules`:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

`allow read, write: if true` — anyone can read and write anything. This is the default Firebase generates during `firebase init` for development. It's the single most common Firebase security mistake.

---

## Security Rules Mental Model

Security Rules are a declarative access control layer that sits between clients and your database. Every read and write from a client SDK passes through rules. If the rule evaluates to `false`, the operation is denied.

```
Client SDK → Security Rules → Firestore
                  │
                  ├── ✅ Rule passes → operation executes
                  └── ❌ Rule fails → "permission-denied" error
```

Rules do NOT apply to:
- Admin SDK (server-side, used in Cloud Functions)
- Firebase console
- Emulator (unless you enable rule enforcement)

Rules DO apply to:
- Every client SDK operation (web, iOS, Android)
- Every REST API call using client credentials

---

## Rule Structure

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /teams/{teamId} {
      allow read: if <condition>;
      allow write: if <condition>;
    }

    match /teams/{teamId}/tasks/{taskId} {
      allow read: if <condition>;
      allow write: if <condition>;
    }

  }
}
```

- `match` defines which documents the rule applies to
- `{teamId}` is a wildcard — captures the document ID as a variable
- `allow read` controls `get` and `list` operations
- `allow write` controls `create`, `update`, and `delete` operations

---

## Rule 1: Only Authenticated Users

```
match /teams/{teamId} {
  allow read, write: if request.auth != null;
}
```

`request.auth` is `null` for unauthenticated users. This blocks anonymous access but lets any signed-in user read any team. Not good enough.

---

## Rule 2: Only Team Members

```
match /teams/{teamId} {
  allow read: if request.auth != null
    && request.auth.uid in resource.data.members;

  allow write: if request.auth != null
    && request.auth.uid in resource.data.members;
}
```

- `request.auth.uid` — the authenticated user's ID
- `resource.data` — the existing document's fields
- `resource.data.members` — the `members` array on the team document

Now only users listed in the team's `members` array can read or write the team document.

---

## Rule 3: Tasks Inherit Team Access

```
match /teams/{teamId}/tasks/{taskId} {
  allow read: if request.auth != null
    && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members;

  allow create: if request.auth != null
    && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members
    && request.resource.data.createdBy == request.auth.uid;

  allow update: if request.auth != null
    && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members;

  allow delete: if request.auth != null
    && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members;
}
```

`get()` reads another document inside a rule. Here we check the parent team's `members` array. This costs one read per evaluation (billed).

For `create`, we also verify that `createdBy` matches the authenticated user — no impersonation.

---

## Granular Permissions: read vs write

```
allow read: if ...;    // covers get (single doc) AND list (query)
allow write: if ...;   // covers create, update, AND delete

// Or be specific:
allow get: if ...;     // single document read
allow list: if ...;    // collection query
allow create: if ...;  // new document
allow update: if ...;  // modify existing
allow delete: if ...;  // remove document
```

---

## Data Validation in Rules

Rules aren't just access control — they validate data shape:

```
match /teams/{teamId}/tasks/{taskId} {
  allow create: if request.auth != null
    && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members
    // Validate required fields
    && request.resource.data.keys().hasAll(["title", "status", "createdBy", "createdAt"])
    // Validate field types
    && request.resource.data.title is string
    && request.resource.data.title.size() > 0
    && request.resource.data.title.size() <= 200
    // Validate status enum
    && request.resource.data.status in ["todo", "in_progress", "done"]
    // Validate creator
    && request.resource.data.createdBy == request.auth.uid;

  allow update: if request.auth != null
    && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members
    // Can't change createdBy or createdAt
    && request.resource.data.createdBy == resource.data.createdBy
    && request.resource.data.createdAt == resource.data.createdAt
    // Status must remain valid
    && request.resource.data.status in ["todo", "in_progress", "done"];
}
```

- `request.resource.data` — the data being written (the "after" state)
- `resource.data` — the existing data (the "before" state)

---

## Helper Functions

Rules get verbose. Use functions to stay readable:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isAuthenticated() {
      return request.auth != null;
    }

    function isTeamMember(teamId) {
      return isAuthenticated()
        && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members;
    }

    function isValidTask() {
      let data = request.resource.data;
      return data.keys().hasAll(["title", "status", "createdBy", "createdAt"])
        && data.title is string
        && data.title.size() > 0
        && data.title.size() <= 200
        && data.status in ["todo", "in_progress", "done"];
    }

    match /teams/{teamId} {
      allow read: if isTeamMember(teamId);
      allow write: if isTeamMember(teamId);

      match /tasks/{taskId} {
        allow read: if isTeamMember(teamId);
        allow create: if isTeamMember(teamId)
          && isValidTask()
          && request.resource.data.createdBy == request.auth.uid;
        allow update: if isTeamMember(teamId)
          && isValidTask();
        allow delete: if isTeamMember(teamId);
      }
    }

    match /users/{userId} {
      allow read: if isAuthenticated();
      allow write: if request.auth.uid == userId;
    }
  }
}
```

---

## The Complete SnapTask Rules

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isAuthenticated() {
      return request.auth != null;
    }

    function isTeamMember(teamId) {
      return isAuthenticated()
        && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members;
    }

    // User profiles
    match /users/{userId} {
      allow read: if isAuthenticated();
      allow create: if request.auth.uid == userId;
      allow update: if request.auth.uid == userId;
      allow delete: if false; // users can't delete their own profile
    }

    // Teams
    match /teams/{teamId} {
      allow read: if isTeamMember(teamId);
      allow create: if isAuthenticated()
        && request.resource.data.members.hasAny([request.auth.uid]);
      allow update: if isTeamMember(teamId);
      allow delete: if false; // only via admin/Cloud Function

      // Tasks within a team
      match /tasks/{taskId} {
        allow read: if isTeamMember(teamId);
        allow create: if isTeamMember(teamId)
          && request.resource.data.createdBy == request.auth.uid;
        allow update: if isTeamMember(teamId);
        allow delete: if isTeamMember(teamId);
      }

      // Comments within a task
      match /tasks/{taskId}/comments/{commentId} {
        allow read: if isTeamMember(teamId);
        allow create: if isTeamMember(teamId)
          && request.resource.data.author == request.auth.uid;
        allow update: if resource.data.author == request.auth.uid;
        allow delete: if resource.data.author == request.auth.uid;
      }
    }
  }
}
```

---

## Testing Rules Locally

The emulator enforces rules. Test them:

```bash
firebase emulators:start
```

In your app, try to read a team you're not a member of. You should get a `permission-denied` error.

For automated testing, use the `@firebase/rules-unit-testing` package:

```typescript
// tests/firestore.rules.test.ts
import { initializeTestEnvironment, assertSucceeds, assertFails } from "@firebase/rules-unit-testing";
import { doc, getDoc, setDoc } from "firebase/firestore";

const testEnv = await initializeTestEnvironment({
  projectId: "snaptask-dev",
  firestore: { rules: fs.readFileSync("firestore.rules", "utf8") },
});

// Test: team member can read team
test("team member can read their team", async () => {
  // Setup: create team with member
  const admin = testEnv.withSecurityRulesDisabled(async (context) => {
    await setDoc(doc(context.firestore(), "teams/team1"), {
      name: "Acme",
      members: ["user1"],
    });
  });

  // Test: user1 can read
  const user1 = testEnv.authenticatedContext("user1");
  await assertSucceeds(getDoc(doc(user1.firestore(), "teams/team1")));

  // Test: user2 cannot read
  const user2 = testEnv.authenticatedContext("user2");
  await assertFails(getDoc(doc(user2.firestore(), "teams/team1")));
});
```

---

## Deploy Rules

```bash
firebase deploy --only firestore:rules
```

Rules deploy instantly. All existing client connections are immediately subject to the new rules.

---

## Common Mistakes

### 1. The wildcard trap

```
// ❌ This matches EVERYTHING — overrides all other rules
match /{document=**} {
  allow read, write: if true;
}
```

Remove this. Write specific rules for each collection.

### 2. Forgetting that `get()` costs reads

Each `get()` in a rule costs one document read. If your rule calls `get()` and you have 1,000 users hitting it, that's 1,000 extra reads. Cache-friendly patterns help (Chapter 17).

### 3. Rules don't filter — they reject

```typescript
// ❌ This query will FAIL even if some tasks match
const q = query(collection(db, "teams", "team1", "tasks"));
// If the user isn't a member of team1, the ENTIRE query is rejected

// Rules don't filter out documents you can't access.
// The query must only request documents the user CAN access.
```

### 4. Testing only the happy path

Test that unauthorized users are blocked. Test that invalid data is rejected. Test edge cases (empty arrays, missing fields).

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Expression                              │ What It Means
────────────────────────────────────────┼──────────────────────────────────────
request.auth                            │ Auth context (null if not signed in)
request.auth.uid                        │ User's unique ID
request.resource.data                   │ Data being written (new state)
resource.data                           │ Existing document data
get(/path/to/doc).data                  │ Read another document in rules
request.resource.data.keys().hasAll([]) │ Require specific fields
data.size()                             │ String length or array/map size
value in ["a", "b", "c"]               │ Enum validation
request.time                            │ Current server timestamp
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marco: "Users want to attach screenshots and files to tasks. Where do those go?"

Firebase Storage. Same security rules pattern, different service.

---

[← Chapter 4: Real-Time](chapter-04-realtime.md) | [Chapter 6: Storage →](chapter-06-storage.md)
