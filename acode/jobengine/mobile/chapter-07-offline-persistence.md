# Chapter 7: Offline & Persistence — Works Without WiFi

[← Chapter 6: Gestures & Animations](chapter-06-gestures-animations.md) | [Chapter 8: Authentication →](chapter-08-authentication.md)

---

## The Problem

Karen steps into the elevator. Signal drops. She opens the app — blank screen, "Failed to load jobs." She walks into the parking garage — same thing. "The web version at least shows the last data I saw. This shows nothing."

Mobile apps live in a world of unreliable connectivity. The app needs to:

1. **Show cached data** when offline (last known state)
2. **Queue actions** performed offline (cancel, submit) and sync when back online
3. **Indicate** what's stale vs fresh
4. **Persist** the cache across app restarts (cold start should show data immediately)

## Architecture: The Offline Stack

```
┌─────────────────────────────────────┐
│           UI Components             │
├─────────────────────────────────────┤
│         React Query Cache           │  ← In-memory, fast
├─────────────────────────────────────┤
│     AsyncStorage / MMKV             │  ← Persisted to disk
├─────────────────────────────────────┤
│         Sync Queue                  │  ← Pending mutations
├─────────────────────────────────────┤
│       Network (when available)      │
└─────────────────────────────────────┘
```

## Step 1: Detect Network State

```bash
npx expo install @react-native-community/netinfo
```

```tsx
// src/hooks/useNetworkStatus.ts
import { useEffect, useState } from "react";
import NetInfo, { NetInfoState } from "@react-native-community/netinfo";

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState(true);
  const [connectionType, setConnectionType] = useState<string>("unknown");

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state: NetInfoState) => {
      setIsConnected(state.isConnected ?? false);
      setConnectionType(state.type);
    });

    return () => unsubscribe();
  }, []);

  return { isConnected, connectionType };
}
```

Show a banner when offline:

```tsx
// src/components/OfflineBanner.tsx
import { View, Text, StyleSheet } from "react-native";
import Animated, { useAnimatedStyle, withTiming, useSharedValue, withRepeat } from "react-native-reanimated";
import { useNetworkStatus } from "../hooks/useNetworkStatus";
import { useEffect } from "react";

export function OfflineBanner() {
  const { isConnected } = useNetworkStatus();
  const opacity = useSharedValue(0);

  useEffect(() => {
    opacity.value = withTiming(isConnected ? 0 : 1, { duration: 300 });
  }, [isConnected]);

  const style = useAnimatedStyle(() => ({
    opacity: opacity.value,
    height: opacity.value === 0 ? 0 : 36,
  }));

  return (
    <Animated.View style={[styles.banner, style]}>
      <Text style={styles.text}>📡 No connection — showing cached data</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: "#92400e",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  text: { color: "#fef3c7", fontSize: 12, fontWeight: "500" },
});
```

## Step 2: Persist React Query Cache

MMKV is 30x faster than AsyncStorage for key-value storage:

```bash
npm install react-native-mmkv
npx expo install @tanstack/query-async-storage-persister @tanstack/react-query-persist-client
```

```tsx
// src/services/storage.ts
import { MMKV } from "react-native-mmkv";

export const storage = new MMKV({
  id: "jobengine-cache",
  encryptionKey: "shopzilla-2024", // Encrypt cached data at rest
});

// Adapter for React Query persister
export const mmkvStorageAdapter = {
  getItem: (key: string) => {
    const value = storage.getString(key);
    return value ?? null;
  },
  setItem: (key: string, value: string) => {
    storage.set(key, value);
  },
  removeItem: (key: string) => {
    storage.delete(key);
  },
};
```

```tsx
// src/services/queryClient.ts — updated with persistence
import { QueryClient } from "@tanstack/react-query";
import { createSyncStoragePersister } from "@tanstack/query-sync-storage-persister";
import { mmkvStorageAdapter } from "./storage";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      gcTime: 1000 * 60 * 60 * 24, // Keep cache for 24 hours
      retry: 3,
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000),
    },
  },
});

export const persister = createSyncStoragePersister({
  storage: mmkvStorageAdapter,
  serialize: JSON.stringify,
  deserialize: JSON.parse,
});
```

