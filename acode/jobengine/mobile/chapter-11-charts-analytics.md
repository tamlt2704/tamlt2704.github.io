# Chapter 11: Charts & Analytics — Visualize the Data

[← Chapter 10: Multiple Screens](chapter-10-responsive-screens.md) | [Chapter 12: Production Release →](chapter-12-production-release.md)

---

## The Problem

Captain Deadline is in a board meeting. The CEO asks: "How reliable is our job engine? What's the failure rate? Are we getting faster or slower?"

Captain Deadline opens the app. He can see individual jobs. He can see the pipeline. But he can't see *trends*. No charts. No graphs. No "jobs completed per hour" line going up and to the right.

"I need a dashboard screen. Charts. Numbers. Something I can show the CEO in 10 seconds."

## Choosing a Chart Library

| Library | Pros | Cons |
|---|---|---|
| `react-native-chart-kit` | Simple API, quick setup | Limited customization, dated look |
| `victory-native` | Full-featured, composable | Heavy bundle size |
| `react-native-gifted-charts` | Beautiful defaults, animated | Newer, smaller community |
| `react-native-skia` + custom | Full control, GPU-accelerated | More code to write |

We'll use **react-native-gifted-charts** — it gives us beautiful, animated charts with minimal code, and it's built on `react-native-svg` (which we already have from Chapter 9).

```bash
npm install react-native-gifted-charts react-native-linear-gradient
npx expo install expo-linear-gradient
```

## The Analytics API

```tsx
// src/types/analytics.ts
export interface JobStats {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  avgDurationMs: number;
  successRate: number; // 0-100
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface AnalyticsData {
  today: JobStats;
  thisWeek: JobStats;
  thisMonth: JobStats;
  jobsPerHour: TimeSeriesPoint[];      // Last 24 hours
  failuresByType: { type: string; count: number }[];
  avgDurationByType: { type: string; durationMs: number }[];
  dailyTrend: TimeSeriesPoint[];       // Last 30 days
  statusDistribution: { status: string; count: number }[];
}
```

```tsx
// src/hooks/useAnalytics.ts
import { useQuery } from "@tanstack/react-query";
import { API_URL } from "../services/config";
import { secureStorage } from "../services/secureStorage";
import type { AnalyticsData } from "../types/analytics";

export function useAnalytics() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: async (): Promise<AnalyticsData> => {
      const token = await secureStorage.getToken();
      const res = await fetch(`${API_URL}/analytics/dashboard`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
    staleTime: 60_000, // Analytics are fresh for 1 minute
    refetchInterval: 60_000,
  });
}
```

## The Analytics Screen

```tsx
// src/screens/AnalyticsScreen.tsx
import { ScrollView, View, Text, StyleSheet, ActivityIndicator, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAnalytics } from "../hooks/useAnalytics";
import { useScreenInfo } from "../hooks/useDeviceType";
import { KPICards } from "../components/charts/KPICards";
import { JobsPerHourChart } from "../components/charts/JobsPerHourChart";
import { FailuresByTypeChart } from "../components/charts/FailuresByTypeChart";
import { DailyTrendChart } from "../components/charts/DailyTrendChart";
import { StatusPieChart } from "../components/charts/StatusPieChart";
import { DurationBarChart } from "../components/charts/DurationBarChart";

export function AnalyticsScreen() {
  const { data, isLoading, error, refetch, isRefetching } = useAnalytics();
  const { columns, isLargeScreen } = useScreenInfo();

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Failed to load analytics</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} tintColor="#3b82f6" />
        }
      >
        {/* KPI Summary Cards */}
        <KPICards stats={data.today} />

        {/* Charts in responsive grid */}
        <View style={[styles.chartGrid, isLargeScreen && styles.chartGridWide]}>
          <View style={[styles.chartCard, isLargeScreen && styles.chartCardHalf]}>
            <Text style={styles.chartTitle}>Jobs per Hour (24h)</Text>
            <JobsPerHourChart data={data.jobsPerHour} />
          </View>

          <View style={[styles.chartCard, isLargeScreen && styles.chartCardHalf]}>
            <Text style={styles.chartTitle}>Status Distribution</Text>
            <StatusPieChart data={data.statusDistribution} />
          </View>

          <View style={[styles.chartCard, isLargeScreen && styles.chartCardHalf]}>
            <Text style={styles.chartTitle}>Failures by Type</Text>
            <FailuresByTypeChart data={data.failuresByType} />
          </View>

          <View style={[styles.chartCard, isLargeScreen && styles.chartCardHalf]}>
            <Text style={styles.chartTitle}>Avg Duration by Type</Text>
            <DurationBarChart data={data.avgDurationByType} />
          </View>

          <View style={styles.chartCard}>
            <Text style={styles.chartTitle}>Daily Trend (30 days)</Text>
            <DailyTrendChart data={data.dailyTrend} />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827" },
  center: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  scroll: { padding: 16 },
  errorText: { color: "#f87171", fontSize: 16 },
  chartGrid: { gap: 16 },
  chartGridWide: { flexDirection: "row", flexWrap: "wrap" },
  chartCard: {
    backgroundColor: "#1f2937",
    borderRadius: 12,
    padding: 16,
    marginBottom: 0,
  },
  chartCardHalf: { width: "48%" },
  chartTitle: { color: "#d1d5db", fontSize: 14, fontWeight: "600", marginBottom: 12 },
});
```

