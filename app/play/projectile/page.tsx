"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { sfxWhoosh, sfxThud } from "@/app/play/sfx";

const G = 9.81;
const SCALE = 4; // pixels per metre
const GROUND_Y_OFFSET = 60; // px from bottom of canvas
const BALL_R = 6;
const TRAIL_COLOR = "#ff6b3588";
const BALL_COLOR = "#ff6b35";
const CANNON_LEN = 50;

function solve(angle: number, v0: number) {
  const rad = (angle * Math.PI) / 180;
  const vx = v0 * Math.cos(rad);
  const vy = v0 * Math.sin(rad);
  const tFlight = (2 * vy) / G;
  const maxH = (vy * vy) / (2 * G);
  const range = vx * tFlight;
  return { vx, vy, tFlight, maxH, range, rad };
}

const FACTS = [
  "🏀 A basketball follows the same parabolic arc!",
  "🚀 NASA uses these equations to launch rockets",
  "🎯 45° gives the maximum range on flat ground",
  "🌙 On the Moon, the ball would go 6× farther (less gravity!)",
  "⚽ A football's curve adds spin — that's the Magnus effect",
  "🏔️ Higher launch = more hang time but not always more distance",
  "💨 In real life, air resistance slows the ball down",
  "🎆 Fireworks are projectiles too!",
];

