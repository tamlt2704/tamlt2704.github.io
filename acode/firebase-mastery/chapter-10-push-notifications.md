# Chapter 10: Push Notifications — "Notify Me on Mobile"

[← Chapter 9: Cloud Functions](chapter-09-cloud-functions.md) | [Chapter 11: Data Modeling →](chapter-11-data-modeling.md)

---

## The Task

Marco: "The Cloud Function sends a notification when a task is assigned. But where does it go? I need actual push notifications — on my phone, in the browser. The real deal."

---

## Firebase Cloud Messaging (FCM)

FCM delivers messages to devices. The flow:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Your Server │     │     FCM      │     │   Device     │
│  (Cloud Fn)  │────▶│   (Google)   │────▶│  (browser/   │
│              │     │              │     │   mobile)    │
└──────────────┘     └──────────────┘     └──────────────┘
     sends                routes              displays
     message              to device           notification
```

1. Device registers with FCM → gets a **token**
2. You store the token in Firestore
3. Cloud Function sends a message to that token
4. FCM delivers it to the device

---

## Get the FCM Token (Web)

```typescript
// src/services/notifications.ts
import { getMessaging, getToken, onMessage } from "firebase/messaging";
import { doc, updateDoc } from "firebase/firestore";
import { db, auth } from "../firebase";

const messaging = getMessaging();

export async function requestNotificationPermission() {
  const permission = await Notification.requestPermission();

  if (permission !== "granted") {
    console.log("Notification permission denied");
    return null;
  }

  // Get the FCM token
  const token = await getToken(messaging, {
    vapidKey: "YOUR_VAPID_KEY_FROM_FIREBASE_CONSOLE",
  });

  // Store it in the user's profile
  const user = auth.currentUser;
  if (user && token) {
    await updateDoc(doc(db, "users", user.uid), {
      fcmToken: token,
    });
  }

  return token;
}
```

Get the VAPID key from: Firebase console → Project Settings → Cloud Messaging → Web Push certificates.

---

## Service Worker (Required for Web)

FCM on web requires a service worker. Create `public/firebase-messaging-sw.js`:

```javascript
// public/firebase-messaging-sw.js
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSy...",
  authDomain: "snaptask-dev-abc.firebaseapp.com",
  projectId: "snaptask-dev-abc",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123",
});

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  const { title, body } = payload.notification || {};

  self.registration.showNotification(title || "SnapTask", {
    body: body || "You have a new notification",
    icon: "/icon-192.png",
    data: payload.data,
  });
});
```

This file must be at the root of your hosting directory (`public/` or `dist/`).

---

## Handle Foreground Messages

When the app is open and in focus, notifications don't show automatically. Handle them:

```typescript
// src/services/notifications.ts
import { onMessage } from "firebase/messaging";

export function listenForMessages(callback: (payload: any) => void) {
  return onMessage(messaging, (payload) => {
    console.log("Foreground message:", payload);
    callback(payload);

    // Optionally show a toast/banner in the app
    // Don't use Notification API here — the app is already in focus
  });
}
```

```tsx
// src/App.tsx
import { useEffect } from "react";
import { listenForMessages } from "./services/notifications";

function App() {
  useEffect(() => {
    const unsubscribe = listenForMessages((payload) => {
      // Show in-app notification (toast, banner, etc.)
      showToast(payload.notification?.title, payload.notification?.body);
    });

    return unsubscribe;
  }, []);

  // ...
}
```

---

## Sending Notifications (Server-Side)

From Cloud Functions (using Admin SDK):

```typescript
import { getMessaging } from "firebase-admin/messaging";

// Send to a specific device
await getMessaging().send({
  token: userFcmToken,
  notification: {
    title: "Task assigned",
    body: "You've been assigned: Design landing page",
  },
  data: {
    taskId: "task-123",
    teamId: "team-abc",
    type: "task_assigned",
  },
  webpush: {
    fcmOptions: {
      link: "https://snaptask-dev.web.app/teams/team-abc/tasks/task-123",
    },
  },
});
```

---

## Topics: Broadcast to Groups

Instead of sending to individual tokens, subscribe users to topics:

```typescript
// Client-side: subscribe to a topic
import { getMessaging, getToken } from "firebase/messaging";

// You can't subscribe to topics from the client on web.
// Use Cloud Functions instead:

// functions/src/index.ts
export const subscribeToTeam = onCall(async (request) => {
  const { teamId } = request.data;
  const userId = request.auth?.uid;

  const userDoc = await db.doc(`users/${userId}`).get();
  const token = userDoc.data()?.fcmToken;

  if (token) {
    await getMessaging().subscribeToTopic(token, `team_${teamId}`);
  }

  return { success: true };
});
```

Send to all subscribers of a topic:

```typescript
await getMessaging().send({
  topic: "team_team-abc",
  notification: {
    title: "Team announcement",
    body: "Sprint planning at 2 PM",
  },
});
```

---

## Notification Payload Structure

```typescript
const message = {
  // Who to send to (pick one):
  token: "device-token",        // specific device
  topic: "team_abc",            // all subscribers
  condition: "'team_abc' in topics || 'admins' in topics", // logic

  // What the user sees:
  notification: {
    title: "Task assigned",
    body: "You've been assigned: Design landing page",
    imageUrl: "https://example.com/image.png", // optional
  },

  // Custom data (for your app logic):
  data: {
    taskId: "task-123",
    type: "task_assigned",
    // All values must be strings!
    priority: "high",
  },

  // Platform-specific options:
  webpush: {
    fcmOptions: {
      link: "https://snaptask.web.app/task/123", // click action
    },
  },
  android: {
    priority: "high",
    notification: {
      channelId: "tasks",
    },
  },
  apns: {
    payload: {
      aps: {
        badge: 1,
        sound: "default",
      },
    },
  },
};
```

---

## Token Lifecycle

FCM tokens can change. Handle token refresh:

```typescript
import { getToken, onMessage } from "firebase/messaging";

// Tokens refresh periodically — update Firestore when they do
export async function refreshToken() {
  const token = await getToken(messaging, { vapidKey: "..." });
  const user = auth.currentUser;

  if (user && token) {
    await updateDoc(doc(db, "users", user.uid), { fcmToken: token });
  }
}
```

Tokens become invalid when:
- User uninstalls the app
- User clears browser data
- Token expires (rare, but happens)

When sending fails with `messaging/registration-token-not-registered`, remove the stale token:

```typescript
try {
  await getMessaging().send({ token, notification: { title: "Test" } });
} catch (error: any) {
  if (error.code === "messaging/registration-token-not-registered") {
    // Token is stale — remove it
    await db.doc(`users/${userId}`).update({ fcmToken: null });
  }
}
```

---

## Request Permission UX

Don't ask for notification permission on page load. Users deny it reflexively. Ask at the right moment:

```tsx
function TaskAssignedBanner({ task }) {
  const [showPermissionPrompt, setShowPermissionPrompt] = useState(false);

  useEffect(() => {
    // Show prompt only if permission hasn't been decided
    if (Notification.permission === "default") {
      setShowPermissionPrompt(true);
    }
  }, []);

  if (!showPermissionPrompt) return null;

  return (
    <div className="banner">
      <p>Want to get notified when tasks are assigned to you?</p>
      <button onClick={async () => {
        await requestNotificationPermission();
        setShowPermissionPrompt(false);
      }}>
        Enable notifications
      </button>
      <button onClick={() => setShowPermissionPrompt(false)}>
        Not now
      </button>
    </div>
  );
}
```

---

## Common Mistakes

### 1. Requesting permission too early

Browsers show "Block" by default if you ask on page load. Wait until the user takes an action that makes notifications relevant.

### 2. Not handling token refresh

If the token changes and you don't update Firestore, notifications stop working silently.

### 3. Sending only `notification` without `data`

If you only send `notification`, your app can't handle the click action or route to the right screen. Always include `data` with context.

### 4. Forgetting the service worker

Without `firebase-messaging-sw.js`, background notifications won't work on web.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Concept                                 │ Details
────────────────────────────────────────┼──────────────────────────────────────
getToken(messaging, { vapidKey })       │ Get device FCM token
onMessage(messaging, callback)          │ Handle foreground messages
firebase-messaging-sw.js               │ Service worker for background
getMessaging().send({ token, ... })     │ Send to one device (Admin SDK)
getMessaging().send({ topic, ... })     │ Send to topic subscribers
subscribeToTopic(token, topic)          │ Subscribe device to topic
notification payload                    │ What user sees (title, body)
data payload                            │ Custom data for app logic
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The MVP is shipped. Auth, database, real-time, security, storage, queries, functions, notifications. But Lena notices a problem:

"When I open the team page, it loads ALL 500 tasks. The page takes 3 seconds to load. And our Firestore bill is climbing."

Time to rethink the data model.

---

[← Chapter 9: Cloud Functions](chapter-09-cloud-functions.md) | [Chapter 11: Data Modeling →](chapter-11-data-modeling.md)