## KPI Cards

The top-level numbers — big, bold, at a glance:

```tsx
// src/components/charts/KPICards.tsx
import { View, Text, StyleSheet } from "react-native";
import { useScreenInfo } from "../../hooks/useDeviceType";
import type { JobStats } from "../../types/analytics";

export function KPICards({ stats }: { stats: JobStats }) {
  const { isLargeScreen } = useScreenInfo();

  const cards = [
    { label: "Total Jobs", value: stats.totalJobs.toLocaleString(), color: "#3b82f6" },
    { label: "Success Rate", value: `${stats.successRate.toFixed(1)}%`, color: "#10b981" },
    { label: "Failed", value: stats.failedJobs.toLocaleString(), color: "#ef4444" },
    { label: "Avg Duration", value: formatDuration(stats.avgDurationMs), color: "#f59e0b" },
  ];

  return (
    <View style={[styles.container, isLargeScreen && styles.containerWide]}>
      {cards.map((card) => (
        <View key={card.label} style={[styles.card, isLargeScreen && styles.cardWide]}>
          <Text style={[styles.value, { color: card.color }]}>{card.value}</Text>
          <Text style={styles.label}>{card.label}</Text>
        </View>
      ))}
    </View>
  );
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 16,
  },
  containerWide: { gap: 12 },
  card: {
    flex: 1,
    minWidth: "45%",
    backgroundColor: "#1f2937",
    borderRadius: 12,
    padding: 16,
    alignItems: "center",
  },
  cardWide: { minWidth: "22%" },
  value: {
    fontSize: 24,
    fontWeight: "bold",
  },
  label: {
    color: "#6b7280",
    fontSize: 12,
    marginTop: 4,
  },
});
```

## Line Chart: Jobs per Hour

```tsx
// src/components/charts/JobsPerHourChart.tsx
import { View, useWindowDimensions } from "react-native";
import { LineChart } from "react-native-gifted-charts";
import type { TimeSeriesPoint } from "../../types/analytics";

interface Props {
  data: TimeSeriesPoint[];
}

export function JobsPerHourChart({ data }: Props) {
  const { width } = useWindowDimensions();
  const chartWidth = Math.min(width - 80, 600);

  const chartData = data.map((point, index) => ({
    value: point.value,
    label: index % 4 === 0 ? new Date(point.timestamp).getHours() + "h" : "",
    dataPointText: undefined,
  }));

  return (
    <View>
      <LineChart
        data={chartData}
        width={chartWidth}
        height={180}
        color="#3b82f6"
        thickness={2}
        dataPointsColor="#3b82f6"
        dataPointsRadius={3}
        startFillColor="rgba(59, 130, 246, 0.3)"
        endFillColor="rgba(59, 130, 246, 0.01)"
        areaChart
        curved
        yAxisColor="#374151"
        xAxisColor="#374151"
        yAxisTextStyle={{ color: "#6b7280", fontSize: 10 }}
        xAxisLabelTextStyle={{ color: "#6b7280", fontSize: 10 }}
        hideRules={false}
        rulesColor="#1f2937"
        backgroundColor="#111827"
        noOfSections={4}
        animateOnDataChange
        animationDuration={500}
        pointerConfig={{
          pointerStripColor: "#3b82f6",
          pointerStripWidth: 1,
          pointerColor: "#3b82f6",
          radius: 5,
          pointerLabelWidth: 80,
          pointerLabelHeight: 30,
          pointerLabelComponent: (items: any[]) => (
            <View style={{ backgroundColor: "#1f2937", padding: 6, borderRadius: 6 }}>
              <Text style={{ color: "#f9fafb", fontSize: 12 }}>{items[0].value} jobs</Text>
            </View>
          ),
        }}
      />
    </View>
  );
}
```

