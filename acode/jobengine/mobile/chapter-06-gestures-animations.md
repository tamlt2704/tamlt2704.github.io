# Chapter 6: Gestures & Animations — Swipe, Drag, Delight

[← Chapter 5: Performance](chapter-05-performance.md) | [Chapter 7: Offline & Persistence →](chapter-07-offline-persistence.md)

---

## The Problem

Karen wants to cancel a job by swiping left — like deleting an email in her mail app. Captain Deadline wants a "pull down to submit" gesture on the Submit tab. Old Greg wants the DAG nodes to be draggable.

The web dashboard has `onClick`. Mobile has an entire vocabulary of touch: tap, long press, swipe, pinch, pan, fling. And users expect 60fps animations during all of them.

Two libraries make this possible:
- **React Native Gesture Handler** — native-level touch recognition
- **React Native Reanimated** — animations that run on the UI thread (not JS thread)

```bash
npx expo install react-native-gesture-handler react-native-reanimated
```

Add the Reanimated plugin to `babel.config.js`:

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ["babel-preset-expo"],
    plugins: ["react-native-reanimated/plugin"], // Must be last
  };
};
```

## Why Not `Animated` from React Native?

The built-in `Animated` API runs on the JS thread. When JS is busy (processing SSE events, computing stats), animations stutter. Reanimated runs animations on the **UI thread** — completely independent of JavaScript. Even if your JS thread freezes, the animation stays at 60fps.

## Swipe-to-Cancel Job Card

```tsx
// src/components/SwipeableJobCard.tsx
import { useCallback } from "react";
import { View, Text, StyleSheet, Alert } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
  interpolate,
  Extrapolation,
} from "react-native-reanimated";
import { JobCard } from "./JobCard";
import { useCancelJob } from "../hooks/useJobMutations";
import type { Job } from "../types";

const SWIPE_THRESHOLD = -120;

interface Props {
  job: Job;
  onPress: (jobId: string) => void;
}

export function SwipeableJobCard({ job, onPress }: Props) {
  const translateX = useSharedValue(0);
  const cancelJob = useCancelJob();

  const confirmCancel = useCallback(() => {
    Alert.alert(
      "Cancel Job?",
      `Cancel ${job.type} #${job.id.slice(0, 8)}?`,
      [
        { text: "No", onPress: () => { translateX.value = withSpring(0); } },
        {
          text: "Cancel Job",
          style: "destructive",
          onPress: () => {
            translateX.value = withTiming(-400, { duration: 200 });
            cancelJob.mutate(job.id);
          },
        },
      ]
    );
  }, [job, cancelJob, translateX]);

  const panGesture = Gesture.Pan()
    .activeOffsetX([-10, 10])
    .onUpdate((event) => {
      // Only allow left swipe, and only for cancellable jobs
      if (event.translationX < 0 && (job.status === "PENDING" || job.status === "RUNNING")) {
        translateX.value = event.translationX;
      }
    })
    .onEnd((event) => {
      if (event.translationX < SWIPE_THRESHOLD) {
        runOnJS(confirmCancel)();
      } else {
        translateX.value = withSpring(0);
      }
    });

  const cardStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  const actionStyle = useAnimatedStyle(() => ({
    opacity: interpolate(
      translateX.value,
      [0, SWIPE_THRESHOLD],
      [0, 1],
      Extrapolation.CLAMP
    ),
  }));

  return (
    <View style={styles.container}>
      {/* Red background revealed on swipe */}
      <Animated.View style={[styles.actionContainer, actionStyle]}>
        <Text style={styles.actionText}>Cancel</Text>
        <Text style={styles.actionIcon}>✕</Text>
      </Animated.View>

      {/* The card itself */}
      <GestureDetector gesture={panGesture}>
        <Animated.View style={cardStyle}>
          <JobCard job={job} onPress={onPress} />
        </Animated.View>
      </GestureDetector>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "relative",
  },
  actionContainer: {
    position: "absolute",
    right: 16,
    top: 0,
    bottom: 0,
    width: 100,
    backgroundColor: "#dc2626",
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
    marginVertical: 6,
  },
  actionText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  actionIcon: {
    color: "#fff",
    fontSize: 24,
    marginTop: 4,
  },
});
```

## Long Press for Quick Actions

Long press a job card to show a context menu:

```tsx
// src/components/JobCardWithActions.tsx
import { useState, useCallback } from "react";
import { View, StyleSheet } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from "react-native-reanimated";
import * as Haptics from "expo-haptics";
import { ActionSheet } from "./ActionSheet";
import type { Job } from "../types";

