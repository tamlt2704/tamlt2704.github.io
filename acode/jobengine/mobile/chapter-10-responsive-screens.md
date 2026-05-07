# Chapter 10: Multiple Screens & Responsive Layouts — Phone, Tablet, Foldable

[← Chapter 9: DAG Visualization](chapter-09-dag-visualization.md) | [Chapter 11: Charts & Analytics →](chapter-11-charts-analytics.md)

---

## The Problem

Mrs. Jira buys the team iPads for "mobile war rooms." She opens the app on a 12.9-inch iPad Pro in landscape. The job cards are tiny, centered in a sea of empty space. The bottom tabs look ridiculous — designed for a thumb, now stretched across 12 inches.

Captain Deadline has a Samsung Galaxy Z Fold5. He unfolds it during a meeting — the app doesn't adapt. Same phone layout, just bigger. "This is a tablet now. Show me more."

The app works on one screen size. It needs to work on all of them:
- **Phone portrait** (375–430px) — single column, bottom tabs
- **Phone landscape** (667–932px) — two columns, compact header
- **Tablet portrait** (768–834px) — sidebar navigation, two-column grid
- **Tablet landscape** (1024–1366px) — three-column master-detail, persistent sidebar
- **Foldable** — adapts when the screen unfolds mid-use

## Detecting Screen Size

```tsx
// src/hooks/useDeviceType.ts
import { useWindowDimensions } from "react-native";

export type DeviceType = "phone" | "tablet";
export type Orientation = "portrait" | "landscape";

interface ScreenInfo {
  device: DeviceType;
  orientation: Orientation;
  width: number;
  height: number;
  columns: number; // Recommended grid columns
  isLargeScreen: boolean;
}

export function useScreenInfo(): ScreenInfo {
  const { width, height } = useWindowDimensions();

  const orientation: Orientation = width > height ? "landscape" : "portrait";
  const shortSide = Math.min(width, height);
  const device: DeviceType = shortSide >= 600 ? "tablet" : "phone";
  const isLargeScreen = width >= 768;

  let columns = 1;
  if (width >= 1024) columns = 3;
  else if (width >= 768) columns = 2;
  else if (width >= 600 && orientation === "landscape") columns = 2;

  return { device, orientation, width, height, columns, isLargeScreen };
}
```

`useWindowDimensions` updates in real time — when the user rotates the device or unfolds a foldable, the layout recalculates instantly.

## Adaptive Navigation: Tabs vs Sidebar

On phones, bottom tabs. On tablets, a persistent sidebar:

