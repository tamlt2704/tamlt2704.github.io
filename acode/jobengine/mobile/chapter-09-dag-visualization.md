# Chapter 9: DAG Visualization — The Pipeline on Your Palm

[← Chapter 8: Authentication](chapter-08-authentication.md) | [Chapter 10: Production Release →](chapter-10-production-release.md)

---

## The Problem

Captain Deadline is in a taxi. He opens the app to check the nightly pipeline. On the web dashboard, React Flow renders a beautiful DAG — nodes connected by edges, color-coded by status. On mobile, the Pipeline tab says "Coming in Chapter 9."

"I need to see which step is blocking the pipeline. Right now. From my phone."

The web's React Flow doesn't work on React Native — it's DOM-based. We need to render the DAG with SVG, handle pan/zoom with gestures, and make it usable on a 6-inch screen.

## The DAG Data Model

From the backend (Chapter 5 of the backend series), a pipeline is a directed acyclic graph:

```tsx
// src/types/pipeline.ts
export interface PipelineNode {
  id: string;
  jobId: string;
  type: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "BLOCKED";
  label: string;
  dependsOn: string[]; // IDs of nodes that must complete first
}

export interface Pipeline {
  id: string;
  name: string;
  nodes: PipelineNode[];
  createdAt: string;
  status: "RUNNING" | "COMPLETED" | "FAILED";
}
```

## Layout Algorithm: Topological Sort + Layers

We need to position nodes in layers (columns) based on their dependencies:

```tsx
// src/utils/dagLayout.ts
import type { PipelineNode } from "../types/pipeline";

interface LayoutNode extends PipelineNode {
  x: number;
  y: number;
  layer: number;
}

const NODE_WIDTH = 140;
const NODE_HEIGHT = 60;
const LAYER_GAP = 180;
const NODE_GAP = 80;

export function layoutDAG(nodes: PipelineNode[]): LayoutNode[] {
  // Assign layers via topological sort
  const layers = assignLayers(nodes);

  // Position nodes within each layer
  return layers.flatMap((layerNodes, layerIndex) =>
    layerNodes.map((node, nodeIndex) => ({
      ...node,
      layer: layerIndex,
      x: layerIndex * LAYER_GAP + 40,
      y: nodeIndex * NODE_GAP + (layerIndex % 2 === 0 ? 0 : NODE_GAP / 2) + 40,
    }))
  );
}

function assignLayers(nodes: PipelineNode[]): PipelineNode[][] {
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));
  const layers: PipelineNode[][] = [];
  const assigned = new Set<string>();

  // Nodes with no dependencies go in layer 0
  let currentLayer = nodes.filter((n) => n.dependsOn.length === 0);

  while (currentLayer.length > 0) {
    layers.push(currentLayer);
    currentLayer.forEach((n) => assigned.add(n.id));

    // Next layer: nodes whose dependencies are all assigned
    currentLayer = nodes.filter(
      (n) => !assigned.has(n.id) && n.dependsOn.every((dep) => assigned.has(dep))
    );
  }

  return layers;
}

export function getEdges(nodes: LayoutNode[]): { from: LayoutNode; to: LayoutNode }[] {
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));
  const edges: { from: LayoutNode; to: LayoutNode }[] = [];

  for (const node of nodes) {
    for (const depId of node.dependsOn) {
      const from = nodeMap.get(depId);
      if (from) {
        edges.push({ from, to: node });
      }
    }
  }

  return edges;
}
```

## SVG Rendering

```bash
npx expo install react-native-svg
```

