import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Data Fetching: Talking to the Backend"
            date="May 4, 2026"
            series="Job Engine Mobile"
            chapter={3}
            prevSlug="jobengine-mobile-02-native-styling"
            prevTitle="Native Styling"
            nextSlug="jobengine-mobile-04-realtime-push"
            nextTitle="Real-time & Push"
        >
            <Section title="The Problem">
                <Paragraph>
                    The job list shows mock data. Karen submits a CSV import from her desk, walks to the coffee machine, opens the app — and sees the same five fake jobs. &quot;Where&apos;s my import?&quot;
                </Paragraph>
                <Paragraph>
                    Mobile has complications the web didn&apos;t: the phone isn&apos;t on localhost, the connection drops in elevators, the app gets backgrounded mid-request, and you need cached data so the list isn&apos;t blank every time she opens the app.
                </Paragraph>
            </Section>

            <Section title="TanStack Query: Server State Done Right">
                <Paragraph>
                    On the web dashboard, we used raw fetch + useState. On mobile you need automatic background refetch when the app comes to foreground, cache that persists across screen navigations, retry logic for flaky connections, and loading/error/success states without boilerplate.
                </Paragraph>
                <Code lang="bash">{`npm install @tanstack/react-query`}</Code>
                <Code lang="tsx" title="src/services/queryClient.ts">{`import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,        // Data is fresh for 30 seconds
      retry: 3,                  // Retry failed requests 3 times
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000),
      refetchOnWindowFocus: true,
    },
  },
});`}</Code>
            </Section>

            <Section title="The API Service">
                <Code lang="tsx" title="src/services/api.ts">{`import { API_URL } from "./config";
import type { Job } from "../types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(\`\${API_URL}\${path}\`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) throw new Error(\`\${res.status}: \${await res.text()}\`);
  return res.json();
}

export const jobsApi = {
  getAll: () => request<Job[]>("/jobs"),
  getById: (id: string) => request<Job>(\`/jobs/\${id}\`),
  submit: (type: string, payload: string, priority = "NORMAL") =>
    request<Job>("/jobs", { method: "POST", body: JSON.stringify({ type, payload, priority }) }),
  cancel: (id: string) => request<void>(\`/jobs/\${id}/cancel\`, { method: "POST" }),
};`}</Code>
            </Section>

            <Section title="Custom Hooks">
                <Code lang="tsx" title="src/hooks/useJobs.ts">{`import { useQuery } from "@tanstack/react-query";
import { jobsApi } from "../services/api";

export function useJobs() {
  return useQuery({
    queryKey: ["jobs"],
    queryFn: jobsApi.getAll,
    refetchInterval: 10_000, // Poll every 10s as fallback
  });
}`}</Code>
                <Paragraph>
                    React Query deduplicates — if two screens use <code>useJobs()</code>, only one network request fires.
                </Paragraph>
            </Section>

            <Section title="Foreground Refetch with AppState">
                <Paragraph>
                    When Karen switches back to the app from Messages, the data should refresh automatically:
                </Paragraph>
                <Code lang="tsx">{`import { AppState } from "react-native";
import { useQueryClient } from "@tanstack/react-query";

export function useAppStateRefetch() {
  const queryClient = useQueryClient();
  useEffect(() => {
    const sub = AppState.addEventListener("change", (state) => {
      if (state === "active") queryClient.invalidateQueries();
    });
    return () => sub.remove();
  }, [queryClient]);
}`}</Code>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Start the backend. Run the app. The job list loads real data. Pull-to-refresh fetches fresh data. Submit a job → switch to Jobs tab → it appears. Kill the backend → error screen with &quot;Tap to retry.&quot; Background the app → reopen → data refreshes.
                </Paragraph>
                <Paragraph>
                    Karen submits a CSV import from her desk. Walks to the coffee machine. Opens the app. Her import is there, status RUNNING, progress bar filling. &quot;But I have to keep opening the app to check. Can&apos;t it just tell me when it&apos;s done?&quot;
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
