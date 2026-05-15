"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { sfxCorrect, sfxWrong, sfxWhoosh, sfxThud, sfxFanfare, sfxExplode } from "@/app/play/sfx";

// ─── Constants ───────────────────────────────────────────────────────────────
const G = 9.8;
const CANVAS_ASPECT = 16 / 10;
const MAX_W = 700;

interface Particle {
  x: number; y: number; vx: number; vy: number; life: number; color: string;
}

interface LevelDef {
  name: string;
  icon: string;
  equation: string;
  challenge: string;
}

const LEVELS: LevelDef[] = [
  { name: "Free Fall", icon: "🍎", equation: "y = ½gt²", challenge: "Drop the ball so it hits the target platform" },
  { name: "Projectile", icon: "🚀", equation: "x = v₀cos(θ)t, y = v₀sin(θ)t - ½gt²", challenge: "Hit the target at the marked distance" },
  { name: "Friction", icon: "📦", equation: "a = F/m - μg", challenge: "Stop the crate on the target zone" },
  { name: "Bounce", icon: "🏀", equation: "v' = -e·v", challenge: "Bounce the ball into the basket" },
  { name: "Pendulum", icon: "🕰️", equation: "θ'' = -(g/L)sin(θ)", challenge: "Release at the right moment to hit the target" },
  { name: "Orbit", icon: "🛰️", equation: "F = GMm/r²", challenge: "Achieve a stable orbit (survive 10 seconds)" },
];

// ─── Styles ──────────────────────────────────────────────────────────────────
const btn: React.CSSProperties = {
  padding: "6px 14px", borderRadius: 6, border: "1px solid #555",
  background: "#1a1a2e", color: "#fff", cursor: "pointer", fontSize: 13,
};
const labelStyle: React.CSSProperties = {
  display: "block", fontSize: 13, color: "#ccc", marginBottom: 12,
};
const sliderStyle: React.CSSProperties = {
  width: "100%", display: "block", marginTop: 6, accentColor: "#4da6ff",
};
const panelStyle: React.CSSProperties = {
  background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16,
};