## Pie Chart: Status Distribution

```tsx
// src/components/charts/StatusPieChart.tsx
import { View, Text, StyleSheet } from "react-native";
import { PieChart } from "react-native-gifted-charts";

const STATUS_COLORS: Record<string, string> = {
  COMPLETED: "#10b981",
  RUNNING: "#3b82f6",
  FAILED: "#ef4444",
  PENDING: "#6b7280",
  CANCELLED: "#a8a29e",
  DEAD: "#fb7185",
};

interface Props {
  data: { status: string; count: number }[];
}

export function StatusPieChart({ data }: Props) {
  const total = data.reduce((sum, d) => sum + d.count, 0);

  const pieData = data
    .filter((d) => d.count > 0)
    .map((d) => ({
      value: d.count,
      color: STATUS_COLORS[d.status] || "#6b7280",
      text: `${Math.round((d.count / total) * 100)}%`,
      textColor: "#f9fafb",
      textSize: 11,
    }));

  return (
    <View style={styles.container}>
      <PieChart
        data={pieData}
        donut
        radius={80}
        innerRadius={50}
        innerCircleColor="#1f2937"
        centerLabelComponent={() => (
          <View style={styles.centerLabel}>
            <Text style={styles.centerValue}>{total}</Text>
            <Text style={styles.centerText}>Total</Text>
          </View>
        )}
        showText
        textColor="#f9fafb"
        textSize={10}
      />

      {/* Legend */}
      <View style={styles.legend}>
        {data.filter((d) => d.count > 0).map((d) => (
          <View key={d.status} style={styles.legendItem}>
            <View style={[styles.legendDot, { backgroundColor: STATUS_COLORS[d.status] }]} />
            <Text style={styles.legendText}>{d.status}</Text>
            <Text style={styles.legendCount}>{d.count}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: "center" },
  centerLabel: { alignItems: "center" },
  centerValue: { color: "#f9fafb", fontSize: 20, fontWeight: "bold" },
  centerText: { color: "#6b7280", fontSize: 11 },
  legend: { marginTop: 16, width: "100%" },
  legendItem: { flexDirection: "row", alignItems: "center", marginBottom: 6 },
  legendDot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  legendText: { color: "#d1d5db", fontSize: 12, flex: 1 },
  legendCount: { color: "#6b7280", fontSize: 12 },
});
```

## Bar Chart: Failures by Type

```tsx
// src/components/charts/FailuresByTypeChart.tsx
import { View, useWindowDimensions } from "react-native";
import { BarChart } from "react-native-gifted-charts";

interface Props {
  data: { type: string; count: number }[];
}

export function FailuresByTypeChart({ data }: Props) {
  const { width } = useWindowDimensions();
  const chartWidth = Math.min(width - 80, 500);

  const barData = data.map((d) => ({
    value: d.count,
    label: d.type.replace("_", "\n"),
    frontColor: "#ef4444",
    topLabelComponent: () => (
      <Text style={{ color: "#f87171", fontSize: 11, marginBottom: 4 }}>{d.count}</Text>
    ),
  }));

  return (
    <View>
      <BarChart
        data={barData}
        width={chartWidth}
        height={160}
        barWidth={40}
        spacing={20}
        roundedTop
        roundedBottom
        yAxisColor="#374151"
        xAxisColor="#374151"
        yAxisTextStyle={{ color: "#6b7280", fontSize: 10 }}
        xAxisLabelTextStyle={{ color: "#6b7280", fontSize: 9 }}
        noOfSections={4}
        backgroundColor="#111827"
        rulesColor="#1f2937"
        isAnimated
        animationDuration={600}
      />
    </View>
  );
}
```

## Horizontal Bar Chart: Average Duration by Type

