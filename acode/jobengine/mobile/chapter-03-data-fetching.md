# Chapter 3: Data Fetching — Talking to the Backend

[← Chapter 2: Native Styling](chapter-02-native-styling.md) | [Chapter 4: Real-time & Push Notifications →](chapter-04-realtime-push.md)

---

## The Problem

The job list shows mock data. Karen submits a CSV import from her desk, walks to the coffee machine, opens the app — and sees the same five fake jobs from Chapter 2. "Where's my import?"

Time to connect to the real backend. But mobile has complications the web didn't:

- The phone isn't on `localhost` — you need a real network address
- The connection drops when Karen walks into the elevator
- The app might be backgrounded mid-request
- You need to cache data so the list isn't blank every time she opens the app

## Environment Configuration

The backend runs on your dev machine. Your phone needs to reach it.

```tsx
// src/services/config.ts
import { Platform } from "react-native";

const DEV_API_URL = Platform.select({
  ios: "http://localhost:8080",        // iOS simulator shares host network
  android: "http://10.0.2.2:8080",    // Android emulator's host alias
  default: "http://localhost:8080",
});

const PROD_API_URL = "https://api.shopzilla.com";

export const API_URL = __DEV__ ? DEV_API_URL : PROD_API_URL;
```

For a physical device on the same WiFi, use your machine's local IP:

```tsx
// When testing on a real phone:
// const DEV_API_URL = "http://192.168.1.42:8080";
```

## TanStack Query (React Query): Server State Done Right

On the web dashboard, we used raw `fetch` + `useState`. That works, but on mobile you need:

- Automatic background refetch when the app comes to foreground
- Cache that persists across screen navigations
- Retry logic for flaky mobile connections
- Loading/error/success states without boilerplate

TanStack Query handles all of this.

```bash
npm install @tanstack/react-query
```

### Setup the Provider

```tsx
// src/services/queryClient.ts
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,        // Data is fresh for 30 seconds
      retry: 3,                  // Retry failed requests 3 times
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000),
      refetchOnWindowFocus: true, // Refetch when app comes to foreground
    },
  },
});
```

```tsx
// App.tsx — updated
import { SafeAreaProvider } from "react-native-safe-area-context";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./src/services/queryClient";
import { RootNavigator } from "./src/navigation/RootNavigator";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaProvider>
        <RootNavigator />
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}
```

## The API Service

```tsx
// src/services/api.ts
import { API_URL } from "./config";
import type { Job } from "../types";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${path}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, `${res.status}: ${body}`);
  }

  return res.json();
}

export const jobsApi = {
  getAll: () => request<Job[]>("/jobs"),

  getById: (id: string) => request<Job>(`/jobs/${id}`),

  submit: (type: string, payload: string, priority = "NORMAL") =>
    request<Job>("/jobs", {
      method: "POST",
      body: JSON.stringify({ type, payload, priority }),
    }),

  cancel: (id: string) =>
    request<void>(`/jobs/${id}/cancel`, { method: "POST" }),

  pause: (id: string) =>
    request<void>(`/jobs/${id}/pause`, { method: "POST" }),

  resume: (id: string) =>
    request<void>(`/jobs/${id}/resume`, { method: "POST" }),
};
```

## Custom Hooks with React Query

```tsx
// src/hooks/useJobs.ts
import { useQuery } from "@tanstack/react-query";
import { jobsApi } from "../services/api";

export function useJobs() {
  return useQuery({
    queryKey: ["jobs"],
    queryFn: jobsApi.getAll,
    refetchInterval: 10_000, // Poll every 10s as fallback (SSE in Chapter 4)
  });
}

export function useJob(id: string) {
  return useQuery({
    queryKey: ["jobs", id],
    queryFn: () => jobsApi.getById(id),
  });
}
```

```tsx
// src/hooks/useJobMutations.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { jobsApi } from "../services/api";

export function useSubmitJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ type, payload, priority }: { type: string; payload: string; priority?: string }) =>
      jobsApi.submit(type, payload, priority),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });
}

export function useCancelJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => jobsApi.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });
}
```

## Update the Job List Screen

