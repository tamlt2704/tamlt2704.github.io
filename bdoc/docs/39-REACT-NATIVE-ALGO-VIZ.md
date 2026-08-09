# Chapter 39: React Native — Build an Algorithm Visualiser App

## What you'll learn

- React Native fundamentals (components, styling, navigation)
- How React Native differs from React web (no DOM, native views)
- Expo for fast development (no Xcode/Android Studio needed to start)
- Building custom animated visualisations (Reanimated + SVG)
- Touch gestures for step-through controls
- The complete algorithm visualiser: bar chart, graph, tree, grid
- State management for step playback
- Performance: 60fps animations on mobile
- Publishing to App Store / Google Play

---

## PART 1: Setup & Fundamentals

## 39.1 React Native vs React Web

```
React Web:                         React Native:
<div>                              <View>
<p>Text</p>                        <Text>Text</Text>
<img src="..." />                  <Image source={{uri: "..."}} />
<input />                          <TextInput />
<button>                           <TouchableOpacity> or <Pressable>
<ul><li>...</li></ul>              <FlatList data={[...]} />
CSS / Tailwind                     StyleSheet (Flexbox-only, no cascade)
DOM (HTML elements)                Native views (UIView, android.view.View)
```

**Key differences:**
- No CSS cascade — styles are component-scoped objects
- Flexbox is the ONLY layout system (no grid, no float, no position: static)
- `flexDirection` defaults to `column` (not `row` like web)
- No `px` units — all numbers are density-independent pixels
- Text MUST be inside `<Text>` (can't put raw text in `<View>`)

## 39.2 Create the project with Expo

```bash
npx create-expo-app AlgoViz --template blank-typescript
cd AlgoViz
npx expo start
```

Scan the QR code with **Expo Go** app (phone) or press `i` for iOS simulator / `a` for Android emulator.

**Project structure:**
```
AlgoViz/
├── app/                     ← Routes (file-based routing with Expo Router)
│   ├── _layout.tsx          ← Root layout (navigation structure)
│   ├── index.tsx            ← Home screen
│   ├── algorithms/
│   │   ├── _layout.tsx      ← Algorithm tab layout
│   │   ├── index.tsx        ← Algorithm list
│   │   └── [slug].tsx       ← Individual algorithm visualiser
├── components/
│   ├── BarChart.tsx
│   ├── GraphChart.tsx
│   ├── TreeChart.tsx
│   ├── Controls.tsx
│   └── CodePanel.tsx
├── lib/
│   ├── algorithms/
│   │   ├── bubbleSort.ts
│   │   ├── mergeSort.ts
│   │   └── bfs.ts
│   └── types.ts
├── assets/
├── app.json                 ← Expo config
└── package.json
```

## 39.3 Install key dependencies

```bash
# Navigation (file-based routing)
npx expo install expo-router expo-linking expo-constants

# SVG for visualisations
npx expo install react-native-svg

# Animations (60fps, runs on UI thread)
npx expo install react-native-reanimated

# Gesture handling
npx expo install react-native-gesture-handler

# Safe area (notch/status bar handling)
npx expo install react-native-safe-area-context
```

## 39.4 Core components

```tsx
import { View, Text, StyleSheet, ScrollView, Pressable } from "react-native";

export default function HomeScreen() {
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Algorithm Visualiser</Text>
      <Text style={styles.subtitle}>Tap an algorithm to visualise it</Text>

      <View style={styles.cardGrid}>
        <AlgorithmCard title="Bubble Sort" category="Sorting" difficulty="easy" />
        <AlgorithmCard title="Merge Sort" category="Sorting" difficulty="medium" />
        <AlgorithmCard title="BFS" category="Graph" difficulty="medium" />
      </View>
    </ScrollView>
  );
}

function AlgorithmCard({ title, category, difficulty }: {
  title: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
}) {
  const diffColor = { easy: "#22c55e", medium: "#f59e0b", hard: "#ef4444" }[difficulty];

  return (
    <Pressable
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
      onPress={() => router.push(`/algorithms/${title.toLowerCase().replace(" ", "-")}`)}
    >
      <View style={[styles.badge, { backgroundColor: diffColor + "20" }]}>
        <Text style={[styles.badgeText, { color: diffColor }]}>{difficulty}</Text>
      </View>
      <Text style={styles.cardTitle}>{title}</Text>
      <Text style={styles.cardCategory}>{category}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#f8fafc",
    marginTop: 60,
  },
  subtitle: {
    fontSize: 16,
    color: "#94a3b8",
    marginTop: 8,
    marginBottom: 24,
  },
  cardGrid: {
    gap: 12,
  },
  card: {
    backgroundColor: "#1e293b",
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: "#334155",
  },
  cardPressed: {
    opacity: 0.8,
    transform: [{ scale: 0.98 }],
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#f8fafc",
    marginTop: 8,
  },
  cardCategory: {
    fontSize: 14,
    color: "#64748b",
    marginTop: 4,
  },
  badge: {
    alignSelf: "flex-start",
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 20,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: "600",
    textTransform: "capitalize",
  },
});
```

## 39.5 Styling system — StyleSheet vs web CSS

```tsx
// React Native StyleSheet — objects, not strings
const styles = StyleSheet.create({
  // Flexbox (default direction: column)
  row: {
    flexDirection: "row",        // horizontal
    alignItems: "center",        // cross-axis (vertical for row)
    justifyContent: "space-between",  // main-axis distribution
    gap: 12,                     // spacing between children
  },

  // Box model (no margin collapse, no shorthand)
  box: {
    padding: 16,                 // all sides
    paddingHorizontal: 20,       // left + right
    marginTop: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#334155",
  },

  // Typography (no CSS inheritance!)
  heading: {
    fontSize: 24,
    fontWeight: "bold",          // "bold", "600", "400" etc.
    color: "#f8fafc",
    letterSpacing: -0.5,
  },

  // Shadows (different API from web)
  elevated: {
    // iOS
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    // Android
    elevation: 8,
  },

  // Absolute positioning (like web)
  overlay: {
    position: "absolute",
    top: 0, left: 0, right: 0, bottom: 0,
  },
});
```

> **No style inheritance in React Native.** If you set `color: "white"` on a `<View>`, its child `<Text>` does NOT inherit it. You must style each `<Text>` individually.

## 39.6 Navigation with Expo Router

```tsx
// app/_layout.tsx (root layout — defines navigation structure)
import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: "#0f172a" },
        headerTintColor: "#f8fafc",
        headerTitleStyle: { fontWeight: "bold" },
        contentStyle: { backgroundColor: "#0f172a" },
      }}
    >
      <Stack.Screen name="index" options={{ title: "AlgoViz" }} />
      <Stack.Screen name="algorithms/[slug]" options={{ title: "Visualiser" }} />
    </Stack>
  );
}

// app/algorithms/[slug].tsx (dynamic route — like Next.js [slug])
import { useLocalSearchParams } from "expo-router";

export default function AlgorithmScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  // slug = "bubble-sort", "bfs", etc.
  return <AlgorithmVisualiser algorithm={slug} />;
}
```

---

## PART 2: Building the Visualiser

## 39.7 Algorithm step engine (same as web version)

```ts
// lib/types.ts
export type AlgorithmStep = {
  codeLine: number;
  description: string;
  array: number[];
  comparing: number[];
  swapping: [number, number] | null;
  sorted: number[];
};

export type GraphStep = {
  codeLine: number;
  description: string;
  nodes: { id: string; label: string }[];
  edges: { source: string; target: string }[];
  visitedNodes: string[];
  currentNode: string | null;
  queueOrStack: string[];
};
```

```ts
// lib/algorithms/bubbleSort.ts (identical to web version)
export function generateBubbleSortSteps(input: number[]): AlgorithmStep[] {
  const steps: AlgorithmStep[] = [];
  const arr = [...input];

  steps.push({
    codeLine: 0,
    description: "Start bubble sort",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [],
  });

  for (let i = 0; i < arr.length - 1; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      steps.push({
        codeLine: 3,
        description: `Compare ${arr[j]} and ${arr[j + 1]}`,
        array: [...arr],
        comparing: [j, j + 1],
        swapping: null,
        sorted: Array.from({ length: i }, (_, k) => arr.length - 1 - k),
      });

      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        steps.push({
          codeLine: 5,
          description: `Swap ${arr[j + 1]} and ${arr[j]}`,
          array: [...arr],
          comparing: [],
          swapping: [j, j + 1],
          sorted: Array.from({ length: i }, (_, k) => arr.length - 1 - k),
        });
      }
    }
  }

  steps.push({
    codeLine: 8,
    description: "Sorted!",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: arr.map((_, i) => i),
  });

  return steps;
}
```

## 39.8 Animated Bar Chart with react-native-svg + Reanimated

```tsx
// components/BarChart.tsx
import { View, StyleSheet } from "react-native";
import Svg, { Rect, Text as SvgText } from "react-native-svg";
import Animated, {
  useAnimatedProps,
  useSharedValue,
  withTiming,
  withSpring,
} from "react-native-reanimated";

const AnimatedRect = Animated.createAnimatedComponent(Rect);

type BarChartProps = {
  data: number[];
  comparing: number[];
  sorted: number[];
  width: number;
  height: number;
};

export default function BarChart({ data, comparing, sorted, width, height }: BarChartProps) {
  const maxVal = Math.max(...data);
  const barWidth = (width - 40) / data.length - 4;
  const chartHeight = height - 40;

  return (
    <View style={styles.container}>
      <Svg width={width} height={height}>
        {data.map((value, index) => {
          const barHeight = (value / maxVal) * chartHeight;
          const x = 20 + index * (barWidth + 4);
          const y = chartHeight - barHeight + 20;

          let fill = "#3b82f6"; // default blue
          if (sorted.includes(index)) fill = "#22c55e";  // green = sorted
          if (comparing.includes(index)) fill = "#f59e0b"; // amber = comparing

          return (
            <View key={index}>
              <Rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                rx={4}
                fill={fill}
              />
              <SvgText
                x={x + barWidth / 2}
                y={y - 8}
                textAnchor="middle"
                fontSize={11}
                fontWeight="bold"
                fill="#f8fafc"
              >
                {value}
              </SvgText>
            </View>
          );
        })}
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
  },
});
```

## 39.9 Smooth animations with Reanimated

```tsx
// components/AnimatedBar.tsx
import Animated, {
  useSharedValue,
  useAnimatedProps,
  withSpring,
  withTiming,
  useEffect as useReanimatedEffect,
} from "react-native-reanimated";
import { Rect } from "react-native-svg";

const AnimatedRect = Animated.createAnimatedComponent(Rect);

type AnimatedBarProps = {
  targetX: number;
  targetY: number;
  targetHeight: number;
  width: number;
  fill: string;
};

export function AnimatedBar({ targetX, targetY, targetHeight, width, fill }: AnimatedBarProps) {
  const x = useSharedValue(targetX);
  const y = useSharedValue(targetY);
  const height = useSharedValue(targetHeight);

  // Animate to new position when props change
  React.useEffect(() => {
    x.value = withSpring(targetX, { damping: 15, stiffness: 150 });
    y.value = withSpring(targetY, { damping: 15, stiffness: 150 });
    height.value = withSpring(targetHeight, { damping: 15, stiffness: 150 });
  }, [targetX, targetY, targetHeight]);

  const animatedProps = useAnimatedProps(() => ({
    x: x.value,
    y: y.value,
    height: height.value,
  }));

  return (
    <AnimatedRect
      animatedProps={animatedProps}
      width={width}
      rx={4}
      fill={fill}
    />
  );
}
```

**Why Reanimated?**
- Animations run on the **UI thread** (not JS thread) → guaranteed 60fps
- `useSharedValue` communicates between JS and UI threads without bridge serialization
- `withSpring` / `withTiming` create smooth physics-based or linear animations
- Normal React Native `Animated` API runs on JS thread → can drop frames during heavy computation

## 39.10 Playback controls

```tsx
// components/Controls.tsx
import { View, Text, Pressable, StyleSheet } from "react-native";

type ControlsProps = {
  onPrev: () => void;
  onNext: () => void;
  onPlay: () => void;
  onReset: () => void;
  isPlaying: boolean;
  currentStep: number;
  totalSteps: number;
};

export default function Controls({
  onPrev, onNext, onPlay, onReset, isPlaying, currentStep, totalSteps,
}: ControlsProps) {
  return (
    <View style={styles.container}>
      {/* Progress bar */}
      <View style={styles.progressTrack}>
        <View
          style={[
            styles.progressFill,
            { width: `${((currentStep + 1) / totalSteps) * 100}%` },
          ]}
        />
      </View>

      {/* Step counter */}
      <Text style={styles.stepText}>
        Step {currentStep + 1} / {totalSteps}
      </Text>

      {/* Buttons */}
      <View style={styles.buttons}>
        <ControlButton icon="⏮" onPress={onReset} />
        <ControlButton icon="◀" onPress={onPrev} />
        <ControlButton
          icon={isPlaying ? "⏸" : "▶"}
          onPress={onPlay}
          primary
        />
        <ControlButton icon="▶" onPress={onNext} />
      </View>
    </View>
  );
}

function ControlButton({ icon, onPress, primary = false }: {
  icon: string; onPress: () => void; primary?: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        primary && styles.primaryButton,
        pressed && styles.buttonPressed,
      ]}
    >
      <Text style={[styles.buttonText, primary && styles.primaryButtonText]}>
        {icon}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  progressTrack: {
    height: 4,
    backgroundColor: "#334155",
    borderRadius: 2,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#3b82f6",
    borderRadius: 2,
  },
  stepText: {
    color: "#94a3b8",
    fontSize: 13,
    textAlign: "center",
  },
  buttons: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: 16,
  },
  button: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "#1e293b",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "#334155",
  },
  primaryButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#3b82f6",
    borderColor: "#3b82f6",
  },
  buttonPressed: { opacity: 0.7, transform: [{ scale: 0.95 }] },
  buttonText: { fontSize: 18, color: "#f8fafc" },
  primaryButtonText: { fontSize: 22 },
});
```

## 39.11 The main visualiser screen

```tsx
// app/algorithms/[slug].tsx
import { useState, useEffect, useMemo, useCallback } from "react";
import { View, Text, useWindowDimensions, StyleSheet } from "react-native";
import { useLocalSearchParams } from "expo-router";
import BarChart from "@/components/BarChart";
import Controls from "@/components/Controls";
import { generateBubbleSortSteps } from "@/lib/algorithms/bubbleSort";
import type { AlgorithmStep } from "@/lib/types";

const INITIAL_ARRAY = [38, 27, 43, 3, 9, 82, 10];

export default function AlgorithmScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const { width, height } = useWindowDimensions();

  const steps = useMemo(() => {
    switch (slug) {
      case "bubble-sort": return generateBubbleSortSteps(INITIAL_ARRAY);
      // case "merge-sort": return generateMergeSortSteps(INITIAL_ARRAY);
      default: return generateBubbleSortSteps(INITIAL_ARRAY);
    }
  }, [slug]);

  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const step = steps[currentStep];

  const handleNext = useCallback(() => {
    setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
  }, [steps.length]);

  const handlePrev = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const handleReset = useCallback(() => {
    setCurrentStep(0);
    setIsPlaying(false);
  }, []);

  const handlePlay = useCallback(() => {
    setIsPlaying((prev) => !prev);
  }, []);

  // Auto-play
  useEffect(() => {
    if (!isPlaying) return;
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 600);
    return () => clearInterval(timer);
  }, [isPlaying, steps.length]);

  return (
    <View style={styles.container}>
      {/* Description */}
      <View style={styles.header}>
        <Text style={styles.description}>{step.description}</Text>
      </View>

      {/* Visualisation */}
      <View style={styles.chartContainer}>
        <BarChart
          data={step.array}
          comparing={step.comparing}
          sorted={step.sorted}
          width={width - 32}
          height={height * 0.4}
        />
      </View>

      {/* Controls */}
      <Controls
        onPrev={handlePrev}
        onNext={handleNext}
        onPlay={handlePlay}
        onReset={handleReset}
        isPlaying={isPlaying}
        currentStep={currentStep}
        totalSteps={steps.length}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  header: { padding: 16 },
  description: { color: "#e2e8f0", fontSize: 16, textAlign: "center" },
  chartContainer: { flex: 1, justifyContent: "center", alignItems: "center" },
});
```



---

## PART 3: Advanced Visualisations

## 39.12 Graph visualisation (BFS/DFS)

```tsx
// components/GraphChart.tsx
import { View } from "react-native";
import Svg, { Circle, Line, Text as SvgText } from "react-native-svg";

type GraphChartProps = {
  nodes: { id: string; label: string; x: number; y: number }[];
  edges: { source: string; target: string }[];
  visitedNodes: string[];
  currentNode: string | null;
  queueOrStack: string[];
  width: number;
  height: number;
};

export default function GraphChart({
  nodes, edges, visitedNodes, currentNode, queueOrStack, width, height,
}: GraphChartProps) {
  // Pre-compute node positions (simple force-directed or fixed layout)
  const nodeMap = Object.fromEntries(nodes.map((n) => [n.id, n]));

  return (
    <Svg width={width} height={height}>
      {/* Edges */}
      {edges.map((edge, i) => {
        const source = nodeMap[edge.source];
        const target = nodeMap[edge.target];
        if (!source || !target) return null;
        return (
          <Line
            key={i}
            x1={source.x}
            y1={source.y}
            x2={target.x}
            y2={target.y}
            stroke="#475569"
            strokeWidth={2}
          />
        );
      })}

      {/* Nodes */}
      {nodes.map((node) => {
        let fill = "#3b82f6"; // default blue
        if (node.id === currentNode) fill = "#ef4444";       // red = active
        if (queueOrStack.includes(node.id)) fill = "#f59e0b"; // amber = in queue
        if (visitedNodes.includes(node.id)) fill = "#6b7280"; // grey = visited

        return (
          <View key={node.id}>
            <Circle cx={node.x} cy={node.y} r={22} fill={fill} stroke="#1e293b" strokeWidth={2} />
            <SvgText
              x={node.x}
              y={node.y + 5}
              textAnchor="middle"
              fontSize={12}
              fontWeight="bold"
              fill="white"
            >
              {node.label}
            </SvgText>
          </View>
        );
      })}
    </Svg>
  );
}
```

**Node positioning for mobile:** Since we don't have D3's force simulation in React Native easily, use pre-computed positions:

```ts
// lib/graphLayouts.ts
export function circleLayout(nodeCount: number, width: number, height: number) {
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) * 0.35;

  return Array.from({ length: nodeCount }, (_, i) => {
    const angle = (2 * Math.PI * i) / nodeCount - Math.PI / 2;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  });
}

export function treeLayout(root: TreeNode, width: number, height: number) {
  // Simple recursive layout — assign x by horizontal position, y by depth
  const positions: Map<string, { x: number; y: number }> = new Map();
  let leafIndex = 0;

  function assignPositions(node: TreeNode, depth: number) {
    if (!node.children || node.children.length === 0) {
      positions.set(node.id, { x: leafIndex * (width / 10), y: depth * 60 + 40 });
      leafIndex++;
    } else {
      for (const child of node.children) assignPositions(child, depth + 1);
      const childPositions = node.children.map((c) => positions.get(c.id)!);
      const avgX = childPositions.reduce((sum, p) => sum + p.x, 0) / childPositions.length;
      positions.set(node.id, { x: avgX, y: depth * 60 + 40 });
    }
  }

  assignPositions(root, 0);
  return positions;
}
```

## 39.13 Swipe gestures for step control

```tsx
// components/SwipeableVisualiser.tsx
import { GestureDetector, Gesture } from "react-native-gesture-handler";
import Animated, { useSharedValue, withSpring, runOnJS } from "react-native-reanimated";

type SwipeableProps = {
  onSwipeLeft: () => void;   // next step
  onSwipeRight: () => void;  // previous step
  children: React.ReactNode;
};

export function SwipeableVisualiser({ onSwipeLeft, onSwipeRight, children }: SwipeableProps) {
  const translateX = useSharedValue(0);

  const gesture = Gesture.Pan()
    .onUpdate((event) => {
      translateX.value = event.translationX * 0.3; // damped drag
    })
    .onEnd((event) => {
      if (event.translationX < -50) {
        runOnJS(onSwipeLeft)();  // swipe left = next
      } else if (event.translationX > 50) {
        runOnJS(onSwipeRight)(); // swipe right = previous
      }
      translateX.value = withSpring(0); // snap back
    });

  const animatedStyle = {
    transform: [{ translateX: translateX }],
  };

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View style={animatedStyle}>
        {children}
      </Animated.View>
    </GestureDetector>
  );
}
```

Usage in the visualiser:
```tsx
<SwipeableVisualiser onSwipeLeft={handleNext} onSwipeRight={handlePrev}>
  <BarChart data={step.array} ... />
</SwipeableVisualiser>
```

## 39.14 Code panel (syntax-highlighted)

```tsx
// components/CodePanel.tsx
import { View, Text, ScrollView, StyleSheet } from "react-native";

type CodePanelProps = {
  code: string[];
  currentLine: number;
  language: string;
};

const KEYWORDS = new Set(["public", "void", "int", "for", "if", "else", "return", "new", "boolean"]);

export default function CodePanel({ code, currentLine }: CodePanelProps) {
  return (
    <ScrollView style={styles.container} horizontal={false}>
      {code.map((line, index) => (
        <View
          key={index}
          style={[styles.line, index === currentLine && styles.activeLine]}
        >
          <Text style={styles.lineNumber}>{index + 1}</Text>
          <Text style={styles.code}>
            {line.split(/(\s+|\b)/).map((token, i) => (
              <Text
                key={i}
                style={KEYWORDS.has(token) ? styles.keyword : styles.normal}
              >
                {token}
              </Text>
            ))}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#1e1e2e",
    borderRadius: 12,
    padding: 12,
    maxHeight: 200,
  },
  line: {
    flexDirection: "row",
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: 4,
  },
  activeLine: {
    backgroundColor: "rgba(250, 204, 21, 0.15)",
    borderLeftWidth: 3,
    borderLeftColor: "#facc15",
  },
  lineNumber: {
    color: "#6b7280",
    width: 24,
    fontSize: 12,
    fontFamily: "monospace",
  },
  code: {
    fontSize: 12,
    fontFamily: "monospace",
    color: "#e2e8f0",
  },
  keyword: { color: "#c084fc" },
  normal: { color: "#e2e8f0" },
});
```

---

## PART 4: Performance & Polish

## 39.15 Performance rules for 60fps

| Rule | Why | How |
|------|-----|-----|
| Use `useCallback` on handlers | Prevent child re-renders | Wrap onPress, onSwipe handlers |
| Use `useMemo` for step generation | Don't recalculate 1000 steps every render | `useMemo(() => generate(...), [input])` |
| Animate on UI thread | JS thread can't guarantee 60fps | Use `react-native-reanimated` (not `Animated`) |
| Use `FlatList` for long lists | Only renders visible items | Replace `ScrollView` + `map` for 50+ items |
| Avoid inline styles in loops | Creates new objects every render | Use `StyleSheet.create` + dynamic via array |
| `React.memo` for heavy components | Skip re-render if props unchanged | `export default React.memo(BarChart)` |
| Reduce SVG elements | SVG re-render is expensive | Batch updates, use fewer shapes |

```tsx
// ❌ Inline style in render loop (new object every frame)
{data.map((val, i) => (
  <Rect style={{ fill: comparing.includes(i) ? "amber" : "blue" }} />
))}

// ✅ Compute once, pass as prop
const fills = useMemo(
  () => data.map((_, i) => comparing.includes(i) ? "#f59e0b" : "#3b82f6"),
  [data, comparing]
);
```

## 39.16 Dark/Light theme

```tsx
// context/ThemeContext.tsx
import { createContext, useContext, useState } from "react";
import { useColorScheme } from "react-native";

const themes = {
  dark: {
    background: "#0f172a",
    card: "#1e293b",
    text: "#f8fafc",
    textSecondary: "#94a3b8",
    border: "#334155",
    primary: "#3b82f6",
  },
  light: {
    background: "#f8fafc",
    card: "#ffffff",
    text: "#0f172a",
    textSecondary: "#64748b",
    border: "#e2e8f0",
    primary: "#3b82f6",
  },
};

const ThemeContext = createContext(themes.dark);
export const useTheme = () => useContext(ThemeContext);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const systemScheme = useColorScheme(); // "dark" or "light"
  const theme = themes[systemScheme || "dark"];

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
}
```

## 39.17 Haptic feedback

```tsx
import * as Haptics from "expo-haptics";

function handleNext() {
  setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); // subtle tap
}

function handleSwap() {
  // When bars swap — medium haptic
  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
}

function handleComplete() {
  // When sorting finishes — success haptic
  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
}
```

---

## PART 5: Publishing

## 39.18 Build for production

```bash
# Build for iOS
npx expo build:ios
# or with EAS (recommended):
npx eas build --platform ios

# Build for Android
npx eas build --platform android

# Build both
npx eas build --platform all
```

**EAS (Expo Application Services)** handles signing, building, and submitting without local Xcode/Android Studio.

## 39.19 App Store checklist

```
□ App icon (1024×1024, no transparency for iOS)
□ Splash screen (configured in app.json)
□ App name and description
□ Screenshots (6.7", 6.5", 5.5" for iOS; phone + tablet for Android)
□ Privacy policy URL
□ Version number and build number
□ Test on real devices (not just simulator)
□ Performance: no janky animations, fast startup
□ Accessibility: labels on buttons, sufficient contrast
□ Handle edge cases: empty states, error screens, offline
```

```json
// app.json
{
  "expo": {
    "name": "AlgoViz",
    "slug": "algo-viz",
    "version": "1.0.0",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#0f172a"
    },
    "ios": {
      "bundleIdentifier": "com.yourname.algoviz",
      "buildNumber": "1"
    },
    "android": {
      "package": "com.yourname.algoviz",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#0f172a"
      }
    }
  }
}
```

---

## Summary

✅ React Native fundamentals: View, Text, StyleSheet, Pressable (no DOM, no CSS cascade)
✅ Expo setup: quick start without Xcode/Android Studio
✅ File-based navigation with Expo Router (same pattern as Next.js)
✅ SVG-based algorithm visualisations (BarChart, GraphChart) with react-native-svg
✅ 60fps animations with Reanimated (UI thread, spring physics)
✅ Gesture controls: swipe left/right to step through algorithms
✅ Code panel with basic syntax highlighting
✅ Step engine: identical logic to web version (shared TypeScript)
✅ Performance: useMemo, useCallback, React.memo, FlatList, Reanimated
✅ Polish: dark/light theme, haptic feedback, progress bar
✅ Publishing: EAS build → App Store / Google Play

## Key takeaways

**React Native ≠ React Web with a different renderer.** No CSS cascade, no `<div>`, Flexbox-only layout, different styling mental model. But the React paradigm (components, hooks, state) is identical — and your algorithm logic (step generation) is 100% shared.

**Reanimated is non-negotiable for smooth animations.** Regular `Animated` runs on the JS thread — any computation (step generation, re-renders) drops frames. Reanimated runs animations on the native UI thread — guaranteed 60fps regardless of JS load.

**Code sharing between web and mobile is real.** Your `lib/algorithms/` directory (step generators, types) is identical in both projects. Only the rendering layer (SVG components, controls) differs. This is the promise of React Native — learn once, build for all platforms.

**Ship with Expo + EAS.** No need to maintain Xcode/Gradle configs. EAS handles signing, building, and submitting. Focus on your app, not build infrastructure.

---

→ [Back to Chapter 38: GraphQL](./38-GRAPHQL.md)