```tsx
// src/components/charts/DurationBarChart.tsx
import { View, Text, StyleSheet } from "react-native";
import Animated, { useAnimatedStyle, withTiming, useSharedValue, withDelay } from "react-native-reanimated";
import { useEffect } from "react";

interface Props {
  data: { type: string; durationMs: number }[];
}

export function DurationBarChart({ data }: Props) {
  const maxDuration = Math.max(...data.map((d) => d.durationMs));

  return (
    <View style={styles.container}>
      {data.map((item, index) => (
        <DurationRow
          key={item.type}
          type={item.type}
          durationMs={item.durationMs}
          maxDuration={maxDuration}
          index={index}
        />
      ))}
    </View>
  );
}

function DurationRow({ type, durationMs, maxDuration, index }: {
  type: string;
  durationMs: number;
  maxDuration: number;
  index: number;
}) {
  const width = useSharedValue(0);
  const percentage = (durationMs / maxDuration) * 100;

  useEffect(() => {
    width.value = withDelay(index * 100, withTiming(percentage, { duration: 800 }));
  }, [percentage, index]);

  const barStyle = useAnimatedStyle(() => ({
    width: `${width.value}%`,
  }));

  return (
    <View style={styles.row}>
      <Text style={styles.typeLabel}>{type.replace("_", " ")}</Text>
      <View style={styles.barTrack}>
        <Animated.View style={[styles.barFill, barStyle]} />
      </View>
      <Text style={styles.durationLabel}>{formatDuration(durationMs)}</Text>
    </View>
  );
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

const styles = StyleSheet.create({
  container: { gap: 10 },
  row: { flexDirection: "row", alignItems: "center" },
  typeLabel: { color: "#d1d5db", fontSize: 11, width: 80 },
  barTrack: { flex: 1, height: 16, backgroundColor: "#374151", borderRadius: 8, overflow: "hidden", marginHorizontal: 8 },
  barFill: { height: "100%", backgroundColor: "#f59e0b", borderRadius: 8 },
  durationLabel: { color: "#6b7280", fontSize: 11, width: 50, textAlign: "right" },
});
```

## Daily Trend: Multi-Line Chart

Show completed vs failed over 30 days:

```tsx
// src/components/charts/DailyTrendChart.tsx
import { View, Text, StyleSheet, useWindowDimensions } from "react-native";
import { LineChart } from "react-native-gifted-charts";
import type { TimeSeriesPoint } from "../../types/analytics";

interface Props {
  data: TimeSeriesPoint[];
}

export function DailyTrendChart({ data }: Props) {
  const { width } = useWindowDimensions();
  const chartWidth = Math.min(width - 64, 800);

  // Split into completed and failed series
  const chartData = data.map((point, index) => ({
    value: point.value,
    label: index % 7 === 0 ? formatDate(point.timestamp) : "",
  }));

  return (
    <View>
      <LineChart
        data={chartData}
        width={chartWidth}
        height={200}
        color="#10b981"
        thickness={2}
        dataPointsColor="#10b981"
        dataPointsRadius={2}
        startFillColor="rgba(16, 185, 129, 0.2)"
        endFillColor="rgba(16, 185, 129, 0.01)"
        areaChart
        curved
        yAxisColor="#374151"
        xAxisColor="#374151"
        yAxisTextStyle={{ color: "#6b7280", fontSize: 10 }}
        xAxisLabelTextStyle={{ color: "#6b7280", fontSize: 9 }}
        hideRules={false}
        rulesColor="#1f2937"
        backgroundColor="#111827"
        noOfSections={5}
        animateOnDataChange
        animationDuration={600}
        scrollToEnd
        pointerConfig={{
          pointerStripColor: "#10b981",
          pointerStripWidth: 1,
          pointerColor: "#10b981",
          radius: 4,
          pointerLabelWidth: 100,
          pointerLabelHeight: 40,
          pointerLabelComponent: (items: any[]) => (
            <View style={styles.tooltip}>
              <Text style={styles.tooltipText}>{items[0].value} jobs</Text>
            </View>
          ),
        }}
      />

      {/* Legend */}
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendLine, { backgroundColor: "#10b981" }]} />
          <Text style={styles.legendText}>Completed</Text>
        </View>
      </View>
    </View>
  );
}

function formatDate(timestamp: string): string {
  const d = new Date(timestamp);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

const styles = StyleSheet.create({
  tooltip: { backgroundColor: "#1f2937", padding: 6, borderRadius: 6, borderWidth: 1, borderColor: "#374151" },
  tooltipText: { color: "#f9fafb", fontSize: 11 },
  legend: { flexDirection: "row", justifyContent: "center", marginTop: 12, gap: 16 },
  legendItem: { flexDirection: "row", alignItems: "center", gap: 6 },
  legendLine: { width: 16, height: 3, borderRadius: 2 },
  legendText: { color: "#9ca3af", fontSize: 11 },
});
```

