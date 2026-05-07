# Chapter 2: Native Styling — Building a Job List That Feels Native

[← Chapter 1: First Screen](chapter-01-first-screen.md) | [Chapter 3: Data Fetching →](chapter-03-data-fetching.md)

---

## The Problem

Karen opens the app. "It looks like a website someone shoved into a phone." She's right. The placeholder text is centered on a blank screen. No cards, no badges, no visual hierarchy. It doesn't *feel* like an app.

Native apps have specific design patterns — iOS has rounded cards with subtle shadows, Android has Material elevation. Both have pull-to-refresh, safe area insets, and platform-specific spacing. Time to make it feel native.

## StyleSheet: Not CSS

React Native's `StyleSheet` looks like CSS but isn't:

- No cascading — styles don't inherit from parents (except `Text` color within nested `Text`)
- No class names — styles are objects, applied directly
- No media queries — use `Dimensions` or `useWindowDimensions`
- No pseudo-classes — no `:hover`, `:focus` (use `Pressable` states instead)
- Units are density-independent pixels (dp) — `16` means 16dp, not 16px

```tsx
// ❌ This is NOT how it works
<View className="flex items-center p-4 bg-gray-900">

// ✅ This is React Native
<View style={styles.container}>

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    padding: 16,
    backgroundColor: "#111827",
  },
});
```

`StyleSheet.create` validates your styles at creation time and optimizes them for the bridge.

## The Job Card

```tsx
// src/components/JobCard.tsx
import { View, Text, StyleSheet, Pressable, Platform } from "react-native";
import type { Job } from "../types";

interface Props {
  job: Job;
  onPress: (jobId: string) => void;
}

export function JobCard({ job, onPress }: Props) {
  return (
    <Pressable
      onPress={() => onPress(job.id)}
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
    >
      <View style={styles.header}>
        <Text style={styles.jobType}>{job.type.replace("_", " ")}</Text>
        <StatusBadge status={job.status} />
      </View>

      <Text style={styles.jobId}>#{job.id.slice(0, 8)}</Text>

      {job.status === "RUNNING" && job.progress !== undefined && (
        <View style={styles.progressTrack}>
          <View style={[styles.progressFill, { width: `${job.progress}%` }]} />
        </View>
      )}

      <View style={styles.footer}>
        <Text style={styles.timestamp}>
          {new Date(job.createdAt).toLocaleTimeString()}
        </Text>
        <Text style={styles.priority}>{job.priority}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1f2937",
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 6,
    // Platform-specific shadows
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 4,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  cardPressed: {
    opacity: 0.8,
    transform: [{ scale: 0.98 }],
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  jobType: {
    color: "#60a5fa",
    fontSize: 14,
    fontWeight: "600",
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
  },
  jobId: {
    color: "#6b7280",
    fontSize: 12,
    marginTop: 4,
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
  },
  progressTrack: {
    height: 4,
    backgroundColor: "#374151",
    borderRadius: 2,
    marginTop: 12,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#3b82f6",
    borderRadius: 2,
  },
  footer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 12,
  },
  timestamp: {
    color: "#6b7280",
    fontSize: 11,
  },
  priority: {
    color: "#9ca3af",
    fontSize: 11,
    fontWeight: "500",
  },
});
```

## Status Badge

```tsx
// src/components/StatusBadge.tsx
import { View, Text, StyleSheet } from "react-native";
import type { JobStatus } from "../types";

const STATUS_COLORS: Record<JobStatus, { bg: string; text: string }> = {
  PENDING: { bg: "#374151", text: "#9ca3af" },
  RUNNING: { bg: "#1e3a5f", text: "#60a5fa" },
  COMPLETED: { bg: "#064e3b", text: "#34d399" },
  FAILED: { bg: "#7f1d1d", text: "#f87171" },
  CANCELLED: { bg: "#44403c", text: "#a8a29e" },
  DEAD: { bg: "#4c0519", text: "#fb7185" },
};

export function StatusBadge({ status }: { status: JobStatus }) {
  const colors = STATUS_COLORS[status];

  return (
    <View style={[styles.badge, { backgroundColor: colors.bg }]}>
      <Text style={[styles.text, { color: colors.text }]}>{status}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  text: {
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
});
```

## Types

```tsx
// src/types/index.ts
export type JobStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED" | "DEAD";

export type JobPriority = "CRITICAL" | "HIGH" | "NORMAL" | "LOW";

export interface Job {
  id: string;
  type: string;
  status: JobStatus;
  priority: JobPriority;
  progress?: number;
  result?: string;
  createdAt: string;
  updatedAt: string;
  payload?: string;
}
```

## FlatList: The Native List

On the web, you'd map over an array and render `<div>`s. On mobile, that kills performance — 10,000 job cards would mount 10,000 views. `FlatList` virtualizes: only visible items are rendered.