export default function ProjectilePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);
  const [angle, setAngle] = useState(45);
  const [power, setPower] = useState(50);
  const [flying, setFlying] = useState(false);
  const [stats, setStats] = useState({ t: 0, h: 0, d: 0 });
  const [result, setResult] = useState<{ maxH: number; range: number; tFlight: number } | null>(null);
  const [fact, setFact] = useState(FACTS[0]);

  const v0 = power; // m/s

  const getCanvasSize = useCallback(() => {
    const w = Math.min(900, window.innerWidth - 32);
    return { w, h: Math.round(w * 0.55) };
  }, []);

  // Draw static scene (cannon + grid)
  const drawScene = useCallback(
    (ctx: CanvasRenderingContext2D, W: number, H: number) => {
      const groundY = H - GROUND_Y_OFFSET;
      ctx.clearRect(0, 0, W, H);

      // Sky gradient
      const sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#0f172a");
      sky.addColorStop(1, "#1e3a5f");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);

      // Ground
      ctx.fillStyle = "#22c55e22";
      ctx.fillRect(0, groundY, W, GROUND_Y_OFFSET);
      ctx.strokeStyle = "#22c55e66";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, groundY);
      ctx.lineTo(W, groundY);
      ctx.stroke();

      // Distance markers
      ctx.fillStyle = "#ffffff44";
      ctx.font = "10px sans-serif";
      for (let m = 0; m <= 200; m += 25) {
        const x = 40 + m * SCALE;
        if (x > W) break;
        ctx.beginPath();
        ctx.moveTo(x, groundY);
        ctx.lineTo(x, groundY + 6);
        ctx.strokeStyle = "#ffffff33";
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillText(`${m}m`, x - 8, groundY + 18);
      }

      // Cannon base
      const cx = 40, cy = groundY;
      ctx.fillStyle = "#555";
      ctx.beginPath();
      ctx.arc(cx, cy, 10, 0, Math.PI * 2);
      ctx.fill();

      // Cannon barrel
      const rad = (angle * Math.PI) / 180;
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(-rad);
      ctx.fillStyle = "#888";
      ctx.fillRect(0, -5, CANNON_LEN, 10);
      ctx.restore();

      return { groundY, cx, cy };
    },
    [angle]
  );

  // Draw predicted trajectory (dotted)
  const drawPreview = useCallback(
    (ctx: CanvasRenderingContext2D, W: number, H: number, groundY: number) => {
      const { vx, vy, tFlight } = solve(angle, v0);
      ctx.setLineDash([4, 6]);
      ctx.strokeStyle = "#ffffff22";
      ctx.lineWidth = 1;
      ctx.beginPath();
      const steps = 80;
      for (let i = 0; i <= steps; i++) {
        const t = (i / steps) * tFlight;
        const x = 40 + vx * t * SCALE;
        const y = groundY - (vy * t - 0.5 * G * t * t) * SCALE;
        if (x > W) break;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);
    },
    [angle, v0]
  );

  // Static + preview redraw
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || flying) return;
    const { w, h } = getCanvasSize();
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d")!;
    const { groundY } = drawScene(ctx, w, h);
    drawPreview(ctx, w, h, groundY);

    const s = solve(angle, v0);
    setStats({ t: 0, h: 0, d: 0 });
    setResult({ maxH: s.maxH, range: s.range, tFlight: s.tFlight });
  }, [angle, v0, flying, drawScene, drawPreview, getCanvasSize]);

  const launch = () => {
    if (flying) return;
    setFlying(true);
    sfxWhoosh();
    setFact(FACTS[Math.floor(Math.random() * FACTS.length)]);
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    const { vx, vy, tFlight } = solve(angle, v0);
    const groundY = H - GROUND_Y_OFFSET;
    const trail: { x: number; y: number }[] = [];
    let startTs: number | null = null;
    const SIM_SPEED = 1; // real-time

    const frame = (ts: number) => {
      if (!startTs) startTs = ts;
      const elapsed = ((ts - startTs) / 1000) * SIM_SPEED;
      const t = Math.min(elapsed, tFlight);
      const bx = 40 + vx * t * SCALE;
      const by = groundY - (vy * t - 0.5 * G * t * t) * SCALE;

      drawScene(ctx, W, H);

      // Trail
      trail.push({ x: bx, y: by });
      ctx.beginPath();
      ctx.strokeStyle = TRAIL_COLOR;
      ctx.lineWidth = 2;
      trail.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
      ctx.stroke();

      // Ball
      ctx.beginPath();
      ctx.arc(bx, by, BALL_R, 0, Math.PI * 2);
      ctx.fillStyle = BALL_COLOR;
      ctx.fill();
      ctx.shadowColor = BALL_COLOR;
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Height line
      if (by < groundY - 2) {
        ctx.setLineDash([3, 3]);
        ctx.strokeStyle = "#ffffff33";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(bx, by + BALL_R);
        ctx.lineTo(bx, groundY);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = "#ffffffaa";
        ctx.font = "11px sans-serif";
        ctx.fillText(`${((groundY - by) / SCALE).toFixed(1)}m`, bx + 8, (by + groundY) / 2);
      }

      setStats({
        t: +t.toFixed(2),
        h: +((groundY - by) / SCALE).toFixed(1),
        d: +((bx - 40) / SCALE).toFixed(1),
      });

      if (t < tFlight) {
        rafRef.current = requestAnimationFrame(frame);
      } else {
        // Landing burst
        for (let i = 0; i < 8; i++) {
          const a = (i / 8) * Math.PI * 2;
          const r = 15 + Math.random() * 10;
          ctx.beginPath();
          ctx.arc(bx + Math.cos(a) * r, groundY - Math.abs(Math.sin(a)) * r, 2, 0, Math.PI * 2);
          ctx.fillStyle = "#22c55e88";
          ctx.fill();
        }
        sfxThud();
        setFlying(false);
      }
    };
    rafRef.current = requestAnimationFrame(frame);
  };

  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      {/* Top bar */}
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🚀 Projectile Launcher</h1>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px", alignItems: "flex-start" }}>
        {/* Canvas */}
        <canvas
          ref={canvasRef}
          style={{ borderRadius: 12, border: "1px solid #333", maxWidth: "100%" }}
        />

        {/* Controls panel */}
        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 220, flex: "0 0 auto" }}>
          {/* Angle */}
          <label style={labelStyle}>
            🎯 Angle: {angle}°
            <input
              type="range" min={5} max={85} value={angle}
              onChange={e => setAngle(+e.target.value)}
              disabled={flying}
              style={sliderStyle}
            />
          </label>

          {/* Power */}
          <label style={labelStyle}>
            💪 Power: {power} m/s
            <input
              type="range" min={5} max={100} value={power}
              onChange={e => setPower(+e.target.value)}
              disabled={flying}
              style={sliderStyle}
            />
          </label>

          <button onClick={launch} disabled={flying} style={{
            ...btn,
            width: "100%",
            marginTop: 12,
            background: flying ? "#333" : "#ff6b35",
            color: "#fff",
            fontSize: 16,
            fontWeight: 700,
            border: "none",
          }}>
            {flying ? "Flying..." : "🚀 Launch!"}
          </button>

          {/* Live stats */}
          <div style={{ marginTop: 16, fontSize: 13, lineHeight: 1.8 }}>
            <div>⏱ Time: <b>{stats.t}s</b></div>
            <div>📏 Distance: <b>{stats.d}m</b></div>
            <div>📐 Height: <b>{stats.h}m</b></div>
          </div>

          {/* Predicted results */}
          {result && (
            <div style={{ marginTop: 12, padding: "10px 12px", background: "#0a0a1a", borderRadius: 8, fontSize: 12, lineHeight: 1.8 }}>
              <div style={{ color: "#888", marginBottom: 4 }}>Predicted:</div>
              <div>Max Height: <b style={{ color: "#4da6ff" }}>{result.maxH.toFixed(1)}m</b></div>
              <div>Range: <b style={{ color: "#22c55e" }}>{result.range.toFixed(1)}m</b></div>
              <div>Flight Time: <b style={{ color: "#f59e0b" }}>{result.tFlight.toFixed(2)}s</b></div>
            </div>
          )}

          {/* Fun fact */}
          <div style={{ marginTop: 14, padding: "10px 12px", background: "#1e293b", borderRadius: 8, fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>
            {fact}
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

const labelStyle: React.CSSProperties = {
  display: "block", fontSize: 13, color: "#ccc", marginBottom: 12,
};

const sliderStyle: React.CSSProperties = {
  width: "100%", display: "block", marginTop: 6, accentColor: "#ff6b35",
};
