"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { sfxExplode, sfxGameOver, sfxWrong } from "@/app/play/sfx";

const W = 600;
const H = 500;
const ASTEROID_R = 28;
const FALL_SPEED_BASE = 0.4;

type Asteroid = { id: number; x: number; y: number; a: number; b: number; product: number };

function randInt(min: number, max: number) { return Math.floor(Math.random() * (max - min + 1)) + min; }

export default function TimesTablePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef(0);
  const [table, setTable] = useState(5);
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [gameOver, setGameOver] = useState(false);
  const [inputA, setInputA] = useState("");
  const [inputB, setInputB] = useState("");

  const asteroidsRef = useRef<Asteroid[]>([]);
  const scoreRef = useRef(0);
  const livesRef = useRef(3);
  const gameOverRef = useRef(false);
  const tableRef = useRef(table);
  const nextId = useRef(0);
  const spawnTimer = useRef(0);

  useEffect(() => { scoreRef.current = score; }, [score]);
  useEffect(() => { livesRef.current = lives; }, [lives]);
  useEffect(() => { gameOverRef.current = gameOver; }, [gameOver]);
  useEffect(() => { tableRef.current = table; }, [table]);

  const spawnAsteroid = useCallback(() => {
    const t = tableRef.current;
    const b = randInt(1, 12);
    asteroidsRef.current.push({
      id: nextId.current++,
      x: randInt(ASTEROID_R + 10, W - ASTEROID_R - 10),
      y: -ASTEROID_R,
      a: t, b, product: t * b,
    });
  }, []);

  const restart = useCallback(() => {
    setScore(0); setLives(3); setGameOver(false);
    asteroidsRef.current = [];
    scoreRef.current = 0; livesRef.current = 3; gameOverRef.current = false;
    spawnTimer.current = 0;
  }, []);

  const shoot = useCallback((a: number, b: number) => {
    const product = a * b;
    const idx = asteroidsRef.current.findIndex(ast => ast.product === product);
    if (idx >= 0) {
      asteroidsRef.current.splice(idx, 1);
      sfxExplode();
      setScore(s => s + 1);
    }
  }, []);

  const handleShoot = () => {
    const a = parseInt(inputA);
    const b = parseInt(inputB);
    if (!isNaN(a) && !isNaN(b)) {
      shoot(a, b);
      setInputA("");
      setInputB("");
    }
  };

  // Quick-shoot: click asteroid to type its factors
  const handleCanvasClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const ast = asteroidsRef.current.find(a =>
      Math.hypot(a.x - mx, a.y - my) < ASTEROID_R + 5
    );
    if (ast) {
      asteroidsRef.current = asteroidsRef.current.filter(a => a.id !== ast.id);
      sfxExplode();
      setScore(s => s + 1);
    }
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    canvas.width = W;
    canvas.height = H;

    const frame = () => {
      if (gameOverRef.current) {
        ctx.clearRect(0, 0, W, H);
        ctx.fillStyle = "#0f172a";
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = "#ef4444";
        ctx.font = "bold 32px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("Game Over!", W / 2, H / 2 - 20);
        ctx.fillStyle = "#fff";
        ctx.font = "18px sans-serif";
        ctx.fillText(`Score: ${scoreRef.current}`, W / 2, H / 2 + 20);
        ctx.textAlign = "start";
        rafRef.current = requestAnimationFrame(frame);
        return;
      }

      // Spawn
      spawnTimer.current++;
      const spawnRate = Math.max(60, 150 - scoreRef.current * 3);
      if (spawnTimer.current >= spawnRate) {
        spawnTimer.current = 0;
        spawnAsteroid();
      }

      // Move
      const speed = FALL_SPEED_BASE + scoreRef.current * 0.02;
      asteroidsRef.current.forEach(a => { a.y += speed; });

      // Check ground
      const fallen = asteroidsRef.current.filter(a => a.y > H + ASTEROID_R);
      if (fallen.length > 0) {
        asteroidsRef.current = asteroidsRef.current.filter(a => a.y <= H + ASTEROID_R);
        sfxWrong();
        const newLives = livesRef.current - fallen.length;
        setLives(Math.max(0, newLives));
        if (newLives <= 0) { setGameOver(true); sfxGameOver(); }
      }

      // Draw
      ctx.clearRect(0, 0, W, H);
      const bg = ctx.createLinearGradient(0, 0, 0, H);
      bg.addColorStop(0, "#0f172a");
      bg.addColorStop(1, "#1e293b");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, W, H);

      // Stars
      for (let i = 0; i < 30; i++) {
        const sx = (i * 137.5) % W;
        const sy = (i * 97.3) % H;
        ctx.fillStyle = "#ffffff22";
        ctx.fillRect(sx, sy, 1.5, 1.5);
      }

      // Ground line
      ctx.strokeStyle = "#ef444466";
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 4]);
      ctx.beginPath();
      ctx.moveTo(0, H - 4);
      ctx.lineTo(W, H - 4);
      ctx.stroke();
      ctx.setLineDash([]);

      // Asteroids
      asteroidsRef.current.forEach(a => {
        // Rock
        ctx.beginPath();
        ctx.arc(a.x, a.y, ASTEROID_R, 0, Math.PI * 2);
        const g = ctx.createRadialGradient(a.x - 5, a.y - 5, 2, a.x, a.y, ASTEROID_R);
        g.addColorStop(0, "#a78bfa");
        g.addColorStop(1, "#4c1d95");
        ctx.fillStyle = g;
        ctx.fill();
        ctx.strokeStyle = "#7c3aed44";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Product text
        ctx.fillStyle = "#fff";
        ctx.font = "bold 16px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(String(a.product), a.x, a.y + 1);

        // Factors hint (small)
        ctx.fillStyle = "#ffffff55";
        ctx.font = "9px sans-serif";
        ctx.fillText(`${a.a}×${a.b}`, a.x, a.y + 16);
        ctx.textAlign = "start";
      });

      // HUD
      ctx.fillStyle = "#fff";
      ctx.font = "14px sans-serif";
      ctx.fillText(`Score: ${scoreRef.current}`, 12, 24);
      ctx.fillText(`❤️`.repeat(livesRef.current), 12, 46);

      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(rafRef.current);
  }, [spawnAsteroid]);

  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>☄️ Times Table Shooter</h1>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px" }}>
        <canvas ref={canvasRef} onClick={handleCanvasClick} style={{ borderRadius: 12, border: "1px solid #333", cursor: "crosshair" }} />

        <div style={{ background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16, minWidth: 220 }}>
          <label style={lbl}>
            📊 Table: {table}×
            <input type="range" min={2} max={12} value={table} onChange={e => setTable(+e.target.value)} style={slider} />
          </label>

          <div style={{ fontSize: 13, color: "#888", marginBottom: 8 }}>Type factors to shoot:</div>
          <div style={{ display: "flex", gap: 4, alignItems: "center", marginBottom: 12 }}>
            <input value={inputA} onChange={e => setInputA(e.target.value)} placeholder="?" style={inp} onKeyDown={e => e.key === "Enter" && handleShoot()} />
            <span>×</span>
            <input value={inputB} onChange={e => setInputB(e.target.value)} placeholder="?" style={inp} onKeyDown={e => e.key === "Enter" && handleShoot()} />
            <button onClick={handleShoot} style={{ ...btn, background: "#8b5cf6", border: "none" }}>💥</button>
          </div>

          <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>Or click an asteroid to destroy it!</div>

          <button onClick={restart} style={{ ...btn, width: "100%", marginBottom: 12 }}>🔄 Restart</button>

          <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.7 }}>
            <p style={{ margin: 0 }}>☄️ Asteroids fall with products. Click them or type the factors to destroy them before they hit the ground!</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const btn: React.CSSProperties = { padding: "6px 14px", borderRadius: 6, border: "1px solid #555", background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13 };
const lbl: React.CSSProperties = { display: "block", fontSize: 13, color: "#ccc", marginBottom: 12 };
const slider: React.CSSProperties = { width: "100%", display: "block", marginTop: 6, accentColor: "#8b5cf6" };
const inp: React.CSSProperties = { width: 40, padding: "4px 6px", borderRadius: 4, border: "1px solid #555", background: "#0a0a1a", color: "#fff", fontSize: 14, textAlign: "center" };