```tsx
// src/screens/JobListScreen.tsx — updated
import { FlatList, StyleSheet, View, Text, RefreshControl, ActivityIndicator } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { JobCard } from "../components/JobCard";
import { StatsBar } from "../components/StatsBar";
import { useJobs } from "../hooks/useJobs";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { JobStackParamList } from "../navigation/RootNavigator";
import { useNavigation } from "@react-navigation/native";

export function JobListScreen() {
  const { data: jobs, isLoading, error, refetch, isRefetching } = useJobs();
  const navigation = useNavigation<NativeStackNavigationProp<JobStackParamList>>();

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Loading jobs...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Failed to load jobs</Text>
        <Text style={styles.errorDetail}>{(error as Error).message}</Text>
        <Text style={styles.retry} onPress={() => refetch()}>
          Tap to retry
        </Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <StatsBar jobs={jobs ?? []} />
      <FlatList
        data={jobs}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <JobCard job={item} onPress={(id) => navigation.navigate("JobDetail", { jobId: id })} />
        )}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
            tintColor="#3b82f6"
            colors={["#3b82f6"]}
          />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No jobs yet</Text>
            <Text style={styles.emptyHint}>Submit one from the Submit tab</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827" },
  center: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  list: { paddingVertical: 8 },
  loadingText: { color: "#6b7280", marginTop: 12, fontSize: 14 },
  errorText: { color: "#f87171", fontSize: 18, fontWeight: "bold" },
  errorDetail: { color: "#6b7280", fontSize: 13, marginTop: 8, textAlign: "center", paddingHorizontal: 32 },
  retry: { color: "#3b82f6", fontSize: 14, marginTop: 16, fontWeight: "600" },
  empty: { alignItems: "center", paddingTop: 100 },
  emptyText: { color: "#6b7280", fontSize: 16 },
  emptyHint: { color: "#4b5563", fontSize: 13, marginTop: 4 },
});
```

## Submit Job Screen

```tsx
// src/screens/SubmitJobScreen.tsx — updated
import { View, Text, TextInput, StyleSheet, Pressable, Alert, ScrollView } from "react-native";
import { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useSubmitJob } from "../hooks/useJobMutations";
import type { JobPriority } from "../types";

const JOB_TYPES = ["CSV_IMPORT", "IMAGE_RESIZE", "PRICE_CALC", "EMAIL_BATCH"];
const PRIORITIES: JobPriority[] = ["CRITICAL", "HIGH", "NORMAL", "LOW"];

export function SubmitJobScreen() {
  const [type, setType] = useState(JOB_TYPES[0]);
  const [payload, setPayload] = useState("");
  const [priority, setPriority] = useState<JobPriority>("NORMAL");
  const submitJob = useSubmitJob();

  const handleSubmit = () => {
    if (!payload.trim()) {
      Alert.alert("Missing payload", "Enter a payload for the job");
      return;
    }

    submitJob.mutate(
      { type, payload, priority },
      {
        onSuccess: () => {
          Alert.alert("Job submitted", `${type} job queued with ${priority} priority`);
          setPayload("");
        },
        onError: (err) => {
          Alert.alert("Submission failed", (err as Error).message);
        },
      }
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.form}>
        <Text style={styles.label}>Job Type</Text>
        <View style={styles.chipRow}>
          {JOB_TYPES.map((t) => (
            <Pressable
              key={t}
              style={[styles.chip, type === t && styles.chipActive]}
              onPress={() => setType(t)}
            >
              <Text style={[styles.chipText, type === t && styles.chipTextActive]}>
                {t.replace("_", " ")}
              </Text>
            </Pressable>
          ))}
        </View>

        <Text style={styles.label}>Priority</Text>
        <View style={styles.chipRow}>
          {PRIORITIES.map((p) => (
            <Pressable
              key={p}
              style={[styles.chip, priority === p && styles.chipActive]}
              onPress={() => setPriority(p)}
            >
              <Text style={[styles.chipText, priority === p && styles.chipTextActive]}>{p}</Text>
            </Pressable>
          ))}
        </View>

        <Text style={styles.label}>Payload</Text>
        <TextInput
          style={styles.input}
          value={payload}
          onChangeText={setPayload}
          placeholder='{"file": "products.csv"}'
          placeholderTextColor="#4b5563"
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />

        <Pressable
          style={[styles.submitButton, submitJob.isPending && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={submitJob.isPending}
        >
          <Text style={styles.submitText}>
            {submitJob.isPending ? "Submitting..." : "Submit Job"}
          </Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827" },
  form: { padding: 20 },
  label: { color: "#d1d5db", fontSize: 14, fontWeight: "600", marginTop: 20, marginBottom: 8 },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: "#1f2937",
    borderWidth: 1,
    borderColor: "#374151",
  },
  chipActive: { backgroundColor: "#1e3a5f", borderColor: "#3b82f6" },
  chipText: { color: "#9ca3af", fontSize: 13, fontWeight: "500" },
  chipTextActive: { color: "#60a5fa" },
  input: {
    backgroundColor: "#1f2937",
    borderWidth: 1,
    borderColor: "#374151",
    borderRadius: 8,
    padding: 12,
    color: "#f9fafb",
    fontSize: 14,
    minHeight: 100,
    fontFamily: "monospace",
  },
  submitButton: {
    backgroundColor: "#3b82f6",
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 24,
  },
  submitButtonDisabled: { opacity: 0.6 },
  submitText: { color: "#ffffff", fontSize: 16, fontWeight: "bold" },
});
```