export function JobCardWithActions({ job, onPress }: { job: Job; onPress: (id: string) => void }) {
  const [showActions, setShowActions] = useState(false);
  const scale = useSharedValue(1);

  const longPressGesture = Gesture.LongPress()
    .minDuration(500)
    .onStart(() => {
      scale.value = withSpring(0.95);
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    })
    .onEnd(() => {
      scale.value = withSpring(1);
      setShowActions(true);
    });

  const tapGesture = Gesture.Tap().onEnd(() => {
    onPress(job.id);
  });

  const composed = Gesture.Exclusive(longPressGesture, tapGesture);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <>
      <GestureDetector gesture={composed}>
        <Animated.View style={animatedStyle}>
          <JobCard job={job} onPress={() => {}} />
        </Animated.View>
      </GestureDetector>

      <ActionSheet
        visible={showActions}
        onClose={() => setShowActions(false)}
        job={job}
      />
    </>
  );
}
```

Install haptics:

```bash
npx expo install expo-haptics
```

## Animated Status Transitions

When a job status changes (via SSE), animate the badge color transition:

```tsx
// src/components/AnimatedStatusBadge.tsx
import { useEffect } from "react";
import { StyleSheet } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSequence,
  withTiming,
  withSpring,
} from "react-native-reanimated";
import type { JobStatus } from "../types";

const STATUS_COLORS: Record<JobStatus, string> = {
  PENDING: "#374151",
  RUNNING: "#1e3a5f",
  COMPLETED: "#064e3b",
  FAILED: "#7f1d1d",
  CANCELLED: "#44403c",
  DEAD: "#4c0519",
};

export function AnimatedStatusBadge({ status }: { status: JobStatus }) {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  useEffect(() => {
    // Pulse animation when status changes
    scale.value = withSequence(
      withSpring(1.2, { damping: 8 }),
      withSpring(1, { damping: 12 })
    );
    opacity.value = withSequence(
      withTiming(0.5, { duration: 100 }),
      withTiming(1, { duration: 200 })
    );
  }, [status]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <Animated.View style={[styles.badge, { backgroundColor: STATUS_COLORS[status] }, animatedStyle]}>
      <Animated.Text style={styles.text}>{status}</Animated.Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  text: { color: "#f9fafb", fontSize: 11, fontWeight: "700" },
});
```

## Pull-to-Submit (Fun Easter Egg)

On the Submit tab, pull down past a threshold to quick-submit a job:

```tsx
// src/components/PullToSubmit.tsx
import { View, Text, StyleSheet } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  runOnJS,
  interpolate,
} from "react-native-reanimated";

const SUBMIT_THRESHOLD = 150;

export function PullToSubmit({ onSubmit, children }: { onSubmit: () => void; children: React.ReactNode }) {
  const translateY = useSharedValue(0);

  const panGesture = Gesture.Pan()
    .onUpdate((e) => {
      if (e.translationY > 0) {
        translateY.value = e.translationY * 0.5; // Resistance
      }
    })
    .onEnd((e) => {
      if (e.translationY > SUBMIT_THRESHOLD) {
        runOnJS(onSubmit)();
      }
      translateY.value = withSpring(0);
    });

  const contentStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));

  const hintStyle = useAnimatedStyle(() => ({
    opacity: interpolate(translateY.value, [0, SUBMIT_THRESHOLD], [0, 1]),
    transform: [{ scale: interpolate(translateY.value, [0, SUBMIT_THRESHOLD], [0.5, 1]) }],
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <View style={styles.container}>
        <Animated.View style={[styles.hint, hintStyle]}>
          <Text style={styles.hintText}>Release to quick-submit</Text>
        </Animated.View>
        <Animated.View style={contentStyle}>{children}</Animated.View>
      </View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  hint: { position: "absolute", top: 20, alignSelf: "center" },
  hintText: { color: "#3b82f6", fontSize: 14, fontWeight: "600" },
});
```

## Shared Element Transitions

When tapping a job card to open the detail screen, animate the card expanding:

```tsx
// This requires react-native-reanimated 3 + React Navigation 7
// src/navigation/RootNavigator.tsx — add shared transitions
import { SharedTransition, withSpring } from "react-native-reanimated";

const customTransition = SharedTransition.custom((values) => {
  "worklet";
  return {
    width: withSpring(values.targetWidth),
    height: withSpring(values.targetHeight),
    originX: withSpring(values.targetOriginX),
    originY: withSpring(values.targetOriginY),
  };
});
```

## Verify

1. Swipe a PENDING job card left → red "Cancel" background reveals → release past threshold → confirmation dialog
2. Long press a card → haptic feedback + scale animation → action sheet appears
3. Watch a job transition from RUNNING to COMPLETED → badge pulses
4. Scroll the list → still 60fps with all animations active
5. All animations run on the UI thread — block JS with a heavy computation and animations still work

Karen swipes a job left. The red background slides in. She releases. "Cancel Job?" She taps yes. The card slides off screen. Satisfying.

"What happens when I'm on the subway with no signal?"

Offline mode. Chapter 7.

---

[← Chapter 5: Performance](chapter-05-performance.md) | [Chapter 7: Offline & Persistence →](chapter-07-offline-persistence.md)
