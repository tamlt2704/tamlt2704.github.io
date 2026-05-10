# Chapter 11: Export & Serialize

[← Chapter 10: Performance](chapter-10-performance.md) | [Chapter 12: Production Patterns →](chapter-12-production.md)

---

## The Problem

Users build a workflow, close the tab, and it's gone. Kai's feature request: "Save to backend, export as image for docs, and share via link — like a Google Docs share URL." You need serialization (JSON), image export (PNG/SVG), and URL-based sharing.

## Serialize to JSON

Nodes and edges are plain objects — `JSON.stringify` just works:

```tsx
import { useReactFlow } from '@xyflow/react';

function SaveLoadPanel() {
  const { getNodes, getEdges, setNodes, setEdges } = useReactFlow();

  const onSave = () => {
    const flow = { nodes: getNodes(), edges: getEdges() };
    const json = JSON.stringify(flow, null, 2);
    localStorage.setItem('pipeline-flow', json);
    console.log('Saved', flow.nodes.length, 'nodes');
  };

  const onLoad = () => {
    const saved = localStorage.getItem('pipeline-flow');
    if (!saved) return;
    const { nodes, edges } = JSON.parse(saved);
    setNodes(nodes);
    setEdges(edges);
  };

  const onDownload = () => {
    const flow = { nodes: getNodes(), edges: getEdges() };
    const blob = new Blob([JSON.stringify(flow, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'workflow.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: 'flex', gap: 4 }}>
      <button onClick={onSave}>💾 Save</button>
      <button onClick={onLoad}>📂 Load</button>
      <button onClick={onDownload}>⬇️ Download JSON</button>
    </div>
  );
}
```

## Export to PNG/SVG with html-to-image

```bash
npm install html-to-image
```

```tsx
import { toPng, toSvg } from 'html-to-image';
import { useReactFlow, getNodesBounds, getViewportForBounds } from '@xyflow/react';

function ExportButton() {
  const { getNodes } = useReactFlow();

  const exportImage = (format: 'png' | 'svg') => {
    const nodesBounds = getNodesBounds(getNodes());
    const imageWidth = 1024;
    const imageHeight = 768;
    const viewport = getViewportForBounds(nodesBounds, imageWidth, imageHeight, 0.5, 2, 0.1);

    const element = document.querySelector('.react-flow__viewport') as HTMLElement;
    if (!element) return;

    const options = {
      backgroundColor: '#ffffff',
      width: imageWidth,
      height: imageHeight,
      style: {
        width: `${imageWidth}px`,
        height: `${imageHeight}px`,
        transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.zoom})`,
      },
    };

    const exportFn = format === 'png' ? toPng : toSvg;

    exportFn(element, options).then((dataUrl) => {
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = `workflow.${format}`;
      a.click();
    });
  };

  return (
    <div>
      <button onClick={() => exportImage('png')}>📷 Export PNG</button>
      <button onClick={() => exportImage('svg')}>🖼️ Export SVG</button>
    </div>
  );
}
```

## Share via URL (Compressed State)

Encode the flow state into a URL for sharing:

```tsx
import { useReactFlow } from '@xyflow/react';

function ShareButton() {
  const { getNodes, getEdges, setNodes, setEdges } = useReactFlow();

  const share = () => {
    const flow = { nodes: getNodes(), edges: getEdges() };
    const json = JSON.stringify(flow);
    const compressed = btoa(encodeURIComponent(json));
    const url = `${window.location.origin}${window.location.pathname}?flow=${compressed}`;
    navigator.clipboard.writeText(url);
    alert('Link copied!');
  };

  const loadFromURL = () => {
    const params = new URLSearchParams(window.location.search);
    const encoded = params.get('flow');
    if (!encoded) return;
    try {
      const json = decodeURIComponent(atob(encoded));
      const { nodes, edges } = JSON.parse(json);
      setNodes(nodes);
      setEdges(edges);
    } catch (e) {
      console.error('Invalid flow URL');
    }
  };

  return <button onClick={share}>🔗 Copy Share Link</button>;
}
```

## Full Example

```tsx
import { ReactFlow, ReactFlowProvider, useNodesState, useEdgesState, Panel, Background, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 100, y: 0 }, data: { label: 'Start' }, type: 'input' },
  { id: '2', position: { x: 100, y: 120 }, data: { label: 'Process' } },
  { id: '3', position: { x: 100, y: 240 }, data: { label: 'End' }, type: 'output' },
];
const initialEdges: Edge[] = [
  { id: 'e1', source: '1', target: '2' },
  { id: 'e2', source: '2', target: '3' },
];

function Flow() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Panel position="top-left">
          <SaveLoadPanel />
          <ExportButton />
          <ShareButton />
        </Panel>
      </ReactFlow>
    </div>
  );
}

export default function App() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
```

## What You Learned

- `getNodes()` / `getEdges()` from `useReactFlow()` return current state for serialization
- `setNodes()` / `setEdges()` restore a flow from JSON
- `html-to-image` captures the viewport element as PNG or SVG
- `getNodesBounds` + `getViewportForBounds` compute the right transform for image export
- `btoa`/`atob` with `encodeURIComponent` compresses flow state into shareable URLs

---

[Chapter 12: Production Patterns →](chapter-12-production.md)