// ─── Main Component ──────────────────────────────────────────────────────────
export default function PhysicsQuestPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);
  const particlesRef = useRef<Particle[]>([]);

  const [gameState, setGameState] = useState<"menu" | "playing" | "levelComplete" | "gameOver" | "victory">("menu");
  const [currentLevel, setCurrentLevel] = useState(0);
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [simRunning, setSimRunning] = useState(false);
  const [flash, setFlash] = useState<string | null>(null);

  // Level-specific controls
  const [slider1, setSlider1] = useState(50);
  const [slider2, setSlider2] = useState(45);
  const [liveStats, setLiveStats] = useState<Record<string, string>>({});

  // Level-specific targets (randomized)
  const [targetVal, setTargetVal] = useState(0);

  const getCanvasSize = useCallback(() => {
    const w = Math.min(MAX_W, (typeof window !== "undefined" ? window.innerWidth : 800) - 32);
    return { w, h: Math.round(w / CANVAS_ASPECT) };
  }, []);

  // ─── Particle system ────────────────────────────────────────────────────────
  const spawnParticles = useCallback((x: number, y: number, color: string, count = 20) => {
    const ps: Particle[] = [];
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 50 + Math.random() * 150;
      ps.push({ x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed, life: 1, color });
    }
    particlesRef.current = [...particlesRef.current, ...ps];
  }, []);

  const updateParticles = useCallback((dt: number) => {
    particlesRef.current = particlesRef.current
      .map(p => ({ ...p, x: p.x + p.vx * dt, y: p.y + p.vy * dt, vy: p.vy + 200 * dt, life: p.life - dt * 1.5 }))
      .filter(p => p.life > 0);
  }, []);

  const drawParticles = useCallback((ctx: CanvasRenderingContext2D) => {
    particlesRef.current.forEach(p => {
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 3 * p.life, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1;
  }, []);

  // ─── Flash effect ───────────────────────────────────────────────────────────
  const triggerFlash = useCallback((color: string) => {
    setFlash(color);
    setTimeout(() => setFlash(null), 200);
  }, []);

  // ─── Level initialization ───────────────────────────────────────────────────
  const initLevel = useCallback((lvl: number) => {
    setSimRunning(false);
    setLiveStats({});
    particlesRef.current = [];
    cancelAnimationFrame(rafRef.current);

    switch (lvl) {
      case 0: // Free Fall
        setSlider1(50); // drop height %
        setTargetVal(30 + Math.floor(Math.random() * 40)); // target x position %
        break;
      case 1: // Projectile
        setSlider1(50); // power
        setSlider2(45); // angle
        setTargetVal(40 + Math.floor(Math.random() * 40)); // target distance %
        break;
      case 2: // Friction
        setSlider1(50); // push force
        setTargetVal(50 + Math.floor(Math.random() * 30)); // target zone %
        break;
      case 3: // Bounce
        setSlider1(60); // launch angle
        setSlider2(70); // power
        setTargetVal(60 + Math.floor(Math.random() * 25)); // basket position %
        break;
      case 4: // Pendulum
        setSlider1(70); // initial angle
        setTargetVal(55 + Math.floor(Math.random() * 30)); // target x %
        break;
      case 5: // Orbit
        setSlider1(50); // launch speed
        setTargetVal(0);
        break;
    }
  }, []);

  // ─── Start game ─────────────────────────────────────────────────────────────
  const startGame = useCallback(() => {
    setGameState("playing");
    setCurrentLevel(0);
    setScore(0);
    setLives(3);
    initLevel(0);
  }, [initLevel]);

  // ─── Level success ──────────────────────────────────────────────────────────
  const onSuccess = useCallback(() => {
    sfxCorrect();
    sfxFanfare();
    setScore(s => s + 100 * (currentLevel + 1));
    const canvas = canvasRef.current;
    if (canvas) spawnParticles(canvas.width / 2, canvas.height / 2, "#22c55e", 30);
    triggerFlash("#22c55e33");
    setSimRunning(false);
    if (currentLevel >= 5) {
      setGameState("victory");
    } else {
      setGameState("levelComplete");
    }
  }, [currentLevel, spawnParticles, triggerFlash]);

  // ─── Level failure ──────────────────────────────────────────────────────────
  const onFail = useCallback(() => {
    sfxWrong();
    triggerFlash("#ff000044");
    setSimRunning(false);
    const newLives = lives - 1;
    setLives(newLives);
    if (newLives <= 0) {
      sfxExplode();
      setGameState("gameOver");
    } else {
      initLevel(currentLevel);
    }
  }, [lives, currentLevel, initLevel, triggerFlash]);

  // ─── Next level ─────────────────────────────────────────────────────────────
  const nextLevel = useCallback(() => {
    const next = currentLevel + 1;
    setCurrentLevel(next);
    setGameState("playing");
    initLevel(next);
  }, [currentLevel, initLevel]);

  // ─── LEVEL 0: Free Fall ─────────────────────────────────────────────────────
  const runFreeFall = useCallback(() => {
    if (simRunning) return;
    setSimRunning(true);
    sfxWhoosh();
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    const groundY = H - 40;
    const dropHeight = (slider1 / 100) * (H - 100); // pixels
    const ballStartY = groundY - dropHeight;
    const ballX = W * 0.3;
    const targetX = W * (targetVal / 100);
    const targetW = 50;
    const SCALE = 3; // pixels per meter for display

    let vy = 0;
    let ballY = ballStartY;
    let prevTs: number | null = null;

    const frame = (ts: number) => {
      if (!prevTs) prevTs = ts;
      const dt = Math.min((ts - prevTs) / 1000, 0.05);
      prevTs = ts;

      vy += G * SCALE * dt * 60;
      ballY += vy * dt;

      // Draw
      ctx.clearRect(0, 0, W, H);
      const sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#0f172a");
      sky.addColorStop(1, "#1e3a5f");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);

      // Ground
      ctx.fillStyle = "#22c55e22";
      ctx.fillRect(0, groundY, W, H - groundY);
      ctx.strokeStyle = "#22c55e66";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, groundY);
      ctx.lineTo(W, groundY);
      ctx.stroke();

      // Target platform
      ctx.fillStyle = "#f59e0b";
      ctx.fillRect(targetX - targetW / 2, groundY - 4, targetW, 8);
      ctx.fillStyle = "#f59e0b88";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("TARGET", targetX, groundY + 20);

      // Drop line
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = "#ffffff22";
      ctx.beginPath();
      ctx.moveTo(ballX, 20);
      ctx.lineTo(ballX, groundY);
      ctx.stroke();
      ctx.setLineDash([]);

      // Ball
      ctx.beginPath();
      ctx.arc(ballX, Math.min(ballY, groundY - 8), 8, 0, Math.PI * 2);
      ctx.fillStyle = "#4da6ff";
      ctx.shadowColor = "#4da6ff";
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Stats
      const heightM = Math.max(0, (groundY - ballY) / SCALE).toFixed(1);
      const velM = (vy / SCALE / 60).toFixed(1);
      const timeElapsed = ((ts - (prevTs ? prevTs : ts)) / 1000).toFixed(2);
      setLiveStats({ "Height": `${heightM}m`, "Velocity": `${velM} m/s` });

      drawParticles(ctx);
      updateParticles(dt);

      if (ballY >= groundY - 8) {
        sfxThud();
        // Check if ball X is near target
        if (Math.abs(ballX - targetX) < targetW / 2 + 8) {
          setTimeout(onSuccess, 300);
        } else {
          setTimeout(onFail, 300);
        }
        return;
      }
      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);
  }, [simRunning, slider1, targetVal, onSuccess, onFail, drawParticles, updateParticles]);

  // ─── LEVEL 1: Projectile ────────────────────────────────────────────────────
  const runProjectile = useCallback(() => {
    if (simRunning) return;
    setSimRunning(true);
    sfxWhoosh();
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    const groundY = H - 40;
    const SCALE = 3;
    const v0 = slider1 * 0.8;
    const angleDeg = slider2;
    const rad = (angleDeg * Math.PI) / 180;
    const vx = v0 * Math.cos(rad);
    const vyInit = v0 * Math.sin(rad);
    const targetX = W * (targetVal / 100);
    const targetW = 40;

    let bx = 40, by = groundY;
    let bvx = vx * SCALE, bvy = -vyInit * SCALE;
    let prevTs: number | null = null;
    const trail: { x: number; y: number }[] = [];

    const frame = (ts: number) => {
      if (!prevTs) prevTs = ts;
      const dt = Math.min((ts - prevTs) / 1000, 0.05);
      prevTs = ts;

      bvy += G * SCALE * dt * 60;
      bx += bvx * dt;
      by += bvy * dt;

      // Draw
      ctx.clearRect(0, 0, W, H);
      const sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#0f172a");
      sky.addColorStop(1, "#1e3a5f");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);

      ctx.fillStyle = "#22c55e22";
      ctx.fillRect(0, groundY, W, H - groundY);
      ctx.strokeStyle = "#22c55e66";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, groundY);
      ctx.lineTo(W, groundY);
      ctx.stroke();

      // Target
      ctx.fillStyle = "#f59e0b";
      ctx.fillRect(targetX - targetW / 2, groundY - 20, targetW, 20);
      ctx.fillStyle = "#f59e0b88";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("TARGET", targetX, groundY + 16);

      // Cannon
      ctx.fillStyle = "#555";
      ctx.beginPath();
      ctx.arc(40, groundY, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.save();
      ctx.translate(40, groundY);
      ctx.rotate(-rad);
      ctx.fillStyle = "#888";
      ctx.fillRect(0, -4, 40, 8);
      ctx.restore();

      // Trail
      trail.push({ x: bx, y: Math.min(by, groundY) });
      ctx.beginPath();
      ctx.strokeStyle = "#4da6ff55";
      ctx.lineWidth = 2;
      trail.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
      ctx.stroke();

      // Ball
      ctx.beginPath();
      ctx.arc(bx, Math.min(by, groundY - 6), 6, 0, Math.PI * 2);
      ctx.fillStyle = "#ff6b35";
      ctx.shadowColor = "#ff6b35";
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

      setLiveStats({
        "Distance": `${((bx - 40) / SCALE).toFixed(1)}m`,
        "Height": `${Math.max(0, (groundY - by) / SCALE).toFixed(1)}m`,
      });

      drawParticles(ctx);
      updateParticles(dt);

      if (by >= groundY && bvy > 0) {
        sfxThud();
        if (Math.abs(bx - targetX) < targetW / 2 + 6) {
          setTimeout(onSuccess, 300);
        } else {
          setTimeout(onFail, 300);
        }
        return;
      }
      if (bx > W + 20) {
        setTimeout(onFail, 100);
        return;
      }
      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);
  }, [simRunning, slider1, slider2, targetVal, onSuccess, onFail, drawParticles, updateParticles]);

  // ─── LEVEL 2: Friction ──────────────────────────────────────────────────────
  const runFriction = useCallback(() => {
    if (simRunning) return;
    setSimRunning(true);
    sfxWhoosh();
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    const groundY = H - 60;
    const mu = 0.3;
    const mass = 5;
    const force = slider1 * 2; // Newtons
    const pushDuration = 0.5; // seconds of push
    const targetX = W * (targetVal / 100);
    const targetW = 60;

    let crateX = 60;
    let crateV = 0;
    let elapsed = 0;
    let prevTs: number | null = null;
    let stopped = false;

    const frame = (ts: number) => {
      if (!prevTs) prevTs = ts;
      const dt = Math.min((ts - prevTs) / 1000, 0.05);
      prevTs = ts;
      elapsed += dt;

      // Physics
      let accel = 0;
      if (elapsed < pushDuration) {
        accel = force / mass - mu * G;
      } else {
        if (crateV > 0.1) {
          accel = -mu * G;
        } else {
          crateV = 0;
          if (!stopped) {
            stopped = true;
            sfxThud();
            // Check
            if (Math.abs(crateX + 20 - targetX) < targetW / 2 + 20) {
              setTimeout(onSuccess, 400);
            } else {
              setTimeout(onFail, 400);
            }
          }
        }
      }
      crateV += accel * dt * 60;
      if (crateV < 0) crateV = 0;
      crateX += crateV * dt;

      // Draw
      ctx.clearRect(0, 0, W, H);
      const sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#0f172a");
      sky.addColorStop(1, "#1e3a5f");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);

      // Surface with friction marks
      ctx.fillStyle = "#8B4513";
      ctx.fillRect(0, groundY, W, H - groundY);
      ctx.strokeStyle = "#a0522d";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, groundY);
      ctx.lineTo(W, groundY);
      ctx.stroke();

      // Friction texture
      ctx.fillStyle = "#00000022";
      for (let i = 0; i < W; i += 20) {
        ctx.fillRect(i, groundY + 5, 10, 2);
      }

      // Target zone
      ctx.fillStyle = "#22c55e44";
      ctx.fillRect(targetX - targetW / 2, groundY - 45, targetW, 45);
      ctx.strokeStyle = "#22c55e";
      ctx.lineWidth = 2;
      ctx.strokeRect(targetX - targetW / 2, groundY - 45, targetW, 45);
      ctx.fillStyle = "#22c55e";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("STOP HERE", targetX, groundY + 16);

      // Crate
      ctx.fillStyle = "#c2884a";
      ctx.fillRect(crateX, groundY - 40, 40, 40);
      ctx.strokeStyle = "#8B4513";
      ctx.lineWidth = 2;
      ctx.strokeRect(crateX, groundY - 40, 40, 40);
      // Crate cross
      ctx.strokeStyle = "#8B451366";
      ctx.beginPath();
      ctx.moveTo(crateX, groundY - 40);
      ctx.lineTo(crateX + 40, groundY);
      ctx.moveTo(crateX + 40, groundY - 40);
      ctx.lineTo(crateX, groundY);
      ctx.stroke();

      // Force arrow
      if (elapsed < pushDuration) {
        ctx.strokeStyle = "#ff6b35";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(crateX - 30, groundY - 20);
        ctx.lineTo(crateX - 5, groundY - 20);
        ctx.stroke();
        ctx.fillStyle = "#ff6b35";
        ctx.beginPath();
        ctx.moveTo(crateX - 5, groundY - 15);
        ctx.lineTo(crateX - 5, groundY - 25);
        ctx.lineTo(crateX + 5, groundY - 20);
        ctx.closePath();
        ctx.fill();
      }

      setLiveStats({
        "Position": `${(crateX / 3).toFixed(1)}m`,
        "Velocity": `${(crateV / 3).toFixed(1)} m/s`,
        "μ": mu.toFixed(2),
      });

      drawParticles(ctx);
      updateParticles(dt);

      if (!stopped && crateX < W + 50) {
        rafRef.current = requestAnimationFrame(frame);
      }
    };
    rafRef.current = requestAnimationFrame(frame);
  }, [simRunning, slider1, targetVal, onSuccess, onFail, drawParticles, updateParticles]);

  // ─── LEVEL 3: Bounce ────────────────────────────────────────────────────────
  const runBounce = useCallback(() => {
    if (simRunning) return;
    setSimRunning(true);
    sfxWhoosh();
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    const groundY = H - 40;
    const restitution = 0.75;
    const angleDeg = slider1;
    const power = slider2 * 0.6;
    const rad = (angleDeg * Math.PI) / 180;
    const basketX = W * (targetVal / 100);
    const basketW = 50;
    const basketY = groundY - 60;

    let bx = 50, by = groundY - 8;
    let bvx = power * Math.cos(rad) * 3;
    let bvy = -power * Math.sin(rad) * 3;
    let prevTs: number | null = null;
    let bounces = 0;
    const trail: { x: number; y: number }[] = [];

    const frame = (ts: number) => {
      if (!prevTs) prevTs = ts;
      const dt = Math.min((ts - prevTs) / 1000, 0.05);
      prevTs = ts;

      bvy += G * 3 * dt * 60;
      bx += bvx * dt;
      by += bvy * dt;

      // Bounce off ground
      if (by >= groundY - 6) {
        by = groundY - 6;
        bvy = -bvy * restitution;
        bounces++;
        sfxThud();
        if (Math.abs(bvy) < 2) bvy = 0;
      }

      // Bounce off walls
      if (bx <= 6) { bx = 6; bvx = -bvx * restitution; }
      if (bx >= W - 6) { bx = W - 6; bvx = -bvx * restitution; }

      // Draw
      ctx.clearRect(0, 0, W, H);
      const sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#0f172a");
      sky.addColorStop(1, "#1e3a5f");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);

      ctx.fillStyle = "#22c55e22";
      ctx.fillRect(0, groundY, W, H - groundY);
      ctx.strokeStyle = "#22c55e66";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, groundY);
      ctx.lineTo(W, groundY);
      ctx.stroke();

      // Walls
      ctx.fillStyle = "#ffffff11";
      ctx.fillRect(0, 0, 4, H);
      ctx.fillRect(W - 4, 0, 4, H);

      // Basket
      ctx.strokeStyle = "#f59e0b";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(basketX - basketW / 2, basketY);
      ctx.lineTo(basketX - basketW / 2, basketY + 30);
      ctx.lineTo(basketX + basketW / 2, basketY + 30);
      ctx.lineTo(basketX + basketW / 2, basketY);
      ctx.stroke();
      ctx.fillStyle = "#f59e0b44";
      ctx.fillRect(basketX - basketW / 2, basketY, basketW, 30);
      ctx.fillStyle = "#f59e0b";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("BASKET", basketX, basketY - 8);

      // Trail
      trail.push({ x: bx, y: by });
      if (trail.length > 60) trail.shift();
      ctx.beginPath();
      ctx.strokeStyle = "#ff6b3544";
      ctx.lineWidth = 1.5;
      trail.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
      ctx.stroke();

      // Ball
      ctx.beginPath();
      ctx.arc(bx, by, 6, 0, Math.PI * 2);
      ctx.fillStyle = "#ff6b35";
      ctx.shadowColor = "#ff6b35";
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;

      setLiveStats({
        "Bounces": `${bounces}`,
        "Velocity": `${(Math.sqrt(bvx * bvx + bvy * bvy) / 3).toFixed(1)} m/s`,
      });

      drawParticles(ctx);
      updateParticles(dt);

      // Check basket
      if (bx > basketX - basketW / 2 && bx < basketX + basketW / 2 &&
          by > basketY && by < basketY + 30 && bvy > 0) {
        spawnParticles(basketX, basketY, "#f59e0b", 15);
        setTimeout(onSuccess, 300);
        return;
      }

      // Timeout / stopped
      if (bounces > 15 || (Math.abs(bvx) < 0.5 && Math.abs(bvy) < 0.5 && by >= groundY - 10)) {
        setTimeout(onFail, 300);
        return;
      }
      if (bx > W + 20) {
        setTimeout(onFail, 100);
        return;
      }

      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);
  }, [simRunning, slider1, slider2, targetVal, onSuccess, onFail, spawnParticles, drawParticles, updateParticles]);

  // ─── LEVEL 4: Pendulum ──────────────────────────────────────────────────────
  const runPendulum = useCallback(() => {
    if (simRunning) return;
    setSimRunning(true);
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    const pivotX = W * 0.35, pivotY = 60;
    const L = 180; // pendulum length in pixels
    const targetX = W * (targetVal / 100);
    const targetW = 40;
    const groundY = H - 40;

    const initAngle = ((slider1 / 100) * 80 - 40) * (Math.PI / 180); // -40 to +40 degrees
    let theta = initAngle;
    let omega = 0;
    let released = false;
    let bobX = pivotX + L * Math.sin(theta);
    let bobY = pivotY + L * Math.cos(theta);
    let bobVx = 0, bobVy = 0;
    let prevTs: number | null = null;
    let clickHandler: ((e: MouseEvent) => void) | null = null;

    // Click to release
    clickHandler = () => {
      if (!released) {
        released = true;
        // Tangential velocity at release
        const tangentSpeed = omega * L;
        bobVx = tangentSpeed * Math.cos(theta);
        bobVy = -tangentSpeed * Math.sin(theta);
        sfxWhoosh();
      }
    };
    canvas.addEventListener("click", clickHandler);

    const frame = (ts: number) => {
      if (!prevTs) prevTs = ts;
      const dt = Math.min((ts - prevTs) / 1000, 0.05);
      prevTs = ts;

      if (!released) {
        // Pendulum physics
        const alpha = -(G * 2.5 / L) * Math.sin(theta);
        omega += alpha * dt * 60;
        omega *= 0.999; // tiny damping
        theta += omega * dt;
        bobX = pivotX + L * Math.sin(theta);
        bobY = pivotY + L * Math.cos(theta);
      } else {
        // Free flight
        bobVy += G * 0.3 * dt * 60;
        bobX += bobVx * dt;
        bobY += bobVy * dt;
      }

      // Draw
      ctx.clearRect(0, 0, W, H);
      const sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#0f172a");
      sky.addColorStop(1, "#1e3a5f");
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, W, H);

      // Ground
      ctx.fillStyle = "#22c55e22";
      ctx.fillRect(0, groundY, W, H - groundY);
      ctx.strokeStyle = "#22c55e66";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, groundY);
      ctx.lineTo(W, groundY);
      ctx.stroke();

      // Target
      ctx.fillStyle = "#f59e0b";
      ctx.fillRect(targetX - targetW / 2, groundY - 20, targetW, 20);
      ctx.fillStyle = "#f59e0b88";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("TARGET", targetX, groundY + 16);

      // Pivot
      ctx.fillStyle = "#888";
      ctx.fillRect(pivotX - 20, pivotY - 5, 40, 10);

      if (!released) {
        // String
        ctx.strokeStyle = "#ccc";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(pivotX, pivotY);
        ctx.lineTo(bobX, bobY);
        ctx.stroke();

        // Click hint
        ctx.fillStyle = "#ffffff88";
        ctx.font = "13px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("Click to release!", W / 2, H - 15);
      }

      // Bob
      ctx.beginPath();
      ctx.arc(bobX, bobY, 12, 0, Math.PI * 2);
      ctx.fillStyle = "#9333ea";
      ctx.shadowColor = "#9333ea";
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.shadowBlur = 0;

      setLiveStats({
        "Angle": `${(theta * 180 / Math.PI).toFixed(1)}°`,
        "Released": released ? "Yes" : "No",
      });

      drawParticles(ctx);
      updateParticles(dt);

      // Check landing
      if (released && bobY >= groundY - 12) {
        sfxThud();
        if (clickHandler) canvas.removeEventListener("click", clickHandler);
        if (Math.abs(bobX - targetX) < targetW / 2 + 12) {
          setTimeout(onSuccess, 300);
        } else {
          setTimeout(onFail, 300);
        }
        return;
      }

      // Off screen
      if (released && (bobX < -50 || bobX > W + 50 || bobY > H + 50)) {
        if (clickHandler) canvas.removeEventListener("click", clickHandler);
        setTimeout(onFail, 100);
        return;
      }

      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);

    // Cleanup
    return () => {
      if (clickHandler) canvas.removeEventListener("click", clickHandler);
    };
  }, [simRunning, slider1, targetVal, onSuccess, onFail, drawParticles, updateParticles]);

  // ─── LEVEL 5: Orbit ─────────────────────────────────────────────────────────
  const runOrbit = useCallback(() => {
    if (simRunning) return;
    setSimRunning(true);
    sfxWhoosh();
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;
    const centerX = W / 2, centerY = H / 2;
    const planetR = 30;
    const GM = 8000; // gravitational parameter
    const orbitR = 100; // initial orbit radius

    // Satellite starts on the right, moving up
    let sx = centerX + orbitR, sy = centerY;
    const launchSpeed = slider1 * 0.06 + 2; // adjustable
    let svx = 0, svy = -launchSpeed * 60;
    let prevTs: number | null = null;
    let elapsed = 0;
    const trail: { x: number; y: number }[] = [];
    let survived = false;

    const frame = (ts: number) => {
      if (!prevTs) prevTs = ts;
      const dt = Math.min((ts - prevTs) / 1000, 0.05);
      prevTs = ts;
      elapsed += dt;

      // Gravity
      const dx = centerX - sx;
      const dy = centerY - sy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const force = GM / (dist * dist);
      const ax = force * (dx / dist);
      const ay = force * (dy / dist);

      svx += ax * dt * 60;
      svy += ay * dt * 60;
      sx += svx * dt;
      sy += svy * dt;

      // Draw
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = "#0a0a1a";
      ctx.fillRect(0, 0, W, H);

      // Stars
      ctx.fillStyle = "#ffffff22";
      for (let i = 0; i < 50; i++) {
        const starX = ((i * 137.5) % W);
        const starY = ((i * 97.3) % H);
        ctx.fillRect(starX, starY, 1, 1);
      }

      // Planet
      const grad = ctx.createRadialGradient(centerX - 8, centerY - 8, 2, centerX, centerY, planetR);
      grad.addColorStop(0, "#4da6ff");
      grad.addColorStop(1, "#1e3a5f");
      ctx.beginPath();
      ctx.arc(centerX, centerY, planetR, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();

      // Atmosphere glow
      ctx.beginPath();
      ctx.arc(centerX, centerY, planetR + 5, 0, Math.PI * 2);
      ctx.strokeStyle = "#4da6ff33";
      ctx.lineWidth = 4;
      ctx.stroke();

      // Trail
      trail.push({ x: sx, y: sy });
      if (trail.length > 200) trail.shift();
      ctx.beginPath();
      ctx.strokeStyle = "#22c55e44";
      ctx.lineWidth = 1.5;
      trail.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
      ctx.stroke();

      // Satellite
      ctx.beginPath();
      ctx.arc(sx, sy, 5, 0, Math.PI * 2);
      ctx.fillStyle = "#f59e0b";
      ctx.shadowColor = "#f59e0b";
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Timer
      ctx.fillStyle = "#fff";
      ctx.font = "14px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(`Orbit time: ${elapsed.toFixed(1)}s / 10s`, W / 2, 25);

      // Progress bar for orbit
      const progress = Math.min(elapsed / 10, 1);
      ctx.fillStyle = "#333";
      ctx.fillRect(W / 2 - 80, 35, 160, 8);
      ctx.fillStyle = "#22c55e";
      ctx.fillRect(W / 2 - 80, 35, 160 * progress, 8);

      setLiveStats({
        "Time": `${elapsed.toFixed(1)}s`,
        "Altitude": `${(dist - planetR).toFixed(0)}px`,
        "Speed": `${(Math.sqrt(svx * svx + svy * svy) / 60).toFixed(1)}`,
      });

      drawParticles(ctx);
      updateParticles(dt);

      // Win condition: survive 10 seconds
      if (elapsed >= 10 && !survived) {
        survived = true;
        spawnParticles(sx, sy, "#f59e0b", 25);
        setTimeout(onSuccess, 300);
        return;
      }

      // Crash into planet
      if (dist < planetR + 5) {
        sfxExplode();
        spawnParticles(sx, sy, "#ff4444", 30);
        setTimeout(onFail, 500);
        return;
      }

      // Escaped too far
      if (dist > W) {
        setTimeout(onFail, 100);
        return;
      }

      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);
  }, [simRunning, slider1, onSuccess, onFail, spawnParticles, drawParticles, updateParticles]);

  // ─── Run current level ──────────────────────────────────────────────────────
  const runLevel = useCallback(() => {
    switch (currentLevel) {
      case 0: runFreeFall(); break;
      case 1: runProjectile(); break;
      case 2: runFriction(); break;
      case 3: runBounce(); break;
      case 4: runPendulum(); break;
      case 5: runOrbit(); break;
    }
  }, [currentLevel, runFreeFall, runProjectile, runFriction, runBounce, runPendulum, runOrbit]);

  // ─── Draw static preview for current level ──────────────────────────────────
  useEffect(() => {
    if (gameState !== "playing" || simRunning) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const { w, h } = getCanvasSize();
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d")!;
    const W = w, H = h;
    const groundY = H - 40;

    // Background
    ctx.clearRect(0, 0, W, H);
    const sky = ctx.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, "#0f172a");
    sky.addColorStop(1, "#1e3a5f");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H);

    switch (currentLevel) {
      case 0: { // Free Fall preview
        ctx.fillStyle = "#22c55e22";
        ctx.fillRect(0, groundY, W, H - groundY);
        ctx.strokeStyle = "#22c55e66";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        ctx.lineTo(W, groundY);
        ctx.stroke();

        const dropHeight = (slider1 / 100) * (H - 100);
        const ballX = W * 0.3;
        const ballY = groundY - dropHeight;
        const targetX = W * (targetVal / 100);

        // Target
        ctx.fillStyle = "#f59e0b";
        ctx.fillRect(targetX - 25, groundY - 4, 50, 8);
        ctx.fillStyle = "#f59e0b88";
        ctx.font = "11px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("TARGET", targetX, groundY + 20);

        // Ball at start
        ctx.beginPath();
        ctx.arc(ballX, ballY, 8, 0, Math.PI * 2);
        ctx.fillStyle = "#4da6ff";
        ctx.fill();

        // Height indicator
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = "#ffffff33";
        ctx.beginPath();
        ctx.moveTo(ballX, ballY + 8);
        ctx.lineTo(ballX, groundY);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = "#ffffff88";
        ctx.font = "11px sans-serif";
        ctx.textAlign = "left";
        ctx.fillText(`${(dropHeight / 3).toFixed(0)}m`, ballX + 12, (ballY + groundY) / 2);
        break;
      }
      case 1: { // Projectile preview
        ctx.fillStyle = "#22c55e22";
        ctx.fillRect(0, groundY, W, H - groundY);
        ctx.strokeStyle = "#22c55e66";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        ctx.lineTo(W, groundY);
        ctx.stroke();

        const targetX = W * (targetVal / 100);
        ctx.fillStyle = "#f59e0b";
        ctx.fillRect(targetX - 20, groundY - 20, 40, 20);
        ctx.fillStyle = "#f59e0b88";
        ctx.font = "11px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("TARGET", targetX, groundY + 16);

        // Cannon
        const rad = (slider2 * Math.PI) / 180;
        ctx.fillStyle = "#555";
        ctx.beginPath();
        ctx.arc(40, groundY, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.save();
        ctx.translate(40, groundY);
        ctx.rotate(-rad);
        ctx.fillStyle = "#888";
        ctx.fillRect(0, -4, 40, 8);
        ctx.restore();

        // Predicted arc
        const v0 = slider1 * 0.8;
        const vx = v0 * Math.cos(rad);
        const vy = v0 * Math.sin(rad);
        const tFlight = (2 * vy) / G;
        ctx.setLineDash([4, 6]);
        ctx.strokeStyle = "#ffffff22";
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 0; i <= 60; i++) {
          const t = (i / 60) * tFlight;
          const x = 40 + vx * t * 3;
          const y = groundY - (vy * t - 0.5 * G * t * t) * 3;
          if (x > W) break;
          i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.setLineDash([]);
        break;
      }
      case 2: { // Friction preview
        const frictionGroundY = H - 60;
        ctx.fillStyle = "#8B4513";
        ctx.fillRect(0, frictionGroundY, W, H - frictionGroundY);
        ctx.strokeStyle = "#a0522d";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, frictionGroundY);
        ctx.lineTo(W, frictionGroundY);
        ctx.stroke();

        const targetX = W * (targetVal / 100);
        ctx.fillStyle = "#22c55e44";
        ctx.fillRect(targetX - 30, frictionGroundY - 45, 60, 45);
        ctx.strokeStyle = "#22c55e";
        ctx.lineWidth = 2;
        ctx.strokeRect(targetX - 30, frictionGroundY - 45, 60, 45);

        // Crate
        ctx.fillStyle = "#c2884a";
        ctx.fillRect(60, frictionGroundY - 40, 40, 40);
        ctx.strokeStyle = "#8B4513";
        ctx.lineWidth = 2;
        ctx.strokeRect(60, frictionGroundY - 40, 40, 40);
        break;
      }
      case 3: { // Bounce preview
        ctx.fillStyle = "#22c55e22";
        ctx.fillRect(0, groundY, W, H - groundY);
        ctx.strokeStyle = "#22c55e66";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        ctx.lineTo(W, groundY);
        ctx.stroke();

        const basketX = W * (targetVal / 100);
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(basketX - 25, groundY - 60);
        ctx.lineTo(basketX - 25, groundY - 30);
        ctx.lineTo(basketX + 25, groundY - 30);
        ctx.lineTo(basketX + 25, groundY - 60);
        ctx.stroke();

        // Ball
        ctx.beginPath();
        ctx.arc(50, groundY - 8, 6, 0, Math.PI * 2);
        ctx.fillStyle = "#ff6b35";
        ctx.fill();
        break;
      }
      case 4: { // Pendulum preview
        ctx.fillStyle = "#22c55e22";
        ctx.fillRect(0, groundY, W, H - groundY);
        ctx.strokeStyle = "#22c55e66";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        ctx.lineTo(W, groundY);
        ctx.stroke();

        const pivotX = W * 0.35, pivotY = 60;
        const L = 180;
        const initAngle = ((slider1 / 100) * 80 - 40) * (Math.PI / 180);
        const bobX = pivotX + L * Math.sin(initAngle);
        const bobY = pivotY + L * Math.cos(initAngle);

        ctx.fillStyle = "#888";
        ctx.fillRect(pivotX - 20, pivotY - 5, 40, 10);
        ctx.strokeStyle = "#ccc";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(pivotX, pivotY);
        ctx.lineTo(bobX, bobY);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(bobX, bobY, 12, 0, Math.PI * 2);
        ctx.fillStyle = "#9333ea";
        ctx.fill();

        const targetX = W * (targetVal / 100);
        ctx.fillStyle = "#f59e0b";
        ctx.fillRect(targetX - 20, groundY - 20, 40, 20);
        break;
      }
      case 5: { // Orbit preview
        ctx.fillStyle = "#0a0a1a";
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = "#ffffff22";
        for (let i = 0; i < 50; i++) {
          ctx.fillRect((i * 137.5) % W, (i * 97.3) % H, 1, 1);
        }
        const cX = W / 2, cY = H / 2;
        const grad = ctx.createRadialGradient(cX - 8, cY - 8, 2, cX, cY, 30);
        grad.addColorStop(0, "#4da6ff");
        grad.addColorStop(1, "#1e3a5f");
        ctx.beginPath();
        ctx.arc(cX, cY, 30, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();

        // Orbit path hint
        ctx.setLineDash([4, 6]);
        ctx.strokeStyle = "#ffffff22";
        ctx.beginPath();
        ctx.arc(cX, cY, 100, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);

        // Satellite
        ctx.beginPath();
        ctx.arc(cX + 100, cY, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#f59e0b";
        ctx.fill();
        break;
      }
    }
  }, [gameState, simRunning, currentLevel, slider1, slider2, targetVal, getCanvasSize]);

  // Cleanup on unmount
  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);

  // ─── Controls for each level ────────────────────────────────────────────────
  const renderControls = () => {
    switch (currentLevel) {
      case 0:
        return (
          <label style={labelStyle}>
            📏 Drop Height: {slider1}%
            <input type="range" min={10} max={95} value={slider1}
              onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
          </label>
        );
      case 1:
        return (
          <>
            <label style={labelStyle}>
              💪 Power: {slider1}%
              <input type="range" min={10} max={100} value={slider1}
                onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <label style={labelStyle}>
              🎯 Angle: {slider2}°
              <input type="range" min={10} max={80} value={slider2}
                onChange={e => setSlider2(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
          </>
        );
      case 2:
        return (
          <label style={labelStyle}>
            💨 Push Force: {slider1}%
            <input type="range" min={10} max={100} value={slider1}
              onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
          </label>
        );
      case 3:
        return (
          <>
            <label style={labelStyle}>
              🎯 Launch Angle: {slider1}°
              <input type="range" min={20} max={80} value={slider1}
                onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <label style={labelStyle}>
              💪 Power: {slider2}%
              <input type="range" min={20} max={100} value={slider2}
                onChange={e => setSlider2(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
          </>
        );
      case 4:
        return (
          <label style={labelStyle}>
            🔄 Start Angle: {((slider1 / 100) * 80 - 40).toFixed(0)}°
            <input type="range" min={0} max={100} value={slider1}
              onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
          </label>
        );
      case 5:
        return (
          <label style={labelStyle}>
            🚀 Launch Speed: {(slider1 * 0.06 + 2).toFixed(1)}
            <input type="range" min={10} max={100} value={slider1}
              onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
          </label>
        );
      default:
        return null;
    }
  };

  // ─── RENDER ─────────────────────────────────────────────────────────────────
  return (
    <div style={{ background: "#0a0a1a", minHeight: "100vh", color: "#fff", fontFamily: "sans-serif", position: "relative" }}>
      {/* Flash overlay */}
      {flash && (
        <div style={{
          position: "fixed", inset: 0, background: flash, zIndex: 100, pointerEvents: "none",
          transition: "opacity 0.2s", opacity: 1,
        }} />
      )}

      {/* Top bar */}
      <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 16px", flexWrap: "wrap" }}>
        <Link href="/" style={{ ...btn, textDecoration: "none" }}>🏠 Home</Link>
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🔬 Physics Fun Quest</h1>
        {gameState === "playing" && (
          <div style={{ marginLeft: "auto", display: "flex", gap: 16, alignItems: "center", fontSize: 13 }}>
            <span>❤️ {lives}</span>
            <span>⭐ {score}</span>
            <span>Level {currentLevel + 1}/6</span>
          </div>
        )}
      </div>

      {/* Progress bar */}
      {gameState === "playing" && (
        <div style={{ padding: "0 16px 8px" }}>
          <div style={{ background: "#333", borderRadius: 4, height: 6, overflow: "hidden" }}>
            <div style={{
              background: "linear-gradient(90deg, #4da6ff, #22c55e)",
              height: "100%", width: `${(currentLevel / 6) * 100}%`,
              transition: "width 0.3s",
            }} />
          </div>
        </div>
      )}

      {/* ─── MENU ──────────────────────────────────────────────────────────── */}
      {gameState === "menu" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 16px", gap: 24 }}>
          <div style={{ ...panelStyle, maxWidth: 500, textAlign: "center", padding: 32 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🔬</div>
            <h2 style={{ margin: "0 0 8px", fontSize: "1.5rem" }}>Physics Fun Quest</h2>
            <p style={{ color: "#94a3b8", margin: "0 0 24px", lineHeight: 1.6 }}>
              Journey through 6 physics challenges! Each level teaches a real physics concept
              through an interactive simulation. Complete all levels to become a Physics Master!
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 24, textAlign: "left" }}>
              {LEVELS.map((l, i) => (
                <div key={i} style={{ padding: "8px 12px", background: "#0a0a1a", borderRadius: 8, fontSize: 12 }}>
                  <span>{l.icon}</span> {l.name}
                </div>
              ))}
            </div>
            <button onClick={startGame} style={{
              ...btn, background: "#4da6ff", border: "none", fontSize: 16, fontWeight: 700,
              padding: "12px 32px", borderRadius: 8, cursor: "pointer",
            }}>
              🚀 Start Quest
            </button>
          </div>
        </div>
      )}

      {/* ─── PLAYING ───────────────────────────────────────────────────────── */}
      {gameState === "playing" && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16, padding: "0 16px 16px", alignItems: "flex-start" }}>
          {/* Canvas */}
          <div style={{ position: "relative" }}>
            <canvas ref={canvasRef} style={{ borderRadius: 12, border: "1px solid #333", maxWidth: "100%", display: "block" }} />
          </div>

          {/* Controls panel */}
          <div style={{ ...panelStyle, minWidth: 220, flex: "0 0 auto", maxWidth: 260 }}>
            {/* Level info */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 20, marginBottom: 4 }}>
                {LEVELS[currentLevel].icon} Level {currentLevel + 1}: {LEVELS[currentLevel].name}
              </div>
              <div style={{ fontSize: 11, color: "#4da6ff", fontFamily: "monospace", marginBottom: 8 }}>
                {LEVELS[currentLevel].equation}
              </div>
              <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.5 }}>
                🎯 {LEVELS[currentLevel].challenge}
              </div>
            </div>

            {/* Sliders */}
            {renderControls()}

            {/* Go button */}
            <button onClick={runLevel} disabled={simRunning} style={{
              ...btn, width: "100%", marginTop: 8,
              background: simRunning ? "#333" : "#22c55e",
              color: "#fff", fontSize: 15, fontWeight: 700, border: "none", padding: "10px 0",
            }}>
              {simRunning ? "Simulating..." : "▶ Go!"}
            </button>

            {/* Live stats */}
            {Object.keys(liveStats).length > 0 && (
              <div style={{ marginTop: 14, fontSize: 12, lineHeight: 1.8 }}>
                {Object.entries(liveStats).map(([k, v]) => (
                  <div key={k}>{k}: <b style={{ color: "#4da6ff" }}>{v}</b></div>
                ))}
              </div>
            )}

            {/* Hint for pendulum */}
            {currentLevel === 4 && simRunning && (
              <div style={{ marginTop: 12, padding: "8px 10px", background: "#0a0a1a", borderRadius: 8, fontSize: 11, color: "#f59e0b" }}>
                💡 Click the canvas to release the pendulum bob!
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── LEVEL COMPLETE ────────────────────────────────────────────────── */}
      {gameState === "levelComplete" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "60px 16px", gap: 20 }}>
          <div style={{ ...panelStyle, maxWidth: 400, textAlign: "center", padding: 32 }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🎉</div>
            <h2 style={{ margin: "0 0 8px" }}>Level Complete!</h2>
            <p style={{ color: "#22c55e", margin: "0 0 4px", fontSize: 14 }}>
              {LEVELS[currentLevel].icon} {LEVELS[currentLevel].name} mastered!
            </p>
            <p style={{ color: "#94a3b8", margin: "0 0 20px", fontSize: 13 }}>
              Score: {score} | Lives: {"❤️".repeat(lives)}
            </p>
            <p style={{ color: "#4da6ff", margin: "0 0 20px", fontSize: 12 }}>
              Next: {LEVELS[currentLevel + 1]?.icon} {LEVELS[currentLevel + 1]?.name}
            </p>
            <button onClick={nextLevel} style={{
              ...btn, background: "#4da6ff", border: "none", fontSize: 15, fontWeight: 700,
              padding: "10px 28px", borderRadius: 8,
            }}>
              ➡️ Next Level
            </button>
          </div>
        </div>
      )}

      {/* ─── VICTORY ───────────────────────────────────────────────────────── */}
      {gameState === "victory" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "60px 16px", gap: 20 }}>
          <div style={{ ...panelStyle, maxWidth: 400, textAlign: "center", padding: 32 }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🏆</div>
            <h2 style={{ margin: "0 0 8px" }}>Physics Master!</h2>
            <p style={{ color: "#f59e0b", margin: "0 0 16px", fontSize: 14 }}>
              You completed all 6 levels!
            </p>
            <p style={{ color: "#22c55e", margin: "0 0 20px", fontSize: 18, fontWeight: 700 }}>
              Final Score: {score}
            </p>
            <button onClick={startGame} style={{
              ...btn, background: "#22c55e", border: "none", fontSize: 15, fontWeight: 700,
              padding: "10px 28px", borderRadius: 8,
            }}>
              🔄 Play Again
            </button>
          </div>
        </div>
      )}

      {/* ─── GAME OVER ─────────────────────────────────────────────────────── */}
      {gameState === "gameOver" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "60px 16px", gap: 20 }}>
          <div style={{ ...panelStyle, maxWidth: 400, textAlign: "center", padding: 32 }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>💥</div>
            <h2 style={{ margin: "0 0 8px" }}>Game Over</h2>
            <p style={{ color: "#ff4444", margin: "0 0 8px", fontSize: 14 }}>
              You ran out of lives!
            </p>
            <p style={{ color: "#94a3b8", margin: "0 0 20px", fontSize: 13 }}>
              Reached Level {currentLevel + 1} | Score: {score}
            </p>
            <button onClick={startGame} style={{
              ...btn, background: "#4da6ff", border: "none", fontSize: 15, fontWeight: 700,
              padding: "10px 28px", borderRadius: 8,
            }}>
              🔄 Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