```tsx
// src/components/DAGGraph.tsx
import { View, StyleSheet, Dimensions } from "react-native";
import Svg, { Rect, Text as SvgText, Line, Circle, Defs, LinearGradient, Stop } from "react-native-svg";
import { layoutDAG, getEdges } from "../utils/dagLayout";
import type { PipelineNode } from "../types/pipeline";

const NODE_WIDTH = 140;
const NODE_HEIGHT = 60;

const STATUS_COLORS: Record<string, string> = {
  PENDING: "#6b7280",
  RUNNING: "#3b82f6",
  COMPLETED: "#10b981",
  FAILED: "#ef4444",
  BLOCKED: "#f59e0b",
};

interface Props {
  nodes: PipelineNode[];
  onNodePress?: (nodeId: string) => void;
}

export function DAGGraph({ nodes, onNodePress }: Props) {
  const layoutNodes = layoutDAG(nodes);
  const edges = getEdges(layoutNodes);

  // Calculate SVG dimensions
  const maxX = Math.max(...layoutNodes.map((n) => n.x)) + NODE_WIDTH + 40;
  const maxY = Math.max(...layoutNodes.map((n) => n.y)) + NODE_HEIGHT + 40;

  return (
    <Svg width={maxX} height={maxY} viewBox={`0 0 ${maxX} ${maxY}`}>
      {/* Edges */}
      {edges.map((edge, i) => (
        <Line
          key={`edge-${i}`}
          x1={edge.from.x + NODE_WIDTH}
          y1={edge.from.y + NODE_HEIGHT / 2}
          x2={edge.to.x}
          y2={edge.to.y + NODE_HEIGHT / 2}
          stroke={STATUS_COLORS[edge.from.status]}
          strokeWidth={2}
          strokeDasharray={edge.from.status === "PENDING" ? "5,5" : undefined}
          opacity={0.6}
        />
      ))}

      {/* Nodes */}
      {layoutNodes.map((node) => (
        <View key={node.id}>
          <Rect
            x={node.x}
            y={node.y}
            width={NODE_WIDTH}
            height={NODE_HEIGHT}
            rx={8}
            fill="#1f2937"
            stroke={STATUS_COLORS[node.status]}
            strokeWidth={2}
            onPress={() => onNodePress?.(node.id)}
          />
          {/* Status indicator dot */}
          <Circle
            cx={node.x + 14}
            cy={node.y + NODE_HEIGHT / 2}
            r={5}
            fill={STATUS_COLORS[node.status]}
          />
          {/* Label */}
          <SvgText
            x={node.x + 26}
            y={node.y + NODE_HEIGHT / 2 - 6}
            fill="#f9fafb"
            fontSize={11}
            fontWeight="bold"
          >
            {node.label.length > 14 ? node.label.slice(0, 14) + "…" : node.label}
          </SvgText>
          {/* Status text */}
          <SvgText
            x={node.x + 26}
            y={node.y + NODE_HEIGHT / 2 + 10}
            fill={STATUS_COLORS[node.status]}
            fontSize={9}
          >
            {node.status}
          </SvgText>
        </View>
      ))}
    </Svg>
  );
}
```

## Pan & Zoom with Gestures

The DAG might be larger than the screen. Users need to pan and pinch-to-zoom:

```tsx
// src/screens/PipelineScreen.tsx
import { View, StyleSheet, ActivityIndicator, Text } from "react-native";
import { Gesture, GestureDetector, GestureHandlerRootView } from "react-native-gesture-handler";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withDecay,
} from "react-native-reanimated";
import { SafeAreaView } from "react-native-safe-area-context";
import { DAGGraph } from "../components/DAGGraph";
import { usePipeline } from "../hooks/usePipeline";

export function PipelineScreen() {
  const { data: pipeline, isLoading, error } = usePipeline();

  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);
  const scale = useSharedValue(1);
  const savedScale = useSharedValue(1);

  const panGesture = Gesture.Pan()
    .onUpdate((e) => {
      translateX.value += e.changeX;
      translateY.value += e.changeY;
    })
    .onEnd((e) => {
      // Momentum scrolling
      translateX.value = withDecay({ velocity: e.velocityX, deceleration: 0.997 });
      translateY.value = withDecay({ velocity: e.velocityY, deceleration: 0.997 });
    });

  const pinchGesture = Gesture.Pinch()
    .onUpdate((e) => {
      scale.value = savedScale.value * e.scale;
    })
    .onEnd(() => {
      // Clamp scale between 0.5x and 3x
      if (scale.value < 0.5) scale.value = 0.5;
      if (scale.value > 3) scale.value = 3;
      savedScale.value = scale.value;
    });

  const composed = Gesture.Simultaneous(panGesture, pinchGesture);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
      { scale: scale.value },
    ],
  }));

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  if (error || !pipeline) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Failed to load pipeline</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{pipeline.name}</Text>
        <Text style={styles.status}>{pipeline.status}</Text>
      </View>

      <GestureHandlerRootView style={styles.graphContainer}>
        <GestureDetector gesture={composed}>
          <Animated.View style={[styles.graph, animatedStyle]}>
            <DAGGraph nodes={pipeline.nodes} onNodePress={(id) => console.log("Node:", id)} />
          </Animated.View>
        </GestureDetector>
      </GestureHandlerRootView>

      {/* Legend */}
      <View style={styles.legend}>
        {Object.entries({ Running: "#3b82f6", Completed: "#10b981", Failed: "#ef4444", Blocked: "#f59e0b", Pending: "#6b7280" }).map(([label, color]) => (
          <View key={label} style={styles.legendItem}>
            <View style={[styles.legendDot, { backgroundColor: color }]} />
            <Text style={styles.legendText}>{label}</Text>
          </View>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827" },
  center: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 16, borderBottomWidth: 1, borderBottomColor: "#374151" },
  title: { color: "#f9fafb", fontSize: 18, fontWeight: "bold" },
  status: { color: "#3b82f6", fontSize: 14, fontWeight: "600" },
  graphContainer: { flex: 1, overflow: "hidden" },
  graph: { flex: 1 },
  errorText: { color: "#f87171", fontSize: 16 },
  legend: { flexDirection: "row", justifyContent: "center", gap: 16, padding: 12, borderTopWidth: 1, borderTopColor: "#374151" },
  legendItem: { flexDirection: "row", alignItems: "center", gap: 4 },
  legendDot: { width: 8, height: 8, borderRadius: 4 },
  legendText: { color: "#9ca3af", fontSize: 11 },
});
```

