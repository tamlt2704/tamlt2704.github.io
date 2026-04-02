"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { sfxPop, sfxRemove, sfxZap } from "@/app/play/sfx";

type CellType = "empty" | "battery" | "bulb" | "wire_h" | "wire_v" | "wire_corner_tr" | "wire_corner_tl" | "wire_corner_br" | "wire_corner_bl";

const GRID = 6;
const CELL = 70;

const PARTS: { type: CellType; label: string; icon: string }[] = [
  { type: "battery", label: "Battery", icon: "🔋" },
  { type: "bulb", label: "Bulb", icon: "💡" },
  { type: "wire_h", label: "Wire ─", icon: "━" },
  { type: "wire_v", label: "Wire │", icon: "┃" },
  { type: "wire_corner_tr", label: "Corner ┐", icon: "┓" },
  { type: "wire_corner_tl", label: "Corner ┌", icon: "┏" },
  { type: "wire_corner_br", label: "Corner ┘", icon: "┛" },
  { type: "wire_corner_bl", label: "Corner └", icon: "┗" },
];

// Connection directions for each cell type
const CONNECTIONS: Record<CellType, ("top" | "bottom" | "left" | "right")[]> = {
  empty: [],
  battery: ["left", "right"],
  bulb: ["left", "right"],
  wire_h: ["left", "right"],
  wire_v: ["top", "bottom"],
  wire_corner_tr: ["top", "right"],
  wire_corner_tl: ["top", "left"],
  wire_corner_br: ["bottom", "right"],
  wire_corner_bl: ["bottom", "left"],
};

const OPPOSITE: Record<string, string> = { top: "bottom", bottom: "top", left: "right", right: "left" };

function makeGrid(): CellType[][] {
  return Array.from({ length: GRID }, () => Array(GRID).fill("empty"));
}

function checkCircuit(grid: CellType[][]): { complete: boolean; lit: Set<string> } {
  // Find battery
  let batR = -1, batC = -1;
  for (let r = 0; r < GRID; r++)
    for (let c = 0; c < GRID; c++)
      if (grid[r][c] === "battery") { batR = r; batC = c; }

  if (batR < 0) return { complete: false, lit: new Set() };

  // BFS from battery, follow connections
  const visited = new Set<string>();
  const queue: [number, number][] = [[batR, batC]];
  visited.add(`${batR},${batC}`);
  const DR: Record<string, [number, number]> = { top: [-1, 0], bottom: [1, 0], left: [0, -1], right: [0, 1] };

  while (queue.length) {
    const [r, c] = queue.shift()!;
    const cell = grid[r][c];
    for (const dir of CONNECTIONS[cell]) {
      const [dr, dc] = DR[dir];
      const nr = r + dr, nc = c + dc;
      if (nr < 0 || nr >= GRID || nc < 0 || nc >= GRID) continue;
      const key = `${nr},${nc}`;
      if (visited.has(key)) continue;
      const neighbor = grid[nr][nc];
      if (neighbor === "empty") continue;
      // Check neighbor connects back
      if (CONNECTIONS[neighbor].includes(OPPOSITE[dir] as "top" | "bottom" | "left" | "right")) {
        visited.add(key);
        queue.push([nr, nc]);
      }
    }
  }

  // Circuit is complete if battery is reachable from itself through a loop (visited has bulb and forms cycle)
  // Simpler: check if any bulb is in visited AND the path forms a loop back to battery
  const hasBulb = Array.from(visited).some(k => {
    const [r, c] = k.split(",").map(Number);
    return grid[r][c] === "bulb";
  });

  // Check loop: battery must have 2 connected visited neighbors
  let batConnected = 0;
  for (const dir of CONNECTIONS.battery) {
    const [dr, dc] = DR[dir];
    const nr = batR + dr, nc = batC + dc;
    if (nr < 0 || nr >= GRID || nc < 0 || nc >= GRID) continue;
    const key = `${nr},${nc}`;
    if (visited.has(key) && CONNECTIONS[grid[nr][nc]].includes(OPPOSITE[dir] as "top" | "bottom" | "left" | "right")) {
      batConnected++;
    }
  }

  const complete = hasBulb && batConnected >= 2;
  return { complete, lit: complete ? visited : new Set() };
}

