"use client";

import { useState, useRef, useCallback } from "react";
import Link from "next/link";
import { sfxDraw, sfxCorrect } from "@/app/play/sfx";

const W = 500;
const H = 500;
const START_X = W / 2;
const START_Y = H / 2;

type Line = { x1: number; y1: number; x2: number; y2: number; color: string };

const COLORS = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#8b5cf6", "#ec4899"];

const PRESETS = [
  { name: "Square", code: "forward 80\nright 90\nforward 80\nright 90\nforward 80\nright 90\nforward 80" },
  { name: "Triangle", code: "forward 100\nright 120\nforward 100\nright 120\nforward 100" },
  { name: "Star", code: "repeat 5\nforward 100\nright 144\nend" },
  { name: "Spiral", code: "repeat 36\nforward i*3\nright 90\nend" },
  { name: "Hexagon", code: "repeat 6\nforward 60\nright 60\nend" },
  { name: "Circle-ish", code: "repeat 36\nforward 10\nright 10\nend" },
];

function parse(code: string): Line[] {
  const lines: Line[] = [];
  let x = START_X, y = START_Y, angle = -90; // facing up
  let colorIdx = 0;
  const cmds = code.split("\n").map(l => l.trim()).filter(Boolean);

  const exec = (cmds: string[], depth: number): void => {
    if (depth > 10) return;
    let i = 0;
    while (i < cmds.length) {
      const parts = cmds[i].split(/\s+/);
      const cmd = parts[0].toLowerCase();

      if (cmd === "forward" || cmd === "fd") {
        const dist = parseFloat(parts[1]) || 50;
        const rad = (angle * Math.PI) / 180;
        const nx = x + dist * Math.cos(rad);
        const ny = y + dist * Math.sin(rad);
        lines.push({ x1: x, y1: y, x2: nx, y2: ny, color: COLORS[colorIdx % COLORS.length] });
        x = nx; y = ny;
      } else if (cmd === "right" || cmd === "rt") {
        angle += parseFloat(parts[1]) || 90;
      } else if (cmd === "left" || cmd === "lt") {
        angle -= parseFloat(parts[1]) || 90;
      } else if (cmd === "color") {
        colorIdx++;
      } else if (cmd === "repeat") {
        const count = parseInt(parts[1]) || 4;
        // Collect body until "end"
        const body: string[] = [];
        i++;
        while (i < cmds.length && cmds[i].toLowerCase() !== "end") {
          body.push(cmds[i]);
          i++;
        }
        for (let r = 0; r < count; r++) {
          // Replace "i" with iteration index
          const expanded = body.map(l => l.replace(/\bi\b/g, String(r + 1)));
          exec(expanded, depth + 1);
          // Evaluate expressions like "i*3"
        }
      }
      i++;
      if (lines.length > 2000) return; // safety
    }
  };

  // Pre-process: evaluate simple math expressions in arguments
  const processed = cmds.map(l => {
    return l.replace(/(\d+)\s*\*\s*(\d+)/g, (_, a, b) => String(parseInt(a) * parseInt(b)));
  });
  exec(processed, 0);
  return lines;
}

export default function TurtlePage() {
  const [code, setCode] = useState(PRESETS[0].code);
  const [lines, setLines] = useState<Line[]>(() => parse(PRESETS[0].code));
  const textRef = useRef<HTMLTextAreaElement>(null);

  const run = useCallback(() => {
    const result = parse(code);
    setLines(result);
    if (result.length > 0) sfxDraw();
  }, [code]);

  const loadPreset = (idx: number) => {
    setCode(PRESETS[idx].code);
    const result = parse(PRESETS[idx].code);
    setLines(result);
    sfxCorrect();
  };

  // Turtle position (end of last line or start)
  const tx = lines.length > 0 ? lines[lines.length - 1].x2 : START_X;
  const ty = lines.length > 0 ? lines[lines.length - 1].y2 : START_Y;

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🐢 Turtle Graphics</h1>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px" }}>
        {/* Canvas */}
        <svg width={W} height={H} style={{ background: "#111827", borderRadius: 12, border: "1px solid #333" }}>
          {/* Grid */}
          {Array.from({ length: 11 }, (_, i) => {
            const p = i * (W / 10);
            return (
              <g key={i}>
                <line x1={p} y1={0} x2={p} y2={H} stroke="#ffffff08" />
                <line x1={0} y1={p} x2={W} y2={p} stroke="#ffffff08" />
              </g>
            );
          })}
          {/* Lines */}
          {lines.map((l, i) => (
            <line key={i} x1={l.x1} y1={l.y1} x2={l.x2} y2={l.y2} stroke={l.color} strokeWidth={2} strokeLinecap="round" />
          ))}
          {/* Turtle */}
          <circle cx={tx} cy={ty} r={6} fill="#22c55e" />
          <circle cx={tx} cy={ty} r={3} fill="#fff" />
        </svg>

        {/* Editor */}
        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 260, display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {PRESETS.map((p, i) => (
              <button key={i} onClick={() => loadPreset(i)} style={{ ...btnSm, fontSize: 11 }}>{p.name}</button>
            ))}
          </div>

          <textarea
            ref={textRef}
            value={code}
            onChange={e => setCode(e.target.value)}
            spellCheck={false}
            style={{
              width: "100%", height: 200, background: "#0a0a1a", color: "#e2e8f0", border: "1px solid #444",
              borderRadius: 8, padding: 10, fontSize: 13, fontFamily: "monospace", resize: "vertical",
            }}
          />

          <button onClick={run} style={{ ...btn, background: "#22c55e", color: "#000", fontWeight: 700, border: "none" }}>
            ▶ Run
          </button>

          <button onClick={() => { setCode(""); setLines([]); }} style={btn}>🗑 Clear</button>

          <div style={{ fontSize: 11, color: "#94a3b8", lineHeight: 1.8 }}>
            <b>Commands:</b><br />
            forward 50 — move forward<br />
            right 90 / left 90 — turn<br />
            color — change color<br />
            repeat 4 ... end — loop<br />
          </div>
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
const btnSm: React.CSSProperties = { ...btn, padding: "4px 8px" };
