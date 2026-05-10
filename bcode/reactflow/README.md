# React Flow — From Nodes to Production Editors

A narrative-driven course on React Flow (xyflow). You're a frontend engineer at **PipelineHQ**, a startup building visual workflow editors — think Zapier, n8n, or Figma's prototyping mode. Users drag nodes, connect them with edges, and build automations visually.

## Episodes

| # | Title | The Feature | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, concepts, first flow |
| 01 | [Nodes and Edges](chapter-01-basics.md) | Static diagram | Node types, edge types, positioning |
| 02 | [Interactivity](chapter-02-interactive.md) | Drag, connect, delete | useNodesState, useEdgesState, onConnect |
| 03 | [Custom Nodes](chapter-03-custom-nodes.md) | Branded node components | NodeProps, handles, dynamic content |
| 04 | [Custom Edges](chapter-04-custom-edges.md) | Animated/labeled edges | EdgeProps, markers, path utils |
| 05 | [Layout](chapter-05-layout.md) | Auto-arrange nodes | Dagre, ELK, force-directed layouts |
| 06 | [Controls & Minimap](chapter-06-controls.md) | Navigation UI | MiniMap, Controls, Background, Panel |
| 07 | [State Management](chapter-07-state.md) | Complex flows | Zustand store, undo/redo, persistence |
| 08 | [Validation](chapter-08-validation.md) | Connection rules | isValidConnection, handle types, max connections |
| 09 | [Sub-flows & Groups](chapter-09-groups.md) | Nested workflows | Parent nodes, grouping, expandable |
| 10 | [Performance](chapter-10-performance.md) | 1000+ nodes | Virtualization, memoization, large graphs |
| 11 | [Export & Serialize](chapter-11-export.md) | Save/load/share | JSON serialization, image export, URL sharing |
| 12 | [Production Patterns](chapter-12-production.md) | Ship it | Toolbar, context menus, keyboard shortcuts, testing |

## Prerequisites

- React 18+ (hooks, functional components)
- TypeScript (recommended but not required)
- `npm install @xyflow/react`

## Philosophy

Every React Flow feature is introduced because users need it. You'll see the broken UX first — nodes that can't be moved, edges that connect to wrong handles, layouts that overlap — then learn the API that fixes it. The broken editor comes first. The polished editor follows.