```tsx
// src/navigation/AdaptiveNavigator.tsx
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createDrawerNavigator } from "@react-navigation/drawer";
import { useScreenInfo } from "../hooks/useDeviceType";
import { JobStackNavigator } from "./JobStackNavigator";
import { SubmitJobScreen } from "../screens/SubmitJobScreen";
import { PipelineScreen } from "../screens/PipelineScreen";
import { AnalyticsScreen } from "../screens/AnalyticsScreen";
import { Ionicons } from "@expo/vector-icons";

const Tab = createBottomTabNavigator();
const Drawer = createDrawerNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color, size }) => {
          const icons: Record<string, keyof typeof Ionicons.glyphMap> = {
            Jobs: "list-outline",
            Submit: "add-circle-outline",
            Pipeline: "git-network-outline",
            Analytics: "bar-chart-outline",
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: "#3b82f6",
        tabBarInactiveTintColor: "#6b7280",
        tabBarStyle: { backgroundColor: "#1f2937", borderTopColor: "#374151" },
        headerShown: false,
      })}
    >
      <Tab.Screen name="Jobs" component={JobStackNavigator} />
      <Tab.Screen name="Submit" component={SubmitJobScreen} />
      <Tab.Screen name="Pipeline" component={PipelineScreen} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} />
    </Tab.Navigator>
  );
}

function DrawerNavigator() {
  return (
    <Drawer.Navigator
      screenOptions={{
        drawerType: "permanent",
        drawerStyle: { backgroundColor: "#1f2937", width: 240 },
        drawerActiveTintColor: "#3b82f6",
        drawerInactiveTintColor: "#9ca3af",
        headerStyle: { backgroundColor: "#111827" },
        headerTintColor: "#f9fafb",
        sceneContainerStyle: { backgroundColor: "#111827" },
      }}
    >
      <Drawer.Screen
        name="Jobs"
        component={JobStackNavigator}
        options={{ drawerIcon: ({ color, size }) => <Ionicons name="list-outline" size={size} color={color} /> }}
      />
      <Drawer.Screen
        name="Submit"
        component={SubmitJobScreen}
        options={{ drawerIcon: ({ color, size }) => <Ionicons name="add-circle-outline" size={size} color={color} /> }}
      />
      <Drawer.Screen
        name="Pipeline"
        component={PipelineScreen}
        options={{ drawerIcon: ({ color, size }) => <Ionicons name="git-network-outline" size={size} color={color} /> }}
      />
      <Drawer.Screen
        name="Analytics"
        component={AnalyticsScreen}
        options={{ drawerIcon: ({ color, size }) => <Ionicons name="bar-chart-outline" size={size} color={color} /> }}
      />
    </Drawer.Navigator>
  );
}

export function AdaptiveNavigator() {
  const { isLargeScreen } = useScreenInfo();

  return isLargeScreen ? <DrawerNavigator /> : <TabNavigator />;
}
```

Install the drawer:

```bash
npm install @react-navigation/drawer react-native-gesture-handler
```

## Responsive Grid Layout

The job list should show more columns on wider screens:

```tsx
// src/components/ResponsiveJobGrid.tsx
import { FlatList, StyleSheet, useWindowDimensions } from "react-native";
import { useCallback } from "react";
import { JobCard } from "./JobCard";
import { useScreenInfo } from "../hooks/useDeviceType";
import type { Job } from "../types";

interface Props {
  jobs: Job[];
  onJobPress: (id: string) => void;
}

export function ResponsiveJobGrid({ jobs, onJobPress }: Props) {
  const { columns } = useScreenInfo();
  const { width } = useWindowDimensions();

  const cardWidth = (width - 16 * (columns + 1)) / columns;

  const renderItem = useCallback(
    ({ item }: { item: Job }) => (
      <JobCard job={item} onPress={onJobPress} style={{ width: cardWidth }} />
    ),
    [onJobPress, cardWidth]
  );

  return (
    <FlatList
      data={jobs}
      keyExtractor={(item) => item.id}
      renderItem={renderItem}
      numColumns={columns}
      key={`grid-${columns}`} // Force re-mount when columns change
      columnWrapperStyle={columns > 1 ? styles.row : undefined}
      contentContainerStyle={styles.container}
    />
  );
}

const styles = StyleSheet.create({
  container: { padding: 8 },
  row: { gap: 8, paddingHorizontal: 8 },
});
```

Note the `key={`grid-${columns}`}` — `FlatList` doesn't support dynamic `numColumns`, so we force a re-mount when the column count changes (e.g., rotation).

## Master-Detail on Tablets

On tablets in landscape, show the job list and detail side by side:

```tsx
// src/screens/JobMasterDetail.tsx
import { View, StyleSheet } from "react-native";
import { useState } from "react";
import { useScreenInfo } from "../hooks/useDeviceType";
import { JobListPanel } from "../components/JobListPanel";
import { JobDetailPanel } from "../components/JobDetailPanel";

export function JobMasterDetail() {
  const { isLargeScreen, orientation } = useScreenInfo();
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const showSplitView = isLargeScreen && orientation === "landscape";

  if (showSplitView) {
    return (
      <View style={styles.splitContainer}>
        <View style={styles.masterPanel}>
          <JobListPanel
            selectedId={selectedJobId}
            onSelect={setSelectedJobId}
          />
        </View>
        <View style={styles.detailPanel}>
          {selectedJobId ? (
            <JobDetailPanel jobId={selectedJobId} />
          ) : (
            <EmptyDetail />
          )}
        </View>
      </View>
    );
  }

  // Phone: standard stack navigation
  return <JobListPanel onSelect={setSelectedJobId} />;
}

function EmptyDetail() {
  return (
    <View style={styles.emptyDetail}>
      <Text style={styles.emptyText}>Select a job to view details</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  splitContainer: {
    flex: 1,
    flexDirection: "row",
  },
  masterPanel: {
    width: "40%",
    borderRightWidth: 1,
    borderRightColor: "#374151",
  },
  detailPanel: {
    flex: 1,
  },
  emptyDetail: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#111827",
  },
  emptyText: {
    color: "#6b7280",
    fontSize: 16,
  },
});
```

## Handling Orientation Changes

React to rotation with layout animations:

```tsx
// src/hooks/useOrientationChange.ts
import { useEffect, useRef } from "react";
import { useWindowDimensions } from "react-native";
import type { Orientation } from "./useDeviceType";

export function useOrientationChange(callback: (orientation: Orientation) => void) {
  const { width, height } = useWindowDimensions();
  const prevOrientation = useRef<Orientation>(width > height ? "landscape" : "portrait");

  useEffect(() => {
    const current: Orientation = width > height ? "landscape" : "portrait";
    if (current !== prevOrientation.current) {
      prevOrientation.current = current;
      callback(current);
    }
  }, [width, height, callback]);
}
```

## Foldable Device Support

Samsung Galaxy Z Fold and similar devices change screen size mid-session:

```tsx
// src/hooks/useFoldableState.ts
import { useEffect, useState } from "react";
import { useWindowDimensions } from "react-native";

interface FoldableState {
  isFolded: boolean;
  screenWidth: number;
  transitionInProgress: boolean;
}

export function useFoldableState(): FoldableState {
  const { width } = useWindowDimensions();
  const [prevWidth, setPrevWidth] = useState(width);
  const [transitionInProgress, setTransitionInProgress] = useState(false);

  useEffect(() => {
    // Detect large width changes (fold/unfold)
    const delta = Math.abs(width - prevWidth);
    if (delta > 200) {
      setTransitionInProgress(true);
      // Allow layout to settle
      const timer = setTimeout(() => setTransitionInProgress(false), 300);
      setPrevWidth(width);
      return () => clearTimeout(timer);
    }
    setPrevWidth(width);
  }, [width]);

  return {
    isFolded: width < 600,
    screenWidth: width,
    transitionInProgress,
  };
}
```

## Responsive Spacing & Typography

Scale spacing and font sizes based on screen width:

```tsx
// src/utils/responsive.ts
import { Dimensions, PixelRatio } from "react-native";

const { width: SCREEN_WIDTH } = Dimensions.get("window");

// Base design width (iPhone 14 Pro)
const BASE_WIDTH = 393;

/**
 * Scale a value proportionally to screen width.
 * On a 393px phone: scale(16) = 16
 * On a 768px tablet: scale(16) = 31
 * We cap the scaling to avoid absurdly large values.
 */
export function scale(size: number): number {
  const scaled = (SCREEN_WIDTH / BASE_WIDTH) * size;
  return Math.round(PixelRatio.roundToNearestPixel(Math.min(scaled, size * 1.5)));
}

/**
 * Moderate scale — less aggressive, good for fonts.
 * factor 0.5 means halfway between original and fully scaled.
 */
export function moderateScale(size: number, factor = 0.5): number {
  return Math.round(size + (scale(size) - size) * factor);
}
```

Usage:

```tsx
import { moderateScale } from "../utils/responsive";

const styles = StyleSheet.create({
  title: {
    fontSize: moderateScale(18),
    // Phone: 18, Tablet: ~22
  },
  card: {
    padding: moderateScale(16),
    borderRadius: moderateScale(12),
  },
});
```

