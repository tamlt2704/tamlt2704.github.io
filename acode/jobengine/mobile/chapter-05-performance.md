# Chapter 5: Performance — Silky Smooth at 10,000 Jobs

[← Chapter 4: Real-time & Push](chapter-04-realtime-push.md) | [Chapter 6: Gestures & Animations →](chapter-06-gestures-animations.md)

---

## The Problem

Black Friday. ShopZilla processes 10,000 jobs in a day. Karen scrolls through the job list and it stutters — frames drop, the scroll hitches, her phone gets warm. "This app is slow."

It's not the phone. It's your rendering. Every time a job updates via SSE, the entire list re-renders. Every card recalculates its styles. The FlatList is doing its best, but you're fighting it.

Time to profile, measure, and fix.

## Measuring: The Perf Monitor

Enable the React Native performance monitor:

```tsx
// In development, shake the device → "Show Perf Monitor"
// Or add to App.tsx:
if (__DEV__) {
  // Shows FPS counter on screen
  require("react-native").DevSettings?.addMenuItem("Toggle Perf", () => {
    // Toggle performance overlay
  });
}
```

What to watch:
- **JS FPS**: Should stay at 60. Drops mean your JavaScript thread is busy.
- **UI FPS**: Should stay at 60. Drops mean the native UI thread is blocked.
- **RAM**: Watch for memory leaks (steadily increasing).

