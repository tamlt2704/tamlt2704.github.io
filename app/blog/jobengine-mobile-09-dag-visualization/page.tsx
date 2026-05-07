import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="DAG Visualization: The Pipeline on Your Palm"
            date="May 10, 2026"
            series="Job Engine Mobile"
            chapter={9}
            prevSlug="jobengine-mobile-08-authentication"
            prevTitle="Authentication"
            nextSlug="jobengine-mobile-10-responsive-screens"
            nextTitle="Multiple Screens"
        >
            <Section title="The Problem">
                <Paragraph>
                    Captain Deadline is in a taxi. He opens the app to check the nightly pipeline. On the web, React Flow renders a beautiful DAG. On mobile, the Pipeline tab says &quot;Coming soon.&quot; He needs to see which step is blocking the pipeline. Right now. From his phone.
                </Paragraph>
            </Section>

            <Section title="Layout Algorithm">
                <Paragraph>
                    A pipeline is a directed acyclic graph. We assign layers via topological sort, then position nodes within each layer:
                </Paragraph>
                <Code lang="tsx" title="src/utils/dagLayout.ts">{`export function layoutDAG(nodes: PipelineNode[]): LayoutNode[] {
  const layers = assignLayers(nodes); // Topological sort into columns
  return layers.flatMap((layerNodes, layerIndex) =>
    layerNodes.map((node, nodeIndex) => ({
      ...node,
      x: layerIndex * LAYER_GAP + 40,
      y: nodeIndex * NODE_GAP + 40,
    }))
  );
}

function assignLayers(nodes: PipelineNode[]): PipelineNode[][] {
  const layers: PipelineNode[][] = [];
  const assigned = new Set<string>();
  let currentLayer = nodes.filter((n) => n.dependsOn.length === 0);

  while (currentLayer.length > 0) {
    layers.push(currentLayer);
    currentLayer.forEach((n) => assigned.add(n.id));
    currentLayer = nodes.filter(
      (n) => !assigned.has(n.id) && n.dependsOn.every((dep) => assigned.has(dep))
    );
  }
  return layers;
}`}</Code>
            </Section>

            <Section title="SVG Rendering">
                <Code lang="bash">{`npx expo install react-native-svg`}</Code>
                <Paragraph>
                    Render nodes as rounded rectangles with status-colored borders, connected by lines. Each node shows a label, status dot, and status text.
                </Paragraph>
                <Code lang="tsx">{`import Svg, { Rect, Text as SvgText, Line, Circle } from "react-native-svg";

// Edges: lines connecting dependent nodes
{edges.map((edge) => (
  <Line x1={edge.from.x + NODE_WIDTH} y1={edge.from.y + NODE_HEIGHT / 2}
        x2={edge.to.x} y2={edge.to.y + NODE_HEIGHT / 2}
        stroke={STATUS_COLORS[edge.from.status]} strokeWidth={2} />
))}

// Nodes: colored rectangles with labels
{nodes.map((node) => (
  <Rect x={node.x} y={node.y} width={140} height={60} rx={8}
        fill="#1f2937" stroke={STATUS_COLORS[node.status]} strokeWidth={2} />
))}`}</Code>
            </Section>

            <Section title="Pan & Zoom">
                <Paragraph>
                    The DAG might be larger than the screen. Combine pan and pinch gestures for navigation:
                </Paragraph>
                <Code lang="tsx">{`const panGesture = Gesture.Pan()
  .onUpdate((e) => {
    translateX.value += e.changeX;
    translateY.value += e.changeY;
  })
  .onEnd((e) => {
    translateX.value = withDecay({ velocity: e.velocityX });
    translateY.value = withDecay({ velocity: e.velocityY });
  });

const pinchGesture = Gesture.Pinch()
  .onUpdate((e) => { scale.value = savedScale.value * e.scale; })
  .onEnd(() => {
    scale.value = Math.max(0.5, Math.min(3, scale.value));
    savedScale.value = scale.value;
  });

const composed = Gesture.Simultaneous(panGesture, pinchGesture);`}</Code>
            </Section>

            <Section title="Mobile Fallback: Vertical List">
                <Paragraph>
                    On very small screens (&lt; 375px), the graph is too cramped. Fall back to a vertical timeline list with connector dots and lines:
                </Paragraph>
                <Code lang="tsx">{`const { width } = useWindowDimensions();
if (width < 375) return <PipelineList nodes={nodes} />;
return <DAGGraph nodes={nodes} />;`}</Code>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Open the Pipeline tab → DAG renders with colored nodes and edges. Pinch to zoom. Pan around with momentum. Tap a node → job detail. Rotate to landscape → more graph visible. On iPhone SE → vertical list fallback.
                </Paragraph>
                <Paragraph>
                    Captain Deadline pinches to zoom into the blocked node. It&apos;s the PRICE_CALC step — the exchange rate API is down again. He taps it, sees the error, forwards it to Silent Bob. All from the back of a taxi.
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
