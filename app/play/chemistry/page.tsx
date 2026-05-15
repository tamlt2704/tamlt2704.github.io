"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { sfxCorrect, sfxWrong, sfxPop, sfxFanfare, sfxZap, sfxExplode } from "@/app/play/sfx";

// ─── Constants ───────────────────────────────────────────────────────────────
const CANVAS_ASPECT = 16 / 10;
const MAX_W = 700;

interface Particle {
  x: number; y: number; vx: number; vy: number; life: number; color: string;
}

interface LevelDef {
  name: string;
  icon: string;
  concept: string;
  challenge: string;
}

const LEVELS: LevelDef[] = [
  { name: "Atom Builder", icon: "⚛️", concept: "Atomic Structure", challenge: "Build the correct atom" },
  { name: "Balance the Equation", icon: "⚖️", concept: "Conservation of Mass", challenge: "Balance the chemical equation" },
  { name: "pH Scale", icon: "🧪", concept: "Acids & Bases", challenge: "Mix to reach the target pH" },
  { name: "Reaction Speed", icon: "⏱️", concept: "Kinetics", challenge: "Complete the reaction in time" },
  { name: "Electron Transfer", icon: "🔋", concept: "Electrochemistry", challenge: "Build a galvanic cell" },
  { name: "Gas Laws", icon: "💨", concept: "Ideal Gas Law", challenge: "Reach the target pressure" },
];

// ─── Element data for Level 1 ────────────────────────────────────────────────
const ELEMENTS = [
  { name: "Hydrogen", symbol: "H", p: 1, n: 0, e: 1 },
  { name: "Helium", symbol: "He", p: 2, n: 2, e: 2 },
  { name: "Lithium", symbol: "Li", p: 3, n: 4, e: 3 },
  { name: "Carbon", symbol: "C", p: 6, n: 6, e: 6 },
  { name: "Nitrogen", symbol: "N", p: 7, n: 7, e: 7 },
  { name: "Oxygen", symbol: "O", p: 8, n: 8, e: 8 },
  { name: "Sodium", symbol: "Na", p: 11, n: 12, e: 11 },
  { name: "Neon", symbol: "Ne", p: 10, n: 10, e: 10 },
];

// ─── Equation data for Level 2 ───────────────────────────────────────────────
interface Equation {
  display: string;
  compounds: string[];
  atomCounts: Record<string, number[]>; // atom -> count per compound
  answer: number[];
}

const EQUATIONS: Equation[] = [
  {
    display: "_H₂ + _O₂ → _H₂O",
    compounds: ["H₂", "O₂", "H₂O"],
    atomCounts: { H: [2, 0, 2], O: [0, 2, 1] },
    answer: [2, 1, 2],
  },
  {
    display: "_N₂ + _H₂ → _NH₃",
    compounds: ["N₂", "H₂", "NH₃"],
    atomCounts: { N: [2, 0, 1], H: [0, 2, 3] },
    answer: [1, 3, 2],
  },
  {
    display: "_Fe + _O₂ → _Fe₂O₃",
    compounds: ["Fe", "O₂", "Fe₂O₃"],
    atomCounts: { Fe: [1, 0, 2], O: [0, 2, 3] },
    answer: [4, 3, 2],
  },
  {
    display: "_CH₄ + _O₂ → _CO₂ + _H₂O",
    compounds: ["CH₄", "O₂", "CO₂", "H₂O"],
    atomCounts: { C: [1, 0, 1, 0], H: [4, 0, 0, 2], O: [0, 2, 2, 1] },
    answer: [1, 2, 1, 2],
  },
];

// ─── Metal data for Level 5 ──────────────────────────────────────────────────
interface Metal {
  name: string;
  symbol: string;
  potential: number; // standard reduction potential in V
}

const METALS: Metal[] = [
  { name: "Zinc", symbol: "Zn", potential: -0.76 },
  { name: "Iron", symbol: "Fe", potential: -0.44 },
  { name: "Copper", symbol: "Cu", potential: 0.34 },
  { name: "Silver", symbol: "Ag", potential: 0.80 },
  { name: "Gold", symbol: "Au", potential: 1.50 },
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
  width: "100%", display: "block", marginTop: 6, accentColor: "#a855f7",
};
const panelStyle: React.CSSProperties = {
  background: "#1a1a2e", borderRadius: 12, border: "1px solid #333", padding: 16,
};