```tsx
// App.tsx — wrap with PersistQueryClientProvider
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { queryClient, persister } from "./src/services/queryClient";

export default function App() {
  return (
    <PersistQueryClientProvider client={queryClient} persistOptions={{ persister, maxAge: 1000 * 60 * 60 * 24 }}>
      <SafeAreaProvider>
        <AppContent />
      </SafeAreaProvider>
    </PersistQueryClientProvider>
  );
}
```

Now when Karen opens the app:
1. **Instant**: Cached data loads from MMKV (< 5ms)
2. **Background**: Fresh data fetches from the API
3. **Offline**: Cached data shows with "stale" indicator

## Step 3: Offline Mutation Queue

When Karen cancels a job while offline, queue it and sync later:

```tsx
// src/services/syncQueue.ts
import { storage } from "./storage";
import { API_URL } from "./config";
import NetInfo from "@react-native-community/netinfo";

interface QueuedMutation {
  id: string;
  url: string;
  method: string;
  body?: string;
  timestamp: number;
  retries: number;
}

const QUEUE_KEY = "mutation-queue";

function getQueue(): QueuedMutation[] {
  const raw = storage.getString(QUEUE_KEY);
  return raw ? JSON.parse(raw) : [];
}

function saveQueue(queue: QueuedMutation[]) {
  storage.set(QUEUE_KEY, JSON.stringify(queue));
}

export function enqueue(mutation: Omit<QueuedMutation, "id" | "timestamp" | "retries">) {
  const queue = getQueue();
  queue.push({
    ...mutation,
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    timestamp: Date.now(),
    retries: 0,
  });
  saveQueue(queue);
}

export async function processQueue(authToken?: string): Promise<{ processed: number; failed: number }> {
  const state = await NetInfo.fetch();
  if (!state.isConnected) return { processed: 0, failed: 0 };

  const queue = getQueue();
  if (queue.length === 0) return { processed: 0, failed: 0 };

  let processed = 0;
  let failed = 0;
  const remaining: QueuedMutation[] = [];

  for (const mutation of queue) {
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

      const res = await fetch(mutation.url, {
        method: mutation.method,
        headers,
        body: mutation.body,
      });

      if (res.ok) {
        processed++;
      } else if (res.status >= 500 && mutation.retries < 3) {
        // Server error — retry later
        remaining.push({ ...mutation, retries: mutation.retries + 1 });
        failed++;
      } else {
        // Client error or max retries — drop it
        failed++;
      }
    } catch {
      // Network error — keep in queue
      remaining.push(mutation);
      failed++;
    }
  }

  saveQueue(remaining);
  return { processed, failed };
}

export function getQueueSize(): number {
  return getQueue().length;
}
```

## Step 4: Optimistic Updates

When Karen cancels a job offline, update the UI immediately — don't wait for the server:

```tsx
// src/hooks/useJobMutations.ts — updated with offline support
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { jobsApi } from "../services/api";
import { enqueue } from "../services/syncQueue";
import { useNetworkStatus } from "./useNetworkStatus";
import { API_URL } from "../services/config";
import type { Job } from "../types";

export function useCancelJob() {
  const queryClient = useQueryClient();
  const { isConnected } = useNetworkStatus();

  return useMutation({
    mutationFn: async (id: string) => {
      if (!isConnected) {
        // Queue for later
        enqueue({ url: `${API_URL}/jobs/${id}/cancel`, method: "POST" });
        return;
      }
      return jobsApi.cancel(id);
    },
    // Optimistic update — update UI before server responds
    onMutate: async (id: string) => {
      await queryClient.cancelQueries({ queryKey: ["jobs"] });

      const previousJobs = queryClient.getQueryData<Job[]>(["jobs"]);

      queryClient.setQueryData<Job[]>(["jobs"], (old) =>
        old?.map((job) => (job.id === id ? { ...job, status: "CANCELLED" } : job))
      );

      return { previousJobs };
    },
    onError: (_err, _id, context) => {
      // Rollback on error
      if (context?.previousJobs) {
        queryClient.setQueryData(["jobs"], context.previousJobs);
      }
    },
    onSettled: () => {
      if (isConnected) {
        queryClient.invalidateQueries({ queryKey: ["jobs"] });
      }
    },
  });
}
```

