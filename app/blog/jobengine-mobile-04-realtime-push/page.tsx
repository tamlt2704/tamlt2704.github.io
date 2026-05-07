import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Real-time & Push Notifications: Never Miss a Job"
            date="May 5, 2026"
            series="Job Engine Mobile"
            chapter={4}
            prevSlug="jobengine-mobile-03-data-fetching"
            prevTitle="Data Fetching"
            nextSlug="jobengine-mobile-05-performance"
            nextTitle="Performance"
        >
            <Section title="The Problem">
                <Paragraph>
                    Karen submits a 50,000-row CSV import. It takes 8 minutes. She locks her phone, goes to a meeting. When she comes back, the job finished 6 minutes ago. &quot;Why didn&apos;t it tell me?&quot;
                </Paragraph>
                <Paragraph>
                    Two systems: SSE for foreground (real-time UI updates), push notifications for background (reach the user when the app is closed).
                </Paragraph>
            </Section>

            <Section title="SSE on Mobile">
                <Paragraph>
                    React Native doesn&apos;t have EventSource built in. We use <code>react-native-sse</code> and connect/disconnect based on app lifecycle:
                </Paragraph>
                <Code lang="tsx" title="src/services/sseClient.ts">{`import EventSource from "react-native-sse";
import { queryClient } from "./queryClient";

let eventSource: EventSource | null = null;

export function connectSSE(token?: string) {
  eventSource = new EventSource(\`\${API_URL}/jobs/stream\`, {
    headers: token ? { Authorization: \`Bearer \${token}\` } : {},
  });

  eventSource.addEventListener("job-update", (event) => {
    const data = JSON.parse(event.data);
    // Update React Query cache directly — no refetch needed
    queryClient.setQueryData(["jobs"], (old) =>
      old?.map((job) => job.id === data.jobId ? { ...job, status: data.status, progress: data.progress } : job)
    );
  });
}

export function disconnectSSE() {
  eventSource?.close();
  eventSource = null;
}`}</Code>
                <Paragraph>
                    Connect when the app is active, disconnect when backgrounded. Job cards update in real time — progress bars fill, badges change color, no polling.
                </Paragraph>
            </Section>

            <Section title="Push Notifications">
                <Code lang="bash">{`npx expo install expo-notifications expo-device expo-constants`}</Code>
                <Code lang="tsx" title="src/services/notifications.ts">{`import * as Notifications from "expo-notifications";
import * as Device from "expo-device";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications() {
  if (!Device.isDevice) return null;

  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== "granted") return null;

  const tokenData = await Notifications.getExpoPushTokenAsync({ projectId });
  return tokenData.data; // Send this to your backend
}`}</Code>
            </Section>

            <Section title="Notification Tap → Navigate">
                <Paragraph>
                    When the user taps a notification, navigate to the job detail:
                </Paragraph>
                <Code lang="tsx">{`Notifications.addNotificationResponseReceivedListener((response) => {
  const jobId = response.notification.request.content.data?.jobId;
  if (jobId) navigation.navigate("JobDetail", { jobId });
});`}</Code>
            </Section>

            <Section title="Badge Count">
                <Paragraph>
                    Show unread completions on the app icon. Reset when the user opens the Jobs tab.
                </Paragraph>
                <Code lang="tsx">{`await Notifications.setBadgeCountAsync(count);
// Reset on tab focus:
await Notifications.setBadgeCountAsync(0);`}</Code>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Open the app — job list updates in real time. Background the app → submit a job from curl → wait for completion → push notification appears. Tap it → app opens to Job Detail. Badge shows &quot;1&quot; on the app icon.
                </Paragraph>
                <Paragraph>
                    Karen locks her phone. Goes to her meeting. Five minutes later, her phone buzzes: &quot;CSV_IMPORT completed ✓ — 50,000 rows imported.&quot; She taps it. Green badge. All rows imported. She doesn&apos;t even need to open the app anymore.
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
