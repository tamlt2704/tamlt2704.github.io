# Chapter 9: Cloud Functions — "Notify When Task Assigned"

[← Chapter 8: Indexes](chapter-08-indexes.md) | [Chapter 10: Push Notifications →](chapter-10-push-notifications.md)

---

## The Task

Lena: "When someone assigns a task to me, I want to know. Not by refreshing the app — I want a notification. And I want an email summary at end of day."

Marco: "That's server-side logic. The client can't send notifications to other users."

You: "Cloud Functions. Serverless code that runs in response to events."

---

## What Are Cloud Functions?

Cloud Functions are server-side code that runs without you managing servers. They execute in response to:

- **Firestore triggers** — a document is created, updated, or deleted
- **Auth triggers** — a user signs up or is deleted
- **Storage triggers** — a file is uploaded or deleted
- **HTTP triggers** — someone calls a URL
- **Scheduled triggers** — run on a cron schedule
- **Callable functions** — client SDK calls a function directly

You write the code. Firebase deploys it. Google scales it.

---

## Project Setup

The `functions/` directory was created during `firebase init`:

```
functions/
├── src/
│   └── index.ts
├── package.json
├── tsconfig.json
└── .eslintrc.js
```

```typescript
// functions/src/index.ts
import { onDocumentUpdated } from "firebase-functions/v2/firestore";
import { onDocumentCreated } from "firebase-functions/v2/firestore";
import { onSchedule } from "firebase-functions/v2/scheduler";
import { onCall } from "firebase-functions/v2/https";
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";
import { getMessaging } from "firebase-admin/messaging";

initializeApp();
const db = getFirestore();
```

The Admin SDK (`firebase-admin`) bypasses security rules. It has full read/write access — use it only in trusted server code.

---

## Trigger: Task Assigned

When a task's `assignee` field changes, notify the new assignee:

```typescript
// functions/src/index.ts
import { onDocumentUpdated } from "firebase-functions/v2/firestore";

export const onTaskAssigned = onDocumentUpdated(
  "teams/{teamId}/tasks/{taskId}",
  async (event) => {
    const before = event.data?.before.data();
    const after = event.data?.after.data();

    if (!before || !after) return;

    // Only trigger if assignee changed
    if (before.assignee === after.assignee) return;

    // Only trigger if there's a new assignee (not unassignment)
    if (!after.assignee) return;

    const assigneeId = after.assignee;
    const taskTitle = after.title;
    const teamId = event.params.teamId;

    // Get the assignee's FCM token
    const userDoc = await db.doc(`users/${assigneeId}`).get();
    const fcmToken = userDoc.data()?.fcmToken;

    if (!fcmToken) {
      console.log(`No FCM token for user ${assigneeId}`);
      return;
    }

    // Send push notification
    await getMessaging().send({
      token: fcmToken,
      notification: {
        title: "New task assigned",
        body: `You've been assigned: "${taskTitle}"`,
      },
      data: {
        teamId,
        taskId: event.params.taskId,
        type: "task_assigned",
      },
    });

    console.log(`Notification sent to ${assigneeId} for task "${taskTitle}"`);
  }
);
```

---

## Trigger: New User Setup

When a user signs up, create their profile document:

```typescript
import { beforeUserCreated } from "firebase-functions/v2/identity";

export const onUserCreated = beforeUserCreated(async (event) => {
  const user = event.data;

  await db.doc(`users/${user.uid}`).set({
    displayName: user.displayName || "",
    email: user.email || "",
    photoURL: user.photoURL || "",
    teams: [],
    createdAt: new Date(),
  });
});
```

Or using the Auth trigger:

```typescript
import { onDocumentCreated } from "firebase-functions/v2/firestore";
import * as functions from "firebase-functions";

export const createUserProfile = functions.auth.user().onCreate(async (user) => {
  await db.doc(`users/${user.uid}`).set({
    displayName: user.displayName || "",
    email: user.email || "",
    photoURL: user.photoURL || "",
    teams: [],
    createdAt: new Date(),
  });
});
```

---

## Trigger: Document Created

When a comment is added to a task, notify the task creator:

```typescript
export const onCommentCreated = onDocumentCreated(
  "teams/{teamId}/tasks/{taskId}/comments/{commentId}",
  async (event) => {
    const comment = event.data?.data();
    if (!comment) return;

    const { teamId, taskId } = event.params;

    // Get the task to find the creator
    const taskDoc = await db.doc(`teams/${teamId}/tasks/${taskId}`).get();
    const task = taskDoc.data();

    if (!task) return;

    // Don't notify if the commenter is the task creator
    if (comment.author === task.createdBy) return;

    // Get creator's FCM token and send notification
    const creatorDoc = await db.doc(`users/${task.createdBy}`).get();
    const fcmToken = creatorDoc.data()?.fcmToken;

    if (fcmToken) {
      await getMessaging().send({
        token: fcmToken,
        notification: {
          title: `New comment on "${task.title}"`,
          body: comment.text.substring(0, 100),
        },
      });
    }
  }
);
```

---

## Scheduled Functions

Daily digest email at 8 AM:

```typescript
import { onSchedule } from "firebase-functions/v2/scheduler";

