# Chapter 5: Layout

[← Chapter 4: Custom Edges](chapter-04-custom-edges.md) | [Chapter 6: Controls & Minimap →](chapter-06-controls.md)

---

## The Problem

Users add nodes and they pile up at position `{ x: 0, y: 0 }`. Kai files a bug: "When I add a new step, it lands on top of the previous one. Users shouldn't have to manually arrange 20 nodes into a readable flow." You need auto-layout — an algorithm that calculates positions from the graph structure.

## Dagre: Directed Graph Layout

Dagre is the go-to library for hierarchical graph layout. It takes nodes and edges, computes positions, and returns coordinates.

```bash
npm install @dagrejs/dagre
```

## The Layout Function

```tsx
import Dagre from '@dagrejs/dagre';
import { type Node, type Edge } from '@xyflow/react';

type Direction = 'TB' | 'LR' | 'BT' | 'RL';

function getLayoutedElements(
  nodes: Node[],
  edges: Edge[],
  direction: Direction = 'TB'
): { nodes: Node[]; edges: Edge[] } {
  const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

  g.setGraph({ rankdir: direction, nodesep: 50, ranksep: 80 });

  nodes.forEach((node) => {
    g.setNode(node.id, { width: 172, height: 36 });
  });

  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  Dagre.layout(g);

  const layoutedNodes = nodes.map((node) => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: { x: pos.x - 86, y: pos.y - 18 },
    };
  });

  return { nodes: layoutedNodes, edges };
}
```

## Full Example: Re-layout on Add/Remove

```tsx
import { ReactFlow, useNodesState, useEdgesState, addEdge, Panel, type OnConnect, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCallback, useState } from 'react';

const initialNodes: Node[] = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Start' }, type: 'input' },
  { id: '2', position: { x: 0, y: 0 }, data: { label: 'Validate' } },
  { id: '3', position: { x: 0, y: 0 }, data: { label: 'Transform' } },
  { id: '4', position: { x: 0, y: 0 }, data: { label: 'Send' }, type: 'output' },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
  { id: 'e3-4', source: '3', target: '4' },
];

export default function LayoutFlow() {
  const [direction, setDirection] = useState<Direction>('TB');
  const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
    initialNodes, initialEdges, direction
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  const onConnect: OnConnect = useCallback(
    (conn) => setEdges((eds) => addEdge(conn, eds)),
    [setEdges]
  );

  const onLayout = (dir: Direction) => {
    setDirection(dir);
    const { nodes: newNodes } = getLayoutedElements(nodes, edges, dir);
    setNodes(newNodes);
  };

  const addNode = () => {
    const id = `${nodes.length + 1}`;
    const newNode: Node = { id, position: { x: 0, y: 0 }, data: { label: `Step ${id}` } };
    const newEdge: Edge = { id: `e-${id}`, source: nodes[nodes.length - 1].id, target: id };
    const updated = getLayoutedElements([...nodes, newNode], [...edges, newEdge], direction);
    setNodes(updated.nodes);
    setEdges(updated.edges);
  };

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Panel position="top-left">
          <button onClick={() => onLayout('TB')}>↓ Top-Bottom</button>
          <button onClick={() => onLayout('LR')}>→ Left-Right</button>
          <button onClick={addNode}>+ Add Node</button>
        </Panel>
      </ReactFlow>
    </div>
  );
}
```

## Direction Options

| Value | Flow Direction | Use Case |
|---|---|---|
| `TB` | Top → Bottom | Vertical pipelines |
| `LR` | Left → Right | Horizontal timelines |
| `BT` | Bottom → Top | Dependency trees |
| `RL` | Right → Left | RTL layouts |

## What You Learned

- Dagre computes hierarchical positions from graph structure
- `getLayoutedElements` wraps dagre to return React Flow-compatible nodes
- Re-run layout after adding/removing nodes to keep the graph tidy
- `rankdir` controls flow direction (TB, LR, BT, RL)
- `nodesep` and `ranksep` control spacing between nodes

---

[Chapter 6: Controls & Minimap →](chapter-06-controls.md)
