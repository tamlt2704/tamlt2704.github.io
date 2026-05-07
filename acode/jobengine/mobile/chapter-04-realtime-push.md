# Chapter 4: Real-time & Push Notifications — Never Miss a Job

[← Chapter 3: Data Fetching](chapter-03-data-fetching.md) | [Chapter 5: Performance →](chapter-05-performance.md)

---

## The Problem

Karen submits a 50,000-row CSV import. It takes 8 minutes. She locks her phone, goes to a meeting. When she comes back and opens the app, the job finished 6 minutes ago. "Why didn't it *tell* me?"

On the web dashboard, SSE keeps the UI live. But on mobile:

- The app gets suspended when backgrounded — no SSE connection survives
- You need push notifications to reach the user when the app is closed
- When the app *is* open, you still want real-time updates without polling

Two systems: **SSE for foreground**, **push notifications for background**.

## SSE on Mobile (Foreground Updates)

React Native doesn't have `EventSource` built in. We need a polyfill:

```bash
npm install react-native-sse
```

```tsx
// src/services/sseClient.ts
import EventSource from "react-native-sse";
import { API_URL } from "./config";
import { queryClient } from "./queryClient";
import type { Job } from "../types";

interface JobEvent {
  jobId: string;
  status: Job["status"];
  progress?: number;
  result?: string;
  timestamp: string;
}

let eventSource: EventSource | null = null;

export function connectSSE(token?: string) {
  if (eventSource) {
    eventSource.close();
  }

  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  eventSource = new EventSource(`${API_URL}/jobs/stream`, { headers });

  eventSource.addEventListener("job-update", (event: any) => {
    const data: JobEvent = JSON.parse(event.data);

    // Update the job in the React Query cache
    queryClient.setQueryData<Job[]>(["jobs"], (old) => {
      if (!old) return old;

      const idx = old.findIndex((j) => j.id === data.jobId);
      if (idx === -1) {
        // New job — invalidate to fetch it
        queryClient.invalidateQueries({ queryKey: ["jobs"] });
        return old;
      }

      const updated = [...old];
      updated[idx] = {
        ...updated[idx],
        status: data.status,
        progress: data.progress,
        result: data.result,
        updatedAt: data.timestamp,
      };
      return updated;
    });

    // Also update individual job query if it exists
    queryClient.setQueryData<Job>(["jobs", data.jobId], (old) => {
      if (!old) return old;
      return { ...old, status: data.status, progress: data.progress, result: data.result };
    });
  });

  eventSource.addEventListener("error", () => {
    // Reconnect after 5 seconds
    setTimeout(() => connectSSE(token), 5000);
  });
}

export function disconnectSSE() {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
}
```

### Hook into App Lifecycle

Connect SSE when the app is in the foreground, disconnect when backgrounded:

```tsx
// src/hooks/useSSE.ts
import { useEffect } from "react";
import { AppState } from "react-native";
import { connectSSE, disconnectSSE } from "../services/sseClient";
import { useAuth } from "./useAuth"; // Chapter 8

export function useSSE() {
  const { token } = useAuth();

  useEffect(() => {
    connectSSE(token);

    const subscription = AppState.addEventListener("change", (state) => {
      if (state === "active") {
        connectSSE(token);
      } else {
        disconnectSSE();
      }
    });

    return () => {
      disconnectSSE();
      subscription.remove();
    };
  }, [token]);
}
```

Now when the app is open, job cards update in real time — progress bars fill, badges change color, no polling needed.

## Push Notifications (Background Updates)

When the app is closed, you need Firebase Cloud Messaging (FCM) for Android and Apple Push Notification Service (APNs) for iOS. Expo wraps both:

```bash
npx expo install expo-notifications expo-device expo-constants
```

### Register for Push Notifications

```tsx
// src/services/notifications.ts
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { Platform } from "react-native";
import Constants from "expo-constants";
import { API_URL } from "./config";

// Configure how notifications appear when app is in foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.warn("Push notifications only work on physical devices");
    return null;
  }

  // Check existing permissions
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  // Request if not granted
  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") {
    console.warn("Push notification permission denied");
    return null;
  }

  // Get the Expo push token
  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const tokenData = await Notifications.getExpoPushTokenAsync({ projectId });
  const pushToken = tokenData.data;

  // Android needs a notification channel
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("job-updates", {
      name: "Job Updates",
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#3b82f6",
    });
  }

  return pushToken;
}

export async function sendTokenToBackend(pushToken: string, authToken: string) {
  await fetch(`${API_URL}/devices/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ token: pushToken, platform: Platform.OS }),
  });
}
```

### Notification Listener Hook

```tsx
// src/hooks/useNotifications.ts
import { useEffect, useRef } from "react";
import * as Notifications from "expo-notifications";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { JobStackParamList } from "../navigation/RootNavigator";
import { registerForPushNotifications, sendTokenToBackend } from "../services/notifications";
import { useAuth } from "./useAuth";