For deeper profiling, use **Flipper** (React Native's debugging tool):

```bash
# Install Flipper from https://fbflipper.com/
# It connects automatically to your running app
```

## Problem 1: Unnecessary Re-renders

Every SSE event updates the jobs array. React re-renders the entire `FlatList`. Even cards that didn't change re-render.

### Fix: `React.memo` + Stable References

```tsx
// src/components/JobCard.tsx — memoized
import { memo } from "react";
import { View, Text, StyleSheet, Pressable, Platform } from "react-native";
import type { Job } from "../types";
import { StatusBadge } from "./StatusBadge";

interface Props {
  job: Job;
  onPress: (jobId: string) => void;
}

export const JobCard = memo(function JobCard({ job, onPress }: Props) {
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
        <ProgressBar progress={job.progress} />
      )}
      <View style={styles.footer}>
        <Text style={styles.timestamp}>{new Date(job.createdAt).toLocaleTimeString()}</Text>
        <Text style={styles.priority}>{job.priority}</Text>
      </View>
    </Pressable>
  );
});

// Only re-render if the job actually changed
// React.memo does shallow comparison by default
// For deeper control:
export const JobCardOptimized = memo(
  function JobCard({ job, onPress }: Props) {
    // ... same JSX
    return <View />;
  },
  (prev, next) => {
    // Custom comparison — only re-render if these fields changed
    return (
      prev.job.id === next.job.id &&
      prev.job.status === next.job.status &&
      prev.job.progress === next.job.progress &&
      prev.job.result === next.job.result
    );
  }
);
```

### Fix: Stable `onPress` with `useCallback`

```tsx
// src/screens/JobListScreen.tsx
import { useCallback } from "react";

export function JobListScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<JobStackParamList>>();

  // ❌ Creates a new function every render — breaks memo
  // const handlePress = (id: string) => navigation.navigate("JobDetail", { jobId: id });

  // ✅ Stable reference — memo works
  const handlePress = useCallback(
    (id: string) => navigation.navigate("JobDetail", { jobId: id }),
    [navigation]
  );

  return (
    <FlatList
      data={jobs}
      renderItem={({ item }) => <JobCard job={item} onPress={handlePress} />}
      // ...
    />
  );
}
```

## Problem 2: FlatList Configuration

The default `FlatList` renders 10 items initially and loads more as you scroll. For 10,000 items, we need to tune it:

```tsx
<FlatList
  data={jobs}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}
  // Performance props
  initialNumToRender={15}           // Render 15 items initially (visible screen)
  maxToRenderPerBatch={10}          // Render 10 items per scroll batch
  windowSize={5}                    // Keep 5 screens worth of items in memory
  removeClippedSubviews={true}      // Unmount items that scroll off screen (Android)
  getItemLayout={(_, index) => ({   // Skip measurement if items are fixed height
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  updateCellsBatchingPeriod={50}    // Batch state updates every 50ms
/>
```

### `getItemLayout`: The Biggest Win

If every card is the same height, tell `FlatList` upfront. It skips measuring each item:

```tsx
const ITEM_HEIGHT = 120; // card height + margins
const ITEM_SEPARATOR = 12;

<FlatList
  getItemLayout={(_, index) => ({
    length: ITEM_HEIGHT + ITEM_SEPARATOR,
    offset: (ITEM_HEIGHT + ITEM_SEPARATOR) * index,
    index,
  })}
/>
```

This alone can double scroll performance for large lists.

## Problem 3: Heavy Computations on the JS Thread

The stats bar recalculates counts on every render:

```tsx
// ❌ Recalculates on every render
const counts = jobs.reduce((acc, job) => { ... }, {});

// ✅ Only recalculates when jobs change
import { useMemo } from "react";

const counts = useMemo(
  () => jobs.reduce((acc, job) => {
    acc[job.status] = (acc[job.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>),
  [jobs]
);
```

## Problem 4: Image and Asset Optimization

If job cards had icons or thumbnails:

```tsx
// ❌ Loads full-size image, no caching
<Image source={{ uri: job.thumbnailUrl }} />

// ✅ Cached, resized, progressive loading
import FastImage from "react-native-fast-image";

<FastImage
  source={{ uri: job.thumbnailUrl, priority: FastImage.priority.normal }}
  style={styles.thumbnail}
  resizeMode={FastImage.resizeMode.cover}
/>
```

```bash
npm install react-native-fast-image
```

## Problem 5: Hermes Engine

Hermes is React Native's optimized JavaScript engine. It compiles JS to bytecode ahead of time, reducing startup time and memory usage.

Check if Hermes is enabled:

```tsx
// In your app:
const isHermes = () => !!(global as any).HermesInternal;
console.log("Hermes enabled:", isHermes());
```

With Expo SDK 49+, Hermes is enabled by default. If not:

```json
// app.json
{
  "expo": {
    "jsEngine": "hermes"
  }
}
```

Hermes benefits:
- **50% faster startup** — bytecode loads faster than parsing JS
- **30% less memory** — optimized garbage collector
- **Better profiling** — Chrome DevTools protocol support

## Problem 6: Pagination

Don't fetch 10,000 jobs at once. Use cursor-based pagination:

```tsx
// src/hooks/useInfiniteJobs.ts
import { useInfiniteQuery } from "@tanstack/react-query";
import { API_URL } from "../services/config";
import type { Job } from "../types";

interface JobsPage {
  jobs: Job[];
  nextCursor: string | null;
}

export function useInfiniteJobs() {
  return useInfiniteQuery({
    queryKey: ["jobs", "infinite"],
    queryFn: async ({ pageParam }): Promise<JobsPage> => {
      const url = pageParam
        ? `${API_URL}/jobs?cursor=${pageParam}&limit=20`
        : `${API_URL}/jobs?limit=20`;
      const res = await fetch(url);
      return res.json();
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}
```

```tsx
// src/screens/JobListScreen.tsx — with infinite scroll
export function JobListScreen() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useInfiniteJobs();

  const jobs = data?.pages.flatMap((page) => page.jobs) ?? [];

  return (
    <FlatList
      data={jobs}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <JobCard job={item} onPress={handlePress} />}
      onEndReached={() => {
        if (hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      }}
      onEndReachedThreshold={0.5}
      ListFooterComponent={
        isFetchingNextPage ? (
          <ActivityIndicator style={{ padding: 16 }} color="#3b82f6" />
        ) : null
      }
    />
  );
}
```

## Problem 7: Avoid Anonymous Functions in renderItem

```tsx
// ❌ Creates a new function every render for every item
renderItem={({ item }) => <JobCard job={item} onPress={(id) => navigate(id)} />}

// ✅ Extract to a stable function
const renderItem = useCallback(
  ({ item }: { item: Job }) => <JobCard job={item} onPress={handlePress} />,
  [handlePress]
);

<FlatList renderItem={renderItem} />
```

## The Performance Checklist

| Issue | Fix | Impact |
|---|---|---|
| All cards re-render on any change | `React.memo` with custom comparator | High |
| New function refs break memo | `useCallback` for handlers | High |
| FlatList measures every item | `getItemLayout` | High |
| Too many items in memory | `windowSize`, `removeClippedSubviews` | Medium |
| Heavy computations every render | `useMemo` | Medium |
| Loading all data at once | Infinite scroll pagination | High |
| Slow JS engine | Hermes (enabled by default) | High |
| Large images | `react-native-fast-image` | Medium |
| Startup time | Lazy loading screens | Medium |

## Lazy Loading Screens

Don't load the Pipeline screen until the user taps the tab:

```tsx
import { lazy, Suspense } from "react";
import { ActivityIndicator } from "react-native";

const PipelineScreen = lazy(() => import("../screens/PipelineScreen"));

function LazyPipeline() {
  return (
    <Suspense fallback={<ActivityIndicator size="large" color="#3b82f6" />}>
      <PipelineScreen />
    </Suspense>
  );
}
```

## Verify

Before and after metrics (measured with Flipper on a Pixel 7):

| Metric | Before | After |
|---|---|---|
| List scroll FPS | 38-45 | 58-60 |
| Initial render (1000 jobs) | 1200ms | 180ms |
| Memory (10,000 jobs loaded) | 340MB | 95MB |
| Time to interactive | 2.8s | 1.1s |

Karen scrolls through 500 jobs. Smooth as butter. No stutter. No warmth from the phone. She flicks fast — the list keeps up.

"Nice. But I want to swipe a job to cancel it. Like deleting an email."

Gestures. Chapter 6.

---

[← Chapter 4: Real-time & Push](chapter-04-realtime-push.md) | [Chapter 6: Gestures & Animations →](chapter-06-gestures-animations.md)
