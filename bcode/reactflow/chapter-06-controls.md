# Chapter 6: Controls & Minimap

[← Chapter 5: Layout](chapter-05-layout.md) | [Chapter 7: State Management →](chapter-07-state.md)

---

## The Problem

A user builds a 40-node workflow, zooms into one corner, then panics: "Where am I? How do I get back to the full view?" Kai adds to the backlog: "We need a minimap like Figma, zoom buttons for trackpad-less users, and a grid background so the canvas doesn't feel like a void."

## The Plugin Components

React Flow ships four UI plugins:

| Component | Purpose |
|---|---|
| `MiniMap` | Thumbnail overview, click to navigate |
| `Controls` | Zoom in/out/fit buttons |
| `Background` | Dots, lines, or cross pattern |
| `Panel` | Positioned container for custom UI |

## Full Example

```tsx
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  Panel,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodes: Node[] = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Trigger' }, type: 'input' },
  { id: '2', position: { x: 200, y: 100 }, data: { label: 'Action A' } },
  { id: '3', position: { x: 400, y: 0 }, data: { label: 'Action B' } },
  { id: '4', position: { x: 600, y: 100 }, data: { label: 'Output' }, type: 'output' },
];

const edges: Edge[] = [
  { id: 'e1', source: '1', target: '2' },
  { id: 'e2', source: '1', target: '3' },
  { id: 'e3', source: '2', target: '4' },
  { id: 'e4', source: '3', target: '4' },
];

function Flow() {
  const [nds, , onNodesChange] = useNodesState(nodes);
  const [eds, , onEdgesChange] = useEdgesState(edges);
  const { fitView, setCenter, zoomTo } = useReactFlow();

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nds}
        edges={eds}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#ddd" />

        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'input') return '#3b82f6';
            if (node.type === 'output') return '#22c55e';
            return '#94a3b8';
          }}
          nodeStrokeWidth={3}
          zoomable
          pannable
        />

        <Controls showInteractive={false} />

        <Panel position="top-right">
          <div style={{ display: 'flex', gap: 4 }}>
            <button onClick={() => fitView({ padding: 0.2, duration: 300 })}>
              Fit All
            </button>
            <button onClick={() => setCenter(300, 50, { zoom: 1.5, duration: 300 })}>
              Focus Center
            </button>
            <button onClick={() => zoomTo(1, { duration: 300 })}>
              Reset Zoom
            </button>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}

export default function ControlsFlow() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
```

## Background Variants

```tsx
<Background variant={BackgroundVariant.Dots} />   // Dot grid (default)
<Background variant={BackgroundVariant.Lines} />   // Line grid
<Background variant={BackgroundVariant.Cross} />   // Cross pattern
```

## Viewport Manipulation

`useReactFlow()` exposes viewport controls (must be inside `ReactFlowProvider`):

| Method | What It Does |
|---|---|
| `fitView(options?)` | Zoom/pan to show all nodes |
| `setCenter(x, y, options?)` | Center viewport on coordinates |
| `zoomTo(level, options?)` | Set zoom level (1 = 100%) |
| `zoomIn() / zoomOut()` | Step zoom in/out |
| `getViewport()` | Returns `{ x, y, zoom }` |
| `setViewport({ x, y, zoom })` | Set viewport directly |

## Panel Positions

```tsx
<Panel position="top-left">...</Panel>
<Panel position="top-center">...</Panel>
<Panel position="top-right">...</Panel>
<Panel position="bottom-left">...</Panel>
<Panel position="bottom-center">...</Panel>
<Panel position="bottom-right">...</Panel>
```

## What You Learned

- `MiniMap` gives users a bird's-eye view with click-to-navigate
- `Controls` adds zoom buttons for users without scroll wheels
- `Background` variants (dots, lines, cross) make the canvas feel grounded
- `Panel` positions custom UI overlays at fixed screen positions
- `useReactFlow()` provides `fitView`, `setCenter`, `zoomTo` for programmatic viewport control
- Wrap your flow in `ReactFlowProvider` to use `useReactFlow()` inside child components

---

[Chapter 7: State Management →](chapter-07-state.md)
