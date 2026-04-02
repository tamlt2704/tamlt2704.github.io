"use client";

import { useState } from "react";
import Link from "next/link";
import { sfxPop, sfxRemove, sfxCorrect } from "@/app/play/sfx";

const SIZE = 280;
const R = 120;
const CX = SIZE / 2;
const CY = SIZE / 2;
const COLORS = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#84cc16", "#e879f9", "#06b6d4"];

function slicePath(i: number, total: number, r: number): string {
  const a1 = (i / total) * Math.PI * 2 - Math.PI / 2;
  const a2 = ((i + 1) / total) * Math.PI * 2 - Math.PI / 2;
  const x1 = CX + r * Math.cos(a1);
  const y1 = CY + r * Math.sin(a1);
  const x2 = CX + r * Math.cos(a2);
  const y2 = CY + r * Math.sin(a2);
  const large = total <= 2 ? 1 : 0;
  return `M${CX},${CY} L${x1},${y1} A${r},${r} 0 ${large} 1 ${x2},${y2} Z`;
}

function gcd(a: number, b: number): number { return b === 0 ? a : gcd(b, a % b); }
function simplify(n: number, d: number) { const g = gcd(n, d); return `${n / g}/${d / g}`; }

const CHALLENGES = [
  { q: "Color 1/2 of the pizza", slices: 4, target: 2 },
  { q: "Color 1/3 of the pizza", slices: 6, target: 2 },
  { q: "Color 3/4 of the pizza", slices: 8, target: 6 },
  { q: "Color 2/5 of the pizza", slices: 5, target: 2 },
  { q: "Color 5/6 of the pizza", slices: 6, target: 5 },
];

export default function FractionsPage() {
  const [slices, setSlices] = useState(8);
  const [colored, setColored] = useState<Set<number>>(new Set());
  const [mode, setMode] = useState<"free" | "challenge">("free");
  const [chIdx, setChIdx] = useState(0);

  const ch = CHALLENGES[chIdx];
  const activeSlices = mode === "challenge" ? ch.slices : slices;
  const target = mode === "challenge" ? ch.target : null;
  const correct = target !== null && colored.size === target;

  const toggle = (i: number) => {
    setColored(prev => {
      const s = new Set(prev);
      if (s.has(i)) { s.delete(i); sfxRemove(); } else { s.add(i); sfxPop(); }
      return s;
    });
  };

  const nextChallenge = () => {
    sfxCorrect();
    setChIdx(i => (i + 1) % CHALLENGES.length);
    setColored(new Set());
  };

  const fraction = colored.size > 0 ? simplify(colored.size, activeSlices) : "0";

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🍕 Fraction Pizza</h1>
        <button onClick={() => { setMode("free"); setColored(new Set()); }} style={{ ...btn, background: mode === "free" ? "#3b82f6" : "#1a1a2e" }}>Free Play</button>
        <button onClick={() => { setMode("challenge"); setColored(new Set()); setChIdx(0); }} style={{ ...btn, background: mode === "challenge" ? "#3b82f6" : "#1a1a2e" }}>Challenge</button>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 24, padding: "0 16px 16px", alignItems: "flex-start" }}>
        {/* Pizza */}
        <div style={{ background: "#111827", borderRadius: 16, border: "1px solid #333", padding: 20, textAlign: "center" }}>
          <svg width={SIZE} height={SIZE}>
            {/* Crust circle */}
            <circle cx={CX} cy={CY} r={R + 4} fill="#d97706" />
            {Array.from({ length: activeSlices }, (_, i) => (
              <path
                key={i}
                d={slicePath(i, activeSlices, R)}
                fill={colored.has(i) ? COLORS[i % COLORS.length] : "#fbbf24"}
                stroke="#92400e"
                strokeWidth={2}
                style={{ cursor: "pointer", transition: "fill 0.15s" }}
                onClick={() => toggle(i)}
              />
            ))}
            {/* Center dot */}
            <circle cx={CX} cy={CY} r={4} fill="#92400e" />
          </svg>

          <div style={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}>
            {colored.size}/{activeSlices}
            {colored.size > 0 && colored.size < activeSlices && (
              <span style={{ fontSize: 16, color: "#888", marginLeft: 8 }}>= {fraction}</span>
            )}
          </div>

          {mode === "challenge" && (
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 15, color: correct ? "#22c55e" : "#f59e0b" }}>
                {correct ? "🎉 Correct!" : ch.q}
              </div>
              {correct && <button onClick={nextChallenge} style={{ ...btn, marginTop: 8 }}>Next →</button>}
            </div>
          )}
        </div>

        {/* Controls */}
        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 200 }}>
          {mode === "free" && (
            <label style={lbl}>
              🔪 Slices: {slices}
              <input type="range" min={2} max={12} value={slices} onChange={e => { setSlices(+e.target.value); setColored(new Set()); }} style={slider} />
            </label>
          )}

          <button onClick={() => setColored(new Set())} style={{ ...btn, width: "100%", marginBottom: 12 }}>🗑 Clear</button>

          <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.7 }}>
            <p style={{ margin: "0 0 8px" }}>🍕 <b>Fractions = parts of a whole</b></p>
            <p style={{ margin: "0 0 4px" }}>Click slices to color them. The number shows what fraction you&apos;ve selected!</p>
            <p style={{ margin: 0, color: "#666" }}>2/4 = 1/2 — that&apos;s simplifying!</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
const lbl: React.CSSProperties = { display: "block", fontSize: 13, color: "#ccc", marginBottom: 12 };
const slider: React.CSSProperties = { width: "100%", display: "block", marginTop: 6, accentColor: "#f59e0b" };