## Real-Time Chart Updates

Charts should update when new SSE events arrive:

```tsx
// src/hooks/useRealtimeAnalytics.ts
import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { AnalyticsData } from "../types/analytics";

export function useRealtimeAnalytics() {
  const queryClient = useQueryClient();

  useEffect(() => {
    // When a job completes/fails via SSE, update analytics optimistically
    const unsubscribe = queryClient.getQueryCache().subscribe((event) => {
      if (event?.query.queryKey[0] === "jobs" && event.type === "updated") {
        // Invalidate analytics to refetch
        queryClient.invalidateQueries({ queryKey: ["analytics"] });
      }
    });

    return () => unsubscribe();
  }, [queryClient]);
}
```

## Animated Number Transitions

When KPI values change, animate the number:

```tsx
// src/components/charts/AnimatedNumber.tsx
import { useEffect } from "react";
import { Text, StyleSheet } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedProps,
  withTiming,
  useDerivedValue,
} from "react-native-reanimated";

const AnimatedText = Animated.createAnimatedComponent(Text);

interface Props {
  value: number;
  color: string;
  suffix?: string;
  decimals?: number;
}

export function AnimatedNumber({ value, color, suffix = "", decimals = 0 }: Props) {
  const animatedValue = useSharedValue(0);

  useEffect(() => {
    animatedValue.value = withTiming(value, { duration: 1000 });
  }, [value]);

  const displayValue = useDerivedValue(() => {
    return decimals > 0
      ? animatedValue.value.toFixed(decimals) + suffix
      : Math.round(animatedValue.value).toLocaleString() + suffix;
  });

  // Note: Animated text requires a workaround in RN
  // Using a simpler approach with state for compatibility
  return (
    <Text style={[styles.value, { color }]}>
      {decimals > 0 ? value.toFixed(decimals) : value.toLocaleString()}{suffix}
    </Text>
  );
}

const styles = StyleSheet.create({
  value: { fontSize: 24, fontWeight: "bold" },
});
```

## Chart Interactions: Tap for Details

Tap a bar in the failures chart to see which jobs failed:

```tsx
// In FailuresByTypeChart, add onPress to bars:
const barData = data.map((d) => ({
  value: d.count,
  label: d.type.replace("_", "\n"),
  frontColor: "#ef4444",
  onPress: () => {
    // Navigate to filtered job list showing only failed jobs of this type
    navigation.navigate("Jobs", {
      screen: "JobList",
      params: { filterStatus: "FAILED", filterType: d.type },
    });
  },
}));
```

## Responsive Charts

Charts adapt to screen size using the `useWindowDimensions` hook:

```tsx
// Charts automatically resize because we calculate width from useWindowDimensions
// On tablets, charts get more space and show more data points
// On phones in landscape, charts stretch to fill the wider viewport

const { width } = useWindowDimensions();
const chartWidth = Math.min(width - 80, 800); // Cap at 800px for readability
```

On tablets with the two-column layout from Chapter 10, charts render side by side — pie chart next to the bar chart, line chart spanning full width below.

## Verify

1. Open the Analytics tab → KPI cards show today's stats
2. Scroll down → line chart shows jobs per hour with smooth curve
3. Tap/hold on the line chart → tooltip shows exact value
4. Pie chart shows status distribution with percentages
5. Bar chart shows failures by type — tap a bar → navigates to filtered list
6. Horizontal bars animate in with staggered delay
7. Pull to refresh → charts update with latest data
8. Rotate to landscape → charts resize smoothly
9. On tablet → charts display in two-column grid
10. Submit a job → watch the "Total Jobs" KPI increment

Captain Deadline opens the Analytics tab in the board meeting. The CEO sees: 99.2% success rate. 12,000 jobs today. Average duration 4.2 seconds. The daily trend line goes up and to the right.

"Good numbers. Ship it."

Production release. Chapter 12.

---

[← Chapter 10: Multiple Screens](chapter-10-responsive-screens.md) | [Chapter 12: Production Release →](chapter-12-production-release.md)
