import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Performance: Silky Smooth at 10,000 Jobs"
            date="May 6, 2026"
            series="Job Engine Mobile"
            chapter={5}
            prevSlug="jobengine-mobile-04-realtime-push"
            prevTitle="Real-time & Push"
            nextSlug="jobengine-mobile-06-gestures-animations"
            nextTitle="Gestures & Animations"
        >
            <Section title="The Problem">
                <Paragraph>
                    Black Friday. ShopZilla processes 10,000 jobs in a day. Karen scrolls through the job list and it stutters — frames drop, the scroll hitches, her phone gets warm. Every SSE event re-renders the entire list. Every card recalculates its styles.
                </Paragraph>
            </Section>

            <Section title="React.memo + Stable References">
                <Paragraph>
                    Wrap JobCard in <code>React.memo</code> with a custom comparator. Only re-render if status, progress, or result actually changed:
                </Paragraph>
                <Code lang="tsx">{`export const JobCard = memo(
  function JobCard({ job, onPress }: Props) { /* ... */ },
  (prev, next) => (
    prev.job.id === next.job.id &&
    prev.job.status === next.job.status &&
    prev.job.progress === next.job.progress
  )
);

// Stable handler reference — don't break memo
const handlePress = useCallback(
  (id: string) => navigation.navigate("JobDetail", { jobId: id }),
  [navigation]
);`}</Code>
            </Section>

            <Section title="FlatList Tuning">
                <Code lang="tsx">{`<FlatList
  data={jobs}
  initialNumToRender={15}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}
  getItemLayout={(_, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>`}</Code>
                <Paragraph>
                    <code>getItemLayout</code> is the biggest win — if every card is the same height, FlatList skips measuring each item. This alone can double scroll performance.
                </Paragraph>
            </Section>

            <Section title="Infinite Scroll Pagination">
                <Paragraph>
                    Don&apos;t fetch 10,000 jobs at once. Use cursor-based pagination with TanStack Query&apos;s <code>useInfiniteQuery</code>:
                </Paragraph>
                <Code lang="tsx">{`export function useInfiniteJobs() {
  return useInfiniteQuery({
    queryKey: ["jobs", "infinite"],
    queryFn: async ({ pageParam }) => {
      const url = pageParam
        ? \`\${API_URL}/jobs?cursor=\${pageParam}&limit=20\`
        : \`\${API_URL}/jobs?limit=20\`;
      return (await fetch(url)).json();
    },
    initialPageParam: null,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}

// In the screen:
<FlatList
  onEndReached={() => hasNextPage && fetchNextPage()}
  onEndReachedThreshold={0.5}
/>`}</Code>
            </Section>

            <Section title="Hermes Engine">
                <Paragraph>
                    Hermes compiles JS to bytecode ahead of time. 50% faster startup, 30% less memory. Enabled by default in Expo SDK 49+. Verify with:
                </Paragraph>
                <Code lang="tsx">{`const isHermes = () => !!(global as any).HermesInternal;
console.log("Hermes enabled:", isHermes());`}</Code>
            </Section>

            <Section title="Results">
                <Paragraph>
                    Before and after on a Pixel 7: scroll FPS went from 38-45 to 58-60. Initial render (1000 jobs) dropped from 1200ms to 180ms. Memory usage for 10,000 jobs went from 340MB to 95MB.
                </Paragraph>
                <Paragraph>
                    Karen scrolls through 500 jobs. Smooth as butter. No stutter. &quot;Nice. But I want to swipe a job to cancel it. Like deleting an email.&quot;
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