## Step 5: Sync When Back Online

```tsx
// src/hooks/useSyncOnReconnect.ts
import { useEffect } from "react";
import NetInfo from "@react-native-community/netinfo";
import { useQueryClient } from "@tanstack/react-query";
import { processQueue } from "../services/syncQueue";
import { useAuth } from "./useAuth";

export function useSyncOnReconnect() {
  const queryClient = useQueryClient();
  const { token } = useAuth();

  useEffect(() => {
    let wasOffline = false;

    const unsubscribe = NetInfo.addEventListener(async (state) => {
      if (state.isConnected && wasOffline) {
        // We're back online — process queued mutations
        const result = await processQueue(token);
        if (result.processed > 0) {
          // Refresh all data after syncing
          queryClient.invalidateQueries();
        }
      }
      wasOffline = !state.isConnected;
    });

    return () => unsubscribe();
  }, [queryClient, token]);
}
```

## Step 6: Stale Data Indicators

Show users when they're looking at cached data:

```tsx
// src/components/FreshnessIndicator.tsx
import { View, Text, StyleSheet } from "react-native";

interface Props {
  lastUpdated: number | undefined;
  isStale: boolean;
}

export function FreshnessIndicator({ lastUpdated, isStale }: Props) {
  if (!lastUpdated) return null;

  const age = Date.now() - lastUpdated;
  const minutes = Math.floor(age / 60000);

  if (!isStale) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.text}>
        Updated {minutes < 1 ? "just now" : `${minutes}m ago`}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    backgroundColor: "#1f2937",
  },
  text: { color: "#6b7280", fontSize: 11, textAlign: "center" },
});
```

Use it in the job list:

```tsx
const { data, dataUpdatedAt, isStale } = useJobs();

<FreshnessIndicator lastUpdated={dataUpdatedAt} isStale={isStale} />
```

## Step 7: Persistent User Preferences

Store user settings (filter preferences, sort order) that survive app restarts:

```tsx
// src/store/preferences.ts
import { storage } from "../services/storage";

interface Preferences {
  sortBy: "createdAt" | "priority" | "status";
  sortOrder: "asc" | "desc";
  filterStatus: string[];
  showCompletedJobs: boolean;
}

const PREFS_KEY = "user-preferences";

const DEFAULTS: Preferences = {
  sortBy: "createdAt",
  sortOrder: "desc",
  filterStatus: [],
  showCompletedJobs: true,
};

export function getPreferences(): Preferences {
  const raw = storage.getString(PREFS_KEY);
  return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : DEFAULTS;
}

export function setPreferences(prefs: Partial<Preferences>) {
  const current = getPreferences();
  storage.set(PREFS_KEY, JSON.stringify({ ...current, ...prefs }));
}
```

## The Offline Experience

| Scenario | Behavior |
|---|---|
| App opens with no network | Shows cached jobs instantly, offline banner visible |
| User cancels a job offline | UI updates immediately (optimistic), mutation queued |
| Network returns | Queue processes, data refreshes, banner disappears |
| App killed and reopened offline | Cache loads from MMKV in < 5ms |
| Cache is 24h old | Shows data with "Updated 14h ago" indicator |
| Server returns 500 during sync | Mutation retried up to 3 times |

## Verify

1. Load the app with network → jobs appear
2. Enable airplane mode → offline banner shows
3. Pull to refresh → shows "No connection" but keeps cached data
4. Cancel a job → card immediately shows CANCELLED status
5. Disable airplane mode → banner disappears, queue syncs, data refreshes
6. Kill the app → reopen → cached data appears instantly (no loading spinner)
7. Check MMKV storage size: should be < 1MB for 1000 jobs

Karen walks into the elevator. The banner says "No connection — showing cached data." She can still see her jobs. She swipes to cancel one — it goes grey immediately. She walks out of the elevator. The banner disappears. The cancel syncs. Everything is consistent.

"Now how do I log in? Anyone can see our jobs right now."

Authentication. Chapter 8.

---

[← Chapter 6: Gestures & Animations](chapter-06-gestures-animations.md) | [Chapter 8: Authentication →](chapter-08-authentication.md)