// ─── Main Component ──────────────────────────────────────────────────────────
export default function ChemistryQuestPage() {
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
  const [slider1, setSlider1] = useState(1);
  const [slider2, setSlider2] = useState(1);
  const [slider3, setSlider3] = useState(1);
  const [slider4, setSlider4] = useState(1);
  const [catalystOn, setCatalystOn] = useState(false);
  const [selectedAnode, setSelectedAnode] = useState(0);
  const [selectedCathode, setSelectedCathode] = useState(2);
  const [currentPH, setCurrentPH] = useState(7);

  // Level-specific targets
  const [targetElement, setTargetElement] = useState(0);
  const [targetEquation, setTargetEquation] = useState(0);
  const [targetPH, setTargetPH] = useState(7);
  const [targetTime, setTargetTime] = useState(8);
  const [targetVoltage, setTargetVoltage] = useState(1.1);
  const [targetPressure, setTargetPressure] = useState(2);

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
    particlesRef.current = [];
    cancelAnimationFrame(rafRef.current);

    switch (lvl) {
      case 0: { // Atom Builder
        const el = Math.floor(Math.random() * ELEMENTS.length);
        setTargetElement(el);
        setSlider1(1);
        setSlider2(0);
        setSlider3(1);
        break;
      }
      case 1: { // Balance Equation
        const eq = Math.floor(Math.random() * EQUATIONS.length);
        setTargetEquation(eq);
        setSlider1(1);
        setSlider2(1);
        setSlider3(1);
        setSlider4(1);
        break;
      }
      case 2: { // pH Scale
        const ph = Math.floor(Math.random() * 10) + 2; // 2-11
        setTargetPH(ph);
        setCurrentPH(7);
        break;
      }
      case 3: { // Reaction Speed
        const time = 6 + Math.floor(Math.random() * 5); // 6-10 seconds
        setTargetTime(time);
        setSlider1(25); // temperature
        setCatalystOn(false);
        break;
      }
      case 4: { // Electron Transfer
        const v = [0.78, 1.10, 1.56, 1.94, 2.26][Math.floor(Math.random() * 5)];
        setTargetVoltage(v);
        setSelectedAnode(0);
        setSelectedCathode(2);
        break;
      }
      case 5: { // Gas Laws
        const p = 1.5 + Math.random() * 2.5; // 1.5-4.0 atm
        setTargetPressure(Math.round(p * 10) / 10);
        setSlider1(50); // volume
        setSlider2(50); // temperature
        break;
      }
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


  // ─── LEVEL 0: Atom Builder ──────────────────────────────────────────────────
  const checkAtom = useCallback(() => {
    const el = ELEMENTS[targetElement];
    if (slider1 === el.p && slider2 === el.n && slider3 === el.e) {
      sfxPop();
      onSuccess();
    } else {
      onFail();
    }
  }, [targetElement, slider1, slider2, slider3, onSuccess, onFail]);

  // ─── LEVEL 1: Balance Equation ──────────────────────────────────────────────
  const checkEquation = useCallback(() => {
    const eq = EQUATIONS[targetEquation];
    const coeffs = [slider1, slider2, slider3, slider4].slice(0, eq.compounds.length);
    // Check each atom type
    let balanced = true;
    for (const atom of Object.keys(eq.atomCounts)) {
      const counts = eq.atomCounts[atom];
      // Reactants are before the arrow (first compounds), products after
      // For simplicity: first N-1 are reactants for 3-compound, or first 2 for 4-compound
      const numReactants = eq.compounds.length <= 3 ? 2 : 2;
      let leftSum = 0;
      let rightSum = 0;
      for (let i = 0; i < counts.length; i++) {
        if (i < numReactants) {
          leftSum += coeffs[i] * counts[i];
        } else {
          rightSum += coeffs[i] * counts[i];
        }
      }
      if (leftSum !== rightSum || leftSum === 0) {
        balanced = false;
        break;
      }
    }
    if (balanced) {
      sfxPop();
      onSuccess();
    } else {
      onFail();
    }
  }, [targetEquation, slider1, slider2, slider3, slider4, onSuccess, onFail]);

  // ─── LEVEL 2: pH Scale ──────────────────────────────────────────────────────
  const addAcid = useCallback(() => {
    sfxPop();
    setCurrentPH(prev => Math.max(0, Math.round((prev - 0.5) * 10) / 10));
  }, []);

  const addBase = useCallback(() => {
    sfxPop();
    setCurrentPH(prev => Math.min(14, Math.round((prev + 0.5) * 10) / 10));
  }, []);

  const checkPH = useCallback(() => {
    if (Math.abs(currentPH - targetPH) <= 0.5) {
      onSuccess();
    } else {
      onFail();
    }
  }, [currentPH, targetPH, onSuccess, onFail]);

  // ─── LEVEL 3: Reaction Speed ────────────────────────────────────────────────
  const runReaction = useCallback(() => {
    if (simRunning) return;
    setSimRunning(true);
    sfxZap();
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width, H = canvas.height;

    const temperature = slider1; // 0-100
    const catalyst = catalystOn;
    const speedMultiplier = (temperature / 50) * (catalyst ? 2.5 : 1);
    const reactionDuration = 12 / speedMultiplier; // seconds to complete

    interface Molecule {
      x: number; y: number; vx: number; vy: number; type: number; reacted: boolean;
    }

    const molecules: Molecule[] = [];
    for (let i = 0; i < 30; i++) {
      molecules.push({
        x: 80 + Math.random() * (W - 160),
        y: 80 + Math.random() * (H - 160),
        vx: (Math.random() - 0.5) * 2 * speedMultiplier,
        vy: (Math.random() - 0.5) * 2 * speedMultiplier,
        type: i % 2,
        reacted: false,
      });
    }

    let elapsed = 0;
    let progress = 0;
    let prevTs: number | null = null;

    const frame = (ts: number) => {
      if (!prevTs) prevTs = ts;
      const dt = Math.min((ts - prevTs) / 1000, 0.05);
      prevTs = ts;
      elapsed += dt;
      progress = Math.min(elapsed / reactionDuration, 1);

      // Update molecules
      const speed = speedMultiplier * 60;
      molecules.forEach(m => {
        if (m.reacted) return;
        m.x += m.vx * dt * speed * 0.5;
        m.y += m.vy * dt * speed * 0.5;
        // Bounce off walls
        if (m.x < 60 || m.x > W - 60) m.vx *= -1;
        if (m.y < 60 || m.y > H - 60) m.vy *= -1;
        m.x = Math.max(60, Math.min(W - 60, m.x));
        m.y = Math.max(60, Math.min(H - 60, m.y));
      });

      // Check collisions - react pairs
      for (let i = 0; i < molecules.length; i++) {
        if (molecules[i].reacted) continue;
        for (let j = i + 1; j < molecules.length; j++) {
          if (molecules[j].reacted) continue;
          if (molecules[i].type === molecules[j].type) continue;
          const dx = molecules[i].x - molecules[j].x;
          const dy = molecules[i].y - molecules[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 20 && Math.random() < 0.02 * speedMultiplier) {
            molecules[i].reacted = true;
            molecules[j].reacted = true;
            spawnParticles((molecules[i].x + molecules[j].x) / 2, (molecules[i].y + molecules[j].y) / 2, "#f59e0b", 5);
          }
        }
      }

      // Draw
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = "#0f172a";
      ctx.fillRect(0, 0, W, H);

      // Beaker outline
      ctx.strokeStyle = "#4da6ff44";
      ctx.lineWidth = 2;
      ctx.strokeRect(50, 50, W - 100, H - 100);

      // Temperature indicator
      const tempColor = temperature > 70 ? "#ff4444" : temperature > 40 ? "#f59e0b" : "#4da6ff";
      ctx.fillStyle = tempColor + "22";
      ctx.fillRect(50, 50, W - 100, H - 100);

      // Molecules
      molecules.forEach(m => {
        if (m.reacted) return;
        ctx.beginPath();
        ctx.arc(m.x, m.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = m.type === 0 ? "#ff6b6b" : "#4da6ff";
        ctx.shadowColor = m.type === 0 ? "#ff6b6b" : "#4da6ff";
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      // Catalyst indicator
      if (catalyst) {
        ctx.fillStyle = "#22c55e";
        ctx.font = "11px sans-serif";
        ctx.textAlign = "left";
        ctx.fillText("⚡ Catalyst Active", 60, H - 20);
      }

      // Progress bar
      ctx.fillStyle = "#333";
      ctx.fillRect(50, 30, W - 100, 12);
      ctx.fillStyle = progress >= 1 ? "#22c55e" : "#f59e0b";
      ctx.fillRect(50, 30, (W - 100) * progress, 12);
      ctx.fillStyle = "#fff";
      ctx.font = "10px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(`${(progress * 100).toFixed(0)}%`, W / 2, 40);

      // Timer
      ctx.fillStyle = "#fff";
      ctx.font = "13px sans-serif";
      ctx.textAlign = "right";
      ctx.fillText(`Time: ${elapsed.toFixed(1)}s / ${targetTime}s`, W - 20, 20);

      drawParticles(ctx);
      updateParticles(dt);

      // Check completion
      if (progress >= 1) {
        if (elapsed <= targetTime) {
          setTimeout(onSuccess, 300);
        } else {
          setTimeout(onFail, 300);
        }
        return;
      }

      // Timeout
      if (elapsed > targetTime && progress < 1) {
        setTimeout(onFail, 300);
        return;
      }

      rafRef.current = requestAnimationFrame(frame);
    };
    rafRef.current = requestAnimationFrame(frame);
  }, [simRunning, slider1, catalystOn, targetTime, onSuccess, onFail, spawnParticles, drawParticles, updateParticles]);

  // ─── LEVEL 4: Electron Transfer ────────────────────────────────────────────
  const checkCell = useCallback(() => {
    const anode = METALS[selectedAnode];
    const cathode = METALS[selectedCathode];
    // Voltage = cathode potential - anode potential
    const voltage = cathode.potential - anode.potential;
    if (voltage > 0 && Math.abs(voltage - targetVoltage) < 0.15) {
      sfxZap();
      onSuccess();
    } else {
      onFail();
    }
  }, [selectedAnode, selectedCathode, targetVoltage, onSuccess, onFail]);

  // ─── LEVEL 5: Gas Laws ──────────────────────────────────────────────────────
  const checkGas = useCallback(() => {
    // PV = nRT, P = nRT/V
    // Normalize: at slider1=50, slider2=50 → P=1 atm
    const volume = slider1 / 50; // relative volume (0.02 to 2)
    const temperature = (slider2 / 50) * 300; // K (0 to 600)
    const nR = 1; // constant
    const pressure = (nR * temperature) / (volume * 300); // normalized
    if (Math.abs(pressure - targetPressure) < 0.3) {
      sfxPop();
      onSuccess();
    } else {
      onFail();
    }
  }, [slider1, slider2, targetPressure, onSuccess, onFail]);


  // ─── Run current level ──────────────────────────────────────────────────────
  const runLevel = useCallback(() => {
    switch (currentLevel) {
      case 0: checkAtom(); break;
      case 1: checkEquation(); break;
      case 2: checkPH(); break;
      case 3: runReaction(); break;
      case 4: checkCell(); break;
      case 5: checkGas(); break;
    }
  }, [currentLevel, checkAtom, checkEquation, checkPH, runReaction, checkCell, checkGas]);

  // ─── pH color helper ────────────────────────────────────────────────────────
  const getPHColor = useCallback((ph: number): string => {
    if (ph <= 1) return "#ff0000";
    if (ph <= 3) return "#ff6600";
    if (ph <= 5) return "#cccc00";
    if (ph <= 6) return "#88cc00";
    if (ph <= 8) return "#00cc44";
    if (ph <= 9) return "#0088cc";
    if (ph <= 11) return "#6600cc";
    if (ph <= 13) return "#9900cc";
    return "#cc00ff";
  }, []);

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

    // Background
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, W, H);

    switch (currentLevel) {
      case 0: { // Atom Builder
        const el = ELEMENTS[targetElement];
        const centerX = W / 2, centerY = H / 2;

        // Draw electron shells
        const shells = [1, 2, 3];
        shells.forEach((_, i) => {
          ctx.beginPath();
          ctx.arc(centerX, centerY, 50 + i * 40, 0, Math.PI * 2);
          ctx.strokeStyle = "#ffffff22";
          ctx.lineWidth = 1;
          ctx.stroke();
        });

        // Draw nucleus (protons + neutrons)
        const nucleusR = 25;
        for (let i = 0; i < slider1; i++) {
          const angle = (i / Math.max(slider1, 1)) * Math.PI * 2;
          const r = i < 4 ? 8 : 16;
          const px = centerX + Math.cos(angle) * r;
          const py = centerY + Math.sin(angle) * r;
          ctx.beginPath();
          ctx.arc(px, py, 5, 0, Math.PI * 2);
          ctx.fillStyle = "#ff4444";
          ctx.fill();
        }
        for (let i = 0; i < slider2; i++) {
          const angle = (i / Math.max(slider2, 1)) * Math.PI * 2 + 0.3;
          const r = i < 4 ? 10 : 18;
          const px = centerX + Math.cos(angle) * r;
          const py = centerY + Math.sin(angle) * r;
          ctx.beginPath();
          ctx.arc(px, py, 5, 0, Math.PI * 2);
          ctx.fillStyle = "#888888";
          ctx.fill();
        }

        // Draw electrons on shells
        let eCount = 0;
        const shellCapacity = [2, 8, 8];
        for (let shell = 0; shell < 3 && eCount < slider3; shell++) {
          const shellR = 50 + shell * 40;
          const electronsInShell = Math.min(shellCapacity[shell], slider3 - eCount);
          for (let e = 0; e < electronsInShell; e++) {
            const angle = (e / electronsInShell) * Math.PI * 2 + Date.now() * 0.001;
            const ex = centerX + Math.cos(angle) * shellR;
            const ey = centerY + Math.sin(angle) * shellR;
            ctx.beginPath();
            ctx.arc(ex, ey, 4, 0, Math.PI * 2);
            ctx.fillStyle = "#4da6ff";
            ctx.shadowColor = "#4da6ff";
            ctx.shadowBlur = 6;
            ctx.fill();
            ctx.shadowBlur = 0;
          }
          eCount += electronsInShell;
        }

        // Labels
        ctx.fillStyle = "#fff";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`Build: ${el.name} (${el.symbol})`, W / 2, 30);
        ctx.fillStyle = "#ff4444";
        ctx.fillText(`Protons: ${slider1}`, W / 2 - 120, H - 30);
        ctx.fillStyle = "#888";
        ctx.fillText(`Neutrons: ${slider2}`, W / 2, H - 30);
        ctx.fillStyle = "#4da6ff";
        ctx.fillText(`Electrons: ${slider3}`, W / 2 + 120, H - 30);

        drawParticles(ctx);
        break;
      }

      case 1: { // Balance Equation
        const eq = EQUATIONS[targetEquation];
        const coeffs = [slider1, slider2, slider3, slider4].slice(0, eq.compounds.length);
        const numReactants = 2;

        // Draw equation text
        ctx.fillStyle = "#fff";
        ctx.font = "16px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(eq.display, W / 2, 30);

        // Draw atom circles on each side
        const atomColors: Record<string, string> = { H: "#ffffff", O: "#ff4444", N: "#4da6ff", C: "#333333", Fe: "#cc8844" };
        const leftX = W * 0.25, rightX = W * 0.75;
        const midY = H / 2;

        // Left side (reactants)
        let leftAtoms: { atom: string; count: number }[] = [];
        let rightAtoms: { atom: string; count: number }[] = [];

        for (const atom of Object.keys(eq.atomCounts)) {
          let leftCount = 0, rightCount = 0;
          for (let i = 0; i < eq.atomCounts[atom].length; i++) {
            if (i < numReactants) {
              leftCount += coeffs[i] * eq.atomCounts[atom][i];
            } else {
              rightCount += coeffs[i] * eq.atomCounts[atom][i];
            }
          }
          leftAtoms.push({ atom, count: leftCount });
          rightAtoms.push({ atom, count: rightCount });
        }

        // Draw left atoms
        let yOff = 0;
        leftAtoms.forEach(({ atom, count }) => {
          for (let i = 0; i < Math.min(count, 12); i++) {
            const row = Math.floor(i / 4);
            const col = i % 4;
            ctx.beginPath();
            ctx.arc(leftX - 40 + col * 22, midY - 30 + yOff + row * 22, 9, 0, Math.PI * 2);
            ctx.fillStyle = atomColors[atom] || "#aaa";
            ctx.fill();
            ctx.strokeStyle = "#ffffff44";
            ctx.lineWidth = 1;
            ctx.stroke();
          }
          ctx.fillStyle = "#ccc";
          ctx.font = "11px sans-serif";
          ctx.textAlign = "left";
          ctx.fillText(`${atom}: ${count}`, leftX + 50, midY - 20 + yOff);
          yOff += 55;
        });

        // Arrow
        ctx.fillStyle = "#fff";
        ctx.font = "24px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("→", W / 2, midY + 10);

        // Draw right atoms
        yOff = 0;
        rightAtoms.forEach(({ atom, count }) => {
          for (let i = 0; i < Math.min(count, 12); i++) {
            const row = Math.floor(i / 4);
            const col = i % 4;
            ctx.beginPath();
            ctx.arc(rightX - 40 + col * 22, midY - 30 + yOff + row * 22, 9, 0, Math.PI * 2);
            ctx.fillStyle = atomColors[atom] || "#aaa";
            ctx.fill();
            ctx.strokeStyle = "#ffffff44";
            ctx.lineWidth = 1;
            ctx.stroke();
          }
          ctx.fillStyle = "#ccc";
          ctx.font = "11px sans-serif";
          ctx.textAlign = "left";
          ctx.fillText(`${atom}: ${count}`, rightX + 50, midY - 20 + yOff);
          yOff += 55;
        });

        // Balance indicator
        let isBalanced = true;
        for (const atom of Object.keys(eq.atomCounts)) {
          let l = 0, r = 0;
          for (let i = 0; i < eq.atomCounts[atom].length; i++) {
            if (i < numReactants) l += coeffs[i] * eq.atomCounts[atom][i];
            else r += coeffs[i] * eq.atomCounts[atom][i];
          }
          if (l !== r) { isBalanced = false; break; }
        }
        ctx.fillStyle = isBalanced ? "#22c55e" : "#ff4444";
        ctx.font = "13px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(isBalanced ? "✓ Balanced!" : "✗ Not balanced", W / 2, H - 20);

        drawParticles(ctx);
        break;
      }

      case 2: { // pH Scale
        // Beaker
        const beakerX = W / 2 - 60, beakerY = 60, beakerW = 120, beakerH = H - 120;
        ctx.strokeStyle = "#4da6ff66";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(beakerX, beakerY);
        ctx.lineTo(beakerX, beakerY + beakerH);
        ctx.lineTo(beakerX + beakerW, beakerY + beakerH);
        ctx.lineTo(beakerX + beakerW, beakerY);
        ctx.stroke();

        // Liquid
        const liquidH = beakerH * 0.75;
        const liquidY = beakerY + beakerH - liquidH;
        const phColor = getPHColor(currentPH);
        ctx.fillStyle = phColor + "88";
        ctx.fillRect(beakerX + 3, liquidY, beakerW - 6, liquidH - 3);

        // Bubbles
        for (let i = 0; i < 8; i++) {
          const bx = beakerX + 15 + Math.random() * (beakerW - 30);
          const by = liquidY + Math.random() * liquidH;
          ctx.beginPath();
          ctx.arc(bx, by, 2 + Math.random() * 3, 0, Math.PI * 2);
          ctx.fillStyle = "#ffffff22";
          ctx.fill();
        }

        // pH meter display
        ctx.fillStyle = "#1a1a2e";
        ctx.fillRect(W - 140, 60, 120, 60);
        ctx.strokeStyle = "#333";
        ctx.strokeRect(W - 140, 60, 120, 60);
        ctx.fillStyle = phColor;
        ctx.font = "bold 24px monospace";
        ctx.textAlign = "center";
        ctx.fillText(`pH ${currentPH.toFixed(1)}`, W - 80, 100);
        ctx.fillStyle = "#888";
        ctx.font = "11px sans-serif";
        ctx.fillText(`Target: pH ${targetPH}`, W - 80, 115);

        // pH scale bar
        const scaleX = 30, scaleY = 60, scaleH = H - 120;
        for (let i = 0; i <= 14; i++) {
          const y = scaleY + (i / 14) * scaleH;
          ctx.fillStyle = getPHColor(i);
          ctx.fillRect(scaleX, y, 20, scaleH / 14);
        }
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        const indicatorY = scaleY + (currentPH / 14) * scaleH;
        ctx.beginPath();
        ctx.moveTo(scaleX + 22, indicatorY);
        ctx.lineTo(scaleX + 32, indicatorY - 5);
        ctx.lineTo(scaleX + 32, indicatorY + 5);
        ctx.closePath();
        ctx.fillStyle = "#fff";
        ctx.fill();

        // Target line
        const targetY = scaleY + (targetPH / 14) * scaleH;
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = "#f59e0b";
        ctx.beginPath();
        ctx.moveTo(scaleX, targetY);
        ctx.lineTo(scaleX + 20, targetY);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = "#fff";
        ctx.font = "13px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`Mix to reach pH ${targetPH}`, W / 2, 30);

        drawParticles(ctx);
        break;
      }

      case 3: { // Reaction Speed - static preview
        ctx.fillStyle = "#fff";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`Complete the reaction in under ${targetTime}s`, W / 2, 30);

        // Preview molecules
        ctx.strokeStyle = "#4da6ff44";
        ctx.lineWidth = 2;
        ctx.strokeRect(50, 50, W - 100, H - 100);

        for (let i = 0; i < 20; i++) {
          const mx = 80 + Math.random() * (W - 160);
          const my = 80 + Math.random() * (H - 160);
          ctx.beginPath();
          ctx.arc(mx, my, 8, 0, Math.PI * 2);
          ctx.fillStyle = i % 2 === 0 ? "#ff6b6b" : "#4da6ff";
          ctx.fill();
        }

        // Temperature gauge
        ctx.fillStyle = "#333";
        ctx.fillRect(W - 40, 60, 20, H - 120);
        const tempH = (slider1 / 100) * (H - 120);
        const tempColor = slider1 > 70 ? "#ff4444" : slider1 > 40 ? "#f59e0b" : "#4da6ff";
        ctx.fillStyle = tempColor;
        ctx.fillRect(W - 40, 60 + (H - 120) - tempH, 20, tempH);
        ctx.fillStyle = "#fff";
        ctx.font = "10px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`${slider1}°`, W - 30, H - 30);

        drawParticles(ctx);
        break;
      }

      case 4: { // Electron Transfer
        const anode = METALS[selectedAnode];
        const cathode = METALS[selectedCathode];
        const voltage = cathode.potential - anode.potential;
        const centerY = H / 2;

        // Left half-cell (anode)
        ctx.fillStyle = "#1e3a5f44";
        ctx.fillRect(40, centerY - 60, 120, 120);
        ctx.strokeStyle = "#4da6ff66";
        ctx.lineWidth = 2;
        ctx.strokeRect(40, centerY - 60, 120, 120);

        // Anode metal plate
        ctx.fillStyle = "#cc8844";
        ctx.fillRect(85, centerY - 40, 20, 80);
        ctx.fillStyle = "#fff";
        ctx.font = "12px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(anode.symbol, 95, centerY + 60);
        ctx.fillText("Anode (−)", 100, centerY - 70);

        // Right half-cell (cathode)
        ctx.fillStyle = "#1e3a5f44";
        ctx.fillRect(W - 160, centerY - 60, 120, 120);
        ctx.strokeStyle = "#4da6ff66";
        ctx.lineWidth = 2;
        ctx.strokeRect(W - 160, centerY - 60, 120, 120);

        // Cathode metal plate
        ctx.fillStyle = "#aaaaaa";
        ctx.fillRect(W - 115, centerY - 40, 20, 80);
        ctx.fillStyle = "#fff";
        ctx.font = "12px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(cathode.symbol, W - 105, centerY + 60);
        ctx.fillText("Cathode (+)", W - 100, centerY - 70);

        // Wire connecting them
        ctx.strokeStyle = "#888";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(95, centerY - 45);
        ctx.lineTo(95, 40);
        ctx.lineTo(W - 105, 40);
        ctx.lineTo(W - 105, centerY - 45);
        ctx.stroke();

        // Electron flow dots
        if (voltage > 0) {
          const t = Date.now() * 0.003;
          for (let i = 0; i < 5; i++) {
            const frac = ((t + i * 0.2) % 1);
            let ex: number, ey: number;
            if (frac < 0.3) {
              ex = 95;
              ey = centerY - 45 - (frac / 0.3) * (centerY - 85);
            } else if (frac < 0.7) {
              ex = 95 + ((frac - 0.3) / 0.4) * (W - 200);
              ey = 40;
            } else {
              ex = W - 105;
              ey = 40 + ((frac - 0.7) / 0.3) * (centerY - 85);
            }
            ctx.beginPath();
            ctx.arc(ex, ey, 3, 0, Math.PI * 2);
            ctx.fillStyle = "#ffdd00";
            ctx.shadowColor = "#ffdd00";
            ctx.shadowBlur = 6;
            ctx.fill();
            ctx.shadowBlur = 0;
          }
        }

        // Voltmeter
        ctx.fillStyle = "#1a1a2e";
        ctx.fillRect(W / 2 - 50, 60, 100, 50);
        ctx.strokeStyle = "#333";
        ctx.strokeRect(W / 2 - 50, 60, 100, 50);
        ctx.fillStyle = voltage > 0 ? "#22c55e" : "#ff4444";
        ctx.font = "bold 18px monospace";
        ctx.textAlign = "center";
        ctx.fillText(`${voltage.toFixed(2)}V`, W / 2, 92);
        ctx.fillStyle = "#888";
        ctx.font = "10px sans-serif";
        ctx.fillText(`Target: ${targetVoltage.toFixed(2)}V`, W / 2, 107);

        // Info
        ctx.fillStyle = "#fff";
        ctx.font = "13px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`Create a battery producing ${targetVoltage.toFixed(2)}V`, W / 2, 25);

        drawParticles(ctx);
        break;
      }

      case 5: { // Gas Laws
        const volume = slider1 / 50; // relative
        const temperature = (slider2 / 50) * 300; // K
        const pressure = (1 * temperature) / (volume * 300);

        // Cylinder
        const cylX = W / 2 - 80, cylW = 160;
        const maxCylH = H - 100;
        const cylH = maxCylH * Math.min(volume, 2) / 2;
        const cylY = 50 + maxCylH - cylH;

        // Cylinder walls
        ctx.strokeStyle = "#4da6ff66";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(cylX, 50);
        ctx.lineTo(cylX, 50 + maxCylH);
        ctx.lineTo(cylX + cylW, 50 + maxCylH);
        ctx.lineTo(cylX + cylW, 50);
        ctx.stroke();

        // Piston
        ctx.fillStyle = "#888";
        ctx.fillRect(cylX + 2, cylY - 10, cylW - 4, 12);
        ctx.fillStyle = "#666";
        ctx.fillRect(W / 2 - 5, cylY - 40, 10, 30);

        // Gas molecules
        const numMolecules = 25;
        const gasArea = { x: cylX + 10, y: cylY + 5, w: cylW - 20, h: (50 + maxCylH) - cylY - 10 };
        for (let i = 0; i < numMolecules; i++) {
          const mx = gasArea.x + Math.random() * gasArea.w;
          const my = gasArea.y + Math.random() * Math.max(gasArea.h, 20);
          ctx.beginPath();
          ctx.arc(mx, my, 3, 0, Math.PI * 2);
          ctx.fillStyle = temperature > 400 ? "#ff6b6b" : temperature > 200 ? "#f59e0b" : "#4da6ff";
          ctx.fill();
        }

        // Pressure gauge
        ctx.fillStyle = "#1a1a2e";
        ctx.fillRect(20, 60, 100, 50);
        ctx.strokeStyle = "#333";
        ctx.strokeRect(20, 60, 100, 50);
        ctx.fillStyle = pressure > targetPressure + 0.3 ? "#ff4444" : pressure < targetPressure - 0.3 ? "#4da6ff" : "#22c55e";
        ctx.font = "bold 16px monospace";
        ctx.textAlign = "center";
        ctx.fillText(`${pressure.toFixed(2)} atm`, 70, 90);
        ctx.fillStyle = "#888";
        ctx.font = "10px sans-serif";
        ctx.fillText(`Target: ${targetPressure.toFixed(1)} atm`, 70, 105);

        // Info
        ctx.fillStyle = "#fff";
        ctx.font = "13px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`Reach target pressure: ${targetPressure.toFixed(1)} atm`, W / 2, 25);
        ctx.fillStyle = "#94a3b8";
        ctx.font = "11px sans-serif";
        ctx.fillText(`PV = nRT`, W / 2, H - 15);

        drawParticles(ctx);
        break;
      }
    }
  }, [gameState, simRunning, currentLevel, slider1, slider2, slider3, slider4,
      targetElement, targetEquation, targetPH, targetTime, targetVoltage, targetPressure,
      currentPH, selectedAnode, selectedCathode, catalystOn, getCanvasSize, getPHColor, drawParticles]);

  // Cleanup on unmount
  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);


  // ─── Controls for each level ────────────────────────────────────────────────
  const renderControls = () => {
    switch (currentLevel) {
      case 0: { // Atom Builder
        const el = ELEMENTS[targetElement];
        return (
          <>
            <label style={labelStyle}>
              🔴 Protons: {slider1}
              <input type="range" min={1} max={15} value={slider1}
                onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <label style={labelStyle}>
              ⚪ Neutrons: {slider2}
              <input type="range" min={0} max={16} value={slider2}
                onChange={e => setSlider2(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <label style={labelStyle}>
              🔵 Electrons: {slider3}
              <input type="range" min={1} max={15} value={slider3}
                onChange={e => setSlider3(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>
              Target: {el.name} ({el.symbol})
            </div>
          </>
        );
      }
      case 1: { // Balance Equation
        const eq = EQUATIONS[targetEquation];
        return (
          <>
            {eq.compounds.map((compound, i) => (
              <label key={i} style={labelStyle}>
                {i < 2 ? "⬅️" : "➡️"} {compound}: {[slider1, slider2, slider3, slider4][i]}
                <input type="range" min={1} max={6}
                  value={[slider1, slider2, slider3, slider4][i]}
                  onChange={e => {
                    const v = +e.target.value;
                    if (i === 0) setSlider1(v);
                    else if (i === 1) setSlider2(v);
                    else if (i === 2) setSlider3(v);
                    else setSlider4(v);
                  }}
                  disabled={simRunning} style={sliderStyle} />
              </label>
            ))}
          </>
        );
      }
      case 2: // pH Scale
        return (
          <>
            <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>
              Current pH: <b style={{ color: getPHColor(currentPH) }}>{currentPH.toFixed(1)}</b>
              <br />Target pH: <b style={{ color: "#f59e0b" }}>{targetPH}</b>
            </div>
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
              <button onClick={addAcid} disabled={simRunning} style={{
                ...btn, flex: 1, background: "#ff444444", borderColor: "#ff4444",
              }}>
                🧪 + Acid
              </button>
              <button onClick={addBase} disabled={simRunning} style={{
                ...btn, flex: 1, background: "#4da6ff44", borderColor: "#4da6ff",
              }}>
                🧴 + Base
              </button>
            </div>
          </>
        );
      case 3: // Reaction Speed
        return (
          <>
            <label style={labelStyle}>
              🌡️ Temperature: {slider1}°C
              <input type="range" min={10} max={100} value={slider1}
                onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: 8 }}>
              <input type="checkbox" checked={catalystOn}
                onChange={e => setCatalystOn(e.target.checked)} disabled={simRunning} />
              ⚡ Catalyst
            </label>
            <div style={{ fontSize: 11, color: "#94a3b8" }}>
              Time limit: {targetTime}s
            </div>
          </>
        );
      case 4: // Electron Transfer
        return (
          <>
            <label style={labelStyle}>
              ⊖ Anode (oxidation):
              <select value={selectedAnode} onChange={e => setSelectedAnode(+e.target.value)}
                disabled={simRunning}
                style={{ ...btn, width: "100%", marginTop: 4, padding: "8px 10px" }}>
                {METALS.map((m, i) => (
                  <option key={i} value={i}>{m.name} ({m.symbol}) E°={m.potential}V</option>
                ))}
              </select>
            </label>
            <label style={labelStyle}>
              ⊕ Cathode (reduction):
              <select value={selectedCathode} onChange={e => setSelectedCathode(+e.target.value)}
                disabled={simRunning}
                style={{ ...btn, width: "100%", marginTop: 4, padding: "8px 10px" }}>
                {METALS.map((m, i) => (
                  <option key={i} value={i}>{m.name} ({m.symbol}) E°={m.potential}V</option>
                ))}
              </select>
            </label>
            <div style={{ fontSize: 11, color: "#94a3b8" }}>
              Target: {targetVoltage.toFixed(2)}V
              <br />Cell voltage = E°(cathode) − E°(anode)
            </div>
          </>
        );
      case 5: // Gas Laws
        return (
          <>
            <label style={labelStyle}>
              📦 Volume: {(slider1 / 50).toFixed(2)} L
              <input type="range" min={5} max={100} value={slider1}
                onChange={e => setSlider1(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <label style={labelStyle}>
              🌡️ Temperature: {((slider2 / 50) * 300).toFixed(0)} K
              <input type="range" min={5} max={100} value={slider2}
                onChange={e => setSlider2(+e.target.value)} disabled={simRunning} style={sliderStyle} />
            </label>
            <div style={{ fontSize: 11, color: "#94a3b8" }}>
              Target: {targetPressure.toFixed(1)} atm
              <br />PV = nRT
            </div>
          </>
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
        <h1 style={{ fontSize: "1.3rem", margin: 0 }}>🧪 Chemistry Fun Quest</h1>
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
              background: "linear-gradient(90deg, #a855f7, #22c55e)",
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
            <div style={{ fontSize: 48, marginBottom: 16 }}>🧪</div>
            <h2 style={{ margin: "0 0 8px", fontSize: "1.5rem" }}>Chemistry Fun Quest</h2>
            <p style={{ color: "#94a3b8", margin: "0 0 24px", lineHeight: 1.6 }}>
              Journey through 6 chemistry lab challenges! Each level teaches a real chemistry concept
              through an interactive experiment. Complete all levels to become a Chemistry Master!
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 24, textAlign: "left" }}>
              {LEVELS.map((l, i) => (
                <div key={i} style={{ padding: "8px 12px", background: "#0a0a1a", borderRadius: 8, fontSize: 12 }}>
                  <span>{l.icon}</span> {l.name}
                </div>
              ))}
            </div>
            <button onClick={startGame} style={{
              ...btn, background: "#a855f7", border: "none", fontSize: 16, fontWeight: 700,
              padding: "12px 32px", borderRadius: 8, cursor: "pointer",
            }}>
              🧪 Start Quest
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
          <div style={{ ...panelStyle, minWidth: 220, flex: "0 0 auto", maxWidth: 280 }}>
            {/* Level info */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 20, marginBottom: 4 }}>
                {LEVELS[currentLevel].icon} Level {currentLevel + 1}: {LEVELS[currentLevel].name}
              </div>
              <div style={{ fontSize: 11, color: "#a855f7", fontFamily: "monospace", marginBottom: 8 }}>
                {LEVELS[currentLevel].concept}
              </div>
              <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.5 }}>
                🎯 {LEVELS[currentLevel].challenge}
              </div>
            </div>

            {/* Controls */}
            {renderControls()}

            {/* Go button */}
            <button onClick={runLevel} disabled={simRunning} style={{
              ...btn, width: "100%", marginTop: 8,
              background: simRunning ? "#333" : "#22c55e",
              color: "#fff", fontSize: 15, fontWeight: 700, border: "none", padding: "10px 0",
            }}>
              {simRunning ? "Running..." : currentLevel === 3 ? "▶ Start Reaction" : "✓ Check Answer"}
            </button>
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
            <p style={{ color: "#a855f7", margin: "0 0 20px", fontSize: 12 }}>
              Next: {LEVELS[currentLevel + 1]?.icon} {LEVELS[currentLevel + 1]?.name}
            </p>
            <button onClick={nextLevel} style={{
              ...btn, background: "#a855f7", border: "none", fontSize: 15, fontWeight: 700,
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
            <h2 style={{ margin: "0 0 8px" }}>Chemistry Master!</h2>
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
              ...btn, background: "#a855f7", border: "none", fontSize: 15, fontWeight: 700,
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