export function useNotifications() {
  const { token: authToken } = useAuth();
  const navigation = useNavigation<NativeStackNavigationProp<JobStackParamList>>();
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    // Register and send token to backend
    async function setup() {
      const pushToken = await registerForPushNotifications();
      if (pushToken && authToken) {
        await sendTokenToBackend(pushToken, authToken);
      }
    }
    setup();

    // Handle notification tap — navigate to the job
    responseListener.current = Notifications.addNotificationResponseReceivedListener((response) => {
      const jobId = response.notification.request.content.data?.jobId as string;
      if (jobId) {
        navigation.navigate("JobDetail", { jobId });
      }
    });

    return () => {
      if (responseListener.current) {
        Notifications.removeNotificationSubscription(responseListener.current);
      }
    };
  }, [authToken, navigation]);
}
```

### Backend: Sending Push Notifications

The backend needs to send a push when a job completes or fails. With Expo's push service:

```java
// Backend side — POST to Expo's push API
// POST https://exp.host/--/api/v2/push/send
// {
//   "to": "ExponentPushToken[xxxxxx]",
//   "title": "Job Completed ✓",
//   "body": "CSV_IMPORT finished in 8m 23s",
//   "data": { "jobId": "abc-123" }
// }
```

You don't need Firebase setup for Expo push tokens — Expo routes to FCM/APNs for you.

## Local Notifications (Foreground Alerts)

When the app is open and a job finishes, show an in-app notification banner:

```tsx
// src/components/InAppNotification.tsx
import { useEffect, useState } from "react";
import { Animated, Text, StyleSheet, Pressable } from "react-native";
import { useQueryClient } from "@tanstack/react-query";
import type { Job } from "../types";

interface Notification {
  id: string;
  message: string;
  type: "success" | "error" | "info";
}

export function InAppNotificationBanner() {
  const [notification, setNotification] = useState<Notification | null>(null);
  const slideAnim = useState(new Animated.Value(-100))[0];

  const show = (notif: Notification) => {
    setNotification(notif);
    Animated.sequence([
      Animated.spring(slideAnim, { toValue: 0, useNativeDriver: true }),
      Animated.delay(3000),
      Animated.timing(slideAnim, { toValue: -100, duration: 300, useNativeDriver: true }),
    ]).start(() => setNotification(null));
  };

  // Expose show function via context or event emitter
  // (simplified here for clarity)

  if (!notification) return null;

  const bgColor = notification.type === "success" ? "#064e3b" : notification.type === "error" ? "#7f1d1d" : "#1e3a5f";

  return (
    <Animated.View style={[styles.banner, { backgroundColor: bgColor, transform: [{ translateY: slideAnim }] }]}>
      <Text style={styles.text}>{notification.message}</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  banner: {
    position: "absolute",
    top: 50,
    left: 16,
    right: 16,
    padding: 16,
    borderRadius: 12,
    zIndex: 1000,
  },
  text: { color: "#f9fafb", fontSize: 14, fontWeight: "500" },
});
```

## Notification Categories

Different job events deserve different notification styles:

```tsx
// src/services/notificationCategories.ts
import * as Notifications from "expo-notifications";

export async function setupNotificationCategories() {
  await Notifications.setNotificationCategoryAsync("job-completed", [
    { identifier: "view", buttonTitle: "View Job", options: { opensAppToForeground: true } },
    { identifier: "dismiss", buttonTitle: "Dismiss", options: { isDestructive: true } },
  ]);

  await Notifications.setNotificationCategoryAsync("job-failed", [
    { identifier: "retry", buttonTitle: "Retry", options: { opensAppToForeground: true } },
    { identifier: "view", buttonTitle: "View Details", options: { opensAppToForeground: true } },
  ]);
}
```

Now when a job fails, the notification has a "Retry" button right on the lock screen.

## Badge Count

Show unread job completions on the app icon:

```tsx
// src/services/badge.ts
import * as Notifications from "expo-notifications";

export async function updateBadgeCount(count: number) {
  await Notifications.setBadgeCountAsync(count);
}

// Call when jobs complete while app is backgrounded
// Reset when user opens the Jobs tab
export async function clearBadge() {
  await Notifications.setBadgeCountAsync(0);
}
```

## Putting It All Together

```tsx
// App.tsx — final for this chapter
import { SafeAreaProvider } from "react-native-safe-area-context";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./src/services/queryClient";
import { RootNavigator } from "./src/navigation/RootNavigator";
import { useSSE } from "./src/hooks/useSSE";
import { useNotifications } from "./src/hooks/useNotifications";
import { useAppStateRefetch } from "./src/hooks/useAppStateRefetch";
import { setupNotificationCategories } from "./src/services/notificationCategories";
import { useEffect } from "react";

function AppContent() {
  useSSE();
  useNotifications();
  useAppStateRefetch();

  useEffect(() => {
    setupNotificationCategories();
  }, []);

  return <RootNavigator />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaProvider>
        <AppContent />
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}
```

## Verify

1. Open the app — job list updates in real time (SSE)
2. Submit a job, watch the progress bar fill without pulling to refresh
3. Background the app → submit a job from curl → wait for it to complete
4. A push notification appears: "CSV_IMPORT completed in 2m 15s"
5. Tap the notification → app opens to the Job Detail screen
6. Check the app icon — badge shows "1"
7. Open the Jobs tab — badge clears

Karen locks her phone. Goes to her meeting. Five minutes later, her phone buzzes: "CSV_IMPORT completed ✓ — 50,000 rows imported." She taps it. The app opens to the job detail. Green badge. All rows imported.

She doesn't even need to open the app anymore. The app comes to her.

"Great. But when I scroll through 500 jobs, it stutters."

Performance. Chapter 5.

---

[← Chapter 3: Data Fetching](chapter-03-data-fetching.md) | [Chapter 5: Performance →](chapter-05-performance.md)
