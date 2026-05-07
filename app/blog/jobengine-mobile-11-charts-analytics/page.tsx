import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Charts & Analytics: Visualize the Data"
            date="May 12, 2026"
            series="Job Engine Mobile"
            chapter={11}
            prevSlug="jobengine-mobile-10-responsive-screens"
            prevTitle="Multiple Screens"
            nextSlug="jobengine-mobile-12-production-release"
            nextTitle="Production Release"
        >
            <Section title="The Problem">
                <Paragraph>
                    Captain Deadline is in a board meeting. The CEO asks: &quot;How reliable is our job engine? What&apos;s the failure rate?&quot; He opens the app. He can see individual jobs. But he can&apos;t see trends. No charts. No &quot;jobs completed per hour&quot; line going up and to the right.
                </Paragraph>
            </Section>

            <Section title="Choosing a Chart Library">
                <Paragraph>
                    We use <code>react-native-gifted-charts</code> — beautiful animated charts with minimal code, built on react-native-svg.
                </Paragraph>
                <Code lang="bash">{`npm install react-native-gifted-charts react-native-linear-gradient`}</Code>
            </Section>

            <Section title="KPI Cards">
                <Paragraph>
                    Big numbers at a glance — total jobs, success rate, failures, average duration:
                </Paragraph>
                <Code lang="tsx" title="src/components/charts/KPICards.tsx">{`export function KPICards({ stats }: { stats: JobStats }) {
  const cards = [
    { label: "Total Jobs", value: stats.totalJobs.toLocaleString(), color: "#3b82f6" },
    { label: "Success Rate", value: \`\${stats.successRate.toFixed(1)}%\`, color: "#10b981" },
    { label: "Failed", value: stats.failedJobs.toLocaleString(), color: "#ef4444" },
    { label: "Avg Duration", value: formatDuration(stats.avgDurationMs), color: "#f59e0b" },
  ];

  return (
    <View style={styles.container}>
      {cards.map((card) => (
        <View key={card.label} style={styles.card}>
          <Text style={[styles.value, { color: card.color }]}>{card.value}</Text>
          <Text style={styles.label}>{card.label}</Text>
        </View>
      ))}
    </View>
  );
}`}</Code>
            </Section>

            <Section title="Line Chart: Jobs per Hour">
                <Code lang="tsx">{`import { LineChart } from "react-native-gifted-charts";

<LineChart
  data={chartData}
  width={chartWidth}
  height={180}
  color="#3b82f6"
  thickness={2}
  startFillColor="rgba(59, 130, 246, 0.3)"
  endFillColor="rgba(59, 130, 246, 0.01)"
  areaChart
  curved
  yAxisColor="#374151"
  xAxisColor="#374151"
  animateOnDataChange
  pointerConfig={{
    pointerStripColor: "#3b82f6",
    pointerLabelComponent: (items) => (
      <View style={styles.tooltip}>
        <Text>{items[0].value} jobs</Text>
      </View>
    ),
  }}
/>`}</Code>
                <Paragraph>
                    Touch and hold the chart to see a tooltip with the exact value at that point.
                </Paragraph>
            </Section>

            <Section title="Pie Chart: Status Distribution">
                <Code lang="tsx">{`import { PieChart } from "react-native-gifted-charts";

<PieChart
  data={pieData}
  donut
  radius={80}
  innerRadius={50}
  innerCircleColor="#1f2937"
  centerLabelComponent={() => (
    <View>
      <Text style={{ color: "#f9fafb", fontSize: 20, fontWeight: "bold" }}>{total}</Text>
      <Text style={{ color: "#6b7280", fontSize: 11 }}>Total</Text>
    </View>
  )}
/>`}</Code>
            </Section>

            <Section title="Bar Chart: Failures by Type">
                <Code lang="tsx">{`import { BarChart } from "react-native-gifted-charts";

const barData = data.map((d) => ({
  value: d.count,
  label: d.type.replace("_", "\\n"),
  frontColor: "#ef4444",
  onPress: () => navigation.navigate("Jobs", { filterStatus: "FAILED", filterType: d.type }),
}));

<BarChart data={barData} width={chartWidth} height={160}
  barWidth={40} roundedTop roundedBottom isAnimated />`}</Code>
                <Paragraph>
                    Tap a bar to navigate to a filtered job list showing only failed jobs of that type.
                </Paragraph>
            </Section>

            <Section title="Animated Horizontal Bars">
                <Paragraph>
                    Custom animated bars using Reanimated for average duration by job type — bars animate in with staggered delay:
                </Paragraph>
                <Code lang="tsx">{`function DurationRow({ type, durationMs, maxDuration, index }) {
  const width = useSharedValue(0);
  const percentage = (durationMs / maxDuration) * 100;

  useEffect(() => {
    width.value = withDelay(index * 100, withTiming(percentage, { duration: 800 }));
  }, [percentage, index]);

  const barStyle = useAnimatedStyle(() => ({ width: \`\${width.value}%\` }));

  return (
    <View style={styles.row}>
      <Text>{type}</Text>
      <View style={styles.barTrack}>
        <Animated.View style={[styles.barFill, barStyle]} />
      </View>
      <Text>{formatDuration(durationMs)}</Text>
    </View>
  );
}`}</Code>
            </Section>

            <Section title="Responsive Charts">
                <Paragraph>
                    Charts adapt to screen size using <code>useWindowDimensions</code>. On tablets with the two-column layout from Chapter 10, charts render side by side — pie chart next to bar chart, line chart spanning full width below.
                </Paragraph>
                <Code lang="tsx">{`const { width } = useWindowDimensions();
const chartWidth = Math.min(width - 80, 800);

// On tablets:
<View style={[styles.chartGrid, isLargeScreen && { flexDirection: "row", flexWrap: "wrap" }]}>
  <View style={isLargeScreen ? { width: "48%" } : undefined}>
    <JobsPerHourChart />
  </View>
  <View style={isLargeScreen ? { width: "48%" } : undefined}>
    <StatusPieChart />
  </View>
</View>`}</Code>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Open the Analytics tab → KPI cards show today&apos;s stats. Line chart shows jobs per hour with smooth curve. Tap/hold → tooltip. Pie chart shows status distribution. Bar chart → tap a bar → filtered list. Horizontal bars animate in with stagger. Pull to refresh → charts update. On tablet → two-column chart grid.
                </Paragraph>
                <Paragraph>
                    Captain Deadline opens the Analytics tab in the board meeting. The CEO sees: 99.2% success rate. 12,000 jobs today. Average duration 4.2 seconds. The daily trend line goes up and to the right. &quot;Good numbers. Ship it.&quot;
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
