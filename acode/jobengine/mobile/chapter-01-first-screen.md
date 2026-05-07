# Chapter 1: First Screen — Navigation & Core Components

[← Chapter 0: Setup](chapter-00-setup.md) | [Chapter 2: Native Styling →](chapter-02-native-styling.md)

---

## The Problem

You have a single screen with "ShopZilla Job Engine" in white text. Captain Deadline wants tabs: one for the job list, one for submitting new jobs, one for the pipeline view. "Like every app on my phone."

React Native doesn't have `<a href>` or `react-router`. Mobile navigation is fundamentally different — screens slide, stack, and tab. Time to learn React Navigation.

## React Native ≠ React DOM

First, the mental shift. In React (web), you write:

```tsx
<div className="container">
  <h1>Hello</h1>
  <button onClick={handleClick}>Click me</button>
</div>
```

In React Native, there's no DOM. No `<div>`, no `<h1>`, no `<button>`. Instead:

```tsx
<View style={styles.container}>
  <Text style={styles.heading}>Hello</Text>
  <Pressable onPress={handlePress}>
    <Text>Press me</Text>
  </Pressable>
</View>
```

| Web | React Native | Notes |
|---|---|---|
| `<div>` | `<View>` | Flexbox by default (column direction) |
| `<p>`, `<h1>` | `<Text>` | All text must be inside `<Text>` |
| `<button>` | `<Pressable>` | Handles touch with feedback |
| `<img>` | `<Image>` | Requires `source` prop, not `src` |
| `<input>` | `<TextInput>` | Controlled the same way |
| `<ul>` + `<li>` | `<FlatList>` | Virtualized by default |
| CSS classes | `StyleSheet` | No cascading, no global styles |

Flexbox works the same, except the default `flexDirection` is `column` (not `row`).

## Setting Up Navigation

React Navigation uses a native stack — real iOS/Android navigation transitions, not CSS animations.

```tsx
// src/navigation/RootNavigator.tsx
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { JobListScreen } from "../screens/JobListScreen";
import { SubmitJobScreen } from "../screens/SubmitJobScreen";
import { PipelineScreen } from "../screens/PipelineScreen";
import { JobDetailScreen } from "../screens/JobDetailScreen";
import { Ionicons } from "@expo/vector-icons";

// Type-safe navigation params
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

function JobStackNavigator() {
  return (
    <JobStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: "#111827" },
        headerTintColor: "#f9fafb",
        headerTitleStyle: { fontWeight: "bold" },
      }}
    >
      <JobStack.Screen name="JobList" component={JobListScreen} options={{ title: "Jobs" }} />
      <JobStack.Screen name="JobDetail" component={JobDetailScreen} options={{ title: "Job Detail" }} />
    </JobStack.Navigator>
  );
}

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            const icons: Record<string, keyof typeof Ionicons.glyphMap> = {
              Jobs: focused ? "list" : "list-outline",
              Submit: focused ? "add-circle" : "add-circle-outline",
              Pipeline: focused ? "git-network" : "git-network-outline",
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
      </Tab.Navigator>
    </NavigationContainer>
  );
}
```

## The Screens (Stubs)

```tsx
// src/screens/JobListScreen.tsx
import { View, Text, StyleSheet } from "react-native";

export function JobListScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Job List — coming in Chapter 2</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  text: { color: "#f9fafb", fontSize: 16 },
});
```

```tsx
// src/screens/SubmitJobScreen.tsx
import { View, Text, StyleSheet } from "react-native";

export function SubmitJobScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Submit Job — coming in Chapter 3</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  text: { color: "#f9fafb", fontSize: 16 },
});
```

```tsx
// src/screens/PipelineScreen.tsx
import { View, Text, StyleSheet } from "react-native";

export function PipelineScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Pipeline — coming in Chapter 9</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  text: { color: "#f9fafb", fontSize: 16 },
});
```

```tsx
// src/screens/JobDetailScreen.tsx
import { View, Text, StyleSheet } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { JobStackParamList } from "../navigation/RootNavigator";

type Props = NativeStackScreenProps<JobStackParamList, "JobDetail">;

export function JobDetailScreen({ route }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Job: {route.params.jobId}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  text: { color: "#f9fafb", fontSize: 16 },
});
```

## Wire It Up

Replace `App.tsx`:

```tsx
// App.tsx
import { SafeAreaProvider } from "react-native-safe-area-context";
import { RootNavigator } from "./src/navigation/RootNavigator";

export default function App() {
  return (
    <SafeAreaProvider>
      <RootNavigator />
    </SafeAreaProvider>
  );
}
```

Install the icon library:

```bash
npx expo install @expo/vector-icons
```

## Type-Safe Navigation

Notice `JobStackParamList` — it defines what params each screen expects. This means:

```tsx
// ✅ TypeScript knows jobId is required
navigation.navigate("JobDetail", { jobId: "abc-123" });

// ❌ TypeScript error — missing jobId
navigation.navigate("JobDetail");

// ❌ TypeScript error — wrong param name
navigation.navigate("JobDetail", { id: "abc-123" });
```

No more runtime crashes from missing params. The compiler catches it.

## Navigation Patterns

React Navigation supports multiple patterns. We're using:

1. **Bottom Tabs** — top-level navigation (Jobs, Submit, Pipeline)
2. **Native Stack** — drill-down within a tab (Job List → Job Detail)
3. **Modal** (later) — overlays for confirmations, filters

The stack navigator gives you the native back gesture on iOS (swipe from left edge) and the hardware back button on Android — for free.

## Verify

Run `npx expo start`. You should see:

- Three tabs at the bottom (Jobs, Submit, Pipeline)
- Dark theme matching the web dashboard
- Tapping tabs switches screens
- The Jobs tab shows "Job List — coming in Chapter 2"

Captain Deadline picks up his phone, taps through the tabs. "Good. Now make it show actual jobs."

That's next.

---

[← Chapter 0: Setup](chapter-00-setup.md) | [Chapter 2: Native Styling →](chapter-02-native-styling.md)
