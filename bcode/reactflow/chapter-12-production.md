# Chapter 12: Production Patterns

[← Chapter 11: Export & Serialize](chapter-11-export.md) | [README →](README.md)

---

## The Problem

The editor works, but it doesn't feel professional. Users ask: "Where's the toolbar? Can I right-click? Why doesn't Ctrl+Z work? Can I copy-paste nodes?" Kai's final push: "Make it feel like a real app — not a demo." Time to add the production polish.

## Drag-from-Sidebar (Node Palette)

```tsx
import { type DragEvent } from 'react';

function Sidebar() {
  const onDragStart = (event: DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside style={{ width: 200, padding: 16, borderRight: '1px solid #eee' }}>
      <h3>Nodes</h3>
      <div
        draggable
        onDragStart={(e) => onDragStart(e, 'action')}
        style={{ padding: 8, border: '1px solid #ccc', borderRadius: 4, marginBottom: 8, cursor: 'grab' }}
      >
        ⚙️ Action
      </div>
      <div
        draggable
        onDragStart={(e) => onDragStart(e, 'condition')}
        style={{ padding: 8, border: '1px solid #ccc', borderRadius: 4, cursor: 'grab' }}
      >
        🔀 Condition
      </div>
    </aside>
  );
}
```

Handle the drop on the canvas:

```tsx
import { useReactFlow, type Node } from '@xyflow/react';
import { useCallback, type DragEvent } from 'react';

function useDropHandler() {
  const { screenToFlowPosition, setNodes } = useReactFlow();

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback((event: DragEvent) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');
    if (!type) return;

    const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
    const newNode: Node = {
      id: `${Date.now()}`,
      type,
      position,
      data: { label: `${type} node` },
    };

    setNodes((nds) => [...nds, newNode]);
  }, [screenToFlowPosition, setNodes]);

  return { onDragOver, onDrop };
}
```

## Context Menu (Right-Click)

```tsx
import { useState, useCallback } from 'react';
import { useReactFlow, type Node } from '@xyflow/react';

type MenuPos = { x: number; y: number; nodeId?: string } | null;

function useContextMenu() {
  const [menu, setMenu] = useState<MenuPos>(null);
  const { setNodes, setEdges } = useReactFlow();

  const onNodeContextMenu = useCallback((event: React.MouseEvent, node: Node) => {
    event.preventDefault();
    setMenu({ x: event.clientX, y: event.clientY, nodeId: node.id });
  }, []);

  const onPaneClick = useCallback(() => setMenu(null), []);

  const deleteNode = () => {
    if (!menu?.nodeId) return;
    setNodes((nds) => nds.filter((n) => n.id !== menu.nodeId));
    setEdges((eds) => eds.filter((e) => e.source !== menu.nodeId && e.target !== menu.nodeId));
    setMenu(null);
  };

  const duplicateNode = () => {
    if (!menu?.nodeId) return;
    setNodes((nds) => {
      const original = nds.find((n) => n.id === menu.nodeId);
      if (!original) return nds;
      const copy: Node = {
        ...original,
        id: `${Date.now()}`,
        position: { x: original.position.x + 50, y: original.position.y + 50 },
      };
      return [...nds, copy];
    });
    setMenu(null);
  };

  const ContextMenu = () =>
    menu ? (
      <div style={{
        position: 'absolute', left: menu.x, top: menu.y, zIndex: 1000,
        background: 'white', border: '1px solid #ddd', borderRadius: 6,
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)', padding: 4,
      }}>
        <button onClick={duplicateNode} style={{ display: 'block', width: '100%', padding: '6px 12px', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left' }}>📋 Duplicate</button>
        <button onClick={deleteNode} style={{ display: 'block', width: '100%', padding: '6px 12px', border: 'none', background: 'none', cursor: 'pointer', textAlign: 'left', color: '#ef4444' }}>🗑️ Delete</button>
      </div>
    ) : null;

  return { onNodeContextMenu, onPaneClick, ContextMenu };
}
```

## Keyboard Shortcuts

```tsx
import { useEffect, useCallback } from 'react';
import { useReactFlow, type Node } from '@xyflow/react';

function useKeyboardShortcuts() {
  const { getNodes, setNodes, setEdges } = useReactFlow();

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const selected = getNodes().filter((n) => n.selected);

    // Delete selected nodes
    if (event.key === 'Delete' || event.key === 'Backspace') {
      const ids = new Set(selected.map((n) => n.id));
      setNodes((nds) => nds.filter((n) => !ids.has(n.id)));
      setEdges((eds) => eds.filter((e) => !ids.has(e.source) && !ids.has(e.target)));
    }

    // Copy (Ctrl+C)
    if (event.key === 'c' && (event.ctrlKey || event.metaKey)) {
      sessionStorage.setItem('clipboard', JSON.stringify(selected));
    }

    // Paste (Ctrl+V)
    if (event.key === 'v' && (event.ctrlKey || event.metaKey)) {
      const clipboard = sessionStorage.getItem('clipboard');
      if (!clipboard) return;
      const copied: Node[] = JSON.parse(clipboard);
      const pasted = copied.map((n) => ({
        ...n,
        id: `${n.id}-copy-${Date.now()}`,
        position: { x: n.position.x + 50, y: n.position.y + 50 },
        selected: false,
      }));
      setNodes((nds) => [...nds, ...pasted]);
    }
  }, [getNodes, setNodes, setEdges]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
```

## Testing with React Testing Library

```tsx
import { render, screen } from '@testing-library/react';
import { ReactFlow, ReactFlowProvider, type Node, type Edge } from '@xyflow/react';

const nodes: Node[] = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Test Node' } },
];
const edges: Edge[] = [];

function TestFlow() {
  return (
    <ReactFlowProvider>
      <div style={{ width: 500, height: 500 }}>
        <ReactFlow nodes={nodes} edges={edges} />
      </div>
    </ReactFlowProvider>
  );
}

test('renders nodes', () => {
  render(<TestFlow />);
  expect(screen.getByText('Test Node')).toBeInTheDocument();
});

test('renders correct number of nodes', () => {
  render(<TestFlow />);
  const nodeElements = document.querySelectorAll('.react-flow__node');
  expect(nodeElements).toHaveLength(1);
});
```

## What You Learned

- Drag-from-sidebar uses HTML5 drag events + `screenToFlowPosition` for placement
- Context menus use `onNodeContextMenu` to capture right-clicks
- Keyboard shortcuts listen on `document` and operate on `selected` nodes
- Copy/paste serializes selected nodes to `sessionStorage`
- React Testing Library can render flows inside `ReactFlowProvider` with a sized container
- These patterns together make the editor feel like a professional tool

---

[README →](README.md)
