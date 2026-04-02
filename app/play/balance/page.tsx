"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import Link from "next/link";
import { sfxPop, sfxRemove, sfxFanfare } from "@/app/play/sfx";

type Weight = { mass: number; pos: number; id: number };

const BEAM_W = 600;
const BEAM_H = 12;
const PIVOT_X = 300;
const PIVOT_Y = 220;
const ARM = 260; // half-beam in px
const SLOT_COUNT = 10; // slots per side (-10 to +10)
const SLOT_SPACING = ARM / SLOT_COUNT;
const WEIGHT_MASSES = [1, 2, 3, 5];
const COLORS = ["#f59e0b", "#3b82f6", "#ef4444", "#8b5cf6"];

function torque(weights: Weight[]) {
  return weights.reduce((sum, w) => sum + w.mass * w.pos, 0);
}

function clampAngle(t: number) {
  return Math.max(-25, Math.min(25, t * 3));
}

let nextId = 1;

export default function BalancePage() {
  const [weights, setWeights] = useState<Weight[]>([]);
  const [dragging, setDragging] = useState<{ mass: number } | null>(null);
  const wasBalanced = useRef(false);

  const t = torque(weights);
  const angleDeg = clampAngle(t);
  const balanced = Math.abs(t) < 0.01 && weights.length >= 2;

  useEffect(() => {
    if (balanced && !wasBalanced.current) sfxFanfare();
    wasBalanced.current = balanced;
  }, [balanced]);

  const slotX = (pos: number) => PIVOT_X + pos * SLOT_SPACING;

  const handleDrop = useCallback(
    (e: React.MouseEvent<SVGSVGElement>) => {
      if (!dragging) return;
      const svg = e.currentTarget.getBoundingClientRect();
      const x = e.clientX - svg.left;
      // Find nearest slot
      let best = 0, bestDist = Infinity;
      for (let s = -SLOT_COUNT; s <= SLOT_COUNT; s++) {
        if (s === 0) continue;
        const d = Math.abs(slotX(s) - x);
        if (d < bestDist) { bestDist = d; best = s; }
      }
      if (bestDist < SLOT_SPACING) {
        sfxPop();
        setWeights(prev => [...prev, { mass: dragging.mass, pos: best, id: nextId++ }]);
      }
      setDragging(null);
    },
    [dragging]
  );

  const removeWeight = (id: number) => { sfxRemove(); setWeights(prev => prev.filter(w => w.id !== id)); };

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>⚖️ Balance Scale</h1>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px" }}>
        {/* SVG scene */}
        <svg
          width={BEAM_W} height={340}
          style={{ background: "#111827", borderRadius: 12, border: "1px solid #333", cursor: dragging ? "grabbing" : "default" }}
          onClick={handleDrop}
        >
          {/* Pivot triangle */}
          <polygon points={`${PIVOT_X},${PIVOT_Y} ${PIVOT_X - 18},${PIVOT_Y + 40} ${PIVOT_X + 18},${PIVOT_Y + 40}`} fill="#555" />
          {/* Base */}
          <rect x={PIVOT_X - 50} y={PIVOT_Y + 40} width={100} height={8} rx={3} fill="#444" />

          {/* Beam group — rotated */}
          <g transform={`rotate(${angleDeg}, ${PIVOT_X}, ${PIVOT_Y})`}>
            {/* Beam */}
            <rect x={PIVOT_X - ARM} y={PIVOT_Y - BEAM_H / 2} width={ARM * 2} height={BEAM_H} rx={4} fill="#8b5cf6" />

            {/* Slot markers */}
            {Array.from({ length: SLOT_COUNT * 2 + 1 }, (_, i) => i - SLOT_COUNT).map(s => {
              if (s === 0) return null;
              const sx = slotX(s);
              return (
                <g key={s}>
                  <line x1={sx} y1={PIVOT_Y - BEAM_H / 2} x2={sx} y2={PIVOT_Y - BEAM_H / 2 - 6} stroke="#ffffff33" strokeWidth={1} />
                  <text x={sx} y={PIVOT_Y + BEAM_H / 2 + 14} fill="#ffffff44" fontSize={8} textAnchor="middle">{s}</text>
                </g>
              );
            })}

            {/* Weights on beam */}
            {weights.map(w => {
              const wx = slotX(w.pos);
              const wy = PIVOT_Y - BEAM_H / 2 - 10 - w.mass * 8;
              const ci = WEIGHT_MASSES.indexOf(w.mass);
              return (
                <g key={w.id} onClick={e => { e.stopPropagation(); removeWeight(w.id); }} style={{ cursor: "pointer" }}>
                  <rect x={wx - 10} y={wy} width={20} height={w.mass * 8 + 10} rx={3} fill={COLORS[ci]} opacity={0.85} />
                  <text x={wx} y={wy + (w.mass * 8 + 10) / 2 + 4} fill="#fff" fontSize={11} fontWeight="bold" textAnchor="middle">{w.mass}</text>
                </g>
              );
            })}
          </g>

          {/* Balance indicator */}
          {balanced && (
            <text x={PIVOT_X} y={30} fill="#22c55e" fontSize={18} textAnchor="middle" fontWeight="bold">✅ Balanced!</text>
          )}
          {!balanced && weights.length > 0 && (
            <text x={PIVOT_X} y={30} fill="#f59e0b88" fontSize={13} textAnchor="middle">
              Torque: {t > 0 ? "+" : ""}{t.toFixed(1)} (tilting {t > 0 ? "right" : "left"})
            </text>
          )}
        </svg>

        {/* Controls */}
        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 200 }}>
          <div style={{ fontSize: 13, color: "#888", marginBottom: 10 }}>Drag a weight onto the beam:</div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
            {WEIGHT_MASSES.map((m, i) => (
              <div
                key={m}
                onMouseDown={() => setDragging({ mass: m })}
                style={{
                  width: 44, height: 44, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center",
                  background: COLORS[i], cursor: "grab", fontWeight: 700, fontSize: 16, userSelect: "none",
                  border: dragging?.mass === m ? "2px solid #fff" : "2px solid transparent",
                }}
              >
                {m}
              </div>
            ))}
          </div>

          <button onClick={() => setWeights([])} style={{ ...btn, width: "100%", marginBottom: 12 }}>🗑 Clear All</button>

          <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.7 }}>
            <p style={{ margin: "0 0 8px" }}>⚖️ <b>Torque = mass × distance</b></p>
            <p style={{ margin: "0 0 4px" }}>Place weights on both sides to balance!</p>
            <p style={{ margin: 0, color: "#666" }}>Click a weight on the beam to remove it.</p>
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