## Pipeline Hook

```tsx
// src/hooks/usePipeline.ts
import { useQuery } from "@tanstack/react-query";
import { API_URL } from "../services/config";
import { secureStorage } from "../services/secureStorage";
import type { Pipeline } from "../types/pipeline";

export function usePipeline() {
  return useQuery({
    queryKey: ["pipeline", "active"],
    queryFn: async (): Promise<Pipeline> => {
      const token = await secureStorage.getToken();
      const res = await fetch(`${API_URL}/pipelines/active`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
    refetchInterval: 5000, // Poll for pipeline updates
  });
}
```

## Mobile-Optimized: Vertical List Fallback

On very small screens (< 375px width), the graph is too cramped. Show a vertical list instead:

```tsx
// src/components/PipelineList.tsx
import { FlatList, View, Text, StyleSheet } from "react-native";
import { StatusBadge } from "./StatusBadge";
import type { PipelineNode } from "../types/pipeline";

export function PipelineList({ nodes }: { nodes: PipelineNode[] }) {
  // Sort by layer (topological order)
  const sorted = [...nodes].sort((a, b) => a.dependsOn.length - b.dependsOn.length);

  return (
    <FlatList
      data={sorted}
      keyExtractor={(item) => item.id}
      renderItem={({ item, index }) => (
        <View style={styles.item}>
          <View style={styles.connector}>
            {index > 0 && <View style={styles.line} />}
            <View style={[styles.dot, { backgroundColor: STATUS_COLORS[item.status] }]} />
            {index < sorted.length - 1 && <View style={styles.line} />}
          </View>
          <View style={styles.content}>
            <Text style={styles.label}>{item.label}</Text>
            <Text style={styles.type}>{item.type}</Text>
            <StatusBadge status={item.status as any} />
          </View>
        </View>
      )}
    />
  );
}

const STATUS_COLORS: Record<string, string> = {
  PENDING: "#6b7280", RUNNING: "#3b82f6", COMPLETED: "#10b981", FAILED: "#ef4444", BLOCKED: "#f59e0b",
};

const styles = StyleSheet.create({
  item: { flexDirection: "row", paddingHorizontal: 16 },
  connector: { width: 32, alignItems: "center" },
  line: { width: 2, flex: 1, backgroundColor: "#374151" },
  dot: { width: 12, height: 12, borderRadius: 6, marginVertical: 4 },
  content: { flex: 1, backgroundColor: "#1f2937", borderRadius: 8, padding: 12, marginVertical: 4, marginLeft: 8 },
  label: { color: "#f9fafb", fontSize: 14, fontWeight: "600" },
  type: { color: "#6b7280", fontSize: 12, marginTop: 2 },
});
```

Switch between views based on screen width:

```tsx
import { useWindowDimensions } from "react-native";

function PipelineView({ nodes }: { nodes: PipelineNode[] }) {
  const { width } = useWindowDimensions();

  if (width < 375) {
    return <PipelineList nodes={nodes} />;
  }

  return <DAGGraph nodes={nodes} />;
}
```

## Verify

1. Open the Pipeline tab → DAG renders with colored nodes and edges
2. Pinch to zoom in/out → smooth scaling between 0.5x and 3x
3. Pan around the graph → momentum scrolling with deceleration
4. Tap a node → shows job detail
5. Watch a running pipeline → nodes change color in real time
6. Rotate phone to landscape → more graph visible
7. On a small phone (iPhone SE) → falls back to vertical list view

Captain Deadline pinches to zoom into the blocked node. It's the PRICE_CALC step — the exchange rate API is down again. He taps it, sees the error, forwards it to Silent Bob. All from the back of a taxi.

"Now I need it to work on my iPad too. And show me charts."

Multiple screens and charts. Chapters 10 and 11.

---

[← Chapter 8: Authentication](chapter-08-authentication.md) | [Chapter 10: Multiple Screens →](chapter-10-responsive-screens.md)