## Landscape-Specific Layouts

Some screens need completely different layouts in landscape:

```tsx
// src/screens/SubmitJobScreen.tsx — landscape variant
import { useScreenInfo } from "../hooks/useDeviceType";

export function SubmitJobScreen() {
  const { orientation, isLargeScreen } = useScreenInfo();

  if (orientation === "landscape" || isLargeScreen) {
    return <SubmitJobWideLayout />;
  }

  return <SubmitJobNarrowLayout />;
}

function SubmitJobWideLayout() {
  // Two-column: form on left, preview on right
  return (
    <View style={styles.wideContainer}>
      <View style={styles.formColumn}>
        {/* Job type, priority, payload inputs */}
      </View>
      <View style={styles.previewColumn}>
        {/* Live preview of the job that will be submitted */}
      </View>
    </View>
  );
}

function SubmitJobNarrowLayout() {
  // Single column: scrollable form
  return (
    <ScrollView style={styles.narrowContainer}>
      {/* All inputs stacked vertically */}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wideContainer: { flex: 1, flexDirection: "row", backgroundColor: "#111827" },
  formColumn: { flex: 1, padding: 20, borderRightWidth: 1, borderRightColor: "#374151" },
  previewColumn: { flex: 1, padding: 20 },
  narrowContainer: { flex: 1, backgroundColor: "#111827" },
});
```

## iPad Multitasking (Split View / Slide Over)

iOS iPads support running two apps side by side. Your app might get 1/3, 1/2, or 2/3 of the screen:

```json
// app.json — enable iPad multitasking
{
  "expo": {
    "ios": {
      "supportsTablet": true,
      "requireFullScreen": false  // Allow Split View
    }
  }
}
```

With `useWindowDimensions`, your responsive hooks automatically handle this — the width changes just like a rotation.

## Breakpoint-Based Component Rendering

A utility for conditional rendering based on screen size:

```tsx
// src/components/Responsive.tsx
import { useScreenInfo } from "../hooks/useDeviceType";

interface Props {
  phone?: React.ReactNode;
  tablet?: React.ReactNode;
  landscape?: React.ReactNode;
  children?: React.ReactNode;
}

export function Responsive({ phone, tablet, landscape, children }: Props) {
  const { device, orientation } = useScreenInfo();

  if (landscape && orientation === "landscape") return <>{landscape}</>;
  if (tablet && device === "tablet") return <>{tablet}</>;
  if (phone && device === "phone") return <>{phone}</>;
  return <>{children}</>;
}
```

Usage:

```tsx
<Responsive
  phone={<CompactStatsBar jobs={jobs} />}
  tablet={<ExpandedStatsBar jobs={jobs} />}
/>
```

## Verify

1. **iPhone 15 Pro (portrait)** → single column, bottom tabs, compact cards
2. **iPhone 15 Pro (landscape)** → two columns, landscape header
3. **iPad Pro 12.9" (portrait)** → permanent sidebar, two-column grid
4. **iPad Pro 12.9" (landscape)** → sidebar + master-detail split view
5. **iPad Split View (1/3 width)** → falls back to phone layout
6. **Samsung Galaxy Z Fold (folded)** → phone layout
7. **Samsung Galaxy Z Fold (unfolded)** → tablet layout, smooth transition
8. **Rotate device mid-use** → layout animates to new configuration

Mrs. Jira opens the app on her iPad in landscape. The sidebar shows all sections. The job list takes 40% of the screen, the detail panel shows the selected job on the right. She taps through jobs without navigating away from the list.

Captain Deadline unfolds his Galaxy Z Fold. The app smoothly transitions from phone to tablet layout. Two columns of job cards appear. He nods.

"Now I want charts. Show me trends. How many jobs failed this week?"

Charts. Chapter 11.

---

[← Chapter 9: DAG Visualization](chapter-09-dag-visualization.md) | [Chapter 11: Charts & Analytics →](chapter-11-charts-analytics.md)
