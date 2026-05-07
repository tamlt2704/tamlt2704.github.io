import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Offline & Persistence: Works Without WiFi"
            date="May 8, 2026"
            series="Job Engine Mobile"
            chapter={7}
            prevSlug="jobengine-mobile-06-gestures-animations"
            prevTitle="Gestures & Animations"
            nextSlug="jobengine-mobile-08-authentication"
            nextTitle="Authentication"
        >
            <Section title="The Problem">
                <Paragraph>
                    Karen steps into the elevator. Signal drops. She opens the app — blank screen, &quot;Failed to load jobs.&quot; The web version at least shows the last data she saw. This shows nothing.
                </Paragraph>
                <Paragraph>
                    The app needs to: show cached data when offline, queue actions performed offline, indicate what&apos;s stale vs fresh, and persist the cache across app restarts.
                </Paragraph>
            </Section>

            <Section title="MMKV: 30x Faster Than AsyncStorage">
                <Paragraph>
                    MMKV is a key-value storage library from WeChat. It&apos;s synchronous, encrypted, and 30x faster than AsyncStorage.
                </Paragraph>
                <Code lang="tsx" title="src/services/storage.ts">{`import { MMKV } from "react-native-mmkv";

export const storage = new MMKV({
  id: "jobengine-cache",
  encryptionKey: "shopzilla-2024",
});`}</Code>
            </Section>

            <Section title="Persist React Query Cache">
                <Paragraph>
                    Wire MMKV into React Query&apos;s persistence layer. Now when Karen opens the app, cached data loads from disk in under 5ms — no loading spinner on cold start:
                </Paragraph>
                <Code lang="tsx">{`import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { createSyncStoragePersister } from "@tanstack/query-sync-storage-persister";

const persister = createSyncStoragePersister({ storage: mmkvStorageAdapter });

// Wrap your app:
<PersistQueryClientProvider client={queryClient} persistOptions={{ persister, maxAge: 24 * 60 * 60 * 1000 }}>
  {/* app */}
</PersistQueryClientProvider>`}</Code>
            </Section>

            <Section title="Offline Mutation Queue">
                <Paragraph>
                    When Karen cancels a job offline, queue it and sync when back online:
                </Paragraph>
                <Code lang="tsx" title="src/services/syncQueue.ts">{`export function enqueue(mutation: { url: string; method: string; body?: string }) {
  const queue = getQueue();
  queue.push({ ...mutation, id: Date.now().toString(), timestamp: Date.now(), retries: 0 });
  saveQueue(queue);
}

export async function processQueue(authToken?: string) {
  const state = await NetInfo.fetch();
  if (!state.isConnected) return;

  const queue = getQueue();
  for (const mutation of queue) {
    const res = await fetch(mutation.url, { method: mutation.method, body: mutation.body, headers: { Authorization: \`Bearer \${authToken}\` } });
    if (res.ok) processed++;
  }
}`}</Code>
            </Section>

            <Section title="Optimistic Updates">
                <Paragraph>
                    Update the UI immediately — don&apos;t wait for the server. If the sync fails later, roll back:
                </Paragraph>
                <Code lang="tsx">{`useMutation({
  mutationFn: async (id) => {
    if (!isConnected) { enqueue({ url: \`/jobs/\${id}/cancel\`, method: "POST" }); return; }
    return jobsApi.cancel(id);
  },
  onMutate: async (id) => {
    const previousJobs = queryClient.getQueryData(["jobs"]);
    queryClient.setQueryData(["jobs"], (old) =>
      old?.map((job) => job.id === id ? { ...job, status: "CANCELLED" } : job)
    );
    return { previousJobs };
  },
  onError: (_err, _id, context) => {
    queryClient.setQueryData(["jobs"], context.previousJobs); // Rollback
  },
});`}</Code>
            </Section>

            <Section title="Sync on Reconnect">
                <Paragraph>
                    Listen for network state changes. When connectivity returns, process the queue and refresh all data:
                </Paragraph>
                <Code lang="tsx">{`NetInfo.addEventListener(async (state) => {
  if (state.isConnected && wasOffline) {
    await processQueue(token);
    queryClient.invalidateQueries();
  }
  wasOffline = !state.isConnected;
});`}</Code>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Load the app with network → jobs appear. Enable airplane mode → offline banner shows. Cancel a job → card immediately shows CANCELLED. Disable airplane mode → banner disappears, queue syncs. Kill the app → reopen → cached data appears instantly.
                </Paragraph>
                <Paragraph>
                    Karen walks into the elevator. The banner says &quot;No connection — showing cached data.&quot; She swipes to cancel a job — it goes grey immediately. She walks out. The banner disappears. The cancel syncs. Everything is consistent.
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
