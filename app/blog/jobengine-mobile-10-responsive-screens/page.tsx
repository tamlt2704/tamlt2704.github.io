import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Multiple Screens: Phone, Tablet, Foldable"
            date="May 11, 2026"
            series="Job Engine Mobile"
            chapter={10}
            prevSlug="jobengine-mobile-09-dag-visualization"
            prevTitle="DAG Visualization"
            nextSlug="jobengine-mobile-11-charts-analytics"
            nextTitle="Charts & Analytics"
        >
            <Section title="The Problem">
                <Paragraph>
                    Mrs. Jira buys the team iPads. She opens the app on a 12.9-inch iPad Pro in landscape. The job cards are tiny, centered in a sea of empty space. Captain Deadline has a Samsung Galaxy Z Fold5. He unfolds it — the app doesn&apos;t adapt. Same phone layout, just bigger.
                </Paragraph>
            </Section>

            <Section title="Detecting Screen Size">
                <Code lang="tsx" title="src/hooks/useScreenInfo.ts">{`import { useWindowDimensions } from "react-native";

export function useScreenInfo() {
  const { width, height } = useWindowDimensions();
  const orientation = width > height ? "landscape" : "portrait";
  const device = Math.min(width, height) >= 600 ? "tablet" : "phone";
  const isLargeScreen = width >= 768;

  let columns = 1;
  if (width >= 1024) columns = 3;
  else if (width >= 768) columns = 2;
  else if (width >= 600 && orientation === "landscape") columns = 2;

  return { device, orientation, width, height, columns, isLargeScreen };
}`}</Code>
                <Paragraph>
                    <code>useWindowDimensions</code> updates in real time — when the user rotates or unfolds a foldable, the layout recalculates instantly.
                </Paragraph>
            </Section>

            <Section title="Adaptive Navigation: Tabs vs Sidebar">
                <Paragraph>
                    On phones, bottom tabs. On tablets, a permanent sidebar drawer:
                </Paragraph>
                <Code lang="tsx">{`import { createDrawerNavigator } from "@react-navigation/drawer";

export function AdaptiveNavigator() {
  const { isLargeScreen } = useScreenInfo();
  return isLargeScreen ? <DrawerNavigator /> : <TabNavigator />;
}

// Drawer config for tablets:
<Drawer.Navigator screenOptions={{
  drawerType: "permanent",
  drawerStyle: { backgroundColor: "#1f2937", width: 240 },
}} />`}</Code>
            </Section>

            <Section title="Master-Detail on Tablets">
                <Paragraph>
                    On tablets in landscape, show the job list and detail side by side:
                </Paragraph>
                <Code lang="tsx">{`export function JobMasterDetail() {
  const { isLargeScreen, orientation } = useScreenInfo();
  const [selectedJobId, setSelectedJobId] = useState(null);
  const showSplitView = isLargeScreen && orientation === "landscape";

  if (showSplitView) {
    return (
      <View style={{ flex: 1, flexDirection: "row" }}>
        <View style={{ width: "40%", borderRightWidth: 1 }}>
          <JobListPanel onSelect={setSelectedJobId} />
        </View>
        <View style={{ flex: 1 }}>
          {selectedJobId ? <JobDetailPanel jobId={selectedJobId} /> : <EmptyDetail />}
        </View>
      </View>
    );
  }
  return <JobListPanel onSelect={setSelectedJobId} />;
}`}</Code>
            </Section>

            <Section title="Responsive Grid">
                <Paragraph>
                    The job list shows more columns on wider screens. Note the <code>key</code> prop — FlatList doesn&apos;t support dynamic numColumns, so we force a re-mount:
                </Paragraph>
                <Code lang="tsx">{`const { columns } = useScreenInfo();

<FlatList
  data={jobs}
  numColumns={columns}
  key={\`grid-\${columns}\`}  // Force re-mount when columns change
  columnWrapperStyle={columns > 1 ? { gap: 8 } : undefined}
/>`}</Code>
            </Section>

            <Section title="Foldable Devices">
                <Paragraph>
                    Samsung Galaxy Z Fold changes screen size mid-session. Detect large width changes (&gt; 200px delta) and allow the layout to settle before re-rendering:
                </Paragraph>
                <Code lang="tsx">{`export function useFoldableState() {
  const { width } = useWindowDimensions();
  const [prevWidth, setPrevWidth] = useState(width);

  useEffect(() => {
    const delta = Math.abs(width - prevWidth);
    if (delta > 200) {
      setTransitionInProgress(true);
      setTimeout(() => setTransitionInProgress(false), 300);
    }
    setPrevWidth(width);
  }, [width]);

  return { isFolded: width < 600, transitionInProgress };
}`}</Code>
            </Section>

            <Section title="iPad Multitasking">
                <Paragraph>
                    Enable Split View by setting <code>requireFullScreen: false</code> in app.json. Your responsive hooks handle the rest — the width changes just like a rotation.
                </Paragraph>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    iPhone 15 Pro → single column, bottom tabs. iPad Pro landscape → sidebar + master-detail split. Galaxy Z Fold folded → phone layout. Unfolded → tablet layout, smooth transition. iPad Split View (1/3 width) → falls back to phone layout.
                </Paragraph>
                <Paragraph>
                    Mrs. Jira opens the app on her iPad in landscape. The sidebar shows all sections. The job list takes 40% of the screen, the detail panel shows the selected job on the right. Captain Deadline unfolds his Galaxy Z Fold. The app transitions seamlessly.
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