```tsx
// src/screens/JobListScreen.tsx
import { FlatList, StyleSheet, View, Text, RefreshControl } from "react-native";
import { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { JobCard } from "../components/JobCard";
import { StatsBar } from "../components/StatsBar";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { JobStackParamList } from "../navigation/RootNavigator";
import type { Job } from "../types";
import { useNavigation } from "@react-navigation/native";

// Mock data for now — Chapter 3 connects to the real API
const MOCK_JOBS: Job[] = [
  { id: "a1b2c3d4-e5f6", type: "CSV_IMPORT", status: "RUNNING", priority: "CRITICAL", progress: 67, createdAt: "2024-01-15T09:30:00Z", updatedAt: "2024-01-15T09:31:00Z" },
  { id: "b2c3d4e5-f6a7", type: "IMAGE_RESIZE", status: "COMPLETED", priority: "NORMAL", createdAt: "2024-01-15T09:28:00Z", updatedAt: "2024-01-15T09:29:00Z" },
  { id: "c3d4e5f6-a7b8", type: "PRICE_CALC", status: "FAILED", priority: "HIGH", result: "Exchange rate API timeout", createdAt: "2024-01-15T09:25:00Z", updatedAt: "2024-01-15T09:26:00Z" },
  { id: "d4e5f6a7-b8c9", type: "EMAIL_BATCH", status: "PENDING", priority: "LOW", createdAt: "2024-01-15T09:35:00Z", updatedAt: "2024-01-15T09:35:00Z" },
  { id: "e5f6a7b8-c9d0", type: "CSV_IMPORT", status: "CANCELLED", priority: "NORMAL", createdAt: "2024-01-15T09:20:00Z", updatedAt: "2024-01-15T09:22:00Z" },
];

export function JobListScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const navigation = useNavigation<NativeStackNavigationProp<JobStackParamList>>();

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate network delay — real fetch in Chapter 3
    await new Promise((r) => setTimeout(r, 1000));
    setRefreshing(false);
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <StatsBar jobs={MOCK_JOBS} />
      <FlatList
        data={MOCK_JOBS}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <JobCard job={item} onPress={(id) => navigation.navigate("JobDetail", { jobId: id })} />
        )}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor="#3b82f6"
            colors={["#3b82f6"]}
          />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No jobs yet</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#111827",
  },
  list: {
    paddingVertical: 8,
  },
  empty: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingTop: 100,
  },
  emptyText: {
    color: "#6b7280",
    fontSize: 16,
  },
});
```

## Stats Bar

A quick summary at the top — how many running, failed, pending:

```tsx
// src/components/StatsBar.tsx
import { View, Text, StyleSheet } from "react-native";
import type { Job, JobStatus } from "../types";

export function StatsBar({ jobs }: { jobs: Job[] }) {
  const counts = jobs.reduce(
    (acc, job) => {
      acc[job.status] = (acc[job.status] || 0) + 1;
      return acc;
    },
    {} as Record<JobStatus, number>
  );

  return (
    <View style={styles.container}>
      <StatItem label="Running" count={counts.RUNNING || 0} color="#60a5fa" />
      <StatItem label="Pending" count={counts.PENDING || 0} color="#9ca3af" />
      <StatItem label="Failed" count={counts.FAILED || 0} color="#f87171" />
      <StatItem label="Done" count={counts.COMPLETED || 0} color="#34d399" />
    </View>
  );
}

function StatItem({ label, count, color }: { label: string; count: number; color: string }) {
  return (
    <View style={styles.item}>
      <Text style={[styles.count, { color }]}>{count}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: "#1f2937",
    borderBottomWidth: 1,
    borderBottomColor: "#374151",
  },
  item: {
    alignItems: "center",
  },
  count: {
    fontSize: 20,
    fontWeight: "bold",
  },
  label: {
    color: "#6b7280",
    fontSize: 11,
    marginTop: 2,
  },
});
```

## Pull-to-Refresh

Notice `RefreshControl` in the `FlatList`. Pull down on the list and you get the native spinner — iOS's rubber-band effect, Android's circular indicator. No library needed. This is the native pattern users expect.

## Platform-Specific Code

Sometimes iOS and Android need different styles. Two approaches:

```tsx
// Approach 1: Platform.select (inline)
const styles = StyleSheet.create({
  card: {
    ...Platform.select({
      ios: { shadowColor: "#000", shadowOpacity: 0.2, shadowRadius: 4 },
      android: { elevation: 4 },
    }),
  },
});

// Approach 2: Platform-specific files
// JobCard.ios.tsx — iOS-specific implementation
// JobCard.android.tsx — Android-specific implementation
// React Native auto-resolves based on platform
```

We use `Platform.select` for small differences (shadows, fonts) and separate files for major divergences (navigation patterns, native modules).

## Safe Areas

The iPhone has a notch. The Pixel has a camera cutout. `SafeAreaView` from `react-native-safe-area-context` handles this:

```tsx
import { SafeAreaView } from "react-native-safe-area-context";

// Content won't hide behind the notch or home indicator
<SafeAreaView style={{ flex: 1 }} edges={["top", "bottom"]}>
  {/* your content */}
</SafeAreaView>
```

Always wrap your top-level screen content in `SafeAreaView`. Otherwise Karen's job list starts behind the clock.

## Verify

Run the app. You should see:

- Dark theme with the stats bar at the top
- Five job cards with colored status badges
- Pull-to-refresh with native spinner
- Tap a card → navigates to Job Detail screen
- Platform-appropriate shadows (iOS shadow vs Android elevation)
- Content respects the notch/safe area

Karen pulls down to refresh. The spinner appears. The cards have rounded corners and subtle shadows. "Okay, this looks like an app now. But where's the real data?"

That's Chapter 3.

---

[← Chapter 1: First Screen](chapter-01-first-screen.md) | [Chapter 3: Data Fetching →](chapter-03-data-fetching.md)