// Preset puzzles
const PRESETS = [
  { name: "Simple Loop", grid: (() => { const g = makeGrid(); g[2][1] = "battery"; g[2][2] = "wire_h"; g[2][3] = "wire_h"; g[2][4] = "bulb"; return g; })(), hint: "Connect the bulb back to the battery using wires!" },
  { name: "Blank Canvas", grid: makeGrid(), hint: "Build your own circuit from scratch!" },
];

export default function CircuitsPage() {
  const [grid, setGrid] = useState<CellType[][]>(makeGrid);
  const [selected, setSelected] = useState<CellType>("wire_h");
  const [hint, setHint] = useState("Place a battery, bulb, and connect them in a loop!");
  const wasComplete = useRef(false);

  const { complete, lit } = checkCircuit(grid);

  useEffect(() => {
    if (complete && !wasComplete.current) sfxZap();
    wasComplete.current = complete;
  }, [complete]);

  const placeCell = (r: number, c: number) => {
    setGrid(prev => {
      const g = prev.map(row => [...row]);
      const removing = g[r][c] === selected;
      g[r][c] = removing ? "empty" : selected;
      removing ? sfxRemove() : sfxPop();
      return g;
    });
  };

  const loadPreset = (idx: number) => {
    setGrid(PRESETS[idx].grid.map(r => [...r]));
    setHint(PRESETS[idx].hint);
  };

  const cellIcon = (type: CellType, isLit: boolean) => {
    const part = PARTS.find(p => p.type === type);
    if (!part) return "";
    if (type === "bulb" && isLit) return "⭐";
    return part.icon;
  };

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>⚡ Simple Circuits</h1>
        {complete && <span style={{ color: "#22c55e", fontWeight: 700, fontSize: 16 }}>💡 Circuit Complete!</span>}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px" }}>
        {/* Grid */}
        <div style={{
          display: "grid", gridTemplateColumns: `repeat(${GRID}, ${CELL}px)`,
          gap: 2, background: "#111827", borderRadius: 12, border: "1px solid #333", padding: 12,
        }}>
          {grid.flatMap((row, r) =>
            row.map((cell, c) => {
              const key = `${r},${c}`;
              const isLit = lit.has(key);
              return (
                <div
                  key={key}
                  onClick={() => placeCell(r, c)}
                  style={{
                    width: CELL, height: CELL, borderRadius: 6,
                    background: isLit ? "#22c55e18" : "#1a1a2e",
                    border: isLit ? "1px solid #22c55e44" : "1px solid #333",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: cell === "bulb" && isLit ? 32 : 24,
                    cursor: "pointer", userSelect: "none",
                    transition: "background 0.2s",
                    boxShadow: cell === "bulb" && isLit ? "0 0 20px #fbbf24" : "none",
                  }}
                >
                  {cellIcon(cell, isLit)}
                </div>
              );
            })
          )}
        </div>

        {/* Controls */}
        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 200 }}>
          <div style={{ fontSize: 13, color: "#888", marginBottom: 10 }}>Select a part, then click the grid:</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 }}>
            {PARTS.map(p => (
              <div
                key={p.type}
                onClick={() => setSelected(p.type)}
                style={{
                  padding: "6px 10px", borderRadius: 6, cursor: "pointer", fontSize: 13,
                  background: selected === p.type ? "#3b82f6" : "#0a0a1a",
                  border: selected === p.type ? "1px solid #3b82f6" : "1px solid #444",
                  display: "flex", gap: 8, alignItems: "center",
                }}
              >
                <span style={{ fontSize: 18 }}>{p.icon}</span> {p.label}
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
            {PRESETS.map((p, i) => (
              <button key={i} onClick={() => loadPreset(i)} style={btn}>{p.name}</button>
            ))}
            <button onClick={() => { setGrid(makeGrid()); setHint("Build your own circuit!"); }} style={btn}>🗑 Clear</button>
          </div>

          <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.7 }}>
            <p style={{ margin: "0 0 8px" }}>⚡ <b>Electricity flows in a loop!</b></p>
            <p style={{ margin: "0 0 4px" }}>{hint}</p>
            <p style={{ margin: 0, color: "#666" }}>Click a placed part again to remove it.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = {
  padding: "6px 14px", borderRadius: 6, border: "1px solid #555",
  background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13,
};