## Foreground Refetch with AppState

When Karen switches back to the app from Messages, the data should refresh automatically:

```tsx
// src/hooks/useAppStateRefetch.ts
import { useEffect } from "react";
import { AppState } from "react-native";
import { useQueryClient } from "@tanstack/react-query";

export function useAppStateRefetch() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const subscription = AppState.addEventListener("change", (state) => {
      if (state === "active") {
        queryClient.invalidateQueries();
      }
    });

    return () => subscription.remove();
  }, [queryClient]);
}
```

Add it to `App.tsx`:

```tsx
import { useAppStateRefetch } from "./src/hooks/useAppStateRefetch";

function AppContent() {
  useAppStateRefetch();
  return <RootNavigator />;
}
```

Now every time the app comes to the foreground, all queries are invalidated and refetched. React Query deduplicates — if two screens use `useJobs()`, only one network request fires.

## Error Boundaries for Network Failures

Mobile networks are unreliable. Wrap screens in an error boundary:

```tsx
// src/components/ErrorFallback.tsx
import { View, Text, Pressable, StyleSheet } from "react-native";

interface Props {
  error: Error;
  onRetry: () => void;
}

export function ErrorFallback({ error, onRetry }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.emoji}>📡</Text>
      <Text style={styles.title}>Connection Problem</Text>
      <Text style={styles.message}>{error.message}</Text>
      <Pressable style={styles.button} onPress={onRetry}>
        <Text style={styles.buttonText}>Try Again</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center", padding: 32 },
  emoji: { fontSize: 48, marginBottom: 16 },
  title: { color: "#f9fafb", fontSize: 20, fontWeight: "bold" },
  message: { color: "#6b7280", fontSize: 14, textAlign: "center", marginTop: 8 },
  button: { backgroundColor: "#3b82f6", borderRadius: 8, paddingHorizontal: 24, paddingVertical: 12, marginTop: 24 },
  buttonText: { color: "#fff", fontWeight: "600" },
});
```

## Verify

1. Start the backend: `./gradlew bootRun`
2. Run the app: `npx expo start`
3. The job list loads real data from the API
4. Pull-to-refresh fetches fresh data
5. Submit a job from the Submit tab → switch to Jobs tab → it appears
6. Kill the backend → the error screen shows with "Tap to retry"
7. Background the app → reopen → data refreshes automatically

Karen submits a CSV import from her desk. Walks to the coffee machine. Opens the app. Her import is there, status RUNNING, progress bar filling. She smiles.

"But I have to keep opening the app to check. Can't it just tell me when it's done?"

Push notifications. That's Chapter 4.

---

[← Chapter 2: Native Styling](chapter-02-native-styling.md) | [Chapter 4: Real-time & Push Notifications →](chapter-04-realtime-push.md)
