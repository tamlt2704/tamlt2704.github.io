"use client";

import { useState } from "react";
import Link from "next/link";
import { sfxPlace, sfxRemove } from "@/app/play/sfx";

const GRID = 12;
const CELL = 40;
const W = GRID * CELL;

type Shape = { type: "triangle" | "square" | "circle"; x: number; y: number; color: string; id: number };

const SHAPE_DEFS = [
  { type: "triangle" as const, label: "△ Triangle", color: "#ef4444", area: 0.5, sides: 3 },
  { type: "square" as const, label: "□ Square", color: "#3b82f6", area: 1, sides: 4 },
  { type: "circle" as const, label: "○ Circle", color: "#22c55e", area: Math.PI / 4, sides: 0 },
];

let nextId = 1;

export default function ShapesPage() {
  const [shapes, setShapes] = useState<Shape[]>([]);
  const [selected, setSelected] = useState<"triangle" | "square" | "circle">("square");
  const [showGrid, setShowGrid] = useState(true);

  const totalArea = shapes.reduce((sum, s) => {
    const def = SHAPE_DEFS.find(d => d.type === s.type)!;
    return sum + def.area;
  }, 0);

  const totalPerimeter = shapes.reduce((sum, s) => {
    if (s.type === "square") return sum + 4;
    if (s.type === "triangle") return sum + (1 + 1 + Math.SQRT2);
    return sum + Math.PI;
  }, 0);

  const placeShape = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const gx = Math.floor(mx / CELL);
    const gy = Math.floor(my / CELL);
    if (gx < 0 || gx >= GRID || gy < 0 || gy >= GRID) return;

    // Check if shape already at this cell — remove it
    const existing = shapes.findIndex(s => s.x === gx && s.y === gy);
    if (existing >= 0) {
      sfxRemove();
      setShapes(prev => prev.filter((_, i) => i !== existing));
      return;
    }

    sfxPlace();
    const def = SHAPE_DEFS.find(d => d.type === selected)!;
    setShapes(prev => [...prev, { type: selected, x: gx, y: gy, color: def.color, id: nextId++ }]);
  };

  const renderShape = (s: Shape) => {
    const px = s.x * CELL;
    const py = s.y * CELL;
    if (s.type === "square") {
      return <rect key={s.id} x={px + 2} y={py + 2} width={CELL - 4} height={CELL - 4} rx={2} fill={s.color} opacity={0.8} style={{ cursor: "pointer" }} />;
    }
    if (s.type === "triangle") {
      return <polygon key={s.id} points={`${px + CELL / 2},${py + 3} ${px + 3},${py + CELL - 3} ${px + CELL - 3},${py + CELL - 3}`} fill={s.color} opacity={0.8} style={{ cursor: "pointer" }} />;
    }
    return <circle key={s.id} cx={px + CELL / 2} cy={py + CELL / 2} r={CELL / 2 - 3} fill={s.color} opacity={0.8} style={{ cursor: "pointer" }} />;
  };

  const counts = SHAPE_DEFS.map(d => ({ ...d, count: shapes.filter(s => s.type === d.type).length }));

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🔷 Shape Builder</h1>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px" }}>
        <svg width={W} height={W} onClick={placeShape} style={{ background: "#111827", borderRadius: 12, border: "1px solid #333", cursor: "crosshair" }}>
          {/* Grid */}
          {showGrid && Array.from({ length: GRID + 1 }, (_, i) => (
            <g key={i}>
              <line x1={i * CELL} y1={0} x2={i * CELL} y2={W} stroke="#ffffff0d" strokeWidth={1} />
              <line x1={0} y1={i * CELL} x2={W} y2={i * CELL} stroke="#ffffff0d" strokeWidth={1} />
            </g>
          ))}
          {shapes.map(renderShape)}
        </svg>

        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 220 }}>
          <div style={{ fontSize: 13, color: "#888", marginBottom: 10 }}>Select a shape:</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 }}>
            {SHAPE_DEFS.map(d => (
              <div
                key={d.type}
                onClick={() => setSelected(d.type)}
                style={{
                  padding: "8px 12px", borderRadius: 6, cursor: "pointer", fontSize: 13,
                  background: selected === d.type ? d.color + "33" : "#0a0a1a",
                  border: selected === d.type ? `1px solid ${d.color}` : "1px solid #444",
                  color: selected === d.type ? d.color : "#ccc",
                }}
              >
                {d.label}
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
            <button onClick={() => setShapes([])} style={btn}>🗑 Clear</button>
            <button onClick={() => setShowGrid(!showGrid)} style={btn}>{showGrid ? "Hide Grid" : "Show Grid"}</button>
          </div>

          {/* Stats */}
          <div style={{ padding: "10px 12px", background: "#0a0a1a", borderRadius: 8, fontSize: 12, lineHeight: 1.8, marginBottom: 12 }}>
            <div style={{ color: "#888", marginBottom: 4 }}>Stats (1 cell = 1 unit²):</div>
            {counts.map(c => c.count > 0 && (
              <div key={c.type} style={{ color: c.color }}>{c.label}: <b>{c.count}</b></div>
            ))}
            <div style={{ marginTop: 4 }}>Total Area: <b style={{ color: "#4da6ff" }}>{totalArea.toFixed(2)} units²</b></div>
            <div>Total Perimeter: <b style={{ color: "#f59e0b" }}>{totalPerimeter.toFixed(2)} units</b></div>
          </div>

          <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.7 }}>
            <p style={{ margin: 0 }}>🔷 Click the grid to place shapes. Click a shape to remove it. Watch the area and perimeter change!</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
