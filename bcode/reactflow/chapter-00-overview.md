# Chapter 0: Before You Start

[Chapter 1: Nodes and Edges →](chapter-01-basics.md)

---

## The Story

You're a frontend engineer at **PipelineHQ**, building a visual workflow editor. Users create automations by dragging nodes (triggers, actions, conditions) and connecting them with edges. Think: "When a form is submitted → validate data → send email → update CRM."

Your PM, **Kai**, shows you the mockup: "Users need to build flows visually. Drag nodes from a sidebar, connect them, configure each step. It needs to feel like Figma — smooth, intuitive, infinite canvas."

React Flow (now `@xyflow/react`) is the library that makes this possible.

## What Is React Flow?

React Flow is a React library for building node-based editors and interactive diagrams. It gives you:

- An infinite, pannable, zoomable canvas
- Draggable nodes with connection handles
- Edges (lines) between nodes
- Built-in interactions (select, drag, connect, delete)
- Extensibility (custom nodes, custom edges, plugins)

Used by: Stripe (workflow builder), Vercel (AI SDK playground), n8n, Langflow, and hundreds of startups.

## Setup

```bash
npm install @xyflow/react
```

## Your First Flow (30 seconds)

```tsx
import { ReactFlow, Background } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodes = [
  { id: '1', position: { x: 100, y: 100 }, data: { label: 'Start' } },
  { id: '2', position: { x: 300, y: 200 }, data: { label: 'Process' } },
];

const edges = [
  { id: 'e1-2', source: '1', target: '2' },
];

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow nodes={nodes} edges={edges}>
        <Background />
      </ReactFlow>
    </div>
  );
}
```

That's it. Two nodes connected by an edge on an infinite canvas. Pan with mouse drag, zoom with scroll.

## Core Concepts

```
┌─────────────────────────────────────────────────────┐
│  ReactFlow (the canvas)                              │
│                                                      │
│   ┌──────────┐         ┌──────────┐                │
│   │  Node 1  │────────→│  Node 2  │                │
│   │  (Start) │  Edge   │ (Action) │                │
│   └──────────┘         └──────────┘                │
│        ↑                                            │
│     Handle                                          │
│   (connection point)                                │
│                                                      │
│   [Background] [MiniMap] [Controls]                 │
└─────────────────────────────────────────────────────┘
```

| Concept | What It Is |
|---|---|
| **Node** | A box on the canvas (React component) |
| **Edge** | A line connecting two nodes |
| **Handle** | A connection point on a node (source or target) |
| **Viewport** | The visible area (pan/zoom state) |
| **Background** | Grid/dots behind the flow |
| **MiniMap** | Thumbnail overview for navigation |
| **Controls** | Zoom in/out/fit buttons |

## Node Anatomy

```tsx
{
  id: 'unique-id',           // Required: unique identifier
  type: 'default',           // Optional: 'default', 'input', 'output', or custom
  position: { x: 0, y: 0 }, // Required: position on canvas
  data: { label: 'Hello' },  // Required: passed to the node component
  draggable: true,           // Optional: can user drag it?
  selectable: true,          // Optional: can user select it?
  deletable: true,           // Optional: can user delete it?
}
```

## Edge Anatomy

```tsx
{
  id: 'edge-1',              // Required: unique identifier
  source: 'node-1',         // Required: source node id
  target: 'node-2',         // Required: target node id
  sourceHandle: 'output-a', // Optional: specific handle on source
  targetHandle: 'input-b',  // Optional: specific handle on target
  type: 'default',          // Optional: 'default', 'straight', 'step', 'smoothstep'
  animated: false,           // Optional: dashed animation
  label: 'connects to',     // Optional: text on the edge
}
```

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Frontend Engineer | Builds the visual editor |
| **Kai** | Product Manager | "Make it feel like Figma" |
| **Users** | Non-technical | Build workflows by dragging |
| **The Canvas** | React Flow | Infinite, smooth, extensible |

## The Roadmap

| Ch | The UX Problem | The React Flow Solution |
|---|---|---|
| 1 | Need a static diagram | Nodes, edges, built-in types |
| 2 | Users can't interact | Drag, connect, delete handlers |
| 3 | Nodes look generic | Custom node components |
| 4 | Edges are boring | Custom edges with labels/animations |
| 5 | Nodes overlap | Auto-layout algorithms |
| 6 | Users get lost on large flows | MiniMap, controls, background |
| 7 | State is messy | Zustand store, undo/redo |
| 8 | Invalid connections | Validation rules |
| 9 | Flows are flat | Sub-flows, grouping |
| 10 | Slow with many nodes | Performance optimization |
| 11 | Can't save/share | Serialization, export |
| 12 | Missing polish | Toolbar, shortcuts, context menus |

## Important: The Container Needs a Size

React Flow fills its parent container. If the parent has no height, you see nothing:

```tsx
// ❌ WRONG: no height
<div>
  <ReactFlow nodes={nodes} edges={edges} />
</div>

// ✅ RIGHT: explicit height
<div style={{ width: '100%', height: '100vh' }}>
  <ReactFlow nodes={nodes} edges={edges} />
</div>
```

## Import the CSS

Always import the styles or nothing renders correctly:

```tsx
import '@xyflow/react/dist/style.css';
```

Let's build our first real flow.

---

[Chapter 1: Nodes and Edges →](chapter-01-basics.md)
