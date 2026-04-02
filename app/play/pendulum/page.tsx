"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { sfxTick } from "@/app/play/sfx";

const G = 9.81;
const W = 700;
const H = 450;
const PIVOT_X = W / 2;
const PIVOT_Y = 60;
const PX_PER_M = 150; // pixels per metre

export default function PendulumPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef(0);
  const [length, setLength] = useState(1.5); // metres
  const [mass, setMass] = useState(2); // kg (visual only)
  const [damping, setDamping] = useState(0.002);
  const [running, setRunning] = useState(true);
  const [showTrail, setShowTrail] = useState(true);

  // Physics state refs
  const theta = useRef(Math.PI / 4);
  const omega = useRef(0);
  const trail = useRef<{ x: number; y: number }[]>([]);
  const runRef = useRef(running);
  const lengthRef = useRef(length);
  const dampRef = useRef(damping);
  const trailRef = useRef(showTrail);
  useEffect(() => { runRef.current = running; }, [running]);
  useEffect(() => { lengthRef.current = length; }, [length]);
  useEffect(() => { dampRef.current = damping; }, [damping]);
  useEffect(() => { trailRef.current = showTrail; }, [showTrail]);

  const lastTickSign = useRef(1);

  const period = 2 * Math.PI * Math.sqrt(length / G);

  const reset = useCallback(() => {
    theta.current = Math.PI / 4;
    omega.current = 0;
    trail.current = [];
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    canvas.width = W;
    canvas.height = H;
    let lastT = 0;

    const frame = (ts: number) => {
      const dt = lastT ? Math.min((ts - lastT) / 1000, 0.05) : 0.016;
      lastT = ts;

      if (runRef.current) {
        const L = lengthRef.current;
        const d = dampRef.current;
        // Simple pendulum ODE: θ'' = -(g/L)sin(θ) - d*θ'
        const alpha = -(G / L) * Math.sin(theta.current) - d * omega.current;
        omega.current += alpha * dt;
        theta.current += omega.current * dt;

        // Tick sound at zero-crossing
        const sign = theta.current >= 0 ? 1 : -1;
        if (sign !== lastTickSign.current) {
          lastTickSign.current = sign;
          sfxTick();
        }
      }

      const L = lengthRef.current;
      const Lpx = L * PX_PER_M;
      const bx = PIVOT_X + Lpx * Math.sin(theta.current);
      const by = PIVOT_Y + Lpx * Math.cos(theta.current);

      if (trailRef.current) {
        trail.current.push({ x: bx, y: by });
        if (trail.current.length > 300) trail.current.shift();
      }

      // Draw
      ctx.clearRect(0, 0, W, H);
      const bg = ctx.createLinearGradient(0, 0, 0, H);
      bg.addColorStop(0, "#0f172a");
      bg.addColorStop(1, "#1e293b");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, W, H);

      // Pivot mount
      ctx.fillStyle = "#555";
      ctx.fillRect(PIVOT_X - 40, 0, 80, 12);
      ctx.beginPath();
      ctx.arc(PIVOT_X, PIVOT_Y, 5, 0, Math.PI * 2);
      ctx.fillStyle = "#888";
      ctx.fill();

      // Trail
      if (trailRef.current && trail.current.length > 1) {
        ctx.beginPath();
        trail.current.forEach((p, i) => {
          ctx.strokeStyle = `rgba(139,92,246,${i / trail.current.length * 0.5})`;
          ctx.lineWidth = 1;
          if (i === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.stroke();
      }

      // String
      ctx.beginPath();
      ctx.moveTo(PIVOT_X, PIVOT_Y);
      ctx.lineTo(bx, by);
      ctx.strokeStyle = "#aaa";
      ctx.lineWidth = 2;
      ctx.stroke();

      // Bob
      const bobR = 10 + mass * 3;
      const grad = ctx.createRadialGradient(bx - 3, by - 3, 1, bx, by, bobR);
      grad.addColorStop(0, "#c084fc");
      grad.addColorStop(1, "#7c3aed");
      ctx.beginPath();
      ctx.arc(bx, by, bobR, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.shadowColor = "#7c3aed";
      ctx.shadowBlur = 15;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Angle arc
      if (Math.abs(theta.current) > 0.02) {
        ctx.beginPath();
        const arcR = 40;
        const startA = Math.PI / 2;
        const endA = Math.PI / 2 - theta.current;
        ctx.arc(PIVOT_X, PIVOT_Y, arcR, Math.min(startA, endA), Math.max(startA, endA));
        ctx.strokeStyle = "#f59e0b66";
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = "#f59e0bcc";
        ctx.font = "12px sans-serif";
        ctx.fillText(`${(theta.current * 180 / Math.PI).toFixed(1)}°`, PIVOT_X + 44, PIVOT_Y + 20);
      }

      // Info
      ctx.fillStyle = "#ffffff88";
      ctx.font = "12px sans-serif";
      ctx.fillText(`Period ≈ ${period.toFixed(2)}s`, 12, H - 12);

      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(rafRef.current);
  }, [mass, period]);

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🕐 Pendulum Playground</h1>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px" }}>
        <canvas ref={canvasRef} style={{ borderRadius: 12, border: "1px solid #333" }} />

        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 220 }}>
          <label style={lbl}>
            📏 String Length: {length.toFixed(1)}m
            <input type="range" min={0.3} max={2.5} step={0.1} value={length} onChange={e => setLength(+e.target.value)} style={slider} />
          </label>
          <label style={lbl}>
            ⚖️ Bob Mass: {mass}kg
            <input type="range" min={1} max={5} step={0.5} value={mass} onChange={e => setMass(+e.target.value)} style={slider} />
          </label>
          <label style={lbl}>
            💨 Damping: {damping.toFixed(3)}
            <input type="range" min={0} max={0.05} step={0.001} value={damping} onChange={e => setDamping(+e.target.value)} style={slider} />
          </label>

          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8 }}>
            <button onClick={() => setRunning(!running)} style={btn}>{running ? "⏸ Pause" : "▶ Play"}</button>
            <button onClick={reset} style={btn}>↩ Reset</button>
            <button onClick={() => setShowTrail(!showTrail)} style={btn}>{showTrail ? "Hide Trail" : "Show Trail"}</button>
          </div>

          <div style={{ marginTop: 16, padding: "10px 12px", background: "#0a0a1a", borderRadius: 8, fontSize: 12, lineHeight: 1.8 }}>
            <div>Period: <b style={{ color: "#4da6ff" }}>T ≈ 2π√(L/g) = {period.toFixed(2)}s</b></div>
            <div style={{ color: "#888", marginTop: 4 }}>Mass doesn&apos;t change the period!</div>
          </div>

          <div style={{ marginTop: 12, fontSize: 12, color: "#94a3b8", lineHeight: 1.7 }}>
            <p style={{ margin: 0 }}>🔬 Try changing the string length — longer = slower swing. Mass doesn&apos;t matter!</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
const lbl: React.CSSProperties = { display: "block", fontSize: 13, color: "#ccc", marginBottom: 12 };
const slider: React.CSSProperties = { width: "100%", display: "block", marginTop: 6, accentColor: "#8b5cf6" };
