import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Native Styling: Building a Job List That Feels Native"
            date="May 3, 2026"
            series="Job Engine Mobile"
            chapter={2}
            prevSlug="jobengine-mobile-01-first-screen"
            prevTitle="First Screen"
            nextSlug="jobengine-mobile-03-data-fetching"
            nextTitle="Data Fetching"
        >
            <Section title="The Problem">
                <Paragraph>
                    Karen opens the app. &quot;It looks like a website someone shoved into a phone.&quot; She&apos;s right. No cards, no badges, no visual hierarchy. It doesn&apos;t feel like an app.
                </Paragraph>
            </Section>

            <Section title="StyleSheet: Not CSS">
                <Paragraph>
                    React Native&apos;s StyleSheet looks like CSS but isn&apos;t. No cascading, no class names, no media queries, no pseudo-classes. Units are density-independent pixels. <code>StyleSheet.create</code> validates styles at creation time and optimizes them for the bridge.
                </Paragraph>
                <Code lang="tsx">{`const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1f2937",
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 6,
    ...Platform.select({
      ios: { shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.25, shadowRadius: 4 },
      android: { elevation: 4 },
    }),
  },
});`}</Code>
            </Section>

            <Section title="The Job Card">
                <Paragraph>
                    Each job card shows the type, status badge, ID, progress bar (if running), timestamp, and priority. Platform-specific shadows give it depth on both iOS and Android.
                </Paragraph>
                <Code lang="tsx" title="src/components/JobCard.tsx">{`export function JobCard({ job, onPress }: Props) {
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
          <View style={[styles.progressFill, { width: \`\${job.progress}%\` }]} />
        </View>
      )}
    </Pressable>
  );
}`}</Code>
            </Section>

            <Section title="FlatList: The Native List">
                <Paragraph>
                    On the web, you&apos;d map over an array and render divs. On mobile, that kills performance — 10,000 cards would mount 10,000 views. <code>FlatList</code> virtualizes: only visible items are rendered. Add <code>RefreshControl</code> for pull-to-refresh with the native spinner.
                </Paragraph>
                <Code lang="tsx">{`<FlatList
  data={jobs}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => <JobCard job={item} onPress={handlePress} />}
  refreshControl={
    <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor="#3b82f6" />
  }
  ListEmptyComponent={<Text>No jobs yet</Text>}
/>`}</Code>
            </Section>

            <Section title="Safe Areas">
                <Paragraph>
                    The iPhone has a notch. The Pixel has a camera cutout. <code>SafeAreaView</code> from <code>react-native-safe-area-context</code> handles this — content won&apos;t hide behind the notch or home indicator.
                </Paragraph>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Dark theme with stats bar at the top. Five job cards with colored status badges. Pull-to-refresh with native spinner. Tap a card → navigates to Job Detail. Platform-appropriate shadows.
                </Paragraph>
                <Paragraph>
                    Karen pulls down to refresh. The cards have rounded corners and subtle shadows. &quot;Okay, this looks like an app now. But where&apos;s the real data?&quot;
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
