import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="First Screen: Navigation & Core Components"
            date="May 2, 2026"
            series="Job Engine Mobile"
            chapter={1}
            prevSlug="jobengine-mobile-00-setup"
            prevTitle="Setup"
            nextSlug="jobengine-mobile-02-native-styling"
            nextTitle="Native Styling"
        >
            <Section title="The Problem">
                <Paragraph>
                    You have a single screen with &quot;ShopZilla Job Engine&quot; in white text. Captain Deadline wants tabs: one for the job list, one for submitting new jobs, one for the pipeline view. &quot;Like every app on my phone.&quot;
                </Paragraph>
            </Section>

            <Section title="React Native ≠ React DOM">
                <Paragraph>
                    In React (web), you write <code>&lt;div&gt;</code>, <code>&lt;h1&gt;</code>, <code>&lt;button&gt;</code>. In React Native, there&apos;s no DOM. Instead: <code>View</code>, <code>Text</code>, <code>Pressable</code>. Flexbox works the same, except the default flexDirection is column (not row).
                </Paragraph>
                <Code lang="tsx">{`// Web
<div className="container">
  <h1>Hello</h1>
  <button onClick={handleClick}>Click me</button>
</div>

// React Native
<View style={styles.container}>
  <Text style={styles.heading}>Hello</Text>
  <Pressable onPress={handlePress}>
    <Text>Press me</Text>
  </Pressable>
</View>`}</Code>
            </Section>

            <Section title="Setting Up Navigation">
                <Paragraph>
                    React Navigation uses a native stack — real iOS/Android navigation transitions, not CSS animations. We use bottom tabs for top-level navigation and a native stack for drill-down.
                </Paragraph>
                <Code lang="tsx" title="src/navigation/RootNavigator.tsx">{`import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";

export type RootTabParamList = {
  Jobs: undefined;
  Submit: undefined;
  Pipeline: undefined;
};

export type JobStackParamList = {
  JobList: undefined;
  JobDetail: { jobId: string };
};

const Tab = createBottomTabNavigator<RootTabParamList>();
const JobStack = createNativeStackNavigator<JobStackParamList>();

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ color, size }) => {
            const icons = { Jobs: "list-outline", Submit: "add-circle-outline", Pipeline: "git-network-outline" };
            return <Ionicons name={icons[route.name]} size={size} color={color} />;
          },
          tabBarActiveTintColor: "#3b82f6",
          tabBarStyle: { backgroundColor: "#1f2937", borderTopColor: "#374151" },
        })}
      >
        <Tab.Screen name="Jobs" component={JobStackNavigator} />
        <Tab.Screen name="Submit" component={SubmitJobScreen} />
        <Tab.Screen name="Pipeline" component={PipelineScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}`}</Code>
            </Section>

            <Section title="Type-Safe Navigation">
                <Paragraph>
                    Notice <code>JobStackParamList</code> — it defines what params each screen expects. TypeScript catches missing or wrong params at compile time:
                </Paragraph>
                <Code lang="tsx">{`// ✅ TypeScript knows jobId is required
navigation.navigate("JobDetail", { jobId: "abc-123" });

// ❌ TypeScript error — missing jobId
navigation.navigate("JobDetail");`}</Code>
            </Section>

            <Section title="Navigation Patterns">
                <Paragraph>
                    We&apos;re using three patterns: Bottom Tabs for top-level navigation, Native Stack for drill-down within a tab, and later Modals for confirmations. The stack navigator gives you the native back gesture on iOS (swipe from left edge) and the hardware back button on Android — for free.
                </Paragraph>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Run <code>npx expo start</code>. You should see three tabs at the bottom (Jobs, Submit, Pipeline), dark theme, and tapping tabs switches screens. The Jobs tab shows placeholder text.
                </Paragraph>
                <Paragraph>
                    Captain Deadline picks up his phone, taps through the tabs. &quot;Good. Now make it show actual jobs.&quot;
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