export const dailyDigest = onSchedule("every day 08:00", async (event) => {
  // Get all users
  const usersSnapshot = await db.collection("users").get();

  for (const userDoc of usersSnapshot.docs) {
    const user = userDoc.data();
    const userId = userDoc.id;

    // Get tasks assigned to this user that are due today
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    // Query across all teams for this user's tasks
    const tasksSnapshot = await db
      .collectionGroup("tasks")
      .where("assignee", "==", userId)
      .where("status", "!=", "done")
      .get();

    if (tasksSnapshot.empty) continue;

    const taskCount = tasksSnapshot.size;

    // Send summary notification
    if (user.fcmToken) {
      await getMessaging().send({
        token: user.fcmToken,
        notification: {
          title: "Daily Task Summary",
          body: `You have ${taskCount} open task${taskCount > 1 ? "s" : ""}`,
        },
      });
    }
  }
});
```

Schedule syntax:
- `"every day 08:00"` — daily at 8 AM
- `"every 5 minutes"` — every 5 minutes
- `"every monday 09:00"` — weekly
- Standard cron: `"0 8 * * *"` — 8 AM daily

---

## Callable Functions

Functions the client SDK can call directly (with auth context):

```typescript
// functions/src/index.ts
import { onCall, HttpsError } from "firebase-functions/v2/https";

export const joinTeam = onCall(async (request) => {
  // request.auth is automatically populated
  if (!request.auth) {
    throw new HttpsError("unauthenticated", "Must be signed in");
  }

  const { teamId, inviteCode } = request.data;

  // Validate invite code
  const teamDoc = await db.doc(`teams/${teamId}`).get();
  const team = teamDoc.data();

  if (!team || team.inviteCode !== inviteCode) {
    throw new HttpsError("not-found", "Invalid invite code");
  }

  // Add user to team
  await db.doc(`teams/${teamId}`).update({
    members: admin.firestore.FieldValue.arrayUnion(request.auth.uid),
  });

  // Add team to user's list
  await db.doc(`users/${request.auth.uid}`).update({
    teams: admin.firestore.FieldValue.arrayUnion(teamId),
  });

  return { success: true, teamName: team.name };
});
```

Call from the client:

```typescript
// src/services/functions.ts
import { getFunctions, httpsCallable } from "firebase/functions";

const functions = getFunctions();

export async function joinTeam(teamId: string, inviteCode: string) {
  const joinTeamFn = httpsCallable(functions, "joinTeam");
  const result = await joinTeamFn({ teamId, inviteCode });
  return result.data; // { success: true, teamName: "Acme" }
}
```

Callable functions automatically:
- Validate the auth token
- Serialize/deserialize data
- Handle CORS
- Provide `request.auth` with the user's UID

---

## Deploy Functions

```bash
firebase deploy --only functions
```

Or deploy a specific function:

```bash
firebase deploy --only functions:onTaskAssigned
```

---

## Testing with the Emulator

```bash
firebase emulators:start
```

The Functions emulator runs your code locally. Firestore triggers fire when you modify data in the Firestore emulator. Check the emulator UI → Functions tab for logs.

```typescript
// Connect client to Functions emulator
import { connectFunctionsEmulator } from "firebase/functions";

if (import.meta.env.DEV) {
  connectFunctionsEmulator(functions, "localhost", 5001);
}
```

---

## Function Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  Cloud Function Lifecycle                                    │
│                                                              │
│  1. Event occurs (document write, HTTP request, schedule)    │
│  2. Google spins up a container (cold start: 1-10 seconds)  │
│  3. Your function executes                                   │
│  4. Container stays warm for ~15 minutes                     │
│  5. Next invocation reuses warm container (fast)             │
│  6. After idle timeout, container is destroyed               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

Cold starts are a real issue. Chapter 16 covers optimization.

---

## Common Mistakes

### 1. Infinite loops

```typescript
// ❌ This function triggers itself!
export const onTaskUpdated = onDocumentUpdated("teams/{teamId}/tasks/{taskId}", async (event) => {
  // This writes to the same document, triggering this function again!
  await event.data?.after.ref.update({ processedAt: new Date() });
});
```

Fix: check if the change is relevant before writing:

```typescript
export const onTaskUpdated = onDocumentUpdated("teams/{teamId}/tasks/{taskId}", async (event) => {
  const before = event.data?.before.data();
  const after = event.data?.after.data();

  // Only process if assignee changed (not our own write)
  if (before?.assignee === after?.assignee) return;

  // Safe to write now
});
```

### 2. Not handling errors

If a function throws, it retries (for background triggers). Unhandled errors can cause infinite retries and unexpected costs.

### 3. Doing too much in one function

Keep functions focused. One trigger, one responsibility. Don't build a 500-line function that handles every possible event.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Trigger                                 │ When It Fires
────────────────────────────────────────┼──────────────────────────────────────
onDocumentCreated(path, handler)        │ Document created
onDocumentUpdated(path, handler)        │ Document modified
onDocumentDeleted(path, handler)        │ Document deleted
onDocumentWritten(path, handler)        │ Any write (create/update/delete)
onCall(handler)                         │ Client calls function
onRequest(handler)                      │ HTTP request (REST API)
onSchedule(schedule, handler)           │ Cron schedule
auth.user().onCreate(handler)           │ User signs up
auth.user().onDelete(handler)           │ User deleted
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marco: "The notification logic is ready. But how do I actually get push notifications on mobile? And how does the web app receive them?"

Firebase Cloud Messaging. Tokens, topics, and the notification payload.

---

[← Chapter 8: Indexes](chapter-08-indexes.md) | [Chapter 10: Push Notifications →](chapter-10-push-notifications.md)
